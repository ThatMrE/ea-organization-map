"""Generate a single-file interactive HTML network graph of EA funders & recipients.

Uses vis-network (loaded from CDN). Self-contained: drop index.html into any
folder served as a static site (GitHub Pages, Netlify, S3, etc.).

Reads the same node & edge data from build_canvas.py so the two stay in sync.
"""

import json
import os
from build_canvas import FUNDERS, CAUSE_AREAS, EDGES

# Map preset color codes (Obsidian) to actual hex for the web
COLOR_HEX = {
    "1": "#dc2626",   # red
    "2": "#ea580c",   # orange
    "3": "#ca8a04",   # yellow
    "4": "#16a34a",   # green
    "5": "#0891b2",   # cyan
    "6": "#7c3aed",   # purple
}

def color_to_hex(c):
    if not c:
        return "#475569"
    if c.startswith("#"):
        return c
    return COLOR_HEX.get(c, "#475569")

# Build a unified node/edge dataset for vis-network
vis_nodes = []
vis_edges = []

# --- Funders ---
funder_colors = {}
for fid, label, color in FUNDERS:
    hex_color = color_to_hex(color)
    funder_colors[fid] = hex_color
    vis_nodes.append({
        "id": fid,
        "label": label.replace("\n", "\n"),
        "group": "funder",
        "color": {"background": hex_color, "border": "#0f172a"},
        "shape": "box",
        "font": {"color": "#fff", "size": 14, "face": "Inter, system-ui, sans-serif"},
        "borderWidth": 2,
        "category": "funder",
        "title": f"<b>{label}</b><br>Funder",
    })

# --- Recipients by cause area ---
for area_key, area in CAUSE_AREAS.items():
    area_hex = color_to_hex(area["color"])
    for oid, olabel in area["orgs"]:
        vis_nodes.append({
            "id": oid,
            "label": olabel,
            "group": area_key,
            "color": {"background": "#f8fafc", "border": area_hex},
            "shape": "box",
            "font": {"color": "#0f172a", "size": 12, "face": "Inter, system-ui, sans-serif"},
            "borderWidth": 3,
            "category": area_key,
            "categoryLabel": area["label"],
            "categoryColor": area_hex,
            "title": f"<b>{olabel}</b><br>{area['label']}",
        })

# --- Edges ---
valid_ids = {n["id"] for n in vis_nodes}
edge_id = 0
for (src, dst, primary) in EDGES:
    if src not in valid_ids or dst not in valid_ids:
        continue
    edge_id += 1
    color = funder_colors.get(src, "#94a3b8")
    vis_edges.append({
        "id": f"e{edge_id}",
        "from": src,
        "to": dst,
        "color": {"color": color, "opacity": 0.85 if primary else 0.4},
        "arrows": "to",
        "smooth": {"type": "continuous"},
        "width": 2 if primary else 1,
        "dashes": not primary,
        "funder": src,
        "primary": primary,
    })

# Funder list for the filter UI
funder_filter_data = [
    {"id": fid, "label": label.replace("\n", " — "), "color": color_to_hex(color)}
    for fid, label, color in FUNDERS
]

