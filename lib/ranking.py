import pandas as pd

IDEAL_TEMP = 22.0


def rank_destinations(weather_df: pd.DataFrame) -> pd.DataFrame:
    df = weather_df.copy()
    df["score"] = 100 - (df["avg_temp"] - IDEAL_TEMP).abs() * 2 - df["precip_chance"] * 0.5
    return df.sort_values("score", ascending=False).reset_index(drop=True)
