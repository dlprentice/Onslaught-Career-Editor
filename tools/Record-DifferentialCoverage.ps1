[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$')]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [ValidateSet('baseline', 'action')]
    [string]$Role,

    [Parameter(Mandatory = $true)]
    [string]$TargetExe,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedTargetSha256,

    [ValidateSet('generic.v1', 'options-main-to-options.v1')]
    [string]$Scenario = 'generic.v1',

    [ValidateSet('', 'C1', 'C2')]
    [string]$CampaignId = '',

    [ValidateRange(0, 6)]
    [int]$SequenceIndex = 0,

    [string]$Drrun =
        'G:\bea-parity-lab\tools\DynamoRIO-Windows-11.3.0\' +
        'DynamoRIO-Windows-11.3.0-1\bin32\drrun.exe',

    [Parameter(Mandatory = $true)]
    [string]$ExpectedDrrunSha256,

    [string]$OutputRoot = 'G:\bea-parity-lab\captures',

    [string[]]$GameArguments = @('-skipfmv'),

    [ValidateRange(5, 300)]
    [int]$CaptureSeconds = 10,

    [ValidateRange(1, 299)]
    [int]$ActionDelaySeconds = 5,

    [string]$ActionSequence = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$optionsScenario = 'options-main-to-options.v1'
$optionsRolePatterns = @{
    C1 = @('baseline', 'action', 'action', 'baseline', 'baseline', 'action')
    C2 = @('action', 'baseline', 'baseline', 'action', 'action', 'baseline')
}
$optionsOrderTokens = @{
    C1 = @('B1', 'A1', 'A2', 'B2', 'B3', 'A3')
    C2 = @('A4', 'B4', 'B5', 'A5', 'A6', 'B6')
}

if ($Scenario -eq $optionsScenario) {
    if ([string]::IsNullOrWhiteSpace($CampaignId) -or
        $SequenceIndex -lt 1 -or $SequenceIndex -gt 6) {
        throw 'The Options scenario requires -CampaignId C1|C2 and -SequenceIndex 1..6.'
    }
    $expectedRole = $optionsRolePatterns[$CampaignId][$SequenceIndex - 1]
    if ($Role -cne $expectedRole) {
        throw (
            "Options $CampaignId sequence $SequenceIndex requires role " +
            "'$expectedRole', not '$Role'."
        )
    }
    if (-not [string]::IsNullOrWhiteSpace($ActionSequence)) {
        throw 'The Options scenario owns its exact input; do not pass -ActionSequence.'
    }
} else {
    if (-not [string]::IsNullOrWhiteSpace($CampaignId) -or $SequenceIndex -ne 0) {
        throw 'Campaign metadata is reserved for the Options scenario.'
    }
    if ($ActionDelaySeconds -ge $CaptureSeconds) {
        throw 'ActionDelaySeconds must be shorter than CaptureSeconds.'
    }
    if ($Role -eq 'action' -and [string]::IsNullOrWhiteSpace($ActionSequence)) {
        throw 'Generic action runs require one bounded ActionSequence.'
    }
    if ($Role -eq 'baseline' -and
        -not [string]::IsNullOrWhiteSpace($ActionSequence)) {
        throw 'Generic baseline runs refuse an ActionSequence.'
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

function Get-TextSha256 {
    param([Parameter(Mandatory = $true)][string]$Text)

    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
}

function Get-SaveCorpusFacts {
    param([Parameter(Mandatory = $true)][string]$Root)

    $fullRoot = [IO.Path]::GetFullPath($Root)
    if (-not (Test-Path -LiteralPath $fullRoot -PathType Container)) {
        throw "Save corpus directory does not exist: $fullRoot"
    }
    [string[]]$relativePaths = @(
        Get-ChildItem -LiteralPath $fullRoot -Recurse -File |
            ForEach-Object {
                [IO.Path]::GetRelativePath($fullRoot, $_.FullName).Replace('\', '/')
            }
    )
    [Array]::Sort($relativePaths, [StringComparer]::OrdinalIgnoreCase)
    $files = @(
        foreach ($relative in $relativePaths) {
            $item = Get-Item -LiteralPath (
                Join-Path $fullRoot $relative.Replace('/', '\')
            )
            [ordered]@{
                relativePath = $relative
                bytes = $item.Length
                sha256 = (
                    Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256
                ).Hash
                lastWriteUtc = $item.LastWriteTimeUtc.ToString('o')
            }
        }
    )
    $canonical = @(
        $files | ForEach-Object {
            "{0}`t{1}`t{2}`t{3}" -f
                $_.relativePath, $_.bytes, $_.sha256, $_.lastWriteUtc
        }
    ) -join "`n"
    [long]$totalBytes = 0
    foreach ($file in $files) {
        $totalBytes += [long]$file.bytes
    }
    return [ordered]@{
        root = $fullRoot
        fileCount = $files.Count
        totalBytes = $totalBytes
        aggregateSha256 = Get-TextSha256 -Text $canonical
        files = $files
    }
}

function Test-FileFactsEqual {
    param($Left, $Right)

    return (
        $Left.path -ceq $Right.path -and
        $Left.bytes -eq $Right.bytes -and
        $Left.sha256 -ceq $Right.sha256 -and
        $Left.lastWriteUtc -ceq $Right.lastWriteUtc
    )
}

function Test-CorpusFactsEqual {
    param($Left, $Right)

    return (
        $Left.root -ceq $Right.root -and
        $Left.fileCount -eq $Right.fileCount -and
        $Left.totalBytes -eq $Right.totalBytes -and
        $Left.aggregateSha256 -ceq $Right.aggregateSha256
    )
}

if (-not ('BeaDrcovNativeV2' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class BeaDrcovNativeV2
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(
        uint desiredAccess, bool inheritHandle, int processId);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool ReadProcessMemory(
        IntPtr process, IntPtr address, byte[] buffer, int size, out IntPtr read);

    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetExitCodeProcess(IntPtr process, out uint exitCode);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool GetClientRect(IntPtr window, out RECT rect);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool PostMessage(
        IntPtr window, uint message, UIntPtr wParam, UIntPtr lParam);

    public static int? ReadInt32(int processId, long address)
    {
        IntPtr process = OpenProcess(0x0010u | 0x0400u, false, processId);
        if (process == IntPtr.Zero)
            return null;
        try
        {
            byte[] buffer = new byte[4];
            IntPtr read;
            if (!ReadProcessMemory(
                    process, new IntPtr(address), buffer, buffer.Length, out read) ||
                read.ToInt64() != buffer.Length)
                return null;
            return BitConverter.ToInt32(buffer, 0);
        }
        finally
        {
            CloseHandle(process);
        }
    }

    public static int[] ClientSize(IntPtr window)
    {
        RECT rect;
        if (!GetClientRect(window, out rect))
            return null;
        return new int[] { rect.Right - rect.Left, rect.Bottom - rect.Top };
    }

    public static int? ProcessExitCode(IntPtr process)
    {
        uint exitCode;
        if (process == IntPtr.Zero || !GetExitCodeProcess(process, out exitCode))
            return null;
        return unchecked((int)exitCode);
    }

    public static bool PostMouseButton(
        IntPtr window, bool down, int clientX, int clientY)
    {
        uint message = down ? 0x0201u : 0x0202u;
        UIntPtr wParam = down ? new UIntPtr(1u) : UIntPtr.Zero;
        uint packed = ((uint)(ushort)clientY << 16) | (ushort)clientX;
        return PostMessage(window, message, wParam, new UIntPtr(packed));
    }
}
'@
}

function Wait-ForStablePage {
    param(
        [Parameter(Mandatory = $true)]$Process,
        [Parameter(Mandatory = $true)][long]$Address,
        [Parameter(Mandatory = $true)][int]$Expected,
        [ValidateRange(1, 90)][int]$TimeoutSeconds = 30,
        [ValidateRange(2, 10)][int]$RequiredSamples = 4
    )

    $samples = [Collections.Generic.List[object]]::new()
    $streak = 0
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        if ($Process.HasExited) {
            throw (
                "BEA exited while waiting for frontend page 0x{0:X}." -f $Expected
            )
        }
        $value = [BeaDrcovNativeV2]::ReadInt32($Process.Id, $Address)
        $samples.Add([ordered]@{
            atUtc = [DateTime]::UtcNow.ToString('o')
            value = if ($null -eq $value) { $null } else { [int]$value }
        })
        if ($null -ne $value -and [int]$value -eq $Expected) {
            $streak++
            if ($streak -ge $RequiredSamples) {
                return [ordered]@{
                    expected = $Expected
                    stable = $true
                    requiredSamples = $RequiredSamples
                    samples = @($samples)
                }
            }
        } else {
            $streak = 0
        }
        Start-Sleep -Milliseconds 125
    }
    $recent = @($samples | Select-Object -Last 12 | ForEach-Object {
        if ($null -eq $_.value) { 'null' } else { '0x{0:X}' -f $_.value }
    }) -join ', '
    throw (
        "Frontend page did not settle at 0x{0:X}; recent samples: {1}" -f
            $Expected, $recent
    )
}

function Invoke-BoundedWindowInput {
    param(
        [Parameter(Mandatory = $true)]$Process,
        [Parameter(Mandatory = $true)][string]$HwndHex,
        [Parameter(Mandatory = $true)][string]$Sequence,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][string]$ExpectedExecutable,
        [Parameter(Mandatory = $true)][string]$ExpectedWorkingDirectory,
        [switch]$RequireCursorVerification
    )

    $sender = Join-Path $PSScriptRoot 'send_game_window_input.ps1'
    $arguments = @(
        '-NoProfile', '-File', $sender,
        '-ProcessId', [string]$Process.Id,
        '-HwndHex', $HwndHex,
        '-Sequence', $Sequence,
        '-Transport', 'messages',
        '-AllowBackgroundWindowMessages',
        '-BackgroundWindowMessagesArm', 'ALLOW BACKGROUND BEA WINDOW MESSAGES',
        '-ExpectedExecutablePath', $ExpectedExecutable,
        '-ExpectedWorkingDirectory', $ExpectedWorkingDirectory
    )
    if ($RequireCursorVerification) {
        $arguments += '-VerifyCursorGlobals'
    }
    $text = & pwsh @arguments 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "Bounded target-window input failed: $text"
    }
    $payload = $text | ConvertFrom-Json
    if ($payload.status -cne 'sent' -or
        $payload.transport -cne 'messages' -or
        -not $payload.backgroundWindowMessagesAllowed -or
        [int]$payload.processId -ne $Process.Id -or
        $payload.selectedWindow.executablePath -ine $ExpectedExecutable -or
        $payload.selectedWindow.workingDirectory -ine $ExpectedWorkingDirectory) {
        throw 'Bounded input receipt does not identify the expected target/window route.'
    }
    if ($RequireCursorVerification) {
        $probe = @($payload.cursorProbes | Select-Object -Last 1)
        if ($probe.Count -ne 1 -or
            @($probe[0].matchedX).Count -eq 0 -or
            @($probe[0].matchedY).Count -eq 0) {
            throw 'The frontend cursor globals did not confirm the posted mouse move.'
        }
    }
    $json = ($payload | ConvertTo-Json -Depth 12) + [Environment]::NewLine
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json)
    $stream = [IO.File]::Open(
        $OutputPath,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    } finally {
        $stream.Dispose()
    }
    return [ordered]@{
        receipt = Get-FileFacts -Path $OutputPath
        payload = $payload
    }
}

function Invoke-VerifiedOptionsClick {
    param(
        [Parameter(Mandatory = $true)]$Process,
        [Parameter(Mandatory = $true)][IntPtr]$Window,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    $pageAddress = 0x0089D950
    $cursorXAddress = 0x0089BDA8
    $cursorYAddress = 0x0089BDA4
    $mouseGateAddress = 0x0089BDF0
    $pageBefore = [BeaDrcovNativeV2]::ReadInt32($Process.Id, $pageAddress)
    $cursorX = [BeaDrcovNativeV2]::ReadInt32($Process.Id, $cursorXAddress)
    $cursorY = [BeaDrcovNativeV2]::ReadInt32($Process.Id, $cursorYAddress)
    $mouseGate = [BeaDrcovNativeV2]::ReadInt32($Process.Id, $mouseGateAddress)
    if ($pageBefore -ne 0 -or $cursorX -ne 219 -or $cursorY -ne 404 -or
        $mouseGate -ne 0) {
        throw (
            'Options click precondition changed: page={0}, cursor={1},{2}, gate={3}.' -f
                $pageBefore, $cursorX, $cursorY, $mouseGate
        )
    }
    $down = [BeaDrcovNativeV2]::PostMouseButton($Window, $true, 219, 404)
    Start-Sleep -Milliseconds 60
    $up = [BeaDrcovNativeV2]::PostMouseButton($Window, $false, 219, 404)
    if (-not $down -or -not $up) {
        throw "Failed to post the isolated Options button pair: down=$down up=$up."
    }
    $payload = [ordered]@{
        schemaVersion = 'bea-options-click-receipt.v1'
        generatedAtUtc = [DateTime]::UtcNow.ToString('o')
        processId = $Process.Id
        hwndHex = '0x{0:X}' -f $Window.ToInt64()
        transport = 'PostMessage-button-only'
        precondition = [ordered]@{
            page = $pageBefore
            cursorX = $cursorX
            cursorY = $cursorY
            mouseGate = $mouseGate
        }
        action = [ordered]@{
            clientX = 219
            clientY = 404
            mouseMovePosted = $false
            buttonDownPosted = $down
            buttonUpPosted = $up
        }
    }
    $json = ($payload | ConvertTo-Json -Depth 8) + [Environment]::NewLine
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json)
    $stream = [IO.File]::Open(
        $OutputPath,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    } finally {
        $stream.Dispose()
    }
    return [ordered]@{
        receipt = Get-FileFacts -Path $OutputPath
        payload = $payload
    }
}

function Get-MatchingProcesses {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][DateTime]$StartedAt
    )

    return @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object {
                try {
                    $_.Path -ieq $Executable -and
                    $_.StartTime.ToUniversalTime() -ge $StartedAt.AddSeconds(-1)
                } catch {
                    $false
                }
            }
    )
}

