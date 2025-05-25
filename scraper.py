# InCheonCCScraper
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from pick_datetime_model import PickTimeRange
from user_agent import get_random_user_agent


class IncheonCCScraper:

    def __init__(self):
        self.driver = self.__create_driver()

    def __create_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
        chrome_options.add_argument("window-size=1920,1024")
        chrome_prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def reserve_course(
        self,
        yyyy_mm_dd: str,
        time_range_model: PickTimeRange,
    ):
        self.__go_to_login_page()
        self.__login()
        # TODO: 9시에 cron job and retry 추가 필요
        self.__go_to_pointdate_page(yyyy_mm_dd)
        self.__make_courses_applied_priority(time_range_model)
        print(self.courses_of_priority)

    def __login(self):
        # 환경변수에서 로그인 정보 읽기
        login_id = os.environ.get("LOGIN_ID")
        login_pw = os.environ.get("LOGIN_PW")
        if not login_id or not login_pw:
            raise RuntimeError("환경변수 LOGIN_ID, LOGIN_PW가 필요합니다.")

        id_element = self.driver.find_element(value="login_id")
        pw_element = self.driver.find_element(value="login_pw")
        id_element.send_keys(login_id)
        pw_element.send_keys(login_pw)
        login_button = self.driver.find_element(value="bt_login", by=By.CLASS_NAME)
        login_button.click()

        if EC.alert_is_present():
            self.__handle_alert()

    def __go_to_login_page(self):
        login_path = "https://www.incheoncc.com:1436/login/login.asp"
        return_url = "?returnurl=/pagesite/reservation/live.asp?"
        if login_path in self.driver.current_url:
            return
        self.driver.get(login_path + return_url)

    def __handle_alert(self):
        if EC.alert_is_present():
            result = self.driver.switch_to.alert
            result.accept()

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

    def __make_courses_applied_priority(self, time_range_model: PickTimeRange):
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

    def __reserve_course(self, yyyy_mm_dd: str, selected_time: str):
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
        """TABLE 따라서 같은 시간이 있다면, 예약합니다. 예약 후 예약 확인 페이지로 이동합니다."""
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
