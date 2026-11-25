# 🧭 Interactive Pathfinding Visualizer & Algorithm Benchmark Suite

A desktop simulation tool built with **Python + Pygame** that visualises and benchmarks classical graph search and pathfinding algorithms on an interactive 2D grid.

## ▶️ How to Run

```bash
cd ai_project
python main.py
```

---

## 🗂️ Project Structure

```
ai_project/
├── main.py                        # Entry point — Pygame GUI
├── pathfinder/
│   ├── __init__.py
│   ├── benchmark.py               # Benchmarking engine + CSV export
│   ├── maze_generator.py          # Recursive Backtracking & Prim's maze
│   ├── charts.py                  # Matplotlib chart renderer
│   └── algorithms/
│       ├── __init__.py
│       ├── bfs.py                 # Breadth-First Search
│       ├── dfs.py                 # Depth-First Search
│       ├── dijkstra.py            # Dijkstra's Algorithm (weighted)
│       ├── astar.py               # A* Search (3 heuristics)
│       └── greedy.py              # Greedy Best-First Search
├── benchmark_results.csv          # (auto-generated after benchmark)
├── benchmark_chart.png            # (auto-generated after chart export)
└── grid_snapshot.png              # (auto-generated after image save)
```

---

## 🎮 Controls

| Action | Control |
|--------|---------|
| Run selected algorithm | `Space` or **▶ Run** button |
| Pause / Resume animation | `Space` while running |
| Step one frame | `→` arrow key or **⏭ Step** button |
| Clear path only | `R` key |
| Clear entire grid | `C` key |
| Run benchmark suite | `B` key or **⚡ Benchmark** button |
| Draw walls | Click/drag on grid (Wall mode) |
| Erase | Click/drag (Erase mode) |
| Place Start/Goal | Click in Start / Goal mode |

---

## 🧠 Algorithms

| Algorithm | Optimal? | Weighted? | Heuristic |
|-----------|----------|-----------|-----------|
| BFS | ✅ (unweighted) | ❌ | None |
| DFS | ❌ | ❌ | None |
| Dijkstra | ✅ | ✅ | None |
| A\* (Manhattan) | ✅ | ✅ | Manhattan |
| A\* (Euclidean) | ✅ | ✅ | Euclidean |
| Greedy | ❌ | ❌ | Manhattan |

---

## 🗺️ Terrain Types

| Colour | Type | Move Cost |
|--------|------|-----------|
| Dark | Empty | 1 |
| Black | Wall | Impassable |
| Brown | Mud | 5 |
| Blue | Water | 10 |
| Green | Start | — |
| Red | Goal | — |

---

## 📊 Benchmarking

Click **⚡ Benchmark** to run all 6 algorithm variants on the current grid simultaneously. Results appear in an overlay table showing:
- **Nodes Explored** — search space efficiency
- **Execution Time (ms)** — CPU speed
- **Path Length / Cost** — trajectory optimality
- **Peak Frontier** — memory footprint

Click **📊 Show Charts** to open a matplotlib comparison window and auto-save `benchmark_chart.png`.  
Click **💾 Export CSV** to save `benchmark_results.csv`.

---

## 🌀 Maze Generation

| Button | Algorithm | Property |
|--------|-----------|----------|
| Maze (DFS) | Recursive Backtracking | Long winding corridors |
| Maze (Prim) | Randomised Prim's | Many short dead ends |

---

## 📸 Export

| Output | Description |
|--------|-------------|
| `grid_snapshot.png` | Screenshot of the current grid |
| `benchmark_results.csv` | Performance metrics for all algorithms |
| `benchmark_chart.png` | Bar chart comparison image |
