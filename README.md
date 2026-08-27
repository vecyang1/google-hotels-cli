# Google Hotels CLI & MCP Server 🏨

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Standard-green.svg)](https://modelcontextprotocol.io/)
[![Unit Tests](https://img.shields.io/badge/tests-7%2F7%20passing-brightgreen.svg)](tests/)

A production-grade **Google Hotels Search CLI & Model Context Protocol (MCP) Server** with dual-provider architecture (free `batchexecute` RPC + SerpAPI failover), smart multi-language city resolution, and local caching.

---

## ✨ Features

- 🆓 **100% Free Primary Engine**: Uses reverse-engineered `stays` Google Hotels `batchexecute` client — **zero API keys required, zero recurring fees**.
- 🛡️ **Dual-Provider Resilience**: Auto-failover to SerpAPI Google Hotels engine if rate limits or CAPTCHAs are encountered.
- 🌍 **Smart City & Airport Resolver**: Search using English, Chinese, or 3-letter IATA airport codes (`Tokyo`, `东京`, `Hanoi`, `河内`, `Paris`, `BKK`, `SGN`, etc.).
- ⚡ **Local 2-Hour Caching**: Built-in SHA-256 parameter caching (`~/.cache/google_hotels/`) delivers zero-latency results on repeated checks and protects network bandwidth.
- 🎯 **Comprehensive Filtering**: Star ratings (`--stars 4,5`), guest scores (`--min-rating FOUR_ZERO_PLUS`), amenities (`--amenity POOL,SPA,WIFI`), free cancellation, and multi-currency pricing (`USD`, `CNY`, `EUR`, `JPY`).
- 🤖 **FastMCP Server**: Exposes standard MCP tools (`search_hotels_tool`, `server_status`) for Claude Desktop, Cursor, Antigravity, and Windsurf.
- 📊 **Multi-Format Export**: Human-friendly terminal tables, structured JSON, and exportable CSV.

---

## 🚀 Quick Start

### ⚡ One-Line Install via Smithery (Claude / Cursor / Windsurf)

```bash
# For Claude Desktop
npx -y @smithery/cli install @vecyang1/google-hotels-cli --client claude

# For Cursor
npx -y @smithery/cli install @vecyang1/google-hotels-cli --client cursor
```

### Manual Installation

```bash
git clone https://github.com/vecyang1/google-hotels-cli.git
cd google-hotels-cli

# Using pip or uv
pip install -e .
```

---

## 🖥️ CLI Usage (`hotel_search.py`)

```bash
# Basic search: Tokyo 4/5-star hotels in USD
python3 hotel_search.py "Tokyo" 2026-10-15 2026-10-18 --stars 4,5 --currency USD

# Multi-language destination queries
python3 hotel_search.py "河内" 2026-10-15 2026-10-18 --currency USD
python3 hotel_search.py "BKK" 2026-11-01 2026-11-04 --stars 5 --currency USD

# Advanced filtering: Lowest price, free cancellation, pool & spa
python3 hotel_search.py "Bangkok" 2026-11-01 2026-11-05 \
    --stars 4,5 \
    --sort-by LOWEST_PRICE \
    --amenity POOL \
    --amenity SPA \
    --free-cancellation \
    --currency USD

# Export to JSON or CSV
python3 hotel_search.py "Kyoto" 2026-10-20 2026-10-23 --format json
python3 hotel_search.py "Paris" 2026-12-01 2026-12-05 --format csv --output-file paris_hotels.csv

# Force live search (bypassing local cache)
python3 hotel_search.py "Tokyo" 2026-10-15 2026-10-18 --no-cache
```

### Example Terminal Output

```text
🏨 Google Hotels: Tokyo (Tokyo, Japan hotels)
📅 2026-10-15 ➔ 2026-10-18 (USD)
 #   Hotel Name                         ★    Rating       Price / Night (USD)  Key Amenities           Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 1   Tokyo Bay Shiomi Prince Hotel      4★   4.5 (1742)   USD 219              BEACH_ACCESS, POOL      stays 
 2   Hotel New Otani Tokyo The Main     5★   4.3 (7977)   USD 322              BEACH_ACCESS, POOL      stays 
 3   Imperial Hotel Tokyo               5★   4.5 (12751)  USD 325              BAR, BEACH_ACCESS       stays 
 4   HOSHINOYA Tokyo                    5★   4.4 (1136)   USD 863              BEACH_ACCESS            stays 
```

---

## 🤖 MCP Server Configuration

Add the following to your `claude_desktop_config.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "google-hotels": {
      "command": "python3",
      "args": ["-m", "hotels.server", "--connection_type", "stdio"],
      "cwd": "/path/to/google-hotels-cli",
      "env": {
        "SERP_API_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

### Exposed MCP Tools

1. **`search_hotels_tool`**:
   - `destination` *(string)*: City name, landmark, or IATA code (e.g. `Tokyo`, `河内`, `Paris`, `BKK`)
   - `check_in_date` *(string)*: Check-in date (`YYYY-MM-DD`)
   - `check_out_date` *(string)*: Check-out date (`YYYY-MM-DD`)
   - `adults` *(int, default 2)*: Number of adult guests
   - `currency` *(string, default "USD")*: Currency code (`USD`, `EUR`, `CNY`, `JPY`)
   - `stars` *(string, optional)*: Star rating filter (e.g. `"4,5"`)
   - `sort_by` *(string, default "RELEVANCE")*: `"RELEVANCE"`, `"LOWEST_PRICE"`, `"HIGHEST_RATING"`
   - `amenity` *(string, optional)*: Comma-separated amenities (`"POOL,SPA,WIFI"`)
   - `free_cancellation` *(bool, default false)*: Filter for free cancellation
   - `no_cache` *(bool, default false)*: Bypass cache and force live query
2. **`server_status`**: Check health and dual-provider availability.

---

## 🐍 Python SDK Usage

```python
from hotels.services.hotel_service import search_hotels

# Pass city names or airport codes directly
hotels = search_hotels(
    destination="Tokyo",
    check_in="2026-10-15",
    check_out="2026-10-18",
    stars=[4, 5],
    currency="USD",
    sort_by="LOWEST_PRICE"
)

for h in hotels[:3]:
    print(f"{h.name} ({h.stars}★) | {h.rating} rating | {h.price_formatted} | Amenities: {h.amenities}")
```

---

## 🧪 Testing

Run the deterministic offline test suite:

```bash
python3 -m unittest discover -s tests
```

---

## 📄 License & Credits

- Built & maintained by [Vec Yang](https://github.com/vecyang1).
- Powered by `stays` batchexecute engine by [him229](https://github.com/him229/stays) and SerpAPI.
- Licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
