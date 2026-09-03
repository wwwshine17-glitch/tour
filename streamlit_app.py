import streamlit as st

st.set_page_config(page_title="웨더트립", page_icon=":material/travel_explore:", layout="wide")

recommend_page = st.Page(
    "app_pages/1_여행_추천.py",
    title="여행 추천",
    icon=":material/travel_explore:",
    default=True,
)
detail_page = st.Page(
    "app_pages/2_일정_상세.py",
    title="여행지 추천정보",
    icon=":material/map:",
)

nav = st.navigation([recommend_page, detail_page])
nav.run()
