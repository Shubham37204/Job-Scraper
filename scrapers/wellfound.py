from playwright.sync_api import sync_playwright

def scrape_wellfound(keyword="python"):
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
            url = f"https://wellfound.com/jobs?q={keyword.replace(' ', '+')}&l=India"
            page.goto(url, timeout=30000)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            SELECTORS = [
                ".styles_component__Ey28k",   
                "[data-test='JobListing']",   
                ".job-listing",
                "div[class*='JobListing']",    
                "div[class*='job']",          
            ]

            cards = []
            used_selector = None
            for selector in SELECTORS:
                found = page.query_selector_all(selector)
                if found:
                    cards = found
                    used_selector = selector
                    print(f"[Wellfound] Matched selector: {selector}")
                    break

            if not cards:
                with open("wellfound_debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print(
                    "[Wellfound] No cards found with any selector.\n"
                    "  → Saved page HTML to wellfound_debug.html\n"
                    "  → Open it in browser → DevTools → find job card selector\n"
                    "  → Add it to the SELECTORS list above"
                )
                return []

            for card in cards:
                title_el   = (
                    card.query_selector("h2") or
                    card.query_selector("h3") or
                    card.query_selector("[class*='title']")
                )
                company_el = (
                    card.query_selector("[class*='company']") or
                    card.query_selector("[class*='startup']")
                )
                link_el = card.query_selector("a[href*='/jobs/']") or card.query_selector("a")

                title   = title_el.inner_text().strip()   if title_el   else "N/A"
                company = company_el.inner_text().strip() if company_el else "N/A"

                raw_link = link_el.get_attribute("href") if link_el else ""
                link = (
                    f"https://wellfound.com{raw_link}"
                    if raw_link.startswith("/")
                    else raw_link
                )

                if title == "N/A" and company == "N/A":
                    continue   

                jobs.append({
                    "title":   title,
                    "company": company,
                    "link":    link,
                    "posted":  "N/A",
                    "source":  "Wellfound"
                })

        except Exception as e:
            print(f"[Wellfound] Playwright error: {e}")
        finally:
            browser.close()

    print(f"[Wellfound] Found {len(jobs)} jobs for '{keyword}'")
    return jobs
