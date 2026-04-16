import re
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


_SCRIPT_STYLE_RE = re.compile(r"\s+")


def _validate_url(url: str) -> None:
    if not url or not isinstance(url, str):
        raise ValueError("URL is required.")
    url = url.strip()
    if len(url) > 2048:
        raise ValueError("URL is too long.")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")
    if not parsed.netloc:
        raise ValueError("Invalid URL.")


def _clean_extracted_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text).strip()
    # Keep response reasonable (UI + DB friendly).
    return text[:12000]


def scrape_url_text(url: str) -> str:
    """
    Fetch and extract main article text from a URL.

    Strategy:
    - Remove script/style
    - Prefer <article>, then <main>
    - Fallback to concatenated <p> tags
    """
    _validate_url(url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove irrelevant content blocks.
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    container = soup.find("article")
    if container is None:
        container = soup.find("main")
    if container is None:
        container = soup

    paragraphs = [p.get_text(" ", strip=True) for p in container.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) >= 20]

    if not paragraphs:
        # As a fallback, take visible text from the container.
        text = container.get_text(" ", strip=True)
        extracted = _clean_extracted_text(text)
    else:
        extracted = _clean_extracted_text(" ".join(paragraphs))

    if len(extracted) < 60:
        raise ValueError("Could not extract enough article text from the URL.")

    return extracted

