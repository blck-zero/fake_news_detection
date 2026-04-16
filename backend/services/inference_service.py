import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import joblib

from backend.utils.keywords import extract_top_keywords
from backend.utils.sentiment import analyze_sentiment
from backend.utils.text_processing import preprocess_for_vectorizer


@dataclass(frozen=True)
class PredictionResult:
    prediction: str  # REAL | FAKE
    confidence: float  # percentage 0..100
    sentiment: str  # positive | negative | neutral
    keywords: List[str]
    proba: Tuple[float, float]  # (p_real, p_fake)


def _default_artifact_paths() -> Tuple[str, str]:
    base_dir = os.path.join(os.path.dirname(__file__), "..", "model", "artifacts")
    model_path = os.path.abspath(os.path.join(base_dir, "model.joblib"))
    vectorizer_path = os.path.abspath(os.path.join(base_dir, "vectorizer.pkl"))
    return model_path, vectorizer_path


class InferenceService:
    def __init__(self, model_path: Optional[str] = None, vectorizer_path: Optional[str] = None):
        self.model_path, self.vectorizer_path = _default_artifact_paths()
        if model_path:
            self.model_path = model_path
        if vectorizer_path:
            self.vectorizer_path = vectorizer_path

        self._model = None
        self._vectorizer = None

    def load(self) -> None:
        if not os.path.exists(self.model_path) or not os.path.exists(self.vectorizer_path):
            raise RuntimeError(
                "Model artifacts missing. Run training: python backend/model/train.py --csv <path>."
            )
        self._model = joblib.load(self.model_path)
        self._vectorizer = joblib.load(self.vectorizer_path)

    def is_loaded(self) -> bool:
        return self._model is not None and self._vectorizer is not None

    def predict(self, text: str, top_k_keywords: int = 8) -> PredictionResult:
        if not self.is_loaded():
            self.load()

        prepared = preprocess_for_vectorizer(text)
        # Vectorizer expects space-separated tokens produced by preprocess_for_vectorizer.
        tfidf_row = self._vectorizer.transform([prepared])

        # LogisticRegression supports predict_proba; for robustness, fall back to decision_function.
        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(tfidf_row)[0]  # [p_class0, p_class1]
        else:
            scores = self._model.decision_function(tfidf_row)[0]
            # Simple sigmoid mapping from score to probability of class 1.
            prob1 = 1.0 / (1.0 + pow(2.718281828, -float(scores)))
            proba = [1.0 - prob1, prob1]

        # Training maps {0: REAL, 1: FAKE}.
        p_real, p_fake = float(proba[0]), float(proba[1])
        confidence = max(p_real, p_fake) * 100.0
        prediction = "REAL" if p_real >= p_fake else "FAKE"
        sentiment_result = analyze_sentiment(text)
        keywords = extract_top_keywords(self._vectorizer, tfidf_row, top_k=top_k_keywords)

        return PredictionResult(
            prediction=prediction,
            confidence=confidence,
            sentiment=sentiment_result.label,
            keywords=keywords,
            proba=(p_real, p_fake),
        )


# Singleton instance used by routes to avoid repeated disk loads.
inference_service = InferenceService(
    model_path=os.getenv("MODEL_PATH") or None,
    vectorizer_path=os.getenv("VECTORIZER_PATH") or None,
)

