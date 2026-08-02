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
#   - only the measured copied specimen: pristine BEA.exe plus force_windowed;
#   - never while a d3d9 proxy capture is in flight (the proxy dll is the lock);
#   - launch mode never starts while any BEA.exe is already running;
#     attach mode accepts exactly one process whose image is the copied target;
#   - traces are written to G: only. C: and F: are refused.
# It never writes to the debuggee. TTD records; it does not modify.

[CmdletBinding(DefaultParameterSetName = 'Record')]
param(
    # Root of a COPIED target directory containing BEA.exe.
    [string]$TargetRoot = "$PSScriptRoot\..\local-lab\safe-copy-bea-pristine",

    # Arguments handed to the game. Default records a cold startup with the intro
    # FMV skipped. Pass @() for a fully cold start including the FMV.
    [string[]]$GameArguments = @('-skipfmv'),

    # Short label; becomes the trace directory name under -TraceRoot.
    #
    # Optional in -HashOnly repair mode, where it only LOCATES an existing trace
    # directory: pass -Name (resolved under -TraceRoot) or -TraceDirectory.
    [Parameter(ParameterSetName = 'Record', Mandatory = $true)]
    [Parameter(ParameterSetName = 'HashOnly')]
    [string]$Name,

    # Wall-clock seconds to record for, measured from the moment the .run file
    # first appears (i.e. from the start of recording, not from process launch).
    [int]$Seconds = 20,

    # Record until the GAME EXITS rather than for a fixed duration. This is the
    # mode for a human playing a level: launch, play for as long as you like,
    # quit the game, and the trace closes itself.
    #
    # -Seconds is ignored when this is set. The sampling loop already breaks when
    # the target process disappears; this only stops the duration deadline from
    # cutting the recording short first.
    #
    # SIZE. Measured cost is 26-32 MB/s, so budget roughly 1.8 GB per minute of
    # play. A fifteen-minute run is about 27 GB. G: is the designated capture
    # drive and had 923 GB free on 2026-07-27, so this is affordable - but the
    # free-space floor below is checked DURING recording, not only at the start,
    # because a long session is exactly where a disk fills up.
    [switch]$UntilExit,

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
    # Module-restricted capture remains disabled until a separate implementation
    # is demonstrated to produce a nonempty trace on this title.
    [string[]]$Module = @(),

    # Growth-rate sampling interval. The measured rate is reported and written to
    # the receipt; it is what makes the cost of a longer trace predictable.
    [int]$SampleIntervalSeconds = 2,

    # ATTACH to a BEA that is ALREADY RUNNING instead of launching one.
    #
    # This is the mode for capturing a specific moment. TTD instruments every
    # instruction, so a traced game is a slideshow - the maintainer played 13.5
    # minutes that way on 2026-07-28 and it was unpleasant. With -Attach the game
    # runs at FULL SPEED until the moment you care about, and only then does it
    # slow down.
    #
    # Workflow: start the game normally from the copied target, play to the part
    # you want, then run this with -Attach. Recording begins where you are.
    #
    # The CWD interlock does not apply here because the game is already running -
    # but the SPECIMEN interlock does, and is enforced harder: this refuses to
    # attach to any BEA whose image is not the copied target, so it can never
    # instrument the Steam install by accident.
    [switch]$Attach,

    # HOW LONG TO WAIT FOR TTD TO LET GO OF THE FINISHED .run BEFORE DEFERRING
    # ITS HASH. See the deferral policy below Fail(). A fixed wait is wrong for
    # an artefact whose size varies by 40x, so the budget is a floor plus an
    # allowance per GiB, capped, on a poll that returns the instant the lock
    # clears - a small trace still finishes in well under a second.
    [int]$UnlockFloorSeconds = 300,
    [double]$UnlockSecondsPerGiB = 120,
    [int]$UnlockMaxSeconds = 3600,

    # REPAIR MODE. Hash an already-recorded trace and complete its deferred
    # receipt in place. Records nothing, launches nothing, needs no elevation.
    # It REFUSES a receipt that already carries a real hash.
    [Parameter(ParameterSetName = 'HashOnly', Mandatory = $true)]
    [switch]$HashOnly,

    # The trace directory to repair. Defaults to "$TraceRoot\$Name".
    [Parameter(ParameterSetName = 'HashOnly')]
    [string]$TraceDirectory = '',

    # Run every interlock, print the exact TTD command line, launch nothing.
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$SUPPORTED_COPY_SHA256 = 'E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4'

function Fail([string]$m) { throw $m }

# ---------------------------------------------------------------------------
# THE RECEIPT SURVIVES A FAILED HASH.
#
# Measured 2026-08-02 on two real captures. Tracing finished, TTD wrote
# "Tracing completed at:" and "Trace dumped to" into the .out file, and the
# recorder then died trying to hash the .run because TTD still held the write
# handle. It waited a FIXED 180 s, gave up, threw, and exited 1 WITHOUT WRITING
# receipt.json:
#   G:\bea-ttd\level521-native-20260802-0018-take1  3.19 GB
#   G:\bea-ttd\level521-native-20260802-0018-take2  3.53 GB
# Both traces were completely valid and both receipts had to be reconstructed by
# hand. A fourth take of 13.5 GB in the same session hashed fine, so this is not
# a size threshold - it is a race against a flush whose duration varies with the
# device (both losses were on the USB-attached G:).
#
# The receipt is what every downstream consumer reads: the coverage campaign
# derives -ExpectAliveAtStop from guestOutcome, and parity_lab keys its ingest
# off it. A valid trace with no receipt drops out of the pipeline silently.
#
# Two changes, and the second is the important one:
#   1. the unlock wait is a DEADLINE SCALED TO THE ARTEFACT, not a constant;
#   2. if the wait still expires but the .out file PROVES the trace was
#      finalised, the receipt is written anyway with traceSha256 = $null,
#      traceHashState = 'deferred', and a hashDeferred block naming the reason.
#
# A deferred receipt is honestly incomplete, not quietly complete. Nothing may
# read its null hash as a match: Invoke-TtdCoverageCampaign.ps1 blocks the level
# and parity_lab refuses to call the capture COMPLETE. `-HashOnly` closes it
# without re-recording.
#
# What is NOT deferred: a trace with no completion evidence still fails hard.
# The deferral is licensed by the recorder's own completion markers, not by the
# mere fact that hashing failed.
# ---------------------------------------------------------------------------

function Get-TraceUnlockTimeoutSeconds {
    <#
    .SYNOPSIS
        Seconds to wait for TTD to release its write handle on a finished trace.
    .DESCRIPTION
        A generous floor plus an allowance per GiB, capped. The floor covers the
        fixed finalisation cost; the per-GiB term covers the flush, which is what
        actually scales. The cap keeps a genuinely stuck writer reportable rather
        than turning it into an unbounded hang.
    #>
    param(
        [Parameter(Mandatory = $true)][int64]$TraceBytes,
        [int]$FloorSeconds = 300,
        [double]$SecondsPerGiB = 120,
        [int]$MaxSeconds = 3600
    )

    if ($TraceBytes -lt 0) {
        throw "Trace size cannot be negative: $TraceBytes"
    }
    if ($FloorSeconds -lt 1) {
        throw "The unlock floor must be at least 1 s; got $FloorSeconds."
    }
    if ($SecondsPerGiB -lt 0) {
        throw "The per-GiB unlock allowance cannot be negative; got $SecondsPerGiB."
    }
    if ($MaxSeconds -lt $FloorSeconds) {
        throw "The unlock cap ($MaxSeconds s) is below its floor ($FloorSeconds s)."
    }

    # 1GB is 1073741824 in PowerShell, i.e. a GiB, which is what TTD flushes.
    $gibibytes = [double]$TraceBytes / 1GB
    $seconds = [int][math]::Ceiling($FloorSeconds + ($SecondsPerGiB * $gibibytes))
    if ($seconds -gt $MaxSeconds) { return $MaxSeconds }
    return $seconds
}

function Get-TtdCompletionMarkers {
    <#
    .SYNOPSIS
        What the recorder's own .out file says about whether the trace finished.
    .DESCRIPTION
        'Tracing completed at:' and 'Trace dumped to' are TTD's two statements
        that the trace was finalised and written. Both are required: the first
        alone says recording stopped, the second says the file is on disk.

        A guest exit line is reported but NOT required, because it is evidence
        about the GUEST, not about the trace. Requiring its absence would refuse
        a perfectly finalised run-to-completion trace.
    #>
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$OutText
    )

    $tracingCompleted = [bool]($OutText -match 'Tracing completed at:')
    $traceDumped = [bool]($OutText -match 'Trace dumped to')
    $guestExitObserved = [bool]($OutText -match 'exited with exit code')
    return [pscustomobject]@{
        tracingCompleted  = $tracingCompleted
        traceDumped       = $traceDumped
        guestExitObserved = $guestExitObserved
        traceFinalised    = ($tracingCompleted -and $traceDumped)
    }
}

