"""
Comprehensive Offline Unit Test Suite for Google Hotels Search.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import tempfile

# Ensure package is imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hotels.models.schemas import HotelItem
from hotels.utils.cities import resolve_hotel_query
from hotels.utils.cache import _get_cache_key, get_cached_result, set_cached_result, CACHE_FILE
from hotels.services.hotel_service import search_hotels

class TestGoogleHotels(unittest.TestCase):

    def test_city_resolution(self):
        """Test multi-language city name mapping."""
        self.assertEqual(resolve_hotel_query("河内"), "Hanoi, Vietnam hotels")
        self.assertEqual(resolve_hotel_query("桂林"), "Guilin, Guangxi, China hotels")
        self.assertEqual(resolve_hotel_query("东京"), "Tokyo, Japan hotels")
        self.assertEqual(resolve_hotel_query("Tokyo"), "Tokyo, Japan hotels")
        self.assertEqual(resolve_hotel_query("BKK"), "Bangkok, Thailand hotels")
        self.assertEqual(resolve_hotel_query("Kyoto"), "Kyoto, Japan hotels")
        # Free-text already containing hotel
        self.assertEqual(resolve_hotel_query("Hilton Tokyo Hotel"), "Hilton Tokyo Hotel")

    def test_cache_key_generation(self):
        """Test deterministic cache key generation."""
        k1 = _get_cache_key("Tokyo, Japan hotels", "2026-10-15", "2026-10-18", adults=2, currency="USD")
        k2 = _get_cache_key("tokyo, japan hotels", "2026-10-15", "2026-10-18", adults=2, currency="USD")
        self.assertEqual(k1, k2)

    def test_cache_set_and_get(self):
        """Test caching read and write behavior."""
        dummy_key = "test_hotel_cache_key_123"
        dummy_data = [{"name": "Test Grand Hotel", "price_per_night": 150.0, "currency": "USD"}]
        set_cached_result(dummy_key, dummy_data)
        cached = get_cached_result(dummy_key, ttl=60)
        self.assertIsNotNone(cached)
        self.assertEqual(cached[0]["name"], "Test Grand Hotel")

    def test_hotel_item_normalization(self):
        """Test Pydantic model validation and formatting."""
        item = HotelItem(
            name="Tokyo Imperial Palace Hotel",
            stars=5,
            rating=4.8,
            reviews_count=2150,
            price_per_night=320.0,
            currency="USD",
            amenities=["Free WiFi", "Pool", "Spa"]
        )
        self.assertEqual(item.stars, 5)
        self.assertEqual(item.rating, 4.8)
        self.assertEqual(len(item.amenities), 3)

    @patch("hotels.services.hotel_service.search_hotels_stays")
    def test_search_hotels_sorting_lowest_price(self, mock_stays):
        """Test sorting results by LOWEST_PRICE."""
        mock_stays.return_value = [
            HotelItem(name="Expensive Hotel", price_per_night=400.0, currency="USD"),
            HotelItem(name="Budget Inn", price_per_night=80.0, currency="USD"),
            HotelItem(name="Midscale Hotel", price_per_night=150.0, currency="USD"),
        ]

        results = search_hotels("Tokyo", "2026-10-15", "2026-10-18", sort_by="LOWEST_PRICE", no_cache=True)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Budget Inn")
        self.assertEqual(results[1].name, "Midscale Hotel")
        self.assertEqual(results[2].name, "Expensive Hotel")

    @patch("hotels.services.hotel_service.search_hotels_stays")
    def test_search_hotels_sorting_highest_rating(self, mock_stays):
        """Test sorting results by HIGHEST_RATING."""
        mock_stays.return_value = [
            HotelItem(name="Average Stay", rating=3.8, currency="USD"),
            HotelItem(name="Top Luxury Resort", rating=4.9, currency="USD"),
            HotelItem(name="Good Hotel", rating=4.4, currency="USD"),
        ]

        results = search_hotels("Bangkok", "2026-11-01", "2026-11-05", sort_by="HIGHEST_RATING", no_cache=True)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Top Luxury Resort")
        self.assertEqual(results[1].name, "Good Hotel")
        self.assertEqual(results[2].name, "Average Stay")

    @patch("hotels.services.hotel_service.search_hotels_stays")
    @patch("hotels.services.hotel_service.search_hotels_serpapi")
    @patch("hotels.services.hotel_service.get_serpapi_key")
    def test_failover_to_serpapi_on_stays_failure(self, mock_get_key, mock_serpapi, mock_stays):
        """Test automatic failover to SerpAPI when stays raises error."""
        mock_stays.side_effect = RuntimeError("stays connection error")
        mock_get_key.return_value = "mock_serpapi_key"
        mock_serpapi.return_value = [
            HotelItem(name="Fallback SerpAPI Hotel", price_per_night=200.0, currency="USD", provider="SerpAPI")
        ]

        results = search_hotels("Paris", "2026-12-01", "2026-12-05", provider="auto", no_cache=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Fallback SerpAPI Hotel")
        self.assertEqual(results[0].provider, "SerpAPI")

if __name__ == "__main__":
    unittest.main()
