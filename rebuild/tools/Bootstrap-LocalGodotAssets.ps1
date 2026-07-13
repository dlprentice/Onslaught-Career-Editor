# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [string]$AssetRoot = '',
    [string]$PlayerMesh = '',
    [string]$TerrainMesh = '',
    [string]$PlayerSearch = 'aquila',
    [string]$TerrainSearch = 'ground',
    [switch]$Initialize,
    [switch]$InjectFailureAfterPlayerCopy
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

function Get-RoleReceipt([string]$Path) {
    $fileLease = [Onslaught.LocalFileLease]::OpenRead($Path)
    try {
        $hash = $fileLease.ComputeHash()
        $fileLease.Revalidate()
        return [pscustomobject]@{ Hash = $hash; Length = $fileLease.Length }
    }
    finally { $fileLease.Dispose() }
}

function Assert-VersionFile([string]$Path, [object]$Receipt, [string]$Label) {
    $fileLease = [Onslaught.LocalFileLease]::OpenRead($Path)
    try {
        if ($fileLease.Length -ne $Receipt.Length -or $fileLease.ComputeHash() -ne $Receipt.Hash) {
            throw "$Label version file does not match its held source receipt: $Path"
        }
        $fileLease.Revalidate()
    }
    finally { $fileLease.Dispose() }
}

$playerReceipt = Get-RoleReceipt $player.FullName
$terrainReceipt = Get-RoleReceipt $terrain.FullName
$playerExtension = $player.Extension.ToLowerInvariant()
$terrainExtension = $terrain.Extension.ToLowerInvariant()
$generationText = "onslaught-local-assets.v1`nplayer:$($playerReceipt.Hash):$playerExtension`nterrain:$($terrainReceipt.Hash):$terrainExtension"
$generationBytes = [Text.UTF8Encoding]::new($false).GetBytes($generationText)
$generationId = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($generationBytes)).ToLowerInvariant()
$generationRoot = Join-Path $AssetRoot "versions\$generationId"
$playerName = 'player' + $playerExtension
$terrainName = 'terrain' + $terrainExtension
$playerDest = Join-Path $generationRoot $playerName
$terrainDest = Join-Path $generationRoot $terrainName
$manifestPath = Join-Path $AssetRoot 'manifest.json'
$destinations = @($playerDest, $terrainDest, $manifestPath)
Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $AssetRoot -ForbiddenRoots @((Join-Path $RepoRoot 'rebuild'), (Join-Path $RepoRoot 'references')) -DestinationPaths $destinations | Out-Null
$lease = $null
try {
    $lease = [Onslaught.DirectoryLeaseSet]::Open($RepoRoot, [string[]]@($generationRoot))
    if (Test-Path -LiteralPath $playerDest -PathType Leaf) { Assert-VersionFile $playerDest $playerReceipt 'Player' }
    else { Copy-GuardedFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Source $player.FullName -Destination $playerDest -ExpectedSha256 $playerReceipt.Hash -ExpectedLength $playerReceipt.Length }
    Assert-VersionFile $playerDest $playerReceipt 'Player'
    if ($InjectFailureAfterPlayerCopy) { throw 'Injected failure after player copy.' }

    if (Test-Path -LiteralPath $terrainDest -PathType Leaf) { Assert-VersionFile $terrainDest $terrainReceipt 'Terrain' }
    else { Copy-GuardedFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Source $terrain.FullName -Destination $terrainDest -ExpectedSha256 $terrainReceipt.Hash -ExpectedLength $terrainReceipt.Length }
    Assert-VersionFile $terrainDest $terrainReceipt 'Terrain'
    $manifest = [ordered]@{
        schemaVersion = 'onslaught-rebuild-local-godot-assets-manifest.v1'; presentationMode = 'local-user-mesh-preview'; nonParityClaim = $true
        player = [ordered]@{ mesh = "versions/$generationId/$playerName"; scale = 1.0; yawDegrees = 0.0; yOffsetMeters = 0.0 }
        terrain = [ordered]@{ mesh = "versions/$generationId/$terrainName"; scale = 1.0; yawDegrees = 0.0; yOffsetMeters = 0.0 }
    }
    Write-GuardedTextFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Destination $manifestPath -Content ($manifest | ConvertTo-Json -Depth 6)
}
finally {
    if ($null -ne $lease) { $lease.Dispose() }
}
Write-Host "Activated explicit local player and terrain roles in $manifestPath"
Write-Output $AssetRoot
