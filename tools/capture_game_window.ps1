param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId,
    [Parameter(Mandatory = $true)]
    [string]$HwndHex,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,
    [string]$AllowedOutputRoot = "",
    [string]$ExpectedExecutablePath = "",
    [string]$ExpectedWorkingDirectory = "",
    [string]$SourceGameRoot = "",
    [switch]$PrintOnly,
    [switch]$AllowOverwrite
)

$ErrorActionPreference = "Stop"

if ($ProcessId -le 0) {
    Write-Error "ProcessId must be a positive integer."
    exit 1
}

if ($HwndHex -notmatch '^0x[0-9A-Fa-f]+$') {
    Write-Error "HwndHex must be formatted like 0x1234ABCD."
    exit 1
}

$resolvedOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$resolvedOutputDir = [System.IO.Path]::GetDirectoryName($resolvedOutputPath)
if ([string]::IsNullOrWhiteSpace($resolvedOutputDir)) {
    Write-Error "OutputPath must include a directory."
    exit 1
}

if (-not [string]::Equals([System.IO.Path]::GetExtension($resolvedOutputPath), ".png", [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Error "OutputPath must end in .png."
    exit 1
}

function Test-PathUnderRoot([string]$PathValue, [string]$RootValue) {
    $resolvedPathValue = [System.IO.Path]::GetFullPath($PathValue)
    $resolvedRootValue = [System.IO.Path]::GetFullPath($RootValue).TrimEnd(
        [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
    return $resolvedPathValue.StartsWith(
        $resolvedRootValue + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase) -or
        [string]::Equals($resolvedPathValue, $resolvedRootValue, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-PathsOverlap([string]$LeftValue, [string]$RightValue) {
    return (Test-PathUnderRoot -PathValue $LeftValue -RootValue $RightValue) -or
        (Test-PathUnderRoot -PathValue $RightValue -RootValue $LeftValue)
}

function Test-HasReparseAncestor([string]$PathValue) {
    $candidate = [System.IO.Path]::GetFullPath($PathValue)
    while (-not [string]::IsNullOrWhiteSpace($candidate)) {
        if (Test-Path -LiteralPath $candidate) {
            $item = Get-Item -LiteralPath $candidate -Force
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                return $true
            }
        }

        $parent = [System.IO.Directory]::GetParent($candidate)
        if ($null -eq $parent) {
            break
        }

        $candidate = $parent.FullName
    }

    return $false
}

function Initialize-FileSafetyNative {
    $nativeType = "GameCaptureFileSafetyNative"
    if (-not ([System.Management.Automation.PSTypeName]$nativeType).Type) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class GameCaptureFileSafetyNative {
    [StructLayout(LayoutKind.Sequential)]
    public struct FILETIME {
        public uint dwLowDateTime;
        public uint dwHighDateTime;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct BY_HANDLE_FILE_INFORMATION {
        public uint dwFileAttributes;
        public FILETIME ftCreationTime;
        public FILETIME ftLastAccessTime;
        public FILETIME ftLastWriteTime;
        public uint dwVolumeSerialNumber;
        public uint nFileSizeHigh;
        public uint nFileSizeLow;
        public uint nNumberOfLinks;
        public uint nFileIndexHigh;
        public uint nFileIndexLow;
    }

    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool GetFileInformationByHandle(IntPtr hFile, out BY_HANDLE_FILE_INFORMATION lpFileInformation);
}
"@
    }
}

function Get-FileLinkCount([string]$PathValue) {
    Initialize-FileSafetyNative
    $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
    $stream = [System.IO.File]::Open($PathValue, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, $share)
    try {
        $info = New-Object GameCaptureFileSafetyNative+BY_HANDLE_FILE_INFORMATION
        $ok = [GameCaptureFileSafetyNative]::GetFileInformationByHandle(
            $stream.SafeFileHandle.DangerousGetHandle(),
            [ref]$info)
        if (-not $ok) {
            Write-Error "Could not read existing output file link metadata."
            exit 1
        }

        return [int]$info.nNumberOfLinks
    }
    finally {
        $stream.Dispose()
    }
}

function Assert-ExistingOutputFileIsSafe([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue -PathType Leaf)) {
        return
    }

    $item = Get-Item -LiteralPath $PathValue -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Error "Existing OutputPath must not be a reparse-point file."
        exit 1
    }

    $linkCount = Get-FileLinkCount -PathValue $PathValue
    if ($linkCount -gt 1) {
        Write-Error "Existing OutputPath must not be hardlinked."
        exit 1
    }
}

function Get-ProtectedRoots {
    $roots = @()
    foreach ($key in @("ProgramFiles", "ProgramFiles(x86)")) {
        $raw = [Environment]::GetEnvironmentVariable($key)
        if (-not [string]::IsNullOrWhiteSpace($raw) -and (Test-Path -LiteralPath $raw -PathType Container)) {
            $roots += [System.IO.Path]::GetFullPath($raw)
        }
    }
    return $roots
}

$runningOnWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows
)

if (-not $runningOnWindows) {
    [PSCustomObject]@{
        schemaVersion = "game-window-capture-helper.v1"
        generatedAt = (Get-Date).ToString("o")
        status = "unsupported"
        processId = $ProcessId
        hwndHex = $HwndHex
        outputPath = $resolvedOutputPath
        note = "Window capture is currently implemented only on Windows."
    } | ConvertTo-Json -Depth 6
    exit 0
}

if (-not $PrintOnly -and [string]::IsNullOrWhiteSpace($AllowedOutputRoot)) {
    Write-Error "Real window capture requires AllowedOutputRoot so capture output stays under an app-owned artifact root."
    exit 1
}

if (-not $PrintOnly -and ([string]::IsNullOrWhiteSpace($ExpectedExecutablePath) -or [string]::IsNullOrWhiteSpace($ExpectedWorkingDirectory))) {
    Write-Error "Real window capture requires ExpectedExecutablePath and ExpectedWorkingDirectory so capture cannot target an unrelated BEA.exe window."
    exit 1
}

if (-not $PrintOnly -and [string]::IsNullOrWhiteSpace($SourceGameRoot)) {
    Write-Error "Real window capture requires SourceGameRoot so capture output cannot be written into the read-only game source."
    exit 1
}

$resolvedAllowedOutputRoot = $null
if (-not [string]::IsNullOrWhiteSpace($AllowedOutputRoot)) {
    $resolvedAllowedOutputRoot = [System.IO.Path]::GetFullPath($AllowedOutputRoot).TrimEnd(
        [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
    if (-not (Test-PathUnderRoot -PathValue $resolvedOutputPath -RootValue $resolvedAllowedOutputRoot)) {
        Write-Error "OutputPath must stay under AllowedOutputRoot."
        exit 1
    }

    if (Test-HasReparseAncestor -PathValue $resolvedAllowedOutputRoot) {
        Write-Error "AllowedOutputRoot must not contain a reparse-point ancestor."
        exit 1
    }

    foreach ($protectedRoot in Get-ProtectedRoots) {
        if (Test-PathsOverlap -LeftValue $resolvedAllowedOutputRoot -RightValue $protectedRoot) {
            Write-Error "AllowedOutputRoot must not overlap Program Files or another protected install root."
            exit 1
        }

        if (Test-PathUnderRoot -PathValue $resolvedOutputPath -RootValue $protectedRoot) {
            Write-Error "OutputPath must not be inside Program Files or another protected install root."
            exit 1
        }
    }
}

if (-not $AllowOverwrite -and (Test-Path -LiteralPath $resolvedOutputPath -PathType Leaf)) {
    Write-Error "OutputPath already exists. Use a new artifact path or pass AllowOverwrite explicitly."
    exit 1
}

if ($AllowOverwrite) {
    Assert-ExistingOutputFileIsSafe -PathValue $resolvedOutputPath
}

$resolvedExpectedExecutablePath = $null
$resolvedExpectedWorkingDirectory = $null
$resolvedSourceGameRoot = $null
if (-not [string]::IsNullOrWhiteSpace($ExpectedExecutablePath)) {
    if (-not (Test-Path -LiteralPath $ExpectedExecutablePath -PathType Leaf)) {
        Write-Error "ExpectedExecutablePath was not found."
        exit 1
    }

    $resolvedExpectedExecutablePath = [System.IO.Path]::GetFullPath($ExpectedExecutablePath)
}
if (-not [string]::IsNullOrWhiteSpace($ExpectedWorkingDirectory)) {
    if (-not (Test-Path -LiteralPath $ExpectedWorkingDirectory -PathType Container)) {
        Write-Error "ExpectedWorkingDirectory was not found."
        exit 1
    }

    $resolvedExpectedWorkingDirectory = [System.IO.Path]::GetFullPath($ExpectedWorkingDirectory).TrimEnd(
        [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
}

if (-not [string]::IsNullOrWhiteSpace($SourceGameRoot)) {
    if (-not (Test-Path -LiteralPath $SourceGameRoot -PathType Container)) {
        Write-Error "SourceGameRoot was not found."
        exit 1
    }

    $resolvedSourceGameRoot = [System.IO.Path]::GetFullPath($SourceGameRoot).TrimEnd(
        [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
    if (Test-HasReparseAncestor -PathValue $resolvedSourceGameRoot) {
        Write-Error "SourceGameRoot must not contain a reparse-point ancestor."
        exit 1
    }
}

if ($resolvedAllowedOutputRoot -and $resolvedSourceGameRoot) {
    if (Test-PathsOverlap -LeftValue $resolvedAllowedOutputRoot -RightValue $resolvedSourceGameRoot) {
        Write-Error "AllowedOutputRoot must not overlap the read-only source game root."
        exit 1
    }

    if (Test-PathUnderRoot -PathValue $resolvedOutputPath -RootValue $resolvedSourceGameRoot) {
        Write-Error "OutputPath must not be inside the read-only source game root."
        exit 1
    }
}

$nativeType = "GameWindowCaptureNative"
if (-not ([System.Management.Automation.PSTypeName]$nativeType).Type) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class GameWindowCaptureNative {
    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern IntPtr GetTopWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetWindow(IntPtr hWnd, uint uCmd);

    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }
}
"@
}

function Get-WindowTitleText([IntPtr]$Handle) {
    $length = [GameWindowCaptureNative]::GetWindowTextLength($Handle)
    if ($length -le 0) {
        return ""
    }

    $builder = New-Object System.Text.StringBuilder ($length + 1)
    [void][GameWindowCaptureNative]::GetWindowText($Handle, $builder, $builder.Capacity)
    return $builder.ToString()
}

function Test-RectanglesOverlap($LeftRect, $RightRect) {
    return $LeftRect.Left -lt $RightRect.Right -and
        $LeftRect.Right -gt $RightRect.Left -and
        $LeftRect.Top -lt $RightRect.Bottom -and
        $LeftRect.Bottom -gt $RightRect.Top
}

function Get-OverlapArea($LeftRect, $RightRect) {
    $overlapWidth = [Math]::Max(0, [Math]::Min($LeftRect.Right, $RightRect.Right) - [Math]::Max($LeftRect.Left, $RightRect.Left))
    $overlapHeight = [Math]::Max(0, [Math]::Min($LeftRect.Bottom, $RightRect.Bottom) - [Math]::Max($LeftRect.Top, $RightRect.Top))
    return $overlapWidth * $overlapHeight
}

function Get-RectPayload($RectValue) {
    return [PSCustomObject]@{
        left = $RectValue.Left
        top = $RectValue.Top
        right = $RectValue.Right
        bottom = $RectValue.Bottom
        width = [Math]::Max(0, $RectValue.Right - $RectValue.Left)
        height = [Math]::Max(0, $RectValue.Bottom - $RectValue.Top)
    }
}

function Get-ZOrderOcclusionPayload([IntPtr]$TargetHandle, $TargetRect) {
    [uint32]$GW_HWNDNEXT = 2
    $maxWindows = 512
    $minimumOccluderOverlapArea = 64
    $targetFound = $false
    $targetIndex = -1
    $occludingWindows = @()
    $tinyOverlappingWindows = @()
    $candidate = [GameWindowCaptureNative]::GetTopWindow([IntPtr]::Zero)
    $index = 0

    while ($candidate -ne [IntPtr]::Zero -and $index -lt $maxWindows) {
        if ($candidate -eq $TargetHandle) {
            $targetFound = $true
            $targetIndex = $index
            break
        }

        if ([GameWindowCaptureNative]::IsWindowVisible($candidate) -and -not [GameWindowCaptureNative]::IsIconic($candidate)) {
            $candidateRect = New-Object GameWindowCaptureNative+RECT
            if ([GameWindowCaptureNative]::GetWindowRect($candidate, [ref]$candidateRect) -and
                $candidateRect.Right -gt $candidateRect.Left -and
                $candidateRect.Bottom -gt $candidateRect.Top -and
                (Test-RectanglesOverlap -LeftRect $candidateRect -RightRect $TargetRect)) {
                $overlapArea = Get-OverlapArea -LeftRect $candidateRect -RightRect $TargetRect
                [uint32]$candidateProcessId = 0
                [void][GameWindowCaptureNative]::GetWindowThreadProcessId($candidate, [ref]$candidateProcessId)
                $windowPayload = [PSCustomObject]@{
                    hwndHex = ("0x{0:X}" -f $candidate.ToInt64())
                    processId = [int]$candidateProcessId
                    title = Get-WindowTitleText -Handle $candidate
                    bounds = Get-RectPayload -RectValue $candidateRect
                    overlapArea = $overlapArea
                }
                if ($overlapArea -ge $minimumOccluderOverlapArea) {
                    $occludingWindows += $windowPayload
                }
                else {
                    $tinyOverlappingWindows += $windowPayload
                }
            }
        }

        $candidate = [GameWindowCaptureNative]::GetWindow($candidate, $GW_HWNDNEXT)
        $index++
    }

    $checkedWindowCountBeforeTarget = if ($targetFound) { $targetIndex } else { $index }
    $occludingWindowCount = @($occludingWindows).Count
    $occlusionFree = [bool]($targetFound -and $occludingWindowCount -eq 0)

    $payload = [ordered]@{}
    $payload["checked"] = $true
    $payload["targetFound"] = [bool]$targetFound
    $payload["targetZOrderIndex"] = [int]$targetIndex
    $payload["checkedWindowCountBeforeTarget"] = [int]$checkedWindowCountBeforeTarget
    $payload["minimumOccluderOverlapArea"] = [int]$minimumOccluderOverlapArea
    $payload["occlusionFree"] = $occlusionFree
    $payload["occludingWindowCount"] = [int]$occludingWindowCount
    $payload["occludingWindows"] = @($occludingWindows)
    $payload["tinyOverlappingWindowCount"] = [int]@($tinyOverlappingWindows).Count
    $payload["tinyOverlappingWindows"] = @($tinyOverlappingWindows)
    $payload["note"] = "Top-level z-order windows above the target were checked for rectangle overlap before screen capture; overlaps smaller than minimumOccluderOverlapArea are recorded separately as tiny overlaps."
    return [PSCustomObject]$payload
}

$handleValue = [Convert]::ToInt64($HwndHex.Substring(2), 16)
$handle = [IntPtr]::new($handleValue)

if (-not [GameWindowCaptureNative]::IsWindow($handle)) {
    Write-Error "The provided HwndHex does not identify a live window."
    exit 1
}

[uint32]$windowProcessId = 0
[void][GameWindowCaptureNative]::GetWindowThreadProcessId($handle, [ref]$windowProcessId)
if ([int]$windowProcessId -ne $ProcessId) {
    Write-Error ("Window/process mismatch: hwnd belongs to process {0}, expected {1}." -f $windowProcessId, $ProcessId)
    exit 1
}

$process = $null
$modulePath = $null
$moduleDirectory = $null
try {
    $process = Get-Process -Id $ProcessId -ErrorAction Stop
    $modulePath = [System.IO.Path]::GetFullPath($process.MainModule.FileName)
    $moduleDirectory = [System.IO.Path]::GetDirectoryName($modulePath)
} catch {
    Write-Error "Could not resolve target process executable path."
    exit 1
}

if ($resolvedExpectedExecutablePath -and -not [string]::Equals($modulePath, $resolvedExpectedExecutablePath, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Error "Target process executable path did not match ExpectedExecutablePath."
    exit 1
}

if ($resolvedExpectedWorkingDirectory -and -not [string]::Equals(
    $moduleDirectory.TrimEnd([char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)),
    $resolvedExpectedWorkingDirectory,
    [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Error "Target process working directory did not match ExpectedWorkingDirectory."
    exit 1
}

if ($resolvedAllowedOutputRoot -and $resolvedExpectedWorkingDirectory) {
    if (Test-PathUnderRoot -PathValue $resolvedAllowedOutputRoot -RootValue $resolvedExpectedWorkingDirectory) {
        Write-Error "AllowedOutputRoot must not be inside the copied game working directory."
        exit 1
    }

    if (Test-PathUnderRoot -PathValue $resolvedOutputPath -RootValue $resolvedExpectedWorkingDirectory) {
        Write-Error "OutputPath must not be inside the copied game working directory."
        exit 1
    }
}

if (-not [GameWindowCaptureNative]::IsWindowVisible($handle)) {
    Write-Error "The target window is not visible."
    exit 1
}

$rect = New-Object GameWindowCaptureNative+RECT
if (-not [GameWindowCaptureNative]::GetWindowRect($handle, [ref]$rect)) {
    Write-Error "Could not read target window bounds."
    exit 1
}

$width = [Math]::Max(0, $rect.Right - $rect.Left)
$height = [Math]::Max(0, $rect.Bottom - $rect.Top)
if ($width -le 0 -or $height -le 0) {
    Write-Error ("Target window has invalid bounds: {0}x{1}." -f $width, $height)
    exit 1
}

$foregroundHandle = [GameWindowCaptureNative]::GetForegroundWindow()
$foregroundHwndHex = ("0x{0:X}" -f $foregroundHandle.ToInt64())
[uint32]$foregroundProcessId = 0
if ($foregroundHandle -ne [IntPtr]::Zero) {
    [void][GameWindowCaptureNative]::GetWindowThreadProcessId($foregroundHandle, [ref]$foregroundProcessId)
}
$foregroundMatchesTarget = ([int]$foregroundProcessId -eq $ProcessId -and [string]::Equals($foregroundHwndHex, $HwndHex, [System.StringComparison]::OrdinalIgnoreCase))
$occlusionPayload = $null
try {
    $occlusionPayload = Get-ZOrderOcclusionPayload -TargetHandle $handle -TargetRect $rect
}
catch {
    $occlusionPayload = [PSCustomObject]@{
        checked = $false
        targetFound = $false
        targetZOrderIndex = -1
        checkedWindowCountBeforeTarget = 0
        occlusionFree = $false
        occludingWindowCount = 0
        occludingWindows = @()
        error = $_.Exception.Message
        errorType = $_.Exception.GetType().FullName
        errorPosition = $_.InvocationInfo.PositionMessage
        errorStack = $_.ScriptStackTrace
        note = "Top-level z-order occlusion scan failed; capture may still be valid when foregroundMatchesTarget is true."
    }
}
$visualProof = $foregroundMatchesTarget -or ($occlusionPayload.checked -eq $true -and $occlusionPayload.occlusionFree -eq $true)
$visualProofReason = if ($foregroundMatchesTarget) {
    "foreground-match"
} elseif ($occlusionPayload.occlusionFree) {
    "z-order-occlusion-free"
} else {
    "not-proven"
}

$result = [PSCustomObject]@{
    schemaVersion = "game-window-capture-helper.v1"
    generatedAt = (Get-Date).ToString("o")
    status = if ($PrintOnly) { "planned" } else { "captured" }
    processName = "$($process.ProcessName).exe"
    processId = $ProcessId
    hwndHex = $HwndHex
    foregroundHwndHex = $foregroundHwndHex
    foregroundProcessId = [int]$foregroundProcessId
    foregroundMatchesTarget = $foregroundMatchesTarget
    visualProof = $visualProof
    visualProofReason = $visualProofReason
    occlusion = $occlusionPayload
    executablePath = $modulePath
    workingDirectory = $moduleDirectory
    outputPath = $resolvedOutputPath
    allowedOutputRoot = $resolvedAllowedOutputRoot
    sourceGameRoot = $resolvedSourceGameRoot
    bounds = [PSCustomObject]@{
        left = $rect.Left
        top = $rect.Top
        right = $rect.Right
        bottom = $rect.Bottom
        width = $width
        height = $height
    }
    note = "One bounded screen-region capture at verified target window bounds. Visual proof is true only when the target was foreground-owned or top-level z-order inspection found no meaningfully overlapping visible window above it."
}

if ($PrintOnly) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

if (-not (Test-Path -LiteralPath $resolvedOutputDir -PathType Container)) {
    New-Item -ItemType Directory -Path $resolvedOutputDir | Out-Null
}

Add-Type -AssemblyName System.Drawing
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$tempOutputPath = [System.IO.Path]::Combine(
    $resolvedOutputDir,
    (".capture-" + [System.Guid]::NewGuid().ToString("N") + ".tmp.png"))
try {
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
    $bitmap.Save($tempOutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $graphics.Dispose()
    $bitmap.Dispose()
}

try {
    if ($AllowOverwrite) {
        Assert-ExistingOutputFileIsSafe -PathValue $resolvedOutputPath
    }
    elseif (Test-Path -LiteralPath $resolvedOutputPath -PathType Leaf) {
        Write-Error "OutputPath already exists before final capture write."
        exit 1
    }

    if ($AllowOverwrite -and (Test-Path -LiteralPath $resolvedOutputPath -PathType Leaf)) {
        Remove-Item -LiteralPath $resolvedOutputPath -Force
    }
    [System.IO.File]::Move($tempOutputPath, $resolvedOutputPath)
}
finally {
    if (Test-Path -LiteralPath $tempOutputPath -PathType Leaf) {
        Remove-Item -LiteralPath $tempOutputPath -Force
    }
}

$captureFile = Get-Item -LiteralPath $resolvedOutputPath
$captureHash = (Get-FileHash -LiteralPath $resolvedOutputPath -Algorithm SHA256).Hash.ToLowerInvariant()
$result | Add-Member -NotePropertyName fileSize -NotePropertyValue $captureFile.Length
$result | Add-Member -NotePropertyName sha256 -NotePropertyValue $captureHash

$result | ConvertTo-Json -Depth 8
