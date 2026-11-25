"""A* Search with multiple heuristic options."""
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

def astar(grid, start: Tuple[int,int], goal: Tuple[int,int], heuristic: str = 'manhattan') -> Generator:
    h = HEURISTICS.get(heuristic, _manhattan)
    rows, cols = len(grid), len(grid[0])
    g_score = {start: 0}
    parent: Dict[Tuple,Optional[Tuple]] = {start: None}
    counter = 0
    heap = [(h(start, goal), counter, start)]
    open_set = {start}
    closed_set = set()

    while heap:
        f, _, current = heapq.heappop(heap)
        if current in closed_set:
            continue
        open_set.discard(current)
        closed_set.add(current)
        yield ('visit', current)

        if current == goal:
            path = _reconstruct_path(parent, goal)
            yield ('path', path)
            return

        for neighbor, weight in _get_neighbors(current, rows, cols, grid):
            if neighbor in closed_set:
                continue
            tentative_g = g_score[current] + weight
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + h(neighbor, goal)
                counter += 1
                heapq.heappush(heap, (f_score, counter, neighbor))
                open_set.add(neighbor)
                yield ('frontier', neighbor)

    yield ('no_path',)


def astar_benchmark(grid, start, goal, heuristic='manhattan'):
    h = HEURISTICS.get(heuristic, _manhattan)
    rows, cols = len(grid), len(grid[0])
    g_score = {start: 0}
    parent = {start: None}
    counter = 0
    heap = [(h(start, goal), counter, start)]
    open_set = {start}
    closed_set = set()
    nodes_explored = 0
    peak_frontier = 1

    while heap:
        f, _, current = heapq.heappop(heap)
        if current in closed_set:
            continue
        open_set.discard(current)
        closed_set.add(current)
        nodes_explored += 1

        if current == goal:
            path = _reconstruct_path(parent, goal)
            return path, nodes_explored, g_score[goal], peak_frontier

        for neighbor, weight in _get_neighbors(current, rows, cols, grid):
            if neighbor in closed_set:
                continue
            tentative_g = g_score[current] + weight
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + h(neighbor, goal)
                counter += 1
                heapq.heappush(heap, (f_score, counter, neighbor))
                open_set.add(neighbor)
                peak_frontier = max(peak_frontier, len(heap))

    return None, nodes_explored, 0, peak_frontier


def _get_neighbors(node, rows, cols, grid):
    r, c = node
    WEIGHTS = {0: 1, 2: 5, 3: 10}
    neighbors = []
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
