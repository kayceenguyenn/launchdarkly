from flask import Blueprint, jsonify
from services.yfinance_service import get_fundamentals_data

fundamentals_bp = Blueprint("fundamentals", __name__)


@fundamentals_bp.route("/fundamentals/<ticker>")
def get_fundamentals(ticker):
    data = get_fundamentals_data(ticker)
    if not data:
        return jsonify({"error": "Ticker not found"}), 404
    return jsonify(data)
