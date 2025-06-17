import os

from PySide6.QtWidgets import QApplication

from custom_logger import logger
from pick_datetime_view import PickDatetimeView
from pick_datetime_view_model import PickDatetimeViewModel
from scraper import IncheonCCScraper


def load_hand_tels_from_env():
    hand_tel1 = os.environ.get("HAND_TEL1")
    hand_tel2 = os.environ.get("HAND_TEL2")
    hand_tel3 = os.environ.get("HAND_TEL3")
    return hand_tel1, hand_tel2, hand_tel3


if __name__ == "__main__":
    # 환경변수 확인

    hand_tel1, hand_tel2, hand_tel3 = load_hand_tels_from_env()
    logger.info("환경변수 확인")
    logger.info(f"HAND_TEL1: {hand_tel1}")
    logger.info(f"HAND_TEL2: {hand_tel2}")
    logger.info(f"HAND_TEL2: {hand_tel3}")

    app = QApplication([])
    scraper = IncheonCCScraper()
    scraper.login()
    # TODO: 추후 주말 예약이 가능한지 확인 후 가이드 메세지 필요(예약한도)

    view_model = PickDatetimeViewModel(scraper)
    view_model.load_dates()
    widget = PickDatetimeView(app, view_model)
    widget.show()
    app.exec()
