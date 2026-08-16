import logging
import httpx
from typing import List
from backend.scrapers.base import BaseScraper

logger = logging.getLogger("rental_sniffer.scrapers.chotot")

class ChototScraper(BaseScraper):
    def __init__(self):
        super().__init__("Nhatot / Chotot")
        self.api_url = "https://gateway.chotot.com/v1/public/ad-listing"

    async def fetch_raw_listings(self) -> List[dict]:
        params = {
            "cg": "1000",       # Real Estate category
            "region": "13000",  # HCMC
            "area": "130805",   # District 8
            "q": "bông sao",
            "st": "u,h",        # Rent / Lease listings
            "limit": 30
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.nhatot.com/"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(self.api_url, params=params, headers=headers)
            if resp.status_code != 200:
                logger.error(f"[Chotot] API returned HTTP status {resp.status_code}")
                return []

            data = resp.json()
            ads = data.get("ads", [])
            results = []

            for ad in ads:
                list_id = ad.get("list_id")
                subject = ad.get("subject", "")
                body = ad.get("body", "")
                price_string = ad.get("price_string", "Thỏa thuận")
                account_name = ad.get("account_name", "")
                phone = ad.get("phone")
                
                # Direct canonical URL
                url = f"https://www.nhatot.com/{list_id}.htm"

                published_at = None
                raw_time = ad.get("orig_published_date") or ad.get("ad_date")
                if raw_time:
                    try:
                        from datetime import datetime
                        published_at = datetime.fromtimestamp(int(raw_time) / 1000)
                    except Exception:
                        pass

                results.append({
                    "source_id": str(list_id),
                    "title": subject,
                    "description": body,
                    "price_text": price_string,
                    "seller_name": account_name,
                    "phone": phone,
                    "url": url,
                    "published_at": published_at
                })

            return results
