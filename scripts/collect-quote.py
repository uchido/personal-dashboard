#!/usr/bin/env python3
"""Collect a random quote from a free API."""

import json
import urllib.request
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "quote.json"


def fetch_json(url, timeout=10):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PersonalDashboard/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_quote():
    """Try multiple free quote APIs."""
    # Try quotable.io
    data = fetch_json("https://api.quotable.io/random")
    if "error" not in data:
        return {
            "content": data.get("content", ""),
            "author": data.get("author", "Unknown"),
        }
    
    # Fallback: zenquotes.io
    data = fetch_json("https://zenquotes.io/api/random")
    if "error" not in data and isinstance(data, list) and len(data) > 0:
        return {
            "content": data[0].get("q", ""),
            "author": data[0].get("a", "Unknown"),
        }
    
    # Fallback: local quotes
    fallback_quotes = [
        {"content": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"content": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
        {"content": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
        {"content": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
        {"content": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    ]
    import random
    return random.choice(fallback_quotes)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    quote = get_quote()
    
    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "quote": quote,
    }
    
    OUTPUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Quote written to {OUTPUT_FILE}")
    print(f'  "{quote["content"][:60]}..." - {quote["author"]}' if len(quote["content"]) > 60
          else f'  "{quote["content"]}" - {quote["author"]}')


if __name__ == "__main__":
    main()
