<#
.SYNOPSIS
    Stage-1 coverage over a directory of immutable TTD traces, one at a time.

.DESCRIPTION
    Drives tools/Invoke-TtdExecCoverage.ps1 across every trace directory
    matching -TracePattern under -TraceRoot, sequentially.

    Sequential is a measurement, not a preference.  The two-trace pilot
    (local-lab/TTD-PILOT-2026-07-31.md, 2026-07-31) ran the same trace and the
    same work solo and 2-way parallel and got a speedup of 0.96x: two concurrent
    jobs each run ~1.77x slower and the pair finishes no sooner than running
    them one after the other, because the binding constraint is the
    USB-attached G: volume rather than the 24 logical processors.  Do not add a
    parallel scheduler; it makes the campaign slower and the timings unreadable.

    Three rules this runner does not bend:

    * Traces are IMMUTABLE.  Nothing is ever written inside a trace directory -
      not coverage, not logs, not an index.  Every output goes to a new
      directory under -OutputRoot, and the runner refuses to start if that root
      resolves inside any selected trace directory.
    * Resumable and NEVER retrying.  A level whose output directory already
      holds a receipt is decided from that receipt and skipped, whether the
      recorded outcome was acceptable or not.  A failure is recorded once and
      left alone; a loop that retries a failing trace turns a 4-hour campaign
      into an infinite one and buries the evidence.
    * steps_executed is not evidence.  TTD Replay 1.11.584.0 stops advancing
      its own step accounting on some traces (task #149), so the per-trace
      density metrics logged here are derived from trace bytes, sequence
      counts, and gap events - never from a step count.
    * The receipt is the truth and this log is derived from it.  Status comes
      from the receipt's resolved exitCode, never from $LASTEXITCODE (see the
      cross-check below), and -RebuildLogFromReceipts regenerates the whole log
      from the receipts already on disk rather than editing a line in place.

.NOTES
    Run this yourself; it is unattended, needs no elevation, and the pilot
    measured ~230 s per trace.  The campaign log is the product: one JSON line
    per trace, appended, in the order the traces were processed.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$TraceRoot = 'G:\bea-ttd',

    [string]$TracePattern = 'level-opening-3m-v1-level*',

    [string]$OutputRoot = 'G:\bea-ttd\q-campaign-coverage-v1',

    [string]$TargetExe = (Join-Path $PSScriptRoot '..\local-lab\safe-copy-bea-pristine\BEA.exe'),

    [string]$CoverageWrapper = (Join-Path $PSScriptRoot 'Invoke-TtdExecCoverage.ps1'),

    # Passed straight through when set; otherwise the wrapper resolves its own
    # default collector.  Kept as a parameter because a worktree has no build
    # tree of its own.
    [string]$Collector = '',

    [string]$ModuleName = 'BEA.exe',

    # The pilot's markers: CThing__Init must execute, and an RVA that must not.
    [string[]]$MustHitRva = @('0xF34A0'),
    [string[]]$MustMissRva = @('0x2D150'),

    [switch]$Sequential,

    # Regenerate campaign-log.jsonl from the coverage receipts already on disk
    # and collect nothing.  The log is derived data; when its status labels are
    # wrong the fix is to re-derive every line from the receipts, not to edit
    # the lines that look wrong.  The superseded log is kept beside the new one.
    [switch]$RebuildLogFromReceipts,

    # Smoke-test lever: process at most N traces this pass.  0 means all.
    [int]$MaxTraces = 0,

    # Deterministic in both modes.  Size orders smallest-first, which gets the
    # most traces done per hour if the campaign is interrupted (cost is linear
    # in trace bytes to within 1.7%); Name is stable without touching the
    # volume at all.
    [ValidateSet('Name', 'Size')]
    [string]$Order = 'Name'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# The wrapper legitimately exits non-zero (11) on a published-but-quarantined
# run.  Never let a child exit code become a terminating error here.
$PSNativeCommandUseErrorActionPreference = $false

