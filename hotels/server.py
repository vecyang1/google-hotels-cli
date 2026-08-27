"""
FastMCP Server for Google Hotels Search & Intelligence.
Exposes standard MCP tools for Claude Desktop, Cursor, Antigravity, and Windsurf.
"""

import sys
import os
import json
import argparse
from typing import Optional, List

# Ensure package is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from hotels.services.hotel_service import search_hotels

# Initialize FastMCP App
mcp = FastMCP("google-hotels-server")

@mcp.tool()
async def search_hotels_tool(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    currency: str = "USD",
    stars: Optional[str] = None,
    sort_by: str = "RELEVANCE",
    amenity: Optional[str] = None,
    free_cancellation: bool = False,
    max_results: int = 10,
    no_cache: bool = False,
) -> str:
    """
    Search Google Hotels across worldwide destinations with real-time pricing, star ratings, review scores, and amenities.
    
    Args:
        destination: City name, landmark, or airport code (e.g. "Tokyo", "河内", "Paris", "BKK", "Hanoi")
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        adults: Number of adult guests (default: 2)
        currency: ISO 4217 currency code (e.g. "USD", "CNY", "EUR", "JPY")
        stars: Optional comma-separated star ratings to filter (e.g. "4,5" or "3,4")
        sort_by: Sort order ("RELEVANCE", "LOWEST_PRICE", "HIGHEST_RATING", "MOST_REVIEWED")
        amenity: Optional comma-separated amenities filter ("POOL", "WIFI", "SPA", "FREE_BREAKFAST")
        free_cancellation: Set True to filter only properties offering free cancellation
        max_results: Maximum number of hotel properties to return (default: 10)
        no_cache: Set True to force fresh live query bypassing local 2-hour cache
    """
    star_list = None
    if stars:
        try:
            star_list = [int(s.strip()) for s in stars.split(",") if s.strip()]
        except ValueError:
            pass

    amenity_list = None
    if amenity:
        amenity_list = [a.strip() for a in amenity.split(",") if a.strip()]

    try:
        results = search_hotels(
            destination=destination,
            check_in=check_in_date,
            check_out=check_out_date,
            adults=adults,
            currency=currency.upper(),
            stars=star_list,
            sort_by=sort_by,
            amenities=amenity_list,
            free_cancellation=free_cancellation,
            max_results=max_results,
            provider="auto",
            no_cache=no_cache,
        )

        if not results:
            return json.dumps({
                "status": "empty",
                "message": f"No hotels found for {destination} between {check_in_date} and {check_out_date}."
            }, ensure_ascii=False, indent=2)

        data = [h.model_dump() for h in results]
        return json.dumps({
            "status": "success",
            "count": len(results),
            "destination": destination,
            "dates": f"{check_in_date} to {check_out_date}",
            "currency": currency.upper(),
            "hotels": data
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def server_status() -> str:
    """
    Check the operational health and provider status of the Google Hotels MCP Server.
    """
    return json.dumps({
        "status": "healthy",
        "service": "google-hotels-cli",
        "providers": ["stays (Google Hotels batchexecute RPC)", "SerpAPI Google Hotels"],
        "cache": "2-hour file cache (~/.cache/google_hotels/)"
    }, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Google Hotels FastMCP Server")
    parser.add_argument(
        "--connection_type",
        choices=["stdio", "http"],
        default="stdio",
        help="MCP connection type (stdio or http)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9874,
        help="Port for HTTP connection mode (default: 9874)"
    )
    args = parser.parse_args()

    if args.connection_type == "http":
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
