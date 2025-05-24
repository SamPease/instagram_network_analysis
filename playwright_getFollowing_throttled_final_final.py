import random
import time
import asyncio

def random_throttle_sync(min_sec=2, max_sec=6):
    delay = random.uniform(min_sec, max_sec)
    print(f"Throttling for {delay:.2f} seconds")
    time.sleep(delay)

async def handle_try_again_popup(page):
    try:
        popup = await page.wait_for_selector('text=Try Again Later', timeout=3000)
        if popup:
            print("Detected 'Try Again Later' popup")
            ok_button = await page.query_selector('text=OK')
            if ok_button:
                await ok_button.click()
                print("Clicked OK on rate limit popup. Backing off.")
                await asyncio.sleep(600)  # 10 minutes
                return True
    except:
        pass
    return False


import time
import csv
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from tqdm import tqdm

MUTUALS_FILE = "mutuals_from_html.csv"
GRAPH_FILE = "following_graph.json"
SCROLL_DELAY = 2.5
SCROLL_DELTA = 600
STOP_AFTER_UNCHANGED_ROUNDS = 10

def load_mutuals():
    with open(MUTUALS_FILE, newline='', encoding='utf-8') as f:
        return [row[0].strip() for row in csv.reader(f) if row]

def load_existing_graph():
    if Path(GRAPH_FILE).exists():
        with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_graph(graph):
    with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)

def scrape_following(page, target_user):
    # Go to target user profile
    for attempt in range(3):
        try:
            page.goto(f"https://www.instagram.com/{target_user}/", timeout=15000)
            random_throttle_sync()  # Add throttle after navigating to the profile
            break  # success
        except Exception as e:
            print(f"⚠️ Retry {attempt+1} for {target_user}: {e}")
            time.sleep(5)
    else:
        raise Exception(f"Failed to load profile after retries: {target_user}")


    page.wait_for_selector("a[href$='/following/']")
    page.locator("a[href$='/following/']").first.click()
    random_throttle_sync()  # Add throttle after clicking the "following" link

    # Check for "Try Again Later" popup
    if asyncio.run(handle_try_again_popup(page)):
        print("Sleeping for 10 minutes due to rate limit...")
        time.sleep(600)  # Sleep for 10 minutes

    # Wait for dialog and initial user content
    page.wait_for_selector("div[role='dialog']", timeout=10000)
    page.wait_for_selector("div[role='dialog'] a[href^='/']", timeout=10000)
    print("✅ Dialog opened and list loaded")

    # Locate scrollable content container for username extraction
    modal = page.locator("div[role='dialog']").first
    scroll_area = modal.locator("div[style*='overflow']").first

    usernames = set()
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
        random_throttle_sync()  # Add throttle between scrolls

        # Search for usernames
        links = modal.locator("a[href^='/']")
        elements = links.element_handles()

        for handle in elements:
            try:
                href = handle.get_attribute("href")
                if href:
                    username = href.strip("/").split("/")[0]
                    usernames.add(username)
            except:
                continue

        if len(usernames) == prev_count:
            stable_rounds += 1
        else:
            stable_rounds = 0
            prev_count = len(usernames)

    print(f"✅ Found {len(usernames)} usernames {target_user} is following")
    return(sorted(usernames))

def main():
    mutuals = set(load_mutuals())
    graph = load_existing_graph()
    users_to_check = [user for user in mutuals if user not in graph]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        for user in tqdm(users_to_check):
            try:
                print(f"🔍 Checking {user}...")
                mutual_followings = scrape_following(page, user)
                graph[user] = mutual_followings
                save_graph(graph)
            except Exception as e:
                print(f"❌ Error with {user}: {e}")
                save_graph(graph)
                break

        browser.close()

if __name__ == "__main__":
    main()
