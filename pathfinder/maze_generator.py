"""Procedural maze generators: Recursive Backtracking and Randomized Prim's."""
import random
from typing import List


def generate_recursive_backtracking(rows: int, cols: int) -> List[List[int]]:
    """
    Generates a perfect maze using Recursive Backtracking (DFS).
    Works on odd-sized grids. Returns grid where 1=wall, 0=open.
    """
    # Ensure odd dimensions for cell-based maze
    r = rows if rows % 2 == 1 else rows - 1
    c = cols if cols % 2 == 1 else cols - 1

    grid = [[1] * c for _ in range(r)]

    def carve(row, col):
        grid[row][col] = 0
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < r and 0 <= nc < c and grid[nr][nc] == 1:
                grid[row + dr//2][col + dc//2] = 0
                carve(nr, nc)

    import sys
    sys.setrecursionlimit(10000)
    carve(1, 1)

    # Pad to match target dimensions if needed
    if r < rows:
        grid.append([1] * c)
    if c < cols:
        for row in grid:
            row.append(1)

    # Trim/pad to exact size
    result = []
    for i in range(rows):
        if i < len(grid):
            row = grid[i][:cols]
            while len(row) < cols:
                row.append(1)
            result.append(row)
        else:
            result.append([1] * cols)

    return result


def generate_prims(rows: int, cols: int) -> List[List[int]]:
    """
    Generates a maze using Randomized Prim's algorithm.
    Returns grid where 1=wall, 0=open.
    """
    r = rows if rows % 2 == 1 else rows - 1
    c = cols if cols % 2 == 1 else cols - 1

    grid = [[1] * c for _ in range(r)]

    start_r, start_c = 1, 1
    grid[start_r][start_c] = 0

    walls = []
    for dr, dc in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
        nr, nc = start_r + dr, start_c + dc
        if 0 <= nr < r and 0 <= nc < c:
            walls.append((start_r, start_c, nr, nc))

    while walls:
        idx = random.randint(0, len(walls) - 1)
        r1, c1, r2, c2 = walls[idx]
        walls.pop(idx)

        if grid[r2][c2] == 1:
            grid[r2][c2] = 0
            grid[(r1+r2)//2][(c1+c2)//2] = 0

            for dr, dc in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                nr, nc = r2 + dr, c2 + dc
                if 0 <= nr < r and 0 <= nc < c and grid[nr][nc] == 1:
                    walls.append((r2, c2, nr, nc))

    # Fit to target dimensions
    result = []
    for i in range(rows):
        if i < len(grid):
            row = grid[i][:cols]
            while len(row) < cols:
                row.append(1)
            result.append(row)
        else:
            result.append([1] * cols)

    return result
