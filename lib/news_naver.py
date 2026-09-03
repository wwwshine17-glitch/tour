import re
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

NAVER_NEWS_ENDPOINT = "https://openapi.naver.com/v1/search/news.json"

# PRD 카테고리(안전/치안, 축제/이벤트, 교통/항공편)에 대응하는 검색 키워드.
# 실제 연동 후 결과 품질을 보고 키워드를 다듬어야 한다.
CATEGORY_QUERY_KEYWORDS = {
    "안전치안": "안전",
    "축제이벤트": "축제",
    "교통항공편": "교통",
}

_TAG_RE = re.compile(r"<[^>]+>")


def _clean_text(text: str) -> str:
    return _TAG_RE.sub("", text).replace("&quot;", '"').replace("&amp;", "&")


def _parse_pub_date(pub_date: str) -> str:
    try:
        return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
    except ValueError:
        return pub_date


def fetch_naver_news(destination: str) -> dict[str, pd.DataFrame]:
    """네이버 뉴스 검색 API로 여행지별 뉴스를 카테고리별로 조회한다.

    st.secrets["NAVER_CLIENT_ID"]/["NAVER_CLIENT_SECRET"]가 없거나
    (.streamlit/secrets.toml 미설정), 호출/파싱에 실패하면 예외를 던진다.
    호출부(lib/news.py)는 이 예외를 받아 mock 데이터로 대체한다.
    """
    headers = {
        "X-Naver-Client-Id": st.secrets["NAVER_CLIENT_ID"],
        "X-Naver-Client-Secret": st.secrets["NAVER_CLIENT_SECRET"],
    }

    result = {}
    for category, keyword in CATEGORY_QUERY_KEYWORDS.items():
        response = requests.get(
            NAVER_NEWS_ENDPOINT,
            headers=headers,
            params={"query": f"{destination} {keyword}", "display": 3, "sort": "date"},
            timeout=5,
        )
        response.raise_for_status()
        items = response.json()["items"]
        rows = [
            {
                "headline": _clean_text(item["title"]),
                "date": _parse_pub_date(item["pubDate"]),
                "source": "네이버 뉴스",
            }
            for item in items
        ]
        result[category] = pd.DataFrame(rows, columns=["headline", "date", "source"])
    return result
