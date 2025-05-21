import instaloader
import time
import csv
import os
import pickle

USERNAME = "sampease24"
CHECKPOINT_FILE = "checkpoint.pkl"
OUTPUT_FILE = "mutual_followers.csv"

# Initialize Instaloader
L = instaloader.Instaloader()

# Load session or log in
try:
    L.context.log("Trying to load existing session...")
    L.load_session_from_file(USERNAME)
except FileNotFoundError:
    password = input("Enter your Instagram password: ")  # Prompt for password securely
    L.login(USERNAME, password)
    L.save_session_to_file()

# Load your profile
profile = instaloader.Profile.from_username(L.context, USERNAME)

# Helper to fetch with checkpointing
def fetch_with_checkpoint(generator, label):
    users = {}
    start_index = 0

    # Load checkpoint if it exists
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "rb") as f:
            checkpoint = pickle.load(f)
            users = checkpoint.get(f"{label}_users", {})
            start_index = checkpoint.get(f"{label}_index", 0)
            print(f"[{label}] Resuming from checkpoint at index {start_index} ({len(users)} users loaded)")

    # Fetch new users
    for i, user in enumerate(generator):
        if i < start_index:
            continue  # Skip already processed users

        try:
            users[user.username] = user.biography
        except Exception as e:
            print(f"[{label}] Error fetching user: {e}")
            continue

        if (i + 1) % 10 == 0:
            print(f"[{label}] Fetched {i + 1} users...")
            # Save checkpoint
            with open(CHECKPOINT_FILE, "wb") as f:
                pickle.dump({
                    f"{label}_users": users,
                    f"{label}_index": i + 1
                }, f)

        time.sleep(5)  # Increase sleep to reduce rate-limit risk

    return users

print("Fetching followers...")
followers = fetch_with_checkpoint(profile.get_followers(), "followers")

print("Fetching followees...")
followees = fetch_with_checkpoint(profile.get_followees(), "followees")

# Compute mutuals
mutual_usernames = set(followers.keys()) & set(followees.keys())
mutuals = [(username, followers[username]) for username in mutual_usernames]

# Save to CSV
with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["username", "bio"])
    for i, (username, bio) in enumerate(sorted(mutuals)):  # Sorting can be optional
        writer.writerow([username, bio])
        if (i + 1) % 10 == 0:
            print(f"[save] Saved {i + 1} mutuals...")

print(f"✅ Done! Saved {len(mutuals)} mutual followers to '{OUTPUT_FILE}'")

# Optional: Ask user before deleting checkpoint
if os.path.exists(CHECKPOINT_FILE):
    delete_checkpoint = input("Delete checkpoint file? (y/n): ").strip().lower()
    if delete_checkpoint == 'y':
        os.remove(CHECKPOINT_FILE)
