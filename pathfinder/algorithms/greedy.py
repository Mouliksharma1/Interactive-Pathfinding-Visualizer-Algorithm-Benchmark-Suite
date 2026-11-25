"""Greedy Best-First Search algorithm."""
import heapq
import math
from typing import Generator, Dict, Tuple, Optional

def _manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _euclidean(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def _chebyshev(a, b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

HEURISTICS = {
    'manhattan': _manhattan,
    'euclidean': _euclidean,
    'chebyshev': _chebyshev,
}

def greedy(grid, start: Tuple[int,int], goal: Tuple[int,int], heuristic: str = 'manhattan') -> Generator:
    h = HEURISTICS.get(heuristic, _manhattan)
    rows, cols = len(grid), len(grid[0])
    counter = 0
    heap = [(h(start, goal), counter, start)]
    visited = set()
    parent: Dict[Tuple,Optional[Tuple]] = {start: None}

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        yield ('visit', current)

        if current == goal:
            path = _reconstruct_path(parent, goal)
            yield ('path', path)
            return

        for neighbor in _get_neighbors(current, rows, cols, grid):
            if neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = current
                counter += 1
                heapq.heappush(heap, (h(neighbor, goal), counter, neighbor))
                yield ('frontier', neighbor)

    yield ('no_path',)


def greedy_benchmark(grid, start, goal, heuristic='manhattan'):
    h = HEURISTICS.get(heuristic, _manhattan)
    rows, cols = len(grid), len(grid[0])
    counter = 0
    heap = [(h(start, goal), counter, start)]
    visited = set()
    parent = {start: None}
    nodes_explored = 0
    peak_frontier = 1

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1
        if current == goal:
            path = _reconstruct_path(parent, goal)
            return path, nodes_explored, len(path) - 1, peak_frontier
        for neighbor in _get_neighbors(current, rows, cols, grid):
            if neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = current
                counter += 1
                heapq.heappush(heap, (h(neighbor, goal), counter, neighbor))
                peak_frontier = max(peak_frontier, len(heap))
    return None, nodes_explored, 0, peak_frontier


def _get_neighbors(node, rows, cols, grid):
    r, c = node
    neighbors = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
            neighbors.append((nr, nc))
    return neighbors


def _reconstruct_path(parent, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
