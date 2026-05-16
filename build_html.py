"""Generate a single-file interactive HTML network graph of EA funders & recipients."""

import json
import os
from build_canvas import FUNDERS, CAUSE_AREAS, EDGES
from funders_detail import FUNDER_PEOPLE

COLOR_HEX = {
    "1": "#dc2626",
    "2": "#ea580c",
    "3": "#ca8a04",
    "4": "#16a34a",
    "5": "#0891b2",
    "6": "#7c3aed",
}
def color_to_hex(c):
    if not c:
        return "#475569"
    return c if c.startswith("#") else COLOR_HEX.get(c, "#475569")

vis_nodes = []
vis_edges = []
funder_colors = {}

for fid, label, color in FUNDERS:
    hex_color = color_to_hex(color)
    funder_colors[fid] = hex_color
    vis_nodes.append({
        "id": fid,
        "label": label,
        "group": "funder",
        "color": {"background": hex_color, "border": "#0f172a"},
        "shape": "box",
        "font": {"color": "#fff", "size": 14, "face": "Inter, system-ui, sans-serif"},
        "borderWidth": 2,
        "category": "funder",
    })

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
        })

valid_ids = {n["id"] for n in vis_nodes}
edge_id = 0
for (src, dst, primary) in EDGES:
    if src not in valid_ids or dst not in valid_ids:
        continue
    edge_id += 1
    color = funder_colors.get(src, "#94a3b8")
    vis_edges.append({
        "id": "e" + str(edge_id),
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

funder_filter_data = [
    {"id": fid, "label": label.replace("\n", " - "), "color": color_to_hex(color)}
    for fid, label, color in FUNDERS
]

cause_filter_data = [
    {"id": k, "label": v["label"], "color": color_to_hex(v["color"])}
    for k, v in CAUSE_AREAS.items()
]

# Funder people data for the info panel
funder_people_data = {
    fid: {
        "donors": FUNDER_PEOPLE[fid].get("donors", []),
        "leads":  FUNDER_PEOPLE[fid].get("leads", []),
        "founded": FUNDER_PEOPLE[fid].get("founded"),
        "typical_volume": FUNDER_PEOPLE[fid].get("typical_volume"),
        "notes": FUNDER_PEOPLE[fid].get("notes"),
        "source_url": FUNDER_PEOPLE[fid].get("source_url"),
    }
    for fid in FUNDER_PEOPLE
}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>EA Organization Map - Funders & Recipients</title>
<meta name="description" content="Interactive map of Effective Altruism organizations and their funding relationships, as of May 2025." />
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/vis-network@9.1.9/styles/vis-network.min.css" />
<style>
  :root { color-scheme: light; --bg: #f8fafc; --panel: #ffffff; --border: #e2e8f0; --text: #0f172a; --muted: #64748b; --accent: #7c3aed; }
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
  button.reset { width: 100%; padding: 8px; margin-top: 14px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; }
  button.reset:hover { background: #6d28d9; }
  .controls { display: flex; gap: 6px; margin-top: 8px; }
  .controls button { flex: 1; padding: 6px; font-size: 11px; background: #f1f5f9; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; }
  .controls button:hover { background: #e2e8f0; }
  .info-panel { position: absolute; top: 16px; right: 16px; background: var(--panel); padding: 16px 18px; border-radius: 10px; border: 1px solid var(--border); box-shadow: 0 6px 18px rgba(15,23,42,0.10); max-width: 380px; font-size: 13px; line-height: 1.5; display: none; max-height: calc(100vh - 32px); overflow-y: auto; }
  .info-panel.visible { display: block; }
  .info-panel h3 { margin: 0 0 6px; font-size: 15px; }
  .info-panel .meta { color: var(--muted); font-size: 11px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
  .info-panel .section { margin-top: 10px; }
  .info-panel .section h4 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 0 0 4px; }
  .info-panel ul { margin: 4px 0 0; padding-left: 18px; }
  .info-panel li { margin: 2px 0; }
  .info-panel .scale { font-size: 11px; color: var(--muted); margin-top: 6px; padding: 6px 8px; background: #f1f5f9; border-radius: 4px; }
  .info-panel .note { font-size: 11px; color: var(--text); margin-top: 8px; padding: 6px 8px; background: #fef3c7; border-left: 3px solid #d97706; border-radius: 2px; font-style: italic; }
  .info-panel a { color: var(--accent); }
  .badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 10px; background: #e2e8f0; color: var(--text); margin-left: 4px; }
  .legend-controls { display: flex; gap: 4px; margin-bottom: 6px; }
  .legend-controls a { font-size: 10px; color: var(--accent); cursor: pointer; text-decoration: underline; }
  .footer-note { font-size: 11px; color: var(--muted); margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); line-height: 1.4; }
  @media (max-width: 720px) { #app { grid-template-columns: 1fr; grid-template-rows: auto 1fr; } aside { max-height: 40vh; } }
</style>
</head>
<body>
<div id="app">
  <aside>
    <h1>EA Organization Map</h1>
    <div class="subtitle">Effective Altruism funders &amp; recipients. Click any funder for the people behind it. Knowledge cutoff: May 2025.</div>

    <h2>Funders <span class="badge" id="funder-count"></span></h2>
    <div class="legend-controls"><a id="funder-all">all</a> &middot; <a id="funder-none">none</a></div>
    <div class="legend" id="funder-legend"></div>

    <h2>Cause Areas <span class="badge" id="cause-count"></span></h2>
    <div class="legend-controls"><a id="cause-all">all</a> &middot; <a id="cause-none">none</a></div>
    <div class="legend" id="cause-legend"></div>

    <button class="reset" id="reset">Reset View</button>
    <div class="controls">
      <button id="physics-toggle">Pause physics</button>
      <button id="fit">Fit to view</button>
    </div>

    <div class="footer-note">
      Edges colored by funder (solid = primary, faded = secondary). Click any node for details. Click a funder to see the people behind it.
    </div>
  </aside>
  <main>
    <div id="network"></div>
    <div class="info-panel" id="info-panel"></div>
  </main>
</div>

<script>
const NODES = __NODES__;
const EDGES = __EDGES__;
const FUNDERS = __FUNDERS__;
const CAUSES = __CAUSES__;
const PEOPLE = __PEOPLE__;

const activeFunders = new Set(FUNDERS.map(f => f.id));
const activeCauses = new Set(CAUSES.map(c => c.id));
activeCauses.add('funder');

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

function setAll(set, items, on, containerId) {
  set.clear();
  if (on) items.forEach(i => set.add(i.id));
  document.querySelectorAll(`#${containerId} .legend-item`).forEach(el => {
    if (on) el.classList.remove('disabled'); else el.classList.add('disabled');
  });
  if (containerId === 'cause-legend') set.add('funder');
  applyFilters();
}
document.getElementById('funder-all').onclick = () => setAll(activeFunders, FUNDERS, true, 'funder-legend');
document.getElementById('funder-none').onclick = () => setAll(activeFunders, FUNDERS, false, 'funder-legend');
document.getElementById('cause-all').onclick = () => setAll(activeCauses, CAUSES, true, 'cause-legend');
document.getElementById('cause-none').onclick = () => setAll(activeCauses, CAUSES, false, 'cause-legend');

const nodesDataSet = new vis.DataSet(NODES);
const edgesDataSet = new vis.DataSet(EDGES);
const network = new vis.Network(
  document.getElementById('network'),
  { nodes: nodesDataSet, edges: edgesDataSet },
  {
    physics: { barnesHut: { gravitationalConstant: -8000, springLength: 180, springConstant: 0.02, damping: 0.4 }, stabilization: { iterations: 200 } },
    interaction: { hover: true, tooltipDelay: 200, navigationButtons: false, keyboard: true },
    nodes: { margin: 10, widthConstraint: { maximum: 200 } },
    edges: { selectionWidth: 2 },
  }
);

function applyFilters() {
  const visibleNodeIds = new Set();
  NODES.forEach(n => {
    if (n.category === 'funder') { if (activeFunders.has(n.id)) visibleNodeIds.add(n.id); }
    else { if (activeCauses.has(n.category)) visibleNodeIds.add(n.id); }
  });
  nodesDataSet.update(NODES.map(n => ({ id: n.id, hidden: !visibleNodeIds.has(n.id) })));
  edgesDataSet.update(EDGES.map(e => ({ id: e.id, hidden: !(visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to) && activeFunders.has(e.funder)) })));
}

const infoPanel = document.getElementById('info-panel');

function escapeHtml(s) {
  return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function renderFunderInfo(node) {
  const id = node.id;
  const p = PEOPLE[id] || {};
  const recipients = EDGES.filter(e => e.from === id);
  const meta = [];
  if (p.founded) meta.push('Founded ' + p.founded);
  if (p.typical_volume) meta.push(p.typical_volume);
  meta.push('Funds ' + recipients.length + ' orgs');

  let html = `<h3>${escapeHtml(node.label.replace(/\\n/g, ' '))}</h3>`;
  html += `<div class="meta">${meta.map(escapeHtml).join(' &middot; ')}</div>`;

  if (p.donors && p.donors.length) {
    html += '<div class="section"><h4>Where the money comes from</h4><ul>';
    p.donors.forEach(d => {
      const src = d.source ? ` <span style="color:var(--muted);font-size:11px">— ${escapeHtml(d.source)}</span>` : '';
      html += `<li><strong>${escapeHtml(d.name)}</strong> <span style="color:var(--muted);font-size:11px">(${escapeHtml(d.role)})</span>${src}</li>`;
    });
    html += '</ul></div>';
  }

  if (p.leads && p.leads.length) {
    html += '<div class="section"><h4>Who decides what to fund</h4><ul>';
    p.leads.forEach(ld => {
      html += `<li><strong>${escapeHtml(ld.name)}</strong> <span style="color:var(--muted);font-size:11px">— ${escapeHtml(ld.role)}</span></li>`;
    });
    html += '</ul></div>';
  }

  if (recipients.length) {
    html += '<div class="section"><h4>Recipients (' + recipients.length + ')</h4><ul>';
    recipients.slice(0, 12).forEach(e => {
      const r = NODES.find(n => n.id === e.to);
      if (!r) return;
      const tag = e.primary ? '' : ' <span class="badge">secondary</span>';
      html += `<li>${escapeHtml(r.label.replace(/\\n/g, ' '))}${tag}</li>`;
    });
    if (recipients.length > 12) html += `<li style="color:var(--muted)">+ ${recipients.length - 12} more</li>`;
    html += '</ul></div>';
  }

  if (p.notes) html += `<div class="note">${escapeHtml(p.notes)}</div>`;
  if (p.source_url) html += `<div class="section" style="font-size:11px"><a href="${p.source_url}" target="_blank" rel="noopener">Source &rarr;</a></div>`;

  return html;
}

function renderRecipientInfo(node) {
  const id = node.id;
  const funders = EDGES.filter(e => e.to === id);
  let html = `<h3>${escapeHtml(node.label.replace(/\\n/g, ' '))}</h3>`;
  html += `<div class="meta">${escapeHtml(node.categoryLabel || 'Recipient')} &middot; Funded by ${funders.length} source(s)</div>`;
  html += '<div class="section"><h4>Funded by</h4><ul>';
  funders.forEach(e => {
    const f = NODES.find(n => n.id === e.from);
    if (!f) return;
    const tag = e.primary ? '' : ' <span class="badge">secondary</span>';
    html += `<li><strong>${escapeHtml(f.label.replace(/\\n/g, ' '))}</strong>${tag}</li>`;
  });
  html += '</ul></div>';
  return html;
}

network.on('click', params => {
  if (params.nodes.length === 0) { infoPanel.classList.remove('visible'); return; }
  const id = params.nodes[0];
  const node = NODES.find(n => n.id === id);
  if (!node) return;
  infoPanel.innerHTML = node.category === 'funder' ? renderFunderInfo(node) : renderRecipientInfo(node);
  infoPanel.classList.add('visible');
});

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
</script>
</body>
</html>
"""

html_out = (
    HTML.replace("__NODES__", json.dumps(vis_nodes))
        .replace("__EDGES__", json.dumps(vis_edges))
        .replace("__FUNDERS__", json.dumps(funder_filter_data))
        .replace("__CAUSES__", json.dumps(cause_filter_data))
        .replace("__PEOPLE__", json.dumps(funder_people_data))
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_out)

print("Wrote", OUT)
print("  nodes:", len(vis_nodes))
print("  edges:", len(vis_edges))
print("  funders w/ people:", len(funder_people_data))
