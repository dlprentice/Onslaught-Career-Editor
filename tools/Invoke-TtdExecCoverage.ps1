[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$TraceFile,

    [Parameter(Mandatory = $true)]
    [string]$TargetExe,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [string]$Collector = (Join-Path $PSScriptRoot '..\build\ttd-exec-coverage\bin\ttd_exec_coverage.exe'),
    [string]$ModuleName = 'BEA.exe',
    [string]$ExpectedBase = '',
    [string]$From = '',
    [string]$To = '',
    [string[]]$MustHitRva = @(),
    [string[]]$MustMissRva = @(),
    [switch]$Sequential,

    # Opt in to publishing coverage whose replay counters are impossible.  The
    # ranges are the product and were independently verified; the counters are
    # withheld from the summary and preserved only as poisoned evidence.  The
    # default remains fail-closed: no flag, no receipt.
    [switch]$QuarantineCounters
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PeIdentity {
    param([Parameter(Mandatory = $true)][string]$Path)

    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read
    )
    $reader = [System.IO.BinaryReader]::new($stream)
    try {
        if ($reader.ReadUInt16() -ne 0x5A4D) {
            throw "Not an MZ executable: $Path"
        }
        $stream.Position = 0x3C
        $peOffset = $reader.ReadUInt32()
        if ($peOffset -gt $stream.Length - 0x80) {
            throw "Invalid PE header offset in $Path"
        }
        $stream.Position = $peOffset
        if ($reader.ReadUInt32() -ne 0x00004550) {
            throw "Missing PE signature in $Path"
        }
        $machine = $reader.ReadUInt16()
        $sectionCount = $reader.ReadUInt16()
        $timestamp = $reader.ReadUInt32()
        $stream.Position = $peOffset + 20
        $optionalBytes = $reader.ReadUInt16()
        $characteristics = $reader.ReadUInt16()
        $optionalOffset = $peOffset + 24
        if ($optionalBytes -lt 68 -or $optionalOffset + $optionalBytes -gt $stream.Length) {
            throw "Invalid optional-header size in $Path"
        }
        $stream.Position = $optionalOffset
        $magic = $reader.ReadUInt16()
        if ($magic -ne 0x10B -or $machine -ne 0x14C) {
            throw "TTD coverage currently requires a PE32/x86 target: $Path"
        }
        $stream.Position = $optionalOffset + 28
        $imageBase = $reader.ReadUInt32()
        $stream.Position = $optionalOffset + 56
        $sizeOfImage = $reader.ReadUInt32()
        $stream.Position = $optionalOffset + 64
        $checksum = $reader.ReadUInt32()
        if ($sizeOfImage -eq 0) {
            throw "PE SizeOfImage is zero in $Path"
        }
        return [ordered]@{
            machine = ('0x{0:X4}' -f $machine)
            sectionCount = $sectionCount
            timestamp = ('0x{0:X8}' -f $timestamp)
            characteristics = ('0x{0:X4}' -f $characteristics)
            optionalMagic = ('0x{0:X4}' -f $magic)
            imageBase = ('0x{0:X8}' -f $imageBase)
            sizeOfImage = ('0x{0:X8}' -f $sizeOfImage)
            checksum = ('0x{0:X8}' -f $checksum)
        }
    } finally {
        $reader.Dispose()
        $stream.Dispose()
    }
}

function Get-FileFacts {
    param([Parameter(Mandatory = $true)][string]$Path)

    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = $item.FullName
        bytes = $item.Length
        sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
        lastWriteUtc = $item.LastWriteTimeUtc.ToString('o')
    }
}

