"""
Unified Hotel Search Service.
Handles query normalization, smart caching, dual provider routing & failover.
"""

from typing import List, Optional, Dict, Any
from ..models.schemas import HotelItem
from ..utils.cities import resolve_hotel_query
from ..utils.cache import get_cached_result, set_cached_result, _get_cache_key
from .stays_provider import search_hotels_stays
from .serpapi_provider import search_hotels_serpapi, get_serpapi_key

def search_hotels(
    destination: str,
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
    provider: str = "auto",
    no_cache: bool = False,
) -> List[HotelItem]:
    """
    Search hotels with query resolution, local caching, and provider failover.
    """
    # 1. Resolve search query
    query = resolve_hotel_query(destination)

    # 2. Check cache
    cache_key = _get_cache_key(
        query=query,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        currency=currency,
        stars=tuple(sorted(stars)) if stars else None,
        sort_by=sort_by,
        amenities=tuple(sorted(amenities)) if amenities else None,
        free_cancellation=free_cancellation,
        price_max=price_max,
        max_results=max_results,
    )

    if not no_cache:
        cached = get_cached_result(cache_key)
        if cached:
            # Reconstruct Pydantic models
            return [HotelItem(**item) if isinstance(item, dict) else item for item in cached]

    results: List[HotelItem] = []
    last_error: Optional[Exception] = None

    # 3. Provider Execution
    if provider in ("stays", "auto"):
        try:
            results = search_hotels_stays(
                query=query,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                currency=currency,
                stars=stars,
                sort_by=sort_by,
                amenities=amenities,
                free_cancellation=free_cancellation,
                min_rating=min_rating,
                price_max=price_max,
                max_results=max_results,
            )
        except Exception as e:
            last_error = e
            results = []

    # If stays failed or returned 0 results in auto mode, fallback to SerpAPI
    if not results and (provider == "serpapi" or (provider == "auto" and get_serpapi_key())):
        try:
            results = search_hotels_serpapi(
                query=query,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                currency=currency,
                stars=stars,
                sort_by=sort_by,
                min_rating=min_rating,
                price_max=price_max,
                max_results=max_results,
            )
        except Exception as e:
            if not results and not last_error:
                last_error = e

    if not results and last_error and provider != "auto":
        raise last_error

    # 4. Sorting
    if sort_by == "LOWEST_PRICE":
        results = sorted(results, key=lambda x: (x.price_per_night is None, x.price_per_night or float("inf")))
    elif sort_by == "HIGHEST_RATING":
        results = sorted(results, key=lambda x: x.rating or 0, reverse=True)
    elif sort_by == "MOST_REVIEWED":
        results = sorted(results, key=lambda x: x.reviews_count or 0, reverse=True)

    # 5. Cache result
    if results:
        set_cached_result(cache_key, [r.model_dump() for r in results])

    return results
