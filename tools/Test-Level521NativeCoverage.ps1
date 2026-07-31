# SPDX-License-Identifier: GPL-3.0-or-later
<#
.SYNOPSIS
Did the level-521 session work? Collect coverage over the session's traces and
print a checklist of the seventeen target MissionScript natives.

.DESCRIPTION
Two steps, neither of them reimplemented here:

  1. tools/Invoke-TtdCoverageCampaign.ps1 turns each .run into a coverage.jsonl
     plus a receipt. That runner already reads each trace's recorder receipt to
     decide -ExpectAliveAtStop, and always passes -QuarantineCounters; this
     script does not second-guess either.
  2. This script reads the resulting RECEIPTS and coverage ranges and reports
     which of the seventeen native handler entry bytes are now covered.

THE RECEIPT IS THE TRUTH. The campaign runner's own status labelling can call an
adjudicated Thread-stop 'failed' (task #155) - eight of the sixty-six corpus
levels were mislabelled that way and every one of them was valid. So nothing
here reads campaign-log.jsonl. Each per-trace receipt.json is opened directly and
judged on exitCode (0 clean, or 11 published-with-quarantined-counters) plus
terminalStop.terminalStopAccepted.

WHAT A HIT MEANS. A covered entry byte proves those bytes executed inside the
recorded window. It does not prove the named native is what ran - a shared or
tiny handler body can be reached from elsewhere. A MISS is non-observation
inside this window, never absence from the game.

Runs unattended, needs no elevation. Budget about four minutes per 6 GB trace
(the level521 opening's 5.71 GiB collected in 235 s).

.EXAMPLE
pwsh -File tools\Test-Level521NativeCoverage.ps1 -TracePattern 'level521-native-20260731-1830-take*'

.EXAMPLE
Re-read an already-collected output without running the collector again:

pwsh -File tools\Test-Level521NativeCoverage.ps1 -TracePattern 'level521-native-20260731-1830-take*' -SkipCollection
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    # Which recorded traces to score. Match the whole session:
    #   -TracePattern 'level521-native-<stamp>-take*'
    [Parameter(Mandatory = $true)][string]$TracePattern,

    [string]$TraceRoot = 'G:\bea-ttd',

    # Coverage output. One subdirectory per trace. Defaults to a name derived
    # from the pattern so two sessions never share an output root - the campaign
    # runner never re-runs a trace whose output directory already has a receipt.
    [string]$OutputRoot = '',

    # Passed straight through to the campaign runner. Needed when running from a
    # worktree, which has no build tree of its own.
    [string]$Collector = '',

    [string]$TargetExe = '',

    # The 144-row native registry. Used only to VERIFY the seventeen addresses
    # embedded below. Machine-local and gitignored; when it is absent the report
    # says the addresses are unverified rather than pretending otherwise.
    [string]$NativeTable = '',

    # Score existing coverage output without invoking the collector.
    [switch]$SkipCollection
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $false

$repo = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($TargetExe)) {
    $TargetExe = Join-Path $repo 'local-lab\safe-copy-bea-pristine\BEA.exe'
}
if ([string]::IsNullOrWhiteSpace($NativeTable)) {
    $NativeTable = Join-Path $repo 'local-lab\ghidra-from-trace-2026-07-28\script-native-table-144.tsv'
}
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $stem = ($TracePattern -replace '[^A-Za-z0-9._-]', '-').Trim('-')
    $OutputRoot = Join-Path $TraceRoot ("q-{0}" -f $stem)
}
$campaign = Join-Path $PSScriptRoot 'Invoke-TtdCoverageCampaign.ps1'

$IMAGE_BASE = 0x400000

