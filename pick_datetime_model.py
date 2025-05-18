import json
from dataclasses import dataclass

import arrow
from PySide6.QtCore import QAbstractListModel, Qt


@dataclass
class TimeRangeEndpoint:
    hour: int
    minute: int

    def __post_init__(self):
        if not (0 <= self.hour <= 23):
            raise ValueError("hour는 0~23 사이여야 합니다.")
        if not (0 <= self.minute <= 59):
            raise ValueError("minute는 0~59 사이여야 합니다.")


@dataclass
class PickTimeRange:
    start: TimeRangeEndpoint
    end: TimeRangeEndpoint


class PickDateModel(QAbstractListModel):
    def __init__(self, dates=[]):
        """가능한 날짜,
        오늘이 화요일이면, 2주 후의 주말, 공휴일
        오늘이 목요일이면, 주간
        """
        super().__init__()
        self._dates = dates or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._dates[index.row()]

    def rowCount(self, parent=None):
        return len(self._dates)

    def set_dates(self, dates):
        self.beginResetModel()
        self._dates = self.make_available_dates()
        self.endResetModel()

    def make_available_dates(self) -> list[str]:
        dates: list[str] = []
        # isoweekday() 월요일이 1, 일요일이 7
        today = arrow.now().to("Asia/Seoul")
        # 화,수요일이면
        if today.isoweekday() == 2 or today.weekday() == 3:
            print(f"화,수요일 {today.isoweekday()}")
            dates = self.__make_dates_by_tuesday()
        # 목,금,토,일,월요일이면
        elif today.isoweekday() in [1, 4, 5, 6, 7]:
            print(f"목,금,토,일,월요일 {today.isoweekday()}")
            dates = self.__make_23days_on_thursday()

        return dates

    def __make_dates_by_tuesday(self) -> list[str]:

        days_between_last_thuesday_and_next_19days = (
            self.__get_last_thuesday_next_19days()
        )
        holidays_between_2w_and_3w = (
            self.__get_holidays_between_next20days_and_next_saturday()
        )
        available_dates = days_between_last_thuesday_and_next_19days.extend(
            holidays_between_2w_and_3w
        )

        if available_dates is None:
            return []

        return available_dates

    def __get_last_thuesday_next_19days(self) -> list[str]:
        """지난 화요일과 다음 19일까지의 날짜(2주후 주말까지)"""
        range_days = 20
        available_dates = []
        before_tuesday = arrow.now().shift(weekday=1).shift(days=-7)
        # 0~19
        for day in range(range_days):
            yyyymmdd = before_tuesday.shift(days=day).strftime("%Y%m%d")
            available_dates.append(yyyymmdd)

        return available_dates

    def __get_holidays_between_next20days_and_next_saturday(self) -> list[str]:
        """2-3주차의 주일(weekdays) 중 공휴일"""
        before_tuesday = arrow.now().shift(weekday=1).shift(days=-7)
        next_19days_yyyymmdd = before_tuesday.shift(days=19).strftime("%Y%m%d")
        next_saturday_yyyymmdd = before_tuesday.shift(days=25).strftime("%Y%m%d")
        available_dates: list[str] = []
        with open("holidays.json", "r", encoding="utf-8") as f:
            dates = json.load(f)
            for date in dates:
                if next_19days_yyyymmdd < date["yyyymmdd"] < next_saturday_yyyymmdd:
                    available_dates.append(date["yyyymmdd"])
        return available_dates

    def __make_23days_on_thursday(self):
        """2주 + 다음주차의 주일까지"""

        before_thursday = arrow.now().shift(weekday=3).shift(days=-7)
        available_dates = []
        range_days = 23
        for i in range(range_days):
            yyyymmdd = before_thursday.shift(days=i).strftime("%Y%m%d")
            available_dates.append(yyyymmdd)
        return available_dates
