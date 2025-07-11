import pytest

from pick_datetime_model import ReservationStrategy, TimePoint
from pick_datetime_view_model import PickDatetimeViewModel
from scraper import IncheonCCScraper


def test_dom_schedule_reservation_success(caplog):
    scraper = IncheonCCScraper()
    view_model = PickDatetimeViewModel(scraper)
    view_model.selected_date = "2025-08-01"
    view_model.start = TimePoint(8, 0)
    view_model.end = TimePoint(8, 30)
    view_model.priority_time = TimePoint(8, 0)
    with caplog.at_level("INFO"):
        result = view_model.toggle_dom_cron(
            strategy=ReservationStrategy.DOM, is_test=True
        )
    assert "dom_cron 예약 완료" in caplog.text
    assert result is True