function Test-ProcessDescendsFrom {
    param(
        [Parameter(Mandatory = $true)][int]$ProcessId,
        [Parameter(Mandatory = $true)][int]$AncestorProcessId
    )

    $parents = @{}
    foreach ($row in Get-CimInstance Win32_Process -ErrorAction Stop) {
        $parents[[int]$row.ProcessId] = [int]$row.ParentProcessId
    }
    $current = $ProcessId
    $visited = [Collections.Generic.HashSet[int]]::new()
    while ($current -gt 0 -and $visited.Add($current)) {
        if ($current -eq $AncestorProcessId) {
            return $true
        }
        if (-not $parents.ContainsKey($current)) {
            return $false
        }
        $current = [int]$parents[$current]
    }
    return $false
}

$target = (Resolve-Path -LiteralPath $TargetExe).Path
$drrunPath = (Resolve-Path -LiteralPath $Drrun).Path
$targetLower = $target.ToLowerInvariant()
if ([IO.Path]::GetFileName($target) -ine 'BEA.exe') {
    throw "Expected a copied BEA.exe target: $target"
}
if ($targetLower.Contains('\steamapps\') -or
    $targetLower.StartsWith(
        [Environment]::GetFolderPath('ProgramFiles').ToLowerInvariant()
    ) -or
    $targetLower.StartsWith(
        [Environment]::GetFolderPath('ProgramFilesX86').ToLowerInvariant()
    )) {
    throw 'Refusing an installed or Program Files target. Use a copied BEA directory.'
}
$targetDirectory = Split-Path -Parent $target
$senderPath = Join-Path $PSScriptRoot 'send_game_window_input.ps1'
$defaultOptionsPath = Join-Path $targetDirectory 'defaultoptions.bea'
$saveRoot = Join-Path $targetDirectory 'savegames'
foreach ($requiredPath in @($senderPath, $defaultOptionsPath)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required input does not exist: $requiredPath"
    }
}
if (-not (Test-Path -LiteralPath $saveRoot -PathType Container)) {
    throw "Required save corpus does not exist: $saveRoot"
}
if (Test-Path -LiteralPath (Join-Path $targetDirectory 'd3d9.dll')) {
    throw 'Refusing to combine drcov with an app-local d3d9.dll observer.'
}
if (Get-Process -Name BEA -ErrorAction SilentlyContinue) {
    throw 'A BEA process is already running; differential runs require one owner.'
}
if (@(
    Get-Process -Name drrun -ErrorAction SilentlyContinue |
        Where-Object {
            try { $_.Path -ieq $drrunPath } catch { $false }
        }
).Count -ne 0) {
    throw 'The selected drrun executable is already running.'
}

