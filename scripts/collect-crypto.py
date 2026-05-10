#!/usr/bin/env python3
"""Collect BTC price and Gold spot price using stdlib."""

import json
import urllib.request
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "crypto.json"


def fetch_json(url, timeout=15):
    """Fetch JSON from URL with error handling."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PersonalDashboard/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_btc_price():
    """Get BTC price from CoinGecko."""
    data = fetch_json(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    )
    if "error" in data:
        # Fallback: try alternative API
        data2 = fetch_json("https://api.coindesk.com/v1/bpi/currentprice.json")
        if "error" not in data2:
            price = data2.get("bpi", {}).get("USD", {}).get("rate_float", 0)
            return {
                "price": round(price, 2),
                "change_24h": None,
                "symbol": "BTC",
                "name": "Bitcoin",
            }
        return {"error": data["error"], "symbol": "BTC"}
    
    btc = data.get("bitcoin", {})
    return {
        "price": round(btc.get("usd", 0), 2),
        "change_24h": round(btc.get("usd_24h_change", 0), 2) if btc.get("usd_24h_change") else None,
        "symbol": "BTC",
        "name": "Bitcoin",
    }


def get_gold_price():
    """Get gold price via PAXG (PAX Gold token) from CoinGecko."""
    data = fetch_json(
        "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd&include_24hr_change=true"
    )
    if "error" not in data:
        paxg = data.get("pax-gold", {})
        if paxg.get("usd"):
            return {
                "price": round(paxg["usd"], 2),
                "change_24h": round(paxg.get("usd_24h_change", 0), 2) if paxg.get("usd_24h_change") else None,
                "symbol": "XAU",
                "name": "Gold",
            }
    
    return {"error": "Could not fetch gold price", "symbol": "XAU", "name": "Gold"}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    btc = get_btc_price()
    gold = get_gold_price()
    
    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "assets": [btc, gold],
    }
    
    OUTPUT_FILE.write_text(json.dumps(data, indent=2))
    print(f"Crypto/gold data written to {OUTPUT_FILE}")
    if "error" in btc:
        print(f"  BTC warning: {btc.get('error')}")
    if "error" in gold:
        print(f"  Gold warning: {gold.get('error')}")


if __name__ == "__main__":
    main()
