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
#   - Career saves (.bes) and retail install paths are NEVER touched; the
#     FirstFlightGame argument parser rejects a .bes destination outright.
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
