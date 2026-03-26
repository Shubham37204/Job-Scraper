import requests
from bs4 import BeautifulSoup

def scrape_internshala(keyword="python developer"):
    formatted_keyword = keyword.strip().lower().replace(" ", "-")
    url = f"https://internshala.com/jobs/keywords-{formatted_keyword}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"[Internshala] Request failed: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    job_cards = soup.select(".individual_internship")

    if not job_cards:
        print("[Internshala] No job cards found — selectors may need updating")
        return []

    jobs = []
    for card in job_cards:
        title_el   = card.select_one(".job-internship-name")
        company_el = card.select_one(".company-name")
        date_el    = card.select_one(".status-inactive")

        title   = title_el.text.strip()   if title_el   else "N/A"
        company = company_el.text.strip() if company_el else "N/A"
        posted  = date_el.text.strip()    if date_el    else "N/A"

        raw_link = card.get("data-href", "")           
        if not raw_link:
            link_el  = card.select_one("h3.job-internship-name a, a.job-title-href")
            raw_link = link_el["href"] if link_el else ""

        link = (
            f"https://internshala.com{raw_link}"
            if raw_link.startswith("/")
            else raw_link
        )

        print(f"  → {title} | {company} | {link}")

        jobs.append({
            "title":   title,
            "company": company,
            "link":    link,
            "posted":  posted,
            "source":  "Internshala"
        })

    print(f"[Internshala] Found {len(jobs)} jobs for '{keyword}'")
    return jobs