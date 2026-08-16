import logging
import httpx
from typing import Optional
from backend.models import Listing
from backend.config import settings

logger = logging.getLogger("rental_sniffer.notification")

async def send_discord_alert(listing: Listing) -> bool:
    if not settings.DISCORD_WEBHOOK_URL:
        logger.warning("Discord Webhook URL not configured. Skipping alert.")
        return False

    phone_str = listing.phone or "Chưa rõ"
    zalo_link = f"https://zalo.me/{listing.phone}" if listing.phone else "N/A"
    
    embed = {
        "title": f"🚨 Cho thuê Căn hộ Bông Sao ({listing.block or 'Block B1'})",
        "url": listing.url,
        "color": 5814783,  # Emerald / Green
        "fields": [
            {"name": "💰 Giá", "value": listing.price_text, "inline": True},
            {"name": "🏠 Thiết kế", "value": f"{listing.bedrooms or 2}PN {listing.bathrooms or 2}WC", "inline": True},
            {"name": "📞 SĐT / Zalo", "value": f"{phone_str} ([Mở Zalo]({zalo_link}))" if listing.phone else phone_str, "inline": True},
            {"name": "🌐 Nguồn", "value": listing.source, "inline": True},
            {"name": "📝 Chi tiết", "value": listing.description[:300] + ("..." if len(listing.description) > 300 else "")}
        ],
        "footer": {"text": "Bông Sao Rental Sniffer • Super Recent Match"}
    }

    payload = {
        "content": "@everyone 🚨 **Phát hiện căn hộ Bông Sao mới phù hợp tiêu chí!**",
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
    return await send_discord_alert(listing)
