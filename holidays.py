import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_holidays():
    """
    공휴일 정보를 가져오는 함수, 10000번이 최대 한도라서 프로그램에 넣지 않고, 따로 수동으로 실행하고 JSON 파일로 저장
    수시 실행: 정부가 임시공휴일(대통령선거와 같은 경우처럼) 지정할 때, $python holidays.py 명령어로 업데이트
    정기 실행: 매달 1일에 $python holidays.py 명령어로 업데이트
    추후 프로그램에 사용할 때는 JSON 파일을 읽어오는 형태로 사용.

    TODO: 정기 실행을 사람 손 안 태우고 할 수는 없을까? 5월에 1번만(5월에 이미 했다면, 실행 하지 않도록)
    """
    url = (
        "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
    )

    params = {
        "serviceKey": os.environ.get("API_KEY"),
        "solYear": "2025",
        "numOfRows": "100",
    }
    try:
        response = requests.get(url, params=params)

        # response.content는 bytes이므로, decode('utf-8')로 문자열로 변환
        xml_str = response.content.decode("utf-8")

        # XML 파싱
        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_str)

        # 공휴일 정보 추출
        items = root.findall(".//item")
        holidays = []
        for item in items:
            date_name = item.find("dateName").text  # type: ignore
            locdate = item.find("locdate").text  # type: ignore
            holidays.append({"name": date_name, "yyyymmdd": locdate})

        # holidays.json 파일로 저장
        import json

        with open("holidays.json", "w", encoding="utf-8") as f:
            json.dump(holidays, f, ensure_ascii=False, indent=2)

        # 결과 출력, 추후 log 파일로 저장
        print("holidays.json 파일이 생성되었습니다.")

    except Exception as e:
        print(e)  # TODO: 추후 로그파일로 기록


if __name__ == "__main__":
    get_holidays()
