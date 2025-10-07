import random
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

def confirm(prompt="Are you sure? [Y/n]: ", default=True):
    while True:
        choice = input(prompt).strip().lower()
        if choice == '':
            return default
        if choice in ['y', 'yes']:
            return True
        if choice in ['n', 'no']:
            return False
        print("Please respond with 'y' or 'n'.")


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
            break  # success
        except Exception as e:
            print(f"⚠️ Retry {attempt+1} for {target_user}: {e}")
    else:
        raise Exception(f"Failed to load profile after retries: {target_user}")

    usernames = set()
    prev_count = -1
    stable_rounds = 0

    if confirm("Do you want to save Following? [Y/n]: "):
        print("Continuing...")
    else:
        raise Exception("Exiting...")

    modal = page.locator("div[role='dialog']").first

    # Search for usernames
    links = modal.locator("a[href^='/']")
    elements = links.element_handles()

    for handle in elements:
        try:
            href = handle.get_attribute("href")
            if href:
                username = href.strip("/").split("/")[0]
                # if username in mutuals:
                usernames.add(username)
        except:
            continue


    print(f"✅ Found {len(usernames)} usernames {target_user} is following")
    if len(usernames) <=12:
        raise Exception(f"Found too few usernames ({len(usernames)}) for {target_user}. Check the profile or your connection.")
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