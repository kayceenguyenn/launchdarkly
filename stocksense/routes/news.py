from flask import Blueprint, request, jsonify
from services.yfinance_service import get_news_data

news_bp = Blueprint("news", __name__)


@news_bp.route("/news/<ticker>")
def get_news(ticker):
    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400

    articles = get_news_data(ticker, limit=limit)
    return jsonify({
        "ticker": ticker.upper(),
        "news": articles,
    })
