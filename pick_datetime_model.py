import json
from dataclasses import dataclass
from enum import Enum
from typing import List

import arrow
from PySide6.QtCore import QAbstractListModel, Qt


@dataclass
class TimePoint:
    hour: int
    minute: int

    def __post_init__(self):
        if not (0 <= self.hour <= 23):
            raise ValueError("hour는 0~23 사이여야 합니다.")
        if not (0 <= self.minute <= 59):
            raise ValueError("minute는 0~59 사이여야 합니다.")

    def strf_hhmm(self):
        return f"{self.hour:02d}{self.minute:02d}"


@dataclass
class TimeRange:
    start: TimePoint
    end: TimePoint
    priority_time: TimePoint

    def make_filtered_timepoints_in_range(
        self, timepoints: List[TimePoint]
    ) -> List[TimePoint]:
        return []

    def __make_all_timepoints_in_range(self) -> List[TimePoint]:
        result = []
        start_minutes = self.start.hour * 60 + self.start.minute
        end_minutes = self.end.hour * 60 + self.end.minute
        for m in range(start_minutes, end_minutes + 1):
            hour = m // 60
            minute = m % 60
            result.append(TimePoint(hour, minute))
        return result

    def make_sorted_all_timepoints_by_priority(self) -> List[TimePoint]:
        def diff(tp: TimePoint):
            return abs(
                (tp.hour * 60 + tp.minute)
                - (self.priority_time.hour * 60 + self.priority_time.minute)
            )

        return sorted(self.__make_all_timepoints_in_range(), key=diff)

    def __post_init__(self):
        start_minutes = self.start.hour * 60 + self.start.minute
        end_minutes = self.end.hour * 60 + self.end.minute
        priority_minutes = self.priority_time.hour * 60 + self.priority_time.minute

        if not (start_minutes <= priority_minutes <= end_minutes):
            raise ValueError("priority_time은 start와 end 사이에 있어야 합니다.")


class PickDateModel(QAbstractListModel):
    def __init__(self, dates=[]):
        """가능한 날짜,
        오늘이 화요일이면, 2주 후의 주말, 공휴일
        오늘이 목요일이면, 주간
        """
        super().__init__()
        self._dates = dates or []

    def data(self, index, role) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self._dates[index.row()]

    def rowCount(self, parent=None):
        return len(self._dates)

    def set_dates(self):
        self.beginResetModel()
        self._dates = self.create_available_dates()
        self.endResetModel()

    def create_available_dates(self) -> list[str]:
        dates: list[str] = []
        # isoweekday() 월요일이 1, 일요일이 7
        today = arrow.now().to("Asia/Seoul")
        # 화,수요일이면
        if today.isoweekday() == 2 or today.isoweekday() == 3:
            dates = self.__make_dates_by_tuesday_rules()
        # 목,금,토,일,월요일이면
        elif today.isoweekday() in [1, 4, 5, 6, 7]:

            dates = self.__make_dates_by_thursday_rules()
        return dates

    def __make_dates_by_tuesday_rules(self) -> list[str]:

        days_between_last_thuesday_and_next_19days = (
            self.__make_dates_from_today_to_3rd_weekends()
        )
        holidays_between_2w_and_3w = self.__find_holidays_of_3rd_week_in_json()
        available_dates = set(days_between_last_thuesday_and_next_19days) | set(
            holidays_between_2w_and_3w
        )
        sorted_dates = list(sorted(available_dates))
        return sorted_dates

    def __make_dates_from_today_to_3rd_weekends(self) -> list[str]:
        """지난 화요일과 다음 19일까지의 날짜(2주후 주말까지)"""
        # 로직 테스트 필요
        is_today_tuesday = arrow.now().shift(weekday=1)
        start_day = is_today_tuesday
        end_day = start_day.shift(days=19)

        # 수요일이라면
        if arrow.now().isoweekday() == 3:
            previous_tuesday = arrow.now().shift(weekday=1).shift(days=-7)
            start_day = previous_tuesday.shift(days=1)
            end_day = start_day.shift(days=19 - 1)

        # 오늘부터 3주차 주말까지
        available_dates = [
            start_day.shift(days=i).strftime("%Y%m%d")
            for i in range((end_day - start_day).days + 1)
        ]

        return available_dates

    def __find_holidays_of_3rd_week_in_json(self) -> list[str]:
        """3주차의 주일(weekdays) 중 공휴일"""

        # 화요일
        tuesday = arrow.now().shift(weekday=1)
        # 수요일이라면, 이전 화요일
        if arrow.now().isoweekday() == 3:
            tuesday = arrow.now().shift(weekday=1).shift(days=-7)

        monday_of_3rd_weeks_yyyymmdd = tuesday.shift(days=18).strftime("%Y%m%d")
        saturday_of_3rd_weeks_yyyymmdd = tuesday.shift(days=24).strftime("%Y%m%d")
        holidays_of_3rd_week: list[str] = []

        with open("holidays.json", "r", encoding="utf-8") as f:
            dates = json.load(f)
            for date in dates:
                if (
                    monday_of_3rd_weeks_yyyymmdd
                    <= date["yyyymmdd"]
                    <= saturday_of_3rd_weeks_yyyymmdd
                ):
                    holidays_of_3rd_week.append(date["yyyymmdd"])
        return holidays_of_3rd_week

    def __make_dates_by_thursday_rules(self):
        """목요일 9시 규칙, 오늘부터 2주 + 다음주차의 주일까지"""
        # 목
        # weekday 월 0, 화 1, 수 2, 목 3, 금 4, 토 5, 일 6
        is_today_thursday = arrow.now().shift(weekday=3)
        start_day = is_today_thursday
        end_day = start_day.shift(days=22)

        previous_thursday = arrow.now().shift(weekday=3).shift(days=-7)
        # isoweekday금(월:1,화:2,수:3,목:4,금:5,토:6,일:7)
        if arrow.now().isoweekday() == 5:
            start_day = previous_thursday.shift(days=1)
            end_day = start_day.shift(days=22 - 1)

        # 토
        elif arrow.now().isoweekday() == 6:
            start_day = previous_thursday.shift(days=2)
            end_day = start_day.shift(days=22 - 2)
        # 일
        elif arrow.now().isoweekday() == 7:
            start_day = previous_thursday.shift(days=3)
            end_day = start_day.shift(days=22 - 3)
        # 월
        elif arrow.now().isoweekday() == 1:
            start_day = previous_thursday.shift(days=4)
            end_day = start_day.shift(days=22 - 4)

        # 오늘부터 3주차 주일(weekdays)까지
        available_dates = [
            start_day.shift(days=i).strftime("%Y%m%d")
            for i in range((end_day - start_day).days + 1)
        ]

        return available_dates


class ReservationStrategy(Enum):
    SESSION = "SESSION"  # 직접 요청
    DOM = "DOM"  # DOM API 요청


class ReservationScheduler(Enum):
    NOW = "NOW"  # 지금 실행
    CRON = "CRON"  # 화/목 9시 실행


class OutInType(Enum):
    OUT = 1  # 아웃 코스
    IN = 2  # 인 코스


@dataclass
class Course:
    out_in_number: OutInType
    time: str