# The seventeen natives that level 521's shipped scripts author and that no
# recorded opening ever executed. Handler addresses transcribed from
# local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv, which was
# decoded from the pristine specimen BEA.exe.original.backup, sha256
# 74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750, and are
# re-verified against that table below whenever it is present.
#
# 'trigger' is the player action that reaches the authoring block. See
# tools/RUNBOOK-level521-native-capture.md for the derivation.
$TARGETS = @(
    [pscustomobject]@{ Name = 'UnsetObjective';       Va = 0x00535EE0; Trigger = 'any turret, or the research station, dies' }
    [pscustomobject]@{ Name = 'ShutdownVariable';     Va = 0x00536330; Trigger = 'ALL EIGHT turrets destroyed' }
    [pscustomobject]@{ Name = 'GetX';                 Va = 0x00534B80; Trigger = 'research station destroyed (boss start, t+0s)' }
    [pscustomobject]@{ Name = 'GetY';                 Va = 0x00534C10; Trigger = 'research station destroyed (boss start, t+0s)' }
    [pscustomobject]@{ Name = 'GetZ';                 Va = 0x00534CA0; Trigger = 'research station destroyed (boss start, t+0s)' }
    [pscustomobject]@{ Name = 'SpawnParticle';        Va = 0x00536B70; Trigger = 'research station destroyed (boss start, t+0s)' }
    [pscustomobject]@{ Name = 'ResetSegmentHealth';   Va = 0x005354C0; Trigger = 'boss start + ~8s (27 calls)' }
    [pscustomobject]@{ Name = 'SetSegmentVulnerable'; Va = 0x00534300; Trigger = 'boss start + ~8s (27 calls)' }
    [pscustomobject]@{ Name = 'Die';                  Va = 0x00535CD0; Trigger = 'boss start + ~8s (hive support dies)' }
    [pscustomobject]@{ Name = 'GetMapHeight';         Va = 0x00534AC0; Trigger = 'boss start + ~10s (lift-off loop)' }
    [pscustomobject]@{ Name = 'SetZ';                 Va = 0x00534E50; Trigger = 'boss start + ~10s (lift-off loop)' }
    [pscustomobject]@{ Name = 'SetGoalPoint';         Va = 0x00534EE0; Trigger = 'boss start + ~10s (lift-off loop)' }
    [pscustomobject]@{ Name = 'PlayAnimationWait';    Va = 0x005351D0; Trigger = 'boss start + ~25-60s (first gnat release)' }
    [pscustomobject]@{ Name = 'GetGoodieState';       Va = 0x00533AA0; Trigger = 'HIVE BOSS KILLED (and >=25 gnats killed)' }
    [pscustomobject]@{ Name = 'SetGoodieState';       Va = 0x00533A70; Trigger = 'HIVE BOSS KILLED and >=25 gnats killed' }
    [pscustomobject]@{ Name = 'LevelWon';             Va = 0x005381E0; Trigger = 'HIVE BOSS KILLED' }
    [pscustomobject]@{ Name = 'LevelLostString';      Va = 0x005381C0; Trigger = 'LEVEL LOST (Marshall dies, or ground force wiped)' }
)

# SECOND PRIZE, free with the same window. These natives ARE in the corpus but
# rest on one to three level observations each, and the corpus analysis ranks
# verifying them above adding coverage. Level 521's boss cascade authors all of
# them, so a take-2 hit here is an independent second observation. Scored and
# reported separately; they are not part of the seventeen.
$BONUS = @(
    [pscustomobject]@{ Name = 'CreatePosition'; Va = 0x00534910; CorpusLevels = 1; Trigger = 'boss start, t+0s' }
    [pscustomobject]@{ Name = 'SpawnThing';     Va = 0x00536CD0; CorpusLevels = 1; Trigger = 'first gnat release' }
    [pscustomobject]@{ Name = 'Damage';         Va = 0x005348C0; CorpusLevels = 1; Trigger = 'fly your battle engine INTO the hive boss' }
    [pscustomobject]@{ Name = 'Rand';           Va = 0x00538230; CorpusLevels = 1; Trigger = 'hive boss killed (its children self-destruct)' }
    [pscustomobject]@{ Name = 'IsA';            Va = 0x00536350; CorpusLevels = 2; Trigger = 'fly your battle engine INTO the hive boss' }
    [pscustomobject]@{ Name = 'GetDistToObj';   Va = 0x00536070; CorpusLevels = 2; Trigger = 'boss moving (only if HiveMovement.msl is bound)' }
    [pscustomobject]@{ Name = 'PlayAnimation';  Va = 0x00535160; CorpusLevels = 2; Trigger = 'first gnat release' }
    [pscustomobject]@{ Name = 'SetAllegiance';  Va = 0x00535560; CorpusLevels = 5; Trigger = 'boss start + ~10s' }
    [pscustomobject]@{ Name = 'Activate';       Va = 0x00535D50; CorpusLevels = 6; Trigger = 'boss start + ~10s' }
)

function Fail([string]$Message) { throw $Message }

# ------------------------------------------------- verify the embedded addresses
$addressProvenance = 'UNVERIFIED - native registry not present on this machine'
if (Test-Path -LiteralPath $NativeTable) {
    $registry = @{}
    foreach ($line in [IO.File]::ReadAllLines($NativeTable)) {
        if ($line.StartsWith('#') -or [string]::IsNullOrWhiteSpace($line)) { continue }
        $fields = $line.Split("`t")
        if ($fields.Count -lt 4 -or $fields[0] -ceq 'index') { continue }
        $registry[$fields[3]] = [Convert]::ToUInt32($fields[2], 16)
    }
    $mismatches = @(foreach ($t in (@($TARGETS) + @($BONUS))) {
        if (-not $registry.ContainsKey($t.Name)) { "$($t.Name): absent from the registry" }
        elseif ($registry[$t.Name] -ne $t.Va) {
            "$($t.Name): registry 0x{0:X8} vs embedded 0x{1:X8}" -f $registry[$t.Name], $t.Va
        }
    })
    if ($mismatches.Count -gt 0) {
        Fail ("The embedded native addresses disagree with the registry. Refusing to score " +
              "against addresses that may be wrong.`n  " + ($mismatches -join "`n  "))
    }
    $addressProvenance = "verified against $NativeTable"
}

