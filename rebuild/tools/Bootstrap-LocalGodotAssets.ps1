# SPDX-License-Identifier: GPL-3.0-or-later
# Stages candidate Aquila/terrain meshes from a local BEA asset export into
# local-lab/rebuild-godot and refreshes manifest.json. Does not commit payloads.

[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$ExportRoot = '',
    [string]$PlayerSearch = 'aquila',
    [string]$TerrainSearch = 'ground',
    [switch]$Initialize
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
} else {
    $RepoRoot = [IO.Path]::GetFullPath($RepoRoot)
}

if ($Initialize) {
    & (Join-Path $PSScriptRoot 'Initialize-LocalGodotAssets.ps1') -RepoRoot $RepoRoot | Out-Null
}

$assetRoot = Join-Path $RepoRoot 'local-lab\rebuild-godot'
if (-not (Test-Path -LiteralPath $assetRoot)) {
    & (Join-Path $PSScriptRoot 'Initialize-LocalGodotAssets.ps1') -RepoRoot $RepoRoot | Out-Null
}

if ([string]::IsNullOrWhiteSpace($ExportRoot)) {
    $ExportRoot = Join-Path $RepoRoot 'local-lab\bea-assets\export'
}
$ExportRoot = [IO.Path]::GetFullPath($ExportRoot)

$meshRoots = @(
    (Join-Path $ExportRoot 'asset_export\loose_meshes'),
    (Join-Path $ExportRoot 'asset_export\embedded_meshes'),
    (Join-Path $ExportRoot 'material-package\rebuild-mesh\models')
) | Where-Object { Test-Path -LiteralPath $_ }

function Find-PreferredMesh {
    param(
        [string[]]$Roots,
        [string]$Needle,
        [string[]]$Extensions
    )

    foreach ($root in $Roots) {
        foreach ($ext in $Extensions) {
            $hit = Get-ChildItem -LiteralPath $root -Recurse -File -Filter "*$ext" -ErrorAction SilentlyContinue |
                Where-Object { $_.BaseName -match $Needle } |
                Select-Object -First 1
            if ($hit) {
                return $hit
            }
        }
    }

    foreach ($root in $Roots) {
        foreach ($ext in $Extensions) {
            $hit = Get-ChildItem -LiteralPath $root -Recurse -File -Filter "*$ext" -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($hit) {
                return $hit
            }
        }
    }

    return $null
}

$preferredExt = @('.glb', '.gltf', '.obj', '.fbx')
$playerHit = Find-PreferredMesh -Roots $meshRoots -Needle $PlayerSearch -Extensions $preferredExt
$terrainHit = Find-PreferredMesh -Roots $meshRoots -Needle $TerrainSearch -Extensions $preferredExt

$playerDestDir = Join-Path $assetRoot 'player\aquila'
$terrainDestDir = Join-Path $assetRoot 'terrain\subset'
$stagingDir = Join-Path $assetRoot 'staging\from-export'
New-Item -ItemType Directory -Force -Path $playerDestDir, $terrainDestDir, $stagingDir | Out-Null

$playerRelative = $null
$terrainRelative = $null

if ($playerHit) {
    $destName = 'aquila' + $playerHit.Extension.ToLowerInvariant()
    $dest = Join-Path $playerDestDir $destName
    Copy-Item -LiteralPath $playerHit.FullName -Destination $dest -Force
    Copy-Item -LiteralPath $playerHit.FullName -Destination (Join-Path $stagingDir $playerHit.Name) -Force
    $playerRelative = "player/aquila/$destName"
    Write-Host "Staged player mesh: $($playerHit.FullName) -> $dest"
}

if ($terrainHit) {
    $destName = 'ground' + $terrainHit.Extension.ToLowerInvariant()
    $dest = Join-Path $terrainDestDir $destName
    Copy-Item -LiteralPath $terrainHit.FullName -Destination $dest -Force
    Copy-Item -LiteralPath $terrainHit.FullName -Destination (Join-Path $stagingDir $terrainHit.Name) -Force
    $terrainRelative = "terrain/subset/$destName"
    Write-Host "Staged terrain mesh: $($terrainHit.FullName) -> $dest"
}

if (-not $playerRelative -and -not $terrainRelative) {
    Write-Warning "No export meshes found under $ExportRoot. Workspace initialized; place .glb/.gltf/.obj manually."
}

$manifest = [ordered]@{
    schemaVersion = 'onslaught-rebuild-local-godot-assets-manifest.v1'
    presentationMode = 'local-retail-preview'
    nonParityClaim = $true
}

if ($playerRelative) {
    $manifest.player = [ordered]@{
        mesh = $playerRelative
        scale = 1.0
        yawDegrees = 0.0
        yOffsetMeters = 0.0
    }
}

if ($terrainRelative) {
    $manifest.terrain = [ordered]@{
        mesh = $terrainRelative
        scale = 1.0
        yawDegrees = 0.0
        yOffsetMeters = 0.0
    }
}

$manifestPath = Join-Path $assetRoot 'manifest.json'
($manifest | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $manifestPath -Encoding utf8
Write-Host "Wrote $manifestPath"

if (($playerRelative -and $playerRelative.EndsWith('.fbx')) -or ($terrainRelative -and $terrainRelative.EndsWith('.fbx'))) {
    Write-Warning "FBX staged. First Flight runtime loads .glb/.gltf/.obj only; convert FBX before run:rebuild-godot:local."
}

Write-Output $assetRoot
