import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import logging
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

from backend.config import settings
from backend.database import db
from backend.models import Listing, ScraperRunLog, RegexTestRequest, RegexTestResponse
from backend.parser import analyze_listing
from backend.notification import dispatch_notifications, send_telegram_alert, send_discord_alert
from backend.scrapers.chotot import ChototScraper
from backend.scrapers.batdongsan import BatdongsanScraper
from backend.scrapers.phongtro123 import Phongtro123Scraper
from backend.scrapers.mogi import MogiScraper
from backend.scrapers.facebook import FacebookScraper
from backend.scrapers.generic import (
    create_muaban_scraper, create_homedy_scraper,
    create_dothi_scraper, create_rever_scraper
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("rental_sniffer.main")

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

# Enable CORS for Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scraper Instances Registry
scrapers_list = [
    ChototScraper(),
    BatdongsanScraper(),
    Phongtro123Scraper(),
    MogiScraper(),
    FacebookScraper(),
    create_muaban_scraper(),
    create_homedy_scraper(),
    create_dothi_scraper(),
    create_rever_scraper()
]

IS_RUNNING = False
LAST_SCAN_TIME: Optional[datetime] = None

async def run_all_scrapers():
    global IS_RUNNING, LAST_SCAN_TIME
    if IS_RUNNING:
        logger.warning("Scan already in progress. Skipping loop execution.")
        return

    IS_RUNNING = True
    LAST_SCAN_TIME = datetime.now()
    logger.info("Starting automated scraper cycle across all platforms...")

    for scraper in scrapers_list:
        try:
            listings = await scraper.run()
            new_inserted = 0
            new_matches = 0

            for listing in listings:
                inserted, is_new_match = db.save_listing(listing)
                if inserted:
                    new_inserted += 1
                if is_new_match:
                    new_matches += 1
                    if listing.is_fresh:
                        logger.info(f"🎯 FRESH MATCH FOUND! Source: {listing.source} | Title: {listing.title}")
                        # Dispatch instant notifications
                        notified = await dispatch_notifications(listing)
                        if notified:
                            db.update_notified(listing.hash_id)
                    else:
                        logger.info(f"⏳ Match found but older than {settings.MAX_LISTING_AGE_HOURS}h. Saved to DB without alert. Title: {listing.title}")

            log_entry = ScraperRunLog(
                source=scraper.name,
                items_found=len(listings),
                matches_found=new_matches,
                status="SUCCESS"
            )
            db.log_run(log_entry)

        except Exception as e:
            logger.error(f"Error executing scraper {scraper.name}: {e}")
            log_entry = ScraperRunLog(
                source=scraper.name,
                status="ERROR",
                error_message=str(e)
            )
            db.log_run(log_entry)

    IS_RUNNING = False
    logger.info(f"Scraper cycle completed at {datetime.now().isoformat()}")

async def scheduled_loop():
    logger.info(f"Initializing high-speed continuous listener (Polling Interval: {settings.POLL_INTERVAL_SECONDS}s / {settings.POLL_INTERVAL_SECONDS//60} min, Max Age: {settings.MAX_LISTING_AGE_HOURS}h)")
    while True:
        try:
            await run_all_scrapers()
        except Exception as e:
            logger.error(f"Unhandled exception in background loop: {e}")
        
        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)

async def keep_alive_loop():
    """Periodically pings the public endpoint every 10 minutes to prevent Render free instance from sleeping."""
    if not settings.RENDER_EXTERNAL_URL:
        return
    logger.info(f"Keep-alive self-pinger initialized for {settings.RENDER_EXTERNAL_URL}")
    import httpx
    while True:
        await asyncio.sleep(600)  # Every 10 minutes
        try:
            url = f"{settings.RENDER_EXTERNAL_URL}/api/status"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                logger.info(f"Keep-alive ping sent to {url} (Status: {resp.status_code})")
        except Exception as e:
            logger.debug(f"Keep-alive ping notice: {e}")

@app.on_event("startup")
async def startup_event():
    db.init_db()
    asyncio.create_task(scheduled_loop())
    asyncio.create_task(keep_alive_loop())

@app.get("/api/status")
def get_status():
    recent = db.get_recent_listings(limit=100)
    matches = db.get_recent_listings(limit=100, matches_only=True)
    return {
        "status": "RUNNING" if not IS_RUNNING else "SCANNING",
        "last_scan": LAST_SCAN_TIME.isoformat() if LAST_SCAN_TIME else None,
        "poll_interval_seconds": settings.POLL_INTERVAL_SECONDS,
        "max_listing_age_hours": settings.MAX_LISTING_AGE_HOURS,
        "total_scraped_items": len(recent),
        "total_matches_found": len(matches),
        "target_location": settings.TARGET_LOCATION,
        "target_specs": "Block B1 / Lô B, 2PN 2WC Rent"
    }

@app.get("/api/listings")
def get_listings(limit: int = 50, matches_only: bool = False):
    return db.get_recent_listings(limit=limit, matches_only=matches_only)

@app.get("/api/logs")
def get_logs(limit: int = 30):
    return db.get_recent_logs(limit=limit)

@app.post("/api/trigger-scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    if IS_RUNNING:
        raise HTTPException(status_code=400, detail="Scan cycle already running.")
    background_tasks.add_task(run_all_scrapers)
    return {"message": "Scan cycle triggered successfully."}

@app.post("/api/clear-data")
def clear_data():
    db.clear_database()
    return {"message": "All database records have been purged successfully."}

@app.post("/api/test-regex", response_model=RegexTestResponse)
def test_regex(req: RegexTestRequest):
    res = analyze_listing(req.title, req.description)
    return RegexTestResponse(
        is_rental=res["is_rental"],
        is_sale_excluded=not res["is_rental"],
        block_matched=res["block_matched"],
        bedrooms=res["bedrooms"],
        bathrooms=res["bathrooms"],
        phone=res["phone"],
        is_match=res["is_match"]
    )

@app.post("/api/test-notification")
async def test_notification():
    sample_listing = Listing(
        hash_id="test_hash_123",
        source="TEST_SYSTEM",
        source_id="TEST_001",
        title="[TEST ALERT] Cho thuê căn hộ Bông Sao Block B1 2PN 2WC full nội thất",
        url="https://www.nhatot.com/",
        price_text="7.5 triệu/tháng",
        price_val=7500000.0,
        phone="0909123456",
        seller_name="Anh Nam (Chủ nhà)",
        description="Cho thuê gấp căn hộ chung cư Bông Sao lô B1 2 phòng ngủ 2 vệ sinh. Căn góc thoáng mát, tầng trung view đẹp.",
        block="Block B1",
        bedrooms=2,
        bathrooms=2,
        is_rental=True,
        matches_target=True
    )
    tg_sent = await send_telegram_alert(sample_listing)
    dc_sent = await send_discord_alert(sample_listing)
    return {
        "telegram_sent": tg_sent,
        "discord_sent": dc_sent,
        "detail": "Sent test notifications. Check your Telegram/Discord channel."
    }

if __name__ == "__main__":
    import uvicorn
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio")