# What the campaign accepts from a coverage run.
#   0  clean pass
#   11 ranges published, replay counters quarantined as poisoned evidence (#149)
# Exit 10 - the collector refusing the run - is NOT acceptable.  For the
# alive-at-stop trace class it should no longer occur at all, because the
# wrapper adjudicates that stop reason when told to; if it still appears, the
# failing clause is something other than the terminal event and wants a human.
$AcceptableExitCodes = @(0, 11)

$CampaignSchema = 'bea.ttd.coverage-campaign.v1'

function ConvertTo-PositionSequence {
    # "0x20DE12:0x5B8" -> 2154002.  The sequence component of a TTD position is
    # the campaign's busy-ness denominator.
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text,
        [Parameter(Mandatory = $true)][string]$Field
    )

    if ($Text -notmatch '^0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+$') {
        throw "$Field is not a TTD position: '$Text'"
    }
    return [uint64]::Parse(
        $Text.Split(':')[0].Substring(2),
        [System.Globalization.NumberStyles]::HexNumber)
}

function Test-PathIsUnder {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Ancestor
    )

    $normalized = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    $root = [System.IO.Path]::GetFullPath($Ancestor).TrimEnd('\', '/')
    if ($normalized -ieq $root) {
        return $true
    }
    return $normalized.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-RatioOrNull {
    param([uint64]$Numerator, [uint64]$Denominator)

    if ($Denominator -eq 0) { return $null }
    return [math]::Round(($Numerator / $Denominator), 3)
}

function Get-Field {
    # Absent stays absent.  A receipt that does not carry a field must log a
    # null, never a zero that reads like a measurement.
    param($Owner, [string]$Name)

    if ($null -eq $Owner) { return $null }
    $property = $Owner.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Get-UInt64Field {
    param($Owner, [string]$Name)

    $value = Get-Field -Owner $Owner -Name $Name
    if ($null -eq $value) { return $null }
    $text = [string]$value
    if ($text -notmatch '^[0-9]+$') { return $null }
    return [uint64]::Parse($text)
}

function Resolve-RecorderTraceHash {
    # THE RECORDER RECEIPT'S TRACE HASH, ADJUDICATED FAIL-CLOSED.
    #
    # tools/ttd_record.ps1 may now write a receipt whose traceSha256 is null,
    # when the trace was demonstrably finished but TTD still held the file at the
    # end of the unlock budget.  That receipt is honestly marked
    # traceHashState = 'deferred' with a hashDeferred block, and it exists so a
    # valid trace does not vanish from the pipeline - not so the null can stand
    # in for a hash.
    #
    # An absent hash and a deferred hash are BOTH unusable here.  The difference
    # is only in what the operator is told to do about it.
    param([Parameter(Mandatory = $true)]$Receipt)

    $rawHash = Get-Field -Owner $Receipt -Name 'traceSha256'
    $hash = if ($null -eq $rawHash) { '' } else { ([string]$rawHash).Trim() }
    $rawState = Get-Field -Owner $Receipt -Name 'traceHashState'
    $declaredState = if ($null -eq $rawState) { '' } else { ([string]$rawState).Trim() }
    $hasDeferral = ($null -ne (Get-Field -Owner $Receipt -Name 'hashDeferred'))
    $looksReal = [bool]($hash -match '^[0-9A-Fa-f]{64}$')

    $state =
        if ($looksReal -and ($declaredState -ceq 'deferred' -or $hasDeferral)) { 'contradictory' }
        elseif ($looksReal) { 'present' }
        elseif ($declaredState -ceq 'deferred') { 'deferred' }
        elseif ($hasDeferral) { 'contradictory' }
        else { 'absent' }

    $reason =
        if ($state -ceq 'present') { '' }
        elseif ($state -ceq 'deferred') {
            'recorder receipt defers its trace hash (traceHashState=deferred); ' +
            'complete it with tools/ttd_record.ps1 -HashOnly -TraceDirectory ' +
            '<trace dir> before collecting coverage'
        }
        elseif ($state -ceq 'contradictory') {
            "recorder receipt contradicts itself about its trace hash " +
            "(traceHashState='$declaredState', hash present=$looksReal, " +
            "hashDeferred block=$hasDeferral)"
        }
        else {
            'recorder receipt has no usable traceSha256'
        }

    return [pscustomobject]@{
        state  = $state
        sha256 = if ($state -ceq 'present') { $hash.ToUpperInvariant() } else { $null }
        usable = ($state -ceq 'present')
        reason = $reason
    }
}

function Get-ReceiptExitCode {
    # The wrapper's RESOLVED exit code: what the run actually amounts to after
    # the terminal-stop adjudication.  Falls back to the collector's raw code
    # only for a receipt that predates the resolved field.
    param($Receipt)

    $value = Get-Field -Owner $Receipt -Name 'exitCode'
    if ($null -eq $value) {
        $value = Get-Field -Owner $Receipt -Name 'collectorExitCode'
    }
    if ($null -eq $value) { return $null }
    return [int]$value
}

function Get-ExpectedProcessExit {
    # What $LASTEXITCODE must hold after an IN-PROCESS `& $wrapper` call.
    #
    # THIS IS THE #155 BUG.  An in-process script only sets $LASTEXITCODE by
    # calling `exit`; the wrapper calls `exit` only for a non-zero resolved
    # code.  On a clean run it falls off the end and leaves behind whatever the
    # last NATIVE command set - the collector EXE's raw exit, which is 10 on an
    # adjudicated alive-at-stop trace.  Comparing that raw 10 against the
    # receipt's resolved 0 labelled 8 of 66 sound traces 'failed' in the first
    # full campaign.  Raw-vs-resolved was never the pair that must agree.
    param([Parameter(Mandatory = $true)][int]$ReceiptExit, $ReceiptCollectorExit)

    if ($ReceiptExit -ne 0) { return $ReceiptExit }
    if ($null -eq $ReceiptCollectorExit) { return 0 }
    return [int]$ReceiptCollectorExit
}

function Add-ReceiptDerivedField {
    # Every field of a campaign line that the coverage receipt already knows.
    # One projection, used by the live pass and by -RebuildLogFromReceipts, so
    # a regenerated log cannot drift in shape from a collected one.
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Record,
        [Parameter(Mandatory = $true)]$Receipt
    )

    $coverageBlock = Get-Field -Owner $Receipt -Name 'coverage'
    $summaryBlock = Get-Field -Owner $Receipt -Name 'summary'
    $metadataBlock = Get-Field -Owner $Receipt -Name 'metadata'
    $gapBlock = Get-Field -Owner $Receipt -Name 'gapSummary'
    $terminalStopBlock = Get-Field -Owner $Receipt -Name 'terminalStop'

    $Record['exitCode'] = Get-ReceiptExitCode -Receipt $Receipt
    $collectorExit = Get-Field -Owner $Receipt -Name 'collectorExitCode'
    $Record['collectorExitCode'] =
        if ($null -ne $collectorExit) { [int]$collectorExit } else { $null }
    $Record['rangeCount'] = [int](Get-Field -Owner $coverageBlock -Name 'rangeCount')
    $Record['coveredBytes'] =
        [string](Get-Field -Owner $summaryBlock -Name 'covered_bytes')
    $Record['countersQuarantined'] =
        [bool](Get-Field -Owner $Receipt -Name 'countersQuarantined')
    $Record['stopReason'] =
        [string](Get-Field -Owner $terminalStopBlock -Name 'stopReason')
    $Record['stopReasonAdjudicated'] =
        [bool](Get-Field -Owner $Receipt -Name 'stopReasonAdjudicated')
    $Record['terminalStopAccepted'] =
        [bool](Get-Field -Owner $terminalStopBlock -Name 'terminalStopAccepted')
    $Record['replayComplete'] = [bool](Get-Field -Owner $Receipt -Name 'replayComplete')
    $Record['markerAssertionsPassed'] =
        [bool](Get-Field -Owner $Receipt -Name 'markerAssertionsPassed')
    $Record['coverageSha256'] = [string](Get-Field -Owner $coverageBlock -Name 'sha256')

    # Density, the #149 stop predictor.  Derived from trace bytes, sequence
    # counts, and gap events only: this engine's step accounting is the thing
    # under suspicion, so it is never an input here.
    $traceBytes = Get-UInt64Field -Owner $metadataBlock -Name 'trace_bytes'
    $sequences = ConvertTo-PositionSequence `
        -Text ([string](Get-Field -Owner $metadataBlock -Name 'lifetime_max')) `
        -Field 'lifetime_max'
    $gapEvents = Get-UInt64Field -Owner $gapBlock -Name 'total'
    $Record['density'] = [ordered]@{
        traceBytes = if ($null -ne $traceBytes) { [string]$traceBytes } else { $null }
        sequences = [string]$sequences
        traceBytesPerSequence =
            if ($null -ne $traceBytes) {
                Get-RatioOrNull -Numerator $traceBytes -Denominator $sequences
            } else { $null }
        gapEvents = if ($null -ne $gapEvents) { [string]$gapEvents } else { $null }
        gapEventsPerSequence =
            if ($null -ne $gapEvents) {
                Get-RatioOrNull -Numerator $gapEvents -Denominator $sequences
            } else { $null }
        kindLarge = Get-Field -Owner $gapBlock -Name 'kind_large'
        kindUnrecorded = Get-Field -Owner $gapBlock -Name 'kind_unrecorded'
        kindContextSwitch = Get-Field -Owner $gapBlock -Name 'kind_context_switch'
        eventKernelCall = Get-Field -Owner $gapBlock -Name 'event_KernelCall'
        eventSyntheticFallback =
            Get-Field -Owner $gapBlock -Name 'event_SyntheticFallback'
    }
}

function New-UniqueLogPath {
    # Never overwrite the console transcript of an earlier attempt.
    param([string]$Directory, [string]$Stem)

    $candidate = Join-Path $Directory "$Stem.txt"
    $index = 2
    while (Test-Path -LiteralPath $candidate) {
        $candidate = Join-Path $Directory "$Stem-$index.txt"
        $index++
    }
    return $candidate
}

$traceRootPath = (Resolve-Path -LiteralPath $TraceRoot).Path
if (-not (Test-Path -LiteralPath $traceRootPath -PathType Container)) {
    throw "Trace root is not a directory: $traceRootPath"
}
# A rebuild pass opens no trace, starts no replay, and touches no binary: it
# reads receipts.  Demanding a wrapper, a target, or a collector would make the
# log un-rebuildable on any machine that no longer has them.
$wrapperPath = ''
$targetPath = ''
$collectorPath = ''
if (-not $RebuildLogFromReceipts) {
    $wrapperPath = (Resolve-Path -LiteralPath $CoverageWrapper).Path
    if (-not (Test-Path -LiteralPath $wrapperPath -PathType Leaf)) {
        throw "Coverage wrapper was not found: $wrapperPath"
    }
    $targetPath = (Resolve-Path -LiteralPath $TargetExe).Path
    if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) {
        throw "Target executable was not found: $targetPath"
    }
    if (-not [string]::IsNullOrWhiteSpace($Collector)) {
        $collectorPath = (Resolve-Path -LiteralPath $Collector).Path
    }
}

