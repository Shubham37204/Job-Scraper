import time
from core.storage import init_db, is_new_job, save_job
from core.notifier import send_digest_email, is_recent
from core.verifier import verify_company
from scrapers.internshala import scrape_internshala
from scrapers.indeed      import scrape_indeed
from scrapers.shine import scrape_shine
from scrapers.naukri      import scrape_naukri
from scrapers.linkedin    import scrape_linkedin

KEYWORDS = [
    "python developer",
    "full stack developer",
    "backend developer",
    "react developer",
    "next.js developer",
    "aws engineer",
    "ai engineer",
    "ml engineer",
    "django developer",
    "node.js developer",
]

RELEVANT_TITLE_WORDS = [
    "python", "django", "flask", "fastapi",
    "full stack", "fullstack", "backend", "frontend", "front end",
    "react", "next", "node", "javascript", "typescript",
    "aws", "cloud", "devops", "sre", "reliability",
    "ai", "ml", "machine learning", "deep learning", "data scientist",
    "software", "developer", "engineer", "programmer",
    "api", "microservice", "docker", "kubernetes",
    "java", "kotlin", "flutter", "mobile",
]

BLOCKED_TITLE_WORDS = [
    "customer service", "customer acquisition", "human resources",
    "hr associate", "lead generation", "digital marketing", "seo",
    "content writer", "video editor", "social media",
    "performance marketing", "mechanical", "purchase engineer",
    "site engineer", "rf engineer", "teaching assistant",
    "sales", "marketing executive", "accountant",
]

def is_relevant(title):
    t = title.lower()
    return any(w in t for w in RELEVANT_TITLE_WORDS)

def is_blocked(title):
    t = title.lower()
    return any(w in t for w in BLOCKED_TITLE_WORDS)

def run_scraper():
    print("\n🔍 Starting job scan...\n")

    all_jobs = []

    for idx, keyword in enumerate(KEYWORDS):
        print(f"  🔎 Searching: {keyword}")
        all_jobs += scrape_internshala(keyword=keyword)
        all_jobs += scrape_indeed(keyword=keyword, location="India")
        all_jobs += scrape_shine(keyword=keyword, location="India")

        if (idx + 1) % 3 == 0:
            print("  ⏳ Cooling down 15 seconds...")
            time.sleep(15)

    # These are slower — run once with broad terms
    all_jobs += scrape_naukri(keyword="software developer", location="india")
    all_jobs += scrape_linkedin(keyword="software developer india", location="India")

    print(f"\n📦 Total fetched: {len(all_jobs)}")

    new_jobs             = []
    seen_links           = set()
    skipped_irrelevant   = 0
    skipped_old          = 0
    skipped_duplicate    = 0
    skipped_suspicious   = 0

    for job in all_jobs:
        link    = job.get("link", "")
        title   = job.get("title", "N/A")
        company = job.get("company", "N/A")

        if not link or title == "N/A" or company == "N/A":
            continue
        if is_blocked(title) or not is_relevant(title):
            skipped_irrelevant += 1
            continue
        if link in seen_links or not is_new_job(link):
            skipped_duplicate += 1
            continue
        if not is_recent(job.get("posted", "N/A")):
            skipped_old += 1
            continue

        # --- Company verification ---
        verification = verify_company(company)
        job["verified"]      = verification["verdict"]
        job["company_score"] = verification["score"]
        job["company_reason"]= verification["reason"]

        # Only hard-block if very suspicious (score < 30)
        # Still include ⚠️ Unverified jobs — just flag them
        if verification["score"] < 30:
            skipped_suspicious += 1
            print(f"  🚨 Blocked suspicious company: {company} (score: {verification['score']})")
            continue

        seen_links.add(link)
        save_job(job)
        new_jobs.append(job)

    print(f"\n  🚫 Irrelevant/blocked titles : {skipped_irrelevant}")
    print(f"  🔁 Duplicates               : {skipped_duplicate}")
    print(f"  📅 Too old                  : {skipped_old}")
    print(f"  🚨 Suspicious companies     : {skipped_suspicious}")
    print(f"  ✅ New verified jobs        : {len(new_jobs)}\n")

    send_digest_email(new_jobs)
    print(f"✅ Done.\n")

if __name__ == "__main__":
    init_db()
    run_scraper()
