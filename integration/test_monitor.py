from unittest.mock import patch

import pytest

from moniter import GolfReservationMonitor


class DummyDriver:
    def get_cookies(self):
        # 최소한의 더미 쿠키 반환
        return [{"name": "test", "value": "cookie"}]


def test_monitor_is_alive_date_logs(caplog):
    dummy_driver = DummyDriver()
    monitor = GolfReservationMonitor(
        selenium_cookies=dummy_driver.get_cookies(),
        hour=8,
        minute=59,
        second=50,
    )
    with caplog.at_level("INFO"):
        result = monitor.monitor_is_alive_date(
            "20250801", timeout_minutes=0.01
        )  # 빠른 테스트를 위해 타임아웃 짧게
    # 로그 메시지 검증
    assert "골프 예약 모니터링 시작" in caplog.text
    # assert "📅 대상 날짜: 20250801" in caplog.text
    # assert result is False or result is True  # 타임아웃 또는 성공


def test_monitor_keyboard_interrupt_logs(caplog):
    dummy_driver = DummyDriver()
    monitor = GolfReservationMonitor(
        selenium_cookies=dummy_driver.get_cookies(),
        hour=8,
        minute=59,
        second=50,
    )
    # time.sleep이 호출될 때 KeyboardInterrupt를 발생시키도록 patch
    with patch("time.sleep", side_effect=KeyboardInterrupt):
        with caplog.at_level("INFO"):
            result = monitor.monitor_is_alive_date("20250801", timeout_minutes=0.01)
    assert "🛑 사용자가 모니터링을 중단했습니다 (Ctrl+C)" in caplog.text
    assert result is False
