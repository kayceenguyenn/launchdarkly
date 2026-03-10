from datetime import datetime, timezone
from flask import Blueprint, jsonify
from services.yfinance_service import get_movers_data

movers_bp = Blueprint("movers", __name__)


@movers_bp.route("/movers")
def get_movers():
    data = get_movers_data()
    if data is None:
        return jsonify({"error": "Data source unavailable"}), 503

    return jsonify({
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gainers": data["gainers"],
        "losers": data["losers"],
    })
