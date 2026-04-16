from dataclasses import dataclass

from textblob import TextBlob


@dataclass(frozen=True)
class SentimentResult:
    label: str  # positive | negative | neutral
    polarity: float


def analyze_sentiment(text: str) -> SentimentResult:
    """
    Compute sentiment polarity and map it into positive/negative/neutral.

    If TextBlob fails for any reason, we degrade gracefully to neutral.
    """
    try:
        blob = TextBlob(text or "")
        polarity = float(blob.sentiment.polarity)
        if polarity > 0.1:
            return SentimentResult(label="positive", polarity=polarity)
        if polarity < -0.1:
            return SentimentResult(label="negative", polarity=polarity)
        return SentimentResult(label="neutral", polarity=polarity)
    except Exception:
        return SentimentResult(label="neutral", polarity=0.0)

