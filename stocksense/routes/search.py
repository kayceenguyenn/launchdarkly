from flask import Blueprint, request, jsonify
from services.yfinance_service import search_tickers

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    q = request.args.get("q")
    if not q:
        return jsonify({"error": "Missing required param: q"}), 400

    results = search_tickers(q)
    return jsonify({
        "query": q,
        "results": results,
    })
