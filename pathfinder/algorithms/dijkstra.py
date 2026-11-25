"""Dijkstra's Algorithm with weighted terrain support."""
import heapq
from typing import Generator, Dict, Tuple, Optional

def dijkstra(grid, start: Tuple[int,int], goal: Tuple[int,int]) -> Generator:
    rows, cols = len(grid), len(grid[0])
    dist = {start: 0}
    parent: Dict[Tuple,Optional[Tuple]] = {start: None}
    heap = [(0, start)]
    visited = set()

    while heap:
        cost, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        yield ('visit', current)

        if current == goal:
            path = _reconstruct_path(parent, goal)
            yield ('path', path)
            return

        for neighbor, weight in _get_neighbors(current, rows, cols, grid):
            new_cost = cost + weight
            if neighbor not in dist or new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                parent[neighbor] = current
                heapq.heappush(heap, (new_cost, neighbor))
                yield ('frontier', neighbor)

    yield ('no_path',)


def dijkstra_benchmark(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    dist = {start: 0}
    parent = {start: None}
    heap = [(0, start)]
    visited = set()
    nodes_explored = 0
    peak_frontier = 1

    while heap:
        cost, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1
        if current == goal:
            path = _reconstruct_path(parent, goal)
            total_cost = dist[goal]
            return path, nodes_explored, total_cost, peak_frontier
        for neighbor, weight in _get_neighbors(current, rows, cols, grid):
            new_cost = cost + weight
            if neighbor not in dist or new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                parent[neighbor] = current
                heapq.heappush(heap, (new_cost, neighbor))
                peak_frontier = max(peak_frontier, len(heap))
    return None, nodes_explored, 0, peak_frontier


def _get_neighbors(node, rows, cols, grid):
    r, c = node
    neighbors = []
    # Terrain weights: 0=free(1), 1=wall, 2=mud(5), 3=water(10)
    WEIGHTS = {0: 1, 2: 5, 3: 10}
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
            w = WEIGHTS.get(grid[nr][nc], 1)
            neighbors.append(((nr, nc), w))
    return neighbors


def _reconstruct_path(parent, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
