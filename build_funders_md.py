"""Generate FUNDERS.md — a human-readable reference doc of every funder in the map,
with the principal donors, operational leads, founding year, and typical volume."""

import os
from build_canvas import FUNDERS, EDGES
from funders_detail import FUNDER_PEOPLE

# Count recipients per funder for the summary
recipient_count = {}
for src, dst, _ in EDGES:
    recipient_count[src] = recipient_count.get(src, 0) + 1

lines = []
lines.append("# Funder Reference — People Behind the Money\n")
lines.append("Detailed view of the 17 funders in the EA ecosystem map. "
             "For each funder: the principal donors (where the money comes from), "
             "the operational leads (who decides what to fund), and rough scale.\n")
lines.append("---\n")

for fid, label, _color in FUNDERS:
    if fid not in FUNDER_PEOPLE:
        continue
    p = FUNDER_PEOPLE[fid]
    clean_label = label.replace("\n", " ")
    lines.append(f"## {clean_label}\n")

    meta_bits = []
    if p.get("founded"):
        meta_bits.append(f"**Founded:** {p['founded']}")
    if p.get("typical_volume"):
        meta_bits.append(f"**Scale:** {p['typical_volume']}")
    if fid in recipient_count:
        meta_bits.append(f"**Recipients in map:** {recipient_count[fid]}")
    if meta_bits:
        lines.append("  ·  ".join(meta_bits) + "\n")

    # Principal donors
    lines.append("**Where the money comes from**\n")
    for d in p.get("donors", []):
        src = f" — _{d['source']}_" if d.get("source") else ""
        lines.append(f"- **{d['name']}** ({d['role']}){src}")
    lines.append("")

    # Operational leads
    if p.get("leads"):
        lines.append("**Who decides what to fund**\n")
        for ld in p["leads"]:
            lines.append(f"- **{ld['name']}** — {ld['role']}")
        lines.append("")

    if p.get("notes"):
        lines.append(f"> {p['notes']}\n")

    if p.get("source_url"):
        lines.append(f"_Source: <{p['source_url']}>_\n")

    lines.append("---\n")

# Quick at-a-glance table at the top
table_lines = [
    "## Quick view\n",
    "| Funder | Principal donor(s) | Founded | Scale | # orgs funded |",
    "|---|---|---|---|---|",
]
for fid, label, _ in FUNDERS:
    if fid not in FUNDER_PEOPLE:
        continue
    p = FUNDER_PEOPLE[fid]
    donor_names = ", ".join(d["name"] for d in p.get("donors", [])[:2])
    if len(p.get("donors", [])) > 2:
        donor_names += " +"
    table_lines.append(
        f"| {label.replace(chr(10), ' / ')} | {donor_names} | "
        f"{p.get('founded') or '—'} | {p.get('typical_volume') or '—'} | "
        f"{recipient_count.get(fid, 0)} |"
    )
table_lines.append("")

# Insert the table near the top, after the intro paragraph
final = []
final.extend(lines[:3])           # title + intro + hr
final.extend(table_lines)
final.append("---\n")
final.extend(lines[3:])

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FUNDERS.md")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(final))
print("Wrote", OUT)
print("  Lines:", len(final))
