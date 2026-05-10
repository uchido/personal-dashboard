# Personal Dashboard

Dashboard personal yang nampilin info VPS, crypto/gold, cuaca, berita, dan kutipan harian — langsung dari terminal VPS ke GitHub Pages.

## Fitur

- **💻 VPS Stats** — CPU, RAM, Disk, Uptime, Top Processes
- **💰 Market** — Harga BTC & Gold terkini (via CoinGecko)
- **🌤️ Cuaca** — Palu & Yogyakarta (via wttr.in)
- **📰 Berita** — Headline Global (BBC) & Indonesia (Antara)
- **💡 Quote** — Kutipan inspiratif setiap refresh
- **⏰ Live Clock** — Jam real-time + sapaan

## Cara Kerja

1. **Cron job** di VPS jalanin script tiap 30 menit
2. Script ngumpulin data dari berbagai API + system stats
3. Data disimpan sebagai JSON di `docs/data/`
4. Committed & pushed ke GitHub
5. GitHub Pages nampilin dashboard dari file JSON tersebut

## Setup

### 1. GitHub Pages
Enable GitHub Pages di repo settings → Pages → Source: **GitHub Actions**

### 2. Cron Job di VPS
Jalankan `collect-all.sh` secara periodik:
```bash
bash collect-all.sh
```

## Tech Stack
- Python 3 (stdlib only — no dependencies!)
- Chart.js (CDN)
- GitHub Pages + GitHub Actions
