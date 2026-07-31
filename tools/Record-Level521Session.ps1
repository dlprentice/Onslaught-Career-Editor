# SPDX-License-Identifier: GPL-3.0-or-later
<#
.SYNOPSIS
Launch level 521 on the copied target, wait for you, then attach TTD for one
bounded take. Repeat for as many takes as the session needs.

.DESCRIPTION
This is a thin, level-521-shaped front end over tools/ttd_record.ps1 -Attach.
It adds exactly three things that Record-GameMoment.ps1 does not:

  * it LAUNCHES the copied target for you, from the copied target's own
    directory, with `-skipfmv -level 521`. The working directory is load-bearing
    (BEA resolves data\ relative to its CWD and drops its logs there), and the
    machine's firewall rule is bound to that exact image path.
  * it names the trace `level521-native-<UTC timestamp>-take<N>`, so a session
    is a set of traces that sort together and never collides with an existing
    directory.
  * it prints the in-game action order that the mission scripts require, so the
    natives this capture exists to reach actually execute inside the window.

WHY LEVEL 521. Fifty-one of the 144 MissionScript natives are authored in
shipped scripts and were never observed executing in any of the 66 recorded
level openings. Level 521's own scripts author seventeen of them - more than any
other single level. NONE of the seventeen fires from merely starting the level:
the 181-second level521 opening covered seventeen natives and not one of them
was on this list. Twelve of the seventeen hang off one player action - destroying
the Muspell Research Station - and fire within about a minute of it. See
tools/RUNBOOK-level521-native-capture.md.

ELEVATION. TTD recording needs an elevated token and this machine has no
TTDService, so every recording needs elevation. Run this from ONE elevated
PowerShell 7 window for a whole session and there is no prompt at all between
takes. Run it unelevated and it launches the game unelevated (which is what you
want) and raises one UAC prompt per take.

.EXAMPLE
Take 1 - a short capture of the last turret dying:

    pwsh -File tools\Record-Level521Session.ps1 -Take 1 -Seconds 60 -MaxFileMB 4096

.EXAMPLE
Take 2 - the research-station kill and the whole boss cascade. The game is still
running from take 1, so this attaches to it rather than launching a second copy:

    pwsh -File tools\Record-Level521Session.ps1 -Take 2 -Seconds 300

.EXAMPLE
Print every interlock and the exact recorder command, launch nothing:

    pwsh -File tools\Record-Level521Session.ps1 -DryRun
