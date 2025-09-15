from playwright.sync_api import sync_playwright
import time
import json

def scrape_missing_vehicles_page1():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # set to False if you want to see the browser
        page = browser.new_page()
        page.goto("https://zipnet.delhipolice.gov.in/VehiclesMobiles/MissingVehicles")

        # ✅ Show 50 entries on Page 1
        page.select_option("select[name='missingVehiclesGrid_length']", "50")
        time.sleep(2)  # wait for table refresh

        # ✅ Get all rows in Page 1
        page.wait_for_selector("#missingVehiclesGrid tbody tr")
        rows = page.query_selector_all("#missingVehiclesGrid tbody tr")

        for row in rows:
            cols = row.query_selector_all("td")
            if not cols or len(cols) < 9:
                continue

            record = {
                "state": cols[1].inner_text().strip(),
                "district": cols[2].inner_text().strip(),
                "police_station": cols[3].inner_text().strip(),
                "fir_number": cols[4].inner_text().strip(),
                "fir_date": cols[5].inner_text().strip(),
                "vehicle_registration_no": cols[6].inner_text().strip(),
                "vehicle_type": cols[7].inner_text().strip(),
                "status": cols[8].inner_text().strip()
            }

            # Expand row for details if available
            expand_icon = cols[0].query_selector("i.fa-plus-circle")
            if expand_icon:
                expand_icon.click()
                time.sleep(1)

                details_row = row.evaluate_handle("el => el.nextElementSibling")
                labels = details_row.query_selector_all("label")
                spans = details_row.query_selector_all("span")

                for label, span in zip(labels, spans):
                    key = (
                        label.inner_text()
                        .replace(":", "")
                        .strip()
                        .lower()
                        .replace(" ", "_")
                    )
                    record[key] = span.inner_text().strip()

            results.append(record)

        browser.close()
    return results


if __name__ == "__main__":
    data = scrape_missing_vehicles_page1()

    with open("theft_vehicles_page1.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Scraped {len(data)} records from Page 1 (50 entries) and saved to theft_vehicles_page1.json")
