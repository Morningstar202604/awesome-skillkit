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
    # PS5.1 turns git's stderr progress into fake errors under EAP=Stop.
    # Merge streams at the process level via cmd so PS receives plain text.
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $out = (& cmd /c "git push $UrlOrRemote ${Branch}:${Branch} 2>&1") | Out-String
    $tagOut = (& cmd /c "git push $UrlOrRemote --tags 2>&1") | Out-String
    $ErrorActionPreference = $prevEap
    foreach ($line in (($out.TrimEnd() + "`n" + $tagOut.TrimEnd()) -split "`n")) {
        if ($line.Trim()) { Write-Host ("    " + $line.Trim()) }
    }
    if ($LASTEXITCODE -ne 0) { throw "push to $Label failed (exit $LASTEXITCODE)" }
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
    Push-To "github (token)" "https://Morningstar202604:$($env:GITHUB_TOKEN)@github.com/Morningstar202604/awesome-skillkit.git"
}
elseif (git remote | Select-String -Quiet -Pattern "^github$") {
    Push-To "github (stored credentials)" "github"
}
else {
    Write-Host "-- skip github (no GITHUB_TOKEN, no 'github' remote)" -ForegroundColor DarkYellow
}

Write-Host "=== mirrors synced ===" -ForegroundColor Green
