# Personal Dashboard

Dashboard personal yang nampilin info VPS, crypto/gold, cuaca, berita, dan kutipan harian — sekarang **live via API backend** dari VPS.

## Fitur

- **💻 VPS Stats** — CPU, RAM, Disk, Uptime, Top Processes
- **💰 Market** — Harga BTC & Gold terkini (via CoinGecko)
- **🌤️ Cuaca** — Palu & Yogyakarta (via wttr.in)
- **📰 Berita** — Headline Global (BBC) & Indonesia (Antara)
- **💡 Quote** — Kutipan inspiratif setiap refresh
- **⏰ Live Clock** — Jam real-time + sapaan

## Arsitektur

```
┌──────────────────────────────────────────────────┐
│  VPS (168.110.195.174:8080)                      │
│                                                  │
│  FastAPI Server ── background refresh tiap 10m   │
│  ├── /api/health                                 │
│  ├── /api/vps-stats                              │
│  ├── /api/crypto                                 │
│  ├── /api/weather                                │
│  ├── /api/news                                   │
│  ├── /api/quote                                  │
│  ├── /api/all                                    │
│  ├── /api/refresh (POST)                         │
│  └── /dashboard/ (frontend static)               │
└──────────────────────────────────────────────────┘
```

## API Endpoints

Base URL: `http://168.110.195.174:8080`

| Endpoint        | Method | Description                      |
|-----------------|--------|----------------------------------|
| `/api/health`   | GET    | Status server & cache info       |
| `/api/all`      | GET    | Semua data sekaligus             |
| `/api/vps-stats`| GET    | CPU, RAM, Disk, Proses           |
| `/api/crypto`   | GET    | BTC & Gold price                 |
| `/api/weather`  | GET    | Cuaca Palu & Yogyakarta          |
| `/api/news`     | GET    | Berita BBC & Antara              |
| `/api/quote`    | GET    | Kutipan inspiratif               |
| `/api/refresh`  | POST   | Force refresh data               |

## Frontend

Akses dashboard: **http://168.110.195.174:8080/dashboard/**

Frontend otomatis refresh data tiap 5 menit dari API. Ada juga tombol **⟳ Refresh** manual.

## Service Management

```bash
# Cek status
sudo systemctl status dashboard-api

# Restart
sudo systemctl restart dashboard-api

# Lihat log
sudo journalctl -u dashboard-api -f

# Stop
sudo systemctl stop dashboard-api
```

## Data Collection

Script collector ada di `scripts/`. API server otomatis jalanin semua kolektor:
- Setiap startup
- Setiap 10 menit (background)
- Manual via `POST /api/refresh`

Kalau mau jalanin manual:
```bash
bash collect-all.sh
```

## Tech Stack

- Python 3.11 + FastAPI + Uvicorn
- Chart.js (CDN)
- systemd service
- iptables-persistent
