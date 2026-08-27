"""
Provider 2: SerpAPI Google Hotels Engine.
Used as reliable failover or when direct OTA booking links are needed.
"""

import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from ..models.schemas import HotelItem

# Load environment
load_dotenv()

def get_serpapi_key() -> Optional[str]:
    return os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_API_KEY")

def search_hotels_serpapi(
    query: str,
    check_in: str,
    check_out: str,
    adults: int = 2,
    currency: str = "USD",
    stars: Optional[List[int]] = None,
    sort_by: Optional[str] = None,
    min_rating: Optional[str] = None,
    price_max: Optional[int] = None,
    max_results: int = 10,
) -> List[HotelItem]:
    """
    Execute Google Hotels search via SerpAPI engine.
    """
    api_key = get_serpapi_key()
    if not api_key:
        raise ValueError("SERP_API_KEY not found in environment or .env file.")

    try:
        from serpapi import GoogleSearch
    except ImportError:
        raise ImportError("google-search-results package is required for SerpAPI provider.")

    params: Dict[str, Any] = {
        "engine": "google_hotels",
        "q": query,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": adults,
        "currency": currency,
        "api_key": api_key,
    }

    if stars:
        params["hotel_class"] = ",".join(str(s) for s in stars)
    if price_max is not None:
        params["max_price"] = price_max

    search = GoogleSearch(params)
    data = search.get_dict()

    if "error" in data:
        raise RuntimeError(f"SerpAPI Google Hotels error: {data['error']}")

    properties = data.get("properties", [])
    results: List[HotelItem] = []

    for item in properties[:max_results]:
        # Extract rate
        price_val = None
        price_str = None
        rate_info = item.get("rate_per_night") or {}
        if isinstance(rate_info, dict):
            extracted = rate_info.get("extracted_lowest") or rate_info.get("lowest")
            if extracted:
                import re
                nums = re.findall(r'[\d.]+', str(extracted))
                if nums:
                    price_val = float(nums[0])
            price_str = rate_info.get("lowest") or (f"{currency} {price_val}" if price_val else None)

        # Extract amenities
        amenities = item.get("amenities", [])
        if isinstance(amenities, str):
            amenities = [amenities]

        # Extract vendor prices
        booking_vendors = {}
        for deal in item.get("prices", []):
            vendor_name = deal.get("source")
            vendor_rate = deal.get("rate_per_night", {}).get("lowest")
            if vendor_name and vendor_rate:
                booking_vendors[vendor_name] = vendor_rate

        hotel = HotelItem(
            name=item.get("name", "Unknown Hotel"),
            entity_key=item.get("property_token") or item.get("id"),
            stars=item.get("extracted_hotel_class") or item.get("hotel_class"),
            rating=item.get("overall_rating"),
            reviews_count=item.get("reviews"),
            price_per_night=price_val,
            total_price=item.get("total_rate", {}).get("extracted_lowest"),
            currency=currency,
            price_formatted=price_str,
            amenities=amenities,
            address=item.get("description"),
            thumbnail=item.get("images", [{}])[0].get("thumbnail") if item.get("images") else None,
            provider="SerpAPI (Google Hotels)",
            direct_link=item.get("link"),
            booking_vendors=booking_vendors
        )
        results.append(hotel)

    return results
