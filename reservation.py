import os
from abc import ABC, abstractmethod
from collections import deque

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from custom_logger import logger
from moniter import GolfReservationMonitor
from pick_datetime_model import (
    Course,
    OutInType,
    ReservationStrategy,
    TimePoint,
    TimeRange,
)
from scraper import IncheonCCScraper
from utils import convert_date_format, decode_unicode_url


# 전략 인터페이스
class ReserveMethod(ABC):

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.reserve_ok_url = (
            "https://www.incheoncc.com:1436/GolfRes/onepage/real_resok.asp"
        )

    @abstractmethod
    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        pass


# 1. DoM API 방식 (셀레니움 등)
class DomApiReservation(ReserveMethod):

    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        logger.info("DOM API를 이용하여 예약하기")
        raise Exception("test")

        if not yyyy_mm_dd:
            raise ValueError("날짜가 없습니다.")
        monitor = GolfReservationMonitor(self.driver.get_cookies())

        # 1. 캘린더 모니터링 하기
        if not monitor.monitor_is_alive_date(yyyy_mm_dd):
            logger.info(f"🛑 {yyyy_mm_dd} 날짜가 예약 불가능 상태입니다!")

        # 2. 예약 페이지로 이동 후 예약 가능한 코스 찾고 우선순위대로 정렬하기
        self.driver.refresh()
        self.__go_to_pointdate_page(yyyy_mm_dd)
        sorted_courses = self.__make_courses_applied_priority(time_range_model)

        if not sorted_courses:
            logger.info(f"🛑 {yyyy_mm_dd}에 선택한 시간 중 가능한 시간대가 없습니다!")
            raise RuntimeError(f"🛑 {yyyy_mm_dd} 날짜가 예약 불가능 상태입니다!")

        try:
            courses_dq = deque(sorted_courses)
            course = courses_dq.popleft()
            self.__click_button_in_listpage(course)
            self.__click_button_in_detailpage()
        except NoSuchElementException as e:
            esg_ele = self.driver.find_element("input_ajax")
            if "ERROR" in esg_ele.text:
                # 선점에 의한 에러
                while courses_dq:
                    course = courses_dq.popleft()
                    # TODO: 예약 실패시 세션 방식으로 처리, while 문 처리
                    session = self.__preload_session()
                    payload = self.__make_payload(yyyy_mm_dd, course)
                    response = session.post(self.reserve_ok_url, data=payload)
                    idx = 2
                    if "OK" in response.text:
                        logger.info(
                            f"{idx}번째 시도, {payload["pointtime"]} / {payload["pointid"]} 예약 성공"
                        )
                        # while 문 종료
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
                        logger.info(
                            f"response.text: {decode_unicode_url(response.text)}"
                        )
                    idx += 1

        # 성공할 때만 실행
        else:
            if self.__check_reservation_success(yyyy_mm_dd, course):
                logger.info(f"🎉 {yyyy_mm_dd} {course.time} 예약 성공")
            else:
                logger.info(f"🛑 {yyyy_mm_dd} {course.time} 예약 실패")

        finally:
            logger.info("예약 프로세스: DOMAPI 매크로 종료")

    def __preload_session(self):
        selenium_cookies = self.driver.get_cookies()
        session = requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(cookie["name"], cookie["value"])
        return session

    def __make_payload(self, yyyy_mm_dd: str, course: Course):

        # environ
        hand_tel1 = os.environ.get("HAND_TEL1")
        hand_tel2 = os.environ.get("HAND_TEL2")
        hand_tel3 = os.environ.get("HAND_TEL3")
        # POST 요청에 사용할 데이터
        return {
            "cmd": "ins",
            "cmval": "0",
            "cmrtype": "N",
            "calltype": "AJAX",
            "gonexturl": "/GolfRes/onepage/my_golfreslist.asp",
            "pointdate": yyyy_mm_dd,
            "openyn": "1",
            "dategbn": "6",
            "pointid": course.point_id_out_in,
            "pointtime": course.strf_hhmm(),
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

    def __check_reservation_success(self, yyyy_mm_dd: str, course: Course):
        try:
            reservation_complete_url = (
                "https://www.incheoncc.com:1436/GolfRes/onepage/my_golfreslist.asp"
            )
            self.driver.get(reservation_complete_url)
            converted_date = convert_date_format(yyyy_mm_dd)
            table = self.driver.find_element(By.CLASS_NAME, "cm_time_list_tbl")
            for reservation in table.find_elements(By.TAG_NAME, "tr")[1:]:
                if (
                    reservation.find_elements(By.TAG_NAME, "td")[1].text
                    == converted_date
                    and reservation.find_elements(By.TAG_NAME, "td")[2].text
                    == course.time
                    and course.course_type
                    in reservation.find_elements(By.TAG_NAME, "td")[3].text
                ):
                    return True
            return False
        except UnexpectedAlertPresentException as e:
            if not e.alert_text:
                return False
            if "주말 총 예약선점 가능횟수는 최대 2회 입니다." in e.alert_text:
                logger.info(f"예약 완료 확인 중 예상치 못한 알림 발생: {e.msg}")
                if EC.alert_is_present():
                    result = self.driver.switch_to.alert
                    result.accept()

                return False
            else:
                raise e

    def __click_button_in_detailpage(self):

        btn = self.driver.find_element(By.XPATH, "//form/div/button[1]")
        if btn.text == "예약":
            btn.click()
        # 주석 해제시 예약 완료 처리 됨
        if EC.alert_is_present():
            result = self.driver.switch_to.alert
            result.accept()

    def __click_button_in_listpage(self, course: Course):
        wait = WebDriverWait(self.driver, 10)
        table = wait.until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    "cm_time_list_tbl",
                )
            )
        )
        # 헤더 제외한 행
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if course.course_type == cells[1].text and course.time == cells[2].text:
                cells[6].click()
                break

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

        # 결과를 저장할 list
        scrpaed_courses = []

        # 각 행을 순회하며 데이터 추출
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) != 7:  # 모든 컬럼이 있는지 확인
                raise Exception("코스의 칼럼이 바뀌었습니다.")
            course_type = cells[1].text
            course_time = cells[2].text
            # 문자열을 OutInType enum으로 변환
            point_id_out_in = OutInType.OUT if course_type == "OUT" else OutInType.IN
            scrpaed_courses.append(
                Course(
                    point_id_out_in=point_id_out_in,
                    course_type=course_type,
                    time=course_time,
                )
            )

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
        sorted_courses = sorted(
            filtered,
            key=lambda x: abs(time_to_minutes(x.time) - priority_minutes),
        )

        return sorted_courses


# 2. Session Post 방식
class SessionPostReservation(ReserveMethod):
    """Session Post 방식으로 예약을 진행합니다."""

    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        logger.info("서버에 직접 요청 방식으로 예약하기")
        raise Exception("test")
        if not yyyy_mm_dd:
            raise ValueError("날짜가 없습니다.")
        tps_priority = time_range_model.make_sorted_all_timepoints_by_priority()
        session = self.__preload_session()
        is_success = False
        for idx, time_point in enumerate(tps_priority, start=1):
            for point_id_out_in in ["1", "2"]:
                payload = self.__make_payload(yyyy_mm_dd, time_point, point_id_out_in)
                logger.info(
                    f"{payload["pointdate"]}/{payload["pointtime"]}/{payload["pointid"]}"
                )
                response = session.post(self.reserve_ok_url, data=payload)
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
                    logger.info(f"response.text: {decode_unicode_url(response.text)}")
                idx += 1
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
    ):
        if strategy == ReservationStrategy.SESSION:
            reservation_method = SessionPostReservation(self.scraper.driver)
        elif strategy == ReservationStrategy.DOM:
            reservation_method = DomApiReservation(self.scraper.driver)

        reservation_method.reserve(self.yyyy_mm_dd, self.time_range_model)
