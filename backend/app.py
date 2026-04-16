import os
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

from backend.routes.prediction import prediction_bp
from backend.routes.history import history_bp
from backend.routes.admin import admin_bp
from backend.utils.db import init_db


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///fake_news.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False

    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}},
    )

    # Ensure prediction history table exists.
    init_db()

    app.register_blueprint(prediction_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

    @app.errorhandler(400)
    def handle_400(err):
        return jsonify({"error": "bad_request", "message": str(err)}), 400

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify({"error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_500(err):
        return (
            jsonify(
                {
                    "error": "server_error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

