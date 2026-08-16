from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Listing(BaseModel):
    id: Optional[int] = None
    hash_id: str
    source: str
    source_id: Optional[str] = None
    title: str
    url: str
    price_text: str = "Thỏa thuận"
    price_val: Optional[float] = None
    phone: Optional[str] = None
    seller_name: Optional[str] = None
    description: str = ""
    block: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    is_rental: bool = True
    matches_target: bool = False
    published_at: Optional[datetime] = None
    is_fresh: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    notified_at: Optional[datetime] = None

class ScraperRunLog(BaseModel):
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)
    items_found: int = 0
    matches_found: int = 0
    status: str = "SUCCESS"  # SUCCESS, WARNING, ERROR
    error_message: Optional[str] = None

class RegexTestRequest(BaseModel):
    title: str
    description: str

class RegexTestResponse(BaseModel):
    is_rental: bool
    is_sale_excluded: bool
    block_matched: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    phone: Optional[str]
    is_match: bool
