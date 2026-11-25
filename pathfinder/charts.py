"""Chart renderer for benchmark results using matplotlib."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import List, Dict, Any
import os


PALETTE = [
    '#4e79a7', '#f28e2b', '#e15759', '#76b7b2',
    '#59a14f', '#edc948', '#b07aa1', '#ff9da7',
]


def show_benchmark_charts(results: List[Dict[str, Any]], save_path: str = None):
    """
    Generates a 2x2 panel of bar charts comparing all algorithm metrics.
    Shows in a window and optionally saves to file.
    """
    if not results:
        return

    names = [r['name'] for r in results]
    nodes = [r['nodes_explored'] for r in results]
    times = [r['exec_time_ms'] for r in results]
    lengths = [r['path_length'] for r in results]
    frontier = [r['peak_frontier'] for r in results]

    colors = PALETTE[:len(names)]
    x = np.arange(len(names))
    bar_width = 0.6

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('Algorithm Benchmark Comparison', fontsize=16, fontweight='bold', y=1.01)
    fig.patch.set_facecolor('#1e1e2e')

    metrics = [
        (axes[0,0], nodes,    'Nodes Explored',       '#4e79a7', 'Count'),
        (axes[0,1], times,    'Execution Time (ms)',   '#f28e2b', 'ms'),
        (axes[1,0], lengths,  'Path Length / Cost',    '#59a14f', 'Units'),
        (axes[1,1], frontier, 'Peak Frontier Size',    '#e15759', 'Count'),
    ]

    for ax, data, title, color, ylabel in metrics:
        ax.set_facecolor('#2a2a3e')
        bars = ax.bar(x, data, color=colors, width=bar_width, edgecolor='white', linewidth=0.5)
        ax.set_title(title, color='white', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=30, ha='right', fontsize=8, color='white')
        ax.set_ylabel(ylabel, color='#aaaaaa', fontsize=9)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('#555577')
        ax.spines['left'].set_color('#555577')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.label.set_color('#aaaaaa')
        # Value labels on bars
        for bar, val in zip(bars, data):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data)*0.01,
                    f'{val:.2f}' if isinstance(val, float) else str(val),
                    ha='center', va='bottom', color='white', fontsize=7)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
    # Show non-blocking
    matplotlib.use('TkAgg')
    plt.switch_backend('TkAgg')
    try:
        plt.show(block=False)
        plt.pause(0.1)
    except Exception:
        pass
