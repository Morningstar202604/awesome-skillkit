# Sync the main branch (+ tags) to all distribution platforms.
# Platforms: GitCode (origin) + Gitee + GitHub
#
# Usage:
#   .\sync-mirrors.ps1              # push main + tags everywhere possible
#   .\sync-mirrors.ps1 -Branch dev  # push a different branch
#
# Credentials, tried in this order per platform:
#   1. env var override:  $env:GITEE_TOKEN / $env:GITHUB_TOKEN
#      (used transiently on the command line; NEVER stored on disk)
#   2. named remote whose credentials git already has
#      (Windows Credential Manager entries like git:https://gitee.com)
param(
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

function Push-To([string]$Label, [string]$UrlOrRemote) {
    Write-Host "==> pushing $Branch -> $Label" -ForegroundColor Cyan
    git push $UrlOrRemote "${Branch}:${Branch}"
    if ($LASTEXITCODE -ne 0) { throw "push to $Label failed (exit $LASTEXITCODE)" }
    git push $UrlOrRemote --tags 2>$null | Out-Null
}

Write-Host "=== awesome-skillkit mirror sync (gitcode + gitee + github) ===" -ForegroundColor Yellow

Push-To "origin (gitcode/badhope)" "origin"

if ($env:GITEE_TOKEN) {
    Push-To "gitee (token)" "https://badhope:$($env:GITEE_TOKEN)@gitee.com/badhope/awesome-skillkit.git"
}
elseif (git remote | Select-String -Quiet -Pattern "^gitee$") {
    Push-To "gitee (stored credentials)" "gitee"
}
else {
    Write-Host "-- skip gitee (no GITEE_TOKEN, no 'gitee' remote)" -ForegroundColor DarkYellow
}

if ($env:GITHUB_TOKEN) {
    Push-To "github (token)" "https://badhope:$($env:GITHUB_TOKEN)@github.com/badhope/awesome-skillkit.git"
}
elseif (git remote | Select-String -Quiet -Pattern "^github$") {
    Push-To "github (stored credentials)" "github"
}
else {
    Write-Host "-- skip github (no GITHUB_TOKEN, no 'github' remote)" -ForegroundColor DarkYellow
}

Write-Host "=== mirrors synced ===" -ForegroundColor Green
