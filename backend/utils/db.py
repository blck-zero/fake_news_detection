import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def _parse_sqlite_path(database_url: str) -> str:
    """
    Parse `sqlite:///relative/path.db` or `sqlite:////abs/path.db`.
    Returns a filesystem path usable by sqlite3.
    """
    db_url = (database_url or "").strip()
    prefix = "sqlite:///"
    if db_url.startswith(prefix):
        path = db_url[len(prefix) :]
    elif db_url.startswith("sqlite://"):
        # e.g. sqlite:/absolute or sqlite:relative
        path = db_url[len("sqlite://") :]
        path = path.lstrip("/")
    else:
        # Fallback to allow passing a raw path.
        path = db_url

    # Make relative paths deterministic (relative to backend/ directory).
    if path and path != ":memory:" and not os.path.isabs(path):
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(backend_dir, path)

    return path


def get_db_path() -> str:
    database_url = os.getenv("DATABASE_URL", "sqlite:///fake_news.db")
    return _parse_sqlite_path(database_url)


def _connect() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              input_type TEXT NOT NULL,
              input_value TEXT NOT NULL,
              extracted_text TEXT,
              prediction TEXT NOT NULL,
              confidence REAL NOT NULL,
              sentiment TEXT,
              keywords_json TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_input_type ON predictions(input_type)")
        conn.commit()
    finally:
        conn.close()


def insert_prediction(
    *,
    input_type: str,
    input_value: str,
    extracted_text: Optional[str],
    prediction: str,
    confidence: float,
    sentiment: str,
    keywords: List[str],
) -> int:
    conn = _connect()
    try:
        created_at = datetime.utcnow().isoformat() + "Z"
        keywords_json = json.dumps(keywords, ensure_ascii=False)

        cur = conn.execute(
            """
            INSERT INTO predictions (
              created_at, input_type, input_value, extracted_text,
              prediction, confidence, sentiment, keywords_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                input_type,
                input_value,
                extracted_text,
                prediction,
                float(confidence),
                sentiment,
                keywords_json,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_predictions(limit: int = 200) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        limit = max(1, min(int(limit), 1000))
        rows = conn.execute(
            """
            SELECT id, created_at, input_type, input_value, extracted_text,
                   prediction, confidence, sentiment, keywords_json
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        results: List[Dict[str, Any]] = []
        for r in rows:
            results.append(
                {
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "input_type": r["input_type"],
                    "input_value": r["input_value"],
                    "extracted_text": r["extracted_text"],
                    "prediction": r["prediction"],
                    "confidence": r["confidence"],
                    "sentiment": r["sentiment"],
                    "keywords": json.loads(r["keywords_json"] or "[]"),
                }
            )
        return results
    finally:
        conn.close()


def admin_stats() -> Dict[str, Any]:
    conn = _connect()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM predictions").fetchone()["c"]
        fake = conn.execute("SELECT COUNT(*) AS c FROM predictions WHERE prediction = 'FAKE'").fetchone()[
            "c"
        ]
        real = conn.execute("SELECT COUNT(*) AS c FROM predictions WHERE prediction = 'REAL'").fetchone()[
            "c"
        ]

        text_count = conn.execute("SELECT COUNT(*) AS c FROM predictions WHERE input_type = 'text'").fetchone()[
            "c"
        ]
        url_count = conn.execute("SELECT COUNT(*) AS c FROM predictions WHERE input_type = 'url'").fetchone()[
            "c"
        ]

        def pct(n: int) -> float:
            return (float(n) / float(total) * 100.0) if total else 0.0

        recent = conn.execute(
            """
            SELECT created_at, input_type, input_value, prediction, confidence
            FROM predictions
            ORDER BY created_at DESC
            LIMIT 10
            """
        ).fetchall()

        return {
            "total_predictions": int(total),
            "fake_count": int(fake),
            "real_count": int(real),
            "fake_percentage": pct(fake),
            "real_percentage": pct(real),
            "input_type_breakdown": {"text": int(text_count), "url": int(url_count)},
            "recent": [
                {
                    "created_at": r["created_at"],
                    "input_type": r["input_type"],
                    "input_value": r["input_value"],
                    "prediction": r["prediction"],
                    "confidence": r["confidence"],
                }
                for r in recent
            ],
        }
    finally:
        conn.close()

