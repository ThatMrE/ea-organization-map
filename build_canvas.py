"""Generate Obsidian Canvas file for EA funder-recipient map.

Obsidian Canvas format:
- nodes: list of {id, type, text, x, y, width, height, color?}
- edges: list of {id, fromNode, fromSide, toNode, toSide, label?, color?}

Color codes (Obsidian preset):
  "1" red, "2" orange, "3" yellow, "4" green, "5" cyan, "6" purple
  Or hex like "#abcdef"
"""

import json
import os

# -----------------------------------------------------------------------------
# FUNDERS — left column
# Each funder has a unique color used for both its node and outgoing edges
# -----------------------------------------------------------------------------
FUNDERS = [
    # (id, label, color)
    ("op",       "Open Philanthropy\n(Moskovitz / Tuna)",     "6"),  # purple
    ("sff",      "SFF\n(Tallinn-backed)",                     "5"),  # cyan
    ("ltff",     "EA Funds: LTFF",                            "5"),
    ("eaif",     "EA Funds: EAIF",                            "5"),
    ("awf",      "EA Funds: Animal Welfare",                  "5"),
    ("ghdf",     "EA Funds: Global Health",                   "5"),
    ("ftx",      "FTX Future Fund\n(defunct 2022)",           "1"),  # red
    ("longview", "Longview Philanthropy",                     "4"),  # green
    ("givewell", "GiveWell",                                  "4"),
    ("fp",       "Founders Pledge",                           "4"),
    ("ev",       "Effective Ventures\n(fiscal sponsor)",      "3"),  # yellow
    ("tallinn",  "Jaan Tallinn\n(personal)",                  "5"),
    ("buterin",  "Vitalik Buterin",                           "2"),  # orange
    ("macro",    "Macroscopic Ventures",                      "2"),
    ("astera",   "Astera Institute\n(McCaleb)",               "2"),
    ("schmidt",  "Schmidt Futures\n(adjacent)",               "2"),
    ("aim",      "Charity Entrepreneurship / AIM",            "4"),
]

FUNDER_X = -800
FUNDER_W = 280
FUNDER_H = 90
FUNDER_SPACING = 110

# -----------------------------------------------------------------------------
# RECIPIENT ORGS by cause area
# Each cause area is rendered as a "group" node with org nodes inside.
# -----------------------------------------------------------------------------

# Layout: 2 columns per group, w=240 each, h=70 each, spacing 30y, 20x gutter
ORG_W = 240
ORG_H = 70
ORG_SPACING_Y = 30
ORG_SPACING_X = 20
GROUP_PAD_X = 30
GROUP_PAD_Y = 60

