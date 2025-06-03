import arrow
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QStyledItemDelegate

from pick_datetime_model import (
    PickDateModel,
    ReservationScheduler,
    ReservationStrategy,
    TimePoint,
    TimeRange,
)
from reservation import Reservation
from scraper import IncheonCCScraper


class PickDatetimeViewModel(QObject):
    # 추후 선택한 Input 값에 대한 Signal 사용으로 view에 업데이트

    def __init__(self, scraper: IncheonCCScraper):
        self.scraper = scraper
        self.dates_model = PickDateModel()
        self.start: TimePoint = TimePoint(hour=7, minute=30)
        self.priority_time: TimePoint = TimePoint(hour=8, minute=00)
        self.end: TimePoint = TimePoint(hour=8, minute=30)
        self.selected_date = ""
        self.load_dates()

    def load_dates(self):
        # 가능한 날짜 선택하게 하기
        self.dates_model.set_dates()

    def set_selected_date(self, date: str):
        self.selected_date = date

    def set_start_time(self, hour: int, minute: int):
        start_time = TimePoint(hour=hour, minute=minute)
        self.start = start_time

    def set_end_time(self, hour: int, minute: int):
        end_time = TimePoint(hour=hour, minute=minute)
        self.end = end_time

    def set_priority_time(self, hour: int, minute: int):
        priority_time = TimePoint(hour=hour, minute=minute)
        self.priority_time = priority_time

    def reserve_course(
        self, strategy: ReservationStrategy, scheduler: ReservationScheduler
    ):
        """Reservation 클래스 만들고 난 후 실행"""
        reservation = Reservation(
            scraper=self.scraper,
            strategy=strategy,
            scheduler=scheduler,
            yyyy_mm_dd=self.selected_date,
            time_range_model=TimeRange(
                start=self.start,
                end=self.end,
                priority_time=self.priority_time,
            ),
        )
        reservation.make_reservation()


class DateWithWeekdayDelegate(QStyledItemDelegate):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model

    def displayText(self, value, locale):
        try:
            weekday = arrow.get(value, "YYYYMMDD").format("ddd", locale="ko_kr")
            return f"{value} ({weekday})"
        except Exception:
            return value
