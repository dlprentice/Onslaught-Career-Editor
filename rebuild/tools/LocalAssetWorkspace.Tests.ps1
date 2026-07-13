# SPDX-License-Identifier: GPL-3.0-or-later

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'LocalAssetWorkspace.psm1') -Force

function Assert-Throws([scriptblock]$Action, [string]$Pattern) {
    $caught = $null
    try { & $Action } catch { $caught = $_ }
    if ($null -eq $caught) { throw "Action completed successfully; expected failure matching '$Pattern'." }
    if ($caught.Exception.Message -notmatch $Pattern) { throw $caught }
    $script:throwAssertions++
}

$script:throwAssertions = 0
$helperRejectedSuccess = $false
try { Assert-Throws { $null = 1 + 1 } 'expected-inner-pattern' }
catch { $helperRejectedSuccess = $_.Exception.Message -match 'Action completed successfully' }
if (-not $helperRejectedSuccess) { throw 'Assert-Throws self-test did not reject a successful action.' }

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$scratch = Join-Path $repoRoot ('local-lab\rebuild-godot\tests\' + [Guid]::NewGuid().ToString('N'))
$outside = Join-Path $repoRoot ('local-lab\rebuild-godot-tests\outside-' + [Guid]::NewGuid().ToString('N'))
try {
    [IO.Directory]::CreateDirectory($scratch) | Out-Null
    [IO.Directory]::CreateDirectory($outside) | Out-Null
    Assert-Throws { Assert-LocalAssetOutputRoot -RepoRoot $repoRoot -OutputRoot (Join-Path $repoRoot 'rebuild\bad') } 'local-lab'
    Assert-Throws { Assert-LocalAssetOutputRoot -RepoRoot $repoRoot -OutputRoot (Join-Path $repoRoot 'local-lab\rebuild-godot\..\escape') } 'escape|contain'
    Assert-Throws { Assert-LocalAssetOutputRoot -RepoRoot $scratch -OutputRoot (Join-Path $scratch 'local-lab\rebuild-godot') } 'checkout containing'
    Assert-Throws { Assert-NoReparseTraversal -Path '\\server\share\assets' -AllowMissingLeaf } 'UNC|device|local drive'
    Assert-Throws { Assert-NoReparseTraversal -Path '\\?\C:\local-lab\assets' -AllowMissingLeaf } 'UNC|device|local drive'

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
    $brokenSymlink = Join-Path $scratch 'broken-symlink.bin'
    cmd /c "mklink `"$brokenSymlink`" `"$(Join-Path $outside 'missing-target.bin')`"" | Out-Null
    Assert-Throws { Assert-NoReparseTraversal -Path $brokenSymlink -AllowMissingLeaf } 'reparse'

    $source = Join-Path $scratch 'source.bin'
    $alias = Join-Path $scratch 'alias.bin'
    [IO.File]::WriteAllBytes($source, [byte[]](1, 2, 3))
    cmd /c "mklink /H `"$alias`" `"$source`"" | Out-Null
    Assert-Throws { Assert-RegularSingleLinkFile -Path $alias -Label 'destination' } 'hardlink|single link'

    $sameFile = Join-Path $scratch 'same-file.bin'
    [IO.File]::WriteAllBytes($sameFile, [byte[]](7, 8, 9))
    Assert-Throws {
        Copy-GuardedFile -RepoRoot $repoRoot -OutputRoot $scratch -Source $sameFile -Destination $sameFile
    } 'same|alias|source.*destination'
    Assert-Throws {
        Copy-GuardedFile -RepoRoot $repoRoot -OutputRoot $scratch -Source $source -Destination $alias
    } 'hardlink|single link|alias'

    $failedOut = Join-Path $scratch 'failed-export'
    $fakeGame = Join-Path $scratch 'trusted-game'
    [IO.Directory]::CreateDirectory((Join-Path $fakeGame 'data\resources')) | Out-Null
    Assert-Throws {
        & (Join-Path $PSScriptRoot 'Export-LocalBeaAssets.ps1') -GameRoot $fakeGame -OutRoot $failedOut -ExtractorRoot (Join-Path $scratch 'missing-extractor')
    } 'does not exist|dependency|Path'
    if (Test-Path -LiteralPath $failedOut) { throw 'Export created output before dependency preflight completed.' }

    $handoffRoot = Join-Path $scratch 'handoff'
    & (Join-Path $PSScriptRoot 'Initialize-LocalGodotAssets.ps1') -AssetRoot $handoffRoot | Out-Null
    $handoffStage = Join-Path $handoffRoot 'staging\from-export'
    [IO.File]::WriteAllText((Join-Path $handoffStage 'aquila-player.obj'), "v 0 0 0`nv 1 0 0`nv 0 1 0`nf 1 2 3`n")
    [IO.File]::WriteAllText((Join-Path $handoffStage 'ground-terrain.obj'), "v 0 0 0`nv 1 0 0`nv 0 1 0`nf 1 2 3`n")
    & (Join-Path $PSScriptRoot 'Bootstrap-LocalGodotAssets.ps1') -AssetRoot $handoffRoot | Out-Null
    if (-not (Test-Path -LiteralPath (Join-Path $handoffRoot 'manifest.json') -PathType Leaf)) { throw 'Staged converted meshes did not activate a manifest.' }

    $assetRoot = Join-Path $scratch 'bootstrap'
    & (Join-Path $PSScriptRoot 'Initialize-LocalGodotAssets.ps1') -AssetRoot $assetRoot | Out-Null
    $loose = Join-Path $assetRoot 'staging\from-export'
    [IO.Directory]::CreateDirectory($loose) | Out-Null
    [IO.File]::WriteAllText((Join-Path $loose 'aquila-a.obj'), 'v 0 0 0')
    [IO.File]::WriteAllText((Join-Path $loose 'aquila-b.obj'), 'v 0 0 0')
    [IO.File]::WriteAllText((Join-Path $loose 'ground.obj'), 'v 0 0 0')
    Assert-Throws {
        & (Join-Path $PSScriptRoot 'Bootstrap-LocalGodotAssets.ps1') -AssetRoot $assetRoot
    } 'Ambiguous Player role'
    if (Test-Path -LiteralPath (Join-Path $assetRoot 'manifest.json')) { throw 'Ambiguous bootstrap activated a manifest.' }

    foreach ($scriptName in @('Initialize-LocalGodotAssets.ps1', 'Bootstrap-LocalGodotAssets.ps1', 'Export-LocalBeaAssets.ps1')) {
        if ((Get-Command (Join-Path $PSScriptRoot $scriptName)).Parameters.ContainsKey('RepoRoot')) { throw "$scriptName must pin RepoRoot to its own checkout." }
    }
    if ((Get-Command (Join-Path $PSScriptRoot 'Export-LocalBeaAssets.ps1')).Parameters.ContainsKey('FbxTemplate')) { throw 'Export must consume only ExtractorRoot\BoxWithTextures.fbx.' }
    $exportSource = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'Export-LocalBeaAssets.ps1'))
    $harnessSource = [IO.File]::ReadAllText((Join-Path $repoRoot 'tools\BeaAssetExportHarness\Program.cs'))
    if ($exportSource -notmatch "Join-Path [`$]ExtractorRoot 'BoxWithTextures[.]fbx'" -or
        $harnessSource -notmatch 'Path[.]Combine\(_extractorRoot, "BoxWithTextures[.]fbx"\)') {
        throw 'Export preflight and harness consumption must agree on ExtractorRoot\BoxWithTextures.fbx.'
    }
    Write-Host "Local asset workspace safety tests passed ($script:throwAssertions expected-failure assertions, staging activation, and pinned-template source contract)."
}
finally {
    if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force }
    if (Test-Path -LiteralPath $outside) { Remove-Item -LiteralPath $outside -Recurse -Force }
}
