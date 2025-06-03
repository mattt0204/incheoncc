# InCheonCCScraper
import os

from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from custom_logger import logger
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

    def login(self):

        try:
            self.__go_to_login_page()
            self.__login()
        except UnexpectedAlertPresentException as e:
            logger.info(
                "이미 로그인 경우, 예상치 못한 alert 에러 뜸, But 무시하면 문제 없음"
            )

    def __login(self):
        # 환경변수에서 로그인 정보 읽기

        login_id = os.environ.get("LOGIN_ID")
        login_pw = os.environ.get("LOGIN_PW")

        if not login_id or not login_pw:
            raise RuntimeError("환경변수 LOGIN_ID, LOGIN_PW가 필요합니다.")

        # id 엘리먼트 선택
        id_element = self.driver.find_element(By.ID, "login_id")
        pw_element = self.driver.find_element(By.ID, "login_pw")

        id_element.send_keys(login_id)
        pw_element.send_keys(login_pw)

        login_button = self.driver.find_element(By.CLASS_NAME, "bt_login")
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

    def __close_popup_until_one(self):
        # 현재 윈도우가 2개 이상일 때 반복
        while len(self.driver.window_handles) > 1:
            # 마지막(가장 최근) 윈도우로 전환
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.close()  # 현재 윈도우 닫기
            # 메인 윈도우로 다시 전환
            self.driver.switch_to.window(self.driver.window_handles[0])
