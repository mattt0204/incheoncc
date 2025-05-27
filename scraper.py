# InCheonCCScraper
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from pick_datetime_model import TimeRange
from reservation import Reservation, ReservationStrategy, SessionPostReservation
from user_agent import get_random_user_agent


class IncheonCCScraper:

    def __init__(self, reservation_strategy: ReservationStrategy):
        self.driver = self.__create_driver()
        self.reservation = Reservation(reservation_strategy)

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
        time_range_model: TimeRange,
    ):
        self.__go_to_login_page()
        self.__login()
        self.reservation.set_strategy(SessionPostReservation(self.driver))
        self.reservation.make_reservation(yyyy_mm_dd, time_range_model)

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


# 시간을 만드는 과정부터
# driver web
# 또는 임의로 만들기
