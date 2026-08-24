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
#     BEFORE build, media materialization, or launch. Comparisons fold
#     extended DOS-device prefixes (\\?\C:\..., \\?\UNC\...) onto their plain
#     Win32 identity first, so namespace aliases cannot bypass the boundary,
#     and device bodies that alias no ordinary path are refused outright.
#     The engine-side TapeFile boundary is a second layer, not a substitute.
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
# before anything is built, materialized, or launched. All comparisons run on
# ONE Windows identity: extended DOS-device prefixes are folded to their
# plain Win32 form first, so \\?\C:\... can never carry an alias identity the
# boundary did not evaluate, and device bodies that are not aliases of
# ordinary paths are refused outright.
function ConvertFrom-WindowsComparisonIdentity([string]$PathValue) {
    # Returns the plain Win32 comparison identity. Device bodies that do NOT
    # alias an ordinary path (\\?\GLOBALROOT\..., volume GUIDs) return $null:
    # callers refuse those instead of comparing a fabricated identity.
    if ([string]::IsNullOrEmpty($PathValue)) { return $null }

    if ($PathValue.StartsWith('\\.\', [StringComparison]::Ordinal)) {
        $PathValue = '\\?\' + $PathValue.Substring(4)
    }
    if (-not $PathValue.StartsWith('\\?\', [StringComparison]::Ordinal)) {
        return $PathValue
    }

    $body = $PathValue.Substring(4)
    if ($body.Length -gt 4 -and $body.StartsWith('UNC\', [StringComparison]::OrdinalIgnoreCase)) {
        return '\\' + $body.Substring(4)
    }
    if ($body.Length -ge 3 -and
        [char]::IsAsciiLetter($body[0]) -and
        $body[1] -eq [IO.Path]::VolumeSeparatorChar -and
        ($body[2] -eq [IO.Path]::DirectorySeparatorChar -or $body[2] -eq [IO.Path]::AltDirectorySeparatorChar)) {
        return $body
    }

    # Not an alias of an ordinary file-system path.
    return $null
}

function Test-IsUnsupportedDeviceNamespacePath([string]$PathValue) {
    return $null -eq (ConvertFrom-WindowsComparisonIdentity $PathValue)
}

# At-or-under decision on the folded identity. The EXACT case compares the
# target's DIRECTORY to the root (an existing or fresh .json directly inside
# the root is at-or-under even though the file does not exist yet).
function Test-PathAtOrUnder([string]$CandidateRoot, [string]$TargetPath) {
    $identityRoot = ConvertFrom-WindowsComparisonIdentity $CandidateRoot
    if ($null -eq $identityRoot) { throw "Refusing unevaluated device-namespace candidate root: $CandidateRoot" }
    $root = [IO.Path]::GetFullPath($identityRoot).TrimEnd('\', '/')
    if ([string]::IsNullOrEmpty($root)) { return $false }

    $identityTarget = ConvertFrom-WindowsComparisonIdentity $TargetPath
    if ($null -eq $identityTarget) { throw "Refusing unevaluated device-namespace tape destination: $TargetPath" }
    $fullTarget = [IO.Path]::GetFullPath($identityTarget)
    # EXACT-root case: the FULL target itself (not its directory) compared to
    # the root, so a destination equal to the root is refused outright.
    $trimmedFullTarget = $fullTarget.TrimEnd('\', '/')
    $targetDir = [IO.Path]::GetDirectoryName($fullTarget)
    if ([string]::IsNullOrEmpty($targetDir)) { return $false }
    $targetDir = $targetDir.TrimEnd('\', '/')
    return (
        $targetDir -ieq $root -or
        $trimmedFullTarget -ieq $root -or
        $targetDir.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase) -or
        $targetDir.StartsWith($root + '/', [StringComparison]::OrdinalIgnoreCase)
    )
}

# Exact mirror of materialize_retail_assets.py _steam_roots + _game_candidates(None):
# registry roots (HKCU SteamPath, HKLM WOW6432Node InstallPath), BOTH default
# C: Steam roots, every "path" entry of each parsed steamapps/libraryfolders.vdf,
# the four D:/E: literals, all joined with steamapps/common/Battle Engine Aquila,
# normalized (lowercase, absolute, forward slashes folded) and deduped keeping
# first occurrence order.
function Get-SteamLibraryParents {
    $parents = New-Object System.Collections.Generic.List[string]
    try {
        foreach ($keyPath in @(
            'HKCU:\Software\Valve\Steam',
            'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam'
        )) {
            try {
                if (Test-Path $keyPath) {
                    $item = Get-ItemProperty -Path $keyPath -ErrorAction SilentlyContinue
                    $value = if ($keyPath -like 'HKCU:*') { $item.SteamPath } else { $item.InstallPath }
                    if (-not [string]::IsNullOrWhiteSpace($value)) {
                        $parents.Add($value)
                    }
                }
            } catch {
                # One unreadable hive must not hide the other; Python's
                # per-key `except OSError: pass` has the same shape.
            }
        }
    } catch {
        # Registry provider unavailable: fall through to defaults and vdfs.
    }

    $parents.Add('C:\Program Files (x86)\Steam')
    $parents.Add('C:\Program Files\Steam')

    $libraries = New-Object System.Collections.Generic.List[string]
    foreach ($parent in $parents) {
        $libraries.Add($parent)
        $vdf = Join-Path $parent 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf -PathType Leaf) {
            try {
                $text = [IO.File]::ReadAllText($vdf)
                foreach ($match in [regex]::Matches($text, '"path"\s+"([^"]+)"')) {
                    # Exact mirror of Python's value.replace("\\\\", "\\"):
                    # VDF escapes every backslash as two, so TWO literal
                    # backslash characters collapse to ONE. PowerShell
                    # single quotes do not escape backslashes.
                    $libraries.Add($match.Groups[1].Value.Replace('\\', '\'))
                }
            } catch {
                # Unreadable vdf behaves like Python's read failure: skip it.
            }
        }
    }
    return ,$libraries.ToArray()
}

function Get-ResolvedRetailRoots([string]$ExplicitGameRoot) {
    if (-not [string]::IsNullOrWhiteSpace($ExplicitGameRoot)) {
        return ,@($ExplicitGameRoot)
    }

    $candidates = New-Object System.Collections.Generic.List[string]
    foreach ($library in (Get-SteamLibraryParents)) {
        $candidates.Add((Join-Path $library 'steamapps\common\Battle Engine Aquila'))
    }
    foreach ($literal in @(
        'D:\Steam\steamapps\common\Battle Engine Aquila',
        'D:\SteamLibrary\steamapps\common\Battle Engine Aquila',
        'E:\Steam\steamapps\common\Battle Engine Aquila',
        'E:\SteamLibrary\steamapps\common\Battle Engine Aquila'
    )) {
        $candidates.Add($literal)
    }

    # os.path.normcase(os.path.abspath(...)) mirror: absolute, backslashed,
    # lowercased; dedupe keeps FIRST occurrence exactly like the Python set.
    $unique = New-Object System.Collections.Generic.List[string]
    $seen = @{}
    foreach ($candidate in $candidates) {
        $key = [IO.Path]::GetFullPath($candidate).Replace('/', '\').ToLowerInvariant()
        if (-not $seen.ContainsKey($key)) {
            $seen[$key] = $true
            $unique.Add($key)
        }
    }
    return ,$unique.ToArray()
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

# A tape path that is not an alias of an ordinary file-system path (device
# namespaces, volume GUIDs) has NO evaluated identity: refuse before build,
# materialization, or launch.
if (Test-IsUnsupportedDeviceNamespacePath $TapePath) {
    throw ("Refusing command tape destination '$TapePath': it is a Windows device-namespace " +
        "path, not an ordinary file-system path.")
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
