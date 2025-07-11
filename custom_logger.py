import logging
import sys

import arrow

# 로그 포맷 정의
LOG_FORMAT = "%(asctime)s,%(levelname)s,%(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# root logger 사용
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 콘솔 핸들러
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(console_handler)

# 파일 핸들러 (CSV 포맷)
file_handler = logging.FileHandler("./logs.csv")
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(file_handler)
