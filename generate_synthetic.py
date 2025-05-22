import json
import networkx as nx  # Added missing import
from torch_geometric.datasets import KarateClub
from torch_geometric.utils import to_networkx
from torch_geometric.datasets import WikipediaNetwork  # Import WikipediaNetwork dataset

# Load KarateClub dataset
# dataset = KarateClub()
# data = dataset[0]

# # Convert to NetworkX graph for easy traversal
# G = to_networkx(data, to_undirected=True)

# # Optional: create fake usernames
# node_mapping = {i: f"user{i}" for i in G.nodes}
# G = nx.relabel_nodes(G, node_mapping)

# # Build adjacency list with sorted keys for consistency
# adj_list = {user: list(neighbors) for user, neighbors in G.adjacency()}
# adj_list = dict(sorted(adj_list.items()))  # Ensure keys are sorted

# # Save to JSON
# with open("karate_graph.json", "w") as f:
#     json.dump(adj_list, f, indent=2)

# print("✅ Saved karate_graph.json")

# Load Wikipedia Chameleon dataset
dataset = WikipediaNetwork(root='/tmp/Wikipedia', name='chameleon')
data = dataset[0]

breakpoint()

# Convert to NetworkX graph for easy traversal
G = to_networkx(data, to_undirected=True)

# Optional: create fake usernames
node_mapping = {i: f"user{i}" for i in G.nodes}
G = nx.relabel_nodes(G, node_mapping)

# Build adjacency list with sorted keys for consistency
adj_list = {user: list(neighbors) for user, neighbors in G.adjacency()}
adj_list = dict(sorted(adj_list.items()))  # Ensure keys are sorted

# Save to JSON
with open("chameleon_graph.json", "w") as f:
    json.dump(adj_list, f, indent=2)

print("✅ Saved chameleon_graph.json")
