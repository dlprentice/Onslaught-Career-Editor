# SPDX-License-Identifier: GPL-3.0-or-later
# Thin wrapper for BYO-game asset export into an ignored local-lab root.

[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [string]$GameRoot = '',
    [string]$OutRoot = '',
    [string]$ExtractorRuntimeDir = '',
    [string]$ExtractorRoot = '',
    [int]$LimitArchives = 0,
    [int]$LimitLooseTextures = 0,
    [int]$LimitLooseMeshes = 0,
    [int]$LimitEmbeddedBodies = 0,
    [switch]$SkipExisting
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
} else {
    $RepoRoot = [IO.Path]::GetFullPath($RepoRoot)
}

if ([string]::IsNullOrWhiteSpace($GameRoot)) {
    foreach ($candidate in @('game', 'local-game')) {
        $probe = Join-Path $RepoRoot $candidate
        if (Test-Path -LiteralPath (Join-Path $probe 'data\resources')) {
            $GameRoot = $probe
            break
        }
    }
}

if ([string]::IsNullOrWhiteSpace($GameRoot)) {
    throw "Provide -GameRoot or place a BYO install mirror at game/ or local-game/."
}

$GameRoot = [IO.Path]::GetFullPath($GameRoot)
if ([string]::IsNullOrWhiteSpace($OutRoot)) {
    $OutRoot = Join-Path $RepoRoot 'local-lab\bea-assets\export'
}
$OutRoot = [IO.Path]::GetFullPath($OutRoot)
New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

if ([string]::IsNullOrWhiteSpace($ExtractorRoot)) {
    $ExtractorRoot = Join-Path $RepoRoot 'references\AYAResourceExtractor'
}
if ([string]::IsNullOrWhiteSpace($ExtractorRuntimeDir)) {
    $ExtractorRuntimeDir = Join-Path $ExtractorRoot 'Code\AyaResourceExtractor\bin\Debug\net6.0-windows'
}

foreach ($dllName in @('AYAResourceExtractor.dll', 'DDSTextureUncompress.dll', 'Fbx.dll')) {
    $dllPath = Join-Path $ExtractorRuntimeDir $dllName
    if (-not (Test-Path -LiteralPath $dllPath)) {
        throw "Missing extractor runtime DLL '$dllName' under $ExtractorRuntimeDir. Build the AYA submodule or place prebuilt DLLs there."
    }
}

$exportScript = Join-Path $RepoRoot 'tools\export_game_assets.py'
if (-not (Test-Path -LiteralPath $exportScript)) {
    throw "Missing $exportScript"
}

$pyArgs = @(
    $exportScript,
    '--game-root', $GameRoot,
    '--out-root', $OutRoot,
    '--extractor-root', $ExtractorRoot,
    '--extractor-runtime-dir', $ExtractorRuntimeDir
)

if ($LimitArchives -gt 0) { $pyArgs += @('--limit-archives', "$LimitArchives") }
if ($LimitLooseTextures -gt 0) { $pyArgs += @('--limit-loose-textures', "$LimitLooseTextures") }
if ($LimitLooseMeshes -gt 0) { $pyArgs += @('--limit-loose-meshes', "$LimitLooseMeshes") }
if ($LimitEmbeddedBodies -gt 0) { $pyArgs += @('--limit-embedded-bodies', "$LimitEmbeddedBodies") }
if ($SkipExisting) { $pyArgs += '--skip-existing' }

Write-Host "Exporting BEA assets from $GameRoot -> $OutRoot"
& py -3 @pyArgs
if ($LASTEXITCODE -ne 0) {
    throw "export_game_assets.py failed with exit code $LASTEXITCODE"
}

Write-Output $OutRoot
