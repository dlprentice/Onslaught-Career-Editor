# SPDX-License-Identifier: GPL-3.0-or-later
#
# Offline query harness for a Time Travel Debugging trace.
#
# WHAT THIS IS FOR
# ----------------
# tools/ttd_record.ps1 records ONE retail run into a .run file. This script asks
# that file unlimited questions afterwards - no relaunch, no frontend driving, no
# synthetic input, no risk to the maintainer's session. Give it a trace and a list
# of debugger commands; get back a structured result and a log.
#
# It is deliberately built to be able to FAIL LOUDLY. A probe that cannot disagree
# with reality is worthless, and that failure mode has already burned this project.
# Concretely:
#   - it refuses to report success unless every exact harness marker appears
#     once and in order in one complete debugger transcript;
#   - -KnownAnswer checks PE-header compatibility: four fields exposed at the
#     caller-selected module base must match the image on disk. This does NOT
#     identify the complete image or prove that a query sees runtime-written
#     memory; use a dynamic positive control for that;
#   - -NegativeControl additionally asserts that a query for something that does
#     NOT exist is reported as absent. An instrument that answers everything
#     affirmatively is broken, and this catches that.
#
# USAGE
#   pwsh -NoProfile -File tools\ttd_query.ps1 -Trace G:\bea-ttd\lvl100\lvl100.run `
#        -Commands '!tt 0', 'lm m BEA', 'dx @$curprocess.TTD.Lifetime'
#
#   pwsh -NoProfile -File tools\ttd_query.ps1 -Trace ... -KnownAnswer -NegativeControl
#
# NOTE ON MODES
#   -Trace accepts any file the debugger can open with -z. That is normally a TTD
#   .run file; a crash dump also works and is how the non-TTD half of this harness
#   was validated on 2026-07-27 while TTD recording was blocked on elevation.
#   Pass -AllowNonTraceTarget to use a non-.run file deliberately.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Trace,

    # Debugger commands, run in order, between the sentinel markers.
    [string[]]$Commands = @(),

    # A file of debugger commands (one per line); appended after -Commands.
    [string]$CommandFile,

    # Where the generated command script, log and result JSON go.
    [string]$OutDir,

    [int]$TimeoutSeconds = 900,

    # Cross-check the trace against the PE header of this file, read from disk.
    # Defaults to the copied pristine target.
    [string]$KnownAnswerImage = "$PSScriptRoot\..\local-lab\safe-copy-bea-pristine\BEA.exe",
    [string]$KnownAnswerModule = 'BEA',
    # Load address to read the PE header from. Defaults to the image's own preferred
    # ImageBase, which is correct for BEA.exe (a 2003 binary with no DYNAMICBASE -
    # the whole RE corpus's raw VAs depend on it loading at 0x400000). Pass this
    # explicitly for any module that is relocated by ASLR.
    [uint32]$KnownAnswerBase = 0,
    [switch]$KnownAnswer,
    [switch]$NegativeControl,

    [switch]$AllowNonTraceTarget,

    # Optional explicit debugger path. The normal path is auto-detected; this is
    # useful for controlled harness validation and unusual WinDbg installations.
    [string]$CdbPath,

    # Print the generated command script and the debugger command line; run nothing.
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$BEGIN = '=== TTDQUERY BEGIN ==='
$BODYEND = '=== TTDQUERY OUTPUT END ==='
$END   = '=== TTDQUERY COMPLETE ==='
$KABEG = '=== KNOWNANSWER BEGIN ==='
$NCBEG = '=== NEGCONTROL BEGIN ==='
$ABSENT_SENTINEL = 'NEGCONTROL-MODULE-THAT-CANNOT-EXIST'

if (-not (Test-Path -LiteralPath $Trace)) { throw "No such trace: $Trace" }
$Trace = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Trace).Path)
if (-not $AllowNonTraceTarget -and ([IO.Path]::GetExtension($Trace) -ine '.run')) {
    throw ("'$Trace' is not a .run trace. Pass -AllowNonTraceTarget if you mean to " +
           "open a dump or other -z target.")
}

