from pathlib import Path

import pandas as pd
import streamlit as st

from lib.news_naver import fetch_naver_news

DATA_PATH = Path(__file__).parent.parent / "data" / "mock_news.csv"

CATEGORIES = ["안전치안", "축제이벤트", "교통항공편"]


def _load_mock_news() -> pd.DataFrame:
    # 작은 CSV라 캐싱하지 않는다 - 파일을 수정하면 다음 리런에 바로 반영된다.
    return pd.read_csv(DATA_PATH)


def _mock_news_briefing(destination: str) -> dict[str, pd.DataFrame]:
    df = _load_mock_news()
    df = df[df["destination"] == destination]
    return {
        category: df[df["category"] == category]
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
        for category in CATEGORIES
    }


@st.cache_data(ttl=300)
def get_news_briefing(destination: str) -> dict[str, pd.DataFrame]:
    """여행지의 뉴스 브리핑을 가져온다. 네이버 뉴스 API 키(.streamlit/secrets.toml의
    NAVER_CLIENT_ID/NAVER_CLIENT_SECRET)가 설정되어 있으면 실시간 뉴스를, 없거나
    호출에 실패하면 예시(mock) 데이터로 자동 대체한다."""
    try:
        return fetch_naver_news(destination)
    except Exception:
        st.info("실시간 뉴스 연동 전 - 예시 데이터 표시 중입니다.")
        return _mock_news_briefing(destination)
