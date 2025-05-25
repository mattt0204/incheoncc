# InCheonCCScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pick_datetime_model import TimeRangeEndpoint
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
        self, date: str, start_time: TimeRangeEndpoint, end_time: TimeRangeEndpoint
    ):
        pass
