import logging
import httpx
from bs4 import BeautifulSoup
from typing import List
from backend.scrapers.base import BaseScraper

logger = logging.getLogger("rental_sniffer.scrapers.mogi")

class MogiScraper(BaseScraper):
    def __init__(self):
        super().__init__("Mogi.vn")
        self.search_url = "https://mogi.vn/ho-chi-minh/quan-8/thue-can-ho-tap-the-cu-xa?q=b%C3%B4ng%20sao"

    async def fetch_raw_listings(self) -> List[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                resp = await client.get(self.search_url, headers=headers)
                if resp.status_code == 200:
                    return self._parse_html(resp.text)
                else:
                    logger.warning(f"[Mogi] HTTP status {resp.status_code}")
                    return []
            except Exception as e:
                logger.error(f"[Mogi] Fetch error: {e}")
                return []

    def _parse_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".link-overlay, .prop-item, .item-container")
        results = []

        for card in cards:
            title_elem = card.select_one(".prop-title, .title, h2, h3")
            link_elem = card if card.name == "a" else card.select_one("a[href]")
            price_elem = card.select_one(".price, .prop-price")
            desc_elem = card.select_one(".prop-attr, .description")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                url = link_elem.get("href", "")
                if not url.startswith("http"):
                    url = "https://mogi.vn" + url

                price_text = price_elem.get_text(strip=True) if price_elem else "Thỏa thuận"
                description = desc_elem.get_text(strip=True) if desc_elem else title

                results.append({
                    "source_id": url.split("/")[-1],
                    "title": title,
                    "description": description,
                    "price_text": price_text,
                    "url": url
                })

        return results
