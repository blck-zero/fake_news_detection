from flask import Blueprint, jsonify, request

from backend.services.inference_service import inference_service
from backend.services.scraping_service import scrape_url_text
from backend.utils.db import init_db, insert_prediction


prediction_bp = Blueprint("prediction", __name__)


def _bad_request(message: str, details=None):
    payload = {"error": "bad_request", "message": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), 400


@prediction_bp.route("/predict-text", methods=["POST"])
def predict_text():
    init_db()

    data = request.get_json(silent=True)
    if not data:
        return _bad_request("Request body must be JSON.")

    text = (data.get("text") or "").strip()
    if not text:
        return _bad_request("`text` is required.")
    if len(text) < 20:
        return _bad_request("`text` is too short. Paste a longer news article.")
    if len(text) > 50000:
        return _bad_request("`text` is too long.")

    try:
        result = inference_service.predict(text)
    except RuntimeError as e:
        return jsonify({"error": "model_missing", "message": str(e)}), 503
    except Exception as e:
        return jsonify({"error": "prediction_failed", "message": str(e)}), 500

    insert_prediction(
        input_type="text",
        input_value=text,
        extracted_text=None,
        prediction=result.prediction,
        confidence=result.confidence,
        sentiment=result.sentiment,
        keywords=result.keywords,
    )

    return jsonify(
        {
            "prediction": result.prediction,
            "confidence": round(result.confidence, 4),
            "sentiment": result.sentiment,
            "keywords": result.keywords,
        }
    )


@prediction_bp.route("/predict-url", methods=["POST"])
def predict_url():
    init_db()

    data = request.get_json(silent=True)
    if not data:
        return _bad_request("Request body must be JSON.")

    url = (data.get("url") or "").strip()
    if not url:
        return _bad_request("`url` is required.")
    if len(url) < 10:
        return _bad_request("`url` looks too short.")

    try:
        extracted_text = scrape_url_text(url)
        result = inference_service.predict(extracted_text)
    except ValueError as e:
        return _bad_request(str(e))
    except RuntimeError as e:
        return jsonify({"error": "model_missing", "message": str(e)}), 503
    except Exception as e:
        return jsonify({"error": "prediction_failed", "message": str(e)}), 500

    insert_prediction(
        input_type="url",
        input_value=url,
        extracted_text=extracted_text,
        prediction=result.prediction,
        confidence=result.confidence,
        sentiment=result.sentiment,
        keywords=result.keywords,
    )

    return jsonify(
        {
            "prediction": result.prediction,
            "confidence": round(result.confidence, 4),
            "sentiment": result.sentiment,
            "keywords": result.keywords,
            "extracted_text": extracted_text,
        }
    )

