import re
import urllib.parse


def decode_unicode_url(text):
    """URL 인코딩된 유니코드 문자열을 디코딩합니다."""
    # %uXXXX 형식의 유니코드 문자를 디코딩
    pattern = r"%u([0-9a-fA-F]{4})"
    text = re.sub(pattern, lambda m: chr(int(m.group(1), 16)), text)

    # 일반적인 URL 인코딩 (%20 등)을 디코딩
    return urllib.parse.unquote(text)