function Wait-TtdTraceUnlock {
    <#
    .SYNOPSIS
        Poll until TTD releases the trace file, or until the deadline expires.
    .DESCRIPTION
        Returns rather than throwing, so the caller decides what a timeout means.
        The poll returns the instant the handle frees, so the scaled deadline
        costs nothing on the overwhelmingly common case.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [int]$PollMilliseconds = 500
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Cannot wait on a trace file that does not exist: $Path"
    }

    $started = Get-Date
    $deadline = $started.AddSeconds($TimeoutSeconds)
    while ($true) {
        try {
            $probe = [IO.File]::Open(
                $Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
            $probe.Dispose()
            return [pscustomobject]@{
                unlocked       = $true
                waitedSeconds  = [math]::Round(((Get-Date) - $started).TotalSeconds, 2)
                timeoutSeconds = $TimeoutSeconds
                lastError      = ''
            }
        }
        catch [IO.IOException] {
            $lastError = $_.Exception.Message
            if ((Get-Date) -ge $deadline) {
                return [pscustomobject]@{
                    unlocked       = $false
                    waitedSeconds  = [math]::Round(((Get-Date) - $started).TotalSeconds, 2)
                    timeoutSeconds = $TimeoutSeconds
                    lastError      = $lastError
                }
            }
            Start-Sleep -Milliseconds $PollMilliseconds
        }
    }
}

function New-TtdHashDeferral {
    <#
    .SYNOPSIS
        The machine-readable record of WHY a receipt carries no trace hash.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Reason,
        [Parameter(Mandatory = $true)][string]$TraceFile,
        [Parameter(Mandatory = $true)][int64]$TraceBytes,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [Parameter(Mandatory = $true)][double]$WaitedSeconds,
        [Parameter(Mandatory = $true)][object]$Markers,
        [AllowEmptyString()][string]$OutFile = '',
        [AllowEmptyString()][string]$Detail = '',
        [AllowEmptyString()][string]$RepairCommand = ''
    )

    return [pscustomobject]@{
        reason             = $Reason
        detail             = $Detail
        deferredAtUtc      = (Get-Date).ToUniversalTime().ToString('o')
        traceFile          = $TraceFile
        traceBytes         = $TraceBytes
        waitedSeconds      = $WaitedSeconds
        timeoutSeconds     = $TimeoutSeconds
        completionEvidence = [pscustomobject]@{
            outFile           = $OutFile
            tracingCompleted  = [bool]$Markers.tracingCompleted
            traceDumped       = [bool]$Markers.traceDumped
            guestExitObserved = [bool]$Markers.guestExitObserved
        }
        repairCommand      = $RepairCommand
        consumerContract   = (
            'traceSha256 is null and MUST NOT be read as a match. Any consumer ' +
            'that requires a trace hash must refuse this receipt until the ' +
            'repairCommand above has completed it.')
    }
}

