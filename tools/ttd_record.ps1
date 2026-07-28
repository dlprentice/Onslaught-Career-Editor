# SPDX-License-Identifier: GPL-3.0-or-later
#
# Record ONE Time Travel Debugging trace of a COPIED Battle Engine Aquila target.
#
# WHY THIS EXISTS
# ---------------
# Every other runtime instrument in this repository answers one question per game
# launch: tools/cdb_*_probe.ps1 arm a breakpoint set, drive the frontend, take a
# burst, and quit. Asking a second question means relaunching and re-driving.
#
# TTD inverts that. It records the complete user-mode instruction and memory history
# of ONE run into a .run file. Every later question is answered offline against the
# file by tools/ttd_query.ps1, with no relaunch, no frontend driving, no input, and
# no risk to the maintainer's session. Recording is the expensive step; querying is
# free and repeatable forever.
#
# ELEVATION
# ---------
# TTD recording requires an elevated token. Measured 2026-07-27 on this machine,
# non-elevated, against both TTD builds present:
#
#   Error:  Administrative privileges are required in order to record program
#           execution (Error Code 0x80070005:  Access is denied.)
#
# This script therefore REFUSES to run non-elevated rather than raising a UAC
# consent dialog behind the maintainer's back, and prints the exact command to run
# from an elevated shell. See local-lab/TTD-PIPELINE-2026-07-27.md.
#
# HARD RULES, enforced below and not overridable by any parameter:
#   - never the Steam install, never anything under Program Files;
#   - never unmodified pristine BEA.exe (it runs fullscreen);
#   - never while a d3d9 proxy capture is in flight (the proxy dll is the lock);
#   - never while any BEA.exe is already running;
#   - traces are written to G: only. C: and F: are refused.
# It never writes to the debuggee. TTD records; it does not modify.

