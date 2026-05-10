#!/usr/bin/env python3
"""Collect VPS system stats using only stdlib."""

import json
import os
import subprocess
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "vps-stats.json"


def get_cpu_percent():
    """Read CPU usage from /proc/stat."""
    with open("/proc/stat") as f:
        lines = f.readlines()
    
    # Get first line (total CPU)
    parts = lines[0].split()
    # parts[1] = user, parts[2] = nice, parts[3] = system, parts[4] = idle
    total = sum(int(p) for p in parts[1:])
    idle = int(parts[4])
    
    # Sample again after a short delay
    time.sleep(0.1)
    with open("/proc/stat") as f:
        lines = f.readlines()
    parts2 = lines[0].split()
    total2 = sum(int(p) for p in parts2[1:])
    idle2 = int(parts2[4])
    
    total_delta = total2 - total
    idle_delta = idle2 - idle
    
    if total_delta == 0:
        return 0.0
    
    return round((1 - idle_delta / total_delta) * 100, 1)


def get_memory_info():
    """Read memory info from /proc/meminfo."""
    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            parts = line.split()
            if parts[0].startswith("MemTotal"):
                mem["total"] = round(int(parts[1]) / 1024 / 1024, 1)  # GB
            elif parts[0].startswith("MemAvailable"):
                mem["available"] = round(int(parts[1]) / 1024 / 1024, 1)
            elif parts[0].startswith("MemFree"):
                mem["free"] = round(int(parts[1]) / 1024 / 1024, 1)
    
    mem["used"] = round(mem["total"] - mem["available"], 1)
    mem["percent"] = round((mem["used"] / mem["total"]) * 100, 1) if mem["total"] > 0 else 0
    return mem


def get_disk_info():
    """Get disk usage from df."""
    result = subprocess.run(
        ["df", "-h", "/"], capture_output=True, text=True, timeout=5
    )
    lines = result.stdout.strip().split("\n")
    if len(lines) >= 2:
        parts = lines[1].split()
        return {
            "total": parts[1] if len(parts) > 1 else "N/A",
            "used": parts[2] if len(parts) > 2 else "N/A",
            "available": parts[3] if len(parts) > 3 else "N/A",
            "percent": parts[4] if len(parts) > 4 else "N/A",
        }
    return {"error": "Could not parse df output"}


def get_uptime():
    """Read system uptime."""
    with open("/proc/uptime") as f:
        uptime_seconds = float(f.read().split()[0])
    
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    return {"days": days, "hours": hours, "minutes": minutes, "total_seconds": uptime_seconds}


def get_top_processes():
    """Get top 5 CPU consuming processes."""
    result = subprocess.run(
        ["ps", "aux", "--sort=-%cpu", "--no-headers"], 
        capture_output=True, text=True, timeout=5
    )
    processes = []
    for line in result.stdout.strip().split("\n")[:5]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append({
                "user": parts[0],
                "cpu": parts[2],
                "mem": parts[3],
                "command": parts[10][:50],
            })
    return processes


def get_hostname():
    """Get hostname."""
    try:
        with open("/proc/sys/kernel/hostname") as f:
            return f.read().strip()
    except Exception:
        return os.uname().nodename


def get_load_avg():
    """Get load average."""
    try:
        with open("/proc/loadavg") as f:
            parts = f.read().strip().split()[:3]
            return [float(p) for p in parts]
    except Exception:
        return [0, 0, 0]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "hostname": get_hostname(),
        "cpu": {
            "percent": get_cpu_percent(),
            "cores": os.cpu_count(),
            "load_avg": get_load_avg(),
        },
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "uptime": get_uptime(),
        "top_processes": get_top_processes(),
    }
    
    OUTPUT_FILE.write_text(json.dumps(data, indent=2))
    print(f"VPS stats written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
