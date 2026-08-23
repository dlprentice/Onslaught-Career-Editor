# SPDX-License-Identifier: GPL-3.0-or-later
#
# Record-PlaySession.ps1 - P8 stage 2 procedure owner (DRAFTED on stage 1).
#
# PURPOSE
#   The documented, repeatable procedure for producing a genuine HUMAN replay
#   tape: launch the rebuild with an explicit --record-tape=<path>, play the
#   session by hand, quit to the main menu (or close the window), and verify
#   the finalized tape with OnslaughtRebuild.Headless --expect.
#
#   STAGE 1 STATUS: this card drafts and documents the procedure only. It has
#   NOT been executed against a live native session - no run of this script
#   happened on P8 stage 1, per card scope ("no real/native session"). The
#   serialized native card owns the first genuine human tape.
#
# USAGE (once stage 2 lands)
#   pwsh -NoLogo -NoProfile -File rebuild\tools\Record-PlaySession.ps1 `
#       -TapePath "$env:LOCALAPPDATA\OnslaughtToolkit\recordings\my-session.tape.json" `
#       [-Offline]
#
# SAFETY CONTRACT
#   - The tape path must be absolute and is created with create-new /
#     no-overwrite semantics (TapeFile.WriteNew): an existing file is refused,
#     never overwritten.
#   - Career saves (.bes) and retail install paths are NEVER touched: this
#     script independently rejects a TapePath equal to or under the supplied
#     GameRoot (or a Steam auto-detection-resolved one), and under any
#     existing retail-install-shaped ancestor (BEA.exe beside a data folder),
#     BEFORE build, media materialization, or engine launch. The engine-side
#     TapeFile boundary is a second layer, not a substitute.
#   - The recorded seed is always the build's fixed SimulationSeed, so a
#     recorded tape replays deterministically.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TapePath,
    [switch]$Offline,
    [string]$GameRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not [IO.Path]::IsPathFullyQualified($TapePath)) {
    throw "--record-tape requires an ABSOLUTE path (the game refuses relative paths)."
}
if ([IO.Path]::GetExtension($TapePath) -ine '.json') {
    throw "Command tapes require a .json destination; career saves and retail files are invalid destinations."
}
if (Test-Path -LiteralPath $TapePath) {
    throw "Refusing to overwrite existing command tape destination: $TapePath"
}

# Independent destination boundary (defense in depth against the engine-side
# TapeFile.WriteNew policy): refuse a TapePath at or under the game root
# before anything is built, materialized, or launched.
function Test-PathAtOrUnder([string]$CandidateRoot, [string]$TargetPath) {
    $root = [IO.Path]::GetFullPath($CandidateRoot).TrimEnd('\', '/')
    if ([string]::IsNullOrEmpty($root)) { return $false }
    $targetDir = [IO.Path]::GetFullPath($TargetPath)
    $targetDir = [IO.Path]::GetDirectoryName($targetDir)
    if ([string]::IsNullOrEmpty($targetDir)) { return $false }
    $targetDir = $targetDir.TrimEnd('\', '/')
    return (
        $targetDir -ieq $root -or
        $targetDir -ieq [IO.Path]::GetFullPath($TargetPath).TrimEnd('\', '/') -or
        $targetDir.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase) -or
        $targetDir.StartsWith($root + '/', [StringComparison]::OrdinalIgnoreCase)
    )
}

# Mirror of materialize_retail_assets.py _resolve_game_root: when no explicit
# root was supplied, resolve the same Steam candidates so auto-detection is
# guarded too.
function Get-ResolvedRetailRoots([string]$ExplicitGameRoot) {
    $roots = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($ExplicitGameRoot)) {
        $roots.Add($ExplicitGameRoot)
        return ,$roots.ToArray()
    }

    $steamParents = New-Object System.Collections.Generic.List[string]
    try {
        foreach ($keyPath in @(
            'HKCU:\Software\Valve\Steam',
            'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam'
        )) {
            if (Test-Path $keyPath) {
                $item = Get-ItemProperty -Path $keyPath -ErrorAction SilentlyContinue
                $value = if ($keyPath -like 'HKCU:*') { $item.SteamPath } else { $item.InstallPath }
                if (-not [string]::IsNullOrWhiteSpace($value)) {
                    $steamParents.Add($value)
                }
            }
        }
    } catch {
        # Registry unreadable: fall through to the literal library list.
    }

    foreach ($literal in @('D:\Steam', 'D:\SteamLibrary', 'E:\Steam', 'E:\SteamLibrary')) {
        $steamParents.Add($literal)
    }

    foreach ($parent in $steamParents) {
        $roots.Add((Join-Path $parent 'steamapps\common\Battle Engine Aquila'))
    }
    return ,$roots.ToArray()
}

# Existing-ancestor shape probe: BEA.exe directly beside a data directory
# marks a retail install even when no explicit root was supplied.
function Test-UnderRetailInstallShape([string]$TargetPath) {
    $shapeCursor = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($TargetPath))
    while (-not [string]::IsNullOrEmpty($shapeCursor)) {
        if ((Test-Path -LiteralPath (Join-Path $shapeCursor 'BEA.exe') -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $shapeCursor 'data') -PathType Container)) {
            return $shapeCursor
        }
        $parent = [IO.Path]::GetDirectoryName($shapeCursor)
        if ($parent -eq $shapeCursor) { break }
        $shapeCursor = $parent
    }
    return $null
}