if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path ([IO.Path]::GetDirectoryName($Trace)) ('query-' + (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss'))
}
$OutDir = [IO.Path]::GetFullPath($OutDir)
if (Test-Path -LiteralPath $OutDir) {
    throw "Query output already exists: $OutDir. Choose a fresh -OutDir; stale debugger artifacts are never reused."
}
$null = [IO.Directory]::CreateDirectory($OutDir)

$logPath = Join-Path $OutDir 'cdb.log'
$stdoutPath = Join-Path $OutDir 'cdb-stdout.txt'
$stderrPath = Join-Path $OutDir 'cdb-stderr.txt'
$cmdPath = Join-Path $OutDir 'commands.txt'
$resultPath = Join-Path $OutDir 'result.json'

# ------------------------------------------------------- read the PE from disk
# This is the independent route. Nothing here touches the debugger, the trace, or
# any Microsoft tool - it is a plain read of the file's own headers, so when it is
# compared against what the trace reports, the two answers are genuinely
# independent and CAN disagree.
function Get-PeFacts([string]$path) {
    $fs = [IO.File]::OpenRead($path)
    try {
        $br = New-Object IO.BinaryReader($fs)
        $fs.Position = 0x3C
        $peOff = $br.ReadInt32()
        $fs.Position = $peOff
        if ($br.ReadUInt32() -ne 0x00004550) { throw "Not a PE: $path" }
        $machine = $br.ReadUInt16()
        $null = $br.ReadUInt16()                  # NumberOfSections
        $timeDateStamp = $br.ReadUInt32()
        $null = $br.ReadUInt32(); $null = $br.ReadUInt32()
        $optSize = $br.ReadUInt16(); $null = $br.ReadUInt16()
        $optStart = $fs.Position
        $magic = $br.ReadUInt16()                 # 0x10b PE32
        $fs.Position = $optStart + 0x1C           # PE32 ImageBase
        $imageBase = $br.ReadUInt32()
        $fs.Position = $optStart + 0x38           # PE32 SizeOfImage
        $sizeOfImage = $br.ReadUInt32()
        [pscustomobject]@{
            Path = $path; Machine = $machine; Magic = $magic
            TimeDateStamp = $timeDateStamp; ImageBase = $imageBase
            SizeOfImage = $sizeOfImage; OptionalHeaderSize = $optSize
            Sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
        }
    } finally { $fs.Dispose() }
}

$pe = $null
if ($KnownAnswer) {
    $KnownAnswerImage = [IO.Path]::GetFullPath($KnownAnswerImage)
    if (-not (Test-Path -LiteralPath $KnownAnswerImage)) {
        throw "-KnownAnswer needs an image to cross-check against; '$KnownAnswerImage' does not exist."
    }
    $pe = Get-PeFacts $KnownAnswerImage
}

# ------------------------------------------------------- build command script
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('.symopt+ 0x40')                        # SYMOPT_LOAD_ANYTHING
$lines.Add('.echo LOADING TTD EXTENSION')

# The TTD replay/analysis extensions. cdb normally auto-loads them for a .run, but
# loading them explicitly - and then printing .chain - makes a failure visible in
# the log instead of surfacing later as an unexplained "command not found".
$extCandidates = @()
Get-ChildItem 'C:\Program Files\WindowsApps' -Directory -Filter 'Microsoft.WinDbg_*_x64__8wekyb3d8bbwe' -ErrorAction SilentlyContinue |
    ForEach-Object {
        $extCandidates += (Join-Path $_.FullName 'x86\ttd\TTDAnalyze.dll')
        $extCandidates += (Join-Path $_.FullName 'x86\ttd\TtdExt.dll')
    }
$extCandidates += 'G:\bea-ttd\ttd-x86\TTDAnalyze.dll'
$extCandidates += 'G:\bea-ttd\ttd-x86\TtdExt.dll'
foreach ($e in ($extCandidates | Select-Object -Unique)) {
    if (Test-Path -LiteralPath $e) { $lines.Add('.load ' + ($e -replace '\\', '\\')) }
}
$lines.Add('.chain')
$lines.Add(".echo $BEGIN")
foreach ($c in $Commands) { $lines.Add($c) }
if ($CommandFile) {
    if (-not (Test-Path -LiteralPath $CommandFile)) { throw "No such command file: $CommandFile" }
    foreach ($c in (Get-Content -LiteralPath $CommandFile)) {
        if (-not [string]::IsNullOrWhiteSpace($c)) { $lines.Add($c) }
    }
}
$lines.Add(".echo $BODYEND")

if ($KnownAnswer) {
    # Read the PE header OUT OF THE RECORDED PROCESS MEMORY. This needs no symbols
    # and no extension, and it is what makes the check falsifiable: the bytes come
    # from the trace, the comparison values come from the file on disk, and the two
    # routes share nothing. The PE signature check proves real memory was read
    # rather than zeroes.
    $base = if ($PSBoundParameters.ContainsKey('KnownAnswerBase') -and $KnownAnswerBase) {
        [uint32]$KnownAnswerBase } else { $pe.ImageBase }
    $lines.Add(".echo $KABEG")
    $lines.Add("lm m $KnownAnswerModule")
    $lines.Add(('r $t0 = 0x{0:x}' -f $base))
    $lines.Add('r $t1 = @$t0 + dwo(@$t0+0x3c)')
    $lines.Add('.printf "KA_SIG %08x\n", dwo(@$t1)')
    $lines.Add('.printf "KA_TIMESTAMP %08x\n", dwo(@$t1+8)')
    $lines.Add('.printf "KA_IMAGEBASE %08x\n", dwo(@$t1+0x34)')
    $lines.Add('.printf "KA_SIZEOFIMAGE %08x\n", dwo(@$t1+0x50)')
}
if ($NegativeControl) {
    $lines.Add(".echo $NCBEG")
    $lines.Add("lm m $ABSENT_SENTINEL")
}
$lines.Add(".echo $END")
$lines.Add('q')
($lines -join "`n") | Set-Content -LiteralPath $cmdPath -Encoding ascii

$cdb =
    if ([string]::IsNullOrWhiteSpace($CdbPath)) {
        & (Join-Path $PSScriptRoot 'get_cdb_path.ps1') -AsLiteral
    }
    else {
        [IO.Path]::GetFullPath($CdbPath)
    }
if (-not (Test-Path -LiteralPath $cdb -PathType Leaf)) {
    throw "No such debugger executable: $cdb"
}
$cdbArgs = @('-z', $Trace, '-logo', $logPath, '-cf', $cmdPath)
$preview = ('& "{0}" {1}' -f $cdb, (($cdbArgs | ForEach-Object {
    if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ } }) -join ' '))

