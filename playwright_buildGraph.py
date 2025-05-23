import time
import csv
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

MUTUALS_FILE = "mutuals_from_html.csv"
GRAPH_FILE = "mutual_follow_graph.json"
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

def scrape_following(page, target_user, mutuals):
    page.goto(f"https://www.instagram.com/{target_user}/")
    page.wait_for_selector("a[href$='/following/']")
    page.locator("a[href$='/following/']").first.click()

    page.wait_for_selector("div[role='dialog']", timeout=10000)
    page.wait_for_selector("div[role='dialog'] a[href^='/']", timeout=10000)
    print(f"✅ Dialog opened for {target_user}")

    scroll_area = page.locator("div[role='dialog'] div[class*='xyi19xy'] div[style*='overflow']").first
    modal = page.locator("div[role='dialog']").first
    box = modal.bounding_box()
    x_center = box["x"] + box["width"] / 2
    y_center = box["y"] + box["height"] / 2

    usernames = set()
    prev_count = 0
    same_count_rounds = 0

    while True:
        page.mouse.move(x_center, y_center)
        page.mouse.wheel(0, SCROLL_DELTA)
        time.sleep(SCROLL_DELAY)

        links = scroll_area.locator("a[href^='/']")
        for j in range(links.count()):
            href = links.nth(j).get_attribute("href")
            if (
                href
                and href.startswith("/")
                and not any(x in href for x in ["stories", "reels", "p", "explore", "directory"])
                and href.strip("/").count("/") == 1
            ):
                username = href.strip("/").split("/")[0]
                usernames.add(username)

        if len(usernames) == prev_count:
            same_count_rounds += 1
        else:
            same_count_rounds = 0
        prev_count = len(usernames)

        if same_count_rounds >= STOP_AFTER_UNCHANGED_ROUNDS:
            break

    print(f"✅ Found {len(usernames)} usernames for {target_user}")
    mutual_followings = sorted(list(usernames.intersection(mutuals)))
    print(f"🤝 {target_user} follows {len(mutual_followings)} mutuals")
    return mutual_followings

def main():
    mutuals = set(load_mutuals())
    graph = load_existing_graph()
    users_to_check = [user for user in mutuals if user not in graph]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        for user in users_to_check:
            try:
                print(f"🔍 Checking {user}...")
                mutual_followings = scrape_following(page, user, mutuals)
                graph[user] = mutual_followings
                save_graph(graph)
            except Exception as e:
                print(f"❌ Error with {user}: {e}")
                save_graph(graph)
                break

        browser.close()

if __name__ == "__main__":
    main()
