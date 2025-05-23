import json
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME_LIST_FILE = "usernames.json"
GRAPH_FILE = "mutual_follow_graph.json"
BATCH_SIZE = 10
SLEEP_BETWEEN_REQUESTS = 2  # seconds


def load_json(path):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def scrape_following(page, username, valid_usernames):
    url = f"https://www.instagram.com/{username}/"
    page.goto(url, timeout=60000)
    try:
        page.locator("a[href$='/following/']").click()
        page.wait_for_selector("div[role='dialog']", timeout=10000)  # Wait for the follower box
    except Exception:
        print(f"[!] Could not access following list for {username}")
        return []

    # Updated selector to reliably target scrollable container inside the modal
    page.wait_for_selector("div[role='dialog']", timeout=10000)
    scroll_area = page.locator("div[role='dialog'] div[style*='overflow']")
    if not scroll_area.is_visible():
        print(f"[!] No following list visible for {username}")
        return []  # Use the class to locate the scrollable area
    seen = set()
    retries = 3  # Number of retries for scrolling

    for _ in range(retries):
        prev_count = len(seen)
        while True:
            # Scroll the follower list by evaluating JavaScript to scroll the correct element
            page.evaluate(
                """(scrollArea) => {
                    scrollArea.scrollTop = scrollArea.scrollHeight;
                }""",
                scroll_area,
            )
            time.sleep(1.5)
            handles = scroll_area.locator("a[href*='/']")
            current = handles.evaluate_all("els => els.map(el => el.getAttribute('href').split('/')[1])")
            new_usernames = set(current) - seen
            if not new_usernames:
                break
            seen.update(new_usernames)
            print(f"[DEBUG] Found {len(new_usernames)} new usernames: {new_usernames}")

        # Break out of retry loop if no new usernames are found
        if len(seen) == prev_count:
            break

    print(f"[DEBUG] Total usernames scraped for {username}: {len(seen)}")
    return [user for user in seen if user in valid_usernames and user != username]


def main():
    usernames = load_json(USERNAME_LIST_FILE)
    graph = load_json(GRAPH_FILE)
    remaining = [u for u in usernames if u not in graph]

    print(f"🗂 {len(remaining)} users remaining to process...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        for i in range(0, len(remaining), BATCH_SIZE):
            batch = remaining[i:i + BATCH_SIZE]
            print(f"🔁 Processing batch {i // BATCH_SIZE + 1}: {batch}")
            for username in batch:
                try:
                    follows = scrape_following(page, username, usernames)
                    graph[username] = follows
                    print(f"✅ {username} follows {len(follows)} from the list")
                except Exception as e:
                    print(f"❌ Error with {username}: {e}")
                time.sleep(SLEEP_BETWEEN_REQUESTS)

            save_json(graph, GRAPH_FILE)
            print(f"💾 Progress saved after batch {i // BATCH_SIZE + 1}")

        context.storage_state(path="auth.json")  # Save session
        browser.close()

    print("🎉 All done!")


if __name__ == "__main__":
    main()
