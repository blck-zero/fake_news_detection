from flask import Blueprint, jsonify, request

from backend.utils.db import list_predictions


history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
def history():
    limit = request.args.get("limit", default="200")
    try:
        limit_int = int(limit)
    except ValueError:
        limit_int = 200

    return jsonify({"history": list_predictions(limit=limit_int)})

