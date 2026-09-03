from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "data" / "destinations_kr.csv"


@st.cache_data
def load_destinations() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


MIN_CANDIDATES = 3


def get_candidate_destinations(regions: list[str] | None = None) -> pd.DataFrame:
    df = load_destinations()
    filtered = df[df["region"].isin(regions)] if regions else df
    if regions and len(filtered) < MIN_CANDIDATES:
        remaining = df[~df["name"].isin(filtered["name"])]
        filtered = pd.concat([filtered, remaining.head(MIN_CANDIDATES - len(filtered))])
    return filtered.reset_index(drop=True)
