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


def fetch_asset_prices():
    """Fetch BTC & Gold prices in USD and IDR from CoinGecko (single request)."""
    data = fetch_json(
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin,pax-gold&vs_currencies=usd,idr&include_24hr_change=true"
    )
    if "error" in data:
        return {"btc": {"error": data["error"]}, "gold": {"error": data["error"]}}

    result = {}

    # BTC
    btc = data.get("bitcoin", {})
    if btc.get("usd"):
        result["btc"] = {
            "price": round(btc["usd"], 2),
            "price_idr": round(btc["idr"], 0) if btc.get("idr") else None,
            "change_24h": round(btc.get("usd_24h_change", 0), 2) if btc.get("usd_24h_change") else None,
            "change_24h_idr": round(btc.get("idr_24h_change", 0), 2) if btc.get("idr_24h_change") else None,
            "symbol": "BTC",
            "name": "Bitcoin",
        }
    else:
        result["btc"] = {"error": "No BTC price data", "symbol": "BTC"}

    # Gold (via PAXG)
    paxg = data.get("pax-gold", {})
    if paxg.get("usd"):
        result["gold"] = {
            "price": round(paxg["usd"], 2),
            "price_idr": round(paxg["idr"], 0) if paxg.get("idr") else None,
            "change_24h": round(paxg.get("usd_24h_change", 0), 2) if paxg.get("usd_24h_change") else None,
            "change_24h_idr": round(paxg.get("idr_24h_change", 0), 2) if paxg.get("idr_24h_change") else None,
            "symbol": "XAU",
            "name": "Gold",
        }
    else:
        result["gold"] = {"error": "Could not fetch gold price", "symbol": "XAU", "name": "Gold"}

    return result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    prices = fetch_asset_prices()
    btc = prices.get("btc", {})
    gold = prices.get("gold", {})

    assets = []
    if "error" not in btc:
        assets.append(btc)
    if "error" not in gold:
        assets.append(gold)

    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "assets": assets,
    }

    OUTPUT_FILE.write_text(json.dumps(data, indent=2))
    print(f"Crypto/gold data written to {OUTPUT_FILE}")
    if "error" in btc:
        print(f"  BTC warning: {btc.get('error')}")
    if "error" in gold:
        print(f"  Gold warning: {gold.get('error')}")


if __name__ == "__main__":
    main()
