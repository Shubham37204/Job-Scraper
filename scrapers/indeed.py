from playwright.sync_api import sync_playwright

def scrape_indeed(keyword="python developer", location="India"):
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })

        try:
            formatted_keyword  = keyword.replace(" ", "+")
            formatted_location = location.replace(" ", "+")
            url = f"https://in.indeed.com/jobs?q={formatted_keyword}&l={formatted_location}&sort=date"

            page.goto(url, timeout=30000)

            page.wait_for_selector(".job_seen_beacon", timeout=15000)

            cards = page.query_selector_all(".job_seen_beacon")

            if not cards:
                print("[Indeed] No job cards found after JS load.")
                return []

            for card in cards:
                title_el    = card.query_selector("h2.jobTitle span[title]")
                company_el  = card.query_selector("[data-testid='company-name']")
                location_el = card.query_selector("[data-testid='text-location']")
                date_el     = card.query_selector("[data-testid='myJobsStateDate']")
                link_el     = card.query_selector("h2.jobTitle a")

                title    = title_el.get_attribute("title").strip() if title_el    else "N/A"
                company  = company_el.inner_text().strip()         if company_el  else "N/A"
                posted   = date_el.inner_text().strip()            if date_el     else "N/A"

                raw_link = link_el.get_attribute("href") if link_el else ""
                link = (
                    f"https://in.indeed.com{raw_link}"
                    if raw_link.startswith("/")
                    else raw_link
                )

                jobs.append({
                    "title":   title,
                    "company": company,
                    "link":    link,
                    "posted":  posted,
                    "source":  "Indeed"
                })

        except Exception as e:
            print(f"[Indeed] Playwright error: {e}")
        finally:
            browser.close()

    print(f"[Indeed] Found {len(jobs)} jobs for '{keyword}' in {location}")
    return jobs
