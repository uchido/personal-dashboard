#!/usr/bin/env bash
# Master data collector — run from cron to update all dashboard data.
# Data is served LIVE via the FastAPI server (port 8080).
# Git push is optional (backup for GitHub Pages).
set -e

REPO_DIR="$HOME/personal-dashboard"
cd "$REPO_DIR"

# Pull latest in case there were changes from GitHub Actions or elsewhere
git pull origin main --rebase --autostash 2>/dev/null || echo "No remote changes or first run"

# Run all collectors
echo "=== Collecting VPS Stats ==="
python3 scripts/collect-vps.py

echo "=== Collecting Crypto & Gold ==="
python3 scripts/collect-crypto.py

echo "=== Collecting Weather ==="
python3 scripts/collect-weather.py

echo "=== Collecting News ==="
python3 scripts/collect-news.py

echo "=== Collecting Quote ==="
python3 scripts/collect-quote.py

# Optional: push to GitHub for Pages backup
# Uncomment if you still want GitHub Pages to stay updated:
# echo "=== Committing data ==="
# git add docs/data/
# if git diff --cached --quiet; then
#     echo "No changes to commit"
# else
#     git commit -m "Update dashboard data: $(date '+%Y-%m-%d %H:%M')"
#     git push origin main
#     echo "Data pushed successfully"
# fi

echo "=== Done ==="
echo "Data served live at http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost'):6767/dashboard/"
