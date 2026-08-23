# Sync the main branch to both mirror platforms (GitCode + Gitee).
# Usage:
#   .\sync-mirrors.ps1              # push main to origin (gitcode) + gitee
#   .\sync-mirrors.ps1 -Branch dev  # push a different branch
#
# Credentials (recommended: set env vars before running; tokens are NOT stored):
#   $env:GITEE_TOKEN = "..."     # badhope
# Without env vars the script falls back to the named remote "gitee",
# which uses whatever credentials git already has configured.
param(
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

function Push-To([string]$Label, [string]$UrlOrRemote) {
    Write-Host "==> pushing $Branch -> $Label" -ForegroundColor Cyan
    git push $UrlOrRemote "${Branch}:${Branch}"
    if ($LASTEXITCODE -ne 0) { throw "push to $Label failed (exit $LASTEXITCODE)" }
}

Write-Host "=== awesome-skillkit mirror sync (gitcode + gitee) ===" -ForegroundColor Yellow

Push-To "origin (gitcode/badhope)" "origin"

if ($env:GITEE_TOKEN) {
    Push-To "gitee (badhope)" "https://badhope:$env:GITEE_TOKEN@gitee.com/badhope/awesome-skillkit.git"
} else {
    Push-To "gitee (badhope)" "gitee"
}

Write-Host "=== mirrors synced ===" -ForegroundColor Green