if ($DryRun) {
    Write-Host "--- command script ($cmdPath) ---"
    Get-Content -LiteralPath $cmdPath | Write-Host
    Write-Host "--- debugger command line ---"
    Write-Host $preview
    return
}

$traceBeforeQuery = Get-Item -LiteralPath $Trace
$traceSha256Before = (
    Get-FileHash -LiteralPath $Trace -Algorithm SHA256
).Hash

$env:_NT_SYMBOL_PATH = ''
$startInfo = [Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $cdb
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
foreach ($argument in $cdbArgs) {
    $startInfo.ArgumentList.Add([string]$argument)
}
$proc = [Diagnostics.Process]::new()
$proc.StartInfo = $startInfo
$stdoutStream = $null
$stderrStream = $null
$stdoutCopy = $null
$stderrCopy = $null
$timedOut = $false
$processStarted = $false
try {
    if (-not $proc.Start()) {
        throw "Debugger process did not start: $cdb"
    }
    $processStarted = $true
    $stdoutStream = [IO.File]::Create($stdoutPath)
    $stderrStream = [IO.File]::Create($stderrPath)
    $stdoutCopy = $proc.StandardOutput.BaseStream.CopyToAsync($stdoutStream)
    $stderrCopy = $proc.StandardError.BaseStream.CopyToAsync($stderrStream)
    if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
        $timedOut = $true
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit(10000) | Out-Null
    }
}
finally {
    if ($processStarted -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit(10000) | Out-Null
    }
    if ($stdoutCopy) { $stdoutCopy.GetAwaiter().GetResult() }
    if ($stderrCopy) { $stderrCopy.GetAwaiter().GetResult() }
    if ($stdoutStream) { $stdoutStream.Dispose() }
    if ($stderrStream) { $stderrStream.Dispose() }
}

