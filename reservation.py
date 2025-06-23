import os
import re
from abc import ABC, abstractmethod

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from custom_logger import logger
from moniter import GolfReservationMonitor
from pick_datetime_model import (
    Course,
    OutInType,
    ReservationScheduler,
    ReservationStrategy,
    TimePoint,
    TimeRange,
)
from scraper import IncheonCCScraper
from utils import decode_unicode_url


# 전략 인터페이스
class ReserveMethod(ABC):

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    @abstractmethod
    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        pass

    # TODO: 예약 완료 확인까지 확인 완료
    def is_course_reserved(self, yyyy_mm_dd: str, point_time: str):
        """예약확인페이지에서 예약이 완료되었는지 확인합니다. point_time: 05:06"""
        my_golfreslist_url = (
            "https://www.incheoncc.com:1436/GolfRes/onepage/my_golfreslist.asp"
        )
        self.driver.get(my_golfreslist_url)
        match = re.match(r"(\d{4})(\d{2})(\d{2})", yyyy_mm_dd)
        reservation_date_for_check = ""
        if match:
            year, month, day = match.groups()
            reservation_date_for_check = f"{year}년 {int(month):02d}월 {int(day):02d}일"
        else:
            raise RuntimeError("날짜 형식이 맞지 않습니다.")
        table = self.driver.find_element(By.CLASS_NAME, "cm_time_list_tbl")

        for reservation in table.find_elements(By.TAG_NAME, "tr")[1:]:
            if (
                reservation.find_elements(By.TAG_NAME, "td")[1].text
                == reservation_date_for_check
                and reservation.find_elements(By.TAG_NAME, "td")[2].text == point_time
            ):
                return True

        return False