function Assert-CoverageCountersAreConsistent {
    # A memory-watchpoint execute hit requires an executed instruction, and an
    # instruction is a step, so
    #   callback_hits <= instructions_executed <= steps_executed
    # is a hard invariant of any honest coverage summary.  Two recorded receipts
    # violate it by four orders of magnitude - options-open-manual-01 published
    # 131111 steps against 1137340343 callback hits, frontend-manual-02 137023
    # against 245245503 - because TTD Replay 1.11.584.0 stops advancing its step
    # accounting in some regions of those traces.  A receipt like that is a lying
    # instrument, not a surprising measurement.  Fail closed rather than write a
    # receipt around it.
    param(
        [Parameter(Mandatory = $true)]$Summary,
        [switch]$QuarantineAllowed
    )

    $counterFields = @(
        'callback_hits',
        'instructions_executed',
        'steps_executed'
    )
    $quarantined = $false
    $quarantineProperty = $Summary.PSObject.Properties['counters_quarantined']
    if ($null -ne $quarantineProperty) {
        if ($quarantineProperty.Value -isnot [bool]) {
            throw 'Coverage summary counters_quarantined must be a JSON boolean.'
        }
        $quarantined = [bool]$quarantineProperty.Value
    }

    if ($quarantined) {
        if (-not $QuarantineAllowed) {
            throw (
                'Coverage summary declares counters_quarantined but this run ' +
                'did not request -QuarantineCounters. Refusing a receipt ' +
                'nobody asked to quarantine.'
            )
        }
        # A receipt does not get it both ways: quarantined counters are absent,
        # never absent-and-also-present.
        $leaked = @($counterFields | Where-Object {
            $null -ne $Summary.PSObject.Properties[$_]
        })
        if ($leaked.Count -gt 0) {
            throw (
                'Coverage summary is quarantined but still carries top-level ' +
                "counters ($($leaked -join ', ')). Refusing a receipt that " +
                'claims both.'
            )
        }
        $evidence = $Summary.PSObject.Properties['quarantined_counters']
        if ($null -eq $evidence -or $null -eq $evidence.Value) {
            throw 'Quarantined coverage summary lacks quarantined_counters evidence.'
        }
        foreach ($field in $counterFields) {
            $property = $evidence.Value.PSObject.Properties[$field]
            if ($null -eq $property -or
                ([string]$property.Value) -notmatch '^[0-9]+$') {
                throw "Quarantined counter evidence lacks a decimal $field."
            }
        }
        $reason = $evidence.Value.PSObject.Properties['reason']
        if ($null -eq $reason -or [string]::IsNullOrWhiteSpace(
                [string]$reason.Value)) {
            throw 'Quarantined counter evidence lacks a reason.'
        }
        return
    }

    $values = @{}
    foreach ($field in $counterFields) {
        $property = $Summary.PSObject.Properties[$field]
        if ($null -eq $property) {
            throw "Coverage summary is missing $field."
        }
        $text = [string]$property.Value
        if ($text -notmatch '^[0-9]+$') {
            throw "Coverage summary field $field is not a decimal string: '$text'"
        }
        $values[$field] = [uint64]::Parse($text)
    }

    if ($values['instructions_executed'] -gt $values['steps_executed'] -or
        $values['callback_hits'] -gt $values['instructions_executed']) {
        throw (
            'Coverage summary counters are mutually impossible ' +
            "(callback_hits=$($values['callback_hits']) " +
            "instructions_executed=$($values['instructions_executed']) " +
            "steps_executed=$($values['steps_executed'])). " +
            'A watchpoint hit requires an executed instruction and an ' +
            'instruction is a step, so this receipt would be a lying ' +
            'instrument. Refusing to publish it.'
        )
    }
}

function Assert-FactsUnchanged {
    param(
        [Parameter(Mandatory = $true)]$Before,
        [Parameter(Mandatory = $true)]$After,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($Before.bytes -ne $After.bytes -or
        $Before.sha256 -cne $After.sha256 -or
        $Before.lastWriteUtc -cne $After.lastWriteUtc) {
        throw "$Label changed during TTD replay."
    }
}

$tracePath = (Resolve-Path -LiteralPath $TraceFile).Path
$targetPath = (Resolve-Path -LiteralPath $TargetExe).Path
$collectorPath = (Resolve-Path -LiteralPath $Collector).Path
foreach ($required in @($tracePath, $targetPath, $collectorPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required file was not found: $required"
    }
}
if ([System.IO.Path]::GetFileName($targetPath) -ine $ModuleName) {
    throw "Target filename must match -ModuleName ($ModuleName): $targetPath"
}

$outputRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $outputRoot) {
    if (-not (Test-Path -LiteralPath $outputRoot -PathType Container)) {
        throw "Output path exists and is not a directory: $outputRoot"
    }
    if ((Get-ChildItem -LiteralPath $outputRoot -Force | Select-Object -First 1)) {
        throw "Refusing to overwrite non-empty output directory: $outputRoot"
    }
} else {
    [System.IO.Directory]::CreateDirectory($outputRoot) | Out-Null
}

