import uuid
from flask import Blueprint, request, jsonify
from services.yfinance_service import get_quote_data, get_history_data
from services.scoring import compute_simple_score, compute_advanced_score
from launchdarkly_client import ld_client

quote_bp = Blueprint("quote", __name__)


@quote_bp.route("/quote/<ticker>")
def get_quote(ticker):
    user_key = request.args.get("user_key", str(uuid.uuid4()))
    context = {"kind": "user", "key": user_key}

    quote = get_quote_data(ticker)
    if not quote:
        return jsonify({"error": "Ticker not found"}), 404

    try:
        algorithm = ld_client.variation("price-scoring-algorithm", context, "simple")
    except Exception:
        algorithm = "simple"

    if algorithm == "advanced":
        history = get_history_data(ticker, period="3mo", interval="1d")
        if history is not None and len(history) >= 5:
            score = compute_advanced_score(history)
        else:
            score = compute_simple_score(quote["price"])
            algorithm = "simple"
    else:
        score = compute_simple_score(quote["price"])

    return jsonify({
        **quote,
        "score": score,
        "score_method": algorithm,
    })
