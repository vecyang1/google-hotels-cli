"""
Provider 1: Google Hotels via `stays` reverse-engineered batchexecute engine.
100% Free, Zero API Key required.
"""

import json
import subprocess
import shutil
from typing import List, Optional, Dict, Any
from ..models.schemas import HotelItem, HotelDetail

def search_hotels_stays(
    query: str,
    check_in: str,
    check_out: str,
    adults: int = 2,
    currency: str = "USD",
    stars: Optional[List[int]] = None,
    sort_by: str = "RELEVANCE",
    amenities: Optional[List[str]] = None,
    free_cancellation: bool = False,
    min_rating: Optional[str] = None,
    price_max: Optional[int] = None,
    max_results: int = 10,
) -> List[HotelItem]:
    """
    Execute Google Hotels search via stays CLI (or uvx fallback).
    """
    # Find executable: 'stays' in PATH, or 'uvx'
    stays_cmd = shutil.which("stays")
    if stays_cmd:
        base_cmd = [stays_cmd]
    else:
        uvx_cmd = shutil.which("uvx")
        if uvx_cmd:
            base_cmd = [uvx_cmd, "--from", "stays", "stays"]
        else:
            raise RuntimeError("Neither 'stays' nor 'uvx' found in PATH.")

    cmd = list(base_cmd) + ["search", query, "--check-in", check_in, "--check-out", check_out]
    cmd.extend(["--adults", str(adults)])
    cmd.extend(["--currency", currency])
    cmd.extend(["--max-results", str(max_results)])
    cmd.extend(["--format", "json"])

    if sort_by:
        cmd.extend(["--sort-by", sort_by])
    if stars:
        for s in stars:
            cmd.extend(["--stars", str(s)])
    if amenities:
        for a in amenities:
            cmd.extend(["--amenity", a.upper()])
    if free_cancellation:
        cmd.append("--free-cancellation")
    if min_rating:
        cmd.extend(["--min-rating", min_rating])
    if price_max is not None:
        cmd.extend(["--price-max", str(price_max)])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=40
        )
        if proc.returncode != 0:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"stays command failed (exit {proc.returncode}): {err_msg}")

        output = proc.stdout.strip()
        if not output:
            return []

        data = json.loads(output)
        # Parse output into HotelItem objects
        results = []
        raw_items = []
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            raw_items = data.get("results", data.get("hotels", []))

        for item in raw_items:
            # Extract price
            price_val = item.get("display_price")
            if price_val is None:
                rate_obj = item.get("rate_per_night") or item.get("price") or {}
                if isinstance(rate_obj, (int, float)):
                    price_val = float(rate_obj)
                elif isinstance(rate_obj, dict):
                    price_val = rate_obj.get("amount") or rate_obj.get("value")
                elif isinstance(rate_obj, str):
                    import re
                    nums = re.findall(r'[\d.]+', rate_obj)
                    if nums:
                        price_val = float(nums[0])

            curr = item.get("currency") or currency
            price_str = f"{curr} {price_val:.0f}" if price_val is not None else None

            # Extract amenities & nearby
            raw_amenities = item.get("amenities") or []
            if isinstance(raw_amenities, str):
                raw_amenities = [raw_amenities]
            elif isinstance(raw_amenities, list):
                raw_amenities = [str(x) for x in raw_amenities]

            # If amenities are empty, check nearby for highlights
            if not raw_amenities and item.get("nearby"):
                raw_amenities = [f"Near {n.get('name')}" for n in item.get("nearby", [])[:2]]

            # Extract images
            images = item.get("image_urls") or []
            thumb = images[0] if images else item.get("thumbnail")

            hotel = HotelItem(
                name=item.get("name", "Unknown Hotel"),
                entity_key=item.get("entity_key") or item.get("id"),
                stars=item.get("star_class") or item.get("stars") or item.get("hotel_class"),
                rating=item.get("overall_rating") or item.get("rating"),
                reviews_count=item.get("review_count") or item.get("reviews_count"),
                price_per_night=float(price_val) if price_val is not None else None,
                currency=curr,
                price_formatted=price_str,
                amenities=raw_amenities,
                address=item.get("address") or item.get("location"),
                thumbnail=thumb,
                provider="stays (Google Hotels)",
                direct_link=f"https://www.google.com/travel/hotels/entity/{item.get('entity_key')}" if item.get("entity_key") else None
            )
            results.append(hotel)

        return results

    except subprocess.TimeoutExpired:
        raise TimeoutError("Google Hotels search timed out via stays.")
    except Exception as e:
        raise RuntimeError(f"Error executing stays provider: {e}")
