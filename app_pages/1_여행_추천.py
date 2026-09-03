import streamlit as st

from lib.destinations import get_candidate_destinations
from lib.ranking import rank_destinations
from lib.style import render_footer
from lib.weather import get_weather_scores

st.title("신나는 여행")
st.caption("여행 기간을 입력하면 날씨 좋은 여행지를 비교해 추천합니다.")

REGION_OPTIONS = ["수도권", "강원", "충청", "전라", "경북", "부산/경남", "제주"]

with st.form("trip_input_form"):
    trip_length = st.segmented_control(
        "여행 기간",
        options=["2박3일", "3박4일"],
    )
    regions = st.pills(
        "관심 지역 (선택하지 않으면 전체 지역 대상)",
        options=REGION_OPTIONS,
        selection_mode="multi",
    )
    submitted = st.form_submit_button("추천받기", type="primary")

CONDITION_EMOJI = {
    "맑음": "☀️",
    "구름 조금": "🌤️",
    "흐림": "☁️",
    "비": "🌧️",
}

if submitted:
    if not trip_length:
        st.warning("여행 기간을 선택해 주세요.")
        st.session_state.pop("ranked_destinations", None)
    else:
        with st.spinner("날씨를 비교해 여행지를 추천하는 중입니다..."):
            candidates = get_candidate_destinations(regions)
            if candidates.empty:
                weather_df = None
            else:
                weather_df = get_weather_scores(candidates, trip_length)

        if candidates.empty:
            st.info("선택한 지역에 해당하는 여행지가 없습니다. 다른 지역을 선택해 주세요.")
            st.session_state.pop("ranked_destinations", None)
        else:
            if regions and not candidates["region"].isin(regions).all():
                st.caption("선택하신 지역에 여행지가 적어 다른 지역을 일부 포함해 추천합니다.")
            st.session_state["ranked_destinations"] = rank_destinations(weather_df)
            st.session_state["trip_length"] = trip_length

if "ranked_destinations" in st.session_state:
    ranked_df = st.session_state["ranked_destinations"]
    selected_trip_length = st.session_state["trip_length"]

    st.divider()
    st.subheader(f"{selected_trip_length} 추천 여행지")

    top_df = ranked_df.head(6).reset_index(drop=True)
    n_cols = 3
    for start in range(0, len(top_df), n_cols):
        chunk = top_df.iloc[start : start + n_cols]
        cols = st.columns(n_cols)
        for i, (_, dest) in enumerate(chunk.iterrows()):
            rank = start + i + 1
            with cols[i]:
                with st.container(border=True):
                    emoji = CONDITION_EMOJI.get(dest["condition"], "🌈")
                    st.markdown(f"**{rank}위 · {dest['name']}** ({dest['region']})")
                    st.write(
                        f"{emoji} {dest['condition']} · 평균 {dest['avg_temp']}℃ · "
                        f"강수확률 {dest['precip_chance']}%"
                    )
                    st.caption(f"태그: {dest['tags']}")
                    if st.button(
                        "여행일정 및 상세정보",
                        key=f"detail_btn_{dest['name']}",
                        width="stretch",
                    ):
                        st.session_state["selected_destination"] = dest["name"]
                        st.session_state["selected_trip_length"] = selected_trip_length
                        st.switch_page("app_pages/2_일정_상세.py")

render_footer()
