# InCheonCCScraper
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from user_agent import get_random_user_agent


class IncheonCCScraper:
    """
    Scraper (로그인, 페이지 제어)
    """

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

        self.__go_to_home_page()
        self.__login()
        self.go_to_reservation_page()

    def __go_to_home_page(self):
        home_path = "https://www.incheoncc.com:1436/index.asp"
        if home_path in self.driver.current_url:
            return
        self.driver.get(home_path)
        self.__close_popup_until_one()

    def __login(self):
        # 환경변수에서 로그인 정보 읽기

        loginpage_button = self.driver.find_element(
            By.XPATH, "//div[@class='login_area']/a[1]"
        )
        if loginpage_button.text != "로그인":
            return

        loginpage_button.click()

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
        time.sleep(1)
        self.__close_popup_until_one()

    def __handle_alert(self):
        if EC.alert_is_present():
            result = self.driver.switch_to.alert
            result.accept()

    def __close_popup_until_one(self):
        # 현재 윈도우가 2개 이상일 때 반복
        while len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.close()
        # 메인 윈도우로 다시 전환
        self.driver.switch_to.window(self.driver.window_handles[0])

    def go_to_reservation_page(self):
        reservation_url = (
            "https://www.incheoncc.com:1436/GolfRes/onepage/real_reservation.asp"
        )
        if reservation_url in self.driver.current_url:
            return

        self.driver.get(reservation_url)
