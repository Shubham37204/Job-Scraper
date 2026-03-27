from playwright.sync_api import sync_playwright

def scrape_naukri(keyword="python developer", location="india"):
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
            locale="en-IN",
        )
        page = context.new_page()

        try:
            formatted_keyword  = keyword.strip().replace(" ", "-")
            formatted_location = location.strip().replace(" ", "-")
            url = f"https://www.naukri.com/{formatted_keyword}-jobs-in-{formatted_location}"

            page.goto(url, timeout=40000)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            cards = page.query_selector_all(".cust-job-tuple")
            if not cards:
                cards = page.query_selector_all(".jobTuple")
            if not cards:
                with open("naukri_debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print("[Naukri] No cards found. Saved naukri_debug.html.")
                return []

            for card in cards:
                title_el   = card.query_selector("a.title")
                company_el = card.query_selector(".comp-name")
                date_el    = card.query_selector(".job-post-day")
                link_el    = card.query_selector("a.title")

                title   = title_el.inner_text().strip()  if title_el   else "N/A"
                company = company_el.inner_text().strip() if company_el else "N/A"
                posted  = date_el.inner_text().strip()   if date_el    else "N/A"
                link    = link_el.get_attribute("href")  if link_el    else ""

                if title == "N/A" or company == "N/A":
                    continue

                jobs.append({"title": title, "company": company,
                             "link": link, "posted": posted, "source": "Naukri"})

        except Exception as e:
            print(f"[Naukri] Error: {e}")
        finally:
            browser.close()

    print(f"[Naukri] Found {len(jobs)} jobs for '{keyword}'")
    return jobs