from dataclasses import dataclass
from typing import Tuple

from PySide6.QtCore import QAbstractListModel, Qt


@dataclass
class TimeRangeComponent:
    hour: int
    minute: int


@dataclass
class TimeRange:
    start: TimeRangeComponent
    end: TimeRangeComponent


class PickTimeRangeModel:
    def __init__(self):
        super().__init__()
        self.time_range: Tuple[TimeRange, TimeRange]


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
        self._dates = self.get_available_dates()
        self.endResetModel()

    def get_available_dates(self):
        # 오늘이 화요일이면, 2주 후의 주말, 공휴일
        return []

    def __get_holiday_dates_on_tuesday(self, date):
        pass

    def __get_weekend_dates_on_thursday(self, date):
        pass
