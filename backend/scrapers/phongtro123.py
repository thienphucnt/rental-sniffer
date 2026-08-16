import logging
import httpx
from bs4 import BeautifulSoup
from typing import List
from backend.scrapers.base import BaseScraper

logger = logging.getLogger("rental_sniffer.scrapers.phongtro123")

class Phongtro123Scraper(BaseScraper):
    def __init__(self):
        super().__init__("Phongtro123 & Thuecanho123")
        self.urls = [
            "https://phongtro123.com/cho-thue-can-ho-chung-cu-quan-8-ho-chi-minh?s=b%C3%B4ng+sao",
            "https://thuecanho123.com/cho-thue-can-ho-chung-cu-quan-8-ho-chi-minh.html?s=b%C3%B4ng+sao"
        ]

    async def fetch_raw_listings(self) -> List[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        results = []

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for url in self.urls:
                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        parsed = self._parse_html(resp.text, base_url=url)
                        results.extend(parsed)
                except Exception as e:
                    logger.warning(f"[Phongtro123] Error fetching {url}: {e}")

        return results

    def _parse_html(self, html: str, base_url: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".post-item, .item-post, article, .post-listing")
        domain = "https://phongtro123.com" if "phongtro123" in base_url else "https://thuecanho123.com"
        results = []

        for item in items:
            title_elem = item.select_one(".post-title, .title, h3, h2")
            link_elem = item.select_one("a[href]")
            price_elem = item.select_one(".post-price, .price, .post-price-value")
            desc_elem = item.select_one(".post-summary, .summary, .post-body")
            phone_elem = item.select_one(".post-author-phone, .btn-call, .phone")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                href = link_elem.get("href", "")
                if not href.startswith("http"):
                    href = domain + href
                
                price_text = price_elem.get_text(strip=True) if price_elem else "Thỏa thuận"
                description = desc_elem.get_text(strip=True) if desc_elem else title
                phone = phone_elem.get_text(strip=True) if phone_elem else None

                results.append({
                    "source_id": href.split("/")[-1].split(".")[0],
                    "title": title,
                    "description": description,
                    "price_text": price_text,
                    "phone": phone,
                    "url": href
                })

        return results
