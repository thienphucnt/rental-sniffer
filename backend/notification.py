import logging
import httpx
from typing import Optional
from backend.models import Listing
from backend.config import settings

logger = logging.getLogger("rental_sniffer.notification")

async def send_telegram_alert(listing: Listing) -> bool:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.debug("Telegram credentials not configured. Skipping alert.")
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    phone_str = listing.phone or "Chưa cập nhật"
    zalo_link = f"https://zalo.me/{listing.phone}" if listing.phone else "N/A"
    
    message = (
        f"🚨 <b>PHÁT HIỆN CĂN HỘ CHO THUÊ MỚI!</b> 🚨\n\n"
        f"📍 <b>Dự án:</b> Chung cư Bông Sao ({listing.block or 'Block B1'})\n"
        f"🏠 <b>Cấu trúc:</b> {listing.bedrooms or 2}PN - {listing.bathrooms or 2}WC\n"
        f"💰 <b>Giá thuê:</b> <code>{listing.price_text}</code>\n"
        f"📞 <b>SĐT / Zalo:</b> <code>{phone_str}</code> (<a href='{zalo_link}'>Mở Zalo</a>)\n"
        f"🌐 <b>Nguồn:</b> {listing.source}\n\n"
        f"📝 <b>Mô tả ngắn:</b>\n<i>{listing.description[:200]}...</i>\n\n"
        f"🔗 <a href='{listing.url}'><b>XEM CHI TIẾT BÀI ĐĂNG</b></a>"
    )

    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info(f"Successfully sent Telegram alert for listing {listing.hash_id}")
                return True
            else:
                logger.error(f"Telegram API error {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False

async def send_discord_alert(listing: Listing) -> bool:
    if not settings.DISCORD_WEBHOOK_URL:
        logger.debug("Discord Webhook URL not configured. Skipping alert.")
        return False

    embed = {
        "title": f"🚨 Cho thuê Căn hộ Bông Sao ({listing.block or 'Block B1'})",
        "url": listing.url,
        "color": 5814783,  # Emerald / Green
        "fields": [
            {"name": "💰 Giá", "value": listing.price_text, "inline": True},
            {"name": "🏠 Thiết kế", "value": f"{listing.bedrooms or 2}PN {listing.bathrooms or 2}WC", "inline": True},
            {"name": "📞 SĐT / Zalo", "value": listing.phone or "Chưa rõ", "inline": True},
            {"name": "🌐 Nguồn", "value": listing.source, "inline": True},
            {"name": "📝 Chi tiết", "value": listing.description[:300] + ("..." if len(listing.description) > 300 else "")}
        ],
        "footer": {"text": f"Bông Sao Rental Sniffer • Source ID: {listing.source_id or 'N/A'}"}
    }

    payload = {
        "content": "@everyone Phát hiện căn hộ mới phù hợp tiêu chí!",
        "embeds": [embed]
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)
            if resp.status_code in (200, 204):
                logger.info(f"Successfully sent Discord alert for listing {listing.hash_id}")
                return True
            else:
                logger.error(f"Discord Webhook error {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")
        return False

async def dispatch_notifications(listing: Listing) -> bool:
    tg_success = await send_telegram_alert(listing)
    dc_success = await send_discord_alert(listing)
    return tg_success or dc_success