$coveragePath = Join-Path $outputRoot 'coverage.jsonl'
$receiptPath = Join-Path $outputRoot 'receipt.json'
$buildReceiptCopyPath = Join-Path $outputRoot 'collector-build-receipt.json'
$toolSnapshotDirectory = Join-Path $outputRoot 'collector-tool'
$collectorDirectory = Split-Path -Parent $collectorPath
$replayPath = Join-Path $collectorDirectory 'TTDReplay.dll'
$replayCpuPath = Join-Path $collectorDirectory 'TTDReplayCPU.dll'
$buildReceiptPath = Join-Path (Split-Path -Parent $collectorDirectory) 'build-receipt.json'
foreach ($runtimeFile in @($replayPath, $replayCpuPath, $buildReceiptPath)) {
    if (-not (Test-Path -LiteralPath $runtimeFile -PathType Leaf)) {
        throw "Collector dependency was not found: $runtimeFile"
    }
}

$buildReceipt = Get-Content -Raw -LiteralPath $buildReceiptPath |
    ConvertFrom-Json -Depth 20
if ([string]$buildReceipt.schemaVersion -cne
    'bea-ttd-exec-coverage-build.v2') {
    throw 'Collector build receipt is not the reproducible v2 schema.'
}
$repro = $buildReceipt.reproducibility
$reproBuilds = @($repro.isolatedBuilds)
if ($reproBuilds.Count -ne 2 -or
    $repro.buildCount -ne 2 -or
    $repro.byteIdentical -ne $true -or
    $repro.distinctOutputRoots -ne $true -or
    $repro.allSelfTestsPassed -ne $true -or
    [string]$repro.pdbAlternatePath -cne 'ttd_exec_coverage.pdb') {
    throw 'Collector build receipt does not close its two-build gate.'
}
if ([string]$reproBuilds[0].root -ceq [string]$reproBuilds[1].root) {
    throw 'Collector reproducibility roots are not distinct.'
}
$collectorSourceFacts = Get-FileFacts -Path $collectorPath
$replaySourceFacts = Get-FileFacts -Path $replayPath
$replayCpuSourceFacts = Get-FileFacts -Path $replayCpuPath
$buildReceiptSourceFacts = Get-FileFacts -Path $buildReceiptPath
if ($collectorSourceFacts.sha256 -cne [string]$buildReceipt.collector.sha256) {
    throw 'Collector hash does not match its build receipt.'
}
foreach ($build in $reproBuilds) {
    if ($build.bytes -ne $collectorSourceFacts.bytes -or
        [string]$build.sha256 -cne $collectorSourceFacts.sha256 -or
        [string]$build.selfTest -cne 'PASS') {
        throw 'An isolated collector build disagrees with the published collector.'
    }
}
if ([string]$buildReceipt.apiPackage.archiveSha256 -cne
        [string]$buildReceipt.apiPackage.observedArchiveSha256 -or
    $buildReceipt.apiPackage.extractedFilesVerified -le 0) {
    throw 'Collector API package validation is incomplete.'
}
if ($replaySourceFacts.sha256 -cne [string]$buildReceipt.runtime.replaySha256 -or
    $replayCpuSourceFacts.sha256 -cne [string]$buildReceipt.runtime.replayCpuSha256) {
    throw 'TTD Replay runtime hash does not match the collector build receipt.'
}

[System.IO.Directory]::CreateDirectory($toolSnapshotDirectory) | Out-Null
$snapshotCollectorPath = Join-Path $toolSnapshotDirectory 'ttd_exec_coverage.exe'
$snapshotReplayPath = Join-Path $toolSnapshotDirectory 'TTDReplay.dll'
$snapshotReplayCpuPath = Join-Path $toolSnapshotDirectory 'TTDReplayCPU.dll'
[System.IO.File]::Copy($collectorPath, $snapshotCollectorPath, $false)
[System.IO.File]::Copy($replayPath, $snapshotReplayPath, $false)
[System.IO.File]::Copy($replayCpuPath, $snapshotReplayCpuPath, $false)
[System.IO.File]::Copy($buildReceiptPath, $buildReceiptCopyPath, $false)

