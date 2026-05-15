# EA Organization Map

An interactive map of Effective Altruism organizations and their funding relationships, as of May 2025.

![Preview of the EA funding map — funders on the left, recipients clustered by cause area on the right, edges colored by funder](preview.png)

**Live site:** _Enable GitHub Pages (Settings → Pages → main branch / root) to get a URL like `https://<username>.github.io/ea-organization-map/`._

## What's in here

| File | Format | Description |
|---|---|---|
| `index.html` | Interactive HTML | Click nodes for details, filter by funder or cause area, drag to rearrange. Loads vis-network from CDN. |
| `EA_funding_map.canvas` | Obsidian Canvas | Drop into an Obsidian vault and open as a visual canvas. |
| `EA_funding_mindmap.mermaid` | Mermaid mindmap | Radial mindmap, funders → cause areas → orgs. |
| `EA_funding_graph.mermaid` | Mermaid flowchart | Full cross-funding network — shows where multiple funders back the same org. |
| `EA_AI_safety_deepdive.mermaid` | Mermaid flowchart | AI safety / alignment subset with founders, dates, and org genealogy. |
| `build_canvas.py` | Python script | Source of truth for nodes & edges. Regenerates the `.canvas` file. |
| `build_html.py` | Python script | Generates `index.html` from the same data. |

To regenerate after edits to `build_canvas.py`:

```bash
python3 build_canvas.py && python3 build_html.py
```

## Scope

- **Funders** (17): Open Philanthropy, SFF, EA Funds (LTFF / EAIF / AWF / GHDF), FTX Future Fund (defunct 2022), Longview Philanthropy, GiveWell, Founders Pledge, Effective Ventures (sponsor), individual donors (Tallinn, Buterin, McCaleb), Macroscopic Ventures, Astera Institute, Schmidt Futures (adjacent), Charity Entrepreneurship / AIM.
- **Recipients** (~60): grouped into AI Safety & Alignment, Biosecurity & Pandemic Prevention, Global Health & Development, Animal Welfare, Movement Building & Meta, Policy & Governance, and Closed / Historical.
- **Edges** (125): primary funding relationships (solid) and secondary / smaller grants (dashed).

## Caveats

- Cross-funding is the norm — most major recipients (MIRI, Lightcone, CEA, Rethink Priorities, FLI, GovAI, ALLFED) receive money from several sources. Edges represent publicly known or widely reported flows; private grants are not captured.
- FTX Future Fund grants are historical — the entity dissolved in November 2022 and many grants were subject to bankruptcy clawback.
- FHI Oxford closed April 2024 and is shown under Closed / Historical.
- Schmidt Futures, Astera, and Collison-funded orgs are **EA-adjacent** rather than core EA.
- Anthropic is a for-profit AI lab; it appears because Open Phil made a foundational investment and Alameda invested ~$500M (later sold by the bankruptcy estate). It is not an EA org per se.

## License

CC BY 4.0 — free to share and adapt with attribution.
