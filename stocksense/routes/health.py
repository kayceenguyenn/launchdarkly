from flask import Blueprint, jsonify
from launchdarkly_client import ld_client

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    try:
        initialized = ld_client.is_initialized()
    except Exception:
        initialized = False

    return jsonify({
        "status": "ok",
        "launchdarkly_initialized": initialized,
    })
