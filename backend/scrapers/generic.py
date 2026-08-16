import logging
import httpx
from bs4 import BeautifulSoup
from typing import List
from backend.scrapers.base import BaseScraper

logger = logging.getLogger("rental_sniffer.scrapers.generic")

class GenericPlatformScraper(BaseScraper):
    def __init__(self, platform_name: str, target_url: str, card_selector: str):
        super().__init__(platform_name)
        self.target_url = target_url
        self.card_selector = card_selector

    async def fetch_raw_listings(self) -> List[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                resp = await client.get(self.target_url, headers=headers)
                if resp.status_code == 200:
                    return self._parse_html(resp.text)
                else:
                    logger.warning(f"[{self.name}] Returned HTTP status {resp.status_code}")
                    return []
            except Exception as e:
                logger.error(f"[{self.name}] Error fetching listings: {e}")
                return []

    def _parse_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(self.card_selector)
        results = []

        for card in cards:
            title_elem = card.select_one(".title, h3, h2, a[title]")
            link_elem = card.select_one("a[href]")
            price_elem = card.select_one(".price, .price-text")
            desc_elem = card.select_one(".description, .summary, p")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                url = link_elem.get("href", "")
                if not url.startswith("http"):
                    # Extract domain
                    domain = "/".join(self.target_url.split("/")[:3])
                    url = domain + url

                price_text = price_elem.get_text(strip=True) if price_elem else "Thỏa thuận"
                description = desc_elem.get_text(strip=True) if desc_elem else title

                results.append({
                    "source_id": url.split("/")[-1].split(".")[0],
                    "title": title,
                    "description": description,
                    "price_text": price_text,
                    "url": url
                })

        return results

# Factory functions for remaining targets:
def create_muaban_scraper():
    return GenericPlatformScraper(
        "Muaban.net",
        "https://muaban.net/cho-thue-can-ho-chung-cu-tap-the-quan-8-tp-hcm-l5916-c3202?q=b%C3%B4ng%20sao",
        ".list-item, .item-container"
    )

def create_homedy_scraper():
    return GenericPlatformScraper(
        "Homedy.com",
        "https://homedy.com/cho-thue-can-ho-chung-cu-bong-sao-quan-8-tp-ho-chi-minh",
        ".product-item, .item"
    )

def create_dothi_scraper():
    return GenericPlatformScraper(
        "Dothi.net",
        "https://dothi.net/cho-thue-can-ho-chung-cu-bong-sao",
        ".vip5, .vip0, .product-item"
    )

def create_rever_scraper():
    return GenericPlatformScraper(
        "Rever.vn",
        "https://rever.vn/cho-thue/can-ho/quan-8/bong-sao",
        ".listing-item, .property-card"
    )
