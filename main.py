"""
Pathfinding Visualizer — Simple Edition
Run: python main.py
"""

import pygame
import sys
import os
import time
import threading

from pathfinder.algorithms.bfs      import bfs,      bfs_benchmark
from pathfinder.algorithms.dfs      import dfs,      dfs_benchmark

from pathfinder.algorithms.astar    import astar,    astar_benchmark
from pathfinder.algorithms.greedy   import greedy,   greedy_benchmark
from pathfinder.maze_generator      import generate_recursive_backtracking, generate_prims
from pathfinder.benchmark           import run_benchmark, export_to_csv

# ── Window & Grid ─────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1100, 680
SIDE_W       = 220          # right panel
GRID_W       = WIN_W - SIDE_W
CELL         = 22
COLS         = GRID_W  // CELL
ROWS         = WIN_H   // CELL
FPS          = 60

# ── Cell types ────────────────────────────────────────────────────────────────
EMPTY, WALL, START, GOAL = 0, 1, 4, 5
VISITED, FRONTIER, PATH  = 6, 7, 8

COLORS = {
    EMPTY:    (28, 28, 45),
    WALL:     (15, 15, 25),
    START:    (0,  220, 110),
    GOAL:     (255,  55,  75),
    VISITED:  (50,  90, 170),
    FRONTIER: (90, 190, 230),
    PATH:     (255, 210,  40),
}

