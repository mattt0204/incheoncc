import arrow
from loguru import logger as __logger


def format_record(record):
    """이 함수 이상한데 2가지 일을 하네, 그리고 곧바로"""
    record["time"] = arrow.now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
    message = record["message"].replace('"', "'")
    record["message"] = f'"{message}"'
    return True


# csv 파일에 추가
__logger.add("./logs.csv", format="{time},{level},{message}", filter=format_record)


# logger 인스턴스 생성 및 설정
logger = __logger.bind()  # 새로운 logger 인스턴스 생성