# Cause area list for the filter UI
cause_filter_data = [
    {"id": k, "label": v["label"], "color": color_to_hex(v["color"])}
    for k, v in CAUSE_AREAS.items()
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>EA Organization Map — Funders & Recipients</title>
<meta name="description" content="Interactive map of Effective Altruism organizations and their funding relationships, as of May 2025." />
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/vis-network@9.1.9/styles/vis-network.min.css" />
<style>
  :root {
    color-scheme: light;
    --bg: #f8fafc;
    --panel: #ffffff;
    --border: #e2e8f0;
    --text: #0f172a;
    --muted: #64748b;
    --accent: #7c3aed;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--text); font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }
  #app { display: grid; grid-template-columns: 320px 1fr; height: 100vh; }
  aside { background: var(--panel); border-right: 1px solid var(--border); overflow-y: auto; padding: 20px; }
  main { position: relative; }
  #network { width: 100%; height: 100%; background: var(--bg); }
  h1 { font-size: 18px; margin: 0 0 4px; }
  .subtitle { font-size: 12px; color: var(--muted); margin-bottom: 16px; line-height: 1.4; }
  h2 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 18px 0 8px; }
  .legend { display: flex; flex-direction: column; gap: 6px; }
  .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer; padding: 4px 6px; border-radius: 4px; }
  .legend-item:hover { background: #f1f5f9; }
  .legend-item.disabled { opacity: 0.35; }
  .swatch { width: 14px; height: 14px; border-radius: 3px; flex: 0 0 14px; border: 1px solid rgba(0,0,0,0.1); }
  .swatch-border { background: #f8fafc; }
  button.reset { width: 100%; padding: 8px; margin-top: 14px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; }
  button.reset:hover { background: #6d28d9; }
  .controls { display: flex; gap: 6px; margin-top: 8px; }
  .controls button { flex: 1; padding: 6px; font-size: 11px; background: #f1f5f9; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; }
  .controls button:hover { background: #e2e8f0; }
  .info-panel { position: absolute; top: 16px; right: 16px; background: var(--panel); padding: 14px 16px; border-radius: 8px; border: 1px solid var(--border); box-shadow: 0 4px 12px rgba(15,23,42,0.08); max-width: 320px; font-size: 13px; line-height: 1.5; display: none; }
  .info-panel.visible { display: block; }
  .info-panel h3 { margin: 0 0 6px; font-size: 14px; }
  .info-panel .meta { color: var(--muted); font-size: 11px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
  .info-panel .conn { font-size: 12px; margin-top: 8px; }
  .info-panel .conn strong { display: block; margin-bottom: 4px; }
  .info-panel ul { margin: 4px 0 0; padding-left: 18px; }
  .info-panel li { margin: 2px 0; }
  .badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 10px; background: #e2e8f0; color: var(--text); margin-left: 4px; }
  .stat { font-size: 11px; color: var(--muted); margin-top: 4px; }
  .legend-controls { display: flex; gap: 4px; margin-bottom: 6px; }
  .legend-controls a { font-size: 10px; color: var(--accent); cursor: pointer; text-decoration: underline; }
  footer-note { font-size: 11px; color: var(--muted); margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); display: block; line-height: 1.4; }
  @media (max-width: 720px) {
    #app { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
    aside { max-height: 40vh; }
  }
</style>
</head>
<body>
<div id="app">
  <aside>
    <h1>EA Organization Map</h1>
    <div class="subtitle">Effective Altruism funders &amp; recipients. Edges colored by funder. Knowledge cutoff: May 2025.</div>

    <h2>Funders <span class="badge" id="funder-count"></span></h2>
    <div class="legend-controls"><a id="funder-all">all</a> · <a id="funder-none">none</a></div>
    <div class="legend" id="funder-legend"></div>

    <h2>Cause Areas <span class="badge" id="cause-count"></span></h2>
    <div class="legend-controls"><a id="cause-all">all</a> · <a id="cause-none">none</a></div>
    <div class="legend" id="cause-legend"></div>

    <button class="reset" id="reset">Reset View</button>
    <div class="controls">
      <button id="physics-toggle">Pause physics</button>
      <button id="fit">Fit to view</button>
    </div>

    <footer-note>
      Edges: solid &amp; thick = primary funder; dashed &amp; thin = secondary / smaller grants. Hover any node for details. Source data &amp; mermaid versions in the <a href="https://github.com/" target="_blank" rel="noopener" id="repo-link">repo</a>.
    </footer-note>
  </aside>
  <main>
    <div id="network"></div>
    <div class="info-panel" id="info-panel">
      <h3 id="info-title"></h3>
      <div class="meta" id="info-meta"></div>
      <div class="conn" id="info-conn"></div>
    </div>
  </main>
</div>

<script>
const NODES = __NODES__;
const EDGES = __EDGES__;
const FUNDERS = __FUNDERS__;
const CAUSES = __CAUSES__;

// State
const activeFunders = new Set(FUNDERS.map(f => f.id));
const activeCauses = new Set(CAUSES.map(c => c.id));
activeCauses.add('funder'); // always show funder nodes

// ---- Build legend ----
function buildLegend(containerId, items, activeSet) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  items.forEach(item => {
    const row = document.createElement('div');
    row.className = 'legend-item';
    row.dataset.id = item.id;
    row.innerHTML = `<span class="swatch" style="background:${item.color}"></span><span>${item.label}</span>`;
    row.addEventListener('click', () => {
      if (activeSet.has(item.id)) { activeSet.delete(item.id); row.classList.add('disabled'); }
      else { activeSet.add(item.id); row.classList.remove('disabled'); }
      applyFilters();
    });
    container.appendChild(row);
  });
}
buildLegend('funder-legend', FUNDERS, activeFunders);
buildLegend('cause-legend', CAUSES, activeCauses);
document.getElementById('funder-count').textContent = FUNDERS.length;
document.getElementById('cause-count').textContent = CAUSES.length;

// "all" / "none" controls
function setAll(set, items, on, containerId) {
  set.clear();
  if (on) items.forEach(i => set.add(i.id));
  document.querySelectorAll(`#${containerId} .legend-item`).forEach(el => {
    if (on) el.classList.remove('disabled');
    else el.classList.add('disabled');
  });
  if (containerId === 'cause-legend') set.add('funder');
  applyFilters();
}
document.getElementById('funder-all').onclick = () => setAll(activeFunders, FUNDERS, true, 'funder-legend');
document.getElementById('funder-none').onclick = () => setAll(activeFunders, FUNDERS, false, 'funder-legend');
document.getElementById('cause-all').onclick = () => setAll(activeCauses, CAUSES, true, 'cause-legend');
document.getElementById('cause-none').onclick = () => setAll(activeCauses, CAUSES, false, 'cause-legend');

// ---- Build network ----
const nodesDataSet = new vis.DataSet(NODES);
const edgesDataSet = new vis.DataSet(EDGES);
const network = new vis.Network(
  document.getElementById('network'),
  { nodes: nodesDataSet, edges: edgesDataSet },
  {
    physics: {
      barnesHut: { gravitationalConstant: -8000, springLength: 180, springConstant: 0.02, damping: 0.4 },
      stabilization: { iterations: 200 },
    },
    interaction: { hover: true, tooltipDelay: 200, navigationButtons: false, keyboard: true },
    nodes: { margin: 10, widthConstraint: { maximum: 200 } },
    edges: { selectionWidth: 2 },
  }
);

function applyFilters() {
  // Show node if it's a funder in activeFunders OR a recipient in activeCauses
  const visibleNodeIds = new Set();
  NODES.forEach(n => {
    if (n.category === 'funder') {
      if (activeFunders.has(n.id)) visibleNodeIds.add(n.id);
    } else {
      if (activeCauses.has(n.category)) visibleNodeIds.add(n.id);
    }
  });
  // Hide via opacity / hidden flag
  nodesDataSet.update(NODES.map(n => ({ id: n.id, hidden: !visibleNodeIds.has(n.id) })));
  edgesDataSet.update(EDGES.map(e => ({
    id: e.id,
    hidden: !(visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to) && activeFunders.has(e.funder)),
  })));
}

// ---- Info panel on click ----
const infoPanel = document.getElementById('info-panel');
const infoTitle = document.getElementById('info-title');
const infoMeta = document.getElementById('info-meta');
const infoConn = document.getElementById('info-conn');

network.on('click', params => {
  if (params.nodes.length === 0) { infoPanel.classList.remove('visible'); return; }
  const id = params.nodes[0];
  const node = NODES.find(n => n.id === id);
  if (!node) return;
  infoTitle.textContent = node.label.replace(/\\n/g, ' ');
  if (node.category === 'funder') {
    infoMeta.textContent = 'Funder';
    const recipients = EDGES.filter(e => e.from === id).map(e => {
      const r = NODES.find(n => n.id === e.to);
      return r ? `<li>${r.label.replace(/\\n/g, ' ')} ${e.primary ? '' : '<span class="badge">secondary</span>'}</li>` : '';
    }).join('');
    infoConn.innerHTML = `<strong>Funds ${EDGES.filter(e => e.from === id).length} orgs:</strong><ul>${recipients}</ul>`;
  } else {
    infoMeta.textContent = node.categoryLabel || 'Recipient';
    const funders = EDGES.filter(e => e.to === id).map(e => {
      const f = NODES.find(n => n.id === e.from);
      return f ? `<li>${f.label.replace(/\\n/g, ' ')} ${e.primary ? '' : '<span class="badge">secondary</span>'}</li>` : '';
    }).join('');
    infoConn.innerHTML = `<strong>Funded by ${EDGES.filter(e => e.to === id).length} sources:</strong><ul>${funders}</ul>`;
  }
  infoPanel.classList.add('visible');
});

// ---- Controls ----
let physicsOn = true;
document.getElementById('physics-toggle').onclick = (e) => {
  physicsOn = !physicsOn;
  network.setOptions({ physics: { enabled: physicsOn } });
  e.target.textContent = physicsOn ? 'Pause physics' : 'Resume physics';
};
document.getElementById('fit').onclick = () => network.fit({ animation: true });
document.getElementById('reset').onclick = () => {
  setAll(activeFunders, FUNDERS, true, 'funder-legend');
  setAll(activeCauses, CAUSES, true, 'cause-legend');
  network.fit({ animation: true });
  infoPanel.classList.remove('visible');
};

// Update repo link if hosted on github.io
const host = location.hostname;
if (host.endsWith('.github.io')) {
  const user = host.split('.')[0];
  const repo = location.pathname.split('/')[1] || 'ea-organization-map';
  document.getElementById('repo-link').href = `https://github.com/${user}/${repo}`;
}
</script>
</body>
</html>
"""

# Inject data
html_out = (
    HTML.replace("__NODES__", json.dumps(vis_nodes))
        .replace("__EDGES__", json.dumps(vis_edges))
        .replace("__FUNDERS__", json.dumps(funder_filter_data))
        .replace("__CAUSES__", json.dumps(cause_filter_data))
)

OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "index.html",
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Wrote {OUT}")
print(f"  nodes: {len(vis_nodes)}")
print(f"  edges: {len(vis_edges)}")
print(f"  funders: {len(funder_filter_data)}")
print(f"  cause areas: {len(cause_filter_data)}")
