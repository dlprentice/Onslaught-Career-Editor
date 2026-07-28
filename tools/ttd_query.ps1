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
#   - it refuses to report success unless BOTH sentinel markers appear in the log;
#   - -KnownAnswer cross-checks what the TRACE says about the target image against
#     what the PE HEADER ON DISK says, read by a completely independent route
#     (.NET file parsing). Disagreement is a hard failure, not a warning;
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

    # Print the generated command script and the debugger command line; run nothing.
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$BEGIN = '=== TTDQUERY BEGIN ==='
$END   = '=== TTDQUERY END ==='
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
$lines.Add(".echo $END")

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
$lines.Add('q')
($lines -join "`n") | Set-Content -LiteralPath $cmdPath -Encoding ascii

$cdb = & (Join-Path $PSScriptRoot 'get_cdb_path.ps1') -AsLiteral
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

$env:_NT_SYMBOL_PATH = ''
$proc = Start-Process -FilePath $cdb -ArgumentList $cdbArgs -PassThru -NoNewWindow `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
$timedOut = $false
if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
    $timedOut = $true
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    $proc.WaitForExit(10000) | Out-Null
}

$text = ''
foreach ($p in @($logPath, $stdoutPath)) {
    if (Test-Path -LiteralPath $p) {
        $t = Get-Content -LiteralPath $p -Raw -ErrorAction SilentlyContinue
        if ($t -and $t.Length -gt $text.Length) { $text = $t }
    }
}
$all = @($text -split "`r?`n")

function Slice([string[]]$src, [string]$from, [string]$to) {
    $i = [array]::FindIndex($src, [Predicate[string]] { param($x) $x -like "*$from*" })
    if ($i -lt 0) { return $null }
    $j = if ($to) { [array]::FindIndex($src, $i + 1, [Predicate[string]] { param($x) $x -like "*$to*" }) } else { -1 }
    if ($j -lt 0) { $j = $src.Length }
    return $src[($i + 1)..([Math]::Max($i + 1, $j - 1))]
}

$body = Slice $all $BEGIN $END
$sawBegin = $all -match [regex]::Escape($BEGIN)
$sawEnd = $all -match [regex]::Escape($END)

$problems = [System.Collections.Generic.List[string]]::new()
if ($timedOut) { $problems.Add("debugger timed out after $TimeoutSeconds s") }
if (-not $sawBegin) { $problems.Add('BEGIN sentinel never appeared - the debugger did not reach the commands') }
if (-not $sawEnd) { $problems.Add('END sentinel never appeared - the command script did not complete') }
foreach ($pat in @('Could not open', 'is not a crash dump', 'Unable to load image',
                   'Unrecognized dump', 'File not found', 'Win32 error')) {
    if ($all | Where-Object { $_ -like "*$pat*" }) { $problems.Add("debugger reported: $pat") }
}

# ------------------------------------------------- known-answer cross-check
$knownAnswerResult = $null
if ($KnownAnswer) {
    $ka = Slice $all $KABEG $NCBEG
    if (-not $ka) { $ka = Slice $all $KABEG $null }
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
    $nc = Slice $all $NCBEG $null
    # Same prompt-echo trap as above: cdb prints "0:000> lm m <sentinel>" before it
    # answers, so an unfiltered search finds the harness's own question.
    $nc = @($nc | Where-Object { $_ -notmatch '^\s*\d+:\d+(:x86)?>' })
    $ncText = ($nc -join "`n")
    # An honest debugger reports nothing (or an explicit "no matches") for a module
    # that does not exist. If it echoes a match, the instrument is agreeing with a
    # question that has no true answer, and every other answer becomes suspect.
    $claimedMatch = $ncText -match [regex]::Escape($ABSENT_SENTINEL) -and
                    $ncText -notmatch 'Unable|no matches|not found|Couldn'
    $negativeControlResult = [pscustomobject]@{
        Sentinel = $ABSENT_SENTINEL
        Output = $ncText
        Passed = (-not $claimedMatch)
    }
    if ($claimedMatch) { $problems.Add('NEGATIVE CONTROL FAILED - the debugger reported a match for a module that cannot exist') }
}

$result = [pscustomobject]@{
    schemaVersion   = 'ttd-query-result.v1'
    trace           = $Trace
    traceBytes      = (Get-Item -LiteralPath $Trace).Length
    cdb             = $cdb
    commandScript   = $cmdPath
    logPath         = $logPath
    exitCode        = $proc.ExitCode
    timedOut        = $timedOut
    ok              = ($problems.Count -eq 0)
    problems        = @($problems)
    knownAnswer     = $knownAnswerResult
    negativeControl = $negativeControlResult
    output          = @($body)
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8

if ($result.ok) { Write-Host "OK  - $($result.output.Count) output lines; $resultPath" }
else { Write-Host ("FAIL - " + ($problems -join '; ')) -ForegroundColor Red }
$result
