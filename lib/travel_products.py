"""여행사 상품 데이터 접근 계층.

`data/mock_products.csv`(큐레이션 데이터)를 장기 기본 소스로 사용한다.
운영 중에는 코드 수정 없이 이 CSV만 갱신하면 화면에 즉시 반영된다.

여행사와 실제 제휴 API 계약이 체결되면, AGENCY_API_ADAPTERS에 해당 여행사의
조회 함수를 등록하는 것만으로 그 여행사 데이터만 실시간 연동으로 교체할 수
있다. 계약 전인 지금은 비어 있으며 전량 큐레이션 데이터로 응답한다.
"""

from pathlib import Path
from typing import Callable

import pandas as pd

DATA_PATH = Path(__file__).parent.parent / "data" / "mock_products.csv"

PRICE_COL_BY_TRIP_LENGTH = {"2박3일": "price_2n3d", "3박4일": "price_3n4d"}

# 여행사 고객센터 번호 및 예약 페이지. 번호는 여행사 사정에 따라 변경될 수 있다.
AGENCY_CONTACTS = {
    "하나투어": {"phone": "1577-1233", "url": "https://www.hanatour.com"},
    "모두투어": {"phone": "1544-5252", "url": "https://www.modetour.com"},
    "노랑풍선": {"phone": "1544-2288", "url": "https://www.ybtour.co.kr"},
    "마이리얼트립": {"phone": "1670-8208", "url": "https://www.myrealtrip.com"},
    "인터파크투어": {"phone": "1588-3443", "url": "https://tour.interpark.com"},
    "참좋은여행": {"phone": "1588-7557", "url": "https://www.verygoodtour.com"},
    "롯데관광": {"phone": "1577-3700", "url": "https://www.lottetour.com"},
    "온라인투어": {"phone": "1544-3663", "url": "https://www.onlinetour.co.kr"},
}

# 여행사별 실제 제휴 API 어댑터 등록소. 예: AGENCY_API_ADAPTERS["하나투어"] = hanatour_api.get_products
# (destination, trip_length) -> DataFrame[agency, product_type, product_name, price] 형태를 반환해야 한다.
AGENCY_API_ADAPTERS: dict[str, Callable[[str, str], pd.DataFrame]] = {}


def _load_curated_products() -> pd.DataFrame:
    # 작은 CSV라 캐싱하지 않는다 - 파일을 수정하면 다음 리런에 바로 반영된다.
    return pd.read_csv(DATA_PATH)


def get_products(destination: str, trip_length: str) -> pd.DataFrame:
    """여행지의 여행사 상품을 가져온다. AGENCY_API_ADAPTERS에 등록된 여행사는
    실제 API 응답을, 등록되지 않은 여행사는 큐레이션 CSV를 사용한다."""
    price_col = PRICE_COL_BY_TRIP_LENGTH.get(trip_length, "price_2n3d")

    curated = _load_curated_products()
    curated = curated[curated["destination"] == destination].copy()
    curated["price"] = curated[price_col]

    frames = []
    for agency, group in curated.groupby("agency", sort=False):
        adapter = AGENCY_API_ADAPTERS.get(agency)
        frames.append(adapter(destination, trip_length) if adapter else group)
    result = pd.concat(frames, ignore_index=True) if frames else curated

    result["phone"] = result["agency"].map(lambda a: AGENCY_CONTACTS.get(a, {}).get("phone", "-"))
    result["booking_url"] = result["agency"].map(lambda a: AGENCY_CONTACTS.get(a, {}).get("url", ""))
    return result[
        ["agency", "product_type", "product_name", "price", "phone", "booking_url"]
    ].reset_index(drop=True)


def price_range_summary(products: pd.DataFrame) -> tuple[int, int]:
    if products.empty:
        return 0, 0
    return int(products["price"].min()), int(products["price"].max())
