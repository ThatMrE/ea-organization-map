# Setup script — initializes git repo, creates GitHub repo, pushes, and enables Pages.
# Run in PowerShell from the project folder (C:\Users\ercre\Documents\ea-organization-map).
#
# Requires: git, and EITHER (a) GitHub CLI (`gh`) authenticated OR (b) manual repo creation.
#
# Usage:
#   .\setup-github.ps1                # uses `gh` if available, else prints manual steps
#   .\setup-github.ps1 -RepoName foo  # override repo name

param(
    [string]$RepoName = "ea-organization-map",
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Initializing git repo" -ForegroundColor Cyan
git init -b main | Out-Null
git add .
git commit -m "Initial commit: EA organization funding map

- index.html: interactive vis.js network graph (81 nodes, 125 edges)
- EA_funding_map.canvas: Obsidian Canvas view
- EA_funding_mindmap.mermaid: radial mindmap
- EA_funding_graph.mermaid: full cross-funding flowchart
- EA_AI_safety_deepdive.mermaid: AI safety subset with org genealogy
- build_canvas.py + build_html.py: regeneration scripts" | Out-Null

$ghAvailable = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)

if ($ghAvailable) {
    Write-Host "==> Found GitHub CLI — creating repo and pushing" -ForegroundColor Cyan
    gh repo create $RepoName --$Visibility --source=. --remote=origin --push
    Write-Host "==> Enabling GitHub Pages on main branch root" -ForegroundColor Cyan
    $user = (gh api user --jq .login).Trim()
    gh api -X POST "repos/$user/$RepoName/pages" -f "source[branch]=main" -f "source[path]=/" 2>$null
    Start-Sleep -Seconds 2
    Write-Host ""
    Write-Host "Done. Site will be live in a minute or two at:" -ForegroundColor Green
    Write-Host "  https://$user.github.io/$RepoName/" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "GitHub CLI (gh) not found. Manual steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Create a new public repo at: https://github.com/new"
    Write-Host "   Name it: $RepoName"
    Write-Host "   Do NOT initialize with README, .gitignore, or license."
    Write-Host ""
    Write-Host "2. Push from this folder (replace <USERNAME>):"
    Write-Host ""
    Write-Host "   git remote add origin https://github.com/<USERNAME>/$RepoName.git" -ForegroundColor Cyan
    Write-Host "   git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Enable Pages:"
    Write-Host "   Go to: https://github.com/<USERNAME>/$RepoName/settings/pages"
    Write-Host "   Source: Deploy from a branch — Branch: main, Folder: / (root) — Save."
    Write-Host ""
    Write-Host "4. Visit: https://<USERNAME>.github.io/$RepoName/"
}