$channels = [ordered]@{}
foreach ($entry in @(
    [pscustomobject]@{ Name = 'log'; Path = $logPath }
    [pscustomobject]@{ Name = 'stdout'; Path = $stdoutPath }
    [pscustomobject]@{ Name = 'stderr'; Path = $stderrPath }
)) {
    $channels[$entry.Name] =
        if (Test-Path -LiteralPath $entry.Path) {
            [string](Get-Content -LiteralPath $entry.Path -Raw -ErrorAction SilentlyContinue)
        } else { '' }
}

# Parse one complete primary transcript rather than concatenating the duplicated
# log and stdout streams. Prefer a stream carrying the completion sentinel, then
# the longer stream. Diagnostics are checked across all three channels below.
$primaryChannels = @(
    [pscustomobject]@{ Name = 'log'; Text = $channels.log }
    [pscustomobject]@{ Name = 'stdout'; Text = $channels.stdout }
) | Sort-Object `
    @{ Expression = { $_.Text -match [regex]::Escape($END) }; Descending = $true },
    @{ Expression = { $_.Text.Length }; Descending = $true }
$primaryChannel = $primaryChannels | Select-Object -First 1
$text = $primaryChannel.Text
$all = @($text -split "`r?`n")
$diagnosticText = (($channels.GetEnumerator() | ForEach-Object {
    "=== $($_.Key) ===`n$($_.Value)"
}) -join "`n")
$diagnosticLines = @($diagnosticText -split "`r?`n")

function ExactMarkerIndices([string[]]$src, [string]$marker) {
    $indices = [System.Collections.Generic.List[int]]::new()
    for ($index = 0; $index -lt $src.Length; $index++) {
        # CDB echoes `.echo <marker>` at its prompt before emitting <marker>.
        # Only the exact emitted line is part of the harness protocol.
        if ($src[$index] -ceq $marker) {
            $indices.Add($index)
        }
    }
    return $indices.ToArray()
}

$problems = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$beginIndices = @(ExactMarkerIndices $all $BEGIN)
$bodyEndIndices = @(ExactMarkerIndices $all $BODYEND)
$endIndices = @(ExactMarkerIndices $all $END)
foreach ($marker in @(
    [pscustomobject]@{
        Name = 'BEGIN'; Indices = $beginIndices
        Missing = 'BEGIN sentinel never appeared - the debugger did not reach the commands'
    }
    [pscustomobject]@{
        Name = 'OUTPUT-END'; Indices = $bodyEndIndices
        Missing = 'OUTPUT-END sentinel never appeared - the query output is incomplete'
    }
    [pscustomobject]@{
        Name = 'END'; Indices = $endIndices
        Missing = 'END sentinel never appeared - the command script did not complete'
    }
)) {
    if (@($marker.Indices).Count -eq 0) {
        $problems.Add($marker.Missing)
    }
    elseif (@($marker.Indices).Count -ne 1) {
        $problems.Add("$($marker.Name) sentinel appeared $(@($marker.Indices).Count) times - the debugger transcript is ambiguous")
    }
}
$mainMarkersValid =
    @($beginIndices).Count -eq 1 -and
    @($bodyEndIndices).Count -eq 1 -and
    @($endIndices).Count -eq 1
