from playwright.sync_api import sync_playwright

def scrape_shine(keyword="python developer", location="india"):
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
        )
        page = context.new_page()

        try:
            url = (
                f"https://www.shine.com/job-search/"
                f"{keyword.strip().lower().replace(' ', '-')}-jobs-in-"
                f"{location.strip().lower().replace(' ', '-')}"
            )
            page.goto(url, timeout=30000)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(4000)

            # Scroll to load more jobs
            for _ in range(3):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)

            # Outer card contains everything including posted date
            cards = page.query_selector_all("[class*='jobCardNova_jobCard']")
            if not cards:
                cards = page.query_selector_all("[class*='jobCard']")

            if not cards:
                print("[Shine] No cards found.")
                return []

            seen = set()

            for card in cards:
                try:
                    title_el   = card.query_selector("h3[itemprop='name']")
                    company_el = card.query_selector("[class*='bigCardTopTitleName']")
                    date_el    = card.query_selector("[class*='postedData']")
                    link_el    = card.query_selector("a[href*='/jobs/']")

                    title   = title_el.inner_text().strip()   if title_el   else "N/A"
                    company = company_el.inner_text().strip() if company_el else "N/A"
                    posted  = date_el.inner_text().strip()    if date_el    else "N/A"

                    raw_link = link_el.get_attribute("href")  if link_el    else ""
                    link = (
                        f"https://www.shine.com{raw_link}"
                        if raw_link.startswith("/")
                        else raw_link
                    )

                    if title == "N/A" or company == "N/A" or not link:
                        continue
                    if link in seen:
                        continue
                    seen.add(link)

                    jobs.append({
                        "title":   title,
                        "company": company,
                        "link":    link,
                        "posted":  posted,
                        "source":  "Shine"
                    })
                except Exception:
                    continue

        except Exception as e:
            print(f"[Shine] Error: {e}")
        finally:
            browser.close()

    print(f"[Shine] Found {len(jobs)} jobs for '{keyword}'")
    return jobs