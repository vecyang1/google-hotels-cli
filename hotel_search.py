#!/usr/bin/env python3
"""
Advanced Google Hotels Search CLI.
Production-grade CLI tool for searching Google Hotels across international destinations.
"""

import sys
import os
import argparse
import json
import csv
from datetime import datetime, timedelta

# Ensure package is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotels.services.hotel_service import search_hotels
from hotels.utils.cities import resolve_hotel_query

try:
    from rich.console import Console
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

def print_table(results, destination, check_in, check_out, currency):
    resolved = resolve_hotel_query(destination)
    if RICH_AVAILABLE:
        console = Console()
        table = Table(title=f"🏨 Google Hotels: {destination} ({resolved})\n📅 {check_in} ➔ {check_out} ({currency})", header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Hotel Name", style="bold white", min_width=24)
        table.add_column("★", style="yellow", justify="center", width=4)
        table.add_column("Rating", style="green", width=12)
        table.add_column(f"Price / Night ({currency})", style="bold green", justify="right", width=18)
        table.add_column("Key Amenities", style="dim", min_width=20)
        table.add_column("Source", style="dim", width=12)

        for idx, h in enumerate(results, start=1):
            stars_str = f"{h.stars}★" if h.stars else "—"
            rating_str = f"{h.rating:.1f} ({h.reviews_count or 0})" if h.rating else "—"
            price_str = h.price_formatted or (f"{currency} {h.price_per_night:.0f}" if h.price_per_night else "N/A")
            amenities_str = ", ".join(h.amenities[:3]) if h.amenities else "—"
            
            table.add_row(
                str(idx),
                h.name,
                stars_str,
                rating_str,
                price_str,
                amenities_str,
                h.provider.split()[0]
            )

        console.print(table)
    else:
        print(f"\n--- Google Hotels: {destination} ({check_in} -> {check_out}) ---")
        for idx, h in enumerate(results, start=1):
            stars_str = f"{h.stars}*" if h.stars else ""
            rating_str = f"Rating: {h.rating} ({h.reviews_count})" if h.rating else ""
            price_str = h.price_formatted or f"{currency} {h.price_per_night}"
            print(f"{idx}. {h.name} {stars_str} | {rating_str} | {price_str} | {', '.join(h.amenities[:2])}")

def export_csv(results, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Stars", "Rating", "Reviews", "Price_Per_Night", "Currency", "Amenities", "Direct_Link", "Provider"])
        for h in results:
            writer.writerow([
                h.name,
                h.stars or "",
                h.rating or "",
                h.reviews_count or "",
                h.price_per_night or "",
                h.currency,
                "; ".join(h.amenities),
                h.direct_link or "",
                h.provider
            ])
    print(f"✅ Exported {len(results)} hotels to CSV: {output_file}")

def export_json(results, output_file=None):
    data = [h.model_dump() for h in results]
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"✅ Exported {len(results)} hotels to JSON: {output_file}")
    else:
        print(json_str)

def main():
    parser = argparse.ArgumentParser(description="Advanced Google Hotels Search CLI")
    parser.add_argument("destination", help="City name, landmark, or airport code (e.g. Tokyo, 河内, Paris, BKK)")
    parser.add_argument("check_in", help="Check-in date (YYYY-MM-DD)")
    parser.add_argument("check_out", help="Check-out date (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2, help="Number of adults (default: 2)")
    parser.add_argument("--currency", default="USD", help="ISO 4217 currency code (USD, CNY, EUR, JPY, etc.)")
    parser.add_argument("--stars", type=str, help="Comma-separated star rating filter (e.g. 4,5)")
    parser.add_argument("--sort-by", choices=["RELEVANCE", "LOWEST_PRICE", "HIGHEST_RATING", "MOST_REVIEWED"], default="RELEVANCE", help="Sort order")
    parser.add_argument("--min-rating", choices=["THREE_FIVE_PLUS", "FOUR_ZERO_PLUS", "FOUR_FIVE_PLUS"], help="Minimum guest rating score")
    parser.add_argument("--amenity", action="append", help="Repeatable amenity filter (POOL, WIFI, SPA, FREE_BREAKFAST)")
    parser.add_argument("--free-cancellation", action="store_true", help="Filter for free cancellation only")
    parser.add_argument("--price-max", type=int, help="Maximum price per night cap")
    parser.add_argument("--max-results", type=int, default=10, help="Max number of hotel results (default: 10)")
    parser.add_argument("--provider", choices=["auto", "stays", "serpapi"], default="auto", help="Data provider (default: auto)")
    parser.add_argument("--no-cache", action="store_true", help="Bypass local cache and force live query")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format")
    parser.add_argument("--output-file", help="Path to save CSV or JSON export")

    args = parser.parse_args()

    # Parse stars
    star_list = None
    if args.stars:
        try:
            star_list = [int(s.strip()) for s in args.stars.split(",") if s.strip()]
        except ValueError:
            print("Error: --stars must be comma-separated integers (e.g. --stars 4,5)", file=sys.stderr)
            sys.exit(1)

    try:
        results = search_hotels(
            destination=args.destination,
            check_in=args.check_in,
            check_out=args.check_out,
            adults=args.adults,
            currency=args.currency.upper(),
            stars=star_list,
            sort_by=args.sort_by,
            amenities=args.amenity,
            free_cancellation=args.free_cancellation,
            min_rating=args.min_rating,
            price_max=args.price_max,
            max_results=args.max_results,
            provider=args.provider,
            no_cache=args.no_cache,
        )

        if not results:
            print(f"⚠️ No hotels found for '{args.destination}' ({args.check_in} -> {args.check_out}). Try broadening your filters.")
            sys.exit(0)

        if args.format == "table":
            print_table(results, args.destination, args.check_in, args.check_out, args.currency.upper())
        elif args.format == "json":
            export_json(results, args.output_file)
        elif args.format == "csv":
            if not args.output_file:
                args.output_file = f"hotels_{args.destination}_{args.check_in}.csv".replace(" ", "_")
            export_csv(results, args.output_file)

    except Exception as e:
        print(f"❌ Error executing hotel search: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