foreach ($candidateRoot in (Get-ResolvedRetailRoots $GameRoot)) {
    if (Test-PathAtOrUnder $candidateRoot $TapePath) {
        throw ("Refusing command tape destination '$TapePath': it lies at or under " +
            "game root '$candidateRoot'. Career saves and retail installs are never valid recording targets.")
    }
}

$shapedAncestor = Test-UnderRetailInstallShape $TapePath
if (-not [string]::IsNullOrEmpty($shapedAncestor)) {
    throw ("Refusing command tape destination '$TapePath': ancestor '$shapedAncestor' has the " +
        "retail install layout (BEA.exe beside a data directory).")
}

$buildArguments = @{}
if ($Offline) { $buildArguments.Offline = $true }
if (-not [string]::IsNullOrWhiteSpace($GameRoot)) { $buildArguments.GameRoot = $GameRoot }

$toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))

Write-Host "Recording session tape to: $TapePath"
Write-Host "Play the session, then return to the main menu or close the window;"
Write-Host "the tape is persisted once at session end."

try {
    $mediaArguments = @(
        '-3',
        (Join-Path $PSScriptRoot 'materialize_retail_assets.py'),
        '--startup-media'
    )
    if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
        $mediaArguments += @('--game-root', $GameRoot)
    }

    & py @mediaArguments | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        throw "Retail startup-media preparation failed with exit code $LASTEXITCODE."
    }

    $engineArgs = @(
        '--path', $projectRoot,
        '--windowed', '--resolution', '1280x720',
        '--',
        '--record-tape=' + $TapePath
    )
    & $toolchain.EnginePath @engineArgs
    $engineExitCode = $LASTEXITCODE
}
finally {
    $toolchain.Dispose()
}

if ($engineExitCode -ne 0) {
    Write-Warning "Engine exited with code $engineExitCode; inspect any error output above."
    exit $engineExitCode
}

if (-not (Test-Path -LiteralPath $TapePath)) {
    throw "The engine exited successfully but no tape exists at $TapePath (was the destination already present? TapeFile.WriteNew refuses overwrites)."
}

Write-Host "Verifying the finalized tape:"
dotnet run --project (Join-Path $PSScriptRoot '..\OnslaughtRebuild.Headless\OnslaughtRebuild.Headless.csproj') -- `
    --tape $TapePath --repeat 2
exit $LASTEXITCODE
