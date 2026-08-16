import re
import unicodedata
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from backend.config import settings

def parse_relative_time(text: str) -> Optional[datetime]:
    """Parse relative time phrases like '5 phút trước', '2 giờ trước', 'Hôm qua', '15/08/2026' into datetime."""
    if not text:
        return None
    norm = normalize_text(text)
    now = datetime.now()

    # X phút trước
    m = re.search(r'(\d+)\s*(phút|phut|min)', norm)
    if m:
        return now - timedelta(minutes=int(m.group(1)))

    # X giờ trước
    h = re.search(r'(\d+)\s*(giờ|gio|hour|h)\s*(trước|truoc|ago)?', norm)
    if h:
        return now - timedelta(hours=int(h.group(1)))

    # Hôm nay / Vừa đăng
    if "hôm nay" in norm or "hom nay" in norm or "today" in norm or "vừa đăng" in norm or "vua dang" in norm:
        return now

    # Hôm qua
    if "hôm qua" in norm or "hom qua" in norm or "yesterday" in norm:
        return now - timedelta(days=1)

    # X ngày trước
    d = re.search(r'(\d+)\s*(ngày|ngay|day)', norm)
    if d:
        return now - timedelta(days=int(d.group(1)))

    # DD/MM/YYYY or DD-MM-YYYY
    date_match = re.search(r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', norm)
    if date_match:
        try:
            day, month, year = map(int, date_match.groups())
            return datetime(year, month, day)
        except ValueError:
            pass

    # MM/YYYY (e.g. tháng 08/2025 or 08/2026)
    month_year_match = re.search(r'tháng\s*(\d{1,2})[\/\-](\d{4})', norm)
    if month_year_match:
        try:
            month, year = map(int, month_year_match.groups())
            return datetime(year, month, 1)
        except ValueError:
            pass

    # Explicit year detection fallback (e.g. '2025', '2024')
    year_match = re.search(r'\b(202[0-5])\b', norm)
    if year_match:
        return datetime(int(year_match.group(1)), 1, 1)

    return None

def is_fresh_listing(published_at: Optional[datetime], max_hours: int = None) -> bool:
    """Check if listing was published within the allowable time window (default: 48 hours)."""
    if published_at is None:
        return False  # Strict mode: must have identifiable timing or assume fresh only if recent
    limit_hours = max_hours if max_hours is not None else settings.MAX_LISTING_AGE_HOURS
    cutoff = datetime.now() - timedelta(hours=limit_hours)
    return published_at >= cutoff

def get_freshness_label(published_at: Optional[datetime]) -> str:
    if not published_at:
        return "Chưa rõ thời gian"
    diff = datetime.now() - published_at
    if diff.total_seconds() < 3600:
        mins = max(1, int(diff.total_seconds() / 60))
        return f"⚡ Vừa đăng ({mins} phút trước)"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"🕒 Đăng hôm nay ({hours} giờ trước)"
    elif diff.total_seconds() < 172800:
        return "📅 Đăng hôm qua"
    else:
        days = int(diff.total_seconds() / 86400)
        return f"⚠️ Đăng {days} ngày trước ({published_at.strftime('%d/%m/%Y')})"

def normalize_text(text: str) -> str:
    """Normalize text into lowercase, stripped, standard space string."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def strip_accents(text: str) -> str:
    """Strip Vietnamese diacritics for non-accented fuzzy matching."""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    return text.replace('đ', 'd').replace('Đ', 'D')

# --- Regex Patterns ---

# Transaction type checks
RENTAL_PATTERNS = [
    r'\b(cho\s+thuê|cho\s+thue|thuê|thue)\b',
    r'\b(cho\s*mướn|cho\s*muon)\b',
]

EXCLUSION_PATTERNS = [
    r'\b(cần\s+bán|can\s+ban|bán\s+gấp|ban\s+gap|bán\s+căn|ban\s+can)\b',
    r'\b(chính\s+chủ\s+bán|chinh\s+chu\s+ban)\b',
    r'\b(giá\s+bán|gia\s+ban)\b',
    r'\b(bán|ban)\b(?!\s+(cho\s+thuê|hoặc\s+cho\s+thuê))',
]

# Location / Project matching
BONG_SAO_PATTERNS = [
    r'\bbông\s*sao\b',
    r'\bbong\s*sao\b',
]

# Block matching (Block B1, Lô B1, Lô B, Block B, B1)
BLOCK_PATTERNS = [
    r'\b(block|lô|lo)\s*b1\b',
    r'\b(block|lô|lo)\s*b\b',
    r'\bb1\b',
    r'\blô\s*b\b',
]

# Bedroom matching (2PN, 2 phòng ngủ, 2bed, 2 br)
BEDROOM_PATTERNS = [
    r'\b2\s*(pn|phòng\s*ngủ|phong\s*ngu|bed|br|phong)\b',
    r'\bhai\s*(pn|phòng\s*ngủ|phong\s*ngu)\b',
]

# Bathroom matching (2WC, 2 vệ sinh, 2 phòng vệ sinh, 2bath)
BATHROOM_PATTERNS = [
    r'\b2\s*(wc|vệ\s*sinh|ve\s*sinh|phòng\s*vệ\s*sinh|phong\s*ve\s*sinh|phòng\s*tắm|bath|nhi)\b',
    r'\bhai\s*(wc|vệ\s*sinh|ve\s*sinh)\b',
]

# Combined shortcut matching (2pn 2wc, 2pn2wc, 2 phòng ngủ 2 vệ sinh)
COMBINED_2PN_2WC = r'\b2\s*pn\s*2\s*wc\b|\b2\s*phòng\s*ngủ\s*2\s*vệ\s*sinh\b|\b2\s*phong\s*ngu\s*2\s*ve\s*sinh\b'

# Phone number regex
PHONE_PATTERN = r'\b(0[35789]\d{8}|0[35789]\d{1}[\s\.]?\d{3}[\s\.]?\d{4})\b'

def extract_phone(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(PHONE_PATTERN, text)
    if match:
        clean = re.sub(r'[\s\.]', '', match.group(0))
        return clean
    return None

def is_rental_listing(text: str) -> bool:
    norm = normalize_text(text)
    
    # Check if explicit sale exclusion applies
    for exc in EXCLUSION_PATTERNS:
        if re.search(exc, norm):
            # Check if it explicitly says "bán hoặc cho thuê"
            if not re.search(r'\b(hoặc|or)\s+(cho\s+thuê|thuê)\b', norm):
                return False
                
    # Check if rental pattern matches
    for rent in RENTAL_PATTERNS:
        if re.search(rent, norm):
            return True
            
    return False

def matches_block_b1(text: str) -> Optional[str]:
    norm = normalize_text(text)
    unaccented = strip_accents(norm)
    
    for pat in BLOCK_PATTERNS:
        if re.search(pat, norm) or re.search(pat, unaccented):
            if "b1" in norm or "b1" in unaccented:
                return "Block B1"
            return "Block B (Lô B)"
    return None

def parse_bedrooms_and_bathrooms(text: str) -> tuple[Optional[int], Optional[int]]:
    norm = normalize_text(text)
    unaccented = strip_accents(norm)
    
    # Check combined shortcut first
    if re.search(COMBINED_2PN_2WC, norm) or re.search(COMBINED_2PN_2WC, unaccented):
        return 2, 2
        
    bedrooms = None
    bathrooms = None
    
    for pat in BEDROOM_PATTERNS:
        if re.search(pat, norm) or re.search(pat, unaccented):
            bedrooms = 2
            break
            
    for pat in BATHROOM_PATTERNS:
        if re.search(pat, norm) or re.search(pat, unaccented):
            bathrooms = 2
            break

    # General number fallbacks if explicit pattern wasn't matched
    if bedrooms is None:
        pn_match = re.search(r'\b(\d+)\s*(pn|phòng\s*ngủ|phong\s*ngu)\b', norm)
        if pn_match:
            bedrooms = int(pn_match.group(1))

    if bathrooms is None:
        wc_match = re.search(r'\b(\d+)\s*(wc|vệ\s*sinh|ve\s*sinh)\b', norm)
        if wc_match:
            bathrooms = int(wc_match.group(1))
            
    return bedrooms, bathrooms

def analyze_listing(title: str, description: str = "") -> Dict[str, Any]:
    combined_text = f"{title} {description}"
    norm = normalize_text(combined_text)
    
    # Check location (Bông Sao)
    is_bong_sao = False
    for pat in BONG_SAO_PATTERNS:
        if re.search(pat, norm) or re.search(pat, strip_accents(norm)):
            is_bong_sao = True
            break
            
    is_rental = is_rental_listing(combined_text)
    block_matched = matches_block_b1(combined_text)
    bedrooms, bathrooms = parse_bedrooms_and_bathrooms(combined_text)
    phone = extract_phone(combined_text)
    
    # Check strict compliance:
    # 1. Must be rental
    # 2. Must be Bông Sao
    # 3. Must match Block B / B1
    # 4. Bedrooms == 2 and Bathrooms == 2
    is_match = bool(
        is_rental and
        is_bong_sao and
        block_matched and
        (bedrooms == 2) and
        (bathrooms == 2)
    )
    
    return {
        "is_bong_sao": is_bong_sao,
        "is_rental": is_rental,
        "block_matched": block_matched,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "phone": phone,
        "is_match": is_match
    }
