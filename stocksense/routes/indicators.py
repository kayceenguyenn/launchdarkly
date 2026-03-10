import uuid
import time
import ldclient
import pandas as pd
from flask import Blueprint, request, jsonify
from services.yfinance_service import get_history_data
from launchdarkly_client import ld_client

indicators_bp = Blueprint("indicators", __name__)


def compute_rsi(closes: pd.Series, period: int = 14) -> float:
    delta = closes.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(window=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(float(100 - (100 / (1 + rs))), 2)


def compute_macd(closes: pd.Series) -> dict:
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd_line": round(float(macd_line.iloc[-1]), 4),
        "signal_line": round(float(signal_line.iloc[-1]), 4),
        "histogram": round(float(histogram.iloc[-1]), 4),
    }


@indicators_bp.route("/indicators/<ticker>")
def get_indicators(ticker):
    user_key = request.args.get("user_key", str(uuid.uuid4()))
    user_type = request.args.get("user_type", "free")
    context = ldclient.Context.builder(user_key).kind("user").set("user_type", user_type).build()

    try:
        variation = ld_client.variation("technical-indicator-algorithm", context, "fast")
    except Exception:
        variation = "fast"

    sma_period = 10 if variation == "fast" else 50
    required_period = "3mo" if variation == "fast" else "1y"

    df = get_history_data(ticker, period=required_period, interval="1d")
    if df is None or df.empty:
        return jsonify({"error": "Ticker not found"}), 404

    start = time.time()

    closes = df["Close"]
    sma = round(float(closes.tail(sma_period).mean()), 4)
    rsi = compute_rsi(closes)
    macd = compute_macd(closes)

    elapsed_ms = round((time.time() - start) * 1000, 2)

    try:
        ld_client.track("indicator-response-time-ms", context, None, elapsed_ms)
    except Exception:
        pass

    return jsonify({
        "ticker": ticker.upper(),
        "algorithm_variation": variation,
        "sma": sma,
        "sma_period_days": sma_period,
        "rsi_14": rsi,
        "macd": macd,
        "computation_time_ms": elapsed_ms,
    })