if (
    $mainMarkersValid -and
    -not (
        $beginIndices[0] -lt $bodyEndIndices[0] -and
        $bodyEndIndices[0] -lt $endIndices[0]
    )
) {
    $problems.Add('query sentinels appeared out of order - expected BEGIN, OUTPUT-END, COMPLETE')
    $mainMarkersValid = $false
}
$body =
    if (-not $mainMarkersValid -or $bodyEndIndices[0] -eq $beginIndices[0] + 1) {
        @()
    }
    else {
        @($all[($beginIndices[0] + 1)..($bodyEndIndices[0] - 1)])
    }

$traceAfterQuery = Get-Item -LiteralPath $Trace
$traceSha256After = (
    Get-FileHash -LiteralPath $Trace -Algorithm SHA256
).Hash
if (
    $traceBeforeQuery.Length -ne $traceAfterQuery.Length -or
    $traceBeforeQuery.LastWriteTimeUtc -ne $traceAfterQuery.LastWriteTimeUtc -or
    $traceSha256Before -cne $traceSha256After
) {
    $problems.Add('trace changed while the offline debugger query was running')
}
if ($timedOut) { $problems.Add("debugger timed out after $TimeoutSeconds s") }
if ($proc.ExitCode -ne 0) { $problems.Add("debugger exited with code $($proc.ExitCode)") }
foreach ($pat in @('Could not open', 'is not a crash dump',
                   'Unrecognized dump', 'File not found',
                   'Syntax error in', 'Error: Unable to bind name',
                   "Couldn't resolve error",
                   'pass count must be preceeded by whitespace error in')) {
    if ($diagnosticLines | Where-Object { $_ -like "*$pat*" }) {
        $problems.Add("debugger reported: $pat")
    }
}
$imageLoadPattern = '^Unable to load image (?<path>.+), Win32 error (?<code>\S+)\s*$'
$knownAnswerLeaf = [IO.Path]::GetFileName($KnownAnswerImage)
$imageLoadRows = @(
    $diagnosticLines |
        Where-Object { $_ -match $imageLoadPattern } |
        Select-Object -Unique
)
foreach ($row in $imageLoadRows) {
    $match = [regex]::Match($row, $imageLoadPattern)
    $leaf = [IO.Path]::GetFileName($match.Groups['path'].Value)
    if ($leaf -ieq $knownAnswerLeaf) {
        $problems.Add("debugger could not load known-answer image: $row")
    }
    else {
        # TTD replays commonly lack a local image for a recorded system DLL. That
        # prevents symbols for that DLL, but does not invalidate a BEA query whose
        # own bytes and dynamic calls are independently checked below.
        $warnings.Add("debugger could not load unrelated image: $row")
    }
}
$unclassifiedWin32Rows = @(
    $diagnosticLines |
        Where-Object {
            $_ -like '*Win32 error*' -and
            $_ -notmatch $imageLoadPattern
        } |
        Select-Object -Unique
)
foreach ($row in $unclassifiedWin32Rows) {
    $problems.Add("debugger reported an unclassified Win32 error: $row")
}