function Get-TtdReceiptHashState {
    <#
    .SYNOPSIS
        Classify a parsed ttd-record-receipt's trace-hash state, fail-closed.
    .OUTPUTS
        'present'       a real 64-hex hash and nothing contradicting it
        'deferred'      no hash, traceHashState 'deferred', hashDeferred block
        'contradictory' the receipt disagrees with itself
        'absent'        no hash and no explanation - not a deferral, just missing
    #>
    param([Parameter(Mandatory = $true)][object]$Receipt)

    $hashProperty = $Receipt.PSObject.Properties['traceSha256']
    $hash =
        if ($null -ne $hashProperty -and $null -ne $hashProperty.Value) {
            ([string]$hashProperty.Value).Trim()
        } else { '' }
    $stateProperty = $Receipt.PSObject.Properties['traceHashState']
    $declaredState =
        if ($null -ne $stateProperty -and $null -ne $stateProperty.Value) {
            ([string]$stateProperty.Value).Trim()
        } else { '' }
    $deferralProperty = $Receipt.PSObject.Properties['hashDeferred']
    $hasDeferral = ($null -ne $deferralProperty -and $null -ne $deferralProperty.Value)
    $looksReal = [bool]($hash -match '^[0-9A-Fa-f]{64}$')

    $state =
        if ($looksReal -and ($declaredState -ceq 'deferred' -or $hasDeferral)) { 'contradictory' }
        elseif ($looksReal) { 'present' }
        elseif ($declaredState -ceq 'deferred' -and $hasDeferral) { 'deferred' }
        elseif ($declaredState -ceq 'deferred' -or $hasDeferral) { 'contradictory' }
        else { 'absent' }

    return [pscustomobject]@{
        state          = $state
        sha256         = if ($state -ceq 'present') { $hash.ToUpperInvariant() } else { $null }
        declaredState  = $declaredState
        hasDeferral    = $hasDeferral
    }
}

function Complete-TtdReceiptHashInPlace {
    <#
    .SYNOPSIS
        Fill in a deferred receipt's trace hash without re-recording.
    .DESCRIPTION
        REFUSES a receipt that already carries a real hash - overwriting one
        would destroy the only binding between the receipt and the bytes it was
        written for. Also refuses a receipt whose hash is merely missing: this
        completes a declared deferral, it does not invent provenance for a
        receipt that never explained itself.

        The original deferral is preserved inside hashRepaired.supersededDeferral
        so the receipt keeps saying that its hash was measured later than its
        trace, which is a weaker claim than a hash taken at capture time.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$ReceiptPath,
        [int]$FloorSeconds = 300,
        [double]$SecondsPerGiB = 120,
        [int]$MaxSeconds = 3600
    )

    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) {
        throw "No receipt to repair at $ReceiptPath."
    }
    $receipt = Get-Content -Raw -LiteralPath $ReceiptPath | ConvertFrom-Json -Depth 30
    if ($null -eq $receipt -or
        $receipt -isnot [System.Management.Automation.PSCustomObject]) {
        throw "Receipt is not a JSON object: $ReceiptPath"
    }
    $schemaProperty = $receipt.PSObject.Properties['schemaVersion']
    $schema = if ($null -ne $schemaProperty) { [string]$schemaProperty.Value } else { '' }
    if ($schema -cne 'ttd-record-receipt.v3') {
        throw "Refusing to repair an unsupported receipt schema '$schema': $ReceiptPath"
    }

    $hashState = Get-TtdReceiptHashState -Receipt $receipt
    switch ($hashState.state) {
        'present' {
            throw (
                'Refusing to overwrite a receipt that already carries a real trace ' +
                "hash ($($hashState.sha256)): $ReceiptPath. Repair mode completes a " +
                'deferred hash; it never replaces a measured one.')
        }
        'contradictory' {
            throw (
                'Receipt contradicts itself about its trace hash ' +
                "(traceSha256 present: $($null -ne $hashState.sha256), " +
                "traceHashState '$($hashState.declaredState)', " +
                "hashDeferred block: $($hashState.hasDeferral)): $ReceiptPath")
        }
        'absent' {
            throw (
                'Receipt has no trace hash and no hashDeferred block explaining ' +
                "why: $ReceiptPath. Repair mode completes a DECLARED deferral; it " +
                'will not manufacture provenance for a receipt that never explained ' +
                'itself.')
        }
    }

    $declaredBytesProperty = $receipt.PSObject.Properties['traceBytes']
    if ($null -eq $declaredBytesProperty) {
        throw "Receipt lacks traceBytes, so its trace cannot be bound: $ReceiptPath"
    }
    $declaredBytes = [int64]$declaredBytesProperty.Value

    $receiptDirectory = Split-Path -Parent $ReceiptPath
    $traceProperty = $receipt.PSObject.Properties['traceFile']
    $tracePath = if ($null -ne $traceProperty) { [string]$traceProperty.Value } else { '' }
    if (-not $tracePath -or -not (Test-Path -LiteralPath $tracePath -PathType Leaf)) {
        # The directory may have moved since the deferral. Accept exactly one
        # .run beside the receipt; refuse to guess between several.
        $candidates = @(Get-ChildItem -LiteralPath $receiptDirectory -Filter '*.run' -File -ErrorAction SilentlyContinue)
        if ($candidates.Count -ne 1) {
            throw (
                "Cannot locate the trace for $ReceiptPath - the recorded path " +
                "'$tracePath' does not exist and its directory holds " +
                "$($candidates.Count) .run files.")
        }
        $tracePath = $candidates[0].FullName
    }

    $traceItem = Get-Item -LiteralPath $tracePath
    if ($traceItem.Length -ne $declaredBytes) {
        throw (
            "Trace size changed since the deferral: the receipt records " +
            "$declaredBytes bytes, $tracePath is $($traceItem.Length). Refusing to " +
            'hash a different file into an existing receipt.')
    }

    $timeout = Get-TraceUnlockTimeoutSeconds `
        -TraceBytes $traceItem.Length `
        -FloorSeconds $FloorSeconds `
        -SecondsPerGiB $SecondsPerGiB `
        -MaxSeconds $MaxSeconds
    $unlock = Wait-TtdTraceUnlock -Path $tracePath -TimeoutSeconds $timeout
    if (-not $unlock.unlocked) {
        throw (
            "The trace is STILL locked after $($unlock.waitedSeconds) s of a " +
            "$timeout s budget: $tracePath. The receipt is left deferred and " +
            "unmodified. Last error: $($unlock.lastError)")
    }

    $before = Get-Item -LiteralPath $tracePath
    $sha256 = (Get-FileHash -LiteralPath $tracePath -Algorithm SHA256).Hash
    $after = Get-Item -LiteralPath $tracePath
    if ($before.Length -ne $after.Length -or
        $before.LastWriteTimeUtc -ne $after.LastWriteTimeUtc) {
        throw "The trace changed while its repair hash was being computed: $tracePath"
    }

    $supersededProperty = $receipt.PSObject.Properties['hashDeferred']
    $superseded = if ($null -ne $supersededProperty) { $supersededProperty.Value } else { $null }
    $repaired = [pscustomobject]@{
        repairedAtUtc            = (Get-Date).ToUniversalTime().ToString('o')
        tool                     = 'tools/ttd_record.ps1 -HashOnly'
        hashedFile               = $before.FullName
        hashedBytes              = $before.Length
        traceBytesMatchedReceipt = $true
        waitedSecondsForUnlock   = $unlock.waitedSeconds
        provenance               = (
            'The trace hash was measured AFTER the recording session, not while ' +
            'the recorder held the run. It binds the receipt to the bytes now on ' +
            'disk; it does not independently witness that they are the bytes TTD ' +
            'wrote. Treat provenance as PARTIAL.')
        supersededDeferral       = $superseded
    }

    $receipt | Add-Member -NotePropertyName 'traceSha256' -NotePropertyValue $sha256 -Force
    $receipt | Add-Member -NotePropertyName 'traceHashState' -NotePropertyValue 'present' -Force
    $receipt | Add-Member -NotePropertyName 'hashDeferred' -NotePropertyValue $null -Force
    $receipt | Add-Member -NotePropertyName 'hashRepaired' -NotePropertyValue $repaired -Force
    if ($null -ne $receipt.PSObject.Properties['traceFile']) {
        $receipt.traceFile = $before.FullName
    }

    $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding utf8
    return $receipt
}

