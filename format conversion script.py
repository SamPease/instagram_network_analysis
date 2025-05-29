import json
import csv

# Load mutual usernames from CSV
with open('mutuals_from_html.csv', newline='', encoding='utf-8') as f:
    mutuals = set(line.strip() for line in f if line.strip())

# Load the full following graph
with open('following_graph.json', 'r', encoding='utf-8') as f:
    following_graph = json.load(f)

# Intersect children with mutuals
mutuals_graph = {
    user: [child for child in children if child in mutuals]
    for user, children in following_graph.items()
}

# Save the mutuals graph
with open('mutuals_graph.json', 'w', encoding='utf-8') as f:
    json.dump(mutuals_graph, f, indent=2)

print("mutuals_graph.json written successfully.")
