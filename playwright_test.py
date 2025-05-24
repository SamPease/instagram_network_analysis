
import time
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright

TARGET_USER = "roux.blue.stagram"  # Replace with the target username

def main():
    following = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        # Navigate to user's profile
        page.goto(f"https://www.instagram.com/{TARGET_USER}/")
        page.wait_for_selector("a[href$='/following/']")
        page.locator("a[href$='/following/']").first.click()

        # Wait for modal
        page.wait_for_selector("div[role='dialog']", timeout=10000)
        print("✅ Dialog opened")

        modal = page.locator("div[role='dialog']").first
        scroll_area = modal.locator("div[style*='overflow']").first

        prev_count = -1
        stable_rounds = 0

        print("⏳ Scrolling and checking for following...")
        while stable_rounds < 3:
            # Scroll the modal
            box = modal.bounding_box()
            x_center = box["x"] + box["width"] / 2
            y_center = box["y"] + box["height"] / 2
            page.mouse.move(x_center, y_center)
            page.mouse.wheel(0, 600)
            time.sleep(2.5)

            # Search for usernames
            links = modal.locator("a[href^='/']")
            elements = links.element_handles()

            for handle in elements:
                try:
                    href = handle.get_attribute("href")
                    if href:
                        username = href.strip("/").split("/")[0]
                        # if username in mutuals:
                        following.add(username)
                except:
                    continue

            if len(following) == prev_count:
                stable_rounds += 1
            else:
                stable_rounds = 0
                prev_count = len(following)

        print(f"✅ Found {len(following)} usernames {TARGET_USER} is following")
        print(sorted(following))

        with open(f"{TARGET_USER}_mutuals_found.txt", "w") as f:
            for u in sorted(following):
                f.write(u + "\n")

if __name__ == "__main__":
    main()