$collectorFacts = Get-FileFacts -Path $snapshotCollectorPath
$replayFacts = Get-FileFacts -Path $snapshotReplayPath
$replayCpuFacts = Get-FileFacts -Path $snapshotReplayCpuPath
$buildReceiptFacts = Get-FileFacts -Path $buildReceiptCopyPath
if ($collectorFacts.sha256 -cne $collectorSourceFacts.sha256 -or
    $replayFacts.sha256 -cne $replaySourceFacts.sha256 -or
    $replayCpuFacts.sha256 -cne $replayCpuSourceFacts.sha256 -or
    $buildReceiptFacts.sha256 -cne $buildReceiptSourceFacts.sha256) {
    throw 'Private collector-tool snapshot disagrees with its validated source.'
}
Assert-FactsUnchanged `
    -Before $collectorSourceFacts `
    -After (Get-FileFacts -Path $collectorPath) `
    -Label 'Collector source'
Assert-FactsUnchanged `
    -Before $replaySourceFacts `
    -After (Get-FileFacts -Path $replayPath) `
    -Label 'TTDReplay source'
Assert-FactsUnchanged `
    -Before $replayCpuSourceFacts `
    -After (Get-FileFacts -Path $replayCpuPath) `
    -Label 'TTDReplayCPU source'
Assert-FactsUnchanged `
    -Before $buildReceiptSourceFacts `
    -After (Get-FileFacts -Path $buildReceiptPath) `
    -Label 'Build-receipt source'

$traceBefore = Get-FileFacts -Path $tracePath
$targetBefore = Get-FileFacts -Path $targetPath
$targetPe = Get-PeIdentity -Path $targetPath

$collectorArguments = [System.Collections.Generic.List[string]]::new()
foreach ($value in @(
        '--trace', $tracePath,
        '--module', $ModuleName,
        '--out', $coveragePath,
        '--expect-size', $targetPe.sizeOfImage,
        '--expect-timestamp', $targetPe.timestamp,
        '--expect-checksum', $targetPe.checksum
    )) {
    $collectorArguments.Add([string]$value)
}
if (-not [string]::IsNullOrWhiteSpace($ExpectedBase)) {
    $collectorArguments.Add('--expect-base')
    $collectorArguments.Add($ExpectedBase)
}
if (-not [string]::IsNullOrWhiteSpace($From)) {
    $collectorArguments.Add('--from')
    $collectorArguments.Add($From)
}
if (-not [string]::IsNullOrWhiteSpace($To)) {
    $collectorArguments.Add('--to')
    $collectorArguments.Add($To)
}
if ($Sequential) {
    $collectorArguments.Add('--sequential')
}
if ($QuarantineCounters) {
    $collectorArguments.Add('--quarantine-counters')
}
foreach ($rva in $MustHitRva) {
    $collectorArguments.Add('--must-hit-rva')
    $collectorArguments.Add($rva)
}
foreach ($rva in $MustMissRva) {
    $collectorArguments.Add('--must-miss-rva')
    $collectorArguments.Add($rva)
}

$startedAt = (Get-Date).ToUniversalTime()
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
& $snapshotCollectorPath @collectorArguments
$collectorExitCode = $LASTEXITCODE
$stopwatch.Stop()
$finishedAt = (Get-Date).ToUniversalTime()

$traceAfter = Get-FileFacts -Path $tracePath
$targetAfter = Get-FileFacts -Path $targetPath
Assert-FactsUnchanged -Before $traceBefore -After $traceAfter -Label 'Trace'
Assert-FactsUnchanged -Before $targetBefore -After $targetAfter -Label 'Target executable'
Assert-FactsUnchanged `
    -Before $collectorFacts `
    -After (Get-FileFacts -Path $snapshotCollectorPath) `
    -Label 'Private collector'
Assert-FactsUnchanged `
    -Before $replayFacts `
    -After (Get-FileFacts -Path $snapshotReplayPath) `
    -Label 'Private TTDReplay'
Assert-FactsUnchanged `
    -Before $replayCpuFacts `
    -After (Get-FileFacts -Path $snapshotReplayCpuPath) `
    -Label 'Private TTDReplayCPU'
Assert-FactsUnchanged `
    -Before $buildReceiptFacts `
    -After (Get-FileFacts -Path $buildReceiptCopyPath) `
    -Label 'Private build receipt'

if (-not (Test-Path -LiteralPath $coveragePath -PathType Leaf)) {
    throw "Collector exited $collectorExitCode without producing coverage.jsonl."
}

