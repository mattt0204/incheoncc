import arrow
from apscheduler.schedulers.background import BackgroundScheduler
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStyledItemDelegate

from custom_logger import logger
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
    session_cron_active_changed = Signal(bool)
    dom_cron_active_changed = Signal(bool)

    def __init__(self, scraper: IncheonCCScraper):
        super().__init__()
        self.scraper = scraper
        self.dates_model = PickDateModel()
        self.start: TimePoint = TimePoint(hour=7, minute=0)
        self.priority_time: TimePoint = TimePoint(hour=7, minute=30)
        self.end: TimePoint = TimePoint(hour=8, minute=0)
        self.selected_date = ""
        self.load_dates()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._session_cron_active = False  # Session CRON 상태
        self._dom_cron_active = False  # DOM CRON 상태
        self.day_of_week = "tue,wed,thu"  # 예약 요일
        self.hour = 9  # 예약 시간(시)
        self.minute = 0  # 예약 시간(분)

    @property
    def session_cron_active(self):
        return self._session_cron_active

    @session_cron_active.setter
    def session_cron_active(self, value):
        if self._session_cron_active != value:
            self._session_cron_active = value
            self.session_cron_active_changed.emit(value)

    @property
    def dom_cron_active(self):
        return self._dom_cron_active

    @dom_cron_active.setter
    def dom_cron_active(self, value):
        if self._dom_cron_active != value:
            self._dom_cron_active = value
            self.dom_cron_active_changed.emit(value)

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

        try:
            self.scraper.go_to_reservation_page()
        except Exception as e:
            # 새롭게 만들어서 driver 초기화
            self.scraper = IncheonCCScraper()
            self.scraper.login()
            self.scraper.go_to_reservation_page()

        """Reservation 클래스 만들고 난 후 실행"""
        reservation = Reservation(
            scraper=self.scraper,
            yyyy_mm_dd=self.selected_date,
            time_range_model=TimeRange(
                start=self.start,
                end=self.end,
                priority_time=self.priority_time,
            ),
        )
        reservation.execute(strategy=strategy)

    def _toggle_cron(
        self, strategy: ReservationStrategy, job_id: str, active_attr: str
    ):
        reservation = Reservation(
            scraper=self.scraper,
            yyyy_mm_dd=self.selected_date,
            time_range_model=TimeRange(
                start=self.start,
                end=self.end,
                priority_time=self.priority_time,
            ),
        )
        is_active = getattr(self, active_attr)
        if not is_active:
            self.scheduler.add_job(
                reservation.execute,
                "cron",
                id=job_id,
                day_of_week=self.day_of_week,
                hour=self.hour,
                minute=self.minute,
                replace_existing=True,
                kwargs={"strategy": strategy},
            )
            setattr(self, active_attr, True)
            logger.info(f"{job_id} 예약 완료")
            return True  # 등록됨
        else:
            self.scheduler.remove_job(job_id)
            setattr(self, active_attr, False)
            logger.info(f"{job_id} 예약 취소")
            return False  # 취소됨

    def toggle_session_cron(self, strategy: ReservationStrategy):
        return self._toggle_cron(strategy, "session_cron", "session_cron_active")

    def toggle_dom_cron(self, strategy: ReservationStrategy):
        return self._toggle_cron(strategy, "dom_cron", "dom_cron_active")

    def stop_all_cron(self):
        """모든 예약을 안전하게 종료"""
        self.scheduler.remove_all_jobs()
        self.session_cron_active = False
        self.dom_cron_active = False

    def __del__(self):
        logger.info("PickDatetimeViewModel 소멸됨")


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
