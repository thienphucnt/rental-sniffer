import logging
import httpx
from bs4 import BeautifulSoup
from typing import List
from backend.scrapers.base import BaseScraper
from backend.config import settings

logger = logging.getLogger("rental_sniffer.scrapers.batdongsan")

class BatdongsanScraper(BaseScraper):
    def __init__(self):
        super().__init__("Batdongsan.com.vn")
        self.search_url = "https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-bong-sao"

    async def fetch_raw_listings(self) -> List[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        results = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.search_url, headers=headers)
                
                # Cloudflare check
                if resp.status_code in (403, 503) or "Just a moment..." in resp.text:
                    logger.warning("[Batdongsan] Cloudflare challenge detected. Attempting Playwright stealth fetch...")
                    results = await self._fetch_via_playwright()
                else:
                    results = self._parse_html(resp.text)
        except Exception as e:
            logger.warning(f"[Batdongsan] Direct HTTP fetch failed ({e}). Falling back to Playwright...")
            results = await self._fetch_via_playwright()

        return results

    def _parse_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".re__card-info, .js__card, .re__body")
        results = []

        for card in cards:
            title_elem = card.select_one(".re__card-title, .js__card-title, h3")
            link_elem = card.select_one("a[href]")
            price_elem = card.select_one(".re__card-config-price, .re__card-price")
            desc_elem = card.select_one(".re__card-description, .re__card-summary")
            date_elem = card.select_one(".re__card-published-info-published-date, .re__card-published-info, .re__card-contact-date")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                url = link_elem.get("href", "")
                if not url.startswith("http"):
                    url = "https://batdongsan.com.vn" + url
                
                price_text = price_elem.get_text(strip=True) if price_elem else "Thỏa thuận"
                description = desc_elem.get_text(strip=True) if desc_elem else title
                published_text = date_elem.get_text(strip=True) if date_elem else ""

                results.append({
                    "source_id": url.split("/")[-1].replace(".htm", ""),
                    "title": title,
                    "description": description,
                    "price_text": price_text,
                    "published_text": published_text,
                    "url": url
                })

        return results

    async def _fetch_via_playwright(self) -> List[dict]:
        """Fetch using Playwright in a background thread to prevent Windows asyncio subprocess loop issues."""
        import asyncio
        return await asyncio.to_thread(self._sync_playwright_fetch)

    def _sync_playwright_fetch(self) -> List[dict]:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                try:
                    page.goto(self.search_url, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(3000)
                except Exception as nav_err:
                    logger.debug(f"[Batdongsan] Page navigation warning: {nav_err}")
                content = page.content()
                browser.close()
                return self._parse_html(content)
        except Exception as e:
            logger.error(f"[Batdongsan] Playwright fetch failed: {e}")
            return []