#>
[CmdletBinding()]
param(
    # Take number within this session. Traces are named
    # level521-native-<stamp>-take<N>, so takes sort together and never collide.
    [ValidateRange(1, 99)][int]$Take = 1,

    # Session stamp. Defaults to now (UTC). Pass the SAME value on every take of
    # one session so the traces group under one -TracePattern for the analysis
    # step; the default is printed, and take 1 prints the exact command for the
    # takes that follow.
    [ValidatePattern('^[0-9]{8}-[0-9]{4}$')]
    [string]$SessionStamp = ((Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmm')),

    # Seconds to record once you say go.
    #
    # SIZING. The level521 opening recorded 5.71 GiB in 181 s - 33.8 MB/s - so
    # budget about 2 GB per minute. The default 300 s is about 10 GB and is sized
    # for the boss cascade, whose script-side length is roughly one minute of
    # Pause() calls; the wall-clock cost of those Pause() calls under TTD's
    # slowdown has NOT been measured, so the window is deliberately several times
    # the script-side length rather than tight against it.
    [ValidateRange(5, 3600)][int]$Seconds = 300,

    # Hard ceiling on the .run file. Kept comfortably above Seconds * 34 MB/s:
    # a recording that stops at the cap while the game is still running is
    # reported as 'max-file-aborted' and is an incomplete capture.
    [ValidateRange(64, 1048576)][int]$MaxFileMB = 16384,

    # The level to launch. Defaults to the one this script exists for; exposed so
    # the same session shape can be pointed at another level without a new file.
    [ValidateRange(0, 999)][int]$Level = 521,

    # Root of the COPIED target. Exposed for the same reason ttd_record.ps1
    # exposes it - a worktree has no local-lab/ of its own - and guarded by the
    # same interlocks: ttd_record.ps1 pins the specimen hash and refuses the
    # Steam install and anything under Program Files.
    [string]$TargetRoot = '',

    # Attach to a copied target that is already running and never launch one.
    # Set automatically on the elevated re-invocation, because the unelevated
    # parent has already launched the game by then.
    [switch]$NoLaunch,

    # Skip the "press Enter when you are ready" gate. Set automatically on the
    # elevated re-invocation, where the parent has already asked.
    [switch]$NoPrompt,

    # Run every check, print the recorder command, launch and record nothing.
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repo     = Split-Path $PSScriptRoot -Parent
$recorder = Join-Path $PSScriptRoot 'ttd_record.ps1'
$analyzer = Join-Path $PSScriptRoot 'Test-Level521NativeCoverage.ps1'
if ([string]::IsNullOrWhiteSpace($TargetRoot)) {
    $TargetRoot = Join-Path $repo 'local-lab\safe-copy-bea-pristine'
}
$TargetRoot = [IO.Path]::GetFullPath($TargetRoot)
$exe        = Join-Path $TargetRoot 'BEA.exe'
$traceRoot  = 'G:\bea-ttd'

$sessionName = 'level521-native-{0}' -f $SessionStamp
$traceName   = '{0}-take{1}' -f $sessionName, $Take
$traceDir    = Join-Path $traceRoot $traceName

function Fail([string]$Message) { throw $Message }

foreach ($required in @($recorder, $exe)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "Required input is missing: $required"
    }
}
if (Test-Path -LiteralPath $traceDir) {
    Fail ("Trace output already exists: $traceDir. " +
          "Use the next -Take, or a new -SessionStamp. Stale traces are never reused.")
}

# A recording that hits the file cap while the game is still alive is
# 'max-file-aborted' - finalised but incomplete. Refuse the combination up front
# rather than discover it after the maintainer has played the level.
$projectedMB = [int]($Seconds * 34)
if ($projectedMB -gt ($MaxFileMB * 0.9)) {
    Fail ("At the measured 34 MB/s a ${Seconds}s take projects to about ${projectedMB} MB, " +
          "which is within 10% of -MaxFileMB $MaxFileMB. Raise -MaxFileMB to at least " +
          [int]($projectedMB / 0.85) + " or shorten -Seconds.")
}

$elevated = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# ------------------------------------------------------------------ the target
$allBea  = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue)
$ours    = @($allBea | Where-Object { $_.Path -ieq $exe })
$foreign = @($allBea | Where-Object { $_.Path -ine $exe })

if ($foreign.Count -gt 0) {
    # The maintainer's Steam BEA.exe is a deliberately patched binary and is not
    # a specimen. ttd_record refuses to attach to it; say so before anything else
    # happens, because a running Steam copy also makes the process match ambiguous.
    $paths = ($foreign | ForEach-Object { $_.Path }) -join "`n  "
    Fail ("A BEA.exe that is NOT the copied target is running. Close it first.`nFound:`n  $paths`nExpected:`n  $exe")
}
if ($ours.Count -gt 1) {
    Fail "More than one copy of the target is running ($($ours.Count)). Close all but one."
}

Write-Host ''
Write-Host '================================================================' -ForegroundColor Cyan
Write-Host ("  LEVEL {0} NATIVE-COVERAGE SESSION - take {1}" -f $Level, $Take) -ForegroundColor Cyan
Write-Host '================================================================' -ForegroundColor Cyan
Write-Host ("  session   : {0}" -f $sessionName)
Write-Host ("  trace     : {0}" -f $traceDir)
Write-Host ("  duration  : {0} s  (about {1} GB at the measured 34 MB/s)" -f $Seconds, [math]::Round($projectedMB / 1024, 1))
Write-Host ("  file cap  : {0} MB" -f $MaxFileMB)
Write-Host ("  elevated  : {0}" -f $elevated)
Write-Host ''

if ($DryRun) {
    Write-Host 'DRY RUN - nothing was launched and nothing was recorded.' -ForegroundColor Yellow
    Write-Host 'It would launch (only if no copied target is running):'
    Write-Host ("  {0} -skipfmv -level {1}     (cwd {2})" -f $exe, $Level, $TargetRoot)
    Write-Host 'and then record with:'
    Write-Host ("  {0} -Attach -Name {1} -Seconds {2} -MaxFileMB {3}" -f $recorder, $traceName, $Seconds, $MaxFileMB)
    Write-Host ''
    Write-Host 'and afterwards you would analyse it with:'
    Write-Host ("  pwsh -File {0} -TracePattern '{1}-take*'" -f $analyzer, $sessionName)
    return
}

# ----------------------------------------------------------------- launch
if ($ours.Count -eq 1) {
    Write-Host ("Copied target already running (PID {0}). Attaching to it." -f $ours[0].Id)
}
elseif ($NoLaunch) {
    Fail "-NoLaunch was given but no copied target is running. Nothing to attach to."
}
else {
    if ($elevated) {
        Write-Warning ('This shell is elevated, so the GAME will be launched elevated too. ' +
                       'That works, but a normal-privilege game is closer to how it is played. ' +
                       'To avoid it, start the game yourself and re-run with -NoLaunch.')
    }
    Write-Host ("Launching {0} -skipfmv -level {1}" -f $exe, $Level)
    Write-Host ("  working directory: {0}" -f $TargetRoot)
    $gameStart = [Diagnostics.ProcessStartInfo]::new()
    $gameStart.FileName = $exe
    $gameStart.WorkingDirectory = $TargetRoot
    $gameStart.UseShellExecute = $false
    foreach ($argument in @('-skipfmv', '-level', "$Level")) {
        $gameStart.ArgumentList.Add([string]$argument)
    }
    $null = [Diagnostics.Process]::Start($gameStart)

    for ($i = 0; $i -lt 120; $i++) {
        $ours = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue |
            Where-Object { $_.Path -ieq $exe })
        if ($ours.Count -ge 1) { break }
        Start-Sleep -Milliseconds 250
    }
    if ($ours.Count -eq 0) { Fail "The copied target did not start." }
    Write-Host ("Game is up (PID {0})." -f $ours[0].Id)
}

