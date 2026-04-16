import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
import csv
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

from backend.utils.text_processing import preprocess_for_vectorizer


@dataclass(frozen=True)
class TrainConfig:
    vectorizer_ngram_range: Tuple[int, int] = (1, 2)
    vectorizer_max_features: int = 50000
    vectorizer_min_df: int = 2
    test_size: float = 0.2
    random_state: int = 42


LABEL_TRUE = {"true", "real", "1", "positive"}
LABEL_FALSE = {"false", "fake", "0", "negative"}


def map_label_to_binary(raw_label: Any) -> int:
    """
    Map dataset labels into {0: REAL, 1: FAKE}.
    Supports common ISOT/LIAR-style labels (true/false) and boolean-ish values.
    """
    if raw_label is None or (isinstance(raw_label, float) and np.isnan(raw_label)):
        raise ValueError("Missing label")

    s = str(raw_label).strip().lower()
    if s in LABEL_TRUE:
        return 0
    if s in LABEL_FALSE:
        return 1

    # Fallback: treat unknown strings containing 'fake'/'false' as fake.
    if "fake" in s or "false" in s:
        return 1
    if "real" in s or "true" in s:
        return 0
    raise ValueError(f"Unrecognized label: {raw_label}")


def load_dataset(csv_path: str) -> Tuple[List[str], List[int]]:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row.")
        columns = list(reader.fieldnames)

        # Accept common column names.
        text_col = None
        for candidate in ("text", "statement", "content", "article"):
            if candidate in columns:
                text_col = candidate
                break
        if text_col is None:
            raise ValueError(
                f"CSV must have a text column (one of: text, statement, content, article). Found: {columns}"
            )

        label_col = None
        for candidate in ("label", "target", "class"):
            if candidate in columns:
                label_col = candidate
                break
        if label_col is None:
            raise ValueError(
                f"CSV must have a label column (one of: label, target, class). Found: {columns}"
            )

        texts: List[str] = []
        labels: List[int] = []
        for row in reader:
            raw_text = row.get(text_col)
            raw_label = row.get(label_col)
            if raw_text is None or raw_text == "":
                continue

            if isinstance(raw_label, float) and np.isnan(raw_label):
                continue
            labels.append(map_label_to_binary(raw_label))
            texts.append(preprocess_for_vectorizer(str(raw_text)))

    if len(texts) < 10:
        print(f"Warning: very small dataset loaded: {len(texts)} rows")
    return texts, labels


def train_and_save(
    csv_path: str,
    out_dir: str,
    config: TrainConfig,
) -> Dict[str, Any]:
    os.makedirs(out_dir, exist_ok=True)

    X_text, y = load_dataset(csv_path)

    vectorizer = TfidfVectorizer(
        ngram_range=config.vectorizer_ngram_range,
        max_features=config.vectorizer_max_features,
        min_df=config.vectorizer_min_df,
        token_pattern=r"(?u)\b\w+\b",
        lowercase=False,  # we pre-lowercase in preprocess_for_vectorizer
    )

    X = vectorizer.fit_transform(X_text)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.random_state, stratify=y
    )

    clf = LogisticRegression(
        max_iter=2000,
        n_jobs=-1,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, digits=4)

    model_path = os.path.join(out_dir, "model.joblib")
    vectorizer_path = os.path.join(out_dir, "vectorizer.pkl")
    meta_path = os.path.join(out_dir, "metadata.json")

    joblib.dump(clf, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    metadata = {
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "label_mapping": {"0": "REAL", "1": "FAKE"},
        "config": asdict(config),
        "metrics": {"accuracy": acc, "classification_report": report},
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to CSV with text + label columns")
    parser.add_argument("--out-dir", default=os.path.join(os.path.dirname(__file__), "artifacts"))
    args = parser.parse_args()

    config = TrainConfig()
    metadata = train_and_save(
        csv_path=args.csv,
        out_dir=args.out_dir,
        config=config,
    )
    print(json.dumps(metadata["metrics"], indent=2))


if __name__ == "__main__":
    main()

