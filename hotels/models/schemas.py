from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HotelItem(BaseModel):
    name: str
    entity_key: Optional[str] = None
    stars: Optional[int] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    price_per_night: Optional[float] = None
    total_price: Optional[float] = None
    currency: str = "USD"
    price_formatted: Optional[str] = None
    amenities: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    thumbnail: Optional[str] = None
    provider: str = "stays"
    direct_link: Optional[str] = None
    booking_vendors: Dict[str, Any] = Field(default_factory=dict)

class HotelDetail(BaseModel):
    name: str
    entity_key: str
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    rooms: List[Dict[str, Any]] = Field(default_factory=list)
    amenities: List[str] = Field(default_factory=list)
    cancellation_policy: Optional[str] = None
    photos: List[str] = Field(default_factory=list)
