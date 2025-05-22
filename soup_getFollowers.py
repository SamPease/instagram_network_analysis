from bs4 import BeautifulSoup
import csv

# Function to parse usernames, names, and potential bios from a saved HTML file
def parse_follow_file(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    results = {}

    # Look for all anchor tags that link to Instagram profiles
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://www.instagram.com/") and href.count("/") == 4:
            username = href.split("/")[-2]  # Extract the username
            display_name = ""
            parent_div = a.find_parent("div")
            try:
                parent = a.find_parent()
                # Look for a nearby span with a display name string
                name_span = parent.find_next_sibling("span")
                if name_span and name_span.text.strip() and username not in name_span.text:
                    display_name = name_span.text.strip()
            except Exception:
                pass
            results[username] =display_name

    # Debug: Print total parsed data count
    print(f"Parsed {len(results)} users from {path}")
    return results

# Parse both files
followers = parse_follow_file("followers.html")
followees = parse_follow_file("following.html")

# Find mutuals
mutual_usernames = set(followers.keys()) & set(followees.keys())

# Write mutuals with name and bio to CSV
output_file = "mutuals_from_html.csv"
with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    for username in sorted(mutual_usernames):
        writer.writerow([username])

print(f"✅ Saved {len(mutual_usernames)} mutuals to {output_file}")
