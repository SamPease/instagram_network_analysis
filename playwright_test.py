import time
from pathlib import Path
from playwright.sync_api import sync_playwright

TARGET_USER = "abigail.pease"  # Replace with the target username

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        # Go to target user profile
        page.goto(f"https://www.instagram.com/{TARGET_USER}/")
        page.wait_for_selector("a[href$='/following/']")
        page.locator("a[href$='/following/']").first.click()

        # Wait for dialog and initial user content
        page.wait_for_selector("div[role='dialog']", timeout=10000)
        page.wait_for_selector("div[role='dialog'] a[href^='/']", timeout=10000)
        print("✅ Dialog opened and list loaded")

        # Locate scrollable content container for username extraction
        scroll_area = page.locator("div[role='dialog'] div[class*='xyi19xy'] div[style*='overflow']").first

        usernames = set()
        prev_count = 0
        same_count_rounds = 0

        # Focus and scroll in the visual center of the modal
        modal = page.locator("div[role='dialog']").first
        box = modal.bounding_box()
        x_center = box["x"] + box["width"] / 2
        y_center = box["y"] + box["height"] / 2

        print("⏳ Scrolling to load full list...")
        while True:
            page.mouse.move(x_center, y_center)
            page.mouse.wheel(0, 600)
            time.sleep(2.0)

            # Extract usernames
            links = scroll_area.locator("a[href^='/']")
            for j in range(links.count()):
                href = links.nth(j).get_attribute("href")
                if (
                    href
                    and href.count("/") == 2
                    and not any(x in href for x in ["stories", "reels", "p"])
                    and not href.strip("/").startswith("explore")
                ):
                    username = href.strip("/").split("/")[0]
                    usernames.add(username)

            print(f"🔎 Found {len(usernames)} usernames so far...")

            if len(usernames) == prev_count:
                same_count_rounds += 1
            else:
                same_count_rounds = 0

            prev_count = len(usernames)

            if same_count_rounds >= 5:
                print("✅ No new users loaded after 5 scrolls. Done.")
                break

        print(f"✅ Final count: {len(usernames)} usernames:")
        for u in sorted(usernames):
            print(" -", u)

        import json
        with open("usernames.json", "w", encoding="utf-8") as f:
            json.dump(sorted(usernames), f, indent=2)
        print("💾 Saved to usernames.json")

        browser.close()

if __name__ == "__main__":
    main()