function ConvertTo-WindowsCommandLineArgument([AllowEmptyString()][string]$Argument) {
    if ($Argument.Length -gt 0 -and $Argument -notmatch '[\s"]') {
        return $Argument
    }

    # ProcessStartInfo.ArgumentList is unavailable in Windows PowerShell 5.1.
    # Quote one argv element using the CommandLineToArgvW backslash rules so the
    # compatibility path below remains lossless for spaces, quotes, and trailing
    # backslashes.
    $quoted = [Text.StringBuilder]::new()
    $null = $quoted.Append('"')
    $backslashes = 0
    foreach ($character in $Argument.ToCharArray()) {
        if ($character -eq '\') {
            $backslashes++
            continue
        }
        if ($character -eq '"') {
            $null = $quoted.Append(('\' * (($backslashes * 2) + 1)))
            $null = $quoted.Append('"')
            $backslashes = 0
            continue
        }
        if ($backslashes -gt 0) {
            $null = $quoted.Append(('\' * $backslashes))
            $backslashes = 0
        }
        $null = $quoted.Append($character)
    }
    if ($backslashes -gt 0) {
        $null = $quoted.Append(('\' * ($backslashes * 2)))
    }
    $null = $quoted.Append('"')
    return $quoted.ToString()
}

function Set-NativeProcessArguments(
    [Diagnostics.ProcessStartInfo]$StartInfo,
    [AllowEmptyCollection()][string[]]$Arguments
) {
    if ($null -ne $StartInfo.PSObject.Properties['ArgumentList']) {
        foreach ($argument in $Arguments) {
            $StartInfo.ArgumentList.Add([string]$argument)
        }
        return
    }

    $StartInfo.Arguments = (($Arguments | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument ([string]$_)
    }) -join ' ')
}

# ------------------------------------------------------------- repair mode
# Deliberately ahead of every recording interlock: this launches nothing, opens
# no target, needs no elevation, and must stay usable from an ordinary shell
# hours after the capture session that deferred the hash has ended.
if ($HashOnly) {
    $directory =
        if (-not [string]::IsNullOrWhiteSpace($TraceDirectory)) {
            [IO.Path]::GetFullPath($TraceDirectory)
        }
        elseif (-not [string]::IsNullOrWhiteSpace($Name)) {
            Join-Path ([IO.Path]::GetFullPath($TraceRoot)) $Name
        }
        else {
            Fail '-HashOnly needs either -TraceDirectory or -Name (with -TraceRoot).'
        }
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        Fail "No trace directory at $directory."
    }

    $repairReceiptPath = Join-Path $directory 'receipt.json'
    $repaired = Complete-TtdReceiptHashInPlace `
        -ReceiptPath $repairReceiptPath `
        -FloorSeconds $UnlockFloorSeconds `
        -SecondsPerGiB $UnlockSecondsPerGiB `
        -MaxSeconds $UnlockMaxSeconds

    Write-Host ("repaired: {0}" -f $repairReceiptPath)
    Write-Host ("trace   : {0}" -f $repaired.traceFile)
    Write-Host ("sha256  : {0}" -f $repaired.traceSha256)
    Write-Host 'The hash was measured after the fact; provenance is PARTIAL and the'
    Write-Host 'receipt says so under hashRepaired.provenance.'
    $repaired
    exit 0
}

# ---------------------------------------------------------------- interlock 1-3
if ($Name -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$') {
    Fail "-Name must be 1-64 ASCII letters, digits, dots, underscores, or hyphens, beginning with a letter or digit."
}
if ($Module.Count -gt 0) {
    Fail ("Module-restricted recording is disabled: the measured BEA.exe restriction " +
          "produced an empty preallocated trace. Use the unrestricted default.")
}
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
if ($hash -ine $SUPPORTED_COPY_SHA256) {
    Fail ("Unsupported BEA.exe specimen $hash. TTD evidence is accepted only from " +
          "the measured copied target: canonical Steam BEA.exe plus force_windowed " +
          "(sha256 $SUPPORTED_COPY_SHA256).")
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
if (-not $Attach -and $running.Count -gt 0) {
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
if (Test-Path -LiteralPath $outDir) {
    Fail "Trace output already exists: $outDir. Choose a fresh -Name; stale trace artifacts are never reused."
}

$ttdArgs = @('-accepteula', '-noUI', '-out', $traceFile, '-maxFile', "$MaxFileMB")
if ($Ring) { $ttdArgs += '-ring' }
foreach ($m in $Module) { $ttdArgs += @('-module', $m) }

$attachPid = $null
if ($Attach) {
    # Find the running game, and refuse anything that is not the copied target.
    # This interlock is stricter than the launch path's, because the launch path
    # chooses the image while this one inherits whatever is already running - and
    # the maintainer's Steam install is a deliberately patched binary that must
    # never be treated as a specimen.
    $running = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue)
    if ($running.Count -eq 0) {
        Fail "-Attach was given but no BEA process is running. Start the game from`n  $TargetRoot`nfirst, play to the moment you want, then run this again."
    }
    $ours = @($running | Where-Object { $_.Path -ieq $exe })
    if ($ours.Count -eq 0) {
        $paths = ($running | ForEach-Object { $_.Path }) -join "`n  "
        Fail "A BEA is running but it is NOT the copied target. Refusing to attach.`nExpected:`n  $exe`nFound:`n  $paths"
    }
    if ($ours.Count -gt 1) {
        Fail "More than one copy of the target is running ($($ours.Count)). Refusing to guess which to trace."
    }
    $attachPid = $ours[0].Id
    Write-Host ("attaching to PID {0} ({1})" -f $attachPid, $exe)
    $ttdArgs += @('-attach', "$attachPid")
} else {
    # -launch must be the last option before the program and its arguments.
    $ttdArgs += @('-launch', $exe) + $GameArguments
}

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
    Write-Host "Re-run your original command unchanged from an elevated PowerShell." -ForegroundColor Cyan
    Write-Host "For an attach capture, tools\Record-GameMoment.ps1 preserves every argument while raising UAC."
    Write-Host ""
    Write-Host "The raw recorder command it would run is:"
    Write-Host "  $commandPreview"
    Fail "Not elevated; refusing to raise a UAC consent dialog unattended."
}

$null = [IO.Directory]::CreateDirectory($outDir)

# ------------------------------------------------------------------ record
$startedUtc = (Get-Date).ToUniversalTime()
# -WorkingDirectory is load-bearing, not tidiness. BEA.exe writes runtime logs
# into its CURRENT WORKING DIRECTORY, not next to its own image: the first
# elevated session was launched with the repository root as CWD and the game
# deposited a 2,770-byte setuphistory.txt straight into the repo, where it showed
# up as an untracked file. That is retail-derived runtime output, which CLAUDE.md
# forbids tracking, and it would have been one careless `git add .` from being
# committed. Pinning the CWD to the copied target keeps the game's own droppings
# inside the copy, where they belong and are already ignored.
$recorder = $null
$target = $null
$samples = [System.Collections.Generic.List[object]]::new()
$runFileSeenUtc = $null
$runFileInitialBytes = $null
$deadline =
    if ($UntilExit) { [datetime]::MaxValue }
    else { (Get-Date).AddSeconds($Seconds + 300) }
$recordDeadline = $null
$traceDriveRoot = [IO.Path]::GetPathRoot([IO.Path]::GetFullPath($TraceRoot))
$spaceAborted = $false
$recorderEndedWhileTargetAlive = $false
$recorderExitCode = $null
$primaryFailure = $null
$cleanupProblems = [System.Collections.Generic.List[string]]::new()
$recorderStdoutStream = $null
$recorderStderrStream = $null
$recorderStdoutCopy = $null
$recorderStderrCopy = $null
$recorderStarted = $false

try {
    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $ttd
    $startInfo.WorkingDirectory = $TargetRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    Set-NativeProcessArguments -StartInfo $startInfo -Arguments $ttdArgs
    $recorder = [Diagnostics.Process]::new()
    $recorder.StartInfo = $startInfo
    if (-not $recorder.Start()) {
        Fail "TTD recorder did not start: $ttd"
    }
    $recorderStarted = $true
    $recorderStdoutStream = [IO.FileStream]::new(
        (Join-Path $outDir 'ttd-stdout.txt'),
        [IO.FileMode]::Create,
        [IO.FileAccess]::Write,
        [IO.FileShare]::Read)
    $recorderStderrStream = [IO.FileStream]::new(
        (Join-Path $outDir 'ttd-stderr.txt'),
        [IO.FileMode]::Create,
        [IO.FileAccess]::Write,
        [IO.FileShare]::Read)
    $recorderStdoutCopy = $recorder.StandardOutput.BaseStream.CopyToAsync($recorderStdoutStream)
    $recorderStderrCopy = $recorder.StandardError.BaseStream.CopyToAsync($recorderStderrStream)

    # Wait for the target to appear, then for the .run file to appear.
    for ($i = 0; $i -lt 480; $i++) {
        $target = Get-Process -Name 'BEA' -ErrorAction SilentlyContinue |
            Where-Object { $_.Path -ieq $exe } |
            Select-Object -First 1
        if ($target) { break }
        if ($recorder.HasExited) { break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $target) {
        $err = if (Test-Path (Join-Path $outDir 'ttd-stdout.txt')) {
            (Get-Content -LiteralPath (Join-Path $outDir 'ttd-stdout.txt') -Raw) } else { '' }
        Fail "The copied target never started under TTD.`n$err"
    }

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
            $runFileInitialBytes = $len
            # -UntilExit deliberately leaves this null, so the only things that end
            # the loop are the game exiting or the free-space floor below.
            if (-not $UntilExit) { $recordDeadline = (Get-Date).AddSeconds($Seconds) }
        }
        if ($runFileSeenUtc) {
            $samples.Add([pscustomobject]@{
                SecondsIntoRecording = [math]::Round(((Get-Date).ToUniversalTime() - $runFileSeenUtc).TotalSeconds, 2)
                Bytes                = $len
                MB                   = [math]::Round($len / 1MB, 2)
            })
        }
        if ($recordDeadline -and (Get-Date) -ge $recordDeadline) { break }

        # Free space is re-checked DURING recording, not only up front. At 26-32 MB/s
        # a long play session is precisely where a drive fills, and a trace truncated
        # by a full disk is worse than one stopped deliberately - TTD may not finalise
        # it, and the failure would land on the maintainer mid-level.
        try {
            $freeGB = [math]::Round((Get-PSDrive -Name $traceDriveRoot.TrimEnd(':\') -ErrorAction Stop).Free / 1GB, 1)
            if ($freeGB -lt 10) {
                Write-Warning ("Stopping: only {0} GB free on {1}. The trace is finalised, not truncated." -f $freeGB, $traceDriveRoot)
                $spaceAborted = $true
                break
            }
        } catch { }
        $t = Get-Process -Id $target.Id -ErrorAction SilentlyContinue
        if (-not $t) { break }
        # Recorder exit is terminal even after a .run appears. A max-file stop
        # or recorder failure while the guest remains alive is an incomplete
        # capture, not a reason to keep waiting and later call the
        # completion marker a success.
        if ($recorder.HasExited) {
            $recorderEndedWhileTargetAlive = [bool]$runFileSeenUtc
            $recorderExitCode = $recorder.ExitCode
            break
        }
        Start-Sleep -Seconds $SampleIntervalSeconds
    }
    if (-not $runFileSeenUtc) {
        $so = Join-Path $outDir 'ttd-stdout.txt'
        $msg = if (Test-Path -LiteralPath $so) { Get-Content -LiteralPath $so -Raw } else { '' }
        Write-Warning "No .run file ever appeared under $outDir. Recorder output follows:`n$msg"
    }
}
catch {
    $primaryFailure = $_
}
finally {
    $liveTarget =
        if ($target) {
            Get-Process -Id $target.Id -ErrorAction SilentlyContinue |
                Where-Object { $_.Path -ieq $exe } |
                Select-Object -First 1
        } else { $null }
    if ($liveTarget) {
        # Stop tracing cleanly first so the trace is finalised, then close only a
        # process launched by this script. An attached game belongs to the user.
        foreach ($control in @(
            [pscustomobject]@{ Name = 'stop'; Arguments = @('-accepteula', '-stop', "$($target.Id)") }
            [pscustomobject]@{ Name = 'wait'; Arguments = @('-accepteula', '-wait', '120') }
        )) {
            try {
                # A non-zero native exit must be retained as a cleanup failure,
                # not promoted into a terminating error that masks the original
                # recording exception.
                $oldNativePreference = $PSNativeCommandUseErrorActionPreference
                $PSNativeCommandUseErrorActionPreference = $false
                $controlArguments = $control.Arguments
                $output = & $ttd @controlArguments 2>&1 | Out-String
                $controlExit = $LASTEXITCODE
                $output | Write-Verbose
                if ($controlExit -ne 0) {
                    $cleanupProblems.Add("TTD $($control.Name) exited $controlExit")
                }
            }
            catch {
                $cleanupProblems.Add("TTD $($control.Name) failed: $($_.Exception.Message)")
            }
            finally {
                $PSNativeCommandUseErrorActionPreference = $oldNativePreference
            }
        }
        if (-not $Attach) {
            Get-Process -Id $liveTarget.Id -ErrorAction SilentlyContinue |
                Where-Object { $_.Path -ieq $exe } | Stop-Process -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host 'attach mode: tracing stopped, THE GAME IS STILL RUNNING - carry on playing.'
        }
    }
    if ($recorderStarted -and -not $recorder.HasExited) {
        if (-not $recorder.WaitForExit(60000)) {
            $cleanupProblems.Add("TTD recorder PID $($recorder.Id) did not exit within 60 seconds")
            Stop-Process -Id $recorder.Id -Force -ErrorAction SilentlyContinue
            $recorder.WaitForExit(10000) | Out-Null
        }
    }
    try {
        if ($recorderStdoutCopy) { $recorderStdoutCopy.GetAwaiter().GetResult() }
        if ($recorderStderrCopy) { $recorderStderrCopy.GetAwaiter().GetResult() }
    }
    catch {
        $cleanupProblems.Add("TTD output capture failed: $($_.Exception.Message)")
    }
    finally {
        if ($recorderStdoutStream) { $recorderStdoutStream.Dispose() }
        if ($recorderStderrStream) { $recorderStderrStream.Dispose() }
    }
}

if ($cleanupProblems.Count -gt 0) {
    foreach ($problem in $cleanupProblems) { Write-Warning $problem }
}
if ($primaryFailure) {
    throw $primaryFailure
}
if ($cleanupProblems.Count -gt 0) {
    Fail ("TTD cleanup did not complete cleanly: " + ($cleanupProblems -join '; '))
}

$final = if (Test-Path -LiteralPath $traceFile) { (Get-Item -LiteralPath $traceFile).Length } else { 0 }
$span = if ($runFileSeenUtc) { ((Get-Date).ToUniversalTime() - $runFileSeenUtc).TotalSeconds } else { 0 }
$rate = if ($span -gt 0) { [math]::Round(($final / 1MB) / $span, 2) } else { 0 }
$traceGrew = $runFileInitialBytes -ne $null -and $final -gt $runFileInitialBytes
$stoppedAtFileCap =
    $recorderEndedWhileTargetAlive -and
    -not $Ring -and
    $final -ge ([int64]($MaxFileMB * 1MB * 0.99))

# THE GUEST'S OWN EXIT CODE. Added 2026-07-27 after this script reported
# "exit = 0" with healthy-looking receipts for THREE consecutive runs in which
# BEA died in its fatal-error handler seconds after launch. TTD recorded the
# death faithfully and said so in its own log; nothing here read it. The traces
# were 328-340 MB of a game that never got past sound initialisation, and every
# question asked of them came back a confident zero.
#
# That is the second instrument-lies defect in this file today - the first was
# -Module @('BEA.exe') producing an empty 4 MiB chunk that the size check read as
# success. Both have the same shape: a proxy for success (file exists / file is
# big) standing in for the thing actually wanted (the game ran).
#
# The exit code is authoritative and TTD prints it in two places, so read both.
$guestExit = $null
$guestExitSource = $null
foreach ($candidate in @((Join-Path $outDir "$Name.out"), (Join-Path $outDir 'ttd-stdout.txt'))) {
    if ($guestExit -ne $null) { break }
    if (-not (Test-Path -LiteralPath $candidate)) { continue }
    $text = Get-Content -LiteralPath $candidate -Raw -ErrorAction SilentlyContinue
    if ($text -match 'exited with exit code\s+(-?\d+)') {
        # TTD uses both signed and unsigned spellings for the same 32-bit
        # process exit value. Its summary prints -1 while the detailed .out
        # file prints 4294967295. Parse the complete uint32 domain first, then
        # reinterpret its upper half as the corresponding signed value.
        $rawGuestExit = [int64]::Parse(
            $Matches[1],
            [Globalization.CultureInfo]::InvariantCulture)
        if (
            $rawGuestExit -lt [int]::MinValue -or
            $rawGuestExit -gt [uint32]::MaxValue
        ) {
            Fail "TTD reported an out-of-range 32-bit guest exit code: $rawGuestExit"
        }
        $guestExit =
            if ($rawGuestExit -gt [int]::MaxValue) {
                $rawGuestExit - [int64]4294967296
            } else {
                $rawGuestExit
            }
        $guestExitSource = $candidate
    }
}

# BEA writes its own fatal reason into the log it drops in its CWD. Surfacing it
# turns "the game died" into "the game died BECAUSE", which is the difference
# between a wasted elevation and a fixed launch.
$guestFatal = $null
$setupLog = Join-Path $TargetRoot 'setuphistory.txt'
if (Test-Path -LiteralPath $setupLog) {
    $tail = Get-Content -LiteralPath $setupLog -Tail 5 -ErrorAction SilentlyContinue
    $hit = $tail | Where-Object { $_ -match 'Fatal error' } | Select-Object -Last 1
    if ($hit) { $guestFatal = $hit.Trim() }
}

# CLASSIFY THE OUTCOME, rather than treating "no exit code" as failure.
#
# The first version of this check rejected any run it could not read an exit code
# from. That is exactly backwards for a TIMED recording: the recorder stops
# tracing while the game is still alive, so TTD never prints an exit line, and a
# perfectly good trace was reported as a dead guest. It cost a real play session.
#
# The three outcomes are genuinely different and only one of them is bad:
#   exited-error  guest exited non-zero            -> REJECT
#   exited-clean  guest exited 0                   -> accept
#   alive-at-stop no exit line, tracing completed,
#                 and the game logged no fatal     -> accept, this is normal
# "unknown" is kept for the case where none of those hold, so an ambiguous run is
# still visible rather than being quietly folded into one of the good ones.
$outFile = Join-Path $outDir "$Name.out"
$outText =
    if (Test-Path -LiteralPath $outFile) {
        [string](Get-Content -LiteralPath $outFile -Raw -ErrorAction SilentlyContinue)
    } else { '' }
# ONE parser for the recorder's completion markers, shared by the outcome
# classification below and by the hash-deferral decision after it. Two readers
# of the same evidence that could drift apart is how an instrument starts lying.
$completionMarkers = Get-TtdCompletionMarkers -OutText $outText
$tracingCompleted = $completionMarkers.tracingCompleted
$guestOutcome =
    if ($spaceAborted)                          { 'space-aborted' }
    elseif ($stoppedAtFileCap)                  { 'max-file-aborted' }
    elseif ($recorderEndedWhileTargetAlive)     { 'recorder-ended-early' }
    elseif ($guestFatal)                        { 'exited-error' }
    elseif ($guestExit -ne $null -and $guestExit -ne 0) { 'exited-error' }
    elseif (-not $traceGrew)                    { 'unknown' }
    elseif ($guestExit -eq 0)                   { 'exited-clean' }
    elseif ($tracingCompleted -and $final -gt 0){ 'alive-at-stop' }
    else                                        { 'unknown' }

$traceSha256 = $null
$traceHashState = 'no-trace'
$hashDeferred = $null
$hashRepairCommand = (
    'pwsh -NoProfile -File "' + $PSCommandPath + '" -HashOnly -TraceDirectory "' +
    $outDir + '"')

if ($final -gt 0) {
    # WAIT FOR TTD TO LET GO OF THE .run BEFORE HASHING IT.
    #
    # TTD prints "Trace dumped to ..." and the recorder returns, but the writer
    # can still hold the file open while it finalises. Hashing in that window
    # fails with "The process cannot access the file ... because it is being
    # used by another process".
    #
    # The wait is a deadline SCALED TO THE ARTEFACT, and expiring it no longer
    # destroys the receipt - see the deferral policy at the top of this file.
    $unlockTimeout = Get-TraceUnlockTimeoutSeconds `
        -TraceBytes $final `
        -FloorSeconds $UnlockFloorSeconds `
        -SecondsPerGiB $UnlockSecondsPerGiB `
        -MaxSeconds $UnlockMaxSeconds
    Write-Host ("hash   : waiting up to {0} s for TTD to release {1:N2} GiB" -f
        $unlockTimeout, ($final / 1GB))
    $unlock = Wait-TtdTraceUnlock -Path $traceFile -TimeoutSeconds $unlockTimeout

    if ($unlock.unlocked) {
        $traceBeforeHash = Get-Item -LiteralPath $traceFile
        $traceSha256 = (
            Get-FileHash -LiteralPath $traceFile -Algorithm SHA256
        ).Hash
        $traceAfterHash = Get-Item -LiteralPath $traceFile
        if (
            $traceBeforeHash.Length -ne $traceAfterHash.Length -or
            $traceBeforeHash.LastWriteTimeUtc -ne $traceAfterHash.LastWriteTimeUtc
        ) {
            Fail 'TTD trace changed while its receipt hash was being computed.'
        }
        $traceHashState = 'present'
    }
    elseif ($completionMarkers.traceFinalised) {
        # DEFER, DO NOT DESTROY. The recorder itself says the trace was completed
        # and dumped, so the artefact is real and the pipeline should get a
        # receipt for it. What must not happen is the null being mistaken for a
        # hash, which is what traceHashState and hashDeferred exist to prevent.
        $traceHashState = 'deferred'
        $hashDeferred = New-TtdHashDeferral `
            -Reason 'trace-file-locked-after-completion' `
            -TraceFile $traceFile `
            -TraceBytes $final `
            -TimeoutSeconds $unlock.timeoutSeconds `
            -WaitedSeconds $unlock.waitedSeconds `
            -Markers $completionMarkers `
            -OutFile $outFile `
            -Detail $unlock.lastError `
            -RepairCommand $hashRepairCommand
    }
    else {
        # No completion evidence AND no hash. Nothing licenses a receipt here:
        # a deferral is a claim about a finished trace, and this trace has not
        # been shown to be one.
        Fail (
            "TTD trace file was still locked after $($unlock.waitedSeconds) s of a " +
            "$($unlock.timeoutSeconds) s budget: $traceFile. Its .out file does NOT " +
            'carry both "Tracing completed at:" and "Trace dumped to", so the ' +
            'recording cannot be certified complete and no receipt is written. ' +
            "Inspect $outFile.")
    }
}

$receipt = [pscustomobject]@{
    schemaVersion        = 'ttd-record-receipt.v3'
    guestOutcome         = $guestOutcome
    guestExitCode        = $guestExit
    guestExitSource      = $guestExitSource
    guestFatalError      = $guestFatal
    guestRanCleanly      = ($guestOutcome -in @('exited-clean','alive-at-stop'))
    stoppedForLowSpace   = $spaceAborted
    stoppedAtFileCap     = $stoppedAtFileCap
    recorderEndedEarly   = $recorderEndedWhileTargetAlive
    recorderExitCode     = $recorderExitCode
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
    traceSha256          = $traceSha256
    # 'present' | 'deferred' | 'no-trace'. The scalar discriminator a consumer
    # checks so a null traceSha256 can never be read as a match.
    traceHashState       = $traceHashState
    hashDeferred         = $hashDeferred
    traceGrew            = $traceGrew
    traceMB              = [math]::Round($final / 1MB, 2)
    growthMBPerSecond    = $rate
    ring                 = [bool]$Ring
    maxFileMB            = $MaxFileMB
    samples              = $samples
}
$receiptPath = Join-Path $outDir 'receipt.json'
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8

Write-Host ("trace  : {0} ({1} MB)" -f $traceFile, $receipt.traceMB)
Write-Host ("rate   : {0} MB/s over {1} s" -f $rate, $receipt.actualRecordSeconds)
Write-Host ("receipt: {0}" -f $receiptPath)
$receipt

# Refuse to call a dead guest a success. This is deliberately the LAST thing the
# script does, so the receipt is still written and the trace is still kept - a
# trace of a crash is exactly what you want when diagnosing the crash. What must
# not happen is the caller reading exit 0 and believing the recording is usable.
if ($guestOutcome -eq 'exited-error') {
    Write-Host ''
    Write-Warning ("THE GAME DIED. Guest exit code {0} (from {1})." -f $guestExit, $guestExitSource)
    if ($guestFatal) { Write-Warning ("Its own reason: {0}" -f $guestFatal) }
    Write-Warning 'The trace is kept, but it records a broken launch and its silences mean nothing.'
    Write-Warning 'Most likely cause on this title: the game resolves data\ RELATIVE TO ITS CWD.'
    exit 3
}
if ($guestOutcome -eq 'unknown') {
    Write-Warning 'Cannot tell whether the guest ran - no exit code, no completion marker. UNVERIFIED.'
    exit 4
}
if ($guestOutcome -eq 'space-aborted') {
    Write-Warning 'Recording stopped at the free-space floor. The trace was finalized but is incomplete.'
    exit 5
}
if ($guestOutcome -eq 'max-file-aborted') {
    Write-Warning 'Recording hit the configured max-file boundary while the game was still running. The trace is finalized but incomplete.'
    exit 6
}
if ($guestOutcome -eq 'recorder-ended-early') {
    Write-Warning ("The TTD recorder exited {0} while the game was still running. The trace is incomplete." -f $recorderExitCode)
    exit 7
}
if ($guestOutcome -eq 'alive-at-stop') {
    Write-Host 'guest: still running when the timer stopped tracing (normal for a timed trace).'
}
# A recording far shorter than asked for is not automatically wrong - the target
# may legitimately exit - but with a zero exit code it is worth flagging rather
# than silently accepting, because that is what a clean early quit looks like.
if ($span -gt 0 -and $Seconds -gt 0 -and $span -lt ($Seconds * 0.5)) {
    Write-Warning ("Recorded {0:N1} s of a requested {1} s, though the guest exited cleanly." -f $span, $Seconds)
}

# A DEFERRED HASH IS A DEGRADED SUCCESS, not a failure and not a clean run.
# The trace is kept, the receipt exists, and everything downstream that needs a
# hash refuses this receipt until the repair command below has completed it.
# It gets its own exit code beside the other degraded-but-kept outcomes above so
# an unattended caller cannot mistake it for a fully certified capture.
if ($traceHashState -ceq 'deferred') {
    Write-Host ''
    Write-Warning 'THE TRACE IS COMPLETE BUT ITS HASH IS DEFERRED.'
    Write-Warning ("TTD held the file for the whole {0} s unlock budget." -f $hashDeferred.timeoutSeconds)
    Write-Warning 'The receipt was written with traceSha256 = null and a hashDeferred block.'
    Write-Warning 'Complete it - no re-recording needed - with:'
    Write-Host ("  {0}" -f $hashRepairCommand)
    exit 8
}
exit 0
