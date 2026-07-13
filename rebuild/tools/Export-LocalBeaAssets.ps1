# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [string]$GameRoot = '', [string]$OutRoot = '',
    [string]$ExtractorRuntimeDir = '', [string]$ExtractorRoot = '',
    [int]$LimitArchives = 0, [int]$LimitLooseTextures = 0, [int]$LimitLooseMeshes = 0, [int]$LimitEmbeddedBodies = 0,
    [switch]$SkipExisting
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'LocalAssetWorkspace.psm1') -Force
$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if ([string]::IsNullOrWhiteSpace($GameRoot)) {
    foreach ($candidate in @('game', 'local-game')) { $probe = Join-Path $RepoRoot $candidate; if (Test-Path -LiteralPath (Join-Path $probe 'data\resources')) { $GameRoot = $probe; break } }
}
if ([string]::IsNullOrWhiteSpace($GameRoot)) { throw 'Provide -GameRoot or an ignored trusted canonical retail mirror at game/ or local-game/.' }
$GameRoot = [IO.Path]::GetFullPath($GameRoot)
Assert-NoReparseTraversal -Path $GameRoot | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $GameRoot 'data\resources') -PathType Container)) { throw "GameRoot lacks data/resources: $GameRoot" }

if ([string]::IsNullOrWhiteSpace($OutRoot)) { $OutRoot = Join-Path $RepoRoot 'local-lab\rebuild-godot\export' }
$OutRoot = [IO.Path]::GetFullPath($OutRoot)
if ([string]::IsNullOrWhiteSpace($ExtractorRoot)) { $ExtractorRoot = Join-Path $RepoRoot 'references\AYAResourceExtractor' }
$ExtractorRoot = [IO.Path]::GetFullPath($ExtractorRoot)
if ([string]::IsNullOrWhiteSpace($ExtractorRuntimeDir)) { $ExtractorRuntimeDir = Join-Path $ExtractorRoot 'Code\AyaResourceExtractor\bin\Debug\net6.0-windows' }
$ExtractorRuntimeDir = [IO.Path]::GetFullPath($ExtractorRuntimeDir)
$FbxTemplate = [IO.Path]::GetFullPath((Join-Path $ExtractorRoot 'BoxWithTextures.fbx'))
$exportScript = Join-Path $RepoRoot 'tools\export_game_assets.py'

Assert-NoReparseTraversal -Path $ExtractorRoot | Out-Null
if (-not $ExtractorRuntimeDir.StartsWith($ExtractorRoot.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'ExtractorRuntimeDir must stay under ExtractorRoot.' }
$dependencies = @(
    (Join-Path $ExtractorRuntimeDir 'AYAResourceExtractor.dll'),
    (Join-Path $ExtractorRuntimeDir 'DDSTextureUncompress.dll'),
    (Join-Path $ExtractorRuntimeDir 'Fbx.dll'),
    $FbxTemplate,
    $exportScript)
foreach ($dependency in $dependencies) { Assert-RegularSingleLinkFile -Path $dependency -Label 'trusted-local export dependency' | Out-Null }
Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $OutRoot -ForbiddenRoots @($GameRoot, (Join-Path $GameRoot 'BEA.exe'), $ExtractorRoot, (Join-Path $RepoRoot 'rebuild'), (Join-Path $RepoRoot 'tools')) -DestinationPaths @() | Out-Null
$lease = $null
$dependencyLeases = [Collections.Generic.List[IDisposable]]::new()
try {
    foreach ($dependency in $dependencies) { $dependencyLeases.Add([Onslaught.LocalFileLease]::OpenRead($dependency)) }
    $lease = [Onslaught.DirectoryLeaseSet]::Open($RepoRoot, [string[]]@($OutRoot))
    $pyArgs = @($exportScript, '--game-root', $GameRoot, '--out-root', $OutRoot, '--extractor-root', $ExtractorRoot, '--extractor-runtime-dir', $ExtractorRuntimeDir)
    if ($LimitArchives -gt 0) { $pyArgs += @('--limit-archives', "$LimitArchives") }
    if ($LimitLooseTextures -gt 0) { $pyArgs += @('--limit-loose-textures', "$LimitLooseTextures") }
    if ($LimitLooseMeshes -gt 0) { $pyArgs += @('--limit-loose-meshes', "$LimitLooseMeshes") }
    if ($LimitEmbeddedBodies -gt 0) { $pyArgs += @('--limit-embedded-bodies', "$LimitEmbeddedBodies") }
    if ($SkipExisting) { $pyArgs += '--skip-existing' }
    Write-Host "Exporting trusted canonical retail inputs into ignored local workspace: $OutRoot"
    & py -3 @pyArgs
    if ($LASTEXITCODE -ne 0) { throw "export_game_assets.py failed with exit code $LASTEXITCODE" }
    foreach ($dependencyLease in $dependencyLeases) { $dependencyLease.Revalidate() }
}
finally {
    if ($null -ne $lease) { $lease.Dispose() }
    for ($index = $dependencyLeases.Count - 1; $index -ge 0; $index--) { $dependencyLeases[$index].Dispose() }
}
Write-Output $OutRoot
