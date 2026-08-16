import logging
import httpx
from typing import List
from backend.scrapers.base import BaseScraper
from backend.config import settings

logger = logging.getLogger("rental_sniffer.scrapers.facebook")

class FacebookScraper(BaseScraper):
    def __init__(self):
        super().__init__("Facebook Groups & Marketplace")
        self.target_groups = [
            "Hộ cư dân CC Bông Sao quận 8",
            "Chợ cư dân Chung Cư bông sao quận 8",
            "Cư dân Chung cư Bông Sao Q8"
        ]
        self.search_queries = [
            "Cho thuê chung cư Bông Sao block B1",
            "Bông Sao lô B1 2pn 2wc",
            "Bông Sao lô B thuê"
        ]

    async def fetch_raw_listings(self) -> List[dict]:
        c_user = settings.FB_COOKIE_C_USER
        xs = settings.FB_COOKIE_XS

        if not c_user or not xs:
            logger.info("[Facebook] Session cookies (FB_COOKIE_C_USER / FB_COOKIE_XS) not configured. Using public web search indexer...")
            return await self._fetch_public_fb_index()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": f"c_user={c_user}; xs={xs};",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        results = []
        # Query Facebook Graph / Search endpoints asynchronously
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for query in self.search_queries:
                try:
                    search_url = f"https://www.facebook.com/search/posts?q={httpx.QueryParams({'q': query})}"
                    resp = await client.get(search_url, headers=headers)
                    if resp.status_code == 200:
                        # Extract post items from FB HTML / JSON payloads
                        parsed = self._extract_fb_posts(resp.text, query)
                        results.extend(parsed)
                except Exception as e:
                    logger.warning(f"[Facebook] Error querying '{query}': {e}")

        return results

    async def _fetch_public_fb_index(self) -> List[dict]:
        """Queries Google / Bing search indexers for recent Facebook group posts without triggering bans."""
        search_url = "https://html.duckduckgo.com/html/"
        results = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            for query in self.search_queries:
                try:
                    payload = {"q": f'site:facebook.com "Bông Sao" "{query}"'}
                    resp = await client.post(search_url, data=payload, headers=headers)
                    if resp.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(resp.text, "html.parser")
                        snippets = soup.select(".result__body")
                        for snippet in snippets:
                            title_elem = snippet.select_one(".result__title")
                            url_elem = snippet.select_one(".result__url")
                            desc_elem = snippet.select_one(".result__snippet")

                            if title_elem and url_elem:
                                title = title_elem.get_text(strip=True)
                                url = url_elem.get_text(strip=True)
                                description = desc_elem.get_text(strip=True) if desc_elem else title

                                if not url.startswith("http"):
                                    url = "https://" + url

                                results.append({
                                    "source_id": url.split("/")[-1],
                                    "title": title,
                                    "description": description,
                                    "price_text": "Thỏa thuận",
                                    "url": url
                                })
                except Exception as e:
                    logger.warning(f"[Facebook Public Search] Failed for query '{query}': {e}")

        return results

    def _extract_fb_posts(self, html: str, query: str) -> List[dict]:
        results = []
        # Regex search for Facebook post URLs and raw text payloads
        import re
        links = re.findall(r'href="(https://www\.facebook\.com/groups/[^"]+)"', html)
        for idx, link in enumerate(links[:10]):
            results.append({
                "source_id": f"fb_{idx}",
                "title": f"Facebook Post - Bông Sao ({query})",
                "description": f"Post match from query: {query}. Check group feed.",
                "price_text": "Thỏa thuận",
                "url": link
            })
        return results
