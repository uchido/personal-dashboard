"""
Personal Dashboard API Server — Live backend.
Runs collectors periodically, serves data via FastAPI + CORS.
"""

import asyncio
import json
import subprocess
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "docs" / "data"
DOCS_DIR = BASE_DIR / "docs"

COLLECTORS = [
    "collect-vps.py",
    "collect-crypto.py",
    "collect-weather.py",
    "collect-news.py",
    "collect-quote.py",
]

REFRESH_INTERVAL = 600  # 10 minutes

data_cache: dict[str, dict] = {}
last_refresh: float = 0


def run_collectors():
    """Run all collector scripts and cache their output JSON files."""
    global last_refresh, data_cache

    for script in COLLECTORS:
        script_path = SCRIPTS_DIR / script
        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            continue
        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"✗ {script}: {result.stderr.strip()[-200:]}")
            else:
                print(f"✓ {script}")
        except subprocess.TimeoutExpired:
            print(f"✗ {script}: timed out")
        except Exception as e:
            print(f"✗ {script}: {e}")

    # Read all output files into cache
    fresh_cache: dict[str, dict] = {}
    for json_file in sorted(DATA_DIR.glob("*.json")):
        try:
            fresh_cache[json_file.stem] = json.loads(json_file.read_text())
        except Exception as e:
            fresh_cache[json_file.stem] = {"error": str(e)}

    data_cache = fresh_cache
    last_refresh = time.time()
    print(f"✓ Cache refreshed: {list(data_cache.keys())}")


async def background_refresher():
    """Periodically refresh data in the background."""
    while True:
        await asyncio.sleep(REFRESH_INTERVAL)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_collectors)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: collect immediately
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_collectors)
    # Start periodic refresher
    task = asyncio.create_task(background_refresher())
    yield
    task.cancel()


app = FastAPI(title="Personal Dashboard API", lifespan=lifespan)

# CORS — allow browser requests from GitHub Pages or any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend static files
app.mount("/dashboard", StaticFiles(directory=str(DOCS_DIR), html=True), name="dashboard")


# === API Endpoints ===

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "last_refresh": last_refresh,
        "next_refresh": last_refresh + REFRESH_INTERVAL,
        "cached_datasets": list(data_cache.keys()),
        "refresh_interval_seconds": REFRESH_INTERVAL,
    }


@app.get("/api/all")
async def get_all():
    """Return all cached data in one response."""
    return {"data": data_cache, "last_refresh": last_refresh}


@app.post("/api/refresh")
async def refresh():
    """Force an immediate data refresh."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_collectors)
    return {"status": "ok", "last_refresh": last_refresh}


DATASET_ALIASES = {
    "vps-stats": "vps-stats",
    "vps": "vps-stats",
    "system": "vps-stats",
    "crypto": "crypto",
    "market": "crypto",
    "weather": "weather",
    "news": "news",
    "quote": "quote",
    "quotes": "quote",
}


@app.get("/api/{dataset}")
async def get_dataset(dataset: str):
    """Return a specific dataset by name."""
    key = DATASET_ALIASES.get(dataset, dataset)
    if key in data_cache:
        return data_cache[key]
    available = list(data_cache.keys())
    return {"error": f"Dataset '{dataset}' not found. Available: {available}"}