# ------------------------------------------------------------------- collect
if (-not $SkipCollection) {
    if (-not (Test-Path -LiteralPath $campaign)) { Fail "Missing campaign runner: $campaign" }
    Write-Host ''
    Write-Host 'COLLECTING COVERAGE' -ForegroundColor Cyan
    Write-Host ("  traces : {0}\{1}" -f $TraceRoot, $TracePattern)
    Write-Host ("  output : {0}" -f $OutputRoot)
    Write-Host '  (about four minutes per 6 GB trace)'
    Write-Host ''
    $campaignArguments = @{
        TraceRoot    = $TraceRoot
        TracePattern = $TracePattern
        OutputRoot   = $OutputRoot
        TargetExe    = $TargetExe
    }
    if (-not [string]::IsNullOrWhiteSpace($Collector)) {
        $campaignArguments['Collector'] = $Collector
    }
    $global:LASTEXITCODE = 0
    & $campaign @campaignArguments
    if ($LASTEXITCODE -ne 0) {
        # NOT fatal. The runner exits 1 when its own log has entries a human must
        # read, and task #155 makes that labelling untrustworthy for adjudicated
        # Thread-stops. The receipts below decide.
        Write-Warning ("The campaign runner exited $LASTEXITCODE. Per task #155 its status labels " +
                       'can be wrong for adjudicated Thread-stops; the receipts are scored below.')
    }
}

if (-not (Test-Path -LiteralPath $OutputRoot)) {
    Fail "No coverage output at $OutputRoot. Run without -SkipCollection first."
}

# ------------------------------------------------------------------ score
$ACCEPTABLE_EXIT = @(0, 11)
$perTrace = @()

foreach ($directory in (Get-ChildItem -LiteralPath $OutputRoot -Directory |
                        Where-Object { $_.Name -ne 'logs' } | Sort-Object Name)) {
    $receiptPath = Join-Path $directory.FullName 'receipt.json'
    $coveragePath = Join-Path $directory.FullName 'coverage.jsonl'
    $entry = [ordered]@{
        Trace = $directory.Name; Usable = $false; Reason = ''
        ExitCode = $null; StopAccepted = $null; Quarantined = $null
        Hits = @(); Misses = @(); BonusHits = @()
    }

    if (-not (Test-Path -LiteralPath $receiptPath)) {
        $entry.Reason = 'no receipt.json'
        $perTrace += [pscustomobject]$entry
        continue
    }
    $receipt = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json -Depth 30
    $schema = [string]$receipt.schemaVersion
    if ($schema -cne 'bea-ttd-exec-coverage-receipt.v2') {
        $entry.Reason = "unsupported receipt schema '$schema'"
        $perTrace += [pscustomobject]$entry
        continue
    }

    $exit = if ($null -ne $receipt.PSObject.Properties['exitCode']) { [int]$receipt.exitCode }
            else { [int]$receipt.collectorExitCode }
    $stopAccepted = [bool]$receipt.terminalStop.terminalStopAccepted
    $entry.ExitCode = $exit
    $entry.StopAccepted = $stopAccepted
    $entry.Quarantined = [bool]$receipt.countersQuarantined

    if ($ACCEPTABLE_EXIT -notcontains $exit) { $entry.Reason = "receipt exitCode $exit" }
    elseif (-not $stopAccepted)              { $entry.Reason = 'terminal stop not accepted' }
    elseif (-not (Test-Path -LiteralPath $coveragePath)) { $entry.Reason = 'no coverage.jsonl' }

    if ($entry.Reason) { $perTrace += [pscustomobject]$entry; continue }

    # Load the half-open RVA ranges. 7,073 ranges for a 6 GB trace, so a sorted
    # array plus a binary search is more than enough.
    $starts = [System.Collections.Generic.List[uint32]]::new()
    $ends = [System.Collections.Generic.List[uint32]]::new()
    foreach ($line in [IO.File]::ReadLines($coveragePath)) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $object = $line | ConvertFrom-Json
        if ([string]$object.kind -cne 'range') { continue }
        $starts.Add([Convert]::ToUInt32([string]$object.rva_start, 16))
        $ends.Add([Convert]::ToUInt32([string]$object.rva_end_exclusive, 16))
    }
    $startArray = $starts.ToArray()
    $endArray = $ends.ToArray()
    [array]::Sort($startArray, $endArray)

    $hits = @(); $misses = @(); $bonusHits = @()
    foreach ($t in (@($TARGETS) + @($BONUS))) {
        $rva = [uint32]($t.Va - $IMAGE_BASE)
        $index = [array]::BinarySearch($startArray, $rva)
        if ($index -lt 0) { $index = (-$index) - 2 }
        $covered = ($index -ge 0 -and $rva -lt $endArray[$index])
        if ($BONUS.Name -contains $t.Name) {
            if ($covered) { $bonusHits += $t.Name }
        }
        elseif ($covered) { $hits += $t.Name }
        else { $misses += $t.Name }
    }
    $entry.Usable = $true
    $entry.Hits = $hits
    $entry.Misses = $misses
    $entry.BonusHits = $bonusHits
    $perTrace += [pscustomobject]$entry
}