$outputRootPath = [System.IO.Path]::GetFullPath($OutputRoot)
if (Test-PathIsUnder -Path $outputRootPath -Ancestor $traceRootPath) {
    # G:\bea-ttd is the trace root and also where sibling output directories
    # live, so being under the root is fine - being inside a TRACE directory is
    # not.  That case is caught per trace below, before anything is written.
    Write-Verbose "Output root sits under the trace root: $outputRootPath"
}

$traceDirectories = @(
    Get-ChildItem -LiteralPath $traceRootPath -Directory -Filter $TracePattern |
        Sort-Object -Property Name
)
if ($traceDirectories.Count -eq 0) {
    throw "No trace directories match '$TracePattern' under $traceRootPath."
}
foreach ($directory in $traceDirectories) {
    if (Test-PathIsUnder -Path $outputRootPath -Ancestor $directory.FullName) {
        throw (
            'Refusing to run: the output root would be inside the trace ' +
            "directory $($directory.FullName). Traces are immutable."
        )
    }
}

if ($Order -ceq 'Size') {
    $traceDirectories = @(
        $traceDirectories |
            Sort-Object -Property @{
                Expression = {
                    $run = @(Get-ChildItem -LiteralPath $_.FullName -Filter '*.run' -File)
                    if ($run.Count -eq 1) { [int64]$run[0].Length } else { [int64]::MaxValue }
                }
            }, Name
    )
}

