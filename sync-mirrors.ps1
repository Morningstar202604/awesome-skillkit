# Sync the main branch to all mirror platforms.
# Usage:
#   .\sync-mirrors.ps1              # push main to origin + github + gitee
#   .\sync-mirrors.ps1 -Branch dev  # push a different branch
#
# Credentials (recommended: set env vars before running; tokens are NOT stored):
#   $env:GITHUB_TOKEN = "..."   # weed33834
#   $env:GITEE_TOKEN  = "..."   # badhope
# Without env vars the script falls back to the named remotes, which use
# whatever credentials git already has configured (credential manager).
param(
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

function Push-To([string]$Label, [string]$UrlOrRemote) {
    Write-Host "==> pushing $Branch -> $Label" -ForegroundColor Cyan
    git push $UrlOrRemote "${Branch}:${Branch}"
    if ($LASTEXITCODE -ne 0) { throw "push to $Label failed (exit $LASTEXITCODE)" }
}

Write-Host "=== awesome-skillkit mirror sync ===" -ForegroundColor Yellow

Push-To "origin (gitcode/badhope)" "origin"

if ($env:GITHUB_TOKEN) {
    Push-To "github (weed33834)" "https://weed33834:$env:GITHUB_TOKEN@github.com/weed33834/awesome-skillkit.git"
} else {
    Push-To "github (weed33834)" "github"
}

if ($env:GITEE_TOKEN) {
    Push-To "gitee (badhope)" "https://badhope:$env:GITEE_TOKEN@gitee.com/badhope/awesome-skillkit.git"
} else {
    Push-To "gitee (badhope)" "gitee"
}

Write-Host "=== all mirrors synced ===" -ForegroundColor Green
