import re
import urllib.parse


def decode_unicode_url(text):
    """URL 인코딩된 유니코드 문자열을 디코딩합니다."""
    # %uXXXX 형식의 유니코드 문자를 디코딩
    pattern = r"%u([0-9a-fA-F]{4})"
    text = re.sub(pattern, lambda m: chr(int(m.group(1), 16)), text)

    # 일반적인 URL 인코딩 (%20 등)을 디코딩
    return urllib.parse.unquote(text)


def convert_date_format(date_str):
    try:
        # 날짜 형식이 8자리인지 확인
        if len(date_str) != 8:
            return "올바른 날짜 형식이 아닙니다."

        # 연도, 월, 일 추출
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:]

        # 변환된 형식으로 반환
        converted_date = f"{year}년 {month}월 {day}일"
        return converted_date

    except Exception as e:
        return f"에러가 발생했습니다: {str(e)}"
