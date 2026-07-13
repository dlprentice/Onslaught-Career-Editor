# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [string]$AssetRoot = '',
    [switch]$WriteExampleManifest
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'LocalAssetWorkspace.psm1') -Force

$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$layoutPath = Join-Path $RepoRoot 'rebuild\local-assets.layout.json'
Assert-RegularSingleLinkFile -Path $layoutPath -Label 'tracked layout contract' | Out-Null
$layoutInfo = Get-Item -LiteralPath $layoutPath
if ($layoutInfo.Length -gt 65536) { throw "Tracked layout contract is oversized: $layoutPath" }
$layout = Get-Content -LiteralPath $layoutPath -Raw | ConvertFrom-Json -Depth 8

if ([string]::IsNullOrWhiteSpace($AssetRoot)) { $AssetRoot = Join-Path $RepoRoot $layout.defaultRootRelativeToRepo }
$AssetRoot = [IO.Path]::GetFullPath($AssetRoot)
$readmePath = Join-Path $AssetRoot 'README.local.md'
$examplePath = Join-Path $AssetRoot 'manifest.example.json'
$destinations = @($readmePath)
if ($WriteExampleManifest) { $destinations += $examplePath }
Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $AssetRoot -ForbiddenRoots @((Join-Path $RepoRoot 'rebuild'), (Join-Path $RepoRoot 'references')) -DestinationPaths $destinations | Out-Null

$directories = @($AssetRoot) + @($layout.directories | ForEach-Object { Join-Path $AssetRoot ([string]$_) })
$lease = $null
try {
    $lease = [Onslaught.DirectoryLeaseSet]::Open($RepoRoot, [string[]]$directories)
    $readme = @'
# Local Godot rebuild assets (ignored)

This workspace is an optional user-supplied local presentation input. Keep any retail-derived files ignored and never treat them as simulation truth, redistribution material, or parity evidence.

- `export/` - trusted-local AYA export output
- `player/aquila/` - explicitly selected converted `.glb` or bounded `.obj`
- `terrain/subset/` - explicitly selected converted `.glb` or bounded `.obj`
- `staging/from-export/` - local staging only; FBX is never activated directly
- `manifest.json` - created only after unambiguous player and terrain roles are selected

Run `npm run run:rebuild-godot:local -- --LocalAssetsRoot <exact-root>` to opt in. Ordinary run and smoke commands stay synthetic.
'@
    Write-GuardedTextFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Destination $readmePath -Content $readme
    if ($WriteExampleManifest) {
        $example = $layout.manifestExample | ConvertTo-Json -Depth 6
        Write-GuardedTextFile -RepoRoot $RepoRoot -OutputRoot $AssetRoot -Destination $examplePath -Content $example
    }
}
finally {
    if ($null -ne $lease) { $lease.Dispose() }
}

Write-Host "Initialized ignored local Godot asset workspace: $AssetRoot"
Write-Output $AssetRoot
