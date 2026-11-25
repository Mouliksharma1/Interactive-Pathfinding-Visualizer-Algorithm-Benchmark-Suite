"""Breadth-First Search algorithm."""
from collections import deque
from typing import Generator, Dict, Tuple, List, Optional

def bfs(grid, start: Tuple[int,int], goal: Tuple[int,int]) -> Generator:
    """
    Yields steps: ('visit', node), ('frontier', node), ('path', path_list) or ('no_path',)
    """
    rows, cols = len(grid), len(grid[0])
    queue = deque([start])
    visited = {start}
    parent: Dict[Tuple,Optional[Tuple]] = {start: None}
    frontier_set = {start}

    while queue:
        current = queue.popleft()
        frontier_set.discard(current)
        yield ('visit', current)

        if current == goal:
            path = _reconstruct_path(parent, goal)
            yield ('path', path)
            return

        for neighbor in _get_neighbors(current, rows, cols, grid):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                frontier_set.add(neighbor)
                yield ('frontier', neighbor)

    yield ('no_path',)


def bfs_benchmark(grid, start, goal):
    """Returns (path, nodes_explored, path_length) without yielding."""
    rows, cols = len(grid), len(grid[0])
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    nodes_explored = 0
    peak_frontier = 1

    while queue:
        current = queue.popleft()
        nodes_explored += 1
        if current == goal:
            path = _reconstruct_path(parent, goal)
            return path, nodes_explored, len(path) - 1, peak_frontier
        for neighbor in _get_neighbors(current, rows, cols, grid):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                peak_frontier = max(peak_frontier, len(queue))
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
