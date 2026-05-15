#!/usr/bin/env bash
# Setup script — initializes git repo, creates GitHub repo, pushes, and enables Pages.
# Run from the project folder.
#
# Requires: git, and EITHER (a) GitHub CLI (`gh`) authenticated OR (b) manual repo creation.

set -euo pipefail

REPO_NAME="${1:-ea-organization-map}"
VISIBILITY="${2:-public}"

echo "==> Initializing git repo"
git init -b main >/dev/null
git add .
git commit -m "Initial commit: EA organization funding map

- index.html: interactive vis.js network graph (81 nodes, 125 edges)
- EA_funding_map.canvas: Obsidian Canvas view
- EA_funding_mindmap.mermaid: radial mindmap
- EA_funding_graph.mermaid: full cross-funding flowchart
- EA_AI_safety_deepdive.mermaid: AI safety subset with org genealogy
- build_canvas.py + build_html.py: regeneration scripts" >/dev/null

if command -v gh >/dev/null 2>&1; then
  echo "==> Found GitHub CLI — creating repo and pushing"
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
  echo "==> Enabling GitHub Pages on main branch root"
  USER=$(gh api user --jq .login)
  gh api -X POST "repos/$USER/$REPO_NAME/pages" -f "source[branch]=main" -f "source[path]=/" 2>/dev/null || true
  echo ""
  echo "Done. Site will be live in a minute or two at:"
  echo "  https://$USER.github.io/$REPO_NAME/"
else
  cat <<EOF

GitHub CLI (gh) not found. Manual steps:

1. Create a new $VISIBILITY repo at: https://github.com/new
   Name it: $REPO_NAME
   Do NOT initialize with README, .gitignore, or license.

2. Push from this folder (replace <USERNAME>):

   git remote add origin https://github.com/<USERNAME>/$REPO_NAME.git
   git push -u origin main

3. Enable Pages:
   Go to: https://github.com/<USERNAME>/$REPO_NAME/settings/pages
   Source: Deploy from a branch — Branch: main, Folder: / (root) — Save.

4. Visit: https://<USERNAME>.github.io/$REPO_NAME/
EOF
fi
