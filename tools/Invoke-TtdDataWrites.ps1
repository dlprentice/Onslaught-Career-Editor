[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$TraceFile,

    [Parameter(Mandatory = $true)]
    [string]$TargetExe,

    [Parameter(Mandatory = $true)]
    [string]$DataTargetsTsv,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [Parameter(Mandatory = $true)]
    [string]$From,

    [Parameter(Mandatory = $true)]
    [string]$To,

    [string]$Collector = (Join-Path $PSScriptRoot '..\build\ttd-exec-coverage\bin\ttd_exec_coverage.exe'),
    [string]$ModuleName = 'BEA.exe',
    [string]$ExpectedBase = '',

    [ValidateRange(1, 1000000)]
    [int]$EventLimit = 100000,

    # Optional inclusive-start exclusive-end VA ranges "0xSTART:0xEND" for witnessed-writes grade.
    # When any write/overwrite event occurs, every event PC must fall in one range.
    [string[]]$WriterBodyRanges = @()
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
        if ($reader.ReadUInt16() -ne 0x5A4D) { throw "Not an MZ executable: $Path" }
        $stream.Position = 0x3C
        $peOffset = $reader.ReadUInt32()
        if ($peOffset -gt $stream.Length - 0x80) { throw "Invalid PE header offset: $Path" }
        $stream.Position = $peOffset
        if ($reader.ReadUInt32() -ne 0x00004550) { throw "Missing PE signature: $Path" }
        $machine = $reader.ReadUInt16()
        $sectionCount = $reader.ReadUInt16()
        $timestamp = $reader.ReadUInt32()
        $stream.Position = $peOffset + 20
        $optionalBytes = $reader.ReadUInt16()
        $characteristics = $reader.ReadUInt16()
        $optionalOffset = $peOffset + 24
        if ($optionalBytes -lt 68 -or
            $optionalOffset + $optionalBytes -gt $stream.Length) {
            throw "Invalid optional-header size: $Path"
        }
        $stream.Position = $optionalOffset
        $magic = $reader.ReadUInt16()
        if ($machine -ne 0x14C -or $magic -ne 0x10B) {
            throw "TTD data-write collection requires a PE32/x86 target: $Path"
        }
        $stream.Position = $optionalOffset + 28
        $imageBase = $reader.ReadUInt32()
        $stream.Position = $optionalOffset + 56
        $sizeOfImage = $reader.ReadUInt32()
        $stream.Position = $optionalOffset + 64
        $checksum = $reader.ReadUInt32()
        if ($sizeOfImage -eq 0) { throw "PE SizeOfImage is zero: $Path" }
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

function Assert-FactsUnchanged {
    param($Before, $After, [string]$Label)

    if ($Before.bytes -ne $After.bytes -or
        [string]$Before.sha256 -cne [string]$After.sha256 -or
        [string]$Before.lastWriteUtc -cne [string]$After.lastWriteUtc) {
        throw "$Label changed during TTD replay."
    }
}

function Test-PathIsUnder {
    param([string]$Path, [string]$Ancestor)

    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    $fullAncestor = [System.IO.Path]::GetFullPath($Ancestor).TrimEnd('\')
    return $fullPath.StartsWith(
        $fullAncestor + '\',
        [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-RequiredProperty {
    param($Owner, [string]$Name, [string]$Label)

    $property = $Owner.PSObject.Properties[$Name]
    if ($null -eq $property) { throw "$Label is missing $Name." }
    return $property.Value
}

function Get-RequiredBoolean {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredProperty $Owner $Name $Label
    if ($value -isnot [bool]) { throw "$Label field $Name must be a JSON boolean." }
    return [bool]$value
}

function Get-RequiredUInt64 {
    param($Owner, [string]$Name, [string]$Label)

    $text = [string](Get-RequiredProperty $Owner $Name $Label)
    if ($text -notmatch '^[0-9]+$') {
        throw "$Label field $Name must be an unsigned decimal integer."
    }
    return [uint64]::Parse($text)
}

function Get-OptionalUInt64 {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredProperty $Owner $Name $Label
    if ($null -eq $value) { return $null }
    $text = [string]$value
    if ($text -notmatch '^[0-9]+$') {
        throw "$Label field $Name must be null or an unsigned decimal integer."
    }
    return [uint64]::Parse($text)
}

function Get-NullableIndex {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredProperty $Owner $Name $Label
    if ($null -eq $value) { return $null }
    $text = [string]$value
    if ($text -notmatch '^[0-9]+$') {
        throw "$Label field $Name must be null or a non-negative integer."
    }
    return [int]::Parse($text)
}

function Assert-HexText {
    param($Owner, [string]$Name, [string]$Label)

    $text = [string](Get-RequiredProperty $Owner $Name $Label)
    if ($text -notmatch '^0x[0-9A-F]+$') {
        throw "$Label field $Name must be canonical uppercase hexadecimal."
    }
    return $text
}

function Convert-HexUInt64 {
    param([string]$Text, [string]$Label)

    if ($Text -notmatch '^0x[0-9A-Fa-f]+$') { throw "$Label must be hexadecimal." }
    return [Convert]::ToUInt64($Text.Substring(2), 16)
}

function Convert-UnsignedLiteral {
    param([string]$Text, [string]$Label)

    if ($Text -match '^0[xX][0-9A-Fa-f]+$') {
        return [Convert]::ToUInt64($Text.Substring(2), 16)
    }
    if ($Text -notmatch '^[0-9]+$') {
        throw "$Label must be an unsigned decimal or hexadecimal integer."
    }
    return [uint64]::Parse($Text)
}

function Read-DataWriteTargetTable {
    param([Parameter(Mandatory = $true)][string]$Path)

    $lines = [System.IO.File]::ReadAllLines($Path)
    $header = "target_index`taddress`tsize`texpected_overwrite_count`texpected_write_count"
    if ($lines.Count -lt 2 -or $lines[0] -cne $header) {
        throw 'Snapshotted data-write target table has an unexpected header or no rows.'
    }
    $rows = [System.Collections.Generic.List[object]]::new()
    for ($lineIndex = 1; $lineIndex -lt $lines.Count; $lineIndex++) {
        $fields = $lines[$lineIndex].Split([char]9)
        if ($fields.Count -ne 5 -or [string]::IsNullOrEmpty($lines[$lineIndex])) {
            throw "Snapshotted data-write target row $lineIndex is malformed."
        }
        $index = Convert-UnsignedLiteral $fields[0] "target row $lineIndex index"
        $address = Convert-UnsignedLiteral $fields[1] "target row $lineIndex address"
        $size = Convert-UnsignedLiteral $fields[2] "target row $lineIndex size"
        if ($index -ne $rows.Count -or $address -eq 0 -or $address -ge 0x100000000 -or
            $size -lt 1 -or $size -gt 16 -or $size -gt 0x100000000 - $address) {
            throw "Snapshotted data-write target row $lineIndex is out of range or non-contiguous."
        }
        $expectedOverwrite = if ([string]::IsNullOrEmpty($fields[3])) {
            $null
        } else { Convert-UnsignedLiteral $fields[3] "target row $lineIndex expected overwrite" }
        $expectedWrite = if ([string]::IsNullOrEmpty($fields[4])) {
            $null
        } else { Convert-UnsignedLiteral $fields[4] "target row $lineIndex expected write" }
        $rows.Add([pscustomobject]@{
            target_index = [uint64]$index
            address = ('0x{0:X}' -f $address)
            size = [uint64]$size
            expected_overwrite_count = $expectedOverwrite
            expected_write_count = $expectedWrite
        })
    }
    for ($left = 0; $left -lt $rows.Count; $left++) {
        $leftStart = Convert-HexUInt64 $rows[$left].address "target $left address"
        $leftEnd = $leftStart + $rows[$left].size
        for ($right = $left + 1; $right -lt $rows.Count; $right++) {
            $rightStart = Convert-HexUInt64 $rows[$right].address "target $right address"
            $rightEnd = $rightStart + $rows[$right].size
            if ($leftStart -lt $rightEnd -and $rightStart -lt $leftEnd) {
                throw "Snapshotted data-write targets $left and $right overlap."
            }
        }
    }
    return @($rows)
}

function Assert-TargetTableMatchesRows {
    param($TableRows, $Targets)

    if ($TableRows.Count -ne $Targets.Count) {
        throw 'Snapshotted target-table count disagrees with JSON target rows.'
    }
    $allExpectationsPassed = $true
    for ($index = 0; $index -lt $Targets.Count; $index++) {
        $table = $TableRows[$index]
        $target = $Targets[$index]
        $jsonExpectedOverwrite = Get-OptionalUInt64 $target `
            'expected_overwrite_count' "target $index"
        $jsonExpectedWrite = Get-OptionalUInt64 $target `
            'expected_write_count' "target $index"
        $expectedOverwriteEqual =
            ($null -eq $table.expected_overwrite_count -and $null -eq $jsonExpectedOverwrite) -or
            ($null -ne $table.expected_overwrite_count -and $null -ne $jsonExpectedOverwrite -and
             [uint64]$table.expected_overwrite_count -eq [uint64]$jsonExpectedOverwrite)
        $expectedWriteEqual =
            ($null -eq $table.expected_write_count -and $null -eq $jsonExpectedWrite) -or
            ($null -ne $table.expected_write_count -and $null -ne $jsonExpectedWrite -and
             [uint64]$table.expected_write_count -eq [uint64]$jsonExpectedWrite)
        if ([uint64]$table.target_index -ne [uint64]$target.target_index -or
            [string]$table.address -cne [string]$target.address -or
            [uint64]$table.size -ne [uint64]$target.size -or
            -not $expectedOverwriteEqual -or -not $expectedWriteEqual) {
            throw "Snapshotted target-table row $index disagrees with its JSON target row."
        }
        $observedOverwrite = Get-RequiredUInt64 $target `
            'observed_overwrite_count' "target $index"
        $observedWrite = Get-RequiredUInt64 $target `
            'observed_write_count' "target $index"
        $rowPassed =
            ($null -eq $table.expected_overwrite_count -or
             [uint64]$table.expected_overwrite_count -eq $observedOverwrite) -and
            ($null -eq $table.expected_write_count -or
             [uint64]$table.expected_write_count -eq $observedWrite)
        if ((Get-RequiredBoolean $target 'expectations_passed' "target $index") -ne
            $rowPassed) {
            throw "Data-write target $index expectation result disagrees with the frozen TSV."
        }
        $allExpectationsPassed = $allExpectationsPassed -and $rowPassed
    }
    return $allExpectationsPassed
}

function Convert-TtdPosition {
    param([string]$Text, [string]$Label)

    if ($Text -notmatch '^(0x[0-9A-Fa-f]+|[0-9]+):(0x[0-9A-Fa-f]+|[0-9]+)$') {
        throw "$Label must be SEQUENCE:STEPS."
    }
    $parts = $Text.Split(':')
    function Convert-Part([string]$Part) {
        if ($Part.StartsWith('0x', [System.StringComparison]::OrdinalIgnoreCase)) {
            return [Convert]::ToUInt64($Part.Substring(2), 16)
        }
        return [uint64]::Parse($Part)
    }
    return ('0x{0:X}:0x{1:X}' -f (Convert-Part $parts[0]), (Convert-Part $parts[1]))
}

function Compare-TtdPosition {
    param([string]$Left, [string]$Right)

    $leftCanonical = Convert-TtdPosition $Left 'left TTD position'
    $rightCanonical = Convert-TtdPosition $Right 'right TTD position'
    $leftParts = $leftCanonical.Split(':')
    $rightParts = $rightCanonical.Split(':')
    $leftSequence = Convert-HexUInt64 $leftParts[0] 'left sequence'
    $rightSequence = Convert-HexUInt64 $rightParts[0] 'right sequence'
    if ($leftSequence -lt $rightSequence) { return -1 }
    if ($leftSequence -gt $rightSequence) { return 1 }
    $leftSteps = Convert-HexUInt64 $leftParts[1] 'left steps'
    $rightSteps = Convert-HexUInt64 $rightParts[1] 'right steps'
    if ($leftSteps -lt $rightSteps) { return -1 }
    if ($leftSteps -gt $rightSteps) { return 1 }
    return 0
}

function Assert-TtdPosition {
    param($Owner, [string]$Name, [string]$Label)

    $text = [string](Get-RequiredProperty $Owner $Name $Label)
    if ($text -notmatch '^0x[0-9A-F]+:0x[0-9A-F]+$') {
        throw "$Label field $Name must be a canonical TTD position."
    }
    return $text
}

function Assert-MemoryImage {
    param(
        $Image,
        [string]$ExpectedAddress,
        [uint64]$ExpectedSize,
        [string]$Label,
        [string]$ExpectedObservationPosition = '',
        [switch]$AllowInvalid
    )

    $address = Assert-HexText $Image 'address' $Label
    $validBytes = Get-RequiredUInt64 $Image 'valid_bytes' $Label
    $rangeCount = Get-RequiredUInt64 $Image 'range_count' $Label
    $singleRange = Get-RequiredBoolean $Image 'single_range' $Label
    $queryValid = Get-RequiredBoolean $Image 'query_valid' $Label
    $observationPosition = Assert-TtdPosition $Image 'observation_position' $Label
    $observation = Assert-HexText $Image 'observation_sequence' $Label
    $source = Assert-HexText $Image 'source_sequence' $Label
    $sourceMatches = Get-RequiredBoolean $Image `
        'source_sequence_matches_observation' $Label
    $positionSequence = $observationPosition.Split(':')[0]
    if ($positionSequence -cne $observation) {
        throw "$Label observation sequence disagrees with its full position."
    }
    if (-not [string]::IsNullOrEmpty($ExpectedObservationPosition) -and
        $observationPosition -cne $ExpectedObservationPosition) {
        throw "$Label was not observed at the required replay position."
    }
    $observedMatch = (Convert-HexUInt64 $source "$Label source") -eq
        (Convert-HexUInt64 $observation "$Label observation")
    if ($sourceMatches -ne $observedMatch) {
        throw "$Label source-sequence match field is false metadata."
    }
    if ((Convert-HexUInt64 $source "$Label source") -gt
        (Convert-HexUInt64 $observation "$Label observation")) {
        throw "$Label memory source comes from a future sequence."
    }
    $hex = [string](Get-RequiredProperty $Image 'hex' $Label)
    if (-not $queryValid) {
        if (-not $AllowInvalid) {
            throw "$Label is not a complete single-range memory observation."
        }
        $addressIsDiagnostic = $address -ceq $ExpectedAddress -or
            ($address -ceq '0x0' -and $validBytes -eq 0)
        if (-not $addressIsDiagnostic -or $validBytes -gt $ExpectedSize -or
            $rangeCount -gt 1 -or $hex -notmatch '^[0-9A-F]*$' -or
            $hex.Length -ne 2 * $validBytes -or
            ($singleRange -and $rangeCount -ne 1)) {
            throw "$Label carries a malformed invalid-memory observation."
        }
        return [ordered]@{
            hex = ''
            queryValid = $false
            sequenceMatched = $sourceMatches
            observationPosition = $observationPosition
        }
    }
    if ($address -cne $ExpectedAddress) { throw "$Label address disagrees with its target." }
    if ($validBytes -ne $ExpectedSize -or $rangeCount -ne 1 -or -not $singleRange) {
        throw "$Label is not a complete single-range memory observation."
    }
    if ($hex -notmatch '^[0-9A-F]*$' -or $hex.Length -ne 2 * $ExpectedSize) {
        throw "$Label hex does not contain exactly $ExpectedSize byte(s)."
    }
    return [ordered]@{
        hex = $hex
        queryValid = $true
        sequenceMatched = $sourceMatches
        observationPosition = $observationPosition
    }
}

function Assert-DataWriteRelationships {
    param(
        $Targets,
        $Events,
        $Pairs,
        $Summary,
        [string]$ActualFrom,
        [string]$FinalPosition,
        [switch]$AllowInvalidEndpoints,
        [switch]$AllowInvalidEventMemory
    )

    $overwriteCounts = [uint64[]]::new($Targets.Count)
    $writeCounts = [uint64[]]::new($Targets.Count)
    $pairCounts = [uint64[]]::new($Targets.Count)
    $targetAddresses = [string[]]::new($Targets.Count)
    $targetSizes = [uint64[]]::new($Targets.Count)
    $initialImages = [object[]]::new($Targets.Count)
    $finalImages = [object[]]::new($Targets.Count)
    $eventImages = [object[]]::new($Events.Count)
    $endpointQueriesValid = $true
    $eventMemoryValid = $true
    $allEventEpochsZero = $true
    $lastEventPosition = $null

    $targetEvidencePassed = $true
    $targetGrades = [System.Collections.Generic.List[string]]::new()
    for ($index = 0; $index -lt $Targets.Count; $index++) {
        $target = $Targets[$index]
        if ([int](Get-RequiredProperty $target 'target_index' "target $index") -ne $index) {
            throw "Data-write target indexes are not contiguous at $index."
        }
        $targetAddresses[$index] = Assert-HexText $target 'address' "target $index"
        $targetSizes[$index] = Get-RequiredUInt64 $target 'size' "target $index"
        if ($targetSizes[$index] -lt 1 -or $targetSizes[$index] -gt 16) {
            throw "Data-write target $index has an invalid size."
        }
        $initialImages[$index] = Assert-MemoryImage `
            $target.initial_memory $targetAddresses[$index] `
            $targetSizes[$index] "target $index initial" `
            -ExpectedObservationPosition $ActualFrom `
            -AllowInvalid:$AllowInvalidEndpoints
        $finalImages[$index] = Assert-MemoryImage `
            $target.final_memory $targetAddresses[$index] `
            $targetSizes[$index] "target $index final" `
            -ExpectedObservationPosition $FinalPosition `
            -AllowInvalid:$AllowInvalidEndpoints
        $endpointQueriesValid = $endpointQueriesValid -and
            $initialImages[$index].queryValid -and $finalImages[$index].queryValid
    }

    for ($index = 0; $index -lt $Events.Count; $index++) {
        $event = $Events[$index]
        if ([int](Get-RequiredProperty $event 'event_index' "event $index") -ne $index) {
            throw "Data-write event indexes are not contiguous at $index."
        }
        $type = [string](Get-RequiredProperty $event 'event_type' "event $index")
        if (@('Overwrite', 'Write') -cnotcontains $type) {
            throw "Data-write event $index has unexpected type '$type'."
        }
        $targetIndex = Get-NullableIndex $event 'target_index' "event $index"
        $pairIndex = Get-NullableIndex $event 'pair_index' "event $index"
        $intersections = Get-RequiredUInt64 $event 'intersecting_target_count' "event $index"
        $eventEpoch = Get-RequiredUInt64 $event 'continuity_epoch' "event $index"
        $allEventEpochsZero = $allEventEpochsZero -and $eventEpoch -eq 0
        $eventPosition = Assert-TtdPosition $event 'position' "event $index"
        $previousPosition = Assert-TtdPosition $event 'previous_position' "event $index"
        if ((Compare-TtdPosition $previousPosition $eventPosition) -ge 0 -or
            (Compare-TtdPosition $eventPosition $ActualFrom) -le 0 -or
            (Compare-TtdPosition $eventPosition $FinalPosition) -gt 0 -or
            ($null -ne $lastEventPosition -and
             (Compare-TtdPosition $eventPosition $lastEventPosition) -lt 0)) {
            throw "Data-write event $index lies outside or reverses the exact replay window."
        }
        $lastEventPosition = $eventPosition
        foreach ($field in @('pc', 'sp', 'fp')) {
            Assert-HexText $event $field "event $index" | Out-Null
        }
        $accessAddressText = Assert-HexText $event 'access_address' "event $index"
        $accessAddress = Convert-HexUInt64 $accessAddressText "event $index access address"
        $accessSize = Get-RequiredUInt64 $event 'access_size' "event $index"
        if ($accessSize -eq 0 -or $accessAddress -ge 0x100000000 -or
            $accessSize -gt 0x100000000 - $accessAddress) {
            throw "Data-write event $index has an invalid x86 access range."
        }
        $computedIntersections = [System.Collections.Generic.List[int]]::new()
        for ($candidate = 0; $candidate -lt $Targets.Count; $candidate++) {
            $candidateStart = Convert-HexUInt64 $targetAddresses[$candidate] `
                "target $candidate address"
            $candidateEnd = $candidateStart + $targetSizes[$candidate]
            if ($accessAddress -lt $candidateEnd -and
                $candidateStart -lt $accessAddress + $accessSize) {
                $computedIntersections.Add($candidate)
            }
        }
        if ($intersections -ne $computedIntersections.Count) {
            throw "Data-write event $index intersection count disagrees with the frozen targets."
        }
        foreach ($field in @('control_registers_valid', 'integer_registers_valid', 'register_views_agree')) {
            if (-not (Get-RequiredBoolean $event $field "event $index")) {
                throw "Data-write event $index has an invalid register view."
            }
        }
        if ($null -eq $targetIndex) {
            if ($computedIntersections.Count -eq 1 -or $null -ne $pairIndex) {
                throw "Ambiguous data-write event $index carries a target or pair backlink."
            }
            continue
        }
        if ($targetIndex -lt 0 -or $targetIndex -ge $Targets.Count -or
            $computedIntersections.Count -ne 1 -or
            $computedIntersections[0] -ne $targetIndex) {
            throw "Data-write event $index has an invalid target relationship."
        }
        $eventImages[$index] = Assert-MemoryImage `
            $event.observed_memory $targetAddresses[$targetIndex] `
            $targetSizes[$targetIndex] "event $index memory" `
            -ExpectedObservationPosition $eventPosition `
            -AllowInvalid:$AllowInvalidEventMemory
        $eventMemoryValid = $eventMemoryValid -and $eventImages[$index].queryValid
        if ($type -ceq 'Overwrite') { $overwriteCounts[$targetIndex]++ }
        else { $writeCounts[$targetIndex]++ }
    }

    $usedEvents = [System.Collections.Generic.HashSet[int]]::new()
    for ($index = 0; $index -lt $Pairs.Count; $index++) {
        $pair = $Pairs[$index]
        if ([int](Get-RequiredProperty $pair 'pair_index' "pair $index") -ne $index) {
            throw "Data-write pair indexes are not contiguous at $index."
        }
        $targetIndex = [int](Get-RequiredProperty $pair 'target_index' "pair $index")
        $overwriteIndex = [int](Get-RequiredProperty $pair 'overwrite_event_index' "pair $index")
        $writeIndex = [int](Get-RequiredProperty $pair 'write_event_index' "pair $index")
        if ($targetIndex -lt 0 -or $targetIndex -ge $Targets.Count -or
            $overwriteIndex -lt 0 -or $overwriteIndex -ge $Events.Count -or
            $writeIndex -lt 0 -or $writeIndex -ge $Events.Count -or
            -not $usedEvents.Add($overwriteIndex) -or -not $usedEvents.Add($writeIndex)) {
            throw "Data-write pair $index has invalid or duplicate event backlinks."
        }
        $overwrite = $Events[$overwriteIndex]
        $written = $Events[$writeIndex]
        if ([string]$overwrite.event_type -cne 'Overwrite' -or
            [string]$written.event_type -cne 'Write' -or
            [int]$overwrite.target_index -ne $targetIndex -or
            [int]$written.target_index -ne $targetIndex -or
            [int]$overwrite.pair_index -ne $index -or
            [int]$written.pair_index -ne $index) {
            throw "Data-write pair $index has broken event backlinks."
        }
        foreach ($field in @(
                'unique_thread_id', 'position', 'previous_position', 'pc', 'sp', 'fp',
                'access_address', 'access_size', 'continuity_epoch', 'context_flags')) {
            if ([string]$overwrite.$field -cne [string]$written.$field) {
                throw "Data-write pair $index crosses a different $field boundary."
            }
        }
        foreach ($register in @('eax','ebx','ecx','edx','esi','edi','ebp','esp','eip','eflags')) {
            if ([string]$overwrite.registers.$register -cne [string]$written.registers.$register) {
                throw "Data-write pair $index crosses a different $register register view."
            }
        }
        if ([string]$pair.grade -cne 'STRUCTURAL_WRITE_PAIR' -or
            -not (Get-RequiredBoolean $pair 'checks_passed' "pair $index")) {
            throw "Data-write pair $index does not carry the structural pair grade."
        }
        $preHex = [string]$overwrite.observed_memory.hex
        $postHex = [string]$written.observed_memory.hex
        $changed = Get-RequiredBoolean $pair 'changed' "pair $index"
        if ($changed -ne ($preHex -cne $postHex)) {
            throw "Data-write pair $index changed flag disagrees with its bytes."
        }
        $pairCounts[$targetIndex]++
    }

    for ($index = 0; $index -lt $Targets.Count; $index++) {
        $target = $Targets[$index]
        if ((Get-RequiredUInt64 $target 'observed_overwrite_count' "target $index") -ne
                $overwriteCounts[$index] -or
            (Get-RequiredUInt64 $target 'observed_write_count' "target $index") -ne
                $writeCounts[$index] -or
            (Get-RequiredUInt64 $target 'observed_pair_count' "target $index") -ne
                $pairCounts[$index]) {
            throw "Data-write target $index aggregate counts disagree with raw rows."
        }
        $targetEvents = @($Events | Where-Object { $null -ne $_.target_index -and [int]$_.target_index -eq $index })
        $targetPairs = @($Pairs | Where-Object { [int]$_.target_index -eq $index } |
            Sort-Object { [int]$_.overwrite_event_index })
        $initialSequenceMatched = [bool]$initialImages[$index].sequenceMatched
        $finalSequenceMatched = [bool]$finalImages[$index].sequenceMatched
        $expectedOverwrite = Get-OptionalUInt64 $target `
            'expected_overwrite_count' "target $index"
        $expectedWrite = Get-OptionalUInt64 $target `
            'expected_write_count' "target $index"
        $eventMemorySequenceSourced = $false
        $chainClosed = $false
        $grade = 'BLOCKED'
        if ($null -eq $expectedOverwrite -or $null -eq $expectedWrite) {
            $grade = 'DISCOVERY_ONLY'
        } elseif ($expectedOverwrite -eq $expectedWrite -and $expectedWrite -eq 0) {
            $chainClosed = $targetEvents.Count -eq 0 -and $targetPairs.Count -eq 0 -and
                $overwriteCounts[$index] -eq 0 -and $writeCounts[$index] -eq 0
            if ($chainClosed) { $grade = 'NO_WRITE_CALLBACK_WITNESS' }
        } elseif ($expectedOverwrite -eq $expectedWrite -and $expectedWrite -gt 0 -and
            $targetEvents.Count -eq $expectedWrite * 2 -and
            $targetPairs.Count -eq $expectedWrite -and
            $overwriteCounts[$index] -eq $expectedWrite -and
            $writeCounts[$index] -eq $expectedWrite) {
                $cursorHex = $null
                $chainClosed = $true
                $eventMemorySequenceSourced = $true
                $previousWriteIndex = -1
                foreach ($pair in $targetPairs) {
                    $overwriteIndex = [int]$pair.overwrite_event_index
                    $writeIndex = [int]$pair.write_event_index
                    if ($overwriteIndex -ge $writeIndex -or
                        $overwriteIndex -le $previousWriteIndex) {
                        $chainClosed = $false
                        break
                    }
                    $preImage = $eventImages[$overwriteIndex]
                    $postImage = $eventImages[$writeIndex]
                    $pairMemorySourced = $null -ne $preImage -and $null -ne $postImage -and
                        $preImage.queryValid -and $postImage.queryValid -and
                        $preImage.sequenceMatched -and $postImage.sequenceMatched
                    $eventMemorySequenceSourced =
                        $eventMemorySequenceSourced -and $pairMemorySourced
                    if (-not $pairMemorySourced -or
                        ($null -ne $cursorHex -and [string]$preImage.hex -cne $cursorHex)) {
                        $chainClosed = $false
                        break
                    }
                    $cursorHex = [string]$postImage.hex
                    $previousWriteIndex = $writeIndex
                }
                $chainClosed = $chainClosed -and $eventMemorySequenceSourced -and
                    $null -ne $cursorHex
                if ($chainClosed) { $grade = 'WATCHPOINT_CHAIN_CLOSED' }
        }
        $evidencePassed = $chainClosed -and @(
            'NO_WRITE_CALLBACK_WITNESS','WATCHPOINT_CHAIN_CLOSED'
        ) -ccontains $grade
        if ((Get-RequiredBoolean $target 'initial_sequence_matched' "target $index") -ne
                $initialSequenceMatched -or
            (Get-RequiredBoolean $target 'final_sequence_matched' "target $index") -ne
                $finalSequenceMatched -or
            (Get-RequiredBoolean $target 'event_memory_sequence_sourced' "target $index") -ne
                $eventMemorySequenceSourced -or
            (Get-RequiredBoolean $target 'transition_chain_closed' "target $index") -ne
                $chainClosed -or
            (Get-RequiredBoolean $target 'evidence_checks_passed' "target $index") -ne
                $evidencePassed -or
            [string](Get-RequiredProperty $target 'evidence_grade' "target $index") -cne
                $grade) {
            throw "Data-write target $index evidence grade disagrees with raw relationships."
        }
        $targetEvidencePassed = $targetEvidencePassed -and $evidencePassed
        $targetGrades.Add($grade)
    }

    $orphanCount = [uint64]($Events.Count - $usedEvents.Count)
    $pairingComplete = $orphanCount -eq 0 -and $Pairs.Count * 2 -eq $Events.Count
    if ((Get-RequiredUInt64 $Summary 'event_count' 'summary') -ne $Events.Count -or
        (Get-RequiredUInt64 $Summary 'pair_count' 'summary') -ne $Pairs.Count -or
        (Get-RequiredUInt64 $Summary 'orphan_event_count' 'summary') -ne $orphanCount -or
        (Get-RequiredBoolean $Summary 'pairing_complete' 'summary') -ne $pairingComplete) {
        throw 'Data-write summary counts disagree with raw relationships.'
    }
    return [ordered]@{
        pairCount = [uint64]$Pairs.Count
        orphanEventCount = $orphanCount
        pairingComplete = $pairingComplete
        endpointQueriesValid = $endpointQueriesValid
        eventMemoryValid = $eventMemoryValid
        allEventEpochsZero = $allEventEpochsZero
        targetEvidencePassed = $targetEvidencePassed
        targetGrades = @($targetGrades)
    }
}

function Assert-DataWriteGapAccounting {
    param($GapSummary, $Summary, $Events, $ContinuityBreakRows, $Relationships)

    $total = Get-RequiredUInt64 $GapSummary 'total' 'gap summary'
    $noGap = Get-RequiredUInt64 $GapSummary 'kind_no_gap' 'gap summary'
    $contextSwitch = Get-RequiredUInt64 $GapSummary 'kind_context_switch' 'gap summary'
    $unrecorded = Get-RequiredUInt64 $GapSummary 'kind_unrecorded' 'gap summary'
    $large = Get-RequiredUInt64 $GapSummary 'kind_large' 'gap summary'
    if ($total -ne $noGap + $contextSwitch + $unrecorded + $large) {
        throw 'Data-write gap-kind counts do not sum to the reported total.'
    }
    $eventNames = @(
        'SyntheticSequence','CodeCacheFlush','PreAtomicOperation',
        'PotentialAtomicCollision','EtwEvent','DebugBreak','FastFail','KernelCall',
        'SyntheticFallback','ExceptionDispatch','UnknownInstruction','ThreadSuspended',
        'SListRollback','SyncPoint','PauseEmulation','StopEmulation','Throttled'
    )
    [uint64]$eventTotal = 0
    foreach ($name in $eventNames) {
        $eventTotal += Get-RequiredUInt64 $GapSummary "event_$name" 'gap summary'
    }
    if ($eventTotal -ne $total) {
        throw 'Data-write gap-event counts do not sum to the reported total.'
    }
    $nontrivial = Get-RequiredUInt64 $Summary 'nontrivial_gap_count' 'summary'
    if ($nontrivial -ne $contextSwitch + $unrecorded + $large) {
        throw 'Data-write nontrivial-gap summary disagrees with gap-kind counts.'
    }
    $continuityBreaks = Get-RequiredUInt64 $Summary 'continuity_break_count' 'summary'
    if ($continuityBreaks -ne $ContinuityBreakRows.Count) {
        throw 'Data-write continuity-break rows disagree with the summary count.'
    }
    if ($nontrivial -eq 0 -and $continuityBreaks -eq 0 -and
        -not $Relationships.allEventEpochsZero) {
        throw 'Zero-gap summary contains an event from a later continuity epoch.'
    }
    $truncated = Get-RequiredBoolean $Summary 'truncated' 'summary'
    $callbackFailed = Get-RequiredBoolean $Summary 'callback_failed' 'summary'
    $callbackHits = Get-RequiredUInt64 $Summary 'callback_hits' 'summary'
    if (-not $truncated -and -not $callbackFailed -and $callbackHits -ne $Events.Count) {
        throw 'Data-write callback count disagrees with complete raw event rows.'
    }
    return [ordered]@{
        total = $total
        nontrivial = $nontrivial
        continuityBreaks = $continuityBreaks
        allEventEpochsZero = [bool]$Relationships.allEventEpochsZero
        callbackHits = $callbackHits
        reconciled = $true
    }
}

# Gap-free READY uses the collector exact-window policy.
# Witnessed-writes is a distinct wrapper grade: store pairs may be published
# when gaps are ledgered, never as gap-free READY.
function Get-DataWritesGapFreePromotionPolicy {
    return 'bea.ttd.data-writes.exact-window-watchpoint-chain.v1'
}

function Get-DataWritesWitnessedPromotionPolicy {
    return 'bea.ttd.data-writes.witnessed-writes-with-gap-ledger.v1'
}

function Parse-WriterBodyRanges {
    param([string[]]$Ranges)

    $parsed = [System.Collections.Generic.List[object]]::new()
    foreach ($raw in @($Ranges)) {
        if ([string]::IsNullOrWhiteSpace($raw)) { continue }
        $text = $raw.Trim()
        if ($text -notmatch '^(0x[0-9A-Fa-f]+):(0x[0-9A-Fa-f]+)$') {
            throw "Writer body range must be 0xSTART:0xEND (exclusive end): $raw"
        }
        $start = [uint64]::Parse(
            $Matches[1].Substring(2),
            [System.Globalization.NumberStyles]::AllowHexSpecifier)
        $end = [uint64]::Parse(
            $Matches[2].Substring(2),
            [System.Globalization.NumberStyles]::AllowHexSpecifier)
        if ($end -le $start) {
            throw "Writer body range end must be exclusive and greater than start: $raw"
        }
        $parsed.Add([ordered]@{
            start = $start
            endExclusive = $end
            text = ('0x{0:X}:0x{1:X}' -f $start, $end)
        }) | Out-Null
    }
    # Always return a true zero-length object[] (bare @() collapses to $null).
    return , [object[]]$parsed.ToArray()
}

function Test-PcInWriterBodyRanges {
    param(
        [uint64]$Pc,
        $Ranges
    )
    foreach ($range in @($Ranges)) {
        if ($Pc -ge [uint64]$range.start -and $Pc -lt [uint64]$range.endExclusive) {
            return $true
        }
    }
    return $false
}

function Assert-DataWriteWitnessedWrites {
    <#
    .SYNOPSIS
      Grade witnessed field stores without requiring a gap-free window.
    .NOTES
      Fails closed when write events exist but no body ranges were supplied.
      Does not authorize gap-free READY or call-context return linkage.
    #>
    param(
        $Events,
        $Pairs,
        $Summary,
        $GapAccounting,
        $Relationships,
        [bool]$ReplayComplete,
        [bool]$ExactReplayWindow,
        [bool]$ExpectationsPassed,
        [bool]$CountersSane,
        [bool]$OrderingValid,
        [bool]$ContextsValid,
        [bool]$PairingValid,
        [bool]$SnapshotQueriesValid,
        [uint64]$AmbiguousCallbacks,
        [uint64]$NontrivialGapCount,
        [uint64]$ContinuityBreakCount,
        $WriterBodyRanges
    )

    $truncated = Get-RequiredBoolean $Summary 'truncated' 'summary'
    $callbackFailed = Get-RequiredBoolean $Summary 'callback_failed' 'summary'
    $targetEvidencePassed = [bool]$Relationships.targetEvidencePassed
    $pairingComplete = [bool]$Relationships.pairingComplete
    $reasons = [System.Collections.Generic.List[string]]::new()

    if (-not $ReplayComplete) { $reasons.Add('replay_incomplete') | Out-Null }
    if (-not $ExactReplayWindow) { $reasons.Add('window_not_exact') | Out-Null }
    if (-not $ExpectationsPassed) { $reasons.Add('expectations_failed') | Out-Null }
    if (-not $CountersSane) { $reasons.Add('counters_insane') | Out-Null }
    if ($truncated) { $reasons.Add('truncated') | Out-Null }
    if ($callbackFailed) { $reasons.Add('callback_failed') | Out-Null }
    if (-not $OrderingValid) { $reasons.Add('ordering_invalid') | Out-Null }
    if (-not $ContextsValid) { $reasons.Add('contexts_invalid') | Out-Null }
    if (-not $PairingValid) { $reasons.Add('pairing_invalid') | Out-Null }
    if (-not $pairingComplete) { $reasons.Add('pairing_incomplete') | Out-Null }
    if (-not $targetEvidencePassed) { $reasons.Add('target_evidence_failed') | Out-Null }
    if (-not $SnapshotQueriesValid) { $reasons.Add('snapshot_queries_invalid') | Out-Null }
    if ($AmbiguousCallbacks -ne 0) { $reasons.Add('ambiguous_callbacks') | Out-Null }
    if (-not [bool]$GapAccounting.reconciled) { $reasons.Add('gap_accounting_unreconciled') | Out-Null }

    $rangeList = @(
        @($WriterBodyRanges) | Where-Object { $null -ne $_ -and $null -ne $_.start }
    )
    $eventCount = @($Events).Count
    $outOfBody = [System.Collections.Generic.List[string]]::new()
    if ($eventCount -gt 0 -and $rangeList.Count -eq 0) {
        $reasons.Add('writer_body_ranges_required_when_events_present') | Out-Null
    }
    foreach ($event in @($Events)) {
        $pcText = Assert-HexText $event 'pc' 'witnessed event'
        $pc = Convert-HexUInt64 $pcText 'witnessed event pc'
        if ($rangeList.Count -gt 0 -and -not (Test-PcInWriterBodyRanges -Pc $pc -Ranges $rangeList)) {
            $outOfBody.Add($pcText) | Out-Null
        }
    }
    if ($outOfBody.Count -gt 0) {
        $reasons.Add('writer_pc_outside_body') | Out-Null
    }

    # Poison: gap-free READY must not be claimed via this grade when gaps exist.
    # (Callers write separate markers; this flag is advisory for receipts.)
    $wouldBeGapFree =
        $NontrivialGapCount -eq 0 -and $ContinuityBreakCount -eq 0 -and
        [bool]$Relationships.allEventEpochsZero

    $eligible = $reasons.Count -eq 0
    return [ordered]@{
        eligible = $eligible
        promotionPolicy = (Get-DataWritesWitnessedPromotionPolicy)
        reasons = @($reasons)
        writerBodyRanges = @($rangeList | ForEach-Object { $_.text })
        outOfBodyPcs = @($outOfBody | Select-Object -Unique)
        eventCount = [uint64]$eventCount
        pairCount = [uint64]@($Pairs).Count
        nontrivialGapCount = $NontrivialGapCount
        continuityBreakCount = $ContinuityBreakCount
        wouldAlsoBeGapFree = $wouldBeGapFree
    }
}

function Resolve-MissingDataWriteExitCode {
    param([int]$CollectorExitCode)
    if ($CollectorExitCode -ne 0) { return $CollectorExitCode }
    return 12
}

$canonicalFrom = Convert-TtdPosition $From '-From'
$canonicalTo = Convert-TtdPosition $To '-To'
if ((Compare-TtdPosition $canonicalFrom $canonicalTo) -ge 0) {
    throw '-From must precede -To for an exact nonempty data-write window.'
}
$tracePath = (Resolve-Path -LiteralPath $TraceFile).Path
$targetPath = (Resolve-Path -LiteralPath $TargetExe).Path
$targetsSourcePath = (Resolve-Path -LiteralPath $DataTargetsTsv).Path
$collectorPath = (Resolve-Path -LiteralPath $Collector).Path
$wrapperSourcePath = if ([string]::IsNullOrWhiteSpace($PSCommandPath)) {
    throw 'The data-write wrapper must run from a saved script file.'
} else {
    (Resolve-Path -LiteralPath $PSCommandPath).Path
}
foreach ($required in @(
    $tracePath, $targetPath, $targetsSourcePath, $collectorPath,
    $wrapperSourcePath
)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required file was not found: $required"
    }
}
if ([System.IO.Path]::GetFileName($targetPath) -ine $ModuleName) {
    throw "Target filename must match -ModuleName ($ModuleName): $targetPath"
}

$outputRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-PathIsUnder $outputRoot (Split-Path -Parent $tracePath)) {
    throw 'Refusing to place data-write output inside the immutable trace directory.'
}
if (Test-Path -LiteralPath $outputRoot) {
    if (-not (Test-Path -LiteralPath $outputRoot -PathType Container) -or
        (Get-ChildItem -LiteralPath $outputRoot -Force | Select-Object -First 1)) {
        throw "Refusing to overwrite non-empty or non-directory output: $outputRoot"
    }
} else {
    [System.IO.Directory]::CreateDirectory($outputRoot) | Out-Null
}

$dataPath = Join-Path $outputRoot 'data-writes.jsonl'
$receiptPath = Join-Path $outputRoot 'receipt.json'
$manifestPath = Join-Path $outputRoot 'manifest.json'
$readyPath = Join-Path $outputRoot 'READY'
$targetsSnapshotPath = Join-Path $outputRoot 'targets.tsv'
$buildReceiptCopyPath = Join-Path $outputRoot 'collector-build-receipt.json'
$toolSnapshotDirectory = Join-Path $outputRoot 'collector-tool'
$sourceSnapshotDirectory = Join-Path $outputRoot 'instrument-source'
$wrapperSnapshotPath = Join-Path $sourceSnapshotDirectory 'Invoke-TtdDataWrites.ps1'
$collectorCppSnapshotPath = Join-Path $sourceSnapshotDirectory 'ttd_exec_coverage.cpp'
$collectorProjectSnapshotPath = Join-Path $sourceSnapshotDirectory 'ttd_exec_coverage.vcxproj'
$collectorDirectory = Split-Path -Parent $collectorPath
$replayPath = Join-Path $collectorDirectory 'TTDReplay.dll'
$replayCpuPath = Join-Path $collectorDirectory 'TTDReplayCPU.dll'
$buildReceiptPath = Join-Path (Split-Path -Parent $collectorDirectory) 'build-receipt.json'
foreach ($dependency in @($replayPath, $replayCpuPath, $buildReceiptPath)) {
    if (-not (Test-Path -LiteralPath $dependency -PathType Leaf)) {
        throw "Collector dependency was not found: $dependency"
    }
}

$buildReceipt = Get-Content -Raw -LiteralPath $buildReceiptPath | ConvertFrom-Json -Depth 30
$repro = $buildReceipt.reproducibility
$reproBuilds = @($repro.isolatedBuilds)
if ([string]$buildReceipt.schemaVersion -cne 'bea-ttd-exec-coverage-build.v2' -or
    $reproBuilds.Count -ne 2 -or $repro.buildCount -ne 2 -or
    $repro.byteIdentical -ne $true -or $repro.distinctOutputRoots -ne $true -or
    $repro.allSelfTestsPassed -ne $true -or
    [string]$repro.pdbAlternatePath -cne 'ttd_exec_coverage.pdb' -or
    [string]$reproBuilds[0].root -ceq [string]$reproBuilds[1].root) {
    throw 'Collector build receipt does not close its two-build gate.'
}
$buildInputs = @($buildReceipt.inputs)
if ($buildInputs.Count -ne 2) {
    throw 'Collector build receipt must bind exactly two source inputs.'
}
$cppInput = @($buildInputs | Where-Object {
    [System.IO.Path]::GetFileName([string]$_.path) -ceq 'ttd_exec_coverage.cpp'
})
$projectInput = @($buildInputs | Where-Object {
    [System.IO.Path]::GetFileName([string]$_.path) -ceq 'ttd_exec_coverage.vcxproj'
})
if ($cppInput.Count -ne 1 -or $projectInput.Count -ne 1) {
    throw 'Collector build receipt source-input identities are unexpected.'
}
$collectorCppSourcePath = (Resolve-Path -LiteralPath ([string]$cppInput[0].path)).Path
$collectorProjectSourcePath =
    (Resolve-Path -LiteralPath ([string]$projectInput[0].path)).Path

$collectorSourceFacts = Get-FileFacts $collectorPath
$replaySourceFacts = Get-FileFacts $replayPath
$replayCpuSourceFacts = Get-FileFacts $replayCpuPath
$buildReceiptSourceFacts = Get-FileFacts $buildReceiptPath
$wrapperSourceFacts = Get-FileFacts $wrapperSourcePath
$collectorCppSourceFacts = Get-FileFacts $collectorCppSourcePath
$collectorProjectSourceFacts = Get-FileFacts $collectorProjectSourcePath
if ([string]$buildReceipt.collector.sha256 -cne $collectorSourceFacts.sha256 -or
    [string]$buildReceipt.runtime.replaySha256 -cne $replaySourceFacts.sha256 -or
    [string]$buildReceipt.runtime.replayCpuSha256 -cne $replayCpuSourceFacts.sha256 -or
    [string]$cppInput[0].sha256 -cne $collectorCppSourceFacts.sha256 -or
    [string]$projectInput[0].sha256 -cne $collectorProjectSourceFacts.sha256) {
    throw 'Collector or replay runtime hash disagrees with the build receipt.'
}
foreach ($build in $reproBuilds) {
    if ([string]$build.sha256 -cne $collectorSourceFacts.sha256 -or
        [string]$build.selfTest -cne 'PASS') {
        throw 'An isolated collector build disagrees with the published collector.'
    }
}

[System.IO.Directory]::CreateDirectory($toolSnapshotDirectory) | Out-Null
[System.IO.Directory]::CreateDirectory($sourceSnapshotDirectory) | Out-Null
$snapshotCollectorPath = Join-Path $toolSnapshotDirectory 'ttd_exec_coverage.exe'
$snapshotReplayPath = Join-Path $toolSnapshotDirectory 'TTDReplay.dll'
$snapshotReplayCpuPath = Join-Path $toolSnapshotDirectory 'TTDReplayCPU.dll'
[System.IO.File]::Copy($collectorPath, $snapshotCollectorPath, $false)
[System.IO.File]::Copy($replayPath, $snapshotReplayPath, $false)
[System.IO.File]::Copy($replayCpuPath, $snapshotReplayCpuPath, $false)
[System.IO.File]::Copy($buildReceiptPath, $buildReceiptCopyPath, $false)
[System.IO.File]::Copy($targetsSourcePath, $targetsSnapshotPath, $false)
[System.IO.File]::Copy($wrapperSourcePath, $wrapperSnapshotPath, $false)
[System.IO.File]::Copy($collectorCppSourcePath, $collectorCppSnapshotPath, $false)
[System.IO.File]::Copy(
    $collectorProjectSourcePath, $collectorProjectSnapshotPath, $false)

$collectorFacts = Get-FileFacts $snapshotCollectorPath
$replayFacts = Get-FileFacts $snapshotReplayPath
$replayCpuFacts = Get-FileFacts $snapshotReplayCpuPath
$buildReceiptFacts = Get-FileFacts $buildReceiptCopyPath
$targetsSourceFacts = Get-FileFacts $targetsSourcePath
$targetsFacts = Get-FileFacts $targetsSnapshotPath
$wrapperFacts = Get-FileFacts $wrapperSnapshotPath
$collectorCppFacts = Get-FileFacts $collectorCppSnapshotPath
$collectorProjectFacts = Get-FileFacts $collectorProjectSnapshotPath
if ($collectorFacts.sha256 -cne $collectorSourceFacts.sha256 -or
    $replayFacts.sha256 -cne $replaySourceFacts.sha256 -or
    $replayCpuFacts.sha256 -cne $replayCpuSourceFacts.sha256 -or
    $buildReceiptFacts.sha256 -cne $buildReceiptSourceFacts.sha256 -or
    $targetsFacts.sha256 -cne $targetsSourceFacts.sha256 -or
    $wrapperFacts.sha256 -cne $wrapperSourceFacts.sha256 -or
    $collectorCppFacts.sha256 -cne $collectorCppSourceFacts.sha256 -or
    $collectorProjectFacts.sha256 -cne $collectorProjectSourceFacts.sha256) {
    throw 'Private data-write snapshot disagrees with its validated source.'
}
$frozenTargetRows = Read-DataWriteTargetTable $targetsSnapshotPath

$traceBefore = Get-FileFacts $tracePath
$targetBefore = Get-FileFacts $targetPath
$targetPe = Get-PeIdentity $targetPath
$effectiveBase = if ([string]::IsNullOrWhiteSpace($ExpectedBase)) {
    $targetPe.imageBase
} else { $ExpectedBase }

$arguments = @(
    '--mode', 'data-writes', '--trace', $tracePath, '--module', $ModuleName,
    '--out', $dataPath, '--data-targets-tsv', $targetsSnapshotPath,
    '--expect-base', $effectiveBase, '--expect-size', $targetPe.sizeOfImage,
    '--expect-timestamp', $targetPe.timestamp, '--expect-checksum', $targetPe.checksum,
    '--max-module-bytes', $targetPe.sizeOfImage, '--from', $canonicalFrom,
    '--to', $canonicalTo, '--event-limit', [string]$EventLimit
)
$startedAt = (Get-Date).ToUniversalTime()
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
& $snapshotCollectorPath @arguments
$collectorExitCode = $LASTEXITCODE
$stopwatch.Stop()
$finishedAt = (Get-Date).ToUniversalTime()

Assert-FactsUnchanged $traceBefore (Get-FileFacts $tracePath) 'Trace'
Assert-FactsUnchanged $targetBefore (Get-FileFacts $targetPath) 'Target executable'
Assert-FactsUnchanged $targetsSourceFacts (Get-FileFacts $targetsSourcePath) 'Target table source'
Assert-FactsUnchanged $collectorFacts (Get-FileFacts $snapshotCollectorPath) 'Private collector'
Assert-FactsUnchanged $replayFacts (Get-FileFacts $snapshotReplayPath) 'Private TTDReplay'
Assert-FactsUnchanged $replayCpuFacts (Get-FileFacts $snapshotReplayCpuPath) 'Private TTDReplayCPU'
Assert-FactsUnchanged $buildReceiptFacts (Get-FileFacts $buildReceiptCopyPath) 'Private build receipt'
Assert-FactsUnchanged $targetsFacts (Get-FileFacts $targetsSnapshotPath) 'Private target table'
Assert-FactsUnchanged $wrapperSourceFacts (Get-FileFacts $wrapperSourcePath) 'Wrapper source'
Assert-FactsUnchanged $wrapperFacts (Get-FileFacts $wrapperSnapshotPath) 'Private wrapper source'
Assert-FactsUnchanged $collectorCppSourceFacts (Get-FileFacts $collectorCppSourcePath) 'Collector C++ source'
Assert-FactsUnchanged $collectorCppFacts (Get-FileFacts $collectorCppSnapshotPath) 'Private collector C++ source'
Assert-FactsUnchanged $collectorProjectSourceFacts (Get-FileFacts $collectorProjectSourcePath) 'Collector project source'
Assert-FactsUnchanged $collectorProjectFacts (Get-FileFacts $collectorProjectSnapshotPath) 'Private collector project source'

$instrumentSourceFacts = [ordered]@{
    wrapper = $wrapperFacts
    collectorCpp = $collectorCppFacts
    collectorProject = $collectorProjectFacts
}

if (-not (Test-Path -LiteralPath $dataPath -PathType Leaf)) {
    $effectiveExitCode = Resolve-MissingDataWriteExitCode $collectorExitCode
    $failure = [ordered]@{
        phase = 'post-collector-output-check'
        code = 'data-write-jsonl-missing'
        message = "Collector exited $collectorExitCode without producing data-writes.jsonl."
    }
    $blockedReceipt = [ordered]@{
        schemaVersion = 'bea-ttd-data-writes-receipt.v3'
        generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        startedAtUtc = $startedAt.ToString('o')
        finishedAtUtc = $finishedAt.ToString('o')
        elapsedSeconds = $stopwatch.Elapsed.TotalSeconds
        collectorExitCode = $collectorExitCode
        exitCode = $effectiveExitCode
        readyEligible = $false
        trace = $traceBefore
        target = [ordered]@{ path=$targetBefore.path; bytes=$targetBefore.bytes; sha256=$targetBefore.sha256; lastWriteUtc=$targetBefore.lastWriteUtc; pe=$targetPe }
        targetsSource = $targetsSourceFacts
        targetsSnapshot = $targetsFacts
        collector = $collectorFacts
        replayRuntime = [ordered]@{ version=[string]$buildReceipt.runtime.version; replay=$replayFacts; replayCpu=$replayCpuFacts }
        buildReceipt = $buildReceiptFacts
        instrumentSource = $instrumentSourceFacts
        invocation = [ordered]@{ moduleName=$ModuleName; expectedBase=$effectiveBase; from=$canonicalFrom; to=$canonicalTo; eventLimit=$EventLimit; replayMode='sequential-all-segments' }
        dataWrites = $null
        metadata = $null
        gapSummary = $null
        summary = $null
        failure = $failure
    }
    [System.IO.File]::WriteAllText($receiptPath, ($blockedReceipt | ConvertTo-Json -Depth 35) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    $receiptFacts = Get-FileFacts $receiptPath
    $blockedManifest = [ordered]@{
        schemaVersion='bea-ttd-data-writes-manifest.v3'; generatedAtUtc=(Get-Date).ToUniversalTime().ToString('o'); status='BLOCKED'; collectorExitCode=$collectorExitCode; exitCode=$effectiveExitCode
        specimen=[ordered]@{ traceSha256=$traceBefore.sha256; targetSha256=$targetBefore.sha256; targetsSha256=$targetsFacts.sha256; moduleName=$ModuleName; expectedBase=$effectiveBase; sizeOfImage=$targetPe.sizeOfImage; timestamp=$targetPe.timestamp; checksum=$targetPe.checksum }
        artifacts=[ordered]@{ dataWrites=$null; receipt=$receiptFacts; targets=$targetsFacts; collector=$collectorFacts; replay=$replayFacts; replayCpu=$replayCpuFacts; buildReceipt=$buildReceiptFacts; instrumentSource=$instrumentSourceFacts }
        proof=$null; failure=$failure
    }
    [System.IO.File]::WriteAllText($manifestPath, ($blockedManifest | ConvertTo-Json -Depth 30) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    $blockedReceipt
    exit $effectiveExitCode
}

$metadata = $null
$gapSummary = $null
$summary = $null
$targets = [System.Collections.Generic.List[object]]::new()
$events = [System.Collections.Generic.List[object]]::new()
$pairs = [System.Collections.Generic.List[object]]::new()
$continuityBreakRows = [System.Collections.Generic.List[object]]::new()
$lineCount = 0
$phase = 0
foreach ($line in [System.IO.File]::ReadLines($dataPath)) {
    $lineCount++
    $row = $line | ConvertFrom-Json -Depth 40
    if ([string]$row.schema -cne 'bea.ttd.data-writes.v3') {
        throw "Unexpected data-write schema on line $lineCount."
    }
    switch ([string]$row.kind) {
        'metadata' {
            if ($phase -ne 0 -or $null -ne $metadata) { throw 'Data-write metadata is duplicated or out of order.' }
            $metadata = $row; $phase = 1
        }
        'target' {
            if ($phase -lt 1 -or $phase -gt 1) { throw 'Data-write target row is out of order.' }
            $targets.Add($row)
        }
        'event' {
            if ($phase -lt 1 -or $phase -gt 2) { throw 'Data-write event row is out of order.' }
            $phase = 2; $events.Add($row)
        }
        'pair' {
            if ($phase -lt 1 -or $phase -gt 3) { throw 'Data-write pair row is out of order.' }
            $phase = 3; $pairs.Add($row)
        }
        'continuity-break' {
            if ($phase -lt 1 -or $phase -gt 3) { throw 'Data-write continuity-break row is out of order.' }
            if ((Get-RequiredUInt64 $row 'ordinal' 'continuity-break row') -ne
                $continuityBreakRows.Count) {
                throw 'Data-write continuity-break ordinals are not contiguous.'
            }
            $phase = 3; $continuityBreakRows.Add($row)
        }
        'gap-summary' {
            if ($phase -gt 3 -or $null -ne $gapSummary) { throw 'Data-write gap summary is duplicated or out of order.' }
            $phase = 4; $gapSummary = $row
        }
        'summary' {
            if ($phase -ne 4 -or $null -ne $summary) { throw 'Data-write summary is duplicated or out of order.' }
            $phase = 5; $summary = $row
        }
        default { throw "Unexpected data-write row kind on line $lineCount`: $($row.kind)" }
    }
}
if ($phase -ne 5 -or $null -eq $metadata -or $null -eq $gapSummary -or
    $null -eq $summary -or $targets.Count -eq 0) {
    throw 'Data-write JSONL is incomplete.'
}
if ((Get-RequiredUInt64 $summary 'target_count' 'summary') -ne $targets.Count) {
    throw 'Data-write target count disagrees with the summary.'
}

$canonicalBase = ('0x{0:X}' -f (Convert-HexUInt64 $effectiveBase 'expected base'))
$canonicalSize = ('0x{0:X}' -f (Convert-HexUInt64 $targetPe.sizeOfImage 'image size'))
$canonicalTimestamp = ('0x{0:X}' -f (Convert-HexUInt64 $targetPe.timestamp 'timestamp'))
$canonicalChecksum = ('0x{0:X}' -f (Convert-HexUInt64 $targetPe.checksum 'checksum'))
if ([string]$metadata.processor_architecture -cne 'x86' -or
    [string]$metadata.replay_mode -cne 'sequential-all-segments' -or
    [string]$metadata.raw_value_policy -cne 'untyped-registers-and-bytes' -or
    [string]$metadata.pairing_policy -cne 'exact-same-boundary-structural-candidate' -or
    [string]$metadata.promotion_policy -cne 'bea.ttd.data-writes.exact-window-watchpoint-chain.v1' -or
    [string]$metadata.window_semantics -cne 'state-at-from-transitions-in-open-closed-window' -or
    [string]$metadata.trace_bytes -cne [string]$traceBefore.bytes -or
    [string]$metadata.requested_from -cne $canonicalFrom -or
    [string]$metadata.requested_to -cne $canonicalTo -or
    [string]$metadata.actual_from -cne $canonicalFrom -or
    [System.IO.Path]::GetFileName([string]$metadata.module_name) -ine $ModuleName -or
    [string]$metadata.module_base -cne $canonicalBase -or
    [string]$metadata.module_size -cne $canonicalSize -or
    [string]$metadata.module_timestamp -cne $canonicalTimestamp -or
    [string]$metadata.module_checksum -cne $canonicalChecksum) {
    throw 'Data-write metadata disagrees with the trace, window, mode, or PE identity.'
}
if ([System.IO.Path]::GetFullPath([string]$metadata.trace) -ine $tracePath -or
    [System.IO.Path]::GetFullPath([string]$metadata.targets_tsv) -ine $targetsSnapshotPath) {
    throw 'Data-write metadata paths do not identify the snapshotted inputs.'
}

$finalPosition = Assert-TtdPosition $summary 'final_position' 'summary'
$relationships = Assert-DataWriteRelationships `
    -Targets @($targets) -Events @($events) -Pairs @($pairs) -Summary $summary `
    -ActualFrom ([string]$metadata.actual_from) -FinalPosition $finalPosition `
    -AllowInvalidEndpoints -AllowInvalidEventMemory
$expectationsFromTable = Assert-TargetTableMatchesRows $frozenTargetRows @($targets)
$gapAccounting = Assert-DataWriteGapAccounting `
    $gapSummary $summary @($events) @($continuityBreakRows) $relationships
$replayComplete = Get-RequiredBoolean $summary 'replay_complete' 'summary'
$expectationsPassed = Get-RequiredBoolean $summary 'expectations_passed' 'summary'
$countersSane = Get-RequiredBoolean $summary 'replay_counters_sane' 'summary'
$instructionsExecuted = Get-RequiredUInt64 $summary 'instructions_executed' 'summary'
$stepsExecuted = Get-RequiredUInt64 $summary 'steps_executed' 'summary'
$truncated = Get-RequiredBoolean $summary 'truncated' 'summary'
$callbackFailed = Get-RequiredBoolean $summary 'callback_failed' 'summary'
$orderingValid = Get-RequiredBoolean $summary 'ordering_valid' 'summary'
$contextsValid = Get-RequiredBoolean $summary 'contexts_valid' 'summary'
$pairingValid = Get-RequiredBoolean $summary 'pairing_valid' 'summary'
$snapshotQueriesValid = Get-RequiredBoolean $summary 'snapshot_queries_valid' 'summary'
$targetEvidencePassed = Get-RequiredBoolean $summary 'target_evidence_passed' 'summary'
$exactReplayWindow = Get-RequiredBoolean $summary 'exact_replay_window' 'summary'
$collectorChecksPassed = Get-RequiredBoolean $summary 'collector_checks_passed' 'summary'
$ambiguousCallbacks = Get-RequiredUInt64 $summary 'ambiguous_callbacks' 'summary'
$nontrivialGapCount = Get-RequiredUInt64 $summary 'nontrivial_gap_count' 'summary'
$continuityBreakCount = Get-RequiredUInt64 $summary 'continuity_break_count' 'summary'
$computedReplayComplete = [string]$summary.stop_reason -ceq 'Position' -and
    $finalPosition -ceq $canonicalTo
$computedCountersSane = $stepsExecuted -gt 0 -and
    $instructionsExecuted -le $stepsExecuted
$computedExactReplayWindow = [string]$metadata.actual_from -ceq $canonicalFrom -and
    $finalPosition -ceq $canonicalTo
if ($snapshotQueriesValid -ne [bool]$relationships.endpointQueriesValid -or
    $targetEvidencePassed -ne [bool]$relationships.targetEvidencePassed -or
    $expectationsPassed -ne [bool]$expectationsFromTable -or
    $replayComplete -ne $computedReplayComplete -or
    $countersSane -ne $computedCountersSane -or
    $contextsValid -ne ([bool]$relationships.eventMemoryValid -and $ambiguousCallbacks -eq 0) -or
    $exactReplayWindow -ne $computedExactReplayWindow) {
    throw 'Data-write summary disagrees with independently reconstructed proof state.'
}
$computedCollectorChecks =
    $replayComplete -and $exactReplayWindow -and $expectationsPassed -and $countersSane -and
    -not $truncated -and -not $callbackFailed -and $orderingValid -and
    $contextsValid -and $pairingValid -and $relationships.pairingComplete -and
    $targetEvidencePassed -and
    $ambiguousCallbacks -eq 0 -and $nontrivialGapCount -eq 0 -and
    $continuityBreakCount -eq 0 -and $relationships.allEventEpochsZero -and
    $gapAccounting.reconciled
if ($collectorChecksPassed -ne $computedCollectorChecks) {
    throw 'Native collector-check result disagrees with the wrapper reconstruction.'
}
# READY / READY_GAP_FREE: exact-window gap-free only (collector exit 0).
$readyEligible = $collectorExitCode -eq 0 -and $computedCollectorChecks
if (($collectorExitCode -eq 0) -ne $readyEligible) {
    throw 'Collector exit code and parsed data-write readiness disagree.'
}
$gapFreePromotionPolicy = Get-DataWritesGapFreePromotionPolicy
$witnessedPromotionPolicy = Get-DataWritesWitnessedPromotionPolicy
if ($readyEligible -and [string]$metadata.promotion_policy -cne $gapFreePromotionPolicy) {
    throw 'Gap-free READY requires the exact-window promotion policy identity.'
}

$parsedWriterBodyRanges = Parse-WriterBodyRanges -Ranges $WriterBodyRanges
$witnessedGrade = Assert-DataWriteWitnessedWrites `
    -Events @($events) -Pairs @($pairs) -Summary $summary `
    -GapAccounting $gapAccounting -Relationships $relationships `
    -ReplayComplete $replayComplete -ExactReplayWindow $exactReplayWindow `
    -ExpectationsPassed $expectationsPassed -CountersSane $countersSane `
    -OrderingValid $orderingValid -ContextsValid $contextsValid `
    -PairingValid $pairingValid -SnapshotQueriesValid $snapshotQueriesValid `
    -AmbiguousCallbacks $ambiguousCallbacks `
    -NontrivialGapCount $nontrivialGapCount `
    -ContinuityBreakCount $continuityBreakCount `
    -WriterBodyRanges $parsedWriterBodyRanges
$witnessedWritesEligible = [bool]$witnessedGrade.eligible
# Never promote gap-free READY from the witnessed grade alone.
if ($readyEligible -and -not $computedCollectorChecks) {
    throw 'Internal error: gap-free READY without gap-free collector checks.'
}
if ($readyEligible -and ($nontrivialGapCount -ne 0 -or $continuityBreakCount -ne 0)) {
    throw 'Internal error: gap-free READY with nonzero gap/continuity counts.'
}

$dataFacts = Get-FileFacts $dataPath
$readyWitnessedPath = Join-Path $outputRoot 'READY_WITNESSED_WRITES'
$receipt = [ordered]@{
    schemaVersion='bea-ttd-data-writes-receipt.v3'; generatedAtUtc=(Get-Date).ToUniversalTime().ToString('o'); startedAtUtc=$startedAt.ToString('o'); finishedAtUtc=$finishedAt.ToString('o'); elapsedSeconds=$stopwatch.Elapsed.TotalSeconds
    collectorExitCode=$collectorExitCode; exitCode=$collectorExitCode
    readyEligible=$readyEligible
    readyGapFreeEligible=$readyEligible
    witnessedWritesEligible=$witnessedWritesEligible
    trace=$traceBefore
    target=[ordered]@{ path=$targetBefore.path; bytes=$targetBefore.bytes; sha256=$targetBefore.sha256; lastWriteUtc=$targetBefore.lastWriteUtc; pe=$targetPe }
    targetsSource=$targetsSourceFacts; targetsSnapshot=$targetsFacts; collector=$collectorFacts
    replayRuntime=[ordered]@{ version=[string]$buildReceipt.runtime.version; replay=$replayFacts; replayCpu=$replayCpuFacts }
    buildReceipt=$buildReceiptFacts
    instrumentSource=$instrumentSourceFacts
    invocation=[ordered]@{ moduleName=$ModuleName; expectedBase=$effectiveBase; from=$canonicalFrom; to=$canonicalTo; eventLimit=$EventLimit; replayMode='sequential-all-segments'; writerBodyRanges=@($parsedWriterBodyRanges | ForEach-Object { $_.text }) }
    dataWrites=[ordered]@{ path=$dataFacts.path; bytes=$dataFacts.bytes; sha256=$dataFacts.sha256; schemaVersion='bea.ttd.data-writes.v3'; lineCount=$lineCount; targetCount=$targets.Count; eventCount=$events.Count; pairCount=$pairs.Count; orphanEventCount=$relationships.orphanEventCount }
    promotionPolicy=[string]$metadata.promotion_policy
    gapFreePromotionPolicy=$gapFreePromotionPolicy
    witnessedPromotionPolicy=$witnessedPromotionPolicy
    witnessedGrade=$witnessedGrade
    metadata=$metadata; gapSummary=$gapSummary; gapAccounting=$gapAccounting; summary=$summary; relationships=$relationships
}
[System.IO.File]::WriteAllText($receiptPath, ($receipt | ConvertTo-Json -Depth 35) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
$receiptFacts = Get-FileFacts $receiptPath
$manifestStatus = if ($readyEligible) {
    'READY'
} elseif ($witnessedWritesEligible) {
    'READY_WITNESSED_WRITES'
} else {
    'BLOCKED'
}
$manifest = [ordered]@{
    schemaVersion='bea-ttd-data-writes-manifest.v3'; generatedAtUtc=(Get-Date).ToUniversalTime().ToString('o'); status=$manifestStatus; collectorExitCode=$collectorExitCode; exitCode=$collectorExitCode
    specimen=[ordered]@{ traceSha256=$traceBefore.sha256; targetSha256=$targetBefore.sha256; targetsSha256=$targetsFacts.sha256; moduleName=$ModuleName; expectedBase=$effectiveBase; sizeOfImage=$targetPe.sizeOfImage; timestamp=$targetPe.timestamp; checksum=$targetPe.checksum }
    artifacts=[ordered]@{ dataWrites=$dataFacts; receipt=$receiptFacts; targets=$targetsFacts; collector=$collectorFacts; replay=$replayFacts; replayCpu=$replayCpuFacts; buildReceipt=$buildReceiptFacts; instrumentSource=$instrumentSourceFacts }
    proof=[ordered]@{
        promotionPolicy=[string]$metadata.promotion_policy
        gapFreePromotionPolicy=$gapFreePromotionPolicy
        witnessedPromotionPolicy=$witnessedPromotionPolicy
        readyGapFreeEligible=$readyEligible
        witnessedWritesEligible=$witnessedWritesEligible
        witnessedGrade=$witnessedGrade
        replayComplete=$replayComplete; exactReplayWindow=$exactReplayWindow; expectationsPassed=$expectationsPassed; replayCountersSane=$countersSane; orderingValid=$orderingValid; contextsValid=$contextsValid; pairingValid=$pairingValid; pairingComplete=$relationships.pairingComplete; snapshotQueriesValid=$snapshotQueriesValid; targetEvidencePassed=$targetEvidencePassed; ambiguousCallbacks=$ambiguousCallbacks; nontrivialGapCount=$nontrivialGapCount; continuityBreakCount=$continuityBreakCount; allEventEpochsZero=$relationships.allEventEpochsZero; truncated=$truncated; callbackFailed=$callbackFailed; collectorChecksPassed=$collectorChecksPassed; gapAccounting=$gapAccounting; counts=$relationships
    }
}
[System.IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 30) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
$manifestFacts = Get-FileFacts $manifestPath
if ($readyEligible) {
    $ready = [ordered]@{ schemaVersion='bea-ttd-data-writes-ready.v3'; promotionPolicy=[string]$metadata.promotion_policy; grade='READY_GAP_FREE'; manifest=$manifestFacts; receiptSha256=$receiptFacts.sha256; dataWritesSha256=$dataFacts.sha256; wrapperSha256=$wrapperFacts.sha256; collectorCppSha256=$collectorCppFacts.sha256; collectorProjectSha256=$collectorProjectFacts.sha256 }
    [System.IO.File]::WriteAllText($readyPath, ($ready | ConvertTo-Json -Depth 10) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    $manifestReadback = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json -Depth 30
    if ([string]$manifestReadback.status -cne 'READY' -or
        (Get-FileFacts $manifestPath).sha256 -cne $manifestFacts.sha256 -or
        (Get-FileFacts $receiptPath).sha256 -cne $receiptFacts.sha256 -or
        (Get-FileFacts $dataPath).sha256 -cne $dataFacts.sha256 -or
        (Get-FileFacts $wrapperSnapshotPath).sha256 -cne $wrapperFacts.sha256 -or
        (Get-FileFacts $collectorCppSnapshotPath).sha256 -cne $collectorCppFacts.sha256 -or
        (Get-FileFacts $collectorProjectSnapshotPath).sha256 -cne $collectorProjectFacts.sha256) {
        throw 'READY readback failed to reproduce the manifest-bound artifacts.'
    }
}
if ($witnessedWritesEligible) {
    $readyWitnessed = [ordered]@{
        schemaVersion='bea-ttd-data-writes-ready-witnessed.v1'
        promotionPolicy=$witnessedPromotionPolicy
        grade='READY_WITNESSED_WRITES'
        alsoGapFree=$readyEligible
        nontrivialGapCount=$nontrivialGapCount
        continuityBreakCount=$continuityBreakCount
        writerBodyRanges=@($parsedWriterBodyRanges | ForEach-Object { $_.text })
        manifest=$manifestFacts
        receiptSha256=$receiptFacts.sha256
        dataWritesSha256=$dataFacts.sha256
        wrapperSha256=$wrapperFacts.sha256
        collectorCppSha256=$collectorCppFacts.sha256
        collectorProjectSha256=$collectorProjectFacts.sha256
        witnessedGrade=$witnessedGrade
    }
    [System.IO.File]::WriteAllText(
        $readyWitnessedPath,
        ($readyWitnessed | ConvertTo-Json -Depth 20) + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false))
    $witnessedReadback = Get-Content -Raw -LiteralPath $readyWitnessedPath | ConvertFrom-Json -Depth 20
    if ([string]$witnessedReadback.grade -cne 'READY_WITNESSED_WRITES' -or
        [string]$witnessedReadback.promotionPolicy -cne $witnessedPromotionPolicy -or
        (Get-FileFacts $readyWitnessedPath).sha256 -ceq '') {
        throw 'READY_WITNESSED_WRITES readback failed.'
    }
} elseif (Test-Path -LiteralPath $readyWitnessedPath) {
    Remove-Item -LiteralPath $readyWitnessedPath -Force
}
$receipt
if ($collectorExitCode -ne 0) { exit $collectorExitCode }