# ------------------------------------------------------- the in-game plan
if (-not $NoPrompt) {
    Write-Host ''
    Write-Host 'WHAT HAS TO HAPPEN IN THE GAME (full detail: tools\RUNBOOK-level521-native-capture.md)' -ForegroundColor Yellow
    Write-Host '  Starting the level fires NONE of the seventeen target natives.'
    Write-Host ''
    Write-Host '  take 1 (short)  destroy the LAST of the 8 turrets while recording'
    Write-Host '                  -> UnsetObjective, ShutdownVariable'
    Write-Host '  take 2 (long)   destroy the Muspell Research Station while recording,'
    Write-Host '                  then STAY ALIVE and WATCH the hive boss for a full minute'
    Write-Host '                  -> UnsetObjective, GetX, GetY, GetZ, SpawnParticle,'
    Write-Host '                     ResetSegmentHealth, SetSegmentVulnerable, Die,'
    Write-Host '                     GetMapHeight, SetZ, SetGoalPoint, PlayAnimationWait'
    Write-Host ''
    Write-Host '  Play at FULL SPEED between takes. The game is a slideshow while recording,'
    Write-Host '  so line the shot up FIRST, then start the take, then fire.'
    Write-Host ''
    $answer = Read-Host 'Press Enter when you are lined up and ready to record (or type q to quit)'
    if ($answer -match '^\s*q') {
        Write-Host 'Nothing recorded. The game is still running.'
        return
    }
}

