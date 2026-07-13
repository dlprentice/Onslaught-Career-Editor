# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [string]$AssetRoot = '',
    [string]$PlayerMesh = '',
    [string]$TerrainMesh = '',
    [string]$PlayerSearch = 'aquila',
    [string]$TerrainSearch = 'ground',
    [switch]$Initialize
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'LocalAssetWorkspace.psm1') -Force
$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if ([string]::IsNullOrWhiteSpace($AssetRoot)) { $AssetRoot = Join-Path $RepoRoot 'local-lab\rebuild-godot' }
$AssetRoot = [IO.Path]::GetFullPath($AssetRoot)
if ($Initialize) { & (Join-Path $PSScriptRoot 'Initialize-LocalGodotAssets.ps1') -AssetRoot $AssetRoot | Out-Null }
if (-not (Test-Path -LiteralPath $AssetRoot -PathType Container)) { throw "Initialize the exact local asset root first: $AssetRoot" }
$StageRoot = [IO.Path]::GetFullPath((Join-Path $AssetRoot 'staging\from-export'))
Assert-NoReparseTraversal -Path $StageRoot | Out-Null
if (-not (Test-Path -LiteralPath $StageRoot -PathType Container)) { throw "Converted staging root not found: $StageRoot" }

function Resolve-RoleMesh([string]$ExplicitPath, [string]$Needle, [string]$Role) {
    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        $candidate = if ([IO.Path]::IsPathFullyQualified($ExplicitPath)) { [IO.Path]::GetFullPath($ExplicitPath) } else { [IO.Path]::GetFullPath((Join-Path $StageRoot $ExplicitPath)) }
        if (-not $candidate.StartsWith($StageRoot.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "$Role mesh escapes staging/from-export: $candidate" }
        Assert-NoReparseTraversal -Path $candidate | Out-Null
        return Get-Item -LiteralPath $candidate
    }
    $allConverted = @(Get-ChildItem -LiteralPath $StageRoot -Recurse -File -ErrorAction Stop | Where-Object Extension -in @('.glb', '.obj'))
    if ($allConverted.Count -gt 1000) { throw 'Converted staging root exceeds the 1000-file search bound. Pass explicit role paths after reducing staging.' }
    $matches = @($allConverted | Where-Object BaseName -match $Needle)
    if ($matches.Count -eq 0) { throw "No converted GLB/OBJ candidate matched role '$Role'. Convert/stage FBX, then pass -${Role}Mesh explicitly." }
    if ($matches.Count -ne 1) { throw "Ambiguous $Role role: $($matches.Count) converted candidates matched. Pass -${Role}Mesh explicitly." }
    return $matches[0]
}

$player = Resolve-RoleMesh -ExplicitPath $PlayerMesh -Needle $PlayerSearch -Role 'Player'
$terrain = Resolve-RoleMesh -ExplicitPath $TerrainMesh -Needle $TerrainSearch -Role 'Terrain'
if ([string]::Equals($player.FullName, $terrain.FullName, [StringComparison]::OrdinalIgnoreCase)) { throw 'Player and terrain roles must resolve to distinct mesh files.' }
foreach ($mesh in @($player, $terrain)) {
    Assert-RegularSingleLinkFile -Path $mesh.FullName -Label 'converted role mesh' | Out-Null
    if ($mesh.Extension.ToLowerInvariant() -notin @('.glb', '.obj')) { throw "Manifest activation supports only converted GLB/OBJ: $($mesh.FullName)" }
}

$playerName = 'aquila' + $player.Extension.ToLowerInvariant()
$terrainName = 'ground' + $terrain.Extension.ToLowerInvariant()
$playerDest = Join-Path $AssetRoot "player\aquila\$playerName"
$terrainDest = Join-Path $AssetRoot "terrain\subset\$terrainName"
$manifestPath = Join-Path $AssetRoot 'manifest.json'
$destinations = @($playerDest, $terrainDest, $manifestPath)
Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $AssetRoot -ForbiddenRoots @((Join-Path $RepoRoot 'rebuild'), (Join-Path $RepoRoot 'references')) -DestinationPaths $destinations | Out-Null
$lease = $null
try {
    $lease = [Onslaught.DirectoryLeaseSet]::Open($RepoRoot, [string[]]@((Split-Path -Parent $playerDest), (Split-Path -Parent $terrainDest)))
    Copy-GuardedFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Source $player.FullName -Destination $playerDest
    Copy-GuardedFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Source $terrain.FullName -Destination $terrainDest
    $manifest = [ordered]@{
        schemaVersion = 'onslaught-rebuild-local-godot-assets-manifest.v1'; presentationMode = 'local-user-mesh-preview'; nonParityClaim = $true
        player = [ordered]@{ mesh = "player/aquila/$playerName"; scale = 1.0; yawDegrees = 0.0; yOffsetMeters = 0.0 }
        terrain = [ordered]@{ mesh = "terrain/subset/$terrainName"; scale = 1.0; yawDegrees = 0.0; yOffsetMeters = 0.0 }
    }
    Write-GuardedTextFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Destination $manifestPath -Content ($manifest | ConvertTo-Json -Depth 6)
}
finally {
    if ($null -ne $lease) { $lease.Dispose() }
}
Write-Host "Activated explicit local player and terrain roles in $manifestPath"
Write-Output $AssetRoot
