import os
import random
import sys


def resource_path(relative_path):
    """PyInstaller 환경에서도 리소스 파일 경로를 안전하게 반환"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
    return os.path.join(os.path.abspath("."), relative_path)


user_agent_list_txt_path = (
    resource_path("user_agent_list.txt")
    if hasattr(sys, "_MEIPASS")
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_agent_list.txt")
)


def get_random_user_agent():
    lines = open(user_agent_list_txt_path, "r").read().splitlines()
    return random.choice(lines)


import os
import sys


# .env 파일이 실행 파일과 같은 폴더에 있다고 가정
def env_path():
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller로 빌드된 경우
        env_path = os.path.join(os.path.dirname(sys.executable), "_internal/.env")
    else:
        # 개발 환경
        env_path = os.path.join(os.path.abspath("."), ".env")
    return env_path


def get_log_path():
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller로 빌드된 경우: 실행 파일 위치
        base_path = os.path.dirname(sys.executable)
    else:
        # 개발 환경: 현재 경로
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "app.log")
