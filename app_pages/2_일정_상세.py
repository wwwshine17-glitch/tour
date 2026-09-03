import streamlit as st

from lib.itinerary import generate_itinerary
from lib.news import get_news_briefing
from lib.style import render_footer
from lib.travel_products import get_products, price_range_summary

NEWS_CATEGORY_LABELS = {
    "안전치안": ("안전 · 치안", ":material/shield:"),
    "축제이벤트": ("축제 · 이벤트", ":material/celebration:"),
    "교통항공편": ("교통 · 항공편", ":material/flight:"),
}

st.title("여행지 추천정보")

destination = st.session_state.get("selected_destination")
trip_length = st.session_state.get("selected_trip_length")

if not destination:
    st.info("먼저 여행 추천 페이지에서 여행지를 선택해 주세요.")
    if st.button("여행 추천으로 이동"):
        st.switch_page("app_pages/1_여행_추천.py")
else:
    st.caption(f"{trip_length} · {destination}의 일정, 비용정보, 뉴스 브리핑을 확인합니다.")
    if st.button("다시 추천받기", icon=":material/refresh:"):
        st.session_state.pop("selected_destination", None)
        st.session_state.pop("selected_trip_length", None)
        st.switch_page("app_pages/1_여행_추천.py")

    with st.spinner(f"{destination} 정보를 불러오는 중입니다..."):
        itinerary = generate_itinerary(destination, trip_length)
        products = get_products(destination, trip_length)
        briefing = get_news_briefing(destination)

    tab_itinerary, tab_price, tab_news = st.tabs(["일정", "비용정보", "뉴스 브리핑"])

    with tab_itinerary:
        for day_plan in itinerary:
            with st.expander(f"Day {day_plan['day']}", expanded=day_plan["day"] == 1):
                st.write(f"**오전** · {day_plan['오전']}")
                st.write(f"**오후** · {day_plan['오후']}")
                st.write(f"**저녁** · {day_plan['저녁']}")

    with tab_price:
        if products.empty:
            st.info("등록된 상품 정보가 없습니다.")
        else:
            low, high = price_range_summary(products)
            st.metric("예상 비용대 (1인 기준)", f"{low:,}원 ~ {high:,}원")
            st.caption("가격 정보는 정기 갱신되는 큐레이션 데이터 기준입니다.")

            table_rows = ["| 여행사 | 상품유형 | 상품명 | 비용(원) | 연락처 |", "|---|---|---|---|---|"]
            for _, row in products.iterrows():
                contact = f"[{row['phone']}]({row['booking_url']})" if row["booking_url"] else row["phone"]
                table_rows.append(
                    f"| {row['agency']} | {row['product_type']} | {row['product_name']} | "
                    f"{row['price']:,} | {contact} |"
                )
            st.markdown("\n".join(table_rows))
            st.caption("연락처를 클릭하면 해당 여행사의 예약 페이지로 이동합니다.")

    with tab_news:
        for category, (label, icon) in NEWS_CATEGORY_LABELS.items():
            with st.container(border=True):
                st.markdown(f"**{icon} {label}**")
                items = briefing[category]
                if items.empty:
                    st.caption("관련 뉴스가 없습니다.")
                else:
                    for _, item in items.iterrows():
                        st.write(f"- {item['headline']} ({item['date']}, {item['source']})")

render_footer()