[CmdletBinding()]
param(
    # Root of a COPIED target directory containing BEA.exe.
    [string]$TargetRoot = "$PSScriptRoot\..\local-lab\safe-copy-bea-pristine",

    # Arguments handed to the game. Default records a cold startup with the intro
    # FMV skipped. Pass @() for a fully cold start including the FMV.
    [string[]]$GameArguments = @('-skipfmv'),

    # Short label; becomes the trace directory name under -TraceRoot.
    [Parameter(Mandatory = $true)][string]$Name,

    # Wall-clock seconds to record for, measured from the moment the .run file
    # first appears (i.e. from the start of recording, not from process launch).
    [int]$Seconds = 20,

    # Trace destination. MUST be on G: - TTD traces are large and G: is the
    # designated capture drive on this machine.
    [string]$TraceRoot = 'G:\bea-ttd',

    # Refuse to start unless at least this much is free on the trace drive.
    [int]$RequireFreeGB = 40,

    # Hard cap on the .run file. TTD stops recording when it is reached.
    [int]$MaxFileMB = 32768,

    # Ring-buffer mode: keep only the last -MaxFileMB of execution. Use this when
    # the interesting moment is at the END of a long run.
    [switch]$Ring,

    # Restrict recording to these modules. TTD starts recording when execution
    # enters a listed module and stops when it leaves, so 'BEA.exe' records the
    # game's own code (plus whatever it calls) and skips the d3d9/kernel churn that
    # dominates a full trace. This is expected to be the difference between a
    # practical trace and an impractical one on a 60 fps title; every question this
    # instrument was stood up to answer - the mission-script VM, the HUD, unit AI,
    # weapons - lives inside BEA.exe. Pass @() for an unrestricted full trace.
    # MEASURED 2026-07-27 AND DEFAULTED OFF. This was @('BEA.exe') on the
    # reasoning above, and that reasoning is wrong on this title: module
    # restriction records NOTHING here. A controlled pair, one variable, same
    # target and arguments (-skipfmv -level 100), same elevated session:
    #     -Module @('BEA.exe')  ->  2.19 s,   4 MB   (one empty 4 MiB chunk)
    #     -Module @()           -> 14.15 s, 340 MB   (a real trace)
    # The 4 MB file is a preallocated chunk with nothing written into it, and
    # because the file EXISTS the recorder treated the run as a success and
    # computed a growth rate by dividing a constant by elapsed time. Two earlier
    # traces were reported "recorded" on exactly that basis and contained
    # nothing.
    #
    # So the default is now unrestricted. Real measured cost is about 24 MB/s,
    # which is affordable - the prior "GB per few seconds" estimate had no
    # measurement behind it and is roughly 40x too pessimistic.
    #
    # Pass -Module @('BEA.exe') only if you first re-establish that it captures
    # anything; do not restore it as a default on the strength of the argument
    # in the comment above, which sounded correct and was not.
    [string[]]$Module = @(),

    # Growth-rate sampling interval. The measured rate is reported and written to
    # the receipt; it is what makes the cost of a longer trace predictable.
    [int]$SampleIntervalSeconds = 2,

    # Run every interlock, print the exact TTD command line, launch nothing.
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PRISTINE_SHA256 = '74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750'

function Fail([string]$m) { throw $m }

# ---------------------------------------------------------------- interlock 1-3
$TargetRoot = [IO.Path]::GetFullPath($TargetRoot)
$exe = Join-Path $TargetRoot 'BEA.exe'
if (-not (Test-Path -LiteralPath $exe)) { Fail "No BEA.exe under $TargetRoot" }

$parts = $TargetRoot.Split([char]'\', [char]'/') | Where-Object { $_ }
for ($i = 0; $i -le ($parts.Count - 3); $i++) {
    if ($parts[$i] -ieq 'steamapps' -and $parts[$i + 1] -ieq 'common' -and
        $parts[$i + 2] -ieq 'Battle Engine Aquila') {
        Fail "Refusing to trace the Steam install. Use a copied target."
    }
}
foreach ($k in 'ProgramFiles', 'ProgramFiles(x86)') {
    $pf = [Environment]::GetEnvironmentVariable($k)
    if ($pf -and $TargetRoot.StartsWith(([IO.Path]::GetFullPath($pf)), [StringComparison]::OrdinalIgnoreCase)) {
        Fail "Refusing to trace a target under '$pf'. Use a copied target."
    }
}

$hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
if ($hash -ieq $PRISTINE_SHA256) {
    Fail ("Target is unmodified pristine BEA.exe. It runs fullscreen, which makes an " +
          "unattended recording unrecoverable on a single display. Apply force_windowed " +
          "(5 bytes at file offset 0x12A644) to the COPY first.")
}

# ------------------------------------------- interlock 4-5: mutual exclusion
# local-lab/safe-copy-bea-pristine/d3d9.dll exists ONLY while a d3d9 proxy capture
# is in flight; the capture scripts delete it in a finally block. Its presence is
# the lock. Two recorders in the same directory would fight over the same process.
$proxyLock = Join-Path $TargetRoot 'd3d9.dll'
if (Test-Path -LiteralPath $proxyLock) {
    Fail ("A d3d9 proxy capture appears to be in flight ('$proxyLock' exists). " +
          "Wait for it to finish; the capture scripts delete that file when they exit.")
}
$running = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
    Fail ("BEA.exe is already running (pid(s) " + (($running | ForEach-Object { $_.Id }) -join ', ') +
          "). Refusing to launch a second instance.")
}

# ------------------------------------------------ interlock 6-7: trace drive
$TraceRoot = [IO.Path]::GetFullPath($TraceRoot)
$driveLetter = [IO.Path]::GetPathRoot($TraceRoot).TrimEnd('\', ':')
if ($driveLetter -ine 'G') {
    Fail ("Traces must be written to G: (this machine's designated capture drive). " +
          "Refusing -TraceRoot '$TraceRoot'.")
}
$drive = Get-PSDrive -Name 'G' -ErrorAction Stop
$freeGB = [math]::Round($drive.Free / 1GB, 1)
if ($freeGB -lt $RequireFreeGB) {
    Fail "Only $freeGB GB free on G:; -RequireFreeGB is $RequireFreeGB."
}

# ---------------------------------------------------- locate the TTD recorder
# Two builds exist on this machine. Prefer an x86 build (matching the 32-bit
# target) whose full help and -stop control are available. The in-box
# System32\tttracer.exe is the same engine but suppresses its usage text.
$ttdCandidates = @(
    (Join-Path $TraceRoot 'ttd-x86\TTD.exe'),
    'G:\bea-ttd\ttd-x86\TTD.exe',
    'C:\Windows\SysWOW64\tttracer.exe',
    'C:\Windows\System32\tttracer.exe'
)
$ttd = $null
foreach ($c in $ttdCandidates) { if (Test-Path -LiteralPath $c) { $ttd = $c; break } }
if (-not $ttd) {
    Fail ("No TTD recorder found. Copy the x86 TTD from the WinDbg package: " +
          "Copy-Item -Recurse 'C:\Program Files\WindowsApps\Microsoft.WinDbg_*_x64__8wekyb3d8bbwe\x86\ttd' 'G:\bea-ttd\ttd-x86'")
}

# ------------------------------------------------- interlock 8: elevation
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$elevated = (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

$outDir = Join-Path $TraceRoot $Name
$traceFile = Join-Path $outDir ("{0}.run" -f $Name)

$ttdArgs = @('-accepteula', '-noUI', '-out', $traceFile, '-maxFile', "$MaxFileMB")
if ($Ring) { $ttdArgs += '-ring' }
foreach ($m in $Module) { $ttdArgs += @('-module', $m) }
# -launch must be the last option before the program and its arguments.
$ttdArgs += @('-launch', $exe) + $GameArguments

$commandPreview = ('& "{0}" {1}' -f $ttd, (($ttdArgs | ForEach-Object {
    if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ } }) -join ' '))

if ($DryRun) {
    [pscustomobject]@{
        DryRun = $true; Elevated = $elevated; TargetRoot = $TargetRoot; TargetSha256 = $hash
        Recorder = $ttd; RecorderVersion = (Get-Item -LiteralPath $ttd).VersionInfo.FileVersion
        TraceFile = $traceFile; FreeGB = $freeGB; Command = $commandPreview
    }
    return
}

if (-not $elevated) {
    Write-Host ""
    Write-Host "TTD recording requires an elevated token. This shell is NOT elevated." -ForegroundColor Yellow
    Write-Host "Measured non-elevated failure: 0x80070005 'Administrative privileges are required"
    Write-Host "in order to record program execution'."
    Write-Host ""
    Write-Host "The privilege required is SeDebugPrivilege, which a filtered token does not carry."
    Write-Host "There is no persistent fix: TTD's -initialize route needs TTDService.exe, which is"
    Write-Host "not present on this machine, so EVERY recording session needs its own elevation."
    Write-Host "Keep one elevated shell open for a whole capture session rather than elevating twice."
    Write-Host ""
    Write-Host "Run this script again from an elevated PowerShell:" -ForegroundColor Cyan
    Write-Host ("  pwsh -NoProfile -File `"{0}`" -Name {1} -Seconds {2}{3}" -f
        $PSCommandPath, $Name, $Seconds,
        $(if ($GameArguments.Count) { " -GameArguments " + (($GameArguments | ForEach-Object { "'$_'" }) -join ',') } else { '' }))
    Write-Host ""
    Write-Host "The raw recorder command it would run is:"
    Write-Host "  $commandPreview"
    Fail "Not elevated; refusing to raise a UAC consent dialog unattended."
}

$null = [IO.Directory]::CreateDirectory($outDir)

# ------------------------------------------------------------------ record
$startedUtc = (Get-Date).ToUniversalTime()
$recorder = Start-Process -FilePath $ttd -ArgumentList $ttdArgs -PassThru -NoNewWindow `
    -RedirectStandardOutput (Join-Path $outDir 'ttd-stdout.txt') `
    -RedirectStandardError  (Join-Path $outDir 'ttd-stderr.txt')

# Wait for the target to appear, then for the .run file to appear.
$target = $null
for ($i = 0; $i -lt 480; $i++) {
    $target = Get-Process -Name 'BEA' -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -ieq $exe }
    if ($target) { break }
    if ($recorder.HasExited) { break }
    Start-Sleep -Milliseconds 250
}
if (-not $target) {
    $err = if (Test-Path (Join-Path $outDir 'ttd-stdout.txt')) {
        (Get-Content -LiteralPath (Join-Path $outDir 'ttd-stdout.txt') -Raw) } else { '' }
    Fail "The copied target never started under TTD.`n$err"
}

$samples = [System.Collections.Generic.List[object]]::new()
$runFileSeenUtc = $null
$deadline = (Get-Date).AddSeconds($Seconds + 300)
$recordDeadline = $null

while ((Get-Date) -lt $deadline) {
    $len = 0
    if (Test-Path -LiteralPath $traceFile) { $len = (Get-Item -LiteralPath $traceFile).Length }
    else {
        $any = Get-ChildItem -LiteralPath $outDir -Filter '*.run' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($any) { $traceFile = $any.FullName; $len = $any.Length }
    }
    if ($len -gt 0 -and -not $runFileSeenUtc) {
        $runFileSeenUtc = (Get-Date).ToUniversalTime()
        $recordDeadline = (Get-Date).AddSeconds($Seconds)
    }
    if ($runFileSeenUtc) {
        $samples.Add([pscustomobject]@{
            SecondsIntoRecording = [math]::Round(((Get-Date).ToUniversalTime() - $runFileSeenUtc).TotalSeconds, 2)
            Bytes                = $len
            MB                   = [math]::Round($len / 1MB, 2)
        })
    }
    if ($recordDeadline -and (Get-Date) -ge $recordDeadline) { break }
    $t = Get-Process -Id $target.Id -ErrorAction SilentlyContinue
    if (-not $t) { break }
    # If the recorder itself gave up before a .run ever appeared, stop immediately
    # rather than sitting out the whole -Seconds + 300 budget on a dead run.
    if ($recorder.HasExited -and -not $runFileSeenUtc) { break }
    Start-Sleep -Seconds $SampleIntervalSeconds
}
if (-not $runFileSeenUtc) {
    $so = Join-Path $outDir 'ttd-stdout.txt'
    $msg = if (Test-Path -LiteralPath $so) { Get-Content -LiteralPath $so -Raw } else { '' }
    Write-Warning "No .run file ever appeared under $outDir. Recorder output follows:`n$msg"
}

# Stop tracing cleanly first so the trace is finalised, then close the game.
& $ttd -accepteula -stop $target.Id 2>&1 | Out-String | Write-Verbose
& $ttd -accepteula -wait 120        2>&1 | Out-String | Write-Verbose

Get-Process -Id $target.Id -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -ieq $exe } | Stop-Process -Force -ErrorAction SilentlyContinue
if (-not $recorder.HasExited) { $recorder.WaitForExit(60000) | Out-Null }

$final = if (Test-Path -LiteralPath $traceFile) { (Get-Item -LiteralPath $traceFile).Length } else { 0 }
$span = if ($runFileSeenUtc) { ((Get-Date).ToUniversalTime() - $runFileSeenUtc).TotalSeconds } else { 0 }
$rate = if ($span -gt 0) { [math]::Round(($final / 1MB) / $span, 2) } else { 0 }

$receipt = [pscustomobject]@{
    schemaVersion        = 'ttd-record-receipt.v1'
    name                 = $Name
    recordedAtUtc        = $startedUtc.ToString('o')
    recorder             = $ttd
    recorderVersion      = (Get-Item -LiteralPath $ttd).VersionInfo.FileVersion
    targetRoot           = $TargetRoot
    targetExe            = $exe
    targetSha256         = $hash
    gameArguments        = $GameArguments
    moduleRestriction    = $Module
    requestedSeconds     = $Seconds
    actualRecordSeconds  = [math]::Round($span, 2)
    traceFile            = $traceFile
    traceBytes           = $final
    traceMB              = [math]::Round($final / 1MB, 2)
    growthMBPerSecond    = $rate
    ring                 = [bool]$Ring
    maxFileMB            = $MaxFileMB
    samples              = $samples
}
$receiptPath = Join-Path $outDir 'receipt.json'
$receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding utf8

Write-Host ("trace  : {0} ({1} MB)" -f $traceFile, $receipt.traceMB)
Write-Host ("rate   : {0} MB/s over {1} s" -f $rate, $receipt.actualRecordSeconds)
Write-Host ("receipt: {0}" -f $receiptPath)
$receipt
