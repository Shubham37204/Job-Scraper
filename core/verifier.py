import requests
import time
import re
from bs4 import BeautifulSoup

# Cached results so we don't re-check the same company twice in one run
_cache = {}

# Known legit company name patterns that are always trusted
TRUSTED_COMPANIES = {
    "google", "microsoft", "amazon", "meta", "apple", "tcs",
    "infosys", "wipro", "hcl", "accenture", "ibm", "adobe",
    "flipkart", "swiggy", "zomato", "razorpay", "phonepe",
    "persistent systems", "mphasis", "mindtree", "ltimindtree",
    "cognizant", "capgemini", "deloitte", "pwc", "ey", "kpmg",
    "optum", "oracle", "sap", "atlassian", "freshworks",
}

# Red flag words in company names
SUSPICIOUS_PATTERNS = [
    r"\bpvt\b.*\bpvt\b",         # "Pvt Ltd Pvt Ltd" duplicate
    r"(solutions|services|technologies){2,}",  # "solutions solutions"
    r"^[A-Z]{1,3}\s+(pvt|ltd|llp)$",  # Very short like "AB Pvt Ltd"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
}

def check_ambitionbox(company_name):
    """
    Ambitionbox is India's equivalent of Glassdoor.
    Returns (rating, review_count) or (None, 0) if not found.
    """
    try:
        slug = company_name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s]", "", slug)   # Remove special chars
        slug = slug.replace(" ", "-")
        url  = f"https://www.ambitionbox.com/overview/{slug}-overview"

        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code != 200:
            return None, 0

        soup   = BeautifulSoup(res.text, "html.parser")
        rating = soup.select_one("[class*='rating']")
        reviews= soup.select_one("[class*='review']")

        rating_val  = float(rating.text.strip()) if rating else None
        reviews_val = int(re.sub(r"[^\d]", "", reviews.text)) if reviews else 0

        return rating_val, reviews_val

    except Exception:
        return None, 0


def check_company_website(company_name):
    """
    Searches Google for the company's official website.
    Returns True if a credible domain is found.
    """
    try:
        query = f"{company_name} official website India"
        url   = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        res  = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        # Look for cite tags — these show the URL in Google results
        cites = [c.text for c in soup.select("cite")]

        # If any result has a real domain (not linkedin/naukri), it's a good sign
        for cite in cites:
            if any(skip in cite for skip in ["linkedin", "naukri", "glassdoor", "google"]):
                continue
            if "." in cite and len(cite) > 6:
                return True, cite   # Found a real website

        return False, None

    except Exception:
        return False, None


def has_suspicious_name(company_name):
    """Flags company names that match known scam/fake patterns"""
    name_lower = company_name.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, name_lower):
            return True
    return False


def verify_company(company_name):
    """
    Main function — returns a dict with score and verdict.
    Score: 0-100
    - 80+  → ✅ Likely Genuine
    - 50-79 → ⚠️ Unverified (proceed with caution)
    - <50  → 🚨 Suspicious
    """
    if not company_name or company_name == "N/A":
        return {"score": 0, "verdict": "🚨 Suspicious", "reason": "No company name"}

    # Use cache to avoid rechecking same company
    if company_name in _cache:
        return _cache[company_name]

    score   = 50   # Start at neutral
    reasons = []

    # --- Check 1: Is it a known trusted company? (+50 bonus) ---
    if any(trusted in company_name.lower() for trusted in TRUSTED_COMPANIES):
        score += 50
        reasons.append("✅ Known company")

    # --- Check 2: Suspicious name pattern (-30) ---
    if has_suspicious_name(company_name):
        score -= 30
        reasons.append("🚨 Suspicious name pattern")

    # --- Check 3: Ambitionbox rating ---
    rating, review_count = check_ambitionbox(company_name)
    time.sleep(1)   # Polite delay

    if rating is not None:
        if rating >= 3.5 and review_count >= 10:
            score   += 20
            reasons.append(f"✅ Ambitionbox: {rating}★ ({review_count} reviews)")
        elif rating >= 2.5:
            score   += 5
            reasons.append(f"⚠️ Ambitionbox: {rating}★ ({review_count} reviews)")
        else:
            score   -= 10
            reasons.append(f"🚨 Low Ambitionbox rating: {rating}★")
    else:
        score   -= 10
        reasons.append("⚠️ Not found on Ambitionbox")

    # --- Check 4: Has a real website ---
    has_site, domain = check_company_website(company_name)
    time.sleep(1)

    if has_site:
        score   += 15
        reasons.append(f"✅ Website found: {domain}")
    else:
        score   -= 10
        reasons.append("⚠️ No official website found")

    # Clamp score between 0 and 100
    score = max(0, min(100, score))

    if score >= 80:
        verdict = "✅ Likely Genuine"
    elif score >= 50:
        verdict = "⚠️ Unverified"
    else:
        verdict = "🚨 Suspicious"

    result = {
        "score":   score,
        "verdict": verdict,
        "reason":  " | ".join(reasons),
        "rating":  rating,
        "reviews": review_count,
    }

    _cache[company_name] = result   # Cache so we don't repeat for same company
    return result