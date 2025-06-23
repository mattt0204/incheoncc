import datetime
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from custom_logger import logger
from user_agent import get_random_user_agent


class GolfReservationMonitor:
    def __init__(self, selenium_cookies):
        self.base_url = "https://www.incheoncc.com:1436"
        self.session = requests.Session()
        # 기본 헤더 설정 (실제 브라우저처럼 보이게)
        self.session.headers.update(
            {
                "User-Agent": get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        for cookie in selenium_cookies:
            self.session.cookies.set(cookie["name"], cookie["value"])

    def check_time_window(self) -> tuple[bool, int]:
        """
        현재 시간에 따른 모니터링 가능 여부와 대기 시간 반환

        Returns:
            tuple[bool, int]: (모니터링 가능 여부, 다음 체크까지 대기 시간(초))

        시간대별 모니터링 주기:
        - 8시 51분 ~ 8시 59분: 1분에 1번 (60초 간격)
        - 8시 59분 50초 ~ 9시 10분: 1초에 1번 (1초 간격)
        """
        now = datetime.datetime.now()

        # 시간대 정의
        criterion = now.replace(hour=8, minute=59, second=50, microsecond=0)

        if now < criterion:
            # ~ 8시 59분 50초 : 1분 간격
            return True, 60
        elif criterion <= now:
            # 8시 59분 50초 ~ : 1초 간격
            return True, 1
        else:
            return False, 0

    def get_calendar_data(self, yyyymmdd: str) -> Optional[bool]:
        """
        특정 날짜의 예약 상태를 확인
        yyyymmdd: YYYYMMDD 형식
        Returns: True if live, False if not live, None if error
        """
        try:
            # 달력 데이터를 가져오기 위한 AJAX 요청
            calendar_url = (
                f"{self.base_url}/GolfRes/onepage/real_calendar_ajax_view.asp"
            )

            # 타겟 날짜에서 년월 추출
            yyyymm = yyyymmdd[:6]  # YYYYMM
            # POST 데이터 준비
            post_data = {
                "golfrestype": "real",
                "schDate": yyyymm,
                "usrmemcd": "12",  # 유저멤버번호
                "toDay": yyyymmdd,
                "calnum": "1",  # 다음달이면 2
            }

            response = self.session.post(calendar_url, data=post_data)
            response.raise_for_status()

            # HTML 파싱
            soup = BeautifulSoup(response.text, "html.parser")

            # 해당 날짜의 링크 찾기
            target_day = int(yyyymmdd[-2:])  # 일자만 추출 01 -> 1

            # 모든 날짜 링크 찾기
            date_links = soup.find_all("a", href=True)
            for link in date_links:
                # 링크 텍스트가 해당 일자와 일치하는지 확인
                if link.get_text().strip() == str(target_day):
                    if "예약가능" == link.get("title", ""):  # type: ignore
                        return True
            return False

        except Exception as e:
            logger.info(f"오류 발생: {e}")
            return None

    def monitor_is_alive_date(self, yyyymmdd: str, timeout_minutes: int = 10) -> bool:
        """
        원하는 날짜가 live 상태가 될 때까지 시간대별 모니터링

        Args:
            yyyymmdd (str): 모니터링할 날짜 (YYYYMMDD 형식)
            timeout_minutes (int): 최대 모니터링 시간 (분 단위, 기본값: 10분)

        Returns:
            bool: True if 날짜가 live 상태가 됨, False if 시간 초과 또는 모니터링 불가

        모니터링 주기:
        - ~ 8시 59분 50초: 1분 간격
        - 8시 59분 50초 ~ : 1초 간격
        """

        start_time = datetime.datetime.now()
        timeout_seconds = timeout_minutes * 60

        logger.info(f"🏌️ 골프 예약 모니터링 시작")
        logger.info(f"📅 대상 날짜: {yyyymmdd}")
        logger.info(f"⏰ 모니터링 시간:")
        logger.info(f"   • 00:00 ~ 08:59:50 → 1분 간격")
        logger.info(f"   • 08:59:50 ~ 24:00 → 1초 간격")
        logger.info(f"   • 최대 모니터링 시간: {timeout_minutes}분")
        logger.info(f"   • Ctrl+C로 언제든 중단 가능")
        logger.info("-" * 50)

        check_count = 0
        last_check_time = None

        try:
            while True:
                # 타임아웃 체크
                current_time = datetime.datetime.now()
                elapsed_seconds = (current_time - start_time).total_seconds()
                if elapsed_seconds >= timeout_seconds:
                    logger.info(
                        f"⏰ {timeout_minutes}분 타임아웃으로 모니터링을 종료합니다"
                    )
                    return False

                # 현재 시간 확인 및 모니터링 가능 여부 체크
                can_monitor, wait_seconds = self.check_time_window()

                # 중복 체크 방지 (같은 시간대에 여러 번 체크하지 않음) 8시에 확인 필요
                if wait_seconds == 60:  # 1분 간격 모드
                    current_minute = current_time.replace(second=0, microsecond=0)
                    if last_check_time == current_minute:
                        time.sleep(10)  # 10초 쉬기
                        continue  # last_check_time = current_minute 무시? 혹은 while 자체를 무시?
                    last_check_time = current_minute

                # 모니터링 실행
                check_count += 1
                time_str = current_time.strftime("%H:%M:%S")
                interval_str = "1분 간격" if wait_seconds == 60 else "1초 간격"

                logger.info(f"🔍 검사 #{check_count} - {time_str} ({interval_str})")

                # 예약 상태 확인
                is_live = self.check_calendar_data(yyyymmdd)

                if is_live is None:
                    logger.info("❌ 데이터 조회 실패")
                elif is_live:
                    logger.info(f"✅ 성공! {yyyymmdd} 날짜가 예약 가능 상태입니다!")
                    return True
                else:
                    logger.info(f"⏳ {yyyymmdd} 아직 예약 불가능...")

                # 다음 체크까지 대기(주기 1초 또는 60초)
                time.sleep(wait_seconds)

        except KeyboardInterrupt:
            logger.info("🛑 사용자가 모니터링을 중단했습니다 (Ctrl+C)")
            return False

    def check_calendar_data(self, yyyymmdd: str) -> Optional[bool]:
        """실제 달력 데이터 확인 (간소화된 버전)"""
        try:
            return self.get_calendar_data(yyyymmdd)

        except Exception as e:
            logger.info(f"확인 중 오류: {e}")
            return None
