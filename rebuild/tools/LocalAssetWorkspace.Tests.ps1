# SPDX-License-Identifier: GPL-3.0-or-later

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'LocalAssetWorkspace.psm1') -Force

function Assert-Throws([scriptblock]$Action, [string]$Pattern) {
    try { & $Action; throw "Expected failure matching '$Pattern'." }
    catch { if ($_.Exception.Message -notmatch $Pattern) { throw } }
}

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$scratch = Join-Path $repoRoot ('local-lab\rebuild-godot\tests\' + [Guid]::NewGuid().ToString('N'))
$outside = Join-Path $repoRoot ('local-lab\rebuild-godot-tests\outside-' + [Guid]::NewGuid().ToString('N'))
try {
    [IO.Directory]::CreateDirectory($scratch) | Out-Null
    [IO.Directory]::CreateDirectory($outside) | Out-Null
    Assert-Throws { Assert-LocalAssetOutputRoot -RepoRoot $repoRoot -OutputRoot (Join-Path $repoRoot 'rebuild\bad') } 'local-lab'
    Assert-Throws { Assert-LocalAssetOutputRoot -RepoRoot $repoRoot -OutputRoot (Join-Path $repoRoot 'local-lab\rebuild-godot\..\escape') } 'escape|contain'

    $gameRoot = Join-Path $scratch 'game'
    [IO.Directory]::CreateDirectory($gameRoot) | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $gameRoot 'BEA.exe'), [byte[]](0x4d, 0x5a))
    Assert-Throws { Assert-LocalAssetWritePlan -RepoRoot $repoRoot -OutputRoot $gameRoot -ForbiddenRoots @($gameRoot) -DestinationPaths @() } 'overlap|game|source|local-lab'

    $target = Join-Path $outside 'target'
    [IO.Directory]::CreateDirectory($target) | Out-Null
    $junction = Join-Path $scratch 'junction'
    cmd /c "mklink /J `"$junction`" `"$target`"" | Out-Null
    Assert-Throws { Assert-NoReparseTraversal -Path (Join-Path $junction 'child') -AllowMissingLeaf } 'reparse'

    $fileTarget = Join-Path $outside 'target.bin'
    $symlink = Join-Path $scratch 'symlink.bin'
    [IO.File]::WriteAllBytes($fileTarget, [byte[]](4, 5, 6))
    cmd /c "mklink `"$symlink`" `"$fileTarget`"" | Out-Null
    Assert-Throws { Assert-RegularSingleLinkFile -Path $symlink -Label 'symlink' } 'reparse'

    $source = Join-Path $scratch 'source.bin'
    $alias = Join-Path $scratch 'alias.bin'
    [IO.File]::WriteAllBytes($source, [byte[]](1, 2, 3))
    cmd /c "mklink /H `"$alias`" `"$source`"" | Out-Null
    Assert-Throws { Assert-RegularSingleLinkFile -Path $alias -Label 'destination' } 'hardlink|single link'

    $failedOut = Join-Path $scratch 'failed-export'
    $fakeGame = Join-Path $scratch 'trusted-game'
    [IO.Directory]::CreateDirectory((Join-Path $fakeGame 'data\resources')) | Out-Null
    Assert-Throws {
        & (Join-Path $PSScriptRoot 'Export-LocalBeaAssets.ps1') -RepoRoot $repoRoot -GameRoot $fakeGame -OutRoot $failedOut -ExtractorRoot (Join-Path $scratch 'missing-extractor')
    } 'does not exist|dependency|Path'
    if (Test-Path -LiteralPath $failedOut) { throw 'Export created output before dependency preflight completed.' }

    $assetRoot = Join-Path $scratch 'bootstrap'
    & (Join-Path $PSScriptRoot 'Initialize-LocalGodotAssets.ps1') -RepoRoot $repoRoot -AssetRoot $assetRoot | Out-Null
    $loose = Join-Path $assetRoot 'export\asset_export\loose_meshes'
    [IO.Directory]::CreateDirectory($loose) | Out-Null
    [IO.File]::WriteAllText((Join-Path $loose 'aquila-a.obj'), 'v 0 0 0')
    [IO.File]::WriteAllText((Join-Path $loose 'aquila-b.obj'), 'v 0 0 0')
    [IO.File]::WriteAllText((Join-Path $loose 'ground.obj'), 'v 0 0 0')
    Assert-Throws {
        & (Join-Path $PSScriptRoot 'Bootstrap-LocalGodotAssets.ps1') -RepoRoot $repoRoot -AssetRoot $assetRoot
    } 'Ambiguous Player role'
    if (Test-Path -LiteralPath (Join-Path $assetRoot 'manifest.json')) { throw 'Ambiguous bootstrap activated a manifest.' }
    Write-Host 'Local asset workspace safety tests passed.'
}
finally {
    if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force }
    if (Test-Path -LiteralPath $outside) { Remove-Item -LiteralPath $outside -Recurse -Force }
}
