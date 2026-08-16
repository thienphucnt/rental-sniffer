import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple
from backend.models import Listing, ScraperRunLog
from backend.config import settings

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash_id TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    source_id TEXT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    price_text TEXT,
                    price_val REAL,
                    phone TEXT,
                    seller_name TEXT,
                    description TEXT,
                    block TEXT,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    is_rental INTEGER DEFAULT 1,
                    matches_target INTEGER DEFAULT 0,
                    published_at TIMESTAMP,
                    is_fresh INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified_at TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraper_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    items_found INTEGER DEFAULT 0,
                    matches_found INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'SUCCESS',
                    error_message TEXT
                )
            """)

            # Safe migrations if upgrading existing db
            try:
                cursor.execute("ALTER TABLE listings ADD COLUMN published_at TIMESTAMP")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE listings ADD COLUMN is_fresh INTEGER DEFAULT 1")
            except Exception:
                pass

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash_id ON listings(hash_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone ON listings(phone)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches ON listings(matches_target)")
            conn.commit()

    @staticmethod
    def generate_hash(source: str, url: str, phone: Optional[str] = None) -> str:
        """Generate canonical SHA-256 fingerprint for deduplication."""
        clean_url = url.split("?")[0].strip().lower()
        clean_phone = (phone or "").strip().replace(" ", "").replace(".", "")
        raw = f"{source.lower()}:{clean_url}:{clean_phone}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def is_duplicate(self, hash_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM listings WHERE hash_id = ?", (hash_id,))
            return cursor.fetchone() is not None

    def save_listing(self, listing: Listing) -> Tuple[bool, bool]:
        """
        Saves listing to database.
        Returns tuple: (is_inserted, is_new_match)
        """
        if self.is_duplicate(listing.hash_id):
            return False, False

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO listings (
                    hash_id, source, source_id, title, url, price_text, price_val,
                    phone, seller_name, description, block, bedrooms, bathrooms,
                    is_rental, matches_target, published_at, is_fresh, created_at, notified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                listing.hash_id, listing.source, listing.source_id, listing.title,
                listing.url, listing.price_text, listing.price_val, listing.phone,
                listing.seller_name, listing.description, listing.block,
                listing.bedrooms, listing.bathrooms, 1 if listing.is_rental else 0,
                1 if listing.matches_target else 0,
                listing.published_at.isoformat() if listing.published_at else None,
                1 if listing.is_fresh else 0,
                listing.created_at.isoformat(),
                listing.notified_at.isoformat() if listing.notified_at else None
            ))
            conn.commit()
            return True, listing.matches_target

    def clear_database(self):
        """Wipes all listings and scraper logs to start with a fresh slate."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM listings")
            cursor.execute("DELETE FROM scraper_logs")
            conn.commit()

    def update_notified(self, hash_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings SET notified_at = ? WHERE hash_id = ?",
                (datetime.now().isoformat(), hash_id)
            )
            conn.commit()

    def log_run(self, log: ScraperRunLog):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scraper_logs (source, timestamp, items_found, matches_found, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                log.source, log.timestamp.isoformat(), log.items_found,
                log.matches_found, log.status, log.error_message
            ))
            conn.commit()

    def get_recent_listings(self, limit: int = 50, matches_only: bool = False) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM listings"
            if matches_only:
                query += " WHERE matches_target = 1"
            query += " ORDER BY created_at DESC LIMIT ?"
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_recent_logs(self, limit: int = 30) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scraper_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

db = Database()