$targetBefore = Get-FileFacts -Path $target
$drrunBefore = Get-FileFacts -Path $drrunPath
$recorderBefore = Get-FileFacts -Path $PSCommandPath
$senderBefore = Get-FileFacts -Path $senderPath
$optionsBefore = Get-FileFacts -Path $defaultOptionsPath
$savesBefore = Get-SaveCorpusFacts -Root $saveRoot
if ($targetBefore.sha256 -cne $ExpectedTargetSha256.ToUpperInvariant()) {
    throw "Target SHA-256 mismatch: $($targetBefore.sha256)"
}
if ($drrunBefore.sha256 -cne $ExpectedDrrunSha256.ToUpperInvariant()) {
    throw "drrun SHA-256 mismatch: $($drrunBefore.sha256)"
}
$drrunVersion = (& $drrunPath -version 2>&1 | Out-String).Trim()
$protocolContract = [ordered]@{
    version = 'bea-options-drcov-protocol.v1'
    scenario = $Scenario
    activePageAddress = '0x0089D950'
    cursorXAddress = '0x0089BDA8'
    cursorYAddress = '0x0089BDA4'
    mouseGateAddress = '0x0089BDF0'
    clickToStartPage = 0x0C
    mainMenuPage = 0
    optionsPage = 0x11
    sharedClick = [ordered]@{ x = 320; y = 240 }
    optionsCursor = [ordered]@{ x = 219; y = 404 }
    pageStableSamples = 4
    pageSampleIntervalMilliseconds = 125
    mainMenuSettleMilliseconds = 1000
    observationSeconds = $CaptureSeconds
    gameArguments = @($GameArguments)
    actionCanaries = @('0x004623E0', '0x0051F7E0', '0x0051F6D0')
    sharedCanaries = @('0x0051B660', '0x00464520', '0x00462D40')
    campaignSchedules = [ordered]@{
        C1 = @($optionsOrderTokens.C1)
        C2 = @($optionsOrderTokens.C2)
    }
}
$protocolJson = $protocolContract | ConvertTo-Json -Depth 8 -Compress
$protocolSha256 = Get-TextSha256 -Text $protocolJson

