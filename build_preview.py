"""Generate preview.png — overview of the EA funding network for the README.

Larger, more legible than the earlier version: bigger figure, bigger fonts,
funder labels stay readable.
"""

import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from build_canvas import FUNDERS, CAUSE_AREAS, EDGES

COLOR_HEX = {"1":"#dc2626","2":"#ea580c","3":"#ca8a04","4":"#16a34a","5":"#0891b2","6":"#7c3aed"}
def hex_of(c):
    if not c: return "#475569"
    return c if c.startswith("#") else COLOR_HEX.get(c, "#475569")

G = nx.DiGraph()
funder_color = {}
for fid, label, color in FUNDERS:
    hexc = hex_of(color)
    funder_color[fid] = hexc
    short_label = label.split("\n")[0]
    G.add_node(fid, label=short_label, kind="funder", color=hexc, size=2200)

area_color = {}
for area_key, area in CAUSE_AREAS.items():
    hexc = hex_of(area["color"])
    area_color[area_key] = hexc
    for oid, olabel in area["orgs"]:
        short = olabel.split("\n")[0]
        G.add_node(oid, label=short, kind=area_key, color=hexc, size=600)

for (src, dst, primary) in EDGES:
    if src in G and dst in G:
        G.add_edge(src, dst, color=funder_color.get(src, "#94a3b8"),
                   width=1.6 if primary else 0.7, primary=primary)

# Layout: funders in a left column, recipients in a wider half-circle on the right
pos = {}
n_funders = len(FUNDERS)
for i, (fid, _, _) in enumerate(FUNDERS):
    y = 1.0 - 2.0 * i / max(1, n_funders - 1)
    pos[fid] = (-3.8, y * 2.6)

area_keys = list(CAUSE_AREAS.keys())
n_areas = len(area_keys)
ANG_START, ANG_END = -82, 82
for ai, area_key in enumerate(area_keys):
    orgs = CAUSE_AREAS[area_key]["orgs"]
    n = len(orgs)
    center_ang = ANG_START + (ANG_END - ANG_START) * (ai + 0.5) / n_areas
    sub_span = (ANG_END - ANG_START) / n_areas * 0.92
    sub_start = center_ang - sub_span / 2
    for j, (oid, _) in enumerate(orgs):
        sub_ang = sub_start + sub_span * j / max(1, n - 1) if n > 1 else center_ang
        rad = math.radians(sub_ang)
        # 3-band staircase reduces label overlap
        r = 3.2 + 0.65 * (j % 3)
        pos[oid] = (r * math.cos(rad) + 0.6, r * math.sin(rad) * 1.05)

# Larger figure for better readability
fig, ax = plt.subplots(figsize=(24, 14), dpi=110)
ax.set_facecolor("#f8fafc")
fig.patch.set_facecolor("#f8fafc")

for (u, v) in G.edges():
    nx.draw_networkx_edges(
        G, pos, edgelist=[(u, v)],
        edge_color=G[u][v]["color"],
        width=G[u][v]["width"],
        alpha=0.65 if G[u][v]["primary"] else 0.22,
        arrows=True, arrowsize=7, arrowstyle="-|>",
        connectionstyle="arc3,rad=0.08", ax=ax,
    )

funder_ids = [n for n, d in G.nodes(data=True) if d["kind"] == "funder"]
nx.draw_networkx_nodes(
    G, pos, nodelist=funder_ids,
    node_color=[G.nodes[n]["color"] for n in funder_ids],
    node_size=[G.nodes[n]["size"] for n in funder_ids],
    node_shape="s", edgecolors="#0f172a", linewidths=1.5, ax=ax,
)

for area_key in CAUSE_AREAS:
    ids = [n for n, d in G.nodes(data=True) if d["kind"] == area_key]
    if not ids: continue
    nx.draw_networkx_nodes(
        G, pos, nodelist=ids,
        node_color="#ffffff",
        node_size=[G.nodes[n]["size"] for n in ids],
        node_shape="o",
        edgecolors=area_color[area_key],
        linewidths=2.2, ax=ax,
    )

# Labels — funders inside square in white; recipients offset outward in dark text
funder_labels = {n: G.nodes[n]["label"] for n in funder_ids}
nx.draw_networkx_labels(G, pos, labels=funder_labels, font_size=11,
                        font_color="white", font_weight="bold", ax=ax)

recipient_labels = {n: G.nodes[n]["label"][:28] for n in G.nodes()
                    if n not in funder_ids}
rl_pos = {}
for n in recipient_labels:
    x, y = pos[n]
    cx, cy = 0.6, 0.0
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    if r > 0.001:
        scale = (r + 0.35) / r
        rl_pos[n] = (cx + dx * scale, cy + dy * scale)
    else:
        rl_pos[n] = (x, y)

nx.draw_networkx_labels(G, rl_pos, labels=recipient_labels,
                        font_size=10, font_color="#0f172a", ax=ax)

ax.set_title("EA Organization Map — Funders & Recipients (May 2025)",
             fontsize=20, color="#0f172a", pad=18, weight="bold")
ax.text(0.5, -0.03,
        "Squares (left) = funders.   Circles (right) = recipients, border color = cause area.   "
        "Edges colored by funder;  solid = primary, faded = secondary.",
        ha="center", va="top", transform=ax.transAxes, fontsize=11, color="#475569")
ax.axis("off")

legend_handles = []
for k in CAUSE_AREAS:
    legend_handles.append(mpatches.Patch(facecolor="white", edgecolor=area_color[k],
                                         linewidth=2.2, label=CAUSE_AREAS[k]["label"]))
legend_handles.append(mpatches.Patch(facecolor="#475569", edgecolor="#0f172a",
                                     label="Funder"))
ax.legend(handles=legend_handles, loc="lower left", fontsize=11, frameon=True,
          facecolor="white", edgecolor="#e2e8f0")

ax.margins(0.08)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
plt.tight_layout()
plt.savefig(OUT, dpi=130, bbox_inches="tight", facecolor="#f8fafc")
print("Wrote", OUT)
print("  {} nodes, {} edges".format(G.number_of_nodes(), G.number_of_edges()))