CAUSE_AREAS = {
    "ai_safety": {
        "label": "AI Safety & Alignment",
        "color": "6",
        "cols": 3,
        "x": -300, "y": -200,
        "orgs": [
            ("miri",        "MIRI"),
            ("redwood",     "Redwood Research"),
            ("arc",         "ARC\n(Alignment Research Center)"),
            ("metr",        "METR\n(ARC Evals spinout)"),
            ("anthropic",   "Anthropic\n(for-profit lab)"),
            ("apollo",      "Apollo Research"),
            ("farai",       "FAR AI"),
            ("chai",        "CHAI\n(UC Berkeley)"),
            ("cais",        "Center for AI Safety\n(CAIS)"),
            ("conjecture",  "Conjecture"),
            ("aiimpacts",   "AI Impacts"),
            ("coop",        "Cooperative AI Foundation"),
            ("aiscamp",     "AI Safety Camp"),
            ("mats",        "MATS Program"),
            ("bluedot",     "BlueDot Impact"),
            ("constellation","Constellation"),
            ("lightcone",   "Lightcone Infrastructure\n(LessWrong, LightHaven)"),
            ("govai",       "GovAI"),
        ],
    },
    "biosecurity": {
        "label": "Biosecurity & Pandemic Prevention",
        "color": "4",
        "cols": 2,
        "x": 1100, "y": -200,
        "orgs": [
            ("nti",        "NTI Bio Program"),
            ("jhuchs",     "Johns Hopkins\nCenter for Health Security"),
            ("securebio", "SecureBio\n(Kevin Esvelt)"),
            ("blueprint", "Blueprint Biosecurity"),
            ("csr",       "Council on Strategic Risks"),
            ("sentinel",  "Sentinel Bio"),
            ("oneday",    "1Day Sooner"),
            ("helena",    "Helena Biosciences"),
        ],
    },
    "global_health": {
        "label": "Global Health & Development",
        "color": "5",
        "cols": 2,
        "x": 1100, "y": 700,
        "orgs": [
            ("amf",      "Against Malaria Foundation"),
            ("mc",       "Malaria Consortium\n(SMC)"),
            ("hki",      "Helen Keller International"),
            ("newinc",   "New Incentives"),
            ("evaction", "Evidence Action"),
            ("givedir",  "GiveDirectly"),
            ("fem",      "Family Empowerment Media"),
            ("idi",      "IDinsight"),
        ],
    },
    "animal_welfare": {
        "label": "Animal Welfare",
        "color": "3",
        "cols": 2,
        "x": 1100, "y": 1500,
        "orgs": [
            ("thl",      "The Humane League"),
            ("mfa",      "Mercy For Animals"),
            ("gfi",      "Good Food Institute"),
            ("wai",      "Wild Animal Initiative"),
            ("ace",      "Animal Charity Evaluators"),
            ("ciwf",     "Compassion in World Farming"),
            ("fwi",      "Fish Welfare Initiative"),
            ("sinergia", "Sinergia Animal"),
            ("faun",     "Faunalytics"),
            ("proveg",   "ProVeg International"),
        ],
    },
    "meta": {
        "label": "Movement Building & Meta",
        "color": "2",
        "cols": 2,
        "x": -300, "y": 1500,
        "orgs": [
            ("cea",      "Centre for Effective Altruism"),
            ("80k",      "80,000 Hours"),
            ("gwwc",     "Giving What We Can"),
            ("rp",       "Rethink Priorities"),
            ("gpi",      "GPI\n(Oxford)"),
            ("hli",      "Happier Lives Institute"),
            ("probably", "Probably Good"),
            ("ce",       "Charity Entrepreneurship"),
            ("forethought","Forethought Foundation/Research"),
            ("flI",      "Future of Life Institute"),
            ("allfed",   "ALLFED"),
        ],
    },
    "policy": {
        "label": "Policy & Governance",
        "color": "1",
        "cols": 2,
        "x": 500, "y": 1500,
        "orgs": [
            ("cset",   "CSET\n(Georgetown)"),
            ("cltr",   "CLTR\n(UK)"),
            ("cser",   "CSER\n(Cambridge)"),
            ("iaps",   "IAPS"),
            ("caip",   "Center for AI Policy"),
            ("horizon","Horizon Institute\nfor Public Service"),
            ("simon",  "Simon Institute\nLongterm Gov"),
        ],
    },
    "historical": {
        "label": "Closed / Historical",
        "color": "#888888",
        "cols": 1,
        "x": -300, "y": 2400,
        "orgs": [
            ("fhi",  "FHI Oxford\n(CLOSED Apr 2024)"),
            ("ought","Ought\n(pivoted)"),
        ],
    },
}

# -----------------------------------------------------------------------------
# Funding edges: (funder_id, recipient_id, primary?)
# primary=True -> solid colored edge ; False -> grey/dashed
# -----------------------------------------------------------------------------
EDGES = [
    # Open Philanthropy — primary funder for most large orgs
    ("op", "miri", True), ("op", "redwood", True), ("op", "arc", True),
    ("op", "metr", True), ("op", "anthropic", True), ("op", "apollo", True),
    ("op", "farai", True), ("op", "chai", True), ("op", "cais", True),
    ("op", "mats", True), ("op", "bluedot", True), ("op", "constellation", True),
    ("op", "lightcone", True), ("op", "govai", True), ("op", "flI", True),
    ("op", "nti", True), ("op", "jhuchs", True), ("op", "securebio", True),
    ("op", "blueprint", True), ("op", "csr", True), ("op", "oneday", True),
    ("op", "evaction", True), ("op", "hki", True), ("op", "newinc", True),
    ("op", "fem", True), ("op", "idi", True),
    ("op", "thl", True), ("op", "mfa", True), ("op", "gfi", True),
    ("op", "wai", True), ("op", "ace", True), ("op", "ciwf", True),
    ("op", "cea", True), ("op", "80k", True), ("op", "gwwc", True),
    ("op", "rp", True), ("op", "gpi", True),
    ("op", "cset", True), ("op", "cltr", True), ("op", "cser", True),
    ("op", "iaps", True), ("op", "horizon", True), ("op", "ce", True),
    ("op", "fhi", False),

    # SFF — AI safety heavy
    ("sff", "miri", True), ("sff", "lightcone", True), ("sff", "farai", True),
    ("sff", "apollo", True), ("sff", "aiimpacts", True), ("sff", "conjecture", True),
    ("sff", "aiscamp", True), ("sff", "mats", True), ("sff", "arc", True),
    ("sff", "chai", True), ("sff", "coop", True), ("sff", "bluedot", True),
    ("sff", "flI", True), ("sff", "govai", True), ("sff", "caip", True),
    ("sff", "simon", True), ("sff", "forethought", True), ("sff", "rp", True),
    ("sff", "allfed", True),

    # Tallinn personal (beyond SFF)
    ("tallinn", "miri", False), ("tallinn", "lightcone", False),
    ("tallinn", "flI", False),

    # EA Funds sub-funds
    ("ltff", "miri", False), ("ltff", "apollo", False), ("ltff", "mats", False),
    ("ltff", "aiscamp", False), ("ltff", "aiimpacts", False), ("ltff", "caip", False),
    ("eaif", "cea", False), ("eaif", "80k", False), ("eaif", "probably", False),
    ("eaif", "gwwc", False),
    ("awf", "thl", False), ("awf", "mfa", False), ("awf", "wai", False),
    ("awf", "sinergia", False), ("awf", "fwi", False), ("awf", "faun", False),
    ("awf", "proveg", False),
    ("ghdf", "newinc", False), ("ghdf", "fem", False),

    # FTX (historical, defunct)
    ("ftx", "anthropic", False), ("ftx", "lightcone", False), ("ftx", "arc", False),
    ("ftx", "allfed", False), ("ftx", "flI", False), ("ftx", "helena", False),
    ("ftx", "securebio", False),

    # Longview
    ("longview", "securebio", True), ("longview", "nti", True),
    ("longview", "cltr", True), ("longview", "govai", True),
    ("longview", "bluedot", True), ("longview", "csr", True),

    # GiveWell
    ("givewell", "amf", True), ("givewell", "mc", True), ("givewell", "hki", True),
    ("givewell", "newinc", True), ("givewell", "evaction", True),
    ("givewell", "givedir", False), ("givewell", "idi", False),

    # Founders Pledge
    ("fp", "givedir", True), ("fp", "amf", True), ("fp", "ce", False),
    ("fp", "forethought", False),

    # Effective Ventures (fiscal sponsor)
    ("ev", "cea", False), ("ev", "80k", False), ("ev", "gwwc", False),
    ("ev", "govai", False), ("ev", "bluedot", False), ("ev", "forethought", False),

    # Schmidt (adjacent)
    ("schmidt", "cset", False), ("schmidt", "rp", False),

    # Macroscopic
    ("macro", "mats", False), ("macro", "apollo", False), ("macro", "securebio", False),

    # Buterin
    ("buterin", "flI", False), ("buterin", "sentinel", False),

    # AIM
    ("aim", "fem", False), ("aim", "fwi", False), ("aim", "sinergia", False),
]