# ------------------------------------------------- known-answer cross-check
$knownAnswerResult = $null
if ($KnownAnswer) {
    $knownAnswerIndices = @(ExactMarkerIndices $all $KABEG)
    if (@($knownAnswerIndices).Count -eq 0) {
        $problems.Add('KNOWN-ANSWER sentinel never appeared - the PE-header compatibility check did not run')
    }
    elseif (@($knownAnswerIndices).Count -ne 1) {
        $problems.Add("KNOWN-ANSWER sentinel appeared $(@($knownAnswerIndices).Count) times - the debugger transcript is ambiguous")
    }
    $knownAnswerEndIndices =
        if ($NegativeControl) { @(ExactMarkerIndices $all $NCBEG) }
        else { $endIndices }
    $knownAnswerMarkersValid =
        $mainMarkersValid -and
        @($knownAnswerIndices).Count -eq 1 -and
        @($knownAnswerEndIndices).Count -eq 1 -and
        $bodyEndIndices[0] -lt $knownAnswerIndices[0] -and
        $knownAnswerIndices[0] -lt $knownAnswerEndIndices[0] -and
        $knownAnswerEndIndices[0] -le $endIndices[0]
    if (
            @($knownAnswerIndices).Count -eq 1 -and
            @($knownAnswerEndIndices).Count -eq 1 -and
        -not $knownAnswerMarkersValid
    ) {
        $problems.Add('KNOWN-ANSWER sentinel appeared out of order')
    }
    $ka =
        if (
            $knownAnswerMarkersValid -and
            $knownAnswerEndIndices[0] -gt $knownAnswerIndices[0] + 1
        ) {
            @($all[($knownAnswerIndices[0] + 1)..($knownAnswerEndIndices[0] - 1)])
        }
        else { @() }
    # Drop cdb's own prompt echo of each command; otherwise the harness reads its
    # own question back as if it were an answer.
    $ka = @($ka | Where-Object { $_ -notmatch '^\s*\d+:\d+(:x86)?>' })
    $joined = ($ka -join "`n")
    function Val([string]$k) {
        if ($joined -match ("(?m)^" + $k + "\s+([0-9A-Fa-f]{8})\s*$")) { return [Convert]::ToUInt32($Matches[1], 16) }
        return $null
    }
    # Windows rewrites OptionalHeader.ImageBase in memory to the ACTUAL load address
    # when a module is relocated, so the in-memory field must be compared against the
    # base we read from, not against the file's preferred base. (Measured 2026-07-27:
    # cmd.exe, preferred 0x00400000, loaded and reporting 0x00940000.) For BEA.exe
    # the two coincide, and `relocated` below says so explicitly.
    $effBase = if ($KnownAnswerBase) { [uint32]$KnownAnswerBase } else { $pe.ImageBase }
    $checks = @(
        [pscustomobject]@{ Name = 'PE signature';   FromDisk = [uint32]0x00004550;  FromTrace = (Val 'KA_SIG') }
        [pscustomobject]@{ Name = 'TimeDateStamp';  FromDisk = $pe.TimeDateStamp;   FromTrace = (Val 'KA_TIMESTAMP') }
        [pscustomobject]@{ Name = 'SizeOfImage';    FromDisk = $pe.SizeOfImage;     FromTrace = (Val 'KA_SIZEOFIMAGE') }
        [pscustomobject]@{ Name = 'ImageBase@load'; FromDisk = $effBase;            FromTrace = (Val 'KA_IMAGEBASE') }
    )
    foreach ($c in $checks) {
        $c | Add-Member -NotePropertyName Agree -NotePropertyValue (
            ($null -ne $c.FromTrace) -and ([uint32]$c.FromDisk -eq [uint32]$c.FromTrace))
        if (-not $c.Agree) {
            $problems.Add(("KNOWN-ANSWER MISMATCH {0}: disk=0x{1:X8} trace={2}" -f
                $c.Name, $c.FromDisk, $(if ($null -eq $c.FromTrace) { '<not reported>' } else { ('0x{0:X8}' -f $c.FromTrace) })))
        }
    }
    $knownAnswerResult = [pscustomobject]@{
        Image = $pe.Path; Sha256 = $pe.Sha256; Module = $KnownAnswerModule
        ReadAtBase = ('0x{0:X8}' -f $effBase)
        PreferredImageBaseOnDisk = ('0x{0:X8}' -f $pe.ImageBase)
        Relocated = ($effBase -ne $pe.ImageBase)
        Checks = $checks
        AllAgree = (@($checks | Where-Object { -not $_.Agree }).Count -eq 0)
    }
}

