"""
Generates syntax-highlighted code screenshots as PNG images.
Run before generate_report.py
"""
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
import os

OUT = r"C:\Users\Rudra\Desktop\ai_project\report_assets"
os.makedirs(OUT, exist_ok=True)

SNIPPETS = {
    "bfs_code": (
        r"C:\Users\Rudra\Desktop\ai_project\pathfinder\algorithms\bfs.py",
        None   # whole file
    ),
    "astar_code": (
        r"C:\Users\Rudra\Desktop\ai_project\pathfinder\algorithms\astar.py",
        None
    ),
    "greedy_code": (
        r"C:\Users\Rudra\Desktop\ai_project\pathfinder\algorithms\greedy.py",
        None
    ),
    "dfs_code": (
        r"C:\Users\Rudra\Desktop\ai_project\pathfinder\algorithms\dfs.py",
        None
    ),
    "maze_code": (
        r"C:\Users\Rudra\Desktop\ai_project\pathfinder\maze_generator.py",
        None
    ),
    "benchmark_code": (
        r"C:\Users\Rudra\Desktop\ai_project\pathfinder\benchmark.py",
        None
    ),
}

fmt = ImageFormatter(
    style='monokai',
    font_name='Courier New',
    font_size=14,
    line_numbers=True,
    line_number_bg='#272822',
    line_number_fg='#888888',
    line_number_separator=True,
    hl_color='#49483e',
    image_pad=14,
)

for name, (path, _) in SNIPPETS.items():
    with open(path, 'r') as f:
        code = f.read()
    result = highlight(code, PythonLexer(), fmt)
    out_path = os.path.join(OUT, f"{name}.png")
    with open(out_path, 'wb') as f:
        f.write(result)
    print(f"Saved: {out_path}")

print("All code images generated!")
