# Instagram Network Analysis

This project explores the structure of my Instagram mutual-follow network using tools from web scraping, network science, and machine learning. I scraped mutual connections, built a social graph, and used graph neural networks (GNNs) to model social patterns and predict missing links.

<img width="1705" alt="Screenshot 2025-06-10 at 4 24 39 PM" src="https://github.com/user-attachments/assets/611b5fc3-b156-45b4-9cd0-9905592ccc2f" />

## Overview

- **Data Collection**: Using Playwright, I scraped all users I both follow and am followed by. Then, I gathered each mutual’s following list and filtered it to users already in the mutual set.
- **Graph Construction**: Built a directed graph from this data using NetworkX and PyVis for visualization.
- **Network Analysis**: Computed global and local metrics including centrality, clustering coefficient, and modularity (via Louvain community detection).
- **Graph Machine Learning**: Used PyTorch Geometric to train simple GNNs on the graph to predict connections and explore embeddings.
- **Visualization**: Created an interactive PyVis network that highlights structural features and community groupings.

## Reproducible files (minimal set)

The repository currently contains the minimal files you need to reproduce the final analysis in these exact locations:

- `playwright_saveLogin.py` — Run this first to create a saved session (`auth.json`). Location: `/playwright_saveLogin.py` (repo root).
- `playwright_getMutuals.py` — Main data collection script: reads a CSV of mutuals and writes a graph JSON. Location: `/playwright_getMutuals.py` (repo root).
- `csvs/mutuals.csv` — Input CSV listing the mutual accounts to inspect. Location: `/csvs/mutuals.csv`.
- `graphs/mutuals_graph.json` — Output graph JSON produced by `playwright_getMutuals.py`. Location: `/graphs/mutuals_graph.json`.
- `analysis.ipynb` — Notebook that loads the graph JSON, runs analysis, and writes the interactive HTML visualization (this used to be `graph_vis3.ipynb`). Location: `/analysis.ipynb` (repo root).
- `requirements.txt` — Python dependencies used to reproduce the environment. Location: `/requirements.txt` (repo root).
- `auth.json` — Saved session/login file created by `playwright_saveLogin.py`. If present, location: `/auth.json` (repo root). Treat it as a secret; add it to `.gitignore` or move it to `secrets/` if you plan to commit the repo.

If you've archived exploratory files into `archive/`, that's fine — just make sure the scripts above remain at these locations or update `analysis.ipynb` to point at the new paths.

### Quick run-order (zsh)

Run these from the repo root (paths are exact as listed above):

```bash
# 1) create and activate a venv and install requirements
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) save login/session (creates auth.json)
python3 playwright_saveLogin.py

# 3) create graph JSON from mutuals CSV
python3 playwright_getMutuals.py csvs/mutuals.csv --output graphs/mutuals_graph.json

# 4) open `analysis.ipynb` and run the cells that load `graphs/mutuals_graph.json`
```

Notes
- If `analysis.ipynb` includes hard-coded relative paths, open it and update them to the exact paths above.
- Add `auth.json`, `csvs/large_scrapes/`, and `archive/` to `.gitignore` if you don't want to track them in git.

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
[Blog: Instagram Network Analysis](https://sampease.github.io/project-writeups/instagram-network/)

## Inspiration

This project was originally inspired by [this Medium post](https://medium.com/@maximpiessen/how-i-visualised-my-instagram-network-and-what-i-learned-from-it-d7cc125ef297), but the codebase is entirely my own.

## Disclaimer

This project was done for educational purposes. Please respect Instagram’s terms of service.
