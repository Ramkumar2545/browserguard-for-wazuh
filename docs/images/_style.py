"""Shared style for BrowserGuard diagrams."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

# Dark technical palette
BG        = "#0d1117"   # GitHub dark bg
PANEL     = "#161b22"
PANEL_HI  = "#1f2530"
GRID      = "#30363d"
TEXT      = "#e6edf3"
MUTED     = "#8b949e"

# Accents
BLUE      = "#58a6ff"
GREEN     = "#3fb950"
AMBER     = "#d29922"
RED       = "#f85149"
PURPLE    = "#bc8cff"
CYAN      = "#39c5cf"
PINK      = "#ff7b72"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "savefig.edgecolor": BG,
    "text.color": TEXT,
    "axes.labelcolor": TEXT,
    "axes.edgecolor": GRID,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.family": "DejaVu Sans",
    "font.size": 11,
})

def new_fig(w=13, h=7):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    return fig, ax

def box(ax, x, y, w, h, *, title=None, subtitle=None, lines=None,
        color=BLUE, fill=PANEL, title_size=12, text_size=9.5, mono=False):
    """Rounded panel with title + optional body lines."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=1.2",
        linewidth=1.6, edgecolor=color, facecolor=fill,
    )
    ax.add_patch(patch)
    cx = x + w / 2
    ty = y + h - 2.5
    if title:
        ax.text(cx, ty, title,
                ha="center", va="top", fontsize=title_size,
                color=color, weight="bold")
        ty -= 3.2
    if subtitle:
        ax.text(cx, ty, subtitle,
                ha="center", va="top", fontsize=text_size - 0.5,
                color=MUTED, style="italic")
        ty -= 2.8
    if lines:
        family = "DejaVu Sans Mono" if mono else "DejaVu Sans"
        lh = 2.7
        for ln in lines:
            ax.text(x + 2.2, ty, ln,
                    ha="left", va="top", fontsize=text_size,
                    color=TEXT, family=family)
            ty -= lh

def arrow(ax, x1, y1, x2, y2, *, color=BLUE, label=None, label_offset=(0, 1.4),
          style="-|>", lw=1.6, curved=0.0):
    cs = "arc3,rad=%.2f" % curved
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle=style, mutation_scale=14,
                        color=color, linewidth=lw, connectionstyle=cs)
    ax.add_patch(a)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=9, color=color,
                bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="none", alpha=0.85))

def title(ax, text, subtitle=None):
    ax.text(50, 97, text, ha="center", va="top",
            fontsize=17, color=TEXT, weight="bold")
    if subtitle:
        ax.text(50, 93.6, subtitle, ha="center", va="top",
                fontsize=10.5, color=MUTED, style="italic")

def footer(ax, text):
    ax.text(50, 1.6, text, ha="center", va="bottom",
            fontsize=8.5, color=MUTED, style="italic")

def legend(ax, items, x=2, y=4.5):
    """items = [(label, color)]"""
    for i, (lbl, col) in enumerate(items):
        ax.add_patch(FancyBboxPatch((x + i * 22, y), 1.6, 1.6,
                                    boxstyle="round,pad=0.02,rounding_size=0.4",
                                    linewidth=0, facecolor=col))
        ax.text(x + i * 22 + 2.5, y + 0.8, lbl, ha="left", va="center",
                fontsize=9, color=MUTED)

def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