$runDirectory = [IO.Path]::GetFullPath((Join-Path $OutputRoot $Name))
if (Test-Path -LiteralPath $runDirectory) {
    throw "Output already exists: $runDirectory"
}
[IO.Directory]::CreateDirectory($runDirectory) | Out-Null
$stdoutPath = Join-Path $runDirectory 'drrun-stdout.txt'
$stderrPath = Join-Path $runDirectory 'drrun-stderr.txt'
$receiptPath = Join-Path $runDirectory 'receipt.json'

$startedUtc = [DateTime]::UtcNow
$gameAppearedUtc = $null
$observationStartedUtc = $null
$observationEndUtc = $null
$guestExitTimeUtc = $null
$guestExitedBeforeWindow = $false
$drrunProcess = $null
$gameProcess = $null
$gameProcessHandle = [IntPtr]::Zero
$gameParentProcessId = $null
$gameDescendsFromDrrun = $false
$drrunProcessId = $null
$gameProcessId = $null
$gameHwndHex = $null
$moduleBase = $null
$drrunExitCode = $null
$gameExitCode = $null
$stdoutTask = $null
$stderrTask = $null
$drrunStdout = ''
$drrunStderr = ''
$streamsRead = $false
$forcedTermination = $false
$observationCompleted = $false
$precondition = $null
$outcome = $null
$genericInput = $null
$cleanupProblems = [Collections.Generic.List[string]]::new()
$extraTargetsDetected = 0
$extraDrrunsDetected = 0
$targetSurvivors = 0
$drrunSurvivors = 0
$failure = $null

