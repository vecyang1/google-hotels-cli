# Changelog

All notable changes to `google-hotels-cli` will be documented in this file.

## [0.1.0] - 2026-08-27

### Added
- **Initial Production Release**: Unified Google Hotels Search CLI & FastMCP Server.
- **Dual-Provider Core**:
  - `stays_provider`: 100% free Google Hotels `batchexecute` client (0 API key required).
  - `serpapi_provider`: SerpAPI Google Hotels engine fallback.
- **Smart City & Query Resolver**: Multi-language mapping for Chinese/English cities (`河内`, `桂林`, `东京`, `Bangkok`, `Tokyo`, `BKK`).
- **Smart 2-Hour Caching**: File-based SHA-256 caching in `~/.cache/google_hotels/hotel_cache.json`.
- **Advanced CLI**: `hotel_search.py` supporting terminal tables, CSV, and JSON exports with rich sorting and amenity filters.
- **FastMCP Server**: Exposes `search_hotels_tool` and `server_status`.
- **Test Suite**: 7 offline deterministic unit tests covering normalization, caching, sorting, and failover.
- **Agent Ecosystem Travel Suite Integration**: Registered in `project-capabilities.md` and linked with `mcp-flight-search`, `agoda-orders-cli`, `activity-intel-cli`, and `citycost-cli`.
