# SPDX-License-Identifier: GPL-3.0-or-later
#
# Controlled copied-runtime observation probe.
#
# Reads values out of a RUNNING copy of the game at a chosen point in a chosen
# function, using a breakpoint WINDOW rather than a filter: an "enter" breakpoint
# arms the dump breakpoint, an "exit" breakpoint disarms it. Everything outside the
# window runs at full speed and traps nothing, which is what makes this usable on a
# real-time renderer - a bare breakpoint on a per-draw D3D call traps thousands of
# times per frame and the game never reaches a playable state.
#
# It was written for, and is proven by,
# local-lab/COCKPIT-WORLD-MATRIX-RUNTIME-2026-07-26.md, which used it to read
# IDirect3DDevice9::SetTransform(D3DTS_WORLDMATRIX(0)) at the Level 100 cockpit
# draw. Several other open questions in the handoff are blocked on exactly this
# shape of observation, so the mechanism is generalised here rather than left in
# local-lab.
#
# HARD RULE, enforced below and not overridable by a parameter: this refuses to
# launch the Steam install, and refuses to launch pristine BEA.exe. It only ever
# launches a copied target, and it records the target's sha256 in its own log so a
# reading can be traced back to the exact bytes that produced it. It never writes to
# the debuggee - breakpoints, register reads and memory reads only.
#
# This script starts the target and returns its pid. It does NOT drive the frontend;
# pair it with the input driver used by the evidence note
# (local-lab/cockpit-worldmatrix-2026-07-26/Drive-RunningRetail.ps1) or with
# rebuild/tools/Capture-Retail.ps1's step vocabulary.

[CmdletBinding()]
param(
    # Root of a COPIED target directory containing BEA.exe.
    [string]$TargetRoot = "$PSScriptRoot\..\local-lab\safe-copy-bea-pristine",

    # Virtual address of the function whose body defines the observation window.
    # Its entry arms the dump; the address in -ExitVa disarms it.
    [Parameter(Mandatory = $true)][string]$EnterVa,

    # Virtual address at which the window closes. For a single-call-site function
    # this is the RETURN ADDRESS of that call, which is what makes the window
    # provably specific to that one call rather than to the function in general.
    [Parameter(Mandatory = $true)][string]$ExitVa,

    # Virtual address to break on inside the window - the instruction that performs
    # the thing being observed (e.g. the indirect CALL that reaches SetTransform).
    [Parameter(Mandatory = $true)][string]$DumpVa,

    # Debugger commands run at each DumpVa hit, in order. Registers are available,
    # so prefer register-relative expressions (df /c 4 @edx L10) over hardcoded
    # absolute addresses: a value read through the register the code actually used
    # cannot be pointing at the wrong object.
    [Parameter(Mandatory = $true)][string[]]$DumpCommands,

    # Number of complete windows to record before quitting.
    [int]$Windows = 3,

    # Windows to let pass before recording starts, so a later moment can be reached.
    [int]$SkipWindows = 0,

    [string]$LogPath,
    [string]$ScratchDirectory,
    [string[]]$GameArguments = @('-skipfmv')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$TargetRoot = [IO.Path]::GetFullPath($TargetRoot)
$exe = Join-Path $TargetRoot 'BEA.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw "No BEA.exe under $TargetRoot" }

$installRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila'
if ($TargetRoot.TrimEnd('\') -ieq $installRoot.TrimEnd('\')) {
    throw "Refusing to run against the Steam install. Use a copied target."
}
$hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
if ($hash -ieq '74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750') {
    throw ("Target is unmodified pristine BEA.exe. It runs fullscreen, which makes " +
           "a debugger break unrecoverable on a single display. Apply force_windowed " +
           "(5 bytes at file offset 0x12A644) to the COPY first.")
}

if ([string]::IsNullOrWhiteSpace($ScratchDirectory)) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $ScratchDirectory = Join-Path ([IO.Path]::GetFullPath("$PSScriptRoot\..")) "local-lab\cdb-probes\$stamp"
}
$ScratchDirectory = [IO.Path]::GetFullPath($ScratchDirectory)
$null = [IO.Directory]::CreateDirectory($ScratchDirectory)
if ([string]::IsNullOrWhiteSpace($LogPath)) { $LogPath = Join-Path $ScratchDirectory 'cdb-session.log' }

# cdb's default radix is 16. A decimal window count written bare would be read as
# hex - 800 became 2048 once already - so every count below is emitted with 0n.
$first = $SkipWindows
$last = $SkipWindows + [Math]::Max(1, $Windows)

$enterFile = Join-Path $ScratchDirectory 'on-enter.txt'
$dumpFile  = Join-Path $ScratchDirectory 'on-dump.txt'
$exitFile  = Join-Path $ScratchDirectory 'on-exit.txt'
$initFile  = Join-Path $ScratchDirectory 'init.txt'

@"
.if (@`$t3 >= 0n$first) { .printf "=== WINDOW ENTER (index %d) ===\n", @`$t3; be 2 }
gc
"@ | Set-Content -LiteralPath $enterFile -Encoding ascii

$dumpBody = @('.printf "--- OBSERVATION ---\n"') + $DumpCommands + @('gc')
$dumpBody -join "`n" | Set-Content -LiteralPath $dumpFile -Encoding ascii

@"
bd 2
r `$t3 = @`$t3 + 1
.if (@`$t3 >= 0n$last) { .printf "ALLDONE after %d windows\n", @`$t3; q } .else { gc }
"@ | Set-Content -LiteralPath $exitFile -Encoding ascii

# Backslashes inside a debugger command string must be doubled.
function Esc([string]$p) { $p -replace '\\', '\\' }

@"
.printf "=== TARGET $hash ===\n"
lm m BEA
bu $EnterVa "`$`$><$(Esc $enterFile)"
bu $ExitVa "`$`$><$(Esc $exitFile)"
bu $DumpVa "`$`$><$(Esc $dumpFile)"
bd 2
r `$t3 = 0
bl
.printf "=== RUNNING ===\n"
g
"@ | Set-Content -LiteralPath $initFile -Encoding ascii

$cdb = & (Join-Path $PSScriptRoot 'get_cdb_path.ps1') -AsLiteral
$env:_NT_SYMBOL_PATH = ''

$process = Start-Process -FilePath $cdb -WorkingDirectory $TargetRoot -PassThru -ArgumentList (
    @('-cf', $initFile, '-logo', $LogPath, '-o', $exe) + $GameArguments)

$target = $null
for ($i = 0; $i -lt 240; $i++) {
    $target = Get-Process -Name 'BEA' -ErrorAction SilentlyContinue | Where-Object { $_.Path -ieq $exe }
    if ($target) { break }
    Start-Sleep -Milliseconds 250
}
if (-not $target) { throw "The copied target never started under cdb. See $LogPath." }

[pscustomobject]@{
    TargetRoot       = $TargetRoot
    TargetSha256     = $hash
    DebuggerPid      = $process.Id
    TargetPid        = $target.Id
    ScratchDirectory = $ScratchDirectory
    LogPath          = $LogPath
    Note             = 'cdb quits (and so terminates the copied target) once the requested windows are recorded.'
}
