import re
from typing import List

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_TAG_RE = re.compile(r"<[^>]+>")
_NON_ALNUM_RE = re.compile(r"[^a-zA-Z0-9\s]")
_MULTISPACE_RE = re.compile(r"\s+")

# Basic whitespace-tokenizer; upstream requirements call for tokenization + stopword removal.
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

STOP_WORDS = set(ENGLISH_STOP_WORDS)


def clean_text(raw_text: str) -> str:
    """Normalize text for consistent TF-IDF features."""
    text = raw_text or ""
    text = text.strip().lower()
    text = _URL_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    text = _NON_ALNUM_RE.sub(" ", text)
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


def tokenize_remove_stopwords(cleaned_text: str) -> List[str]:
    """Tokenize cleaned text and remove English stopwords."""
    tokens = _TOKEN_RE.findall(cleaned_text)
    return [t for t in tokens if t not in STOP_WORDS]


def preprocess_for_vectorizer(raw_text: str) -> str:
    """Preprocess a text input into a space-joined token string."""
    cleaned = clean_text(raw_text)
    tokens = tokenize_remove_stopwords(cleaned)
    return " ".join(tokens)

