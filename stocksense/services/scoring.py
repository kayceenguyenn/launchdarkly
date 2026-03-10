import pandas as pd


def compute_simple_score(price: float) -> float:
    return round(price, 4)


def compute_advanced_score(history_df: pd.DataFrame) -> float:
    recent = history_df.tail(5)

    vwap = (recent["Close"] * recent["Volume"]).sum() / recent["Volume"].sum()

    price_5d_ago = recent["Close"].iloc[0]
    price_now = recent["Close"].iloc[-1]
    momentum = ((price_now - price_5d_ago) / price_5d_ago) * 100

    avg_volume_30d = history_df.tail(30)["Volume"].mean()
    today_volume = recent["Volume"].iloc[-1]
    rel_volume = today_volume / avg_volume_30d if avg_volume_30d > 0 else 1.0

    score = (vwap * 0.5) + (momentum * 0.3) + (rel_volume * 0.2)
    return round(float(score), 4)
