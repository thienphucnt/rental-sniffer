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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                resp = await client.get(self.target_url, headers=headers)
                if resp.status_code == 200:
                    return self._parse_html(resp.text)
                else:
                    logger.debug(f"[{self.name}] Returned status {resp.status_code}")
                    return []
            except Exception as e:
                logger.debug(f"[{self.name}] Error fetching listings: {e}")
                return []

    def _parse_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(self.card_selector)
        results = []

        for card in cards:
            title_elem = card.select_one(".title, h3, h2, a[title], .ct_title")
            link_elem = card.select_one("a[href]")
            price_elem = card.select_one(".price, .price-text, .ct_price")
            desc_elem = card.select_one(".description, .summary, p, .ct_dt")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                url = link_elem.get("href", "")
                if not url.startswith("http"):
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

# Factory functions for verified targets:
def create_homedy_scraper():
    return GenericPlatformScraper(
        "Homedy.com",
        "https://homedy.com/cho-thue-can-ho-tp-ho-chi-minh",
        ".item, .product-item"
    )

def create_alonhadat_scraper():
    return GenericPlatformScraper(
        "Alonhadat.com.vn",
        "https://alonhadat.com.vn/nha-dat/cho-thue/can-ho-chung-cu/2/ho-chi-minh/39/quan-8.html?keyword=b%C3%B4ng+sao",
        ".content-item"
    )