$metadata = $null
$summary = $null
$gapSummary = $null
$rangeCount = 0
$assertionCount = 0
$lineCount = 0
foreach ($line in [System.IO.File]::ReadLines($coveragePath)) {
    $lineCount++
    $row = $line | ConvertFrom-Json -Depth 20
    if ([string]$row.schema -cne 'bea.ttd.exec-coverage.v1') {
        throw "Unexpected coverage schema on line $lineCount."
    }
    switch ([string]$row.kind) {
        'metadata' {
            if ($null -ne $metadata) {
                throw 'Coverage contains multiple metadata rows.'
            }
            $metadata = $row
        }
        'range' { $rangeCount++ }
        'assertion' { $assertionCount++ }
        'gap-summary' {
            if ($null -ne $gapSummary) {
                throw 'Coverage contains multiple gap-summary rows.'
            }
            $gapSummary = $row
        }
        'summary' {
            if ($null -ne $summary) {
                throw 'Coverage contains multiple summary rows.'
            }
            $summary = $row
        }
        default { throw "Unexpected coverage row kind on line $lineCount`: $($row.kind)" }
    }
}
if ($null -eq $metadata -or $null -eq $summary -or $null -eq $gapSummary) {
    throw 'Coverage is missing metadata, gap-summary, or summary.'
}
if ($rangeCount -ne [int]$summary.range_count) {
    throw 'Coverage range count does not match its summary.'
}
if ([string]$metadata.trace_bytes -cne [string]$traceBefore.bytes) {
    throw 'Coverage trace size does not match the hashed input trace.'
}
if ([string]$metadata.module_size -cne
    ('0x{0:X}' -f [Convert]::ToUInt64($targetPe.sizeOfImage.Substring(2), 16))) {
    throw 'Coverage module size does not match the target PE.'
}

Assert-CoverageCountersAreConsistent `
    -Summary $summary `
    -QuarantineAllowed:$QuarantineCounters
$countersQuarantined = (
    $null -ne $summary.PSObject.Properties['counters_quarantined'] -and
    $summary.counters_quarantined -eq $true
)

$coverageFacts = Get-FileFacts -Path $coveragePath
$receipt = [ordered]@{
    schemaVersion = 'bea-ttd-exec-coverage-receipt.v2'
    generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    startedAtUtc = $startedAt.ToString('o')
    finishedAtUtc = $finishedAt.ToString('o')
    elapsedSeconds = $stopwatch.Elapsed.TotalSeconds
    collectorExitCode = $collectorExitCode
    replayComplete = $summary.replay_complete -eq $true
    markerAssertionsPassed = $summary.marker_assertions_passed -eq $true
    collectorChecksPassed = $summary.collector_checks_passed -eq $true
    countersQuarantined = $countersQuarantined
    trace = $traceBefore
    target = [ordered]@{
        path = $targetBefore.path
        bytes = $targetBefore.bytes
        sha256 = $targetBefore.sha256
        lastWriteUtc = $targetBefore.lastWriteUtc
        pe = $targetPe
    }
    collector = $collectorFacts
    replayRuntime = [ordered]@{
        version = [string]$buildReceipt.runtime.version
        replay = $replayFacts
        replayCpu = $replayCpuFacts
    }
    buildReceipt = [ordered]@{
        path = $buildReceiptFacts.path
        bytes = $buildReceiptFacts.bytes
        sha256 = $buildReceiptFacts.sha256
        schemaVersion = [string]$buildReceipt.schemaVersion
    }
    invocation = [ordered]@{
        moduleName = $ModuleName
        expectedBase = $ExpectedBase
        from = $From
        to = $To
        sequential = [bool]$Sequential
        quarantineCounters = [bool]$QuarantineCounters
        mustHitRva = @($MustHitRva)
        mustMissRva = @($MustMissRva)
    }
    coverage = [ordered]@{
        path = $coverageFacts.path
        bytes = $coverageFacts.bytes
        sha256 = $coverageFacts.sha256
        schemaVersion = 'bea.ttd.exec-coverage.v1'
        lineCount = $lineCount
        rangeCount = $rangeCount
        assertionCount = $assertionCount
    }
    metadata = $metadata
    gapSummary = $gapSummary
    summary = $summary
}
$receiptJson = $receipt | ConvertTo-Json -Depth 20
[System.IO.File]::WriteAllText(
    $receiptPath,
    $receiptJson + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)

$receipt
if ($collectorExitCode -ne 0) {
    exit $collectorExitCode
}
