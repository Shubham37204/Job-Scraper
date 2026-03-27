from playwright.sync_api import sync_playwright
from schedule import jobs


def scrape_linkedin(keyword="python developer", location="India"):
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,                        # ← no visible window
                                    args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()

        try:
            formatted_keyword = keyword.strip().replace(" ", "%20")
            formatted_location = location.strip().replace(" ", "%20")
            url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={formatted_keyword}"
                f"&location={formatted_location}"
                f"&f_TPR=r86400"
                f"&sortBy=DD"
            )

            page.goto(url, timeout=40000)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            cards = page.query_selector_all(".jobs-search__results-list li")
            if not cards:
                with open("linkedin_debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print("[LinkedIn] No cards found. Saved linkedin_debug.html.")
                return []

           # In scrapers/linkedin.py — replace the for card loop with:
            for card in cards:
                try:
                    title_el   = card.query_selector(".base-search-card__title")
                    company_el = card.query_selector(".base-search-card__subtitle")
                    date_el    = card.query_selector("time")
                    link_el    = card.query_selector("a.base-card__full-link")

                    title   = title_el.inner_text().strip()     if title_el   else "N/A"
                    company = company_el.inner_text().strip()   if company_el else "N/A"
                    posted  = date_el.get_attribute("datetime") if date_el    else "N/A"
                    link    = link_el.get_attribute("href")     if link_el    else ""

                    if title == "N/A" or company == "N/A":
                        continue

                    jobs.append({"title": title, "company": company,
                                "link": link, "posted": posted, "source": "LinkedIn"})
                except Exception:
                    continue   # ← skip broken card, don't crash entire scraper

        except Exception as e:
            print(f"[LinkedIn] Error: {e}")
        finally:
            browser.close()

    print(f"[LinkedIn] Found {len(jobs)} jobs for '{keyword}'")
    return jobs
