#!/usr/bin/env python3
"""Collect weather for Palu and Yogyakarta using wttr.in API."""

import json
import urllib.request
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "weather.json"


def fetch_json(url, timeout=15):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "curl/8.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_weather(location, name):
    """Get weather for a location from wttr.in."""
    data = fetch_json(f"https://wttr.in/{location}?format=j1", timeout=15)
    
    if "error" in data:
        return {"name": name, "error": data["error"]}
    
    current = data.get("current_condition", [{}])[0]
    nearest = data.get("nearest_area", [{}])[0]
    
    weather_info = {
        "name": name,
        "location": nearest.get("areaName", [{}])[0].get("value", location),
        "region": nearest.get("region", [{}])[0].get("value", ""),
        "country": nearest.get("country", [{}])[0].get("value", ""),
        "temp_c": current.get("temp_C", "N/A"),
        "feels_like_c": current.get("FeelsLikeC", "N/A"),
        "humidity": current.get("humidity", "N/A"),
        "wind_speed_kmh": current.get("windspeedKmph", "N/A"),
        "wind_dir": current.get("winddir16Point", "N/A"),
        "visibility_km": current.get("visibility", "N/A"),
        "pressure_mb": current.get("pressure", "N/A"),
        "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
        "condition_code": current.get("weatherCode", "N/A"),
        "uv_index": current.get("uvIndex", "N/A"),
    }
    
    # Add forecast for next 3 days
    forecasts = data.get("weather", [])
    weather_info["forecast"] = []
    for day in forecasts[:3]:
        weather_info["forecast"].append({
            "date": day.get("date", ""),
            "max_temp": day.get("maxtempC", "N/A"),
            "min_temp": day.get("mintempC", "N/A"),
            "condition": day.get("hourly", [{}])[0]
                .get("weatherDesc", [{}])[0].get("value", "N/A"),
            "sunrise": day.get("astronomy", [{}])[0].get("sunrise", "N/A"),
            "sunset": day.get("astronomy", [{}])[0].get("sunset", "N/A"),
        })
    
    return weather_info


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    palu = get_weather("Palu", "Palu")
    jogja = get_weather("Yogyakarta", "Yogyakarta")
    
    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "locations": [palu, jogja],
    }
    
    OUTPUT_FILE.write_text(json.dumps(data, indent=2))
    print(f"Weather data written to {OUTPUT_FILE}")
    
    for loc in [palu, jogja]:
        if "error" in loc:
            print(f"  {loc['name']}: error - {loc['error']}")
        else:
            print(f"  {loc['name']}: {loc['temp_c']}°C, {loc['condition']}")


if __name__ == "__main__":
    main()