# -----------------------------------------------------------------------------
# BUILD
# -----------------------------------------------------------------------------
nodes = []
edges = []

# Funder nodes
for i, (fid, label, color) in enumerate(FUNDERS):
    nodes.append({
        "id": fid,
        "type": "text",
        "text": f"**{label}**",
        "x": FUNDER_X,
        "y": i * FUNDER_SPACING,
        "width": FUNDER_W,
        "height": FUNDER_H,
        "color": color,
    })

# Cause area groups + org nodes
for area_key, area in CAUSE_AREAS.items():
    cols = area["cols"]
    org_count = len(area["orgs"])
    rows = (org_count + cols - 1) // cols
    group_w = cols * ORG_W + (cols - 1) * ORG_SPACING_X + 2 * GROUP_PAD_X
    group_h = rows * ORG_H + (rows - 1) * ORG_SPACING_Y + 2 * GROUP_PAD_Y

    # Group container
    nodes.append({
        "id": f"group_{area_key}",
        "type": "group",
        "label": area["label"],
        "x": area["x"],
        "y": area["y"],
        "width": group_w,
        "height": group_h,
        "color": area["color"],
    })

    # Org nodes inside the group
    for idx, (oid, olabel) in enumerate(area["orgs"]):
        col = idx % cols
        row = idx // cols
        nx = area["x"] + GROUP_PAD_X + col * (ORG_W + ORG_SPACING_X)
        ny = area["y"] + GROUP_PAD_Y + row * (ORG_H + ORG_SPACING_Y)
        nodes.append({
            "id": oid,
            "type": "text",
            "text": olabel,
            "x": nx,
            "y": ny,
            "width": ORG_W,
            "height": ORG_H,
        })

# Build set of valid node ids
valid_ids = {n["id"] for n in nodes}

# Color map for funders (edges colored by source funder)
funder_color = {fid: color for fid, _, color in FUNDERS}

# Edges
edge_id = 0
skipped = []
for (src, dst, primary) in EDGES:
    if src not in valid_ids or dst not in valid_ids:
        skipped.append((src, dst))
        continue
    edge_id += 1
    edge = {
        "id": f"e{edge_id}",
        "fromNode": src,
        "fromSide": "right",
        "toNode": dst,
        "toSide": "left",
        "color": funder_color.get(src, "1"),
    }
    if not primary:
        # Secondary edges: leave default styling (Obsidian doesn't support
        # dashed edges natively; we communicate by omitting the color so it
        # renders grey). Actually we still want some color clue, so keep color
        # but no label.
        pass
    edges.append(edge)

canvas = {"nodes": nodes, "edges": edges}

OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "EA_funding_map.canvas",
)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(canvas, f, indent=2, ensure_ascii=False)

print(f"Wrote {OUT}")
print(f"  {len(nodes)} nodes, {len(edges)} edges")
if skipped:
    print(f"  Skipped {len(skipped)} edges (unknown ids): {skipped}")
