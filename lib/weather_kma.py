from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

KMA_ENDPOINT = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 기상청 격자 좌표(nx, ny). 실제 연동 전 재검증이 필요한 근사값이다.
GRID_BY_DESTINATION = {
    "제주": (52, 38),
    "강릉": (92, 131),
    "속초": (87, 141),
    "춘천": (73, 134),
    "경주": (100, 91),
    "안동": (91, 106),
    "전주": (63, 89),
    "여수": (73, 66),
    "부산": (98, 76),
    "통영": (87, 68),
    "강화도": (51, 130),
    "태안": (95, 131),
    "인천": (55, 124),
    "가평": (68, 134),
    "보령": (66, 120),
    "단양": (98, 125),
    "서귀포": (52, 33),
    "우도": (57, 34),
    "순천": (70, 66),
    "포항": (102, 94),
    "거제": (90, 69),
}


def _latest_base_time(now: datetime) -> tuple[str, str]:
    """초단기실황은 매시 40분 이후 발표된다."""
    if now.minute < 40:
        now = now - timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H00")


def fetch_kma_weather(destinations: pd.DataFrame) -> pd.DataFrame:
    """기상청 초단기실황 API로 후보 여행지의 실제 날씨를 조회한다.

    st.secrets["KMA_API_KEY"]가 없거나(.streamlit/secrets.toml 미설정),
    좌표 매핑이 없는 여행지가 포함되어 있거나, 호출/응답 파싱에 실패하면
    예외를 던진다. 호출부(lib/weather.py)는 이 예외를 받아 mock 데이터로
    대체한다.
    """
    api_key = st.secrets["KMA_API_KEY"]
    base_date, base_time = _latest_base_time(datetime.now())

    rows = []
    for _, dest in destinations.iterrows():
        nx, ny = GRID_BY_DESTINATION[dest["name"]]
        response = requests.get(
            KMA_ENDPOINT,
            params={
                "serviceKey": api_key,
                "dataType": "JSON",
                "base_date": base_date,
                "base_time": base_time,
                "nx": nx,
                "ny": ny,
                "numOfRows": 10,
                "pageNo": 1,
            },
            timeout=5,
        )
        response.raise_for_status()
        items = response.json()["response"]["body"]["items"]["item"]
        values = {item["category"]: item["obsrValue"] for item in items}

        temp = float(values["T1H"])
        is_raining = values.get("PTY", "0") != "0"
        humidity = float(values.get("REH", 50))
        if is_raining:
            condition, precip_chance = "비", 80
        elif humidity >= 70:
            condition, precip_chance = "흐림", 40
        elif humidity >= 55:
            condition, precip_chance = "구름 조금", 20
        else:
            condition, precip_chance = "맑음", 5

        rows.append(
            {
                "name": dest["name"],
                "region": dest["region"],
                "tags": dest["tags"],
                "avg_temp": round(temp, 1),
                "precip_chance": precip_chance,
                "condition": condition,
            }
        )
    return pd.DataFrame(rows)
