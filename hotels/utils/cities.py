"""
Smart City and Destination Query Resolver for Google Hotels.
Maps multi-language city names and airport codes to structured destination queries.
"""

from typing import Dict, Optional

CITY_MAP: Dict[str, str] = {
    # Vietnam
    "河内": "Hanoi, Vietnam",
    "hanoi": "Hanoi, Vietnam",
    "han": "Hanoi, Vietnam",
    "胡志明": "Ho Chi Minh City, Vietnam",
    "胡志明市": "Ho Chi Minh City, Vietnam",
    "ho chi minh": "Ho Chi Minh City, Vietnam",
    "saigon": "Ho Chi Minh City, Vietnam",
    "sgn": "Ho Chi Minh City, Vietnam",
    "岘港": "Da Nang, Vietnam",
    "da nang": "Da Nang, Vietnam",
    "dad": "Da Nang, Vietnam",
    "芽庄": "Nha Trang, Vietnam",
    "nha trang": "Nha Trang, Vietnam",
    "富国岛": "Phu Quoc, Vietnam",
    "phu quoc": "Phu Quoc, Vietnam",
    
    # China & HK & TW
    "桂林": "Guilin, Guangxi, China",
    "guilin": "Guilin, China",
    "kwl": "Guilin, China",
    "南宁": "Nanning, Guangxi, China",
    "nanning": "Nanning, China",
    "nng": "Nanning, China",
    "广州": "Guangzhou, Guangdong, China",
    "guangzhou": "Guangzhou, China",
    "can": "Guangzhou, China",
    "深圳": "Shenzhen, Guangdong, China",
    "shenzhen": "Shenzhen, China",
    "szx": "Shenzhen, China",
    "北京": "Beijing, China",
    "beijing": "Beijing, China",
    "pek": "Beijing, China",
    "pkx": "Beijing, China",
    "上海": "Shanghai, China",
    "shanghai": "Shanghai, China",
    "pvg": "Shanghai, China",
    "sha": "Shanghai, China",
    "成都": "Chengdu, Sichuan, China",
    "chengdu": "Chengdu, China",
    "ctu": "Chengdu, China",
    "tfu": "Chengdu, China",
    "重庆": "Chongqing, China",
    "chongqing": "Chongqing, China",
    "ckg": "Chongqing, China",
    "香港": "Hong Kong",
    "hong kong": "Hong Kong",
    "hkg": "Hong Kong",
    "台北": "Taipei, Taiwan",
    "taipei": "Taipei, Taiwan",
    "tpe": "Taipei, Taiwan",

    # Japan & Korea
    "东京": "Tokyo, Japan",
    "tokyo": "Tokyo, Japan",
    "tyo": "Tokyo, Japan",
    "hnd": "Tokyo, Japan",
    "nrt": "Tokyo, Japan",
    "大阪": "Osaka, Japan",
    "osaka": "Osaka, Japan",
    "osa": "Osaka, Japan",
    "kix": "Osaka, Japan",
    "京都": "Kyoto, Japan",
    "kyoto": "Kyoto, Japan",
    "首尔": "Seoul, South Korea",
    "seoul": "Seoul, South Korea",
    "icn": "Seoul, South Korea",

    # Southeast Asia
    "曼谷": "Bangkok, Thailand",
    "bangkok": "Bangkok, Thailand",
    "bkk": "Bangkok, Thailand",
    "dmk": "Bangkok, Thailand",
    "普吉岛": "Phuket, Thailand",
    "phuket": "Phuket, Thailand",
    "hkt": "Phuket, Thailand",
    "清迈": "Chiang Mai, Thailand",
    "chiang mai": "Chiang Mai, Thailand",
    "cnx": "Chiang Mai, Thailand",
    "新加坡": "Singapore",
    "singapore": "Singapore",
    "sin": "Singapore",
    "吉隆坡": "Kuala Lumpur, Malaysia",
    "kuala lumpur": "Kuala Lumpur, Malaysia",
    "kul": "Kuala Lumpur, Malaysia",
    "巴厘岛": "Bali, Indonesia",
    "bali": "Bali, Indonesia",
    "dps": "Bali, Indonesia",

    # Europe & Americas
    "伦敦": "London, United Kingdom",
    "london": "London, United Kingdom",
    "lhr": "London, United Kingdom",
    "巴黎": "Paris, France",
    "paris": "Paris, France",
    "cdg": "Paris, France",
    "纽约": "New York, NY, USA",
    "new york": "New York, NY, USA",
    "jfk": "New York, NY, USA",
    "旧金山": "San Francisco, CA, USA",
    "san francisco": "San Francisco, CA, USA",
    "sfo": "San Francisco, CA, USA",
    "洛杉矶": "Los Angeles, CA, USA",
    "los angeles": "Los Angeles, CA, USA",
    "lax": "Los Angeles, CA, USA",
}

def resolve_hotel_query(destination: str) -> str:
    """
    Resolve a city name, airport code, or free-text location into an optimal search query.
    """
    raw = destination.strip()
    norm = raw.lower()
    
    # Direct match in map
    if norm in CITY_MAP:
        return f"{CITY_MAP[norm]} hotels"
        
    # If ends with 'hotels' or 'hotel', return as-is
    if norm.endswith("hotel") or norm.endswith("hotels") or "酒店" in norm or "宾馆" in norm or "民宿" in norm:
        return raw
        
    return f"{raw} hotels"
