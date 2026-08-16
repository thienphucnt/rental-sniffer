# 🏙️ Bông Sao Rental Scraper & Social Media Listener

A highly resilient, low-latency web scraper and social media listener designed to track rare real estate rental listings for **Chung cư Bông Sao (Block B1, Ward 5, District 8, Ho Chi Minh City)**.

---

## 🎯 Target Search Specs
- **Location**: Chung cư Bông Sao, Phường 5, Quận 8, TP.HCM
- **Block Aliases**: `Block B1`, `Lô B1`, `Lô B`, `Block B`, `B1`
- **Unit Specs**: Exactly 2 Bedrooms & 2 Bathrooms (`2PN 2WC`, `2 phòng ngủ 2 vệ sinh`)
- **Transaction Type**: Rent (`Cho thuê`) only — strictly excludes sales (`bán`, `cần bán`, `bán gấp`)

---

## 🌐 Monitored Data Sources (Exhaustive List)
1. **Primary Real Estate Platforms**:
   - `Batdongsan.com.vn` (Headless Playwright stealth scraper)
   - `NhaTot.com / Chotot.com` (Direct JSON API integration)
   - `Muaban.net`
   - `Mogi.vn`
   - `Alonhadat.com.vn`
   - `Homedy.com`
   - `Dothi.net`
   - `Phongtro123.com` & `Thuecanho123.com`
   - `Rever.vn`
2. **Social Media (Facebook)**:
   - Group: *"Hộ cư dân CC Bông Sao quận 8"*
   - Group: *"Chợ cư dân Chung Cư bông sao quận 8"*
   - Group: *"Cư dân Chung cư Bông Sao Q8"*
   - Facebook Marketplace & global queries

---

## 🏗️ System Architecture

- **Backend Framework**: Python 3.11+ (FastAPI, Asyncio, Pydantic, HTTPX, BeautifulSoup4, Playwright, SQLite3)
- **Frontend Dashboard**: React + Vite + Lucide Icons + Modern CSS
- **Deduplication Engine**: SQLite database generating composite SHA-256 canonical fingerprints (`hash(source + url + phone)`) to eliminate duplicate notifications.
- **Alert Dispatcher**: Instant push notifications via Telegram Bot API and Discord Webhooks.

---

## 🚀 Getting Started

### 1. Environment Setup

Create a `.env` file in the project root:

```env
# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# High-Speed Listener Settings
POLL_INTERVAL_SECONDS=60      # Polling frequency in seconds (default: 60s / 1 min)
MAX_LISTING_AGE_HOURS=48      # Ignore stale listings older than 48 hours (2 days)

# Facebook Scraping (Session Cookies)
FB_COOKIE_C_USER=your_c_user_cookie
FB_COOKIE_XS=your_xs_cookie

# Optional Proxy Rotation
PROXY_URL=http://username:password@proxy-server:port
```

### 2. Backend Installation & Execution

```bash
# Create virtual environment
python -m venv venv
# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Install Playwright browser dependencies (for Batdongsan & Rever anti-bot bypass)
python -m playwright install chromium

# Run Unit Tests
python -m unittest backend/test_parser.py

# Launch FastAPI Server & Asynchronous Listener
python -m backend.main
```

The backend server will start at `http://localhost:8000`.

### 3. Frontend Control Center Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser to view the Control Center Dashboard.

---

## 🧪 Testing the Regex Engine

You can test listing titles and descriptions directly via the API or Web Dashboard:

```bash
curl -X POST http://localhost:8000/api/test-regex \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cho thuê chung cư Bông Sao Block B1 2PN 2WC lầu trung 7.5 triệu",
    "description": "Liên hệ 0909123456 xem nhà."
  }'
```

---

## 🛡️ Resilience & High Availability Features
- **Isolated Scraper Fault Tolerance**: A failure or rate-limit on one source (e.g. Batdongsan) does not interrupt scraping on other platforms (Nhatot, Mogi, Facebook).
- **Circuit Breaker & Retry Logic**: Exponential backoff with random jitter to prevent IP blocking.
- **Zero-Duplication Assurance**: Even after script restarts or re-posts by agents, duplicate alerts are completely blocked by the persistent SQLite hash index.
