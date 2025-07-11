import pytest

from pick_datetime_model import ReservationStrategy, TimePoint, TimeRange
from pick_datetime_view_model import PickDatetimeViewModel
from scraper import IncheonCCScraper


def test_dom_instant_reservation_success(caplog):
    scraper = IncheonCCScraper()
    view_model = PickDatetimeViewModel(scraper)
    view_model.selected_date = "2025-08-01"
    view_model.start = TimePoint(8, 0)
    view_model.end = TimePoint(8, 30)
    view_model.priority_time = TimePoint(8, 0)
    with caplog.at_level("INFO"):
        with pytest.raises(Exception) as excinfo:
            view_model.reserve_course(strategy=ReservationStrategy.DOM, is_test=True)
    assert "DOM API를 이용하여 예약하기" in caplog.text

    # assert "test 모드는 실제 예약하지 않습니다." in str(excinfo.value)
