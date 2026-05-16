"""Generate funders_preview.png — a focused, legible card-style view of the
17 funders showing the principal donors behind each one."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from build_canvas import FUNDERS, EDGES
from funders_detail import FUNDER_PEOPLE

COLOR_HEX = {"1":"#dc2626","2":"#ea580c","3":"#ca8a04","4":"#16a34a","5":"#0891b2","6":"#7c3aed"}
def hex_of(c):
    if not c: return "#475569"
    return c if c.startswith("#") else COLOR_HEX.get(c, "#475569")

recipient_count = {}
for src, _, _ in EDGES:
    recipient_count[src] = recipient_count.get(src, 0) + 1

COLS = 3
ROWS = (len(FUNDERS) + COLS - 1) // COLS
CARD_W = 5.0
CARD_H = 3.6
GAP_X = 0.35
GAP_Y = 0.45

FIG_W = COLS * CARD_W + (COLS + 1) * GAP_X
FIG_H = ROWS * CARD_H + (ROWS + 1) * GAP_Y + 1.2

fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=110)
fig.patch.set_facecolor("#f8fafc")

# Title bar
fig.text(0.5, 1 - 0.35 / FIG_H, "EA Funders — Who's Behind the Money",
         ha="center", va="top", fontsize=22, weight="bold", color="#0f172a")
fig.text(0.5, 1 - 0.85 / FIG_H,
         "17 funding bodies in the EA ecosystem. For each: the principal donors, "
         "the operational leads, and scale of annual giving. Knowledge cutoff May 2025.",
         ha="center", va="top", fontsize=10, color="#475569")

for idx, (fid, label, color) in enumerate(FUNDERS):
    p = FUNDER_PEOPLE.get(fid, {})
    col = idx % COLS
    row = idx // COLS

    # Card position in figure coordinates (0..1)
    x_in = GAP_X + col * (CARD_W + GAP_X)
    y_in = FIG_H - 1.1 - (row + 1) * CARD_H - row * GAP_Y
    x = x_in / FIG_W
    y = y_in / FIG_H
    w = CARD_W / FIG_W
    h = CARD_H / FIG_H

    ax = fig.add_axes([x, y, w, h])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")

    # Card background
    card = FancyBboxPatch((0.005, 0.005), 0.99, 0.99,
                          boxstyle="round,pad=0.005,rounding_size=0.02",
                          facecolor="white", edgecolor="#e2e8f0",
                          linewidth=1.0, transform=ax.transAxes)
    ax.add_patch(card)

    # Colored top bar with funder name
    bar = FancyBboxPatch((0.005, 0.78), 0.99, 0.22,
                         boxstyle="round,pad=0.005,rounding_size=0.02",
                         facecolor=hex_of(color), edgecolor="none",
                         transform=ax.transAxes)
    ax.add_patch(bar)
    clean_label = label.replace("\n", "  ")
    ax.text(0.04, 0.93, clean_label, transform=ax.transAxes,
            fontsize=12, weight="bold", color="white", va="top")

    # Meta line — founded / scale / # recipients
    meta = []
    if p.get("founded"): meta.append(f"Founded {p['founded']}")
    if p.get("typical_volume"): meta.append(p["typical_volume"])
    meta.append(f"Funds {recipient_count.get(fid, 0)} orgs")
    ax.text(0.04, 0.80, "  ·  ".join(meta), transform=ax.transAxes,
            fontsize=8, color="white", va="top", alpha=0.92)

    # "Where the money comes from"
    ax.text(0.04, 0.72, "WHERE THE MONEY COMES FROM",
            transform=ax.transAxes, fontsize=7, weight="bold",
            color="#64748b", va="top")
    cursor_y = 0.66
    for d in p.get("donors", [])[:3]:
        name_line = d["name"]
        src = d.get("source", "")
        ax.text(0.04, cursor_y, "● " + name_line, transform=ax.transAxes,
                fontsize=9, weight="bold", color="#0f172a", va="top")
        if src:
            ax.text(0.08, cursor_y - 0.06, src, transform=ax.transAxes,
                    fontsize=7.5, color="#64748b", va="top", style="italic")
            cursor_y -= 0.13
        else:
            cursor_y -= 0.07

    # "Who decides" — show first 2 leads
    ax.text(0.04, max(0.30, cursor_y - 0.02), "WHO DECIDES WHAT TO FUND",
            transform=ax.transAxes, fontsize=7, weight="bold",
            color="#64748b", va="top")
    lead_cursor = max(0.25, cursor_y - 0.08)
    for ld in p.get("leads", [])[:3]:
        ax.text(0.04, lead_cursor, "○ " + ld["name"], transform=ax.transAxes,
                fontsize=9, color="#0f172a", va="top")
        ax.text(0.08, lead_cursor - 0.05, ld["role"], transform=ax.transAxes,
                fontsize=7.5, color="#64748b", va="top", style="italic")
        lead_cursor -= 0.10

    # Footer notes if present
    if p.get("notes"):
        notes = p["notes"]
        if len(notes) > 110:
            notes = notes[:108] + "…"
        ax.text(0.04, 0.04, notes, transform=ax.transAxes,
                fontsize=7, color="#475569", va="bottom",
                style="italic", wrap=True)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "funders_preview.png")
plt.savefig(OUT, dpi=120, facecolor="#f8fafc", bbox_inches="tight")
print("Wrote", OUT)
print("  cards:", len(FUNDERS))