try {
    $arguments = @(
        '-t', 'drcov',
        '-dump_text',
        '-logdir', $runDirectory,
        '--',
        $target
    ) + $GameArguments
    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $drrunPath
    $startInfo.WorkingDirectory = $targetDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    foreach ($argument in $arguments) {
        $startInfo.ArgumentList.Add($argument)
    }
    $drrunProcess = [Diagnostics.Process]::new()
    $drrunProcess.StartInfo = $startInfo
    if (-not $drrunProcess.Start()) {
        throw 'Failed to start drrun.'
    }
    $drrunProcessId = $drrunProcess.Id
    $stdoutTask = $drrunProcess.StandardOutput.ReadToEndAsync()
    $stderrTask = $drrunProcess.StandardError.ReadToEndAsync()

    $launchDeadline = [DateTime]::UtcNow.AddSeconds(90)
    while ([DateTime]::UtcNow -lt $launchDeadline) {
        if ($drrunProcess.HasExited) {
            throw "drrun exited before BEA appeared (exit $($drrunProcess.ExitCode))."
        }
        $pathCandidates = @(
            Get-Process -Name BEA -ErrorAction SilentlyContinue |
                Where-Object {
                    try {
                        $_.Path -ieq $target -and
                        $_.StartTime.ToUniversalTime() -ge $startedUtc.AddSeconds(-1)
                    } catch {
                        $false
                    }
                }
        )
        $candidate = @(
            $pathCandidates | Where-Object {
                Test-ProcessDescendsFrom `
                    -ProcessId $_.Id `
                    -AncestorProcessId $drrunProcessId
            }
        )
        if ($candidate.Count -eq 1) {
            $gameProcess = $candidate[0]
            $gameProcessHandle = $gameProcess.Handle
            $gameParentProcessId = [int](
                Get-CimInstance Win32_Process `
                    -Filter "ProcessId = $($gameProcess.Id)" `
                    -ErrorAction Stop
            ).ParentProcessId
            $gameProcessId = $gameProcess.Id
            $gameDescendsFromDrrun = $true
            $gameAppearedUtc = [DateTime]::UtcNow
            break
        }
        if ($candidate.Count -gt 1) {
            throw 'More than one matching copied-target BEA process appeared.'
        }
        Start-Sleep -Milliseconds 100
    }
    if ($null -eq $gameProcess) {
        throw 'Timed out waiting for the instrumented copied-target BEA process.'
    }

    $windowDeadline = [DateTime]::UtcNow.AddSeconds(90)
    while ([DateTime]::UtcNow -lt $windowDeadline) {
        if ($gameProcess.HasExited) {
            throw 'BEA exited before creating a top-level window.'
        }
        $gameProcess.Refresh()
        if ($gameProcess.MainWindowHandle -ne [IntPtr]::Zero) {
            $gameHwndHex = '0x{0:X}' -f $gameProcess.MainWindowHandle.ToInt64()
            break
        }
        Start-Sleep -Milliseconds 100
    }
    if ([string]::IsNullOrWhiteSpace($gameHwndHex)) {
        throw 'Timed out waiting for the instrumented BEA top-level window.'
    }
    $moduleBase = $gameProcess.MainModule.BaseAddress.ToInt64()
    $clientSize = [BeaDrcovNativeV2]::ClientSize($gameProcess.MainWindowHandle)
    if ($Scenario -eq $optionsScenario) {
        if ($moduleBase -ne 0x00400000) {
            throw (
                'Options differential contract requires module base 0x00400000; ' +
                ('observed 0x{0:X8}.' -f $moduleBase)
            )
        }
        if ($null -eq $clientSize -or
            $clientSize[0] -ne 640 -or $clientSize[1] -ne 480) {
            $observed = if ($null -eq $clientSize) {
                'unreadable'
            } else {
                "$($clientSize[0])x$($clientSize[1])"
            }
            throw (
                'Options differential contract requires a 640x480 client; ' +
                "observed $observed."
            )
        }
    }

    if ($Scenario -eq $optionsScenario) {
        $pageAddress = 0x0089D950
        $startPage = Wait-ForStablePage `
            -Process $gameProcess -Address $pageAddress -Expected 0x0C
        $sharedClick = Invoke-BoundedWindowInput `
            -Process $gameProcess `
            -HwndHex $gameHwndHex `
            -Sequence 'click:320x240' `
            -OutputPath (Join-Path $runDirectory 'input-shared-click.json') `
            -ExpectedExecutable $target `
            -ExpectedWorkingDirectory $targetDirectory `
            -RequireCursorVerification
        $mainPage = Wait-ForStablePage `
            -Process $gameProcess -Address $pageAddress -Expected 0
        $rowMove = Invoke-BoundedWindowInput `
            -Process $gameProcess `
            -HwndHex $gameHwndHex `
            -Sequence 'move:219x404' `
            -OutputPath (Join-Path $runDirectory 'input-options-row.json') `
            -ExpectedExecutable $target `
            -ExpectedWorkingDirectory $targetDirectory `
            -RequireCursorVerification
        Start-Sleep -Seconds 1
        $settledMainPage = Wait-ForStablePage `
            -Process $gameProcess -Address $pageAddress -Expected 0
        $settledCursorX = [BeaDrcovNativeV2]::ReadInt32(
            $gameProcess.Id, 0x0089BDA8
        )
        $settledCursorY = [BeaDrcovNativeV2]::ReadInt32(
            $gameProcess.Id, 0x0089BDA4
        )
        $settledMouseGate = [BeaDrcovNativeV2]::ReadInt32(
            $gameProcess.Id, 0x0089BDF0
        )
        if ($settledCursorX -ne 219 -or $settledCursorY -ne 404 -or
            $settledMouseGate -ne 0) {
            throw (
                'Settled Options cursor state differs from the measured contract: ' +
                "$settledCursorX,$settledCursorY gate=$settledMouseGate."
            )
        }
        $commonEpochUtc = [DateTime]::UtcNow
        $precondition = [ordered]@{
            contract = [ordered]@{
                activePageAddress = '0x0089D950'
                clickToStartPage = 0x0C
                mainMenuPage = 0
                sharedClick = [ordered]@{ x = 320; y = 240 }
                optionsCursor = [ordered]@{ x = 219; y = 404 }
                stableSamples = 4
                sampleIntervalMilliseconds = 125
                settleMilliseconds = 1000
            }
            viewport = [ordered]@{ width = 640; height = 480 }
            startPage = $startPage
            sharedClickReceipt = $sharedClick.receipt
            mainPage = $mainPage
            optionsCursorReceipt = $rowMove.receipt
            settledCursor = [ordered]@{
                x = $settledCursorX
                y = $settledCursorY
                mouseGate = $settledMouseGate
            }
            settledMainPage = $settledMainPage
            passed = $true
            commonEpochAtUtc = $commonEpochUtc.ToString('o')
        }
        $expectedFinalPage = if ($Role -eq 'action') { 0x11 } else { 0 }
        $actionInput = $null
        if ($Role -eq 'action') {
            $actionInput = Invoke-VerifiedOptionsClick `
                -Process $gameProcess `
                -Window $gameProcess.MainWindowHandle `
                -OutputPath (Join-Path $runDirectory 'input-action-click.json')
        }
        $initialOutcome = Wait-ForStablePage `
            -Process $gameProcess -Address $pageAddress -Expected $expectedFinalPage
        $observationStartedUtc = [DateTime]::UtcNow
        $observationEndUtc = $observationStartedUtc.AddSeconds($CaptureSeconds)
        $observationSamples = [Collections.Generic.List[object]]::new()
        while ([DateTime]::UtcNow -lt $observationEndUtc) {
            if ($gameProcess.HasExited) {
                $guestExitTimeUtc = $gameProcess.ExitTime.ToUniversalTime()
                $guestExitedBeforeWindow = $true
                throw 'BEA exited before the requested Options observation window ended.'
            }
            $pageValue = [BeaDrcovNativeV2]::ReadInt32(
                $gameProcess.Id, $pageAddress
            )
            $observationSamples.Add([ordered]@{
                atUtc = [DateTime]::UtcNow.ToString('o')
                value = if ($null -eq $pageValue) { $null } else { [int]$pageValue }
            })
            if ($null -eq $pageValue -or [int]$pageValue -ne $expectedFinalPage) {
                throw (
                    'Options role page changed during the observation window: ' +
                    "expected 0x$('{0:X}' -f $expectedFinalPage), observed " +
                    $(if ($null -eq $pageValue) { 'unreadable' } else {
                        "0x$('{0:X}' -f [int]$pageValue)"
                    })
                )
            }
            Start-Sleep -Milliseconds 125
        }
        $finalOutcome = Wait-ForStablePage `
            -Process $gameProcess -Address $pageAddress -Expected $expectedFinalPage
        $observationCompleted = $true
        $outcome = [ordered]@{
            expectedPage = $expectedFinalPage
            initialPage = $initialOutcome
            observationSamples = @($observationSamples)
            finalPage = $finalOutcome
            actionInputReceipt = if ($null -eq $actionInput) {
                $null
            } else {
                $actionInput.receipt
            }
            passed = $true
        }
    } else {
        $actionAt = $gameAppearedUtc.AddSeconds($ActionDelaySeconds)
        while ([DateTime]::UtcNow -lt $actionAt) {
            if ($gameProcess.HasExited) {
                throw 'BEA exited before the generic action window.'
            }
            Start-Sleep -Milliseconds 100
        }
        $observationStartedUtc = $gameAppearedUtc
        if ($Role -eq 'action') {
            $genericInput = Invoke-BoundedWindowInput `
                -Process $gameProcess `
                -HwndHex $gameHwndHex `
                -Sequence $ActionSequence `
                -OutputPath (Join-Path $runDirectory 'input-action.json') `
                -ExpectedExecutable $target `
                -ExpectedWorkingDirectory $targetDirectory
        }
        $observationEndUtc = $gameAppearedUtc.AddSeconds($CaptureSeconds)
        while ([DateTime]::UtcNow -lt $observationEndUtc) {
            if ($gameProcess.HasExited) {
                $guestExitTimeUtc = $gameProcess.ExitTime.ToUniversalTime()
                $guestExitedBeforeWindow = $true
                throw 'BEA exited before the requested generic capture window ended.'
            }
            Start-Sleep -Milliseconds 100
        }
        $observationCompleted = $true
        $precondition = [ordered]@{
            contract = 'generic.v1'
            viewport = [ordered]@{
                width = $clientSize[0]
                height = $clientSize[1]
            }
            passed = $true
            observationStartedAtUtc = $observationStartedUtc.ToString('o')
        }
        $outcome = [ordered]@{
            expectedPage = $null
            actionInputReceipt = if ($null -eq $genericInput) {
                $null
            } else {
                $genericInput.receipt
            }
            passed = $true
        }
    }

    if (-not $gameProcess.HasExited) {
        $null = $gameProcess.CloseMainWindow()
        if (-not $gameProcess.WaitForExit(15000)) {
            $gameProcess.Kill($true)
            $gameProcess.WaitForExit()
            $forcedTermination = $true
        }
    }
    $gameExitCode = [BeaDrcovNativeV2]::ProcessExitCode($gameProcessHandle)
    if ($null -eq $gameExitCode) {
        throw 'Failed to read the instrumented BEA exit code from its retained handle.'
    }
    if ($gameExitCode -ne 0) {
        throw "BEA exited with code $gameExitCode."
    }
    if (-not $drrunProcess.WaitForExit(30000)) {
        throw 'drrun did not finalize its log within 30 seconds of target exit.'
    }
    $drrunExitCode = $drrunProcess.ExitCode
    $drrunStdout = $stdoutTask.GetAwaiter().GetResult()
    $drrunStderr = $stderrTask.GetAwaiter().GetResult()
    $streamsRead = $true
    if ($drrunExitCode -ne 0) {
        throw "drrun exited with code $drrunExitCode."
    }
} catch {
    $failure = $_.Exception.Message
} finally {
    if ($null -ne $gameProcess) {
        try {
            if (-not $gameProcess.HasExited) {
                $gameProcess.Kill($true)
                $gameProcess.WaitForExit()
                $forcedTermination = $true
            }
            if ($gameProcess.HasExited -and $null -eq $gameExitCode) {
                $gameExitCode = [BeaDrcovNativeV2]::ProcessExitCode(
                    $gameProcessHandle
                )
            }
        } catch {
            $cleanupProblems.Add(
                "Failed to clean owned BEA PID $($gameProcess.Id): $($_.Exception.Message)"
            )
        } finally {
            try { $gameProcess.Dispose() } catch {}
        }
    }
    if ($null -ne $drrunProcess) {
        try {
            if (-not $drrunProcess.HasExited) {
                $drrunProcess.Kill($true)
                $drrunProcess.WaitForExit()
            }
            if ($null -eq $drrunExitCode) {
                $drrunExitCode = $drrunProcess.ExitCode
            }
            if (-not $streamsRead -and
                $null -ne $stdoutTask -and $null -ne $stderrTask) {
                $drrunStdout = $stdoutTask.GetAwaiter().GetResult()
                $drrunStderr = $stderrTask.GetAwaiter().GetResult()
                $streamsRead = $true
            }
        } catch {
            $cleanupProblems.Add(
                "Failed to clean drrun PID $($drrunProcess.Id): $($_.Exception.Message)"
            )
        } finally {
            try { $drrunProcess.Dispose() } catch {}
        }
    }

    $matchingTargets = @(
        Get-MatchingProcesses -Executable $target -StartedAt $startedUtc
    )
    $targetSurvivors = $matchingTargets.Count
    $extraTargetsDetected = $targetSurvivors
    foreach ($matching in $matchingTargets) { $matching.Dispose() }
    if ($targetSurvivors -ne 0) {
        $cleanupProblems.Add(
            "$targetSurvivors same-path copied-target BEA process(es) remain; " +
            'they were not killed because path and launch time do not prove ownership.'
        )
    }
    $matchingDrruns = @(
        Get-MatchingProcesses -Executable $drrunPath -StartedAt $startedUtc
    )
    $drrunSurvivors = $matchingDrruns.Count
    $extraDrrunsDetected = $drrunSurvivors
    foreach ($matching in $matchingDrruns) { $matching.Dispose() }
    if ($drrunSurvivors -ne 0) {
        $cleanupProblems.Add(
            "$drrunSurvivors same-path drrun process(es) remain; " +
            'they were not killed because path and launch time do not prove ownership.'
        )
    }
}

