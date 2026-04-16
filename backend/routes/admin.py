from flask import Blueprint, jsonify

from backend.utils.db import admin_stats


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/stats", methods=["GET"])
def stats():
    return jsonify(admin_stats())

