# 웨더트립 (WeatherTrip)

날씨 비교 기반 여행지 추천 + 여행사 트렌드 반영 일정·비용 + 여행지 뉴스 브리핑을
제공하는 Streamlit 웹앱입니다. 여행 기간(2박3일/3박4일)만 입력하면 후보 여행지의
날씨를 비교해 추천하고, 여행지별 일정·비용·뉴스를 한 화면에서 확인할 수 있습니다.

## 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 앱 실행
streamlit run streamlit_app.py
```

브라우저에서 http://localhost:8501 로 접속하면 됩니다.

## 실시간 API 연동 (선택 사항)

아래 API 키가 없어도 앱은 정상 동작합니다 (예시 데이터로 자동 대체되며,
화면에 "실시간 연동 전 - 예시 데이터 표시 중" 안내가 뜹니다). 실시간 데이터를
쓰려면 `.streamlit/secrets.toml` 파일을 만들고 아래 키를 채워 넣으세요
(이 파일은 `.gitignore`에 포함되어 있어 저장소에 올라가지 않습니다).

```toml
# .streamlit/secrets.toml
KMA_API_KEY = "공공데이터포털에서 발급받은 기상청 API 키"
NAVER_CLIENT_ID = "네이버 개발자센터에서 발급받은 Client ID"
NAVER_CLIENT_SECRET = "네이버 개발자센터에서 발급받은 Client Secret"
```

| 키 | 용도 | 미설정 시 동작 |
|---|---|---|
| `KMA_API_KEY` | 기상청 초단기실황 API로 실시간 날씨 조회 (`lib/weather_kma.py`) | 결정론적 예시 날씨 데이터 사용 |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | 네이버 뉴스 검색 API로 실시간 뉴스 조회 (`lib/news_naver.py`) | 큐레이션된 예시 뉴스 데이터 사용 |

여행사 상품 데이터(`data/mock_products.csv`)는 8개 여행사와의 제휴 API 계약이
체결되지 않아, 정기적으로 갱신하는 큐레이션 데이터를 정식 기본 소스로 사용합니다.
계약이 체결되면 `lib/travel_products.py`의 `AGENCY_API_ADAPTERS`에 해당 여행사의
조회 함수를 등록하는 것만으로 그 여행사만 실시간 연동으로 교체할 수 있습니다.

## 프로젝트 구조

```
weathertrip-app/
├── streamlit_app.py        # 진입점 (네비게이션 배선)
├── app_pages/
│   ├── 1_여행_추천.py       # 입력 폼 + 날씨 비교 추천 카드
│   └── 2_일정_상세.py       # 선택 여행지의 일정/비용/뉴스 (탭 3개)
├── lib/                     # 데이터·비즈니스 로직
├── data/                    # 여행지/상품/뉴스 큐레이션 CSV
├── .streamlit/
│   ├── config.toml          # 테마
│   └── secrets.toml         # API 키 (직접 생성, gitignore 대상)
└── requirements.txt
```

## 배포 (Streamlit Community Cloud)

1. 이 폴더를 GitHub 저장소로 푸시합니다 (`.venv/`, `secrets.toml`은 이미
   `.gitignore`에 포함되어 있어 올라가지 않습니다).
2. [share.streamlit.io](https://share.streamlit.io)에서 저장소를 연결하고
   Main file path를 `streamlit_app.py`로 지정합니다.
3. 실시간 API를 쓰려면 앱 설정의 "Secrets"에 위 `.streamlit/secrets.toml`과
   동일한 내용을 입력합니다. 입력하지 않아도 예시 데이터로 정상 배포됩니다.
