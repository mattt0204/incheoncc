import pytest

from utils import decode_unicode_url


@pytest.mark.parametrize(
    "encoded,expected",
    [
        # 테스트 케이스 1: 단순한 유니코드 변환
        ("%uC608%uC57D", "예약"),
        # 테스트 케이스 2: 유니코드와 URL 인코딩 혼합
        ("%uC774%20%uC644%uB8CC", "이 완료"),
        # 테스트 케이스 3: 실제 response.text 예시
        (
            '\r\n\t{"result" : "OK", "gomsg" : "%uC608%uC57D%uC774%20%uC644%uB8CC%20%uB418%uC5C8%uC2B5%uB2C8%uB2E4.%20%uC608%uC57D%uD558%uC2E0%20%uC0AC%uD56D%uC744%20%uD655%uC778%uD558%uC5EC%20%uC8FC%uC2ED%uC2DC%uC694.", "gonexturl" : "/GolfRes/onepage/my_golfreslist.asp"}\r\n',
            '\r\n\t{"result" : "OK", "gomsg" : "예약이 완료 되었습니다. 예약하신 사항을 확인하여 주십시요.", "gonexturl" : "/GolfRes/onepage/my_golfreslist.asp"}\r\n',
        ),
        # 테스트 케이스 4: 인코딩이 없는 일반 텍스트
        ("Hello, World!", "Hello, World!"),
        # 테스트 케이스 5: 빈 문자열
        ("", ""),
    ],
)
def test_decode_unicode_url(encoded: str, expected: str):
    """decode_unicode_url 함수를 테스트합니다."""
    assert decode_unicode_url(encoded) == expected


def test_decode_unicode_url_with_invalid_unicode():
    """잘못된 유니코드 형식에 대한 테스트"""
    # %u 뒤에 올바르지 않은 16진수가 오는 경우
    invalid_unicode = "%uXYZW"
    # 에러 없이 원본 텍스트를 반환해야 함
    assert decode_unicode_url(invalid_unicode) == invalid_unicode
