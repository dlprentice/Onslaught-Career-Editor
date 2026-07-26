# SPDX-License-Identifier: GPL-3.0-or-later
#
# Controlled copied-runtime observation probe - HIT-SCHEDULED variant.
#
# Sibling of tools/cdb_worldmatrix_probe.ps1. That script uses a breakpoint WINDOW
# (arm on enter, disarm on return) because its observation point is a per-draw D3D
# call that fires thousands of times per frame. This script exists for the other
# common shape: an observation point that already fires exactly ONCE PER FRAME, such
# as the single call site of CDXLandscape::Render at 0x0053e688. There a window buys
# nothing and a single counted breakpoint is both simpler and more honest - the value
# is read at literally the instruction named, with nothing else armed.
#
# The breakpoint script keeps a hit counter and dumps only on a schedule
# (-FirstHit, then every -HitStride hits, -Dumps times, then quits). That is what
# lets one run sample the same state at two level times far apart, which is the
# discriminator a "is this state constant in time?" question needs. Every dump is
# stamped with .time so the real elapsed interval is measured, not assumed from an
# assumed frame rate.
#
# HARD RULE, enforced below and not overridable by a parameter: this refuses to
# launch the Steam install, and refuses to launch pristine BEA.exe. It only ever
# launches a copied target, and it records the target's sha256 in its own log so a
# reading can be traced back to the exact bytes that produced it. It never writes to
# the debuggee - breakpoints, register reads and memory reads only.
#
# This script starts the target and returns its pid. It does NOT drive the frontend;
# pair it with the input driver used by the evidence notes
# (local-lab/cockpit-worldmatrix-2026-07-26/Drive-RunningRetail.ps1).

[CmdletBinding()]
param(
    # Root of a COPIED target directory containing BEA.exe.
    [string]$TargetRoot = "$PSScriptRoot\..\local-lab\safe-copy-bea-pristine",

    # Virtual address to break on. Chosen so that it fires about once per frame;
    # if it fires far more often, use tools/cdb_worldmatrix_probe.ps1 instead.
    [Parameter(Mandatory = $true)][string]$HitVa,

    # Debugger commands run at each scheduled dump, in order.
    [Parameter(Mandatory = $true)][string[]]$DumpCommands,

    # Hit index of the first dump. Hits before this run untrapped-but-counted, which
    # is how the frontend and the first seconds of the level are skipped.
    [int]$FirstHit = 300,

    # Hits between dumps.
    [int]$HitStride = 600,

    # Number of dumps to take before quitting.
    [int]$Dumps = 4,

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

# cdb's default radix is 16. A decimal count written bare would be read as hex, so
# every count below is emitted with the 0n prefix.
$hitFile  = Join-Path $ScratchDirectory 'on-hit.txt'
$initFile = Join-Path $ScratchDirectory 'init.txt'

$dumpBody = ($DumpCommands | ForEach-Object { "  $_" }) -join "`n"

@"
r `$t3 = @`$t3 + 1
.if (@`$t3 >= @`$t5) {
  .printf "--- OBSERVATION hit %d ---\n", @`$t3
  .time
$dumpBody
  r `$t4 = @`$t4 + 1
  r `$t5 = @`$t5 + 0n$HitStride
  .if (@`$t4 >= 0n$Dumps) { .printf "ALLDONE after %d dumps\n", @`$t4; q }
}
gc
"@ | Set-Content -LiteralPath $hitFile -Encoding ascii

# Backslashes inside a debugger command string must be doubled.
function Esc([string]$p) { $p -replace '\\', '\\' }

@"
.printf "=== TARGET $hash ===\n"
lm m BEA
r `$t3 = 0
r `$t4 = 0
r `$t5 = 0n$FirstHit
bu $HitVa "`$`$><$(Esc $hitFile)"
bl
u $HitVa L1
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
    Note             = 'cdb quits (and so terminates the copied target) once the requested dumps are recorded.'
}
