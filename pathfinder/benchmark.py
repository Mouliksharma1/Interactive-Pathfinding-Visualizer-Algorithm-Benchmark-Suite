"""Benchmarking engine: runs all algorithms and collects metrics."""
import time
import csv
from typing import List, Dict, Any, Optional, Tuple

from pathfinder.algorithms.bfs import bfs_benchmark
from pathfinder.algorithms.dfs import dfs_benchmark
from pathfinder.algorithms.dijkstra import dijkstra_benchmark
from pathfinder.algorithms.astar import astar_benchmark
from pathfinder.algorithms.greedy import greedy_benchmark


ALGORITHMS = {
    'BFS': bfs_benchmark,
    'DFS': dfs_benchmark,
    'Dijkstra': dijkstra_benchmark,
    'A* (Manhattan)': lambda g, s, e: astar_benchmark(g, s, e, 'manhattan'),
    'A* (Euclidean)': lambda g, s, e: astar_benchmark(g, s, e, 'euclidean'),
    'Greedy (Manhattan)': lambda g, s, e: greedy_benchmark(g, s, e, 'manhattan'),
}


def run_benchmark(grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int]) -> List[Dict[str, Any]]:
    """
    Runs all algorithms on the same grid and returns a list of result dicts.
    Each dict has: name, path_found, path_length, nodes_explored, exec_time_ms, peak_frontier
    """
    results = []
    for name, fn in ALGORITHMS.items():
        t0 = time.perf_counter()
        path, nodes, path_cost, peak_frontier = fn(grid, start, goal)
        t1 = time.perf_counter()
        exec_ms = round((t1 - t0) * 1000, 4)
        results.append({
            'name': name,
            'path_found': path is not None,
            'path_length': path_cost if path else 0,
            'nodes_explored': nodes,
            'exec_time_ms': exec_ms,
            'peak_frontier': peak_frontier,
        })
    return results


def export_to_csv(results: List[Dict[str, Any]], filepath: str):
    """Exports benchmark results to a CSV file."""
    if not results:
        return
    fieldnames = ['name', 'path_found', 'path_length', 'nodes_explored', 'exec_time_ms', 'peak_frontier']
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
