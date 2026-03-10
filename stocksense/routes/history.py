import uuid
from flask import Blueprint, request, jsonify
from services.yfinance_service import get_history_data

history_bp = Blueprint("history", __name__)

VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"}
VALID_INTERVALS = {"1d", "1wk", "1mo"}


@history_bp.route("/history/<ticker>")
def get_history(ticker):
    period = request.args.get("period", "1mo")
    interval = request.args.get("interval", "1d")

    if period not in VALID_PERIODS:
        return jsonify({"error": f"Invalid period. Valid values: {', '.join(sorted(VALID_PERIODS))}"}), 400
    if interval not in VALID_INTERVALS:
        return jsonify({"error": f"Invalid interval. Valid values: {', '.join(sorted(VALID_INTERVALS))}"}), 400

    df = get_history_data(ticker, period=period, interval=interval)
    if df is None:
        return jsonify({"error": "Ticker not found"}), 404

    data = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        }
        for date, row in df.iterrows()
    ]

    return jsonify({
        "ticker": ticker.upper(),
        "period": period,
        "interval": interval,
        "data": data,
    })