[IO.File]::WriteAllText(
    $stdoutPath,
    $drrunStdout,
    [Text.UTF8Encoding]::new($false)
)
[IO.File]::WriteAllText(
    $stderrPath,
    $drrunStderr,
    [Text.UTF8Encoding]::new($false)
)

$logs = @(
    Get-ChildItem -LiteralPath $runDirectory `
        -Filter 'drcov.BEA.exe.*.proc.log' -File
)
$log = if ($logs.Count -eq 1) { $logs[0] } else { $null }
$logFacts = if ($null -eq $log) {
    $null
} else {
    Get-FileFacts -Path $log.FullName
}
$targetAfter = Get-FileFacts -Path $target
$drrunAfter = Get-FileFacts -Path $drrunPath
$recorderAfter = Get-FileFacts -Path $PSCommandPath
$senderAfter = Get-FileFacts -Path $senderPath
$optionsAfter = Get-FileFacts -Path $defaultOptionsPath
$savesAfter = Get-SaveCorpusFacts -Root $saveRoot

$targetUnchanged = Test-FileFactsEqual $targetBefore $targetAfter
$drrunUnchanged = Test-FileFactsEqual $drrunBefore $drrunAfter
$recorderUnchanged = Test-FileFactsEqual $recorderBefore $recorderAfter
$senderUnchanged = Test-FileFactsEqual $senderBefore $senderAfter
$optionsUnchanged = Test-FileFactsEqual $optionsBefore $optionsAfter
$savesUnchanged = Test-CorpusFactsEqual $savesBefore $savesAfter

$problems = [Collections.Generic.List[string]]::new()
if (-not [string]::IsNullOrWhiteSpace($failure)) { $problems.Add($failure) }
if ($logs.Count -ne 1) {
    $problems.Add("Expected one BEA drcov log, found $($logs.Count).")
} elseif ($logFacts.bytes -eq 0) {
    $problems.Add('drcov produced an empty log.')
}
if (-not $observationCompleted) { $problems.Add('Observation window did not complete.') }
if ($guestExitedBeforeWindow) { $problems.Add('Guest exited before the observation end.') }
if ($gameExitCode -ne 0) { $problems.Add("BEA exit code is $gameExitCode.") }
if ($drrunExitCode -ne 0) { $problems.Add("drrun exit code is $drrunExitCode.") }
if ($forcedTermination) { $problems.Add('Forced process termination was required.') }
if (-not $targetUnchanged) { $problems.Add('Target executable changed during capture.') }
if (-not $drrunUnchanged) { $problems.Add('drrun executable changed during capture.') }
if (-not $recorderUnchanged) { $problems.Add('Recorder script changed during capture.') }
if (-not $senderUnchanged) { $problems.Add('Input sender changed during capture.') }
if (-not $optionsUnchanged) { $problems.Add('defaultoptions.bea changed during capture.') }
if (-not $savesUnchanged) { $problems.Add('Save corpus changed during capture.') }
foreach ($problem in $cleanupProblems) { $problems.Add($problem) }
if ($extraTargetsDetected -ne 0) {
    $problems.Add("$extraTargetsDetected additional copied-target process(es) were detected.")
}
if ($extraDrrunsDetected -ne 0) {
    $problems.Add("$extraDrrunsDetected additional drrun process(es) were detected.")
}

$captureComplete = $problems.Count -eq 0
$finishedUtc = [DateTime]::UtcNow
$orderToken = if ($Scenario -eq $optionsScenario) {
    $optionsOrderTokens[$CampaignId][$SequenceIndex - 1]
} else {
    $null
}
$actionStatus = if ($Role -eq 'baseline') {
    'NONE_BASELINE'
} elseif ($Scenario -eq $optionsScenario) {
    'MECHANICALLY_VERIFIED'
} else {
    'POSTED_NOT_ACKNOWLEDGED'
}
$receipt = [ordered]@{
    schemaVersion = if ($Scenario -eq $optionsScenario) {
        'bea-drcov-capture-receipt.v2'
    } else {
        'bea-drcov-capture-receipt.v1'
    }
    runId = $Name
    role = $Role
    scenario = $Scenario
    campaignId = if ($Scenario -eq $optionsScenario) { $CampaignId } else { $null }
    sequenceIndex = if ($Scenario -eq $optionsScenario) {
        $SequenceIndex
    } else {
        $null
    }
    orderToken = $orderToken
    logPath = if ($null -eq $logFacts) { '' } else { $logFacts.path }
    logSha256 = if ($null -eq $logFacts) { '' } else { $logFacts.sha256 }
    logBytes = if ($null -eq $logFacts) { 0 } else { $logFacts.bytes }
    targetPath = $target
    targetSha256 = $targetAfter.sha256
    targetUnchanged = $targetUnchanged
    captureComplete = [bool]$captureComplete
    actionStatus = $actionStatus
    actionProtocol = if ($Scenario -eq $optionsScenario) {
        if ($Role -eq 'action') {
            'Shared main-menu precondition; one target-window click at client 219,404.'
        } else {
            'Shared main-menu precondition; no input during the observation window.'
        }
    } elseif ($Role -eq 'action') {
        "At +${ActionDelaySeconds}s, target-window message sequence: $ActionSequence"
    } else {
        "No input; ${CaptureSeconds}s baseline."
    }
    protocolVersion = $protocolContract.version
    protocolSha256 = $protocolSha256
    protocol = $protocolContract
    artifacts = [ordered]@{
        targetBefore = $targetBefore
        targetAfter = $targetAfter
        drrunBefore = $drrunBefore
        drrunAfter = $drrunAfter
        recorderBefore = $recorderBefore
        recorderAfter = $recorderAfter
        inputSenderBefore = $senderBefore
        inputSenderAfter = $senderAfter
    }
    tool = 'DynamoRIO drcov'
    toolVersion = $drrunVersion
    drrunPath = $drrunPath
    drrunSha256 = $drrunAfter.sha256
    gameArguments = @($GameArguments)
    workingDirectory = $targetDirectory
    requestedCaptureSeconds = $CaptureSeconds
    precondition = $precondition
    outcome = $outcome
    corpus = [ordered]@{
        defaultOptionsBefore = $optionsBefore
        defaultOptionsAfter = $optionsAfter
        saveCorpusBefore = $savesBefore
        saveCorpusAfter = $savesAfter
        unchanged = [bool]($optionsUnchanged -and $savesUnchanged)
    }
    process = [ordered]@{
        targetProcessId = $gameProcessId
        targetParentProcessId = $gameParentProcessId
        targetDescendsFromDrrun = [bool]$gameDescendsFromDrrun
        drrunProcessId = $drrunProcessId
        targetHwndHex = $gameHwndHex
        moduleBase = if ($null -eq $moduleBase) {
            $null
        } else {
            '0x{0:X8}' -f $moduleBase
        }
        startedAtUtc = $startedUtc.ToString('o')
        gameAppearedAtUtc = if ($null -eq $gameAppearedUtc) {
            $null
        } else {
            $gameAppearedUtc.ToString('o')
        }
        observationStartedAtUtc = if ($null -eq $observationStartedUtc) {
            $null
        } else {
            $observationStartedUtc.ToString('o')
        }
        observationEndAtUtc = if ($null -eq $observationEndUtc) {
            $null
        } else {
            $observationEndUtc.ToString('o')
        }
        guestExitTimeUtc = if ($null -eq $guestExitTimeUtc) {
            $null
        } else {
            $guestExitTimeUtc.ToString('o')
        }
        guestExitedBeforeWindow = [bool]$guestExitedBeforeWindow
        observationCompleted = [bool]$observationCompleted
        targetExitCode = $gameExitCode
        drrunExitCode = $drrunExitCode
        forcedTermination = [bool]$forcedTermination
    }
    cleanup = [ordered]@{
        matchingProcessScanPerformed = $true
        extraMatchingTargetsDetected = $extraTargetsDetected
        extraMatchingDrrunsDetected = $extraDrrunsDetected
        targetSurvivorCount = $targetSurvivors
        drrunSurvivorCount = $drrunSurvivors
        problems = @($cleanupProblems)
    }
    startedAtUtc = $startedUtc.ToString('o')
    finishedAtUtc = $finishedUtc.ToString('o')
    elapsedSeconds = [Math]::Round(($finishedUtc - $startedUtc).TotalSeconds, 3)
    failure = if ($problems.Count -eq 0) { $null } else { @($problems) }
}

$receiptJson = ($receipt | ConvertTo-Json -Depth 20) + [Environment]::NewLine
$receiptBytes = [Text.UTF8Encoding]::new($false).GetBytes($receiptJson)
$receiptStream = [IO.File]::Open(
    $receiptPath,
    [IO.FileMode]::CreateNew,
    [IO.FileAccess]::Write,
    [IO.FileShare]::None
)
try {
    $receiptStream.Write($receiptBytes, 0, $receiptBytes.Length)
    $receiptStream.Flush($true)
} finally {
    $receiptStream.Dispose()
}
$receipt
if (-not $captureComplete) {
    throw (
        "Differential coverage capture failed; receipt: $receiptPath; " +
        (@($problems) -join ' | ')
    )
}
