from core.storage import init_db, is_new_job, save_job
from core.notifier import send_digest_email, is_recent
from scrapers.internshala import scrape_internshala
from scrapers.wellfound import scrape_wellfound
from scrapers.indeed import scrape_indeed

KEYWORDS = [
    "python developer",
    "full stack developer",
    "backend developer",
    "next.js developer",
    "react developer",
    "aws engineer",
    "ai engineer",
    "ml engineer",
    "django developer",
    "node.js developer",
]

BLOCKED_TITLE_WORDS = [
    "customer service", "customer acquisition", "human resources", "hr associate",
    "lead generation", "digital marketing", "seo", "content writer",
    "video editor", "social media", "performance marketing",
    "mechanical", "purchase engineer", "site engineer", "rf engineer",
    "teaching assistant", "sales", "marketing executive",
]

def is_blocked(title):
    title_lower = title.lower()
    return any(word in title_lower for word in BLOCKED_TITLE_WORDS)

def run_scraper():
    print("\n🔍 Starting job scan...\n")

    all_jobs = []

    for keyword in KEYWORDS:
        print(f"  🔎 Searching: {keyword}")
        all_jobs += scrape_internshala(keyword=keyword)
        all_jobs += scrape_indeed(keyword=keyword, location="India")
    all_jobs += scrape_wellfound(keyword="software engineer")

    print(f"\n📦 Total fetched: {len(all_jobs)}")

    new_jobs = []
    seen_links = set()  

    for job in all_jobs:
        link    = job.get("link", "")
        title   = job.get("title", "N/A")
        company = job.get("company", "N/A")

        if not link or title == "N/A" or company == "N/A":
            continue
        if link in seen_links:          
            continue
        if not is_new_job(link):        
            continue
        if not is_recent(job.get("posted", "N/A")):   
            print(f"  ⏭ Skipping old job: {title} ({job.get('posted')})")
            continue
        if is_blocked(title):          
            skipped_irrelevant += 1
            continue

        seen_links.add(link)
        save_job(job)
        new_jobs.append(job)

    send_digest_email(new_jobs)
    print(f"✅ Done. {len(new_jobs)} new recent jobs found.\n")


if __name__ == "__main__":
    init_db()
    run_scraper()
