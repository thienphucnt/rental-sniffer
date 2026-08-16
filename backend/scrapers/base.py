import logging
import abc
import asyncio
from typing import List, Optional
from backend.models import Listing
from backend.parser import analyze_listing, extract_phone
from backend.database import db

logger = logging.getLogger("rental_sniffer.scrapers")

class BaseScraper(abc.ABC):
    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    async def fetch_raw_listings(self) -> List[dict]:
        """Fetch raw listing dictionaries from source."""
        pass

    def build_listing_object(self, raw: dict) -> Optional[Listing]:
        title = raw.get("title", "")
        description = raw.get("description", "")
        url = raw.get("url", "")
        source_id = raw.get("source_id", "")
        price_text = raw.get("price_text", "Thỏa thuận")
        phone = raw.get("phone") or extract_phone(f"{title} {description}")

        analysis = analyze_listing(title, description)
        
        # STRICT NOISE FILTER: Discard any listing that does NOT explicitly mention Bông Sao
        if not analysis["is_bong_sao"]:
            return None

        hash_id = db.generate_hash(self.name, url, phone)

        published_at = raw.get("published_at")
        if not published_at:
            from backend.parser import parse_relative_time
            date_text = raw.get("published_text") or f"{title} {description}"
            published_at = parse_relative_time(date_text)

        from backend.parser import is_fresh_listing
        is_fresh = is_fresh_listing(published_at)

        # STRICT CRITERIA: A match MUST meet criteria AND be strictly fresh (< 48h)
        is_strict_match = bool(analysis["is_match"] and is_fresh)

        listing = Listing(
            hash_id=hash_id,
            source=self.name,
            source_id=source_id,
            title=title,
            url=url,
            price_text=price_text,
            phone=phone,
            seller_name=raw.get("seller_name"),
            description=description,
            block=analysis["block_matched"],
            bedrooms=analysis["bedrooms"],
            bathrooms=analysis["bathrooms"],
            is_rental=analysis["is_rental"],
            matches_target=is_strict_match,
            published_at=published_at,
            is_fresh=is_fresh
        )
        return listing

    async def run(self) -> List[Listing]:
        logger.info(f"[{self.name}] Executing scraper run...")
        try:
            raw_items = await self.fetch_raw_listings()
            listings = []
            matches_count = 0

            for raw in raw_items:
                listing = self.build_listing_object(raw)
                if listing is not None:
                    listings.append(listing)
                    if listing.matches_target:
                        matches_count += 1

            logger.info(f"[{self.name}] Found {len(listings)} Bông Sao items ({matches_count} fresh matching criteria)")
            return listings
        except Exception as e:
            logger.error(f"[{self.name}] Error during scrape execution: {e}", exc_info=True)
            raise e