ALGO_LIST = [
    ("BFS",    bfs,   bfs_benchmark,                                          {}),
    ("DFS",    dfs,   dfs_benchmark,                                          {}),
    ("A*",     astar, lambda g,s,e: astar_benchmark(g,s,e,'manhattan'),       {'heuristic':'manhattan'}),
    ("Greedy", greedy,lambda g,s,e: greedy_benchmark(g,s,e,'manhattan'),      {'heuristic':'manhattan'}),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def txt(surf, text, x, y, font, color=(210, 215, 255), cx=False):
    s = font.render(text, True, color)
    if cx:
        x -= s.get_width() // 2
    surf.blit(s, (x, y))

def rr(surf, color, rect, r=7, bw=0, bc=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if bw and bc:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=r)


# ── Button ────────────────────────────────────────────────────────────────────

class Btn:
    def __init__(self, rect, label, base=(55,55,95), hover=(80,80,140), active_col=(60,160,80), font=None):
        self.rect   = pygame.Rect(rect)
        self.label  = label
        self.base   = base
        self.hover  = hover
        self.active_col = active_col
        self.font   = font
        self.on     = False   # toggled state
        self._hov   = False

    def draw(self, surf):
        col = self.active_col if self.on else (self.hover if self._hov else self.base)
        rr(surf, col, self.rect, 7, 1, (100,100,160))
        if self.font:
            lbl = self.font.render(self.label, True, (230,235,255))
            surf.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                            self.rect.centery - lbl.get_height()//2))

    def update(self, pos):
        self._hov = self.rect.collidepoint(pos)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Slider ────────────────────────────────────────────────────────────────────

class Slider:
    def __init__(self, x, y, w, lo, hi, val, label, font):
        self.rect  = pygame.Rect(x, y, w, 10)
        self.lo, self.hi = lo, hi
        self.val   = val
        self.label = label
        self.font  = font
        self._drag = False

    @property
    def norm(self): return (self.val - self.lo) / (self.hi - self.lo)

    def draw(self, surf):
        pygame.draw.rect(surf, (45,45,70), self.rect, border_radius=5)
        fw = int(self.norm * self.rect.w)
        pygame.draw.rect(surf, (70,130,210), (*self.rect.topleft, fw, self.rect.h), border_radius=5)
        tx = self.rect.x + fw
        pygame.draw.circle(surf, (200,220,255), (tx, self.rect.centery), 8)
        lbl = self.font.render(f'{self.label}  {self.val}', True, (160,170,210))
        surf.blit(lbl, (self.rect.x, self.rect.y - 17))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(0, 20).collidepoint(event.pos): self._drag = True
        if event.type == pygame.MOUSEBUTTONUP:   self._drag = False
        if event.type == pygame.MOUSEMOTION and self._drag:
            r = max(0.0, min(1.0, (event.pos[0]-self.rect.x)/self.rect.w))
            self.val = int(self.lo + r*(self.hi-self.lo))


# ── App ───────────────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pathfinding Visualizer")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock  = pygame.time.Clock()

        self.f16 = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.f13 = pygame.font.SysFont("Segoe UI", 13)
        self.f11 = pygame.font.SysFont("Segoe UI", 11)

        # Grid data
        self.cells   = [[EMPTY]*COLS for _ in range(ROWS)]
        self.display = [[EMPTY]*COLS for _ in range(ROWS)]
        self.start   = None
        self.goal    = None

        # Animation state
        self.gen        = None
        self.animating  = False
        self.paused     = False
        self.status     = "Auto-generated maze — press SPACE to run!"
        self.scol       = (140, 200, 255)
        self.bench_res  = []
        self.show_bench = False

        # Build UI
        self.algo_idx = 2   # A* default
        self._build_panel()

        # Auto-generate maze on start
        self._gen_maze('dfs')

    # ── Panel ─────────────────────────────────────────────────────────────────

    def _build_panel(self):
        px, bw, bh = GRID_W + 10, SIDE_W - 20, 30

        # Algo buttons (mutually exclusive)
        self.algo_btns = []
        for i, (name, *_) in enumerate(ALGO_LIST):
            b = Btn((px, 55 + i*36, bw, bh), name, font=self.f13)
            self.algo_btns.append(b)
        self.algo_btns[self.algo_idx].on = True

        # Speed slider
        self.speed = Slider(px, 265, bw, 1, 100, 25, "Speed", self.f11)

        # Action buttons — just the essentials
        actions = [
            ("▶  Run / Pause",   "run",        (30,110,70),  (45,160,100)),
            ("↺  New Maze",       "maze",       (30, 70,120), (45,110,170)),
            ("⚡  Benchmark",     "bench",      (90, 40,120), (140, 65,180)),
            ("💾  Export CSV",    "csv",        (40, 80, 80), (60,125,125)),
            ("📸  Save Image",    "img",        (55, 55,100), (85, 85,150)),
            ("🗑  Clear",         "clear",      (110,35, 35), (165, 55, 55)),
        ]
        self.act = {}
        for i, (label, key, base, hov) in enumerate(actions):
            b = Btn((px, 300 + i*40, bw, bh), label, base=base, hover=hov, font=self.f13)
            self.act[key] = b

        # Draw-mode toggle (only wall / erase needed — no terrain clutter)
        self.mode       = "wall"   # "wall" | "erase" | "start" | "goal"
        mode_defs = [("Wall","wall",(50,50,80)), ("Erase","erase",(80,50,50)),
                     ("Start","start",(20,110,60)), ("Goal","goal",(130,30,40))]
        self.mode_btns = []
        half = (bw-4)//2
        for i, (lbl, m, col) in enumerate(mode_defs):
            r, c = i//2, i%2
            b = Btn((px + c*(half+4), 560 + r*36, half, 26), lbl,
                    base=col, hover=tuple(min(v+40,255) for v in col), font=self.f11)
            b._mode = m
            self.mode_btns.append(b)
        self.mode_btns[0].on = True

    # ── Grid helpers ──────────────────────────────────────────────────────────

    def _reset_display(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.display[r][c] = self.cells[r][c]
        if self.start: self.display[self.start[0]][self.start[1]] = START
        if self.goal:  self.display[self.goal[0]] [self.goal[1]]  = GOAL

    def _clear_path(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.display[r][c] in (VISITED, FRONTIER, PATH):
                    self.display[r][c] = self.cells[r][c]
        self._reset_display()

    def _clear_all(self):
        self.cells   = [[EMPTY]*COLS for _ in range(ROWS)]
        self.display = [[EMPTY]*COLS for _ in range(ROWS)]
        self.start = self.goal = None
        self.gen = None; self.animating = False
        self.show_bench = False
        self.status = "Grid cleared."; self.scol = (200,200,255)

    def _raw(self):
        """Grid for algorithms (walls only, no overlay states)."""
        raw = []
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                v = self.cells[r][c]
                row.append(WALL if v == WALL else EMPTY)
            raw.append(row)
        return raw

    def _cell_at(self, mx, my):
        if mx < 0 or mx >= GRID_W or my < 0 or my >= WIN_H:
            return None, None
        c, r = mx//CELL, my//CELL
        if 0 <= r < ROWS and 0 <= c < COLS:
            return r, c
        return None, None

    def _paint(self, r, c):
        if r is None: return
        if self.mode == "wall":
            if (r,c) == self.start or (r,c) == self.goal: return
            self.cells[r][c]   = WALL
            self.display[r][c] = WALL
        elif self.mode == "erase":
            self.cells[r][c]   = EMPTY
            self.display[r][c] = EMPTY
            if self.start == (r,c): self.start = None
            if self.goal  == (r,c): self.goal  = None
        elif self.mode == "start":
            if self.start:
                sr,sc = self.start
                self.display[sr][sc] = self.cells[sr][sc]
            self.start = (r,c); self.cells[r][c] = EMPTY; self.display[r][c] = START
        elif self.mode == "goal":
            if self.goal:
                gr,gc = self.goal
                self.display[gr][gc] = self.cells[gr][gc]
            self.goal = (r,c); self.cells[r][c] = EMPTY; self.display[r][c] = GOAL

    # ── Maze ──────────────────────────────────────────────────────────────────

    def _gen_maze(self, kind='dfs'):
        maze = (generate_recursive_backtracking(ROWS, COLS)
                if kind == 'dfs' else generate_prims(ROWS, COLS))
        for r in range(ROWS):
            for c in range(COLS):
                self.cells[r][c] = maze[r][c] if r < len(maze) and c < len(maze[0]) else WALL

        # Place start top-left open cell, goal bottom-right open cell
        self.start = self._first_open(from_top=True)
        self.goal  = self._first_open(from_top=False)
        self._reset_display()
        self.gen = None; self.animating = False
        import random
        kind_name = "Backtracking" if kind == 'dfs' else "Prim's"
        self.status = f"New maze ({kind_name}) — Space to run!"; self.scol = (100,210,255)

    def _first_open(self, from_top=True):
        rng = range(ROWS) if from_top else range(ROWS-1, -1, -1)
        crng = range(COLS) if from_top else range(COLS-1, -1, -1)
        for r in rng:
            for c in crng:
                if self.cells[r][c] == EMPTY:
                    return (r, c)
        return (1, 1)

    # ── Algorithm animation ───────────────────────────────────────────────────

    def _start_algo(self):
        if not self.start or not self.goal:
            self.status = "Place Start & Goal first!"; self.scol = (255,100,100); return
        self._clear_path()
        raw = self._raw()
        _, fn, _, kw = ALGO_LIST[self.algo_idx]
        self.gen = fn(raw, self.start, self.goal, **kw)
        self.animating = True; self.paused = False
        self.status = f"Running {ALGO_LIST[self.algo_idx][0]}…"; self.scol = (100,220,255)

    def _advance(self, n=1):
        for _ in range(n):
            if not self.gen: return
            try:
                step = next(self.gen)
                self._apply(step)
            except StopIteration:
                self.animating = False; self.gen = None; return

    def _apply(self, step):
        kind = step[0]
        if kind == 'visit':
            r,c = step[1]
            if self.display[r][c] not in (START,GOAL): self.display[r][c] = VISITED
        elif kind == 'frontier':
            r,c = step[1]
            if self.display[r][c] not in (START,GOAL,VISITED): self.display[r][c] = FRONTIER
        elif kind == 'path':
            self._clear_path()
            for r,c in step[1]:
                if self.display[r][c] not in (START,GOAL): self.display[r][c] = PATH
            self.status = f"Done! Path length = {len(step[1])-1}"; self.scol = (80,255,140)
            self.animating = False
        elif kind == 'no_path':
            self.status = "No path found!"; self.scol = (255,80,80); self.animating = False

    # ── Benchmark ─────────────────────────────────────────────────────────────

    def _benchmark(self):
        if not self.start or not self.goal:
            self.status = "Place Start & Goal first!"; self.scol=(255,100,100); return
        self.status = "Benchmarking…"; self.scol=(220,180,255)
        raw = self._raw()
        self.bench_res = run_benchmark(raw, self.start, self.goal)
        self.show_bench = True
        self.status = "Benchmark done!"; self.scol=(160,255,160)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def _draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                ct = self.display[r][c]
                col = COLORS.get(ct, COLORS[EMPTY])
                rect = (c*CELL, r*CELL, CELL, CELL)
                pygame.draw.rect(self.screen, col, rect)
                pygame.draw.rect(self.screen, (38,38,58), rect, 1)

        # Hover highlight
        mx,my = pygame.mouse.get_pos()
        hr,hc = self._cell_at(mx,my)
        if hr is not None:
            pygame.draw.rect(self.screen, (255,255,255),
                             (hc*CELL, hr*CELL, CELL, CELL), 2)

    def _draw_panel(self):
        px = GRID_W
        pygame.draw.rect(self.screen, (20,20,38), (px,0,SIDE_W,WIN_H))
        pygame.draw.line(self.screen, (60,60,100),(px,0),(px,WIN_H),2)

        txt(self.screen, "ALGORITHM", px+10, 32, self.f11, (120,140,210))
        for b in self.algo_btns: b.draw(self.screen)

        self.speed.draw(self.screen)

        for b in self.act.values(): b.draw(self.screen)

        txt(self.screen, "DRAW MODE", px+10, 538, self.f11, (120,140,210))
        for b in self.mode_btns: b.draw(self.screen)

        # Status bar
        pygame.draw.rect(self.screen, (14,14,28),(px, WIN_H-28, SIDE_W, 28))
        s = self.f11.render(self.status[:30], True, self.scol)
        self.screen.blit(s, (px+6, WIN_H-20))

        # Legend strip (bottom of grid)
        legend = [("Start",COLORS[START]),("Goal",COLORS[GOAL]),
                  ("Visited",COLORS[VISITED]),("Frontier",COLORS[FRONTIER]),("Path",COLORS[PATH])]
        lx = 6
        for name,col in legend:
            pygame.draw.rect(self.screen, col, (lx, WIN_H-18, 11, 11), border_radius=2)
            s = self.f11.render(name, True, (160,160,190))
            self.screen.blit(s, (lx+13, WIN_H-19))
            lx += s.get_width() + 24

    def _draw_bench(self):
        if not self.show_bench or not self.bench_res: return
        ow,oh = 640, 54+len(self.bench_res)*22+10
        ox = (GRID_W - ow)//2
        oy = (WIN_H  - oh)//2
        surf = pygame.Surface((ow,oh), pygame.SRCALPHA)
        surf.fill((18,18,36,220)); self.screen.blit(surf,(ox,oy))
        pygame.draw.rect(self.screen,(75,75,140),(ox,oy,ow,oh),2,border_radius=10)
        txt(self.screen,"Benchmark Results",ox+ow//2,oy+8,self.f16,(200,220,255),cx=True)

        # Close btn
        cr = pygame.Rect(ox+ow-32,oy+6,24,20)
        pygame.draw.rect(self.screen,(150,35,35),cr,border_radius=4)
        txt(self.screen,"✕",cr.centerx,cr.y+2,self.f11,(255,255,255),cx=True)
        self._cr = cr

        hdrs = ["Algorithm","Nodes","Time(ms)","Path"]
        cws  = [180, 70, 90, 60]
        hx   = ox+10; hy = oy+34
        for h,w in zip(hdrs,cws):
            s=self.f11.render(h,True,(150,170,230)); self.screen.blit(s,(hx,hy)); hx+=w
        hy += 18
        for i,r in enumerate(self.bench_res):
            bg=(30,32,55) if i%2==0 else (35,38,62)
            pygame.draw.rect(self.screen,bg,(ox+4,hy-2,ow-8,20),border_radius=3)
            vals=[r['name'][:22], str(r['nodes_explored']),
                  f"{r['exec_time_ms']:.3f}", str(r['path_length']) if r['path_found'] else "N/A"]
            cols=[(220,220,255),(160,220,160),(255,195,80),(90,210,255)]
            hx=ox+10
            for v,col,w in zip(vals,cols,cws):
                s=self.f11.render(v,True,col); self.screen.blit(s,(hx,hy)); hx+=w
            hy+=22

    # ── Events ────────────────────────────────────────────────────────────────

    def _events(self):
        mx,my = pygame.mouse.get_pos()
        held  = pygame.mouse.get_pressed()[0]

        for b in self.algo_btns: b.update((mx,my))
        for b in self.act.values(): b.update((mx,my))
        for b in self.mode_btns: b.update((mx,my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.animating: self.paused = not self.paused
                    else: self._start_algo()
                elif event.key == pygame.K_r:
                    self._clear_path(); self.animating=False; self.gen=None
                elif event.key == pygame.K_m:
                    import random
                    self._gen_maze(random.choice(['dfs','prim']))
                elif event.key == pygame.K_b:
                    self._benchmark()

            # Slider
            self.speed.handle(event)

            # Algo buttons
            for i,b in enumerate(self.algo_btns):
                if b.clicked(event):
                    for x in self.algo_btns: x.on=False
                    b.on=True; self.algo_idx=i

            # Mode buttons
            for b in self.mode_btns:
                if b.clicked(event):
                    for x in self.mode_btns: x.on=False
                    b.on=True; self.mode=b._mode

            # Action buttons
            for key,b in self.act.items():
                if b.clicked(event):
                    if key=='run':
                        if self.animating: self.paused=not self.paused
                        else: self._start_algo()
                    elif key=='maze':
                        import random
                        self._gen_maze(random.choice(['dfs','prim']))
                    elif key=='bench': self._benchmark()
                    elif key=='csv':
                        if self.bench_res:
                            export_to_csv(self.bench_res,'benchmark_results.csv')
                            self.status="Saved benchmark_results.csv"; self.scol=(160,255,160)
                        else:
                            self.status="Run benchmark first!"; self.scol=(255,160,80)
                    elif key=='img':
                        gs = self.screen.subsurface((0,0,GRID_W,WIN_H))
                        pygame.image.save(gs,'grid_snapshot.png')
                        self.status="Saved grid_snapshot.png"; self.scol=(160,255,160)
                    elif key=='clear':
                        self._gen_maze('dfs')   # clear = fresh maze

            # Close bench overlay
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if self.show_bench and hasattr(self,'_cr') and self._cr.collidepoint(event.pos):
                    self.show_bench=False

            # Mouse paint on grid
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                r,c=self._cell_at(mx,my); self._paint(r,c)

        # Drag paint
        if held:
            r,c=self._cell_at(mx,my)
            if r is not None and self.mode in ('wall','erase'): self._paint(r,c)

    # ── Main Loop ─────────────────────────────────────────────────────────────

    def run(self):
        last=0
        while True:
            self.clock.tick(FPS)
            self._events()

            if self.animating and not self.paused:
                now=time.time()
                delay=1.0/max(1,self.speed.val*4)
                if now-last>=delay:
                    n=max(1,self.speed.val//15)
                    self._advance(n); last=now

            self.screen.fill((28,28,45))
            self._draw_grid()
            self._draw_panel()
            self._draw_bench()

            # Shortcut hint (bottom left)
            hint="[Space] Run  [M] Maze  [R] Reset  [B] Bench"
            s=self.f11.render(hint,True,(60,65,100))
            self.screen.blit(s,(6,WIN_H-19))

            pygame.display.flip()


if __name__=='__main__':
    App().run()
