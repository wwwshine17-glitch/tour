import hashlib
import random
from datetime import date

import pandas as pd
import streamlit as st

from lib.weather_kma import fetch_kma_weather

CONDITIONS = ["맑음", "구름 조금", "흐림", "비"]


def _seed_for(name: str) -> int:
    today = date.today().isoformat()
    digest = hashlib.sha256(f"{name}-{today}".encode()).hexdigest()
    return int(digest[:8], 16)


def _mock_weather(destinations: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, dest in destinations.iterrows():
        rng = random.Random(_seed_for(dest["name"]))
        avg_temp = round(rng.uniform(15, 29), 1)
        precip_chance = rng.randint(0, 80)
        condition = CONDITIONS[min(precip_chance // 25, len(CONDITIONS) - 1)]
        rows.append(
            {
                "name": dest["name"],
                "region": dest["region"],
                "tags": dest["tags"],
                "avg_temp": avg_temp,
                "precip_chance": precip_chance,
                "condition": condition,
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=600)
def get_weather_scores(destinations: pd.DataFrame, trip_length: str) -> pd.DataFrame:
    """후보 여행지의 날씨를 조회한다. 기상청 API 키(.streamlit/secrets.toml의
    KMA_API_KEY)가 설정되어 있으면 실시간 데이터를 쓰고, 키가 없거나 호출에
    실패하면 예시(mock) 데이터로 자동 대체한다."""
    try:
        return fetch_kma_weather(destinations)
    except Exception:
        st.info("실시간 날씨 연동 전 - 예시 데이터 표시 중입니다.")
        return _mock_weather(destinations)
