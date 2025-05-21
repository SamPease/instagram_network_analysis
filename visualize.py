import json
import torch
from torch_geometric.data import Data
from torch_geometric.utils import to_networkx
import networkx as nx
import matplotlib.pyplot as plt

# Load graph from JSON
with open("karate_graph.json") as f:
    adj_dict = json.load(f)

# Map usernames to integer indices
usernames = sorted(adj_dict.keys())
user_to_idx = {user: i for i, user in enumerate(usernames)}
idx_to_user = {i: user for user, i in user_to_idx.items()}

# Create edge list for directed graph
edge_index = []
for user, neighbors in adj_dict.items():
    for neighbor in neighbors:
        edge_index.append([user_to_idx[user], user_to_idx[neighbor]])

edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()

# Optional: dummy node features (identity matrix)
x = torch.eye(len(usernames), dtype=torch.float)

# Build PyG data object
data = Data(x=x, edge_index=edge_index)

# Convert to NetworkX DiGraph
G = to_networkx(data, to_undirected=True)

# Relabel nodes back to usernames for display
G = nx.relabel_nodes(G, idx_to_user)

# Draw directed graph
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray',
        node_size=700, arrows=True, connectionstyle='arc3,rad=0.1')
plt.title("Directed Graph from JSON")
plt.show()
