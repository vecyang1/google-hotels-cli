---
name: google-hotels-cli
description: Production-grade Google Hotels CLI & FastMCP Server with dual-provider architecture (stays batchexecute + SerpAPI), multi-language city resolver, and local caching.
---

# Google Hotels Search & Intelligence (`google-hotels-cli`)

A unified, production-ready tool for searching and analyzing Google Hotels worldwide with real-time room rates, star ratings, guest review scores, amenities, and direct booking links.

## 🚀 Quick Commands

```bash
# Navigate to skill directory
cd google-hotels-cli

# Basic: Search Tokyo 4/5-star hotels in USD
python3 hotel_search.py "Tokyo" 2026-10-15 2026-10-18 --stars 4,5 --currency USD

# Multi-language city support (Chinese / English / Airport codes)
python3 hotel_search.py "河内" 2026-10-15 2026-10-18 --currency USD
python3 hotel_search.py "桂林" 2026-09-02 2026-09-05 --stars 4,5 --currency CNY
python3 hotel_search.py "BKK" 2026-11-01 2026-11-04 --stars 5 --currency USD

# Advanced filtering: Lowest price sort, free cancellation, pool/spa amenities
python3 hotel_search.py "Bangkok" 2026-11-01 2026-11-05 \
    --stars 4,5 \
    --sort-by LOWEST_PRICE \
    --amenity POOL \
    --amenity SPA \
    --free-cancellation \
    --currency USD

# Export to CSV or JSON
python3 hotel_search.py "Kyoto" 2026-10-20 2026-10-23 --format json
python3 hotel_search.py "Paris" 2026-12-01 2026-12-05 --format csv --output-file paris_hotels.csv

# Force live query bypassing local 2-hour cache
python3 hotel_search.py "Tokyo" 2026-10-15 2026-10-18 --no-cache
```

## ✨ Key Capabilities

1. **Dual-Provider Architecture & Auto-Failover**:
   - **Primary**: `stays` (Google Hotels internal `batchexecute` protocol) — **100% Free, Zero API Key required**.
   - **Failover / Secondary**: SerpAPI `google_hotels` engine (loads `SERP_API_KEY` from `.env` or environment).
2. **Smart City & Query Resolver** (`hotels.utils.cities`):
   - Maps multi-language city names and IATA codes (`河内`, `桂林`, `胡志明`, `东京`, `Hanoi`, `Tokyo`, `BKK`, `SIN`, etc.) into optimal hotel search queries.
3. **Smart Local Caching** (`hotels.utils.cache`):
   - 2-hour TTL file-based cache in `~/.cache/google_hotels/` protects against rate limits and duplicate queries.
4. **Rich Filters & Sorting**:
   - Star class (`--stars 4,5`), guest rating (`--min-rating FOUR_ZERO_PLUS`), price cap (`--price-max 200`), free cancellation (`--free-cancellation`), amenities (`--amenity POOL,WIFI,SPA`).
5. **FastMCP Server** (`hotels.server`):
   - Native integration for Claude Desktop, Cursor, Antigravity, and Windsurf (`search_hotels_tool`, `server_status`).

## 🌐 Agent Ecosystem Cross-Tool Travel Ecosystem Workflow

| Step | Tool / Skill | Role in Travel Planning |
| :--- | :--- | :--- |
| **1. Transit & Flight** | `mcp-flight-search` | Find lowest fare flight dates, airlines, and high-speed rail alternatives |
| **2. Hotel & Accommodation** | `google-hotels-cli` / `agoda-orders-cli` | Compare Google Hotels live rates, star classes, and Agoda loyalty ledger |
| **3. Activities & Experiences**| `activity-intel-cli` | Retrieve top-rated Klook tours and Airbnb Experiences |
| **4. Nomad Living Cost** | `citycost-cli` | Evaluate destination baseline living expenses and safety index |

## 🧪 Verification

```bash
cd google-hotels-cli
python3 -m unittest discover -s tests
```

## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**: 
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
- **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
- **NO**: Do nothing.
- **Constraint**: Only log **High-Signal** improvements.
