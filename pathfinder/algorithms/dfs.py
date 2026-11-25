"""Depth-First Search algorithm."""
from typing import Generator, Dict, Tuple, List, Optional

def dfs(grid, start: Tuple[int,int], goal: Tuple[int,int]) -> Generator:
    rows, cols = len(grid), len(grid[0])
    stack = [start]
    visited = set()
    parent: Dict[Tuple,Optional[Tuple]] = {start: None}

    while stack:
        current = stack.pop()
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
                stack.append(neighbor)
                yield ('frontier', neighbor)

    yield ('no_path',)


def dfs_benchmark(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    stack = [start]
    visited = set()
    parent = {start: None}
    nodes_explored = 0
    peak_frontier = 1

    while stack:
        current = stack.pop()
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
                stack.append(neighbor)
                peak_frontier = max(peak_frontier, len(stack))
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