# ------------------------------------------------------------ elevate + record
if (-not $elevated) {
    Write-Host ''
    Write-Host 'Raising the elevation prompt now. Approve it, get back to the game,' -ForegroundColor Cyan
    Write-Host 'and THEN do the thing - the window is long enough to absorb the delay.' -ForegroundColor Cyan
    Write-Host ''
    $self = $MyInvocation.MyCommand.Path
    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = 'pwsh.exe'
    $startInfo.UseShellExecute = $true
    $startInfo.Verb = 'runas'
    foreach ($argument in @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $self,
        '-Take', "$Take", '-SessionStamp', $SessionStamp,
        '-Seconds', "$Seconds", '-MaxFileMB', "$MaxFileMB", '-Level', "$Level",
        '-TargetRoot', $TargetRoot, '-NoLaunch', '-NoPrompt'
    )) {
        $startInfo.ArgumentList.Add([string]$argument)
    }
    $elevatedProcess = [Diagnostics.Process]::Start($startInfo)
    $elevatedProcess.WaitForExit()
    exit $elevatedProcess.ExitCode
}

Write-Host ''
Write-Host '================================================================'
Write-Host ("  RECORDING take {0} for {1} seconds. GO." -f $Take, $Seconds)
Write-Host '  The game slows down now, and speeds back up and KEEPS RUNNING'
Write-Host '  when this finishes.'
Write-Host '================================================================'
Write-Host ''

$recorderStart = [Diagnostics.ProcessStartInfo]::new()
$recorderStart.FileName = 'pwsh.exe'
$recorderStart.UseShellExecute = $false
$recorderStart.CreateNoWindow = $false
foreach ($argument in @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $recorder,
    '-TargetRoot', $TargetRoot, '-Name', $traceName, '-Attach',
    '-Seconds', "$Seconds", '-MaxFileMB', "$MaxFileMB", '-TraceRoot', $traceRoot
)) {
    $recorderStart.ArgumentList.Add([string]$argument)
}
$recorderProcess = [Diagnostics.Process]::Start($recorderStart)
$recorderProcess.WaitForExit()
$code = $recorderProcess.ExitCode

# ---------------------------------------------------------------- the receipt
# The RECEIPT is the truth, here and in the analysis step. Read it rather than
# reporting the exit code alone.
Write-Host ''
$receiptPath = Join-Path $traceDir 'receipt.json'
if (Test-Path -LiteralPath $receiptPath) {
    $receipt = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json -Depth 20
    Write-Host ("outcome : {0}" -f $receipt.guestOutcome)
    Write-Host ("trace   : {0:N0} MB over {1:N1} s ({2} MB/s)" -f
        $receipt.traceMB, $receipt.actualRecordSeconds, $receipt.growthMBPerSecond)
    Write-Host ("receipt : {0}" -f $receiptPath)
    if ($receipt.guestOutcome -ceq 'alive-at-stop') {
        Write-Host 'HEALTHY: the game was still running when the timer stopped tracing.' -ForegroundColor Green
    } else {
        Write-Warning ("guestOutcome is '{0}', not 'alive-at-stop'. Read the receipt before trusting this take." -f
            $receipt.guestOutcome)
    }
} else {
    Write-Warning "No receipt at $receiptPath - the recorder did not get far enough to write one."
}

if ($code -eq 0) {
    Write-Host ''
    Write-Host '================================================================' -ForegroundColor Green
    Write-Host '  TAKE COMPLETE. The game is still running - carry on playing.' -ForegroundColor Green
    Write-Host '================================================================' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Next take (run from this same window to avoid another UAC prompt):'
    Write-Host ("  pwsh -File {0} -SessionStamp {1} -Take {2}" -f
        $MyInvocation.MyCommand.Path, $SessionStamp, ($Take + 1))
    Write-Host ''
    Write-Host 'When the session is finished, check what you actually caught:'
    Write-Host ("  pwsh -File {0} -TracePattern '{1}-take*'" -f $analyzer, $sessionName)
} else {
    Write-Warning ("Recorder exited {0} - see the messages above and the receipt." -f $code)
}
Write-Host ''
Read-Host 'Press Enter to close'
exit $code
