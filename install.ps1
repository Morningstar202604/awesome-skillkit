# SkillKit one-click installer (Windows PowerShell)
# Usage: .\install.ps1 [target-dir]   (default: $HOME\.claude\skills)
# Note: if dist/ is empty, run build.py or bash build.sh first
param(
    [string]$Target = "$HOME\.claude\skills"
)

$HubDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir = Join-Path $HubDir "dist"

if (-not (Test-Path $SkillsDir)) {
    Write-Error "dist directory not found: $SkillsDir (run build.py or bash build.sh first)"
    exit 1
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
$count = 0

Get-ChildItem -Path $SkillsDir -Filter "*.zip" | ForEach-Object {
    $name = $_.BaseName
    $dest = Join-Path $Target $name
    Write-Host "installing $name -> $dest"
    Expand-Archive -Path $_.FullName -DestinationPath $dest -Force
    $count++
}

Write-Host "done: installed $count skill(s) to $Target"
Write-Host "Start a new session to use them."