# ------------------------------------------------------------------ report
$usable = @($perTrace | Where-Object Usable)
$union = [System.Collections.Generic.HashSet[string]]::new()
$bonusUnion = [System.Collections.Generic.HashSet[string]]::new()
foreach ($t in $usable) {
    foreach ($h in $t.Hits) { $null = $union.Add($h) }
    foreach ($h in $t.BonusHits) { $null = $bonusUnion.Add($h) }
}

Write-Host ''
Write-Host '================================================================' -ForegroundColor Cyan
Write-Host '  LEVEL 521 TARGET NATIVES - DID THE SESSION REACH THEM?' -ForegroundColor Cyan
Write-Host '================================================================' -ForegroundColor Cyan
Write-Host ("  coverage output : {0}" -f $OutputRoot)
Write-Host ("  traces scored   : {0} usable of {1}" -f $usable.Count, $perTrace.Count)
Write-Host ("  handler addrs   : {0}" -f $addressProvenance)
Write-Host ''

foreach ($t in $perTrace) {
    if ($t.Usable) {
        Write-Host ("  {0}: OK (exit {1}, stop accepted, {2}/17 hit)" -f
            $t.Trace, $t.ExitCode, $t.Hits.Count) -ForegroundColor Green
    } else {
        Write-Host ("  {0}: UNUSABLE - {1}" -f $t.Trace, $t.Reason) -ForegroundColor Red
    }
}

if ($usable.Count -eq 0) {
    Write-Host ''
    Write-Warning 'No usable coverage. Nothing can be said about the seventeen natives.'
    exit 1
}

Write-Host ''
Write-Host '  CHECKLIST (union over every usable trace in this session)'
Write-Host '  ---------------------------------------------------------------'
foreach ($t in $TARGETS) {
    $covered = $union.Contains($t.Name)
    $mark = if ($covered) { '[x]' } else { '[ ]' }
    $colour = if ($covered) { 'Green' } else { 'DarkGray' }
    Write-Host ("  {0} {1,-21} 0x{2:X8}  {3}" -f $mark, $t.Name, $t.Va, $t.Trigger) -ForegroundColor $colour
}
Write-Host '  ---------------------------------------------------------------'
Write-Host ("  {0} of {1} covered." -f $union.Count, $TARGETS.Count) -ForegroundColor Cyan

Write-Host ''
Write-Host '  SECOND OBSERVATIONS for thinly-evidenced natives (not part of the 17)'
Write-Host '  ---------------------------------------------------------------'
foreach ($t in $BONUS) {
    $covered = $bonusUnion.Contains($t.Name)
    $mark = if ($covered) { '[x]' } else { '[ ]' }
    $colour = if ($covered) { 'Green' } else { 'DarkGray' }
    Write-Host ("  {0} {1,-15} 0x{2:X8}  corpus levels: {3}  {4}" -f
        $mark, $t.Name, $t.Va, $t.CorpusLevels, $t.Trigger) -ForegroundColor $colour
}
Write-Host '  ---------------------------------------------------------------'
Write-Host ("  {0} of {1} corroborated." -f $bonusUnion.Count, $BONUS.Count) -ForegroundColor Cyan

Write-Host ''
Write-Host '  A HIT proves those entry bytes executed in the recorded window. It does'
Write-Host '  not prove the named native is what ran. A MISS is non-observation inside'
Write-Host '  this window, never absence from the game.'
Write-Host ''

[pscustomobject]@{
    outputRoot        = $OutputRoot
    tracesScored      = $perTrace.Count
    tracesUsable      = $usable.Count
    addressProvenance = $addressProvenance
    covered           = @($TARGETS | Where-Object { $union.Contains($_.Name) } | ForEach-Object Name)
    notCovered        = @($TARGETS | Where-Object { -not $union.Contains($_.Name) } | ForEach-Object Name)
    coveredCount      = $union.Count
    targetCount       = $TARGETS.Count
    bonusCovered      = @($BONUS | Where-Object { $bonusUnion.Contains($_.Name) } | ForEach-Object Name)
    bonusCoveredCount = $bonusUnion.Count
    bonusCount        = $BONUS.Count
    perTrace          = $perTrace
}
