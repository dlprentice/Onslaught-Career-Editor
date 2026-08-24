[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$TraceFile,

    [Parameter(Mandatory = $true)]
    [string]$TargetExe,

    [Parameter(Mandatory = $true)]
    [string]$TargetsTsv,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [string]$Collector = (Join-Path $PSScriptRoot '..\build\ttd-exec-coverage\bin\ttd_exec_coverage.exe'),
    [string]$ModuleName = 'BEA.exe',
    [string]$ExpectedBase = '',
    [string]$From = '',
    [string]$To = '',

    [ValidateRange(1, 256)]
    [int]$StackBytes = 64,

    [ValidateRange(1, 1000000)]
    [int]$EventLimit = 100000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Versioned successor to the historically pinned wrapper. Long TTD replays can
# stop advancing the diagnostic instruction counters while callback delivery
# continues; the boundary guard therefore caps callbacks by replay capacity.

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
        if ($optionalBytes -lt 68 -or
            $optionalOffset + $optionalBytes -gt $stream.Length) {
            throw "Invalid optional-header size in $Path"
        }
        $stream.Position = $optionalOffset
        $magic = $reader.ReadUInt16()
        if ($machine -ne 0x14C -or $magic -ne 0x10B) {
            throw "TTD call-context requires a PE32/x86 target: $Path"
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

function Resolve-MissingCallContextExitCode {
    param([Parameter(Mandatory = $true)][int]$CollectorExitCode)

    if ($CollectorExitCode -ne 0) {
        return $CollectorExitCode
    }
    return 12
}

function Assert-FactsUnchanged {
    param(
        [Parameter(Mandatory = $true)]$Before,
        [Parameter(Mandatory = $true)]$After,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($Before.bytes -ne $After.bytes -or
        [string]$Before.sha256 -cne [string]$After.sha256 -or
        [string]$Before.lastWriteUtc -cne [string]$After.lastWriteUtc) {
        throw "$Label changed during TTD replay."
    }
}

function Test-PathIsUnder {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Ancestor
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    $fullAncestor = [System.IO.Path]::GetFullPath($Ancestor).TrimEnd('\')
    return $fullPath.StartsWith(
        $fullAncestor + '\',
        [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-RequiredProperty {
    param(
        [Parameter(Mandatory = $true)]$Owner,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $property = $Owner.PSObject.Properties[$Name]
    if ($null -eq $property) {
        throw "$Label is missing $Name."
    }
    return $property.Value
}

function Get-RequiredScalarProperty {
    param(
        [Parameter(Mandatory = $true)]$Owner,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $property = $Owner.PSObject.Properties[$Name]
    if ($null -eq $property) {
        throw "$Label is missing $Name."
    }
    if ($property.Value -is [System.Array]) {
        throw "$Label field $Name must be one scalar JSON value, not an array."
    }
    return $property.Value
}

function Get-RequiredObject {
    param(
        [Parameter(Mandatory = $true)]$Owner,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($null -eq $value -or $value -isnot [pscustomobject]) {
        throw "$Label field $Name must be one JSON object."
    }
    return $value
}

function Get-RequiredArray {
    param(
        [Parameter(Mandatory = $true)]$Owner,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $property = $Owner.PSObject.Properties[$Name]
    if ($null -eq $property) {
        throw "$Label is missing $Name."
    }
    if ($property.Value -isnot [System.Array]) {
        throw "$Label field $Name must be one JSON array."
    }
    return $property.Value
}

function Get-RequiredBoolean {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -isnot [bool]) {
        throw "$Label field $Name must be a JSON boolean."
    }
    return [bool]$value
}

function Get-RequiredString {
    param($Owner, [string]$Name, [string]$Label, [switch]$AllowEmpty)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -isnot [string] -or
        (-not $AllowEmpty -and [string]::IsNullOrEmpty($value))) {
        throw "$Label field $Name must be one JSON string."
    }
    return $value
}

function Get-RequiredUInt64 {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -is [long]) {
        if ($value -lt 0) {
            throw "$Label field $Name must be an unsigned decimal integer."
        }
        return [uint64]$value
    }
    if ($value -isnot [string] -or $value -notmatch '^[0-9]+$') {
        throw "$Label field $Name must be an unsigned decimal integer."
    }
    return [uint64]::Parse($value)
}

function Get-RequiredIndex {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -isnot [long] -or $value -lt 0 -or $value -gt [int]::MaxValue) {
        throw "$Label field $Name must be one scalar non-negative Int32 JSON number."
    }
    return [int]$value
}

function Get-RequiredUInt32TextScalar {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -isnot [string] -or $value -notmatch '^[0-9]+$') {
        throw "$Label field $Name must be one unsigned decimal JSON string."
    }
    $parsed = [uint64]::Parse($value)
    if ($parsed -gt [uint32]::MaxValue) {
        throw "$Label field $Name exceeds UInt32 range."
    }
    return [uint64]$parsed
}

function Add-UInt64Checked {
    param(
        [Parameter(Mandatory = $true)][uint64]$Left,
        [Parameter(Mandatory = $true)][uint64]$Right,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($Right -gt ([uint64]::MaxValue - $Left)) {
        throw "$Label overflows UInt64."
    }
    return [uint64]($Left + $Right)
}

function Get-NullableIndex {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($null -eq $value) {
        return $null
    }
    if ($value -isnot [long] -or $value -lt 0 -or $value -gt [int]::MaxValue) {
        throw "$Label field $Name must be null or one scalar non-negative Int32 JSON number."
    }
    return [int]$value
}

function Get-NullableUInt64 {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($null -eq $value) {
        return $null
    }
    if ($value -is [long]) {
        if ($value -lt 0) {
            throw "$Label field $Name must be null or an unsigned decimal integer."
        }
        return [uint64]$value
    }
    if ($value -isnot [string] -or $value -notmatch '^[0-9]+$') {
        throw "$Label field $Name must be null or an unsigned decimal integer."
    }
    return [uint64]::Parse($value)
}

function Convert-UnsignedNumericText {
    param([Parameter(Mandatory = $true)][string]$Text, [string]$Label)

    if ($Text -match '^0[xX]([0-9A-Fa-f]+)$') {
        return [Convert]::ToUInt64($Matches[1], 16)
    }
    if ($Text -match '^[0-9]+$') {
        return [uint64]::Parse($Text)
    }
    throw "$Label must be an unsigned decimal or hexadecimal integer."
}

function Convert-ToCanonicalHex {
    param([Parameter(Mandatory = $true)][uint64]$Value)

    return '0x{0:X}' -f $Value
}

function Assert-HexText {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -isnot [string] -or $value -notmatch '^0x[0-9A-F]+$') {
        throw "$Label field $Name must be canonical uppercase hexadecimal."
    }
    return $value
}

function Assert-TtdPosition {
    param($Owner, [string]$Name, [string]$Label)

    $value = Get-RequiredScalarProperty -Owner $Owner -Name $Name -Label $Label
    if ($value -isnot [string] -or $value -notmatch '^0x[0-9A-F]+:0x[0-9A-F]+$') {
        throw "$Label field $Name must be a canonical TTD position."
    }
    return $value
}

function Convert-TtdPositionValue {
    param($Owner, [string]$Name, [string]$Label)

    $text = Assert-TtdPosition $Owner $Name $Label
    $parts = $text.Split(':')
    return [pscustomobject]@{
        sequence = [Convert]::ToUInt64($parts[0].Substring(2), 16)
        steps = [Convert]::ToUInt64($parts[1].Substring(2), 16)
    }
}

function Compare-TtdPositionValue {
    param($Left, $Right)

    if ($Left.sequence -lt $Right.sequence) { return -1 }
    if ($Left.sequence -gt $Right.sequence) { return 1 }
    if ($Left.steps -lt $Right.steps) { return -1 }
    if ($Left.steps -gt $Right.steps) { return 1 }
    return 0
}

function Read-CallContextTargetSpecifications {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][uint64]$ModuleBase
    )

    $expectedHeader = 'target_index' + "`t" + 'entry_rva' + "`t" +
        'range_start_rva' + "`t" + 'range_end_rva_exclusive' + "`t" +
        'expected_entry_count' + "`t" + 'expected_call_count' + "`t" +
        'expected_return_count'
    $lines = [System.IO.File]::ReadAllLines($Path)
    if ($lines.Count -lt 2 -or $lines[0] -cne $expectedHeader) {
        throw 'Call-context target snapshot has an unexpected header or no rows.'
    }
    $specifications = [System.Collections.Generic.List[object]]::new()
    for ($lineIndex = 1; $lineIndex -lt $lines.Count; $lineIndex++) {
        $fields = $lines[$lineIndex].Split("`t")
        if ($fields.Count -ne 7) {
            throw "Call-context target snapshot row $lineIndex has the wrong field count."
        }
        $targetIndex = Convert-UnsignedNumericText $fields[0] 'target_index'
        if ($targetIndex -gt [int]::MaxValue -or $targetIndex -gt $specifications.Count) {
            throw 'Call-context target snapshot indexes are not contiguous and grouped.'
        }
        $entryRva = Convert-UnsignedNumericText $fields[1] 'entry_rva'
        $rangeStart = Convert-UnsignedNumericText $fields[2] 'range_start_rva'
        $rangeEnd = Convert-UnsignedNumericText $fields[3] 'range_end_rva_exclusive'
        if ($rangeStart -ge $rangeEnd -or
            $entryRva -gt ([uint64]::MaxValue - $ModuleBase)) {
            throw 'Call-context target snapshot has an invalid range or entry VA.'
        }
        $expected = [object[]]::new(3)
        for ($fieldIndex = 4; $fieldIndex -le 6; $fieldIndex++) {
            $expected[$fieldIndex - 4] = if ($fields[$fieldIndex] -ceq '') {
                $null
            } else {
                Convert-UnsignedNumericText $fields[$fieldIndex] "expected count $fieldIndex"
            }
        }
        if ($targetIndex -eq $specifications.Count) {
            $specifications.Add([pscustomobject]@{
                target_index = [int]$targetIndex
                entry_rva = Convert-ToCanonicalHex $entryRva
                entry_va = Convert-ToCanonicalHex ($ModuleBase + $entryRva)
                expected_entry_count = $expected[0]
                expected_call_count = $expected[1]
                expected_return_count = $expected[2]
                ranges = [System.Collections.Generic.List[object]]::new()
            })
        }
        $specification = $specifications[[int]$targetIndex]
        if ([string]$specification.entry_rva -cne (Convert-ToCanonicalHex $entryRva) -or
            $specification.expected_entry_count -ne $expected[0] -or
            $specification.expected_call_count -ne $expected[1] -or
            $specification.expected_return_count -ne $expected[2]) {
            throw 'Repeated call-context target snapshot rows disagree.'
        }
        if ($specification.ranges.Count -gt 0) {
            $priorEnd = Convert-UnsignedNumericText `
                ([string]$specification.ranges[$specification.ranges.Count - 1].rva_end_exclusive) `
                'prior range end'
            if ($rangeStart -lt $priorEnd) {
                throw 'Call-context target snapshot ranges overlap or are unsorted.'
            }
        }
        $specification.ranges.Add([pscustomobject]@{
            rva_start = Convert-ToCanonicalHex $rangeStart
            rva_end_exclusive = Convert-ToCanonicalHex $rangeEnd
        })
    }
    return @($specifications)
}

function Get-EventStackReturnAddress {
    param($Event, [string]$Label, [switch]$RequirePairable)

    $stack = Get-RequiredObject $Event 'stack' $Label
    $address = Assert-HexText $stack 'address' "$Label stack"
    $sp = Assert-HexText $Event 'sp' $Label
    $addressValue = Convert-UnsignedNumericText $address "$Label stack address"
    $spValue = Convert-UnsignedNumericText $sp "$Label sp"
    $validBytes = Get-RequiredUInt64 $stack 'valid_bytes' "$Label stack"
    $queryValid = Get-RequiredBoolean $stack 'query_valid' "$Label stack"
    $hex = Get-RequiredString $stack 'hex' "$Label stack" -AllowEmpty
    if ($hex -notmatch '^(?:[0-9A-F]{2})*$' -or $hex.Length -ne $validBytes * 2) {
        throw "$Label stack bytes are malformed."
    }
    if ($addressValue -gt [uint32]::MaxValue -or $addressValue -ne $spValue) {
        throw "$Label stack address disagrees with its x86 stack pointer."
    }
    if ($RequirePairable -and
        (-not $queryValid -or $address -cne $sp -or $validBytes -lt 4)) {
        throw "$Label lacks a pairable stack return address."
    }
    if ($validBytes -lt 4) {
        return $null
    }
    $value = [uint64]0
    for ($index = 0; $index -lt 4; $index++) {
        $value = $value -bor ([Convert]::ToUInt64($hex.Substring($index * 2, 2), 16) -shl ($index * 8))
    }
    return Convert-ToCanonicalHex $value
}

function Get-EventRegister {
    param($Event, [string]$Name, [string]$Label)

    $registers = Get-RequiredObject $Event 'registers' $Label
    return Assert-HexText $registers $Name "$Label registers"
}

function Test-EventContextValid {
    param($Event, [string]$Label)

    $reportedControl = Get-RequiredBoolean $Event 'control_registers_valid' $Label
    $reportedInteger = Get-RequiredBoolean $Event 'integer_registers_valid' $Label
    $reportedViews = Get-RequiredBoolean $Event 'register_views_agree' $Label
    $contextFlags = Convert-UnsignedNumericText `
        (Assert-HexText $Event 'context_flags' $Label) "$Label context_flags"
    $controlMask = [uint64]0x10001
    $integerMask = [uint64]0x10002
    $control = ($contextFlags -band $controlMask) -eq $controlMask
    $integer = ($contextFlags -band $integerMask) -eq $integerMask
    $pc = Convert-UnsignedNumericText (Assert-HexText $Event 'pc' $Label) "$Label pc"
    $sp = Convert-UnsignedNumericText (Assert-HexText $Event 'sp' $Label) "$Label sp"
    $fp = Convert-UnsignedNumericText (Assert-HexText $Event 'fp' $Label) "$Label fp"
    $registerPc = Convert-UnsignedNumericText `
        (Get-EventRegister $Event 'eip' $Label) "$Label registers.eip"
    $registerSp = Convert-UnsignedNumericText `
        (Get-EventRegister $Event 'esp' $Label) "$Label registers.esp"
    $registerFp = Convert-UnsignedNumericText `
        (Get-EventRegister $Event 'ebp' $Label) "$Label registers.ebp"
    $views = $control -and $registerPc -eq $pc -and
        $registerSp -eq $sp -and $registerFp -eq $fp
    if ($reportedControl -ne $control -or $reportedInteger -ne $integer -or
        $reportedViews -ne $views) {
        throw "$Label context-derived flags disagree with raw context evidence."
    }
    $stack = Get-RequiredObject $Event 'stack' $Label
    $stackValid = Get-RequiredBoolean $stack 'query_valid' "$Label stack"
    Get-EventStackReturnAddress $Event $Label | Out-Null
    $valid = $control -and $integer -and $views -and
        $contextFlags -le [uint32]::MaxValue -and
        $pc -le [uint32]::MaxValue -and $sp -le [uint32]::MaxValue -and
        $fp -le [uint32]::MaxValue -and $stackValid
    if ([string]$Event.event_type -ceq 'return') {
        $instruction = Get-RequiredObject $Event 'instruction_bytes' $Label
        $instructionAddress = Assert-HexText $instruction 'address' "$Label instruction"
        $instructionValid = Get-RequiredBoolean $instruction 'query_valid' "$Label instruction"
        $instructionBytes = Get-RequiredUInt64 $instruction 'valid_bytes' "$Label instruction"
        $instructionHex = Get-RequiredString `
            $instruction 'hex' "$Label instruction" -AllowEmpty
        if ($instructionHex -notmatch '^(?:[0-9A-F]{2})*$' -or
            $instructionHex.Length -ne $instructionBytes * 2) {
            throw "$Label instruction bytes are malformed."
        }
        $valid = $valid -and $instructionValid -and
            $instructionAddress -ceq [string]$Event.pc
    }
    return [bool]$valid
}

function Test-EventDecodedNearReturn {
    param($Event, [string]$Label)

    $instruction = Get-RequiredObject $Event 'instruction_bytes' $Label
    $validBytes = Get-RequiredUInt64 $instruction 'valid_bytes' "$Label instruction"
    $hex = Get-RequiredString $instruction 'hex' "$Label instruction" -AllowEmpty
    if ($validBytes -gt 3) {
        throw "$Label return-instruction buffer exceeds the native three-byte bound."
    }
    $actual =
        ($validBytes -ge 1 -and $hex -match '^C3') -or
        ($validBytes -ge 3 -and $hex -match '^C2[0-9A-F]{4}')
    $reported = Get-RequiredBoolean $Event 'decoded_near_return' $Label
    if ($reported -ne $actual) {
        throw "$Label decoded-return flag disagrees with its instruction bytes."
    }
    return [bool]$actual
}

function Assert-CallContextRelationships {
    param(
        [Parameter(Mandatory = $true)]$Targets,
        [Parameter(Mandatory = $true)]$TargetSpecifications,
        [Parameter(Mandatory = $true)]$Events,
        [Parameter(Mandatory = $true)]$Invocations,
        [Parameter(Mandatory = $true)]$GapSummary,
        [Parameter(Mandatory = $true)]$Summary,
        [Parameter(Mandatory = $true)][int]$ExpectedStackBytes,
        [string]$Schema = 'bea.ttd.call-context.v3'
    )

    if (@('bea.ttd.call-context.v2', 'bea.ttd.call-context.v3') -cnotcontains
        $Schema) {
        throw "Unsupported call-context relationship schema: $Schema"
    }
    $legacyV2 = $Schema -ceq 'bea.ttd.call-context.v2'

    $eventCallCounts = [uint64[]]::new($Targets.Count)
    $eventEntryCounts = [uint64[]]::new($Targets.Count)
    $eventReturnCounts = [uint64[]]::new($Targets.Count)
    $orphanReturnCounts = [uint64[]]::new($Targets.Count)
    $pairCounts = [uint64[]]::new($Targets.Count)
    $returnCounts = [uint64[]]::new($Targets.Count)
    $gapFreeCounts = [uint64[]]::new($Targets.Count)
    $allTargetExpectationsPassed = $true
    $allPairingExpectationsPassed = $true
    $allEventContextsValid = $true
    $allEventsOrdered = $true

    if ($TargetSpecifications.Count -ne $Targets.Count) {
        throw 'Call-context target rows do not match the snapshotted target table.'
    }

    for ($index = 0; $index -lt $Targets.Count; $index++) {
        $target = $Targets[$index]
        $specification = $TargetSpecifications[$index]
        if ((Get-RequiredIndex $target 'target_index' "target $index") -ne $index) {
            throw "Call-context target indexes are not contiguous at $index."
        }
        $targetCountFields = @(
                'observed_entry_count',
                'observed_call_count',
                'observed_return_count',
                'observed_call_entry_pair_count',
                'observed_validated_return_count',
                'observed_gap_free_envelope_count')
        if (-not $legacyV2) {
            $targetCountFields += 'observed_orphan_return_count'
        }
        foreach ($field in $targetCountFields) {
            Get-RequiredUInt64 $target $field "target $index" | Out-Null
        }
        $entryRva = Assert-HexText $target 'entry_rva' "target $index"
        $entryVa = Assert-HexText $target 'entry_va' "target $index"
        if ($entryRva -cne [string]$specification.entry_rva -or
            $entryVa -cne [string]$specification.entry_va) {
            throw "Target $index identity disagrees with the snapshotted target table."
        }
        foreach ($field in @(
                'expected_entry_count',
                'expected_call_count',
                'expected_return_count')) {
            $actual = Get-NullableUInt64 $target $field "target $index"
            $expected = $specification.$field
            if (($null -eq $actual) -ne ($null -eq $expected) -or
                ($null -ne $actual -and $actual -ne $expected)) {
                throw "Target $index $field disagrees with the snapshotted target table."
            }
        }
        $ranges = @(Get-RequiredArray $target 'ranges' "target $index")
        if ($ranges.Count -ne $specification.ranges.Count) {
            throw "Target $index ranges disagree with the snapshotted target table."
        }
        for ($rangeIndex = 0; $rangeIndex -lt $ranges.Count; $rangeIndex++) {
            if ((Assert-HexText $ranges[$rangeIndex] 'rva_start' "target $index range") -cne
                    [string]$specification.ranges[$rangeIndex].rva_start -or
                (Assert-HexText $ranges[$rangeIndex] 'rva_end_exclusive' "target $index range") -cne
                    [string]$specification.ranges[$rangeIndex].rva_end_exclusive) {
                throw "Target $index ranges disagree with the snapshotted target table."
            }
        }
        $targetExpectation = $true
        foreach ($pair in @(
                @('expected_entry_count', 'observed_entry_count'),
                @('expected_call_count', 'observed_call_count'),
                @('expected_return_count', 'observed_return_count'))) {
            $expected = Get-NullableUInt64 $target $pair[0] "target $index"
            $observed = Get-RequiredUInt64 $target $pair[1] "target $index"
            if ($null -ne $expected -and $expected -ne $observed) {
                $targetExpectation = $false
            }
        }
        if ((Get-RequiredBoolean $target 'expectations_passed' "target $index") -ne
            $targetExpectation) {
            throw "Target $index expectations flag disagrees with its counts."
        }
        $allTargetExpectationsPassed = $allTargetExpectationsPassed -and $targetExpectation
    }

    $priorEventEpoch = [uint64]0
    $havePriorEventEpoch = $false
    $priorEventPosition = $null
    $priorEventPositionByThread = @{}
    $sameThreadPositionGroups = @{}
    for ($index = 0; $index -lt $Events.Count; $index++) {
        $event = $Events[$index]
        if ((Get-RequiredIndex $event 'event_index' "event $index") -ne $index) {
            throw "Call-context event indexes are not contiguous at $index."
        }
        $eventType = Get-RequiredString $event 'event_type' "event $index"
        if (@('call', 'entry', 'return') -cnotcontains $eventType) {
            throw "Call-context event $index has unknown type '$eventType'."
        }
        $targetIndex = Get-RequiredIndex $event 'target_index' "event $index"
        if ($targetIndex -lt 0 -or $targetIndex -ge $Targets.Count) {
            throw "Call-context event $index has an invalid target index."
        }
        $eventEpoch = if ($legacyV2) {
            [uint64]0
        } else {
            Get-RequiredUInt64 $event 'association_epoch' "event $index"
        }
        if (-not $legacyV2) {
            if ($havePriorEventEpoch -and $eventEpoch -lt $priorEventEpoch) {
                throw "Call-context event epochs decrease at event $index."
            }
            $priorEventEpoch = $eventEpoch
            $havePriorEventEpoch = $true
        }
        switch ($eventType) {
            'call' { $eventCallCounts[$targetIndex]++ }
            'entry' { $eventEntryCounts[$targetIndex]++ }
            'return' { $eventReturnCounts[$targetIndex]++ }
        }
        $eventPosition = Convert-TtdPositionValue $event 'position' "event $index"
        $previousEventPosition = Convert-TtdPositionValue `
            $event 'previous_position' "event $index"
        if ((Compare-TtdPositionValue $previousEventPosition $eventPosition) -gt 0) {
            throw "Call-context event $index has a previous position after its position."
        }
        if ($null -ne $priorEventPosition -and
            (Compare-TtdPositionValue $eventPosition $priorEventPosition) -lt 0) {
            $allEventsOrdered = $false
        }
        $priorEventPosition = $eventPosition
        foreach ($field in @('pc', 'sp', 'fp', 'instruction_target', 'fallthrough', 'raw_edx_eax')) {
            Assert-HexText $event $field "event $index" | Out-Null
        }
        $uniqueThreadId = Get-RequiredUInt32TextScalar `
            $event 'unique_thread_id' "event $index"
        $threadKey = $uniqueThreadId.ToString(
            [System.Globalization.CultureInfo]::InvariantCulture)
        $eventPcText = Assert-HexText $event 'pc' "event $index"
        if ($priorEventPositionByThread.ContainsKey($threadKey)) {
            $priorThreadPosition = $priorEventPositionByThread[$threadKey]
            $threadPositionComparison =
                Compare-TtdPositionValue $eventPosition $priorThreadPosition
            if ($threadPositionComparison -gt 0 -and
                (Compare-TtdPositionValue `
                    $previousEventPosition $priorThreadPosition) -lt 0) {
                throw "Call-context event $index has impossible same-thread chronology."
            }
        }
        $priorEventPositionByThread[$threadKey] = $eventPosition
        $positionGroupKey = "$threadKey|$([string]$event.position)"
        if (-not $sameThreadPositionGroups.ContainsKey($positionGroupKey)) {
            $sameThreadPositionGroups[$positionGroupKey] = [pscustomobject]@{
                pc = $eventPcText
                previousPosition = [string]$event.previous_position
                eventTypes = [System.Collections.Generic.HashSet[string]]::new(
                    [System.StringComparer]::Ordinal)
            }
        }
        $positionGroup = $sameThreadPositionGroups[$positionGroupKey]
        if ($eventPcText -cne [string]$positionGroup.pc -or
            [string]$event.previous_position -cne
                [string]$positionGroup.previousPosition -or
            (($eventType -ceq 'call' -and $positionGroup.eventTypes.Contains('return')) -or
             ($eventType -ceq 'return' -and $positionGroup.eventTypes.Contains('call')))) {
            throw "Call-context event $index has incoherent same-thread same-position evidence."
        }
        [void]$positionGroup.eventTypes.Add($eventType)
        Get-RequiredUInt32TextScalar $event 'os_thread_id' "event $index" | Out-Null
        $registers = Get-RequiredObject $event 'registers' "event $index"
        $expectedRegisterNames = @(
            'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp', 'eip', 'eflags'
        )
        $actualRegisterNames = @($registers.PSObject.Properties.Name)
        if ($actualRegisterNames.Count -ne $expectedRegisterNames.Count -or
            @($actualRegisterNames | Where-Object {
                    $expectedRegisterNames -cnotcontains $_
                }).Count -ne 0) {
            throw "Call-context event $index has a missing or unexpected x86 register."
        }
        $registerValues = @{}
        foreach ($registerName in $expectedRegisterNames) {
            $registerValue = Convert-UnsignedNumericText `
                (Get-EventRegister $event $registerName "event $index") `
                "event $index registers.$registerName"
            if ($registerValue -gt [uint32]::MaxValue) {
                throw "Call-context event $index register $registerName exceeds x86 width."
            }
            $registerValues[$registerName] = [uint64]$registerValue
        }
        $rawEdxEax = Convert-UnsignedNumericText `
            (Assert-HexText $event 'raw_edx_eax' "event $index") `
            "event $index raw_edx_eax"
        $recomputedEdxEax = [uint64](
            $registerValues['edx'] * [uint64]4294967296 + $registerValues['eax'])
        if ($rawEdxEax -ne $recomputedEdxEax) {
            throw "Call-context event $index raw EDX:EAX disagrees with its registers."
        }
        $basicReturnValue = Convert-UnsignedNumericText `
            (Assert-HexText $event 'basic_return_value_untyped' "event $index") `
            "event $index basic_return_value_untyped"
        if ($basicReturnValue -gt [uint32]::MaxValue -or
            $basicReturnValue -ne $registerValues['eax']) {
            throw "Call-context event $index basic untyped return value disagrees with EAX."
        }
        $stack = Get-RequiredObject $event 'stack' "event $index"
        $stackRequested = Get-RequiredIndex `
            $stack 'requested_bytes' "event $index stack"
        $stackValidBytes = Get-RequiredUInt64 `
            $stack 'valid_bytes' "event $index stack"
        if ($stackRequested -ne $ExpectedStackBytes -or
            $stackValidBytes -gt [uint64]$stackRequested) {
            throw "Call-context event $index stack extent disagrees with the requested bound."
        }
        foreach ($field in @(
                'control_registers_valid',
                'integer_registers_valid',
                'register_views_agree',
                'decoded_near_return')) {
            Get-RequiredBoolean $event $field "event $index" | Out-Null
        }
        $instruction = Get-RequiredObject `
            $event 'instruction_bytes' "event $index"
        $instructionAddress = Convert-UnsignedNumericText `
            (Assert-HexText $instruction 'address' "event $index instruction") `
            "event $index instruction address"
        $instructionValidBytes = Get-RequiredUInt64 `
            $instruction 'valid_bytes' "event $index instruction"
        $instructionQueryValid = Get-RequiredBoolean `
            $instruction 'query_valid' "event $index instruction"
        $instructionHex = Get-RequiredString `
            $instruction 'hex' "event $index instruction" -AllowEmpty
        if ($instructionAddress -gt [uint32]::MaxValue -or
            $instructionHex -notmatch '^(?:[0-9A-F]{2})*$' -or
            $instructionHex.Length -ne $instructionValidBytes * 2) {
            throw "Call-context event $index instruction envelope is malformed."
        }
        if ($eventType -cne 'return' -and
            ($instructionAddress -ne 0 -or $instructionValidBytes -ne 0 -or
             $instructionQueryValid -or $instructionHex -cne '' -or
             (Get-RequiredBoolean $event 'decoded_near_return' "event $index"))) {
            throw "Call-context non-return event $index carries return-instruction evidence."
        }
        $target = $Targets[$targetIndex]
        $targetEntry = Convert-UnsignedNumericText `
            (Assert-HexText $target 'entry_va' "target $targetIndex") `
            "target $targetIndex entry_va"
        $eventPc = Convert-UnsignedNumericText `
            (Assert-HexText $event 'pc' "event $index") "event $index pc"
        $instructionTarget = Convert-UnsignedNumericText `
            (Assert-HexText $event 'instruction_target' "event $index") `
            "event $index instruction_target"
        $fallthrough = Convert-UnsignedNumericText `
            (Assert-HexText $event 'fallthrough' "event $index") `
            "event $index fallthrough"
        foreach ($value in @($eventPc, $instructionTarget, $fallthrough)) {
            if ($value -gt [uint32]::MaxValue) {
                throw "Call-context event $index contains an address wider than x86."
            }
        }
        switch ($eventType) {
            'call' {
                if ($instructionTarget -ne $targetEntry -or
                    $fallthrough -le $eventPc -or
                    ($fallthrough - $eventPc) -lt 2 -or
                    ($fallthrough - $eventPc) -gt 15) {
                    throw "Call-context call event $index does not target its selected entry."
                }
            }
            'entry' {
                if ($eventPc -ne $targetEntry -or
                    $instructionTarget -ne $targetEntry -or $fallthrough -ne 0) {
                    throw "Call-context entry event $index does not identify its selected entry."
                }
            }
            'return' {
                $entryRva = Convert-UnsignedNumericText `
                    (Assert-HexText $target 'entry_rva' "target $targetIndex") `
                    "target $targetIndex entry_rva"
                if ($targetEntry -lt $entryRva) {
                    throw "Target $targetIndex entry VA/RVA cannot define a module base."
                }
                $moduleBase = $targetEntry - $entryRva
                $returnInRange = $false
                if ($eventPc -ge $moduleBase) {
                    $returnRva = $eventPc - $moduleBase
                    foreach ($range in @(
                            Get-RequiredArray $target 'ranges' "target $targetIndex")) {
                        $rangeStart = Convert-UnsignedNumericText `
                            (Assert-HexText $range 'rva_start' "target $targetIndex range") `
                            "target $targetIndex range start"
                        $rangeEnd = Convert-UnsignedNumericText `
                            (Assert-HexText $range 'rva_end_exclusive' "target $targetIndex range") `
                            "target $targetIndex range end"
                        if ($returnRva -ge $rangeStart -and $returnRva -lt $rangeEnd) {
                            $returnInRange = $true
                            break
                        }
                    }
                }
                if (-not $returnInRange -or $fallthrough -ne 0) {
                    throw "Call-context return event $index is outside its selected target range."
                }
            }
        }
        $allEventContextsValid = $allEventContextsValid -and
            (Test-EventContextValid $event "event $index")
        if ($eventType -ceq 'return') {
            Test-EventDecodedNearReturn $event "event $index" | Out-Null
        }
    }

    function Assert-LinkedEvent {
        param(
            [int]$EventIndex,
            [string]$ExpectedType,
            [int]$InvocationIndex,
            [int]$TargetIndex,
            [uint64]$Thread,
            [uint64]$AssociationEpoch,
            [bool]$LegacySchemaV2
        )

        if ($EventIndex -lt 0 -or $EventIndex -ge $Events.Count) {
            throw "Invocation $InvocationIndex references an invalid event."
        }
        $event = $Events[$EventIndex]
        $eventTargetIndex = Get-RequiredIndex $event 'target_index' "event $EventIndex"
        $eventInvocationIndex = Get-NullableIndex `
            $event 'invocation_index' "event $EventIndex"
        if ((Get-RequiredString $event 'event_type' "event $EventIndex") -cne
                $ExpectedType -or
            $eventTargetIndex -ne $TargetIndex -or
            (Get-RequiredUInt32TextScalar `
                $event 'unique_thread_id' "event $EventIndex") -ne $Thread -or
            (-not $LegacySchemaV2 -and
             (Get-RequiredUInt64 $event 'association_epoch' "event $EventIndex") -ne
                $AssociationEpoch) -or
            $null -eq $eventInvocationIndex -or
            $eventInvocationIndex -ne $InvocationIndex) {
            throw "Invocation $InvocationIndex has a broken $ExpectedType backlink."
        }
    }

    for ($index = 0; $index -lt $Invocations.Count; $index++) {
        $invocation = $Invocations[$index]
        if ((Get-RequiredIndex $invocation 'invocation_index' "invocation $index") -ne $index) {
            throw "Call-context invocation indexes are not contiguous at $index."
        }
        $targetIndex = Get-RequiredIndex $invocation 'target_index' "invocation $index"
        if ($targetIndex -lt 0 -or $targetIndex -ge $Targets.Count) {
            throw "Invocation $index has an invalid target index."
        }
        $thread = Get-RequiredUInt32TextScalar `
            $invocation 'unique_thread_id' "invocation $index"
        $associationEpoch = if ($legacyV2) {
            [uint64]0
        } else {
            Get-RequiredUInt64 $invocation 'association_epoch' "invocation $index"
        }
        $call = Get-NullableIndex $invocation 'call_event_index' "invocation $index"
        $entry = Get-NullableIndex $invocation 'entry_event_index' "invocation $index"
        $returned = Get-NullableIndex $invocation 'return_event_index' "invocation $index"
        $callEntryPassed = Get-RequiredBoolean $invocation 'call_entry_checks_passed' "invocation $index"
        $returnPassed = Get-RequiredBoolean $invocation 'return_checks_passed' "invocation $index"
        $gapCrossed = Get-RequiredBoolean $invocation 'gap_crossed' "invocation $index"
        $continuityCrossed = Get-RequiredBoolean $invocation 'continuity_break_crossed' "invocation $index"
        $grade = Get-RequiredString $invocation 'grade' "invocation $index"

        if ($null -ne $call) {
            Assert-LinkedEvent $call 'call' $index $targetIndex $thread `
                $associationEpoch $legacyV2
        }
        if ($null -ne $entry) {
            Assert-LinkedEvent $entry 'entry' $index $targetIndex $thread `
                $associationEpoch $legacyV2
        }
        if ($null -ne $returned) {
            Assert-LinkedEvent $returned 'return' $index $targetIndex $thread `
                $associationEpoch $legacyV2
        }

        $callEntrySemantics = $false
        if ($null -ne $call -and $null -ne $entry) {
            $callEvent = $Events[$call]
            $entryEvent = $Events[$entry]
            $callStackReturn = Get-EventStackReturnAddress `
                $callEvent "invocation $index call" -RequirePairable
            $entryStackReturn = Get-EventStackReturnAddress `
                $entryEvent "invocation $index entry" -RequirePairable
            $callPosition = Convert-TtdPositionValue `
                $callEvent 'position' "invocation $index call"
            $entryPosition = Convert-TtdPositionValue `
                $entryEvent 'position' "invocation $index entry"
            $registersUnchanged = $true
            foreach ($register in @('edi', 'esi', 'ebx', 'edx', 'ecx', 'eax', 'ebp', 'eflags')) {
                $registersUnchanged = $registersUnchanged -and
                    (Get-EventRegister $callEvent $register "invocation $index call") -ceq
                    (Get-EventRegister $entryEvent $register "invocation $index entry")
            }
            $callEntrySemantics =
                [string]$entryEvent.previous_position -ceq [string]$callEvent.position -and
                (Compare-TtdPositionValue $callPosition $entryPosition) -lt 0 -and
                [string]$entryEvent.sp -ceq [string]$callEvent.sp -and
                $callStackReturn -ceq [string]$callEvent.fallthrough -and
                $entryStackReturn -ceq [string]$callEvent.fallthrough -and
                $registersUnchanged
        }
        if ($callEntryPassed -ne $callEntrySemantics) {
            throw "Invocation $index call-entry flag disagrees with raw event evidence."
        }

        $returnSemantics = $false
        if ($null -ne $call -and $null -ne $entry -and $null -ne $returned) {
            $callEvent = $Events[$call]
            $entryEvent = $Events[$entry]
            $returnEvent = $Events[$returned]
            $returnStack = Get-EventStackReturnAddress `
                $returnEvent "invocation $index return" -RequirePairable
            $entryPosition = Convert-TtdPositionValue `
                $entryEvent 'position' "invocation $index entry"
            $returnPosition = Convert-TtdPositionValue `
                $returnEvent 'position' "invocation $index return"
            $returnSemantics =
                -not $gapCrossed -and -not $continuityCrossed -and
                (Compare-TtdPositionValue $entryPosition $returnPosition) -lt 0 -and
                (Test-EventDecodedNearReturn $returnEvent "invocation $index return") -and
                [string]$returnEvent.instruction_bytes.address -ceq [string]$returnEvent.pc -and
                [string]$returnEvent.sp -ceq [string]$entryEvent.sp -and
                $returnStack -ceq [string]$returnEvent.instruction_target -and
                [string]$returnEvent.instruction_target -ceq [string]$callEvent.fallthrough
        }
        if ($returnPassed -ne $returnSemantics) {
            throw "Invocation $index return flag disagrees with raw event evidence."
        }

        switch ($grade) {
            'CALL_ONLY' {
                if ($null -eq $call -or $null -ne $entry -or $null -ne $returned -or
                    $callEntryPassed -or $returnPassed) {
                    throw "Invocation $index contradicts CALL_ONLY."
                }
            }
            'ENTRY_ONLY' {
                if ($null -ne $call -or $null -eq $entry -or $null -ne $returned -or
                    $callEntryPassed -or $returnPassed) {
                    throw "Invocation $index contradicts ENTRY_ONLY."
                }
            }
            'CALL_ENTRY' {
                if ($null -eq $call -or $null -eq $entry -or -not $callEntryPassed -or
                    $null -ne $returned -or $returnPassed) {
                    throw "Invocation $index contradicts CALL_ENTRY."
                }
                $pairCounts[$targetIndex]++
            }
            'CALL_ENTRY_RETURN' {
                if ($null -eq $call -or $null -eq $entry -or $null -eq $returned -or
                    -not $callEntryPassed -or -not $returnPassed -or
                    $gapCrossed -or $continuityCrossed) {
                    throw "Invocation $index contradicts CALL_ENTRY_RETURN."
                }
                $pairCounts[$targetIndex]++
                $returnCounts[$targetIndex]++
                $gapFreeCounts[$targetIndex]++
            }
            default { throw "Invocation $index has unknown grade '$grade'." }
        }
    }

    for ($index = 0; $index -lt $Events.Count; $index++) {
        $event = $Events[$index]
        $eventType = Get-RequiredString $event 'event_type' "event $index"
        $targetIndex = Get-RequiredIndex $event 'target_index' "event $index"
        $linkedInvocation = Get-NullableIndex $event 'invocation_index' "event $index"
        if ($null -eq $linkedInvocation) {
            if ($eventType -cne 'return') {
                throw "Call-context $eventType event $index lacks an invocation backlink."
            }
            $orphanReturnCounts[$targetIndex]++
            continue
        }
        if ($linkedInvocation -lt 0 -or $linkedInvocation -ge $Invocations.Count) {
            throw "Call-context event $index references an invalid invocation."
        }
        $invocation = $Invocations[$linkedInvocation]
        $inverseField = switch ($eventType) {
            'call' { 'call_event_index' }
            'entry' { 'entry_event_index' }
            'return' { 'return_event_index' }
        }
        $inverseIndex = Get-NullableIndex `
            $invocation $inverseField "invocation $linkedInvocation"
        if ($null -eq $inverseIndex -or $inverseIndex -ne $index) {
            throw "Call-context event $index has no matching invocation backlink."
        }
        if ($eventType -ceq 'return' -and
            (Get-RequiredString `
                $invocation 'grade' "invocation $linkedInvocation") -cne
                'CALL_ENTRY_RETURN') {
            throw "Call-context return event $index is linked to a non-return grade."
        }
    }

    # Schema v3 exposes association epochs, so replay the collector's pending
    # call/LIFO state. Legacy v2 intentionally did not serialize those epochs;
    # its exact backlinks, raw call-entry-return semantics, and aggregate
    # accounting remain independently checked above and below.
    if (-not $legacyV2) {
        $pendingByThread = @{}
        $activeByThread = @{}
        $replayedAssociationEpoch = [uint64]0
        $haveReplayedAssociationEpoch = $false
        for ($index = 0; $index -lt $Events.Count; $index++) {
            $event = $Events[$index]
            $eventEpoch = Get-RequiredUInt64 $event 'association_epoch' "event $index"
            if (-not $haveReplayedAssociationEpoch -or
                $eventEpoch -ne $replayedAssociationEpoch) {
                $pendingByThread = @{}
                $activeByThread = @{}
                $replayedAssociationEpoch = $eventEpoch
                $haveReplayedAssociationEpoch = $true
            }
            $eventType = Get-RequiredString $event 'event_type' "event $index"
            $thread = Get-RequiredUInt32TextScalar `
                $event 'unique_thread_id' "event $index"
            $threadKey = $thread.ToString(
                [System.Globalization.CultureInfo]::InvariantCulture)
            $linkedInvocation = Get-NullableIndex `
                $event 'invocation_index' "event $index"

            if ($eventType -ceq 'call') {
                if ($null -eq $linkedInvocation) {
                    throw "Call-context call event $index lacks an invocation backlink."
                }
                if ($pendingByThread.ContainsKey($threadKey)) {
                    $displacedInvocation = [int]$pendingByThread[$threadKey]
                    if (-not (Get-RequiredBoolean `
                        $Invocations[$displacedInvocation] 'continuity_break_crossed' `
                        "invocation $displacedInvocation")) {
                        throw "Call-context call event $index contradicts native pending-call association."
                    }
                }
                $pendingByThread[$threadKey] = [int]$linkedInvocation
                continue
            }

            if ($eventType -ceq 'entry') {
                if ($null -eq $linkedInvocation) {
                    throw "Call-context entry event $index lacks an invocation backlink."
                }
                $grade = Get-RequiredString `
                    $Invocations[$linkedInvocation] 'grade' "invocation $linkedInvocation"
                if ($grade -ceq 'CALL_ENTRY' -or $grade -ceq 'CALL_ENTRY_RETURN') {
                    if (-not $pendingByThread.ContainsKey($threadKey) -or
                        [int]$pendingByThread[$threadKey] -ne $linkedInvocation) {
                        throw "Call-context entry event $index contradicts native pending-call association."
                    }
                    if (-not $activeByThread.ContainsKey($threadKey)) {
                        $activeByThread[$threadKey] =
                            [System.Collections.Generic.List[int]]::new()
                    }
                    $activeByThread[$threadKey].Add([int]$linkedInvocation)
                } elseif ($grade -cne 'ENTRY_ONLY') {
                    throw "Call-context entry event $index has an impossible association grade."
                }
                $pendingByThread.Remove($threadKey)
                continue
            }

            if ($eventType -cne 'return') {
                continue
            }
            $expectedInvocation = $null
            if ($activeByThread.ContainsKey($threadKey)) {
                $active = $activeByThread[$threadKey]
                if ($active.Count -gt 0) {
                    $expectedInvocation = [int]$active[$active.Count - 1]
                    $active.RemoveAt($active.Count - 1)
                }
            }
            if ($null -eq $linkedInvocation) {
                if ($null -ne $expectedInvocation -and
                    $null -ne (Get-NullableIndex `
                        $Invocations[$expectedInvocation] 'return_event_index' `
                        "invocation $expectedInvocation")) {
                    throw "Call-context orphan return event $index contradicts native LIFO association."
                }
            } elseif ($null -eq $expectedInvocation -or
                $linkedInvocation -ne $expectedInvocation) {
                throw "Call-context return event $index contradicts native LIFO association."
            }
        }
    }

    $pairTotal = [uint64]0
    $returnTotal = [uint64]0
    $rawReturnTotal = [uint64]0
    $orphanReturnTotal = [uint64]0
    $gapFreeTotal = [uint64]0
    $entryEventTotal = [uint64]0
    $callEventTotal = [uint64]0
    for ($index = 0; $index -lt $Targets.Count; $index++) {
        $target = $Targets[$index]
        $observedEntries = Get-RequiredUInt64 `
            $target 'observed_entry_count' "target $index"
        $observedCalls = Get-RequiredUInt64 `
            $target 'observed_call_count' "target $index"
        $observedReturns = Get-RequiredUInt64 `
            $target 'observed_return_count' "target $index"
        $observedOrphans = if ($legacyV2) {
            $orphanReturnCounts[$index]
        } else {
            Get-RequiredUInt64 `
                $target 'observed_orphan_return_count' "target $index"
        }
        if ($observedEntries -ne $eventEntryCounts[$index] -or
            $observedCalls -ne $eventCallCounts[$index] -or
            $observedReturns -ne $eventReturnCounts[$index] -or
            $observedOrphans -ne $orphanReturnCounts[$index] -or
            (Get-RequiredUInt64 $target 'observed_call_entry_pair_count' "target $index") -ne
                $pairCounts[$index] -or
            (Get-RequiredUInt64 $target 'observed_validated_return_count' "target $index") -ne
                $returnCounts[$index] -or
            (Get-RequiredUInt64 $target 'observed_gap_free_envelope_count' "target $index") -ne
                $gapFreeCounts[$index]) {
            throw "Target $index aggregate counts disagree with its invocations."
        }
        if ($observedReturns -ne
            (Add-UInt64Checked $returnCounts[$index] $orphanReturnCounts[$index] `
                "target $index return accounting")) {
            throw "Target $index return/orphan accounting does not close."
        }
        $expectedCall = Get-NullableUInt64 `
            $target 'expected_call_count' "target $index"
        $expectedEntry = Get-NullableUInt64 `
            $target 'expected_entry_count' "target $index"
        if ($null -ne $expectedCall -and $null -ne $expectedEntry -and
            $expectedCall -eq $expectedEntry -and
            $pairCounts[$index] -ne $expectedCall) {
            $allPairingExpectationsPassed = $false
        }
        $pairTotal = Add-UInt64Checked $pairTotal $pairCounts[$index] 'pair total'
        $returnTotal = Add-UInt64Checked $returnTotal $returnCounts[$index] `
            'validated return total'
        $rawReturnTotal = Add-UInt64Checked $rawReturnTotal $eventReturnCounts[$index] `
            'raw return total'
        $orphanReturnTotal = Add-UInt64Checked `
            $orphanReturnTotal $orphanReturnCounts[$index] 'orphan return total'
        $gapFreeTotal = Add-UInt64Checked $gapFreeTotal $gapFreeCounts[$index] `
            'gap-free envelope total'
        $entryEventTotal = Add-UInt64Checked `
            $entryEventTotal $observedEntries 'entry-event total'
        $callEventTotal = Add-UInt64Checked `
            $callEventTotal $observedCalls 'call-event total'
    }
    if ((Get-RequiredUInt64 $Summary 'call_entry_pair_count' 'summary') -ne $pairTotal -or
        (Get-RequiredUInt64 $Summary 'validated_return_count' 'summary') -ne $returnTotal -or
        (Get-RequiredUInt64 $Summary 'gap_free_envelope_count' 'summary') -ne $gapFreeTotal) {
        throw 'Call-context summary aggregates disagree with the invocation rows.'
    }
    if (-not $legacyV2 -and
        ((Get-RequiredUInt64 $Summary 'raw_return_count' 'summary') -ne
            $rawReturnTotal -or
         (Get-RequiredUInt64 $Summary 'orphan_return_count' 'summary') -ne
            $orphanReturnTotal)) {
        throw 'Call-context summary return aggregates disagree with the event rows.'
    }
    if ($rawReturnTotal -ne
        (Add-UInt64Checked $returnTotal $orphanReturnTotal `
            'summary return accounting')) {
        throw 'Call-context summary return/orphan accounting does not close.'
    }
    if ((Get-RequiredBoolean $Summary 'expectations_passed' 'summary') -ne
            $allTargetExpectationsPassed -or
        (Get-RequiredBoolean $Summary 'pairing_expectations_passed' 'summary') -ne
            $allPairingExpectationsPassed -or
        (Get-RequiredBoolean $Summary 'ordering_valid' 'summary') -ne
            $allEventsOrdered -or
        (Get-RequiredBoolean $Summary 'contexts_valid' 'summary') -ne
            $allEventContextsValid) {
        throw 'Call-context summary flags disagree with target, pairing, ordering, or event rows.'
    }

    $associationBarrierCount = $null
    $finalAssociationEpoch = $null
    if (-not $legacyV2) {
        $associationBarrierCount = [uint64]0
        foreach ($part in @(
                (Get-RequiredUInt64 $GapSummary 'kind_context_switch' 'gap summary'),
                (Get-RequiredUInt64 $GapSummary 'kind_unrecorded' 'gap summary'),
                (Get-RequiredUInt64 $GapSummary 'kind_large' 'gap summary'),
                (Get-RequiredUInt64 $Summary 'continuity_break_callbacks' 'summary'))) {
            $associationBarrierCount = Add-UInt64Checked `
                $associationBarrierCount $part 'association barrier total'
        }
        $recordedBarriers = Get-RequiredUInt64 `
            $Summary 'association_barrier_count' 'summary'
        $finalAssociationEpoch = Get-RequiredUInt64 `
            $Summary 'final_association_epoch' 'summary'
        if ($recordedBarriers -ne $associationBarrierCount -or
            $finalAssociationEpoch -ne $associationBarrierCount) {
            throw 'Call-context association-barrier accounting does not close.'
        }
    }
    $gapKindTotal = [uint64]0
    foreach ($part in @(
            (Get-RequiredUInt64 $GapSummary 'kind_no_gap' 'gap summary'),
            (Get-RequiredUInt64 $GapSummary 'kind_context_switch' 'gap summary'),
            (Get-RequiredUInt64 $GapSummary 'kind_unrecorded' 'gap summary'),
            (Get-RequiredUInt64 $GapSummary 'kind_large' 'gap summary'))) {
        $gapKindTotal = Add-UInt64Checked $gapKindTotal $part 'gap-kind total'
    }
    if ((Get-RequiredUInt64 $GapSummary 'total' 'gap summary') -ne $gapKindTotal) {
        throw 'Call-context gap total disagrees with its kind partition.'
    }
    $gapEventFields = @(
        'event_SyntheticSequence',
        'event_CodeCacheFlush',
        'event_PreAtomicOperation',
        'event_PotentialAtomicCollision',
        'event_EtwEvent',
        'event_DebugBreak',
        'event_FastFail',
        'event_KernelCall',
        'event_SyntheticFallback',
        'event_ExceptionDispatch',
        'event_UnknownInstruction',
        'event_ThreadSuspended',
        'event_SListRollback',
        'event_SyncPoint',
        'event_PauseEmulation',
        'event_StopEmulation',
        'event_Throttled'
    )
    $actualGapEventFields = @(
        $GapSummary.PSObject.Properties.Name |
            Where-Object { $_.StartsWith('event_', [System.StringComparison]::Ordinal) }
    )
    if ($actualGapEventFields.Count -ne $gapEventFields.Count -or
        @($actualGapEventFields | Where-Object { $gapEventFields -cnotcontains $_ }).Count -ne 0) {
        throw 'Call-context gap event partition has missing or unexpected fields.'
    }
    $gapEventTotal = [uint64]0
    foreach ($field in $gapEventFields) {
        $gapEventTotal = Add-UInt64Checked $gapEventTotal `
            (Get-RequiredUInt64 $GapSummary $field 'gap summary') 'gap-event total'
    }
    if ((Get-RequiredUInt64 $GapSummary 'total' 'gap summary') -ne $gapEventTotal) {
        throw 'Call-context gap total disagrees with its event partition.'
    }
    if (-not $legacyV2) {
        foreach ($event in $Events) {
            if ((Get-RequiredUInt64 $event 'association_epoch' 'event') -gt
                $finalAssociationEpoch) {
                throw 'Call-context event epoch exceeds the final association epoch.'
            }
        }
        foreach ($invocation in $Invocations) {
            if ((Get-RequiredUInt64 $invocation 'association_epoch' 'invocation') -gt
                $finalAssociationEpoch) {
                throw 'Call-context invocation epoch exceeds the final association epoch.'
            }
        }
    }

    return [ordered]@{
        callEntryPairCount = $pairTotal
        validatedReturnCount = $returnTotal
        rawReturnCount = $rawReturnTotal
        entryEventCount = $entryEventTotal
        callAndReturnEventCount = Add-UInt64Checked `
            $callEventTotal $rawReturnTotal 'call-and-return event total'
        orphanReturnCount = $orphanReturnTotal
        gapFreeEnvelopeCount = $gapFreeTotal
        associationBarrierCount = $associationBarrierCount
        finalAssociationEpoch = $finalAssociationEpoch
        targetExpectationsPassed = $allTargetExpectationsPassed
        pairingExpectationsPassed = $allPairingExpectationsPassed
        eventOrderingValid = $allEventsOrdered
        eventContextsValid = $allEventContextsValid
    }
}

function Assert-CallContextReplayBoundary {
    param(
        [Parameter(Mandatory = $true)]$Metadata,
        [Parameter(Mandatory = $true)]$Summary,
        [Parameter(Mandatory = $true)]$Events,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$RequestedFromArgument,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$RequestedToArgument,
        [Parameter(Mandatory = $true)][int]$ExpectedStackBytes,
        [Parameter(Mandatory = $true)][int]$ExpectedEventLimit,
        [Parameter(Mandatory = $true)][uint64]$EventCount,
        [Parameter(Mandatory = $true)][uint64]$EntryEventCount,
        [Parameter(Mandatory = $true)][uint64]$CallAndReturnEventCount
    )

    $lifetimeMin = Convert-TtdPositionValue $Metadata 'lifetime_min' 'metadata'
    $lifetimeMax = Convert-TtdPositionValue $Metadata 'lifetime_max' 'metadata'
    $requestedFrom = Convert-TtdPositionValue $Metadata 'requested_from' 'metadata'
    $requestedTo = Convert-TtdPositionValue $Metadata 'requested_to' 'metadata'
    if ((Compare-TtdPositionValue $lifetimeMin $lifetimeMax) -gt 0 -or
        (Compare-TtdPositionValue $requestedFrom $lifetimeMin) -lt 0 -or
        (Compare-TtdPositionValue $requestedFrom $lifetimeMax) -gt 0 -or
        (Compare-TtdPositionValue $requestedTo $lifetimeMin) -lt 0 -or
        (Compare-TtdPositionValue $requestedTo $lifetimeMax) -gt 0 -or
        (Compare-TtdPositionValue $requestedFrom $requestedTo) -gt 0) {
        throw 'Call-context requested window is outside its reported lifetime.'
    }

    $moduleLoadSequence = Convert-UnsignedNumericText `
        (Assert-HexText $Metadata 'module_load_sequence' 'metadata') `
        'metadata module_load_sequence'
    $moduleUnloadSequence = Convert-UnsignedNumericText `
        (Assert-HexText $Metadata 'module_unload_sequence' 'metadata') `
        'metadata module_unload_sequence'
    $sequenceIdMax = [Convert]::ToUInt64('FFFFFFFFFFFFFFFE', 16)
    $finiteUnload = $moduleUnloadSequence -ne $sequenceIdMax
    if ($moduleLoadSequence -gt $sequenceIdMax -or
        $moduleUnloadSequence -gt $sequenceIdMax -or
        $requestedFrom.sequence -lt $moduleLoadSequence -or
        ($finiteUnload -and
         ($moduleLoadSequence -ge $moduleUnloadSequence -or
          $requestedTo.sequence -ge $moduleUnloadSequence))) {
        throw 'Call-context requested window claims a module instance that is not active.'
    }

    $expectedFrom = if ([string]::IsNullOrEmpty($RequestedFromArgument)) {
        Get-RequiredString $Metadata 'lifetime_min' 'metadata'
    } else {
        if ($RequestedFromArgument -notmatch '^0x[0-9A-F]+:0x[0-9A-F]+$') {
            throw 'Call-context -From must be a canonical TTD position.'
        }
        $RequestedFromArgument
    }
    $expectedTo = if ([string]::IsNullOrEmpty($RequestedToArgument)) {
        Get-RequiredString $Metadata 'lifetime_max' 'metadata'
    } else {
        if ($RequestedToArgument -notmatch '^0x[0-9A-F]+:0x[0-9A-F]+$') {
            throw 'Call-context -To must be a canonical TTD position.'
        }
        $RequestedToArgument
    }
    if ((Get-RequiredString $Metadata 'requested_from' 'metadata') -cne $expectedFrom -or
        (Get-RequiredString $Metadata 'requested_to' 'metadata') -cne $expectedTo) {
        throw 'Call-context metadata window disagrees with the invocation.'
    }

    $reportedStackBytes = Get-RequiredIndex `
        $Metadata 'stack_bytes_requested' 'metadata'
    $reportedEventLimit = Get-RequiredUInt64 $Metadata 'event_limit' 'metadata'
    if ($reportedStackBytes -ne $ExpectedStackBytes -or
        $reportedEventLimit -ne [uint64]$ExpectedEventLimit -or
        $EventCount -gt $reportedEventLimit) {
        throw 'Call-context metadata limits disagree with the invocation or rows.'
    }

    $stopReason = Get-RequiredString $Summary 'stop_reason' 'summary'
    $expectedStopReason = if ([string]::IsNullOrEmpty($RequestedToArgument)) {
        'Process'
    } else {
        'Position'
    }
    $finalPosition = Convert-TtdPositionValue $Summary 'final_position' 'summary'
    $finalAtNativeTerminal =
        (Compare-TtdPositionValue $finalPosition $lifetimeMax) -eq 0
    if (-not [string]::IsNullOrEmpty($RequestedToArgument)) {
        $finalAtNativeTerminal =
            (Compare-TtdPositionValue $finalPosition $requestedTo) -eq 0
    } elseif (-not $finalAtNativeTerminal -and
        $lifetimeMax.steps -lt [uint64]::MaxValue) {
        # ReplayForward(Position::Max) has been observed to leave the cursor
        # exactly one step beyond lifetime.Max after the Process stop.
        $finalAtNativeTerminal =
            $finalPosition.sequence -eq $lifetimeMax.sequence -and
            $finalPosition.steps -eq ($lifetimeMax.steps + [uint64]1)
    }
    if (-not $finalAtNativeTerminal) {
        throw 'Call-context final position is outside the native replay terminal boundary.'
    }

    if ([uint64]$Events.Count -ne $EventCount) {
        throw 'Call-context replay event rows disagree with their declared count.'
    }
    for ($index = 0; $index -lt $Events.Count; $index++) {
        $eventPosition = Convert-TtdPositionValue `
            $Events[$index] 'position' "event $index"
        $previousPosition = Convert-TtdPositionValue `
            $Events[$index] 'previous_position' "event $index"
        if ((Compare-TtdPositionValue $eventPosition $requestedFrom) -lt 0 -or
            (Compare-TtdPositionValue $eventPosition $requestedTo) -gt 0 -or
            (Compare-TtdPositionValue $eventPosition $finalPosition) -gt 0) {
            throw "Call-context event $index is outside the requested replay window."
        }
        if ((Compare-TtdPositionValue $previousPosition $lifetimeMin) -lt 0 -or
            (Compare-TtdPositionValue $previousPosition $finalPosition) -gt 0 -or
            ($index -ne 0 -and
             (Compare-TtdPositionValue $previousPosition $requestedFrom) -lt 0)) {
            throw "Call-context event $index previous position is outside the replay boundary."
        }
    }
    $recomputedReplayComplete =
        $stopReason -ceq $expectedStopReason -and
        (Compare-TtdPositionValue $finalPosition $requestedTo) -ge 0
    $reportedReplayComplete = Get-RequiredBoolean $Summary 'replay_complete' 'summary'
    if ($reportedReplayComplete -ne $recomputedReplayComplete) {
        throw 'Call-context replay-complete flag disagrees with its stop boundary.'
    }

    $replayChunks = Get-RequiredUInt64 $Summary 'replay_chunks' 'summary'
    $replayChunkSteps = Get-RequiredUInt64 $Summary 'replay_chunk_steps' 'summary'
    $entryCallbacks = Get-RequiredUInt64 $Summary 'entry_callbacks' 'summary'
    $callReturnCallbacks = Get-RequiredUInt64 `
        $Summary 'call_return_callbacks' 'summary'
    $instructionsExecuted = Get-RequiredUInt64 `
        $Summary 'instructions_executed' 'summary'
    $stepsExecuted = Get-RequiredUInt64 $Summary 'steps_executed' 'summary'
    if ($replayChunkSteps -ne [uint64]1000000000) {
        throw 'Call-context replay callbacks or chunk limits do not close.'
    }
    if ($replayChunks -gt ([uint64]::MaxValue / $replayChunkSteps)) {
        throw 'Call-context replay chunk capacity overflows UInt64.'
    }
    $replayStepCapacity = [uint64]($replayChunks * $replayChunkSteps)
    if ($replayChunks -eq 0 -or $replayChunks -gt [uint64]1000000 -or
        $stepsExecuted -gt $replayStepCapacity -or
        $instructionsExecuted -gt $stepsExecuted -or
        $entryCallbacks -ne $EntryEventCount -or
        $callReturnCallbacks -lt $CallAndReturnEventCount -or
        $entryCallbacks -gt $replayStepCapacity -or
        $callReturnCallbacks -gt $replayStepCapacity) {
        throw 'Call-context replay callbacks or chunk limits do not close.'
    }

    return [ordered]@{
        replayComplete = [bool]$recomputedReplayComplete
        expectedStopReason = $expectedStopReason
        finalPosition = Get-RequiredString $Summary 'final_position' 'summary'
        requestedFrom = Get-RequiredString $Metadata 'requested_from' 'metadata'
        requestedTo = Get-RequiredString $Metadata 'requested_to' 'metadata'
        replayChunks = $replayChunks
        replayChunkSteps = $replayChunkSteps
        entryCallbacks = $entryCallbacks
        callReturnCallbacks = $callReturnCallbacks
        instructionsExecuted = $instructionsExecuted
        stepsExecuted = $stepsExecuted
        replayStepCapacity = $replayStepCapacity
    }
}

$tracePath = (Resolve-Path -LiteralPath $TraceFile).Path
$targetPath = (Resolve-Path -LiteralPath $TargetExe).Path
$targetsSourcePath = (Resolve-Path -LiteralPath $TargetsTsv).Path
$collectorPath = (Resolve-Path -LiteralPath $Collector).Path
foreach ($required in @($tracePath, $targetPath, $targetsSourcePath, $collectorPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required file was not found: $required"
    }
}
if ([System.IO.Path]::GetFileName($targetPath) -ine $ModuleName) {
    throw "Target filename must match -ModuleName ($ModuleName): $targetPath"
}

$outputRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-PathIsUnder -Path $outputRoot -Ancestor (Split-Path -Parent $tracePath)) {
    throw 'Refusing to place call-context output inside the immutable trace directory.'
}
if (Test-Path -LiteralPath $outputRoot) {
    if (-not (Test-Path -LiteralPath $outputRoot -PathType Container)) {
        throw "Output path exists and is not a directory: $outputRoot"
    }
    if (Get-ChildItem -LiteralPath $outputRoot -Force | Select-Object -First 1) {
        throw "Refusing to overwrite non-empty output directory: $outputRoot"
    }
} else {
    [System.IO.Directory]::CreateDirectory($outputRoot) | Out-Null
}

$contextPath = Join-Path $outputRoot 'call-context.jsonl'
$receiptPath = Join-Path $outputRoot 'receipt.json'
$manifestPath = Join-Path $outputRoot 'manifest.json'
$readyPath = Join-Path $outputRoot 'READY'
$targetsSnapshotPath = Join-Path $outputRoot 'targets.tsv'
$buildReceiptCopyPath = Join-Path $outputRoot 'collector-build-receipt.json'
$toolSnapshotDirectory = Join-Path $outputRoot 'collector-tool'
$collectorDirectory = Split-Path -Parent $collectorPath
$replayPath = Join-Path $collectorDirectory 'TTDReplay.dll'
$replayCpuPath = Join-Path $collectorDirectory 'TTDReplayCPU.dll'
$buildReceiptPath = Join-Path (Split-Path -Parent $collectorDirectory) 'build-receipt.json'
foreach ($dependency in @($replayPath, $replayCpuPath, $buildReceiptPath)) {
    if (-not (Test-Path -LiteralPath $dependency -PathType Leaf)) {
        throw "Collector dependency was not found: $dependency"
    }
}

$buildReceipt = Get-Content -Raw -LiteralPath $buildReceiptPath |
    ConvertFrom-Json -Depth 30
$repro = $buildReceipt.reproducibility
$reproBuilds = @($repro.isolatedBuilds)
if ([string]$buildReceipt.schemaVersion -cne 'bea-ttd-exec-coverage-build.v2' -or
    $reproBuilds.Count -ne 2 -or
    $repro.buildCount -ne 2 -or
    $repro.byteIdentical -ne $true -or
    $repro.distinctOutputRoots -ne $true -or
    $repro.allSelfTestsPassed -ne $true -or
    [string]$repro.pdbAlternatePath -cne 'ttd_exec_coverage.pdb' -or
    [string]$reproBuilds[0].root -ceq [string]$reproBuilds[1].root) {
    throw 'Collector build receipt does not close its two-build gate.'
}

$collectorSourceFacts = Get-FileFacts $collectorPath
$replaySourceFacts = Get-FileFacts $replayPath
$replayCpuSourceFacts = Get-FileFacts $replayCpuPath
$buildReceiptSourceFacts = Get-FileFacts $buildReceiptPath
if ([string]$buildReceipt.collector.sha256 -cne $collectorSourceFacts.sha256 -or
    [string]$buildReceipt.runtime.replaySha256 -cne $replaySourceFacts.sha256 -or
    [string]$buildReceipt.runtime.replayCpuSha256 -cne $replayCpuSourceFacts.sha256) {
    throw 'Collector or replay runtime hash disagrees with the build receipt.'
}
foreach ($build in $reproBuilds) {
    if ([string]$build.sha256 -cne $collectorSourceFacts.sha256 -or
        [string]$build.selfTest -cne 'PASS') {
        throw 'An isolated collector build disagrees with the published collector.'
    }
}

[System.IO.Directory]::CreateDirectory($toolSnapshotDirectory) | Out-Null
$snapshotCollectorPath = Join-Path $toolSnapshotDirectory 'ttd_exec_coverage.exe'
$snapshotReplayPath = Join-Path $toolSnapshotDirectory 'TTDReplay.dll'
$snapshotReplayCpuPath = Join-Path $toolSnapshotDirectory 'TTDReplayCPU.dll'
[System.IO.File]::Copy($collectorPath, $snapshotCollectorPath, $false)
[System.IO.File]::Copy($replayPath, $snapshotReplayPath, $false)
[System.IO.File]::Copy($replayCpuPath, $snapshotReplayCpuPath, $false)
[System.IO.File]::Copy($buildReceiptPath, $buildReceiptCopyPath, $false)
[System.IO.File]::Copy($targetsSourcePath, $targetsSnapshotPath, $false)

$collectorFacts = Get-FileFacts $snapshotCollectorPath
$replayFacts = Get-FileFacts $snapshotReplayPath
$replayCpuFacts = Get-FileFacts $snapshotReplayCpuPath
$buildReceiptFacts = Get-FileFacts $buildReceiptCopyPath
$targetsSourceFacts = Get-FileFacts $targetsSourcePath
$targetsFacts = Get-FileFacts $targetsSnapshotPath
if ($collectorFacts.sha256 -cne $collectorSourceFacts.sha256 -or
    $replayFacts.sha256 -cne $replaySourceFacts.sha256 -or
    $replayCpuFacts.sha256 -cne $replayCpuSourceFacts.sha256 -or
    $buildReceiptFacts.sha256 -cne $buildReceiptSourceFacts.sha256 -or
    $targetsFacts.sha256 -cne $targetsSourceFacts.sha256) {
    throw 'Private call-context snapshot disagrees with its validated source.'
}

$traceBefore = Get-FileFacts $tracePath
$targetBefore = Get-FileFacts $targetPath
$targetPe = Get-PeIdentity $targetPath
$effectiveBase = if ([string]::IsNullOrWhiteSpace($ExpectedBase)) {
    $targetPe.imageBase
} else {
    $ExpectedBase
}

$collectorArguments = [System.Collections.Generic.List[string]]::new()
foreach ($value in @(
        '--mode', 'call-context',
        '--trace', $tracePath,
        '--module', $ModuleName,
        '--out', $contextPath,
        '--targets-tsv', $targetsSnapshotPath,
        '--expect-base', $effectiveBase,
        '--expect-size', $targetPe.sizeOfImage,
        '--expect-timestamp', $targetPe.timestamp,
        '--expect-checksum', $targetPe.checksum,
        '--max-module-bytes', $targetPe.sizeOfImage,
        '--stack-bytes', [string]$StackBytes,
        '--event-limit', [string]$EventLimit
    )) {
    $collectorArguments.Add([string]$value)
}
if (-not [string]::IsNullOrWhiteSpace($From)) {
    $collectorArguments.Add('--from')
    $collectorArguments.Add($From)
}
if (-not [string]::IsNullOrWhiteSpace($To)) {
    $collectorArguments.Add('--to')
    $collectorArguments.Add($To)
}

$startedAt = (Get-Date).ToUniversalTime()
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
& $snapshotCollectorPath @collectorArguments
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

if (-not (Test-Path -LiteralPath $contextPath -PathType Leaf)) {
    $effectiveExitCode = Resolve-MissingCallContextExitCode $collectorExitCode
    $failure = [ordered]@{
        phase = 'post-collector-output-check'
        code = 'call-context-jsonl-missing'
        message = "Collector exited $collectorExitCode without producing call-context.jsonl."
    }
    $blockedReceipt = [ordered]@{
        schemaVersion = 'bea-ttd-call-context-receipt.v3'
        generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        startedAtUtc = $startedAt.ToString('o')
        finishedAtUtc = $finishedAt.ToString('o')
        elapsedSeconds = $stopwatch.Elapsed.TotalSeconds
        collectorExitCode = $collectorExitCode
        exitCode = $effectiveExitCode
        readyEligible = $false
        trace = $traceBefore
        target = [ordered]@{
            path = $targetBefore.path
            bytes = $targetBefore.bytes
            sha256 = $targetBefore.sha256
            lastWriteUtc = $targetBefore.lastWriteUtc
            pe = $targetPe
        }
        targetsSource = $targetsSourceFacts
        targetsSnapshot = $targetsFacts
        collector = $collectorFacts
        replayRuntime = [ordered]@{
            version = [string]$buildReceipt.runtime.version
            replay = $replayFacts
            replayCpu = $replayCpuFacts
        }
        buildReceipt = $buildReceiptFacts
        invocation = [ordered]@{
            moduleName = $ModuleName
            expectedBase = $effectiveBase
            from = $From
            to = $To
            stackBytes = $StackBytes
            eventLimit = $EventLimit
            replayMode = 'sequential-all-segments'
        }
        callContext = $null
        metadata = $null
        gapSummary = $null
        summary = $null
        failure = $failure
    }
    [System.IO.File]::WriteAllText(
        $receiptPath,
        ($blockedReceipt | ConvertTo-Json -Depth 35) + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
    $blockedReceiptFacts = Get-FileFacts $receiptPath
    $blockedManifest = [ordered]@{
        schemaVersion = 'bea-ttd-call-context-manifest.v3'
        generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        status = 'BLOCKED'
        collectorExitCode = $collectorExitCode
        exitCode = $effectiveExitCode
        specimen = [ordered]@{
            traceSha256 = $traceBefore.sha256
            targetSha256 = $targetBefore.sha256
            targetsSha256 = $targetsFacts.sha256
            moduleName = $ModuleName
            expectedBase = $effectiveBase
            sizeOfImage = $targetPe.sizeOfImage
            timestamp = $targetPe.timestamp
            checksum = $targetPe.checksum
        }
        artifacts = [ordered]@{
            callContext = $null
            receipt = $blockedReceiptFacts
            targets = $targetsFacts
            collector = $collectorFacts
            replay = $replayFacts
            replayCpu = $replayCpuFacts
            buildReceipt = $buildReceiptFacts
        }
        proof = $null
        failure = $failure
    }
    [System.IO.File]::WriteAllText(
        $manifestPath,
        ($blockedManifest | ConvertTo-Json -Depth 30) + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
    $blockedReceipt
    exit $effectiveExitCode
}

$metadata = $null
$gapSummary = $null
$summary = $null
$targets = [System.Collections.Generic.List[object]]::new()
$events = [System.Collections.Generic.List[object]]::new()
$invocations = [System.Collections.Generic.List[object]]::new()
$lineCount = 0
$kinds = [System.Collections.Generic.List[string]]::new()
$callContextSchema = $null
foreach ($line in [System.IO.File]::ReadLines($contextPath)) {
    $lineCount++
    $row = $line | ConvertFrom-Json -Depth 40
    $rowSchema = Get-RequiredString $row 'schema' "line $lineCount"
    if ($null -eq $callContextSchema) {
        if (@('bea.ttd.call-context.v2', 'bea.ttd.call-context.v3') -cnotcontains
            $rowSchema) {
            throw "Unexpected call-context schema on line $lineCount."
        }
        $callContextSchema = $rowSchema
    } elseif ($rowSchema -cne $callContextSchema) {
        throw "Unexpected call-context schema on line $lineCount."
    }
    $kind = Get-RequiredString $row 'kind' "line $lineCount"
    $kinds.Add($kind)
    switch ($kind) {
        'metadata' {
            if ($null -ne $metadata) { throw 'Multiple call-context metadata rows.' }
            $metadata = $row
        }
        'target' { $targets.Add($row) }
        'event' { $events.Add($row) }
        'invocation' { $invocations.Add($row) }
        'gap-summary' {
            if ($null -ne $gapSummary) { throw 'Multiple call-context gap summaries.' }
            $gapSummary = $row
        }
        'summary' {
            if ($null -ne $summary) { throw 'Multiple call-context summaries.' }
            $summary = $row
        }
        default { throw "Unexpected call-context row kind on line $lineCount`: $kind" }
    }
}
if ($null -eq $metadata -or $null -eq $gapSummary -or $null -eq $summary -or
    $targets.Count -eq 0 -or $kinds[0] -cne 'metadata' -or
    $kinds[$kinds.Count - 1] -cne 'summary') {
    throw 'Call-context JSONL is incomplete or out of envelope order.'
}
if ((Get-RequiredUInt64 $summary 'target_count' 'summary') -ne $targets.Count -or
    (Get-RequiredUInt64 $summary 'event_count' 'summary') -ne $events.Count -or
    (Get-RequiredUInt64 $summary 'invocation_count' 'summary') -ne $invocations.Count) {
    throw 'Call-context row counts disagree with the summary.'
}
if ((Get-RequiredString $metadata 'processor_architecture' 'metadata') -cne 'x86' -or
    (Get-RequiredString $metadata 'replay_mode' 'metadata') -cne
        'sequential-all-segments' -or
    (Get-RequiredString $metadata 'entry_phase' 'metadata') -cne
        'execute-watchpoint-before-entry-instruction' -or
    (Get-RequiredString $metadata 'call_phase' 'metadata') -cne
        'callback-position-at-call-instruction' -or
    (Get-RequiredString $metadata 'return_phase' 'metadata') -cne
        'callback-position-at-ret-instruction' -or
    (Get-RequiredString $metadata 'raw_value_policy' 'metadata') -cne
        'untyped-registers-and-bytes' -or
    (Get-RequiredString $metadata 'window_semantics' 'metadata') -cne
        'inclusive-position-bounds' -or
    (Get-RequiredString $metadata 'uint64_encoding' 'metadata') -cne
        'decimal-string' -or
    (Get-RequiredUInt64 $metadata 'trace_bytes' 'metadata') -ne
        [uint64]$traceBefore.bytes -or
    (Get-RequiredUInt64 $metadata 'targets_tsv_bytes' 'metadata') -ne
        [uint64]$targetsFacts.bytes -or
    (Get-RequiredString $metadata 'module_requested' 'metadata') -cne $ModuleName -or
    [System.IO.Path]::GetFileName(
        (Get-RequiredString $metadata 'module_name' 'metadata')) -ine $ModuleName -or
    (Assert-HexText $metadata 'module_base' 'metadata') -cne
        ('0x{0:X}' -f [Convert]::ToUInt64($effectiveBase.Substring(2), 16)) -or
    (Assert-HexText $metadata 'module_size' 'metadata') -cne
        ('0x{0:X}' -f [Convert]::ToUInt64($targetPe.sizeOfImage.Substring(2), 16)) -or
    (Assert-HexText $metadata 'module_timestamp' 'metadata') -cne
        ('0x{0:X}' -f [Convert]::ToUInt64($targetPe.timestamp.Substring(2), 16)) -or
    (Assert-HexText $metadata 'module_checksum' 'metadata') -cne
        ('0x{0:X}' -f [Convert]::ToUInt64($targetPe.checksum.Substring(2), 16))) {
    throw 'Call-context metadata disagrees with the trace, mode, or PE identity.'
}
if ($callContextSchema -ceq 'bea.ttd.call-context.v3' -and
    (Get-RequiredString $metadata 'association_policy' 'metadata') -cne
        'global-epoch-breaks-on-every-non-no-gap-and-continuity-callback') {
    throw 'Call-context metadata has an unexpected association policy.'
}
if ([System.IO.Path]::GetFullPath(
        (Get-RequiredString $metadata 'trace' 'metadata')) -ine $tracePath -or
    [System.IO.Path]::GetFullPath(
        (Get-RequiredString $metadata 'targets_tsv' 'metadata')) -ine
        $targetsSnapshotPath) {
    throw 'Call-context metadata paths do not identify the snapshotted inputs.'
}

$targetSpecifications = Read-CallContextTargetSpecifications `
    -Path $targetsSnapshotPath `
    -ModuleBase ([Convert]::ToUInt64($effectiveBase.Substring(2), 16))
$relationshipCounts = Assert-CallContextRelationships `
    -Targets @($targets) `
    -TargetSpecifications @($targetSpecifications) `
    -Events @($events) `
    -Invocations @($invocations) `
    -GapSummary $gapSummary `
    -Summary $summary `
    -ExpectedStackBytes $StackBytes `
    -Schema $callContextSchema
$replayBoundary = Assert-CallContextReplayBoundary `
    -Metadata $metadata `
    -Summary $summary `
    -Events @($events) `
    -RequestedFromArgument $From `
    -RequestedToArgument $To `
    -ExpectedStackBytes $StackBytes `
    -ExpectedEventLimit $EventLimit `
    -EventCount ([uint64]$events.Count) `
    -EntryEventCount $relationshipCounts.entryEventCount `
    -CallAndReturnEventCount $relationshipCounts.callAndReturnEventCount
$replayComplete = [bool]$replayBoundary.replayComplete
$expectationsPassed = Get-RequiredBoolean $summary 'expectations_passed' 'summary'
$pairingPassed = Get-RequiredBoolean $summary 'pairing_expectations_passed' 'summary'
$countersSane = Get-RequiredBoolean $summary 'replay_counters_sane' 'summary'
$instructionsExecuted = Get-RequiredUInt64 $summary 'instructions_executed' 'summary'
$stepsExecuted = Get-RequiredUInt64 $summary 'steps_executed' 'summary'
$recomputedCountersSane = $instructionsExecuted -le $stepsExecuted
if ($countersSane -ne $recomputedCountersSane) {
    throw 'Call-context replay-counter flag disagrees with its raw counters.'
}
$truncated = Get-RequiredBoolean $summary 'truncated' 'summary'
$callbackFailed = Get-RequiredBoolean $summary 'callback_failed' 'summary'
$orderingValid = Get-RequiredBoolean $summary 'ordering_valid' 'summary'
$contextsValid = Get-RequiredBoolean $summary 'contexts_valid' 'summary'
$collectorChecksPassed = Get-RequiredBoolean $summary 'collector_checks_passed' 'summary'
$recomputedCollectorChecks = (
    $replayComplete -and
    $relationshipCounts.targetExpectationsPassed -and
    $relationshipCounts.pairingExpectationsPassed -and
    $recomputedCountersSane -and
    -not $truncated -and
    -not $callbackFailed -and
    $relationshipCounts.eventOrderingValid -and
    $relationshipCounts.eventContextsValid
)
if ($collectorChecksPassed -ne $recomputedCollectorChecks) {
    throw 'Call-context collector-check flag disagrees with its component gates.'
}
$readyEligible = (
    $collectorExitCode -eq 0 -and
    $recomputedCollectorChecks -and
    $replayComplete -and
    $relationshipCounts.targetExpectationsPassed -and
    $relationshipCounts.pairingExpectationsPassed -and
    $recomputedCountersSane -and
    -not $truncated -and
    -not $callbackFailed -and
    $relationshipCounts.eventOrderingValid -and
    $relationshipCounts.eventContextsValid
)
if (($collectorExitCode -eq 0) -ne $readyEligible) {
    throw 'Collector exit code and parsed call-context readiness disagree.'
}

$contextFacts = Get-FileFacts $contextPath
$receipt = [ordered]@{
    schemaVersion = 'bea-ttd-call-context-receipt.v3'
    generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    startedAtUtc = $startedAt.ToString('o')
    finishedAtUtc = $finishedAt.ToString('o')
    elapsedSeconds = $stopwatch.Elapsed.TotalSeconds
    collectorExitCode = $collectorExitCode
    exitCode = $collectorExitCode
    readyEligible = $readyEligible
    trace = $traceBefore
    target = [ordered]@{
        path = $targetBefore.path
        bytes = $targetBefore.bytes
        sha256 = $targetBefore.sha256
        lastWriteUtc = $targetBefore.lastWriteUtc
        pe = $targetPe
    }
    targetsSource = $targetsSourceFacts
    targetsSnapshot = $targetsFacts
    collector = $collectorFacts
    replayRuntime = [ordered]@{
        version = [string]$buildReceipt.runtime.version
        replay = $replayFacts
        replayCpu = $replayCpuFacts
    }
    buildReceipt = $buildReceiptFacts
    invocation = [ordered]@{
        moduleName = $ModuleName
        expectedBase = $effectiveBase
        from = $From
        to = $To
        stackBytes = $StackBytes
        eventLimit = $EventLimit
        replayMode = 'sequential-all-segments'
    }
    callContext = [ordered]@{
        path = $contextFacts.path
        bytes = $contextFacts.bytes
        sha256 = $contextFacts.sha256
        schemaVersion = $callContextSchema
        lineCount = $lineCount
        targetCount = $targets.Count
        eventCount = $events.Count
        invocationCount = $invocations.Count
        callEntryPairCount = $relationshipCounts.callEntryPairCount
        validatedReturnCount = $relationshipCounts.validatedReturnCount
        rawReturnCount = $relationshipCounts.rawReturnCount
        orphanReturnCount = $relationshipCounts.orphanReturnCount
        gapFreeEnvelopeCount = $relationshipCounts.gapFreeEnvelopeCount
        associationBarrierCount = $relationshipCounts.associationBarrierCount
        finalAssociationEpoch = $relationshipCounts.finalAssociationEpoch
    }
    metadata = $metadata
    gapSummary = $gapSummary
    summary = $summary
}
[System.IO.File]::WriteAllText(
    $receiptPath,
    ($receipt | ConvertTo-Json -Depth 35) + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)
$receiptFacts = Get-FileFacts $receiptPath

$manifest = [ordered]@{
    schemaVersion = 'bea-ttd-call-context-manifest.v3'
    generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    status = if ($readyEligible) { 'READY' } else { 'BLOCKED' }
    collectorExitCode = $collectorExitCode
    exitCode = $collectorExitCode
    specimen = [ordered]@{
        traceSha256 = $traceBefore.sha256
        targetSha256 = $targetBefore.sha256
        targetsSha256 = $targetsFacts.sha256
        moduleName = $ModuleName
        expectedBase = $effectiveBase
        sizeOfImage = $targetPe.sizeOfImage
        timestamp = $targetPe.timestamp
        checksum = $targetPe.checksum
    }
    artifacts = [ordered]@{
        callContext = $contextFacts
        receipt = $receiptFacts
        targets = $targetsFacts
        collector = $collectorFacts
        replay = $replayFacts
        replayCpu = $replayCpuFacts
        buildReceipt = $buildReceiptFacts
    }
    proof = [ordered]@{
        replayComplete = $replayComplete
        expectationsPassed = $expectationsPassed
        pairingExpectationsPassed = $pairingPassed
        replayCountersSane = $countersSane
        orderingValid = $orderingValid
        contextsValid = $contextsValid
        truncated = $truncated
        callbackFailed = $callbackFailed
        collectorChecksPassed = $collectorChecksPassed
        counts = $relationshipCounts
    }
}
[System.IO.File]::WriteAllText(
    $manifestPath,
    ($manifest | ConvertTo-Json -Depth 30) + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)
$manifestFacts = Get-FileFacts $manifestPath

if ($readyEligible) {
    $ready = [ordered]@{
        schemaVersion = 'bea-ttd-call-context-ready.v3'
        manifest = $manifestFacts
        receiptSha256 = $receiptFacts.sha256
        callContextSha256 = $contextFacts.sha256
    }
    [System.IO.File]::WriteAllText(
        $readyPath,
        ($ready | ConvertTo-Json -Depth 10) + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
    $manifestReadback = Get-Content -Raw -LiteralPath $manifestPath |
        ConvertFrom-Json -Depth 30
    if ([string]$manifestReadback.status -cne 'READY' -or
        (Get-FileFacts $manifestPath).sha256 -cne $manifestFacts.sha256 -or
        (Get-FileFacts $receiptPath).sha256 -cne $receiptFacts.sha256 -or
        (Get-FileFacts $contextPath).sha256 -cne $contextFacts.sha256) {
        throw 'READY readback failed to reproduce the manifest-bound artifacts.'
    }
}

$receipt
if ($collectorExitCode -ne 0) {
    exit $collectorExitCode
}
