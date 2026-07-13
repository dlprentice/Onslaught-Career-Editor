# SPDX-License-Identifier: GPL-3.0-or-later
# Creates the ignored local-lab/rebuild-godot workspace for optional retail mesh preview.
# Does not extract game assets and never writes proprietary payloads into Git.

[CmdletBinding()]
param(
    [string]$RepoRoot = '',
    [switch]$WriteExampleManifest
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
} else {
    $RepoRoot = [IO.Path]::GetFullPath($RepoRoot)
}

$layoutPath = Join-Path $RepoRoot 'rebuild\local-assets.layout.json'
if (-not (Test-Path -LiteralPath $layoutPath)) {
    throw "Missing tracked layout contract: $layoutPath"
}

$layout = Get-Content -LiteralPath $layoutPath -Raw | ConvertFrom-Json
$root = Join-Path $RepoRoot $layout.defaultRootRelativeToRepo
$directories = @($layout.directories)

foreach ($relative in $directories) {
    $path = Join-Path $root $relative
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

$readmePath = Join-Path $root 'README.local.md'
$readme = @"
# Local Godot rebuild assets (ignored)

This folder is under ``local-lab/`` and must stay out of Git.

## Layout

- ``player/aquila/`` - Aquila mesh (``.glb`` / ``.gltf`` / ``.obj``) plus textures if needed
- ``terrain/subset/`` - one environment/terrain subset mesh
- ``staging/from-export/`` - optional copies from ``export_game_assets.py`` output
- ``import/`` - optional Godot editor import scratch
- ``manifest.json`` - tells First Flight which meshes to load

## Bootstrap

1. Mirror a BYO game install under ``game/`` or ``local-game/``.
2. Build or place AYA extractor DLLs under ``references/AYAResourceExtractor/.../bin/Debug/net6.0-windows/``.
3. Run ``npm run export:local-bea-assets`` (or the PowerShell wrapper) into ``local-lab/bea-assets/export``.
4. Run ``npm run bootstrap:rebuild-godot-assets`` to stage candidate meshes and write ``manifest.json``.
5. Convert staged ``.fbx`` to ``.glb``/``.obj`` if needed, then ``npm run run:rebuild-godot:local``.

Smoke mode always keeps procedural synthetics. Local meshes are a non-parity preview only.
"@
Set-Content -LiteralPath $readmePath -Value $readme -Encoding utf8

$manifestPath = Join-Path $root 'manifest.json'
if ($WriteExampleManifest -or -not (Test-Path -LiteralPath $manifestPath)) {
    $example = @{
        schemaVersion = 'onslaught-rebuild-local-godot-assets-manifest.v1'
        presentationMode = 'local-retail-preview'
        nonParityClaim = $true
        player = @{
            mesh = 'player/aquila/aquila.glb'
            scale = 1.0
            yawDegrees = 0.0
            yOffsetMeters = 0.0
        }
        terrain = @{
            mesh = 'terrain/subset/ground.glb'
            scale = 1.0
            yawDegrees = 0.0
            yOffsetMeters = 0.0
        }
    }
    $example | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

Write-Host "Initialized local Godot asset workspace: $root"
Write-Output $root