# 1. DoM API 방식 (셀레니움 등)
class DomApiReservation(ReserveMethod):

    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        if not yyyy_mm_dd:
            raise ValueError("날짜가 없습니다.")
        logger.info("돔 API를 이용하여 예약하기")
        self.__go_to_reservation_page()
        monitor = GolfReservationMonitor(self.driver.get_cookies())

        # 1. 캘린더 모니터링 하기
        if not monitor.monitor_is_alive_date(yyyy_mm_dd):
            logger.info(f"🛑 {yyyy_mm_dd} 날짜가 예약 불가능 상태입니다!")
            raise RuntimeError(f"🛑 {yyyy_mm_dd} 날짜가 예약 불가능 상태입니다!")
        # 2. 예약 페이지로 이동 후 예약 가능한 코스 찾고 우선순위대로 정렬하기
        self.driver.refresh()
        self.__go_to_pointdate_page(yyyy_mm_dd)
        self.__make_courses_applied_priority(time_range_model)

        if not self.courses_of_priority:
            logger.info(f"🛑 {yyyy_mm_dd}에 선택한 시간 중 가능한 시간대가 없습니다!")
            raise RuntimeError(f"🛑 {yyyy_mm_dd} 날짜가 예약 불가능 상태입니다!")

        # queue 자료구조로 처리하도록 바꾸기(deque?)
        # 3. 우선순위 1순위 테스트
        # 3a 실패하면 SessionPost 방식으로 예약 시도
        # 4. 예약상세 페이지에서 예약 버튼 누르기
        # 4a 실패하면 SessionPost 방식으로 예약 시도
        # 5. 예약 확인 페이지에서 예약 완료 확인 보고 후 다시, 예약하기 페이지로 이동

        pass

    def __go_to_reservation_page(self):
        """예약페이지로 이동"""
        reservation_url = (
            "https://www.incheoncc.com:1436/GolfRes/onepage/real_reservation.asp"
        )
        if reservation_url in self.driver.current_url:
            return
        self.driver.get(reservation_url)

    def __go_to_pointdate_page(self, yyyy_mm_dd):
        """yyyy_mm_dd 형식의 날짜를 클릭하여 페이지를 이동합니다."""
        # TODO: 9시 이후에는 until 코스가 보일 때까지,또는 응답이 올 때 까지, //  how 재시도 또는 새로 고침, 규칙을 설정
        wait = WebDriverWait(self.driver, 10)
        cal_live_dates = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//table[@class='cm_calender_tbl']//td/a[contains(@class,'cal_live')]",
                )
            )
        )
        # 날짜 클릭
        for cal_live_date in cal_live_dates:
            href = cal_live_date.get_attribute("href")
            if yyyy_mm_dd in href:
                cal_live_date.click()
                break

    def __make_courses_applied_priority(self, time_range_model: TimeRange):
        """
        1. start_end 사이에 있는 모든 코스 course_times_scrpaed 수집한다.
        2. priority_time에 가까운 코스 순으로 배열을 sort 합니다.

        """
        wait = WebDriverWait(self.driver, 10)
        table = wait.until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    "cm_time_list_tbl",
                )
            )
        )
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # 헤더 행 제외
        # row 모두 수집하지 않은 이유는 어차피 stale 걸릴 거라서

        # 결과를 저장할 list
        scrpaed_courses = []

        # 각 행을 순회하며 데이터 추출
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 7:  # 모든 컬럼이 있는지 확인
                course_out_in_number = cells[1].text
                course_time = cells[2].text
                # 문자열을 OutInType enum으로 변환
                out_in_type = (
                    OutInType.OUT if course_out_in_number == "OUT" else OutInType.IN
                )
                scrpaed_courses.append(Course(out_in_type, course_time))

        def time_to_minutes(tstr):
            h, m = map(int, tstr.split(":"))
            return h * 60 + m

        start_minutes = time_range_model.start.hour * 60 + time_range_model.start.minute
        end_minutes = time_range_model.end.hour * 60 + time_range_model.end.minute
        priority_minutes = (
            time_range_model.priority_time.hour * 60
            + time_range_model.priority_time.minute
        )
        filtered = [
            course
            for course in scrpaed_courses
            if time_to_minutes(course.time) >= start_minutes
            and time_to_minutes(course.time) <= end_minutes
        ]
        sorted_course_times = sorted(
            filtered,
            key=lambda x: abs(time_to_minutes(x.time) - priority_minutes),
        )

        self.courses_of_priority = sorted_course_times

    def __reserve_course(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        """yyyy_mm_dd 형식의 날짜와 time_range_model을 이용하여 예약을 진행합니다.
        selected_time: 05:06
        3. 우선순위 배열 순서대로 신청합니다. 에러 발생시 코스 선택 페이지로 이동해서, 다시 실행합니다.
        실패시 에러 페이지 확인 -> 다시 실시간 캘린더 눌러서, 코스 선택페이지로 이동해야함
        """
        if not self.courses_of_priority:
            raise RuntimeError("코스가 없습니다.")

        for course in self.courses_of_priority:
            self.__reserve_course_by_time(course)

    def __reserve_course_by_time(self, selected_time: str):
        """
        1. TABLE 에 같은 시간이 있다면, 예약 버튼을 눌러 예약 안내 엘리먼트를 불러옵니다.
        2. 예약 안내 페이지로 진입시, 엘리먼트가 발생시, 다시 point_date_page로 이동 후 다시 예약을 시작합니다.
        3. 예약 안내 페이지로 진입시, 엘리먼트가 정상적으로 작동하고, 버튼이 있다면, 버튼을 눌러 예약 완료를 합니다.
        3. 예약 안내 페이지에서 예약 버튼을 누르고 에러가 발생한다면, 다시 point_date_page로 이동한 후 다시 예약을 시작합니다.

        예약 후 예약 확인 페이지로 이동합니다."""
        pass


# 2. Session Post 방식
class SessionPostReservation(ReserveMethod):
    """Session Post 방식으로 예약을 진행합니다."""

    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        if not yyyy_mm_dd:
            raise ValueError("날짜가 없습니다.")
        tps_priority = time_range_model.make_sorted_all_timepoints_by_priority()
        session = self.__preload_session()
        reserve_ok_url = "https://www.incheoncc.com:1436/GolfRes/onepage/real_resok.asp"
        logger.info("세션 직접 요청으로 예약하기")
        is_success = False
        for idx, time_point in enumerate(tps_priority, start=1):
            for point_id_out_in in ["1", "2"]:
                payload = self.__make_payload(yyyy_mm_dd, time_point, point_id_out_in)
                logger.info(
                    f"{payload["pointdate"]}/{payload["pointtime"]}/{payload["pointid"]}"
                )
                response = session.post(reserve_ok_url, data=payload)
                if "OK" in response.text:
                    logger.info(
                        f"{idx}번째 시도, {payload["pointtime"]} / {payload["pointid"]} 예약 성공"
                    )
                    is_success = True
                    break
                elif "오류" in decode_unicode_url(response.text):
                    logger.info(
                        f"{idx}번째 시도, {payload["pointtime"]} / {payload["pointid"]} 예약 실패, 없는 시간"
                    )
                elif "동시예약" in decode_unicode_url(response.text):
                    logger.info(
                        f"{idx}번째 시도, {payload["pointtime"]} / {payload["pointid"]} 예약 실패, 동시예약으로 인한 실패"
                    )
                elif (
                    "다른 곳에서 회원님의 아이디로 로그인 되었습니다."
                    in decode_unicode_url(response.text)
                ):
                    logger.info(
                        f"{idx}번째 시도, {payload["pointtime"]} / {payload["pointid"]} 예약 실패, 이중 로그인로 인한 실패"
                    )
                else:
                    logger.info(
                        f"{idx}번째 시도, {payload["pointtime"]} / {payload["pointid"]} 예약 실패, 원인이 밝혀지지 않은 실패"
                    )
            if is_success:
                break

    def __preload_session(self) -> requests.Session:
        # Selenium에서 로그인 등 필요한 쿠키 가져오기
        selenium_cookies = self.driver.get_cookies()

        # requests 세션 초기화
        session = requests.Session()

        # Selenium에서 가져온 세션 쿠키를 requests 세션에 추가
        for cookie in selenium_cookies:
            session.cookies.set(cookie["name"], cookie["value"])
        return session

    def __make_payload(
        self, yyyy_mm_dd: str, timepoint: TimePoint, point_id_out_in="1"
    ):
        # environ
        hand_tel1 = os.environ.get("HAND_TEL1")
        hand_tel2 = os.environ.get("HAND_TEL2")
        hand_tel3 = os.environ.get("HAND_TEL3")
        # POST 요청에 사용할 데이터
        form_data = {
            "cmd": "ins",
            "cmval": "0",
            "cmrtype": "N",
            "calltype": "AJAX",
            "gonexturl": "/GolfRes/onepage/my_golfreslist.asp",
            "pointdate": yyyy_mm_dd,
            "openyn": "1",
            "dategbn": "6",
            "pointid": point_id_out_in,
            "pointtime": timepoint.strf_hhmm(),
            "flagtype": "I",
            "punish_cd": "UNABLE",
            "self_r_yn": "N",
            "res_gubun": "N",
            "usrmemcd": "12",
            "memberno": "12061000",
            "hand_tel1": hand_tel1,
            "hand_tel2": hand_tel2,
            "hand_tel3": hand_tel3,
        }
        return form_data


# Context
class Reservation:
    """예약 총괄 책임 담당
    View에서 받은 파라미터 관리
    예약 플로우 전체 오케스트레이션
    타이밍 제어 (9시 정확히, 사전 로그인 체크)
    Strategy와 Scraper 간 데이터 전달
    """

    def __init__(
        self,
        scraper: IncheonCCScraper,
        yyyy_mm_dd: str,
        time_range_model: TimeRange,
    ):
        self.scraper = scraper
        self.yyyy_mm_dd = yyyy_mm_dd
        self.time_range_model = time_range_model

    def execute(
        self,
        strategy: ReservationStrategy,
        scheduler: ReservationScheduler,
    ):
        # 실제 예약 실행(예약방식,how에 따라 달라짐)
        if strategy == ReservationStrategy.SESSION:
            reservation_method = SessionPostReservation(self.scraper.driver)
        elif strategy == ReservationStrategy.DOM:
            reservation_method = DomApiReservation(self.scraper.driver)
        else:
            raise ValueError("지원하지 않는 예약 방식(how)입니다.")

        if scheduler == ReservationScheduler.CRON:
            # 예약된 시간까지 대기 후 실행 (예: scheduler 사용)
            # self.scheduler.wait_until_reserved_time()
            # reservation_method.reserve(self.yyyy_mm_dd, self.time_range_model)
            pass
        elif scheduler == ReservationScheduler.NOW:
            # 즉시 실행
            reservation_method.reserve(self.yyyy_mm_dd, self.time_range_model)