# ------------------------------------------------------- negative control
$negativeControlResult = $null
if ($NegativeControl) {
    $negativeControlIndices = @(ExactMarkerIndices $all $NCBEG)
    $negativeControlMarkersValid =
        $mainMarkersValid -and
        @($negativeControlIndices).Count -eq 1 -and
        $bodyEndIndices[0] -lt $negativeControlIndices[0] -and
        $negativeControlIndices[0] -lt $endIndices[0] -and
        (
            -not $KnownAnswer -or
            (
                @($knownAnswerIndices).Count -eq 1 -and
                $knownAnswerIndices[0] -lt $negativeControlIndices[0]
            )
        )
    if (@($negativeControlIndices).Count -eq 0) {
        $problems.Add('NEGATIVE-CONTROL sentinel never appeared - the adverse query did not run')
    }
    elseif (@($negativeControlIndices).Count -ne 1) {
        $problems.Add("NEGATIVE-CONTROL sentinel appeared $(@($negativeControlIndices).Count) times - the debugger transcript is ambiguous")
    }
    elseif (-not $negativeControlMarkersValid) {
        $problems.Add('NEGATIVE-CONTROL sentinel appeared out of order')
    }
    $nc =
        if (
            $negativeControlMarkersValid -and
            $endIndices[0] -gt $negativeControlIndices[0] + 1
        ) {
            @($all[($negativeControlIndices[0] + 1)..($endIndices[0] - 1)])
        }
        else { @() }
    # Same prompt-echo trap as above: cdb prints "0:000> lm m <sentinel>" before it
    # answers, so an unfiltered search finds the harness's own question.
    $nc = @($nc | Where-Object { $_ -notmatch '^\s*\d+:\d+(:x86)?>' })
    $ncText = ($nc -join "`n")
    # An honest debugger reports nothing (or an explicit "no matches") for a module
    # that does not exist. Match an actual `lm` module row, not the sentinel inside
    # an error or an unrelated warning elsewhere in the same section.
    $moduleRowPattern =
        '^\s*[0-9A-Fa-f`?]+\s+[0-9A-Fa-f`?]+\s+' +
        [regex]::Escape($ABSENT_SENTINEL) +
        '(?:\s|$)'
    $claimedRows = @($nc | Where-Object { $_ -match $moduleRowPattern })
    $claimedMatch = @($claimedRows).Count -gt 0
    $negativeControlResult = [pscustomobject]@{
        Sentinel = $ABSENT_SENTINEL
        Output = $ncText
        Passed = ($negativeControlMarkersValid -and -not $claimedMatch)
    }
    if ($claimedMatch) { $problems.Add('NEGATIVE CONTROL FAILED - the debugger reported a match for a module that cannot exist') }
}

$result = [pscustomobject]@{
    schemaVersion   = 'ttd-query-result.v3'
    trace           = $Trace
    traceBytes      = $traceBeforeQuery.Length
    traceSha256     = $traceSha256Before
    cdb             = $cdb
    commandScript   = $cmdPath
    logPath         = $logPath
    stdoutPath      = $stdoutPath
    stderrPath      = $stderrPath
    primaryChannel  = $primaryChannel.Name
    exitCode        = $proc.ExitCode
    timedOut        = $timedOut
    ok              = ($problems.Count -eq 0)
    problems        = @($problems)
    warnings        = @($warnings)
    knownAnswer     = $knownAnswerResult
    negativeControl = $negativeControlResult
    output          = @($body | Where-Object { $null -ne $_ })
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8

if ($result.ok) { Write-Host "OK  - $(@($result.output).Count) output lines; $resultPath" }
else { Write-Host ("FAIL - " + ($problems -join '; ')) -ForegroundColor Red }
$result
if (-not $result.ok) { exit 1 }
