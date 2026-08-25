# SkillKit one-click installer (Windows PowerShell)
# Usage: .\install.ps1 [target-dir]   (default: $HOME\.claude\skills)
# Note: if dist/ is empty, run build.py or bash build.sh first
param(
    [string]$Target = "$HOME\.claude\skills"
)

$HubDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $HubDir "dist"

if (-not (Test-Path -LiteralPath $DistDir)) {
    Write-Error "dist directory not found: $DistDir (run build.py or bash build.sh first)"
    exit 1
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
$packCount = 0

Get-ChildItem -LiteralPath $DistDir -Filter "*.zip" | ForEach-Object {
    $tmp = Join-Path $env:TEMP ("skillkit_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        Expand-Archive -LiteralPath $_.FullName -DestinationPath $tmp -Force
        # skills are flat at the zip root: <skill-name>/SKILL.md
        Get-ChildItem -LiteralPath $tmp -Directory | ForEach-Object {
            $dest = Join-Path $Target $_.Name
            if (Test-Path -LiteralPath $dest) {
                Remove-Item -LiteralPath $dest -Recurse -Force
            }
            Move-Item -LiteralPath $_.FullName -Destination $dest
        }
    }
    finally {
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
    }
    Write-Host "installed pack $($_.Name)"
    $packCount++
}

Write-Host ""
$discovered = @(Get-ChildItem -LiteralPath $Target -Recurse -Depth 1 -Filter "SKILL.md" -File)
Write-Host ("done: {0} pack(s) installed flat to {1}" -f $packCount, $Target)
Write-Host ("verify: {0} skill(s) discoverable at <target>\<skill-name>\SKILL.md" -f $discovered.Count)
if ($discovered.Count -eq 0) {
    Write-Warning "no SKILL.md found directly under skill folders - layout looks wrong"
    exit 2
}
Write-Host "Start a new session to use them."
