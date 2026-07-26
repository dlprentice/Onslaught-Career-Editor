# SPDX-License-Identifier: GPL-3.0-or-later
#
# Controlled copied-runtime observation probe - GATED-BURST variant.
#
# Third sibling of tools/cdb_worldmatrix_probe.ps1 (breakpoint WINDOW around one
# wrapper call) and tools/cdb_lightstate_probe.ps1 (one breakpoint, hit-scheduled).
# This one exists for the third common shape: a set of observation points that each
# fire MANY times per frame, where the interesting quantity is the whole per-frame
# CENSUS rather than one sample.
#
# Shape: one cheap GATE breakpoint that is known to fire exactly once per rendered
# frame stays armed for the whole session. Everything else starts DISABLED, so the
# frontend and the first seconds of the level run at essentially full speed. On gate
# hit -GateFrame the probe enables the whole observation set; -GateWindowFrames gate
# hits later it disables them again and quits. The result is every hit of every
# observation point across an exact, bounded number of frames, with .time stamps on
# both edges so the window is measured rather than assumed.
#
# Running the same probe twice with different -GateFrame values is what turns
# "the state was X" into "the state was X at two different level times".
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

    # Virtual address of the once-per-frame gate. The default is the single call site
    # of CDXLandscape::Render, which tools/cdb_lightstate_probe.ps1 already
    # established fires exactly once per in-level frame and never in the frontend.
    [string]$GateVa = '0x0053e688',

    # Gate hit (i.e. in-level frame index) at which the observation set is armed.
    [int]$GateFrame = 400,

    # How many further gate hits the observation set stays armed for.
    [int]$GateWindowFrames = 2,

    # Debugger commands run once, at the arming edge.
    [string[]]$GateDumpCommands = @(),

    # Additional gate hits (in-level frame indices) at which -ExtraDumpCommands run
    # without arming anything. This is how one run samples a slowly-varying global at
    # several level times while still taking its per-draw census at one time.
    [int[]]$ExtraDumpFrames = @(),
    [string[]]$ExtraDumpCommands = @(),

    # Observation points. Each entry is a hashtable @{ Id = <int 1..30>; Va = '0x...';
    # Commands = @('.printf ...', 'dd ...') }. Ids must be distinct and must not
    # collide with -ScratchBreakpointIds. Id 0 is reserved for the gate.
    [Parameter(Mandatory = $true)][hashtable[]]$Sites,

    # Breakpoint ids the site command scripts may create and destroy at runtime
    # (used for one-shot "return address" breakpoints). They are excluded from the
    # bulk enable/disable so a stale be/bd cannot resurrect one.
    [int[]]$ScratchBreakpointIds = @(),

    # Hard cap on total observation-point hits, in case a site turns out to fire far
    # more often than expected. Reaching it disarms and quits immediately.
    [int]$MaxHits = 4000,

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

# Backslashes inside a debugger command string must be doubled.
function Esc([string]$p) { $p -replace '\\', '\\' }

$ids = @()
foreach ($s in $Sites) {
    foreach ($k in @('Id', 'Va', 'Commands')) {
        if (-not $s.ContainsKey($k)) { throw "Site is missing '$k': $($s | Out-String)" }
    }
    if ([int]$s.Id -le 0) { throw "Site id must be >= 1 (0 is the gate)." }
    if ($ids -contains [int]$s.Id) { throw "Duplicate site id $($s.Id)." }
    if ($ScratchBreakpointIds -contains [int]$s.Id) { throw "Site id $($s.Id) collides with a scratch id." }
    $ids += [int]$s.Id
}
$idList = ($ids | Sort-Object) -join ' '

# cdb's default radix is 16. A decimal count written bare would be read as hex, so
# every count below is emitted with the 0n prefix.
$siteFiles = @()
foreach ($s in $Sites) {
    $f = Join-Path $ScratchDirectory ("on-site-{0}.txt" -f $s.Id)
    $body = (@($s.Commands) | ForEach-Object { $_ }) -join "`n"
    @"
r `$t4 = @`$t4 + 1
$body
.if (@`$t4 >= 0n$MaxHits) { .printf "MAXHITS %d - disarming\n", @`$t4; bd $idList; .printf "ALLDONE\n" }
gc
"@ | Set-Content -LiteralPath $f -Encoding ascii
    $siteFiles += ,@($s.Id, $s.Va, $f)
}

$gateDumpBody = (@($GateDumpCommands) | ForEach-Object { "  $_" }) -join "`n"
$extraBody = (@($ExtraDumpCommands) | ForEach-Object { "  $_" }) -join "`n"
$extraBranches = ''
foreach ($f in ($ExtraDumpFrames | Sort-Object -Unique)) {
    if ($f -eq $GateFrame -or $f -eq ($GateFrame + $GateWindowFrames)) {
        throw "ExtraDumpFrames entry $f collides with the arm/disarm frame."
    }
    $extraBranches += @"
.elsif (@`$t3 == 0n$f) {
  .printf "--- EXTRA DUMP at gate frame %d ---\n", @`$t3
  .time
$extraBody
}

"@
}

$gateFile = Join-Path $ScratchDirectory 'on-gate.txt'
@"
r `$t3 = @`$t3 + 1
.if (@`$t3 == 0n$GateFrame) {
  .printf "--- ARM at gate frame %d ---\n", @`$t3
  .time
$gateDumpBody
  be $idList
}
.elsif (@`$t3 == 0n$($GateFrame + $GateWindowFrames)) {
  .printf "--- DISARM at gate frame %d, total site hits %d ---\n", @`$t3, @`$t4
  .time
  bd $idList
  .printf "ALLDONE\n"
}
$extraBranches
.if (@`$t3 >= 0n$($GateFrame + $GateWindowFrames)) { q }
gc
"@ | Set-Content -LiteralPath $gateFile -Encoding ascii

$initLines = @(
    ".printf `"=== TARGET $hash ===\n`"",
    'lm m BEA',
    'r $t1 = 0', 'r $t2 = 0', 'r $t3 = 0', 'r $t4 = 0', 'r $t6 = 0', 'r $t7 = 0',
    "bp0 $GateVa `"`$`$><$(Esc $gateFile)`""
)
foreach ($sf in $siteFiles) {
    $initLines += "bp$($sf[0]) $($sf[1]) `"`$`$><$(Esc $sf[2])`""
}
$initLines += "bd $idList"
$initLines += 'bl'
$initLines += ".printf `"=== RUNNING ===\n`""
$initLines += 'g'

$initFile = Join-Path $ScratchDirectory 'init.txt'
($initLines -join "`n") | Set-Content -LiteralPath $initFile -Encoding ascii

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
    Note             = 'cdb quits (and so terminates the copied target) once the gate window closes.'
}
