# Instagram Network Analysis

This project explores the structure of my Instagram mutual-follow network using tools from web scraping, network science, and machine learning. I scraped mutual connections, built a social graph, and used graph neural networks (GNNs) to model social patterns and predict missing links.

<img width="1705" alt="Screenshot 2025-06-10 at 4 24 39 PM" src="https://github.com/user-attachments/assets/611b5fc3-b156-45b4-9cd0-9905592ccc2f" />

## Overview

- **Data Collection**: Using Playwright, I scraped all users I both follow and am followed by. Then, I gathered each mutual’s following list and filtered it to users already in the mutual set.
- **Graph Construction**: Built a directed graph from this data using NetworkX and PyVis for visualization.
- **Network Analysis**: Computed global and local metrics including centrality, clustering coefficient, and modularity (via Louvain community detection).
- **Graph Machine Learning**: Used PyTorch Geometric to train simple GNNs on the graph to predict connections and explore embeddings.
- **Visualization**: Created an interactive PyVis network that highlights structural features and community groupings.

## Technical Highlights

- GNNs implemented with PyTorch Geometric
- Louvain clustering and centrality measures
- Fully automated web scraping pipeline with Playwright
- Interactive network rendered with PyVis
- Clean separation of scraping, analysis, and modeling logic in Jupyter notebooks

## Notebook

All analysis can be found in [`graph_vis3.ipynb`](https://github.com/SamPease/instagram_network_analysis/blob/master/graph_vis3.ipynb)

## Blog Post

A full write-up of this project, with visuals and explanations, is available here:  
👉 [Blog: Instagram Network Analysis](https://sampease.github.io/instagram-network.html)

## Inspiration

This project was originally inspired by [this Medium post](https://medium.com/@maximpiessen/how-i-visualised-my-instagram-network-and-what-i-learned-from-it-d7cc125ef297), but the codebase is entirely my own.

## Disclaimer

This project was done for educational purposes. Please respect Instagram’s terms of service.