$selected = $traceDirectories
if ($MaxTraces -gt 0) {
    $selected = @($traceDirectories | Select-Object -First $MaxTraces)
}

[System.IO.Directory]::CreateDirectory($outputRootPath) | Out-Null
$logDirectory = Join-Path $outputRootPath 'logs'
[System.IO.Directory]::CreateDirectory($logDirectory) | Out-Null
$campaignLogPath = Join-Path $outputRootPath 'campaign-log.jsonl'
$utf8 = [System.Text.UTF8Encoding]::new($false)

function Write-CampaignLine {
    param([Parameter(Mandatory = $true)][System.Collections.IDictionary]$Record)

    # Every line closes with a timestamp, including the ones that end early.
    if (-not $Record.Contains('finishedAtUtc')) {
        $Record['finishedAtUtc'] = (Get-Date).ToUniversalTime().ToString('o')
    }
    $json = ([pscustomobject]$Record | ConvertTo-Json -Depth 8 -Compress)
    [System.IO.File]::AppendAllText($campaignLogPath, $json + "`n", $utf8)
    return $json
}

# A rebuild replaces the log wholesale.  The superseded file is moved aside,
# never deleted and never edited in place: if the re-derivation is itself wrong,
# the original labels are still on disk to prove it.
$carriedForward = @{}
if ($RebuildLogFromReceipts) {
    if (Test-Path -LiteralPath $campaignLogPath -PathType Leaf) {
        foreach ($line in [System.IO.File]::ReadLines($campaignLogPath)) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            $row = $line | ConvertFrom-Json -Depth 20
            if ($null -ne $row.PSObject.Properties['kind']) { continue }
            $rowLevel = [string](Get-Field -Owner $row -Name 'level')
            if ([string]::IsNullOrWhiteSpace($rowLevel)) { continue }
            # Last line wins: a resumed campaign appends, so the newest entry
            # for a level is the one that described the run that stands.
            $carriedForward[$rowLevel] = $row
        }
        $supersededPath = Join-Path $outputRootPath (
            'campaign-log.superseded-{0}.jsonl' -f
            (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ'))
        [System.IO.File]::Move($campaignLogPath, $supersededPath)
        Write-Host ("campaign: superseded log moved to {0}" -f $supersededPath)
    }
    Write-Host ("campaign: rebuilding {0} from receipts under {1}" -f
        $campaignLogPath, $outputRootPath)
}

Write-Host ("campaign: {0} trace directories selected of {1} matched; output {2}" -f
    $selected.Count, $traceDirectories.Count, $outputRootPath)

$counts = [ordered]@{ ok = 0; skipped = 0; blocked = 0; failed = 0 }
$campaignStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($directory in $selected) {
    $level = $directory.Name
    $levelStartedAt = (Get-Date).ToUniversalTime()
    $record = [ordered]@{
        schema = $CampaignSchema
        level = $level
        traceDirectory = $directory.FullName
        startedAtUtc = $levelStartedAt.ToString('o')
        status = 'failed'
        reason = ''
        exitCode = $null
        wallSeconds = $null
    }

    try {
        $outputDirectory = Join-Path $outputRootPath $level
        $record['outputDirectory'] = $outputDirectory

        $runFiles = @(Get-ChildItem -LiteralPath $directory.FullName -Filter '*.run' -File)
        if ($runFiles.Count -ne 1) {
            $record['status'] = 'blocked'
            $record['reason'] = "expected exactly one .run file, found $($runFiles.Count)"
            $counts['blocked']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: BLOCKED - {1}" -f $level, $record['reason'])
            continue
        }
        $tracePath = $runFiles[0].FullName
        $record['traceFile'] = $tracePath
        $record['traceBytes'] = [string]$runFiles[0].Length

        # The trace's own recorder receipt is the ONLY authority for the trace
        # class.  The expectation is read from it, never inferred from what the
        # replay happened to do.
        $recorderReceiptPath = Join-Path $directory.FullName 'receipt.json'
        if (-not (Test-Path -LiteralPath $recorderReceiptPath -PathType Leaf)) {
            $record['status'] = 'blocked'
            $record['reason'] = 'trace directory has no recorder receipt.json'
            $counts['blocked']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: BLOCKED - {1}" -f $level, $record['reason'])
            continue
        }
        $recorder = Get-Content -Raw -LiteralPath $recorderReceiptPath |
            ConvertFrom-Json -Depth 20
        $recorderSchema = [string]$recorder.schemaVersion
        if ($recorderSchema -cne 'ttd-record-receipt.v3') {
            $record['status'] = 'blocked'
            $record['reason'] = "unsupported recorder receipt schema '$recorderSchema'"
            $counts['blocked']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: BLOCKED - {1}" -f $level, $record['reason'])
            continue
        }
        $guestOutcomeProperty = $recorder.PSObject.Properties['guestOutcome']
        if ($null -eq $guestOutcomeProperty -or
            [string]::IsNullOrWhiteSpace([string]$guestOutcomeProperty.Value)) {
            $record['status'] = 'blocked'
            $record['reason'] = 'recorder receipt has no guestOutcome'
            $counts['blocked']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: BLOCKED - {1}" -f $level, $record['reason'])
            continue
        }
        $guestOutcome = [string]$guestOutcomeProperty.Value
        $expectAliveAtStop = ($guestOutcome -ceq 'alive-at-stop')
        $record['guestOutcome'] = $guestOutcome
        $record['expectAliveAtStop'] = $expectAliveAtStop
        $recordedHash = Resolve-RecorderTraceHash -Receipt $recorder
        $record['recordedTraceSha256'] = $recordedHash.sha256
        $record['recordedTraceHashState'] = $recordedHash.state

        # RESUME.  An output directory that already holds a receipt decides
        # this level - acceptable or not - and is never re-run.
        $existingReceiptPath = Join-Path $outputDirectory 'receipt.json'
        if (Test-Path -LiteralPath $outputDirectory) {
            if (Test-Path -LiteralPath $existingReceiptPath -PathType Leaf) {
                $existing = Get-Content -Raw -LiteralPath $existingReceiptPath |
                    ConvertFrom-Json -Depth 30
                $existingExit = Get-ReceiptExitCode -Receipt $existing
                $record['exitCode'] = $existingExit
                if ($RebuildLogFromReceipts) {
                    # Re-derive the whole line.  The receipt decides the status
                    # exactly as it does on a live pass; the three fields only
                    # the runner ever observed are carried across from the
                    # superseded log so the rebuild loses no evidence.
                    Add-ReceiptDerivedField -Record $record -Receipt $existing
                    $prior = $carriedForward[$level]
                    foreach ($field in @('startedAtUtc', 'wallSeconds', 'consoleLog')) {
                        $value = Get-Field -Owner $prior -Name $field
                        if ($null -ne $value) { $record[$field] = $value }
                    }
                    if ($null -eq (Get-Field -Owner $prior -Name 'consoleLog')) {
                        $consoleCandidate =
                            Join-Path $logDirectory "$level-console.txt"
                        if (Test-Path -LiteralPath $consoleCandidate -PathType Leaf) {
                            $record['consoleLog'] = $consoleCandidate
                        }
                    }
                    $record['rebuiltFromReceipt'] = $true
                    $record['rebuiltAtUtc'] =
                        (Get-Date).ToUniversalTime().ToString('o')
                    if ($null -ne $existingExit -and
                        $AcceptableExitCodes -contains $existingExit) {
                        $record['status'] = 'ok'
                        $record['reason'] = ''
                        $counts['ok']++
                    } else {
                        $record['status'] = 'failed'
                        $record['reason'] = "coverage run exited $existingExit"
                        $counts['failed']++
                    }
                } elseif ($null -ne $existingExit -and
                    $AcceptableExitCodes -contains $existingExit) {
                    $record['status'] = 'skipped'
                    $record['reason'] = "already collected with exit $existingExit"
                    $counts['skipped']++
                } else {
                    $record['status'] = 'blocked'
                    $record['reason'] =
                        "existing receipt records exit $existingExit; not retrying"
                    $counts['blocked']++
                }
            } else {
                $record['status'] = 'blocked'
                $record['reason'] =
                    'output directory exists without a receipt; left untouched'
                $counts['blocked']++
            }
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: {1} - {2}" -f
                $level, $record['status'].ToUpperInvariant(), $record['reason'])
            continue
        }

        if ($RebuildLogFromReceipts) {
            # Nothing was ever collected for this level.  A rebuild reports
            # that; it does not go and collect it.
            $record['status'] = 'blocked'
            $record['reason'] = 'no coverage output directory to rebuild from'
            $counts['blocked']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: BLOCKED - {1}" -f $level, $record['reason'])
            continue
        }

        # FAIL CLOSED ON A RECORDER RECEIPT THAT CANNOT NAME ITS TRACE.
        #
        # Deliberately AFTER the resume block above: a level already collected
        # against a hash that was usable at the time keeps its result.  This
        # gates only a FRESH collection, where publishing coverage attributed to
        # a trace the receipt cannot identify would put an unbindable artefact
        # into the evidence store.
        #
        # A deferred hash is recoverable without re-recording, and the reason
        # string carries the exact command, so a blocked level is one repair away
        # from collecting on the next resume pass.
        if (-not $recordedHash.usable) {
            $record['status'] = 'blocked'
            $record['reason'] = $recordedHash.reason
            $counts['blocked']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: BLOCKED - {1}" -f $level, $record['reason'])
            continue
        }

        $wrapperArguments = @{
            TraceFile = $tracePath
            TargetExe = $targetPath
            OutputDirectory = $outputDirectory
            ModuleName = $ModuleName
            MustHitRva = $MustHitRva
            MustMissRva = $MustMissRva
            QuarantineCounters = $true
        }
        if (-not [string]::IsNullOrWhiteSpace($collectorPath)) {
            $wrapperArguments['Collector'] = $collectorPath
        }
        if ($Sequential) {
            $wrapperArguments['Sequential'] = $true
        }
        if ($expectAliveAtStop) {
            $wrapperArguments['ExpectAliveAtStop'] = $true
        }
        $record['quarantineCounters'] = $true
        $record['sequentialReplay'] = [bool]$Sequential

        Write-Host ("  {0}: collecting (expectAliveAtStop={1}) ..." -f
            $level, $expectAliveAtStop)

        # A script invoked with & runs in this process but its `exit` only ends
        # that script and sets $LASTEXITCODE.  Reset first: a wrapper run that
        # falls off the end without calling exit leaves the PREVIOUS value in
        # place, and a stale success code is exactly the sort of quiet lie this
        # pipeline exists to refuse.  The receipt is cross-checked against it
        # below, so a disagreement fails the trace rather than the campaign.
        $global:LASTEXITCODE = 0
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $captured = & $wrapperPath @wrapperArguments *>&1
        $stopwatch.Stop()
        $observedExit = $LASTEXITCODE
        $record['wallSeconds'] = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)

        $consolePath = New-UniqueLogPath -Directory $logDirectory -Stem "$level-console"
        [System.IO.File]::WriteAllText(
            $consolePath,
            ($captured | Out-String),
            $utf8)
        $record['consoleLog'] = $consolePath

        if (-not (Test-Path -LiteralPath $existingReceiptPath -PathType Leaf)) {
            $record['status'] = 'failed'
            $record['exitCode'] = $observedExit
            $record['reason'] =
                "coverage wrapper exited $observedExit without writing a receipt"
            $counts['failed']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: FAILED - {1}" -f $level, $record['reason'])
            continue
        }

        $receipt = Get-Content -Raw -LiteralPath $existingReceiptPath |
            ConvertFrom-Json -Depth 30
        $receiptExit = Get-ReceiptExitCode -Receipt $receipt
        if ($null -eq $receiptExit) {
            throw 'coverage receipt carries neither exitCode nor collectorExitCode'
        }

        # THE RECEIPT DECIDES THE STATUS.  $LASTEXITCODE is only cross-checked
        # against the code that can actually reach it - see
        # Get-ExpectedProcessExit.  A disagreement still fails the trace,
        # because it means the wrapper did something neither branch explains.
        $record['observedProcessExit'] = $observedExit
        Add-ReceiptDerivedField -Record $record -Receipt $receipt
        $expectedObservedExit = Get-ExpectedProcessExit `
            -ReceiptExit $receiptExit `
            -ReceiptCollectorExit $record['collectorExitCode']
        if ($observedExit -ne $expectedObservedExit) {
            $record['status'] = 'failed'
            $record['reason'] = (
                "observed process exit $observedExit is neither the receipt's " +
                "resolved exit $receiptExit nor, on a clean run, its collector " +
                "exit $($record['collectorExitCode'])")
            $counts['failed']++
            Write-CampaignLine -Record $record | Out-Null
            Write-Host ("  {0}: FAILED - {1}" -f $level, $record['reason'])
            continue
        }

        if ($AcceptableExitCodes -contains $receiptExit) {
            $record['status'] = 'ok'
            $record['reason'] = ''
            $counts['ok']++
        } else {
            $record['status'] = 'failed'
            $record['reason'] = "coverage run exited $receiptExit"
            $counts['failed']++
        }
    } catch {
        $record['status'] = 'failed'
        $record['reason'] = "runner error: $($_.Exception.Message)"
        $counts['failed']++
    }

    $record['finishedAtUtc'] = (Get-Date).ToUniversalTime().ToString('o')
    Write-CampaignLine -Record $record | Out-Null
    Write-Host ("  {0}: {1} exit={2} wall={3}s ranges={4} covered={5}" -f
        $level,
        $record['status'].ToUpperInvariant(),
        $record['exitCode'],
        $record['wallSeconds'],
        $(if ($record.Contains('rangeCount')) { $record['rangeCount'] } else { '-' }),
        $(if ($record.Contains('coveredBytes')) { $record['coveredBytes'] } else { '-' }))
}

$campaignStopwatch.Stop()
$summary = [ordered]@{
    schema = $CampaignSchema
    kind = 'campaign-summary'
    mode = if ($RebuildLogFromReceipts) { 'rebuild-from-receipts' } else { 'collect' }
    finishedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    outputRoot = $outputRootPath
    campaignLog = $campaignLogPath
    matched = $traceDirectories.Count
    selected = $selected.Count
    ok = $counts['ok']
    skipped = $counts['skipped']
    blocked = $counts['blocked']
    failed = $counts['failed']
    wallSeconds = [math]::Round($campaignStopwatch.Elapsed.TotalSeconds, 2)
}
Write-CampaignLine -Record $summary | Out-Null
[pscustomobject]$summary

# Loud, not fatal: every trace was recorded either way, and nothing was
# retried.  A non-zero exit means the log has entries a human must read.
if ($counts['failed'] -gt 0 -or $counts['blocked'] -gt 0) {
    exit 1
}
