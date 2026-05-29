# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Home temperature monitoring system using a Hubitat hub. Two Python scripts run as systemd user services:

- **`get_hub.py`** — polls the Hubitat REST API every 5 minutes, writes temperature readings to a CSV file at `~/.logs/monitoring/`
- **`plot.py`** — Flask web server (port 5000) that serves a browser UI to select and plot CSV files using Plotly

## Running the scripts

Run the monitoring script directly (polls forever):
```bash
python3 get_hub.py
```

Run the web server directly:
```bash
python3 plot.py
```
Then open `http://localhost:5000` in a browser.

## Service management

Services are installed as systemd user units at `~/.config/systemd/user/`.

```bash
# Install/reinstall service files
cp monitoring.service web-server.service ~/.config/systemd/user/

# Enable and start
systemctl --user enable monitoring web-server
systemctl --user start monitoring web-server

# Check status / logs
systemctl --user status monitoring
journalctl --user -u monitoring -f
```

## Architecture

**Data flow:** `get_hub.py` → Hubitat API (192.168.0.108) → `~/.logs/monitoring/YYYY-MM-DD_HH-MM-SS.csv`

**CSV format:** Each session creates one file. The first row is always the header (written when no temperature data is found yet — the hub returns devices in an order where headers are built on the first pass). Subsequent rows are timestamped readings. The `@Time` column is named with `@` to force alphabetical-first ordering, which matters because `plot.py` relies on `Object.keys(data)[0]` being the time axis after Flask's `jsonify` sorts keys.

**Error handling:** Temperature readings outside 0–200°F are replaced with the previous valid value and logged to a paired `.err` file. Network failures retry after 3 seconds.

**Dependencies:** `get_hub.py` uses only stdlib. `plot.py` requires `flask` and `pandas`.

## Key constants to know

- Hubitat hub hostname: `hubitat.local` (mDNS, in `get_hub.py`)
- Poll interval: 300 seconds (`get_hub.py:62`)
- Web server port: 5000 (`plot.py:91`)
- Data/log directory: `~/.logs/monitoring/`
