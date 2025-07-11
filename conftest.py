# E2E 테스트 환경 세팅: .env.test 파일 자동 로드

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# e2e 폴더 기준 루트에 .env.test가 있다고 가정


@pytest.fixture(autouse=True, scope="session")
def load_test_env():
    # .env.test 파일을 자동으로 로드
    env_path = Path(__file__).parent / ".env.test"
    loaded = load_dotenv(dotenv_path=env_path)
    print("dotenv loaded:", loaded)
    print("HAND_TEL1:", os.environ.get("HAND_TEL1"))
    print("LOGIN_ID:", os.environ.get("LOGIN_ID"))
    print("픽스쳐 실행")
