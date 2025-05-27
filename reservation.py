import re
from abc import ABC, abstractmethod

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pick_datetime_model import TimeRange


# 전략 인터페이스
class ReservationStrategy(ABC):

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    @abstractmethod
    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        pass


# 1. DoM API 방식 (셀레니움 등)
class DomApiReservation(ReservationStrategy):
    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        driver = webdriver.Chrome()
        driver.get("https://example.com/reserve")
        # 로그인, 폼 입력, 버튼 클릭 등 실제 브라우저 조작
        # driver.find_element(...).send_keys(user)
        # driver.find_element(...).click()
        driver.quit()

    def __go_to_pointdate_page(self, yyyy_mm_dd):
        """yyyy_mm_dd 형식의 날짜를 클릭하여 페이지를 이동합니다."""
        # TODO: 9시이후에는 until 코스가 보일 때까지,또는 응답이 올 때 까지, //  how 재시도 또는 새로 고침, 규칙을 설정
        # TODO: 9시 이전에는 세션 끊길수도있으니, 1분마다 누르기
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
        course_times_scrpaed = []

        # 각 행을 순회하며 데이터 추출
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 7:  # 모든 컬럼이 있는지 확인
                course_time = cells[2].text
                course_times_scrpaed.append(course_time)

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
            course_time
            for course_time in course_times_scrpaed
            if time_to_minutes(course_time) >= start_minutes
            and time_to_minutes(course_time) <= end_minutes
        ]
        sorted_course_times = sorted(
            filtered,
            key=lambda x: abs(time_to_minutes(x) - priority_minutes),
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

    def __check_reservation_complete(self, yyyy_mm_dd: str, point_time: str):
        """예약확인페이지에서 예약이 완료되었는지 확인합니다. point_time: 05:06"""
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


# 2. Session Post 방식 (requests 등)
class SessionPostReservation(ReservationStrategy):
    def reserve(self, yyyy_mm_dd: str, time_range_model: TimeRange):

        seesion = self.__preload_session()

        # print(f"{}에 Session Post로 예약 시도, 결과: {response.status_code}")

    def __preload_session(self):
        # Selenium에서 로그인 등 필요한 쿠키 가져오기
        selenium_cookies = self.driver.get_cookies()

        # requests 세션 초기화
        session = requests.Session()

        # Selenium에서 가져온 세션 쿠키를 requests 세션에 추가
        for cookie in selenium_cookies:
            session.cookies.set(cookie["name"], cookie["value"])


# Context
class Reservation:
    def __init__(self, strategy: ReservationStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: ReservationStrategy):
        self.strategy = strategy

    def make_reservation(self, yyyy_mm_dd: str, time_range_model: TimeRange):
        self.strategy.reserve(yyyy_mm_dd, time_range_model)


# # 사용 예시
# reservation = Reservation(DomApiReservation())
# reservation.make_reservation("홍길동", "10:00")

# reservation.set_strategy(SessionPostReservation())
# reservation.make_reservation("홍길동", "11:00")
