import asyncio
import json
import os
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://kolkatapolice.gov.in/show-all-missing-vehicle/"
OUTPUT_DIR = "missing_vehicles_pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def scrape_page(page, page_number):
    print(f"🔎 Scraping page {page_number}...")
    await page.goto(f"{BASE_URL}?paged={page_number}", timeout=60000)
    await page.wait_for_selector("table.missing-table tbody tr")

    rows = await page.query_selector_all("table.missing-table tbody tr")
    page_data = []

    for row_index, row in enumerate(rows, start=1):
        cols = await row.query_selector_all("td")
        if len(cols) < 7:
            continue

        record = {
            "RegistrationNo": (await cols[0].text_content()).strip(),
            "EngineNo": (await cols[1].text_content()).strip(),
            "ChassisNo": (await cols[2].text_content()).strip(),
            "CaseNo": (await cols[3].text_content()).strip(),
            "Model": (await cols[4].text_content()).strip(),
            "Manufacturer": (await cols[5].text_content()).strip(),
            "LostOn": (await cols[6].text_content()).strip(),
        }

        # Handle View Details
        try:
            detail_btn = await row.query_selector("a")
            if detail_btn:
                await detail_btn.click()
                await page.wait_for_selector(".modal.show", timeout=10000)

                modal_html = await page.inner_html(".modal.show")
                modal_soup = BeautifulSoup(modal_html, "html.parser")

                for tr in modal_soup.select("table tbody tr"):
                    tds = tr.find_all("td")
                    if len(tds) >= 2:
                        key = tds[0].get_text(strip=True).replace(" ", "_")
                        value = tds[1].get_text(strip=True)
                        if key not in ["Registration_No", "Engine_No", "Chasis_No"]:  # skip duplicates
                            record[key] = value

                # Close modal
                close_btn = await page.query_selector(".modal.show button.btn-close")
                if close_btn:
                    await close_btn.click()
                    await page.wait_for_selector(".modal.show", state="detached")

                await asyncio.sleep(random.uniform(1, 2))  # polite delay
        except Exception as e:
            print(f"⚠️ Modal failed for row {row_index} on page {page_number}: {e}")

        page_data.append(record)

    # Save JSON for this page
    output_file = os.path.join(OUTPUT_DIR, f"missing_vehicles_page_{page_number}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(page_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved page {page_number} → {output_file}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        total_pages = 215
        for page_number in range(1, total_pages + 1):
            await scrape_page(page, page_number)
            await asyncio.sleep(random.uniform(2, 4))

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
