param(
    [string]$ProcessName = "BEA.exe",
    [int]$ProcessId = 0,
    [string]$HwndHex = "",
    [Parameter(Mandatory = $true)]
    [string]$Sequence,
    [int]$StepDelayMs = 60,
    [string]$ExpectedExecutablePath = "",
    [string]$ExpectedWorkingDirectory = "",
    [string]$RuntimeReceiptPath = "",
    [string]$ExpectedReceiptSha256 = "",
    [switch]$AllowBackgroundWindowMessages,
    [string]$BackgroundWindowMessagesArm = "",
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"
$backgroundWindowMessageArmPhrase = "ALLOW BACKGROUND BEA WINDOW MESSAGES"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$canaryMode = -not [string]::IsNullOrWhiteSpace($RuntimeReceiptPath) -or
    -not [string]::IsNullOrWhiteSpace($ExpectedReceiptSha256)
$validatedReceipt = $null

if ($canaryMode) {
    if ([string]::IsNullOrWhiteSpace($RuntimeReceiptPath) -or
        [string]::IsNullOrWhiteSpace($ExpectedReceiptSha256)) {
        Write-Error "Canary input requires RuntimeReceiptPath and ExpectedReceiptSha256."
        exit 1
    }
    if ($AllowBackgroundWindowMessages) {
        Write-Error "Canary input refuses background window messages and requires exact foreground SendInput."
        exit 1
    }
}

if ($StepDelayMs -lt 0 -or $StepDelayMs -gt 1000) {
    Write-Error "StepDelayMs must be between 0 and 1000."
    exit 1
}

$runningOnWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows
)

if (-not $runningOnWindows) {
    [PSCustomObject]@{
        schemaVersion = "game-window-input.v1"
        generatedAt = (Get-Date).ToString("o")
        mutation = $false
        processName = $ProcessName
        processId = if ($ProcessId -gt 0) { $ProcessId } else { $null }
        status = "unsupported"
        actions = @()
        note = "Scoped window input is currently implemented only for Windows top-level windows."
    } | ConvertTo-Json -Depth 8
    exit 1
}

$allowedKeys = @{
    "UP" = 0x26
    "DOWN" = 0x28
    "LEFT" = 0x25
    "RIGHT" = 0x27
    "W" = 0x57
    "A" = 0x41
    "S" = 0x53
    "D" = 0x44
    "Q" = 0x51
    "O" = 0x4F
    "E" = 0x45
    "R" = 0x52
    "F" = 0x46
    "Z" = 0x5A
    "X" = 0x58
    "C" = 0x43
    "V" = 0x56
    "SPACE" = 0x20
    "ENTER" = 0x0D
    "ESCAPE" = 0x1B
    "TAB" = 0x09
    "SHIFT" = 0x10
    "LSHIFT" = 0xA0
    "RSHIFT" = 0xA1
    "CTRL" = 0x11
    "LCTRL" = 0xA2
    "RCTRL" = 0xA3
    "BACKSLASH" = 0xDC
    "F1" = 0x70
    "F2" = 0x71
    "F3" = 0x72
    "F5" = 0x74
    "F6" = 0x75
    "F7" = 0x76
    "F8" = 0x77
    "F9" = 0x78
    "F10" = 0x79
    "F11" = 0x7A
    "F12" = 0x7B
}

$scanCodes = @{
    "ESCAPE" = @{ code = 0x01; extended = $false }
    "F1" = @{ code = 0x3B; extended = $false }
    "F2" = @{ code = 0x3C; extended = $false }
    "F3" = @{ code = 0x3D; extended = $false }
    "F5" = @{ code = 0x3F; extended = $false }
    "F6" = @{ code = 0x40; extended = $false }
    "F7" = @{ code = 0x41; extended = $false }
    "F8" = @{ code = 0x42; extended = $false }
    "F9" = @{ code = 0x43; extended = $false }
    "F10" = @{ code = 0x44; extended = $false }
    "F11" = @{ code = 0x57; extended = $false }
    "F12" = @{ code = 0x58; extended = $false }
    "Q" = @{ code = 0x10; extended = $false }
    "W" = @{ code = 0x11; extended = $false }
    "E" = @{ code = 0x12; extended = $false }
    "R" = @{ code = 0x13; extended = $false }
    "A" = @{ code = 0x1E; extended = $false }
    "S" = @{ code = 0x1F; extended = $false }
    "D" = @{ code = 0x20; extended = $false }
    "F" = @{ code = 0x21; extended = $false }
    "Z" = @{ code = 0x2C; extended = $false }
    "X" = @{ code = 0x2D; extended = $false }
    "C" = @{ code = 0x2E; extended = $false }
    "V" = @{ code = 0x2F; extended = $false }
    "TAB" = @{ code = 0x0F; extended = $false }
    "O" = @{ code = 0x18; extended = $false }
    "ENTER" = @{ code = 0x1C; extended = $false }
    "CTRL" = @{ code = 0x1D; extended = $false }
    "LCTRL" = @{ code = 0x1D; extended = $false }
    "RCTRL" = @{ code = 0x1D; extended = $true }
    "SHIFT" = @{ code = 0x2A; extended = $false }
    "LSHIFT" = @{ code = 0x2A; extended = $false }
    "RSHIFT" = @{ code = 0x36; extended = $false }
    "BACKSLASH" = @{ code = 0x2B; extended = $false }
    "SPACE" = @{ code = 0x39; extended = $false }
    "UP" = @{ code = 0x48; extended = $true }
    "DOWN" = @{ code = 0x50; extended = $true }
    "LEFT" = @{ code = 0x4B; extended = $true }
    "RIGHT" = @{ code = 0x4D; extended = $true }
}

function Parse-InputSequence {
    param([string]$RawSequence)

    $actions = New-Object System.Collections.Generic.List[object]
    $tokens = $RawSequence -split '[,;\r\n]+' | Where-Object { $_.Trim().Length -gt 0 }
    if ($tokens.Count -lt 1 -or $tokens.Count -gt 32) {
        Write-Error "Sequence must contain between 1 and 32 actions."
        exit 1
    }

    foreach ($token in $tokens) {
        $trimmed = $token.Trim()
        $parts = $trimmed -split ':', 2
        if ($parts.Count -ne 2) {
            Write-Error ("Invalid action '{0}'. Use tap:KEY, down:KEY, up:KEY, wait:MS, or click:XxY." -f $trimmed)
            exit 1
        }

        $kind = $parts[0].Trim().ToLowerInvariant()
        $value = $parts[1].Trim().ToUpperInvariant()
        if ($kind -eq "wait") {
            $waitMs = 0
            if (-not [int]::TryParse($value, [ref]$waitMs) -or $waitMs -lt 0 -or $waitMs -gt 5000) {
                Write-Error "wait action must be between 0 and 5000 milliseconds."
                exit 1
            }
            $actions.Add([PSCustomObject]@{
                kind = "wait"
                key = $null
                virtualKey = $null
                durationMs = $waitMs
            }) | Out-Null
            continue
        }

        if ($kind -eq "click") {
            $clickMatch = [regex]::Match($value, '^(\d{1,4})[X,](\d{1,4})$')
            if (-not $clickMatch.Success) {
                Write-Error "click action must be formatted as click:XxY with non-negative client coordinates."
                exit 1
            }
            $clientX = [int]$clickMatch.Groups[1].Value
            $clientY = [int]$clickMatch.Groups[2].Value
            if ($clientX -gt 4096 -or $clientY -gt 4096) {
                Write-Error "click coordinates must be between 0 and 4096."
                exit 1
            }
            $actions.Add([PSCustomObject]@{
                kind = "click"
                key = $null
                virtualKey = $null
                scanCode = $null
                extended = $false
                x = $clientX
                y = $clientY
                durationMs = $null
            }) | Out-Null
            continue
        }

        if (@("tap", "down", "up") -notcontains $kind) {
            Write-Error ("Unsupported action kind '{0}'." -f $kind)
            exit 1
        }
        if (-not $allowedKeys.ContainsKey($value)) {
            Write-Error ("Unsupported key '{0}'." -f $value)
            exit 1
        }
        $actions.Add([PSCustomObject]@{
            kind = $kind
            key = $value
            virtualKey = $allowedKeys[$value]
            scanCode = $scanCodes[$value].code
            extended = $scanCodes[$value].extended
            durationMs = $null
        }) | Out-Null
    }

    return $actions
}

$actions = @(Parse-InputSequence -RawSequence $Sequence)

if ($canaryMode) {
    Import-Module (Join-Path $scriptRoot "runtime_process_identity.psm1") -Force -ErrorAction Stop
    $validatedReceipt = Assert-RuntimeProcessReceipt `
        -ReceiptPath $RuntimeReceiptPath `
        -ExpectedReceiptSha256 $ExpectedReceiptSha256
    $receiptProcessId = [int]$validatedReceipt.Receipt.process.id
    $receiptHwndHex = [string]$validatedReceipt.Receipt.window.hwndHex
    $receiptExecutablePath = [string]$validatedReceipt.Receipt.process.executable.path
    $receiptWorkingDirectory = [string]$validatedReceipt.Receipt.process.workingDirectory
    $receiptProcessName = [System.IO.Path]::GetFileName($receiptExecutablePath)

    if ($ProcessId -gt 0 -and $ProcessId -ne $receiptProcessId) {
        Write-Error ("ProcessId '{0}' does not match runtime receipt process id '{1}'." -f $ProcessId, $receiptProcessId)
        exit 1
    }
    if (-not [string]::IsNullOrWhiteSpace($HwndHex) -and
        -not [string]::Equals($HwndHex, $receiptHwndHex, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error ("HwndHex '{0}' does not match runtime receipt window '{1}'." -f $HwndHex, $receiptHwndHex)
        exit 1
    }
    if (-not [string]::Equals($ProcessName, $receiptProcessName, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error ("ProcessName '{0}' does not match runtime receipt executable '{1}'." -f $ProcessName, $receiptProcessName)
        exit 1
    }
    if (-not [string]::IsNullOrWhiteSpace($ExpectedExecutablePath) -and
        -not [string]::Equals($ExpectedExecutablePath, $receiptExecutablePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error "ExpectedExecutablePath does not match the runtime receipt executable path."
        exit 1
    }
    if (-not [string]::IsNullOrWhiteSpace($ExpectedWorkingDirectory) -and
        -not [string]::Equals($ExpectedWorkingDirectory, $receiptWorkingDirectory, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error "ExpectedWorkingDirectory does not match the runtime receipt working directory."
        exit 1
    }

    $ProcessId = $receiptProcessId
    $HwndHex = $receiptHwndHex
    $ExpectedExecutablePath = $receiptExecutablePath
    $ExpectedWorkingDirectory = $receiptWorkingDirectory
}

if (-not $PrintOnly -and ($ProcessId -le 0 -or [string]::IsNullOrWhiteSpace($HwndHex))) {
    [PSCustomObject]@{
        schemaVersion = "game-window-input.v1"
        generatedAt = (Get-Date).ToString("o")
        mutation = $false
        processName = "$([System.IO.Path]::GetFileNameWithoutExtension($ProcessName)).exe"
        processId = if ($ProcessId -gt 0) { $ProcessId } else { $null }
        hwndHex = if ([string]::IsNullOrWhiteSpace($HwndHex)) { $null } else { $HwndHex }
        status = "target-required"
        plannedOnly = $true
        actionCount = $actions.Count
        actions = @($actions)
        selectedWindow = $null
        note = "Real scoped input sends require both ProcessId and HwndHex. No input was sent."
    } | ConvertTo-Json -Depth 8
    if ($PrintOnly) {
        exit 0
    }

    exit 1
}

if (-not $PrintOnly -and ([string]::IsNullOrWhiteSpace($ExpectedExecutablePath) -or [string]::IsNullOrWhiteSpace($ExpectedWorkingDirectory))) {
    Write-Error "Real scoped input requires ExpectedExecutablePath and ExpectedWorkingDirectory so input cannot target an unrelated BEA.exe window."
    exit 1
}

$resolvedExpectedExecutablePath = $null
$resolvedExpectedWorkingDirectory = $null
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

$nativeType = "GameWindowInputNative"
if (-not ([System.Management.Automation.PSTypeName]$nativeType).Type) {
    Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public static class GameWindowInputNative {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint Msg, UIntPtr wParam, UIntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool GetClientRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool ClientToScreen(IntPtr hWnd, ref POINT point);

    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);

    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    public struct POINT {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT {
        public uint type;
        public InputUnion U;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct InputUnion {
        [FieldOffset(0)]
        public KEYBDINPUT ki;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct KEYBDINPUT {
        public ushort wVk;
        public ushort wScan;
        public uint dwFlags;
        public uint time;
        public UIntPtr dwExtraInfo;
    }

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

    public static bool SendScanKey(ushort scanCode, bool keyUp, bool extended) {
        INPUT[] inputs = new INPUT[1];
        inputs[0].type = 1;
        inputs[0].U.ki.wVk = 0;
        inputs[0].U.ki.wScan = scanCode;
        inputs[0].U.ki.dwFlags = 0x0008 | (keyUp ? 0x0002u : 0u) | (extended ? 0x0001u : 0u);
        inputs[0].U.ki.time = 0;
        inputs[0].U.ki.dwExtraInfo = UIntPtr.Zero;
        return SendInput(1, inputs, Marshal.SizeOf(typeof(INPUT))) == 1;
    }

    public static bool SendClientMouseClick(IntPtr hWnd, int clientX, int clientY) {
        RECT rect;
        if (!GetClientRect(hWnd, out rect)) {
            return false;
        }
        if (clientX < rect.Left || clientY < rect.Top || clientX >= rect.Right || clientY >= rect.Bottom) {
            return false;
        }
        POINT point = new POINT { X = clientX, Y = clientY };
        if (!ClientToScreen(hWnd, ref point)) {
            return false;
        }
        if (!SetCursorPos(point.X, point.Y)) {
            return false;
        }
        mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
        mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
        return true;
    }

    [DllImport("kernel32.dll")]
    public static extern uint GetCurrentThreadId();
}
"@
}

function Resolve-TargetWindow {
    $targetProcessName = [System.IO.Path]::GetFileNameWithoutExtension($ProcessName).ToLowerInvariant()
    $matches = New-Object System.Collections.Generic.List[object]
    $requestedHandle = [IntPtr]::Zero
    if (-not [string]::IsNullOrWhiteSpace($HwndHex)) {
        $handleText = $HwndHex.Trim()
        if ($handleText.StartsWith("0x", [System.StringComparison]::OrdinalIgnoreCase)) {
            $handleText = $handleText.Substring(2)
        }
        $handleValue = [Convert]::ToInt64($handleText, 16)
        $requestedHandle = [IntPtr]::new($handleValue)
    }

    $callback = [GameWindowInputNative+EnumWindowsProc]{
        param([IntPtr]$hWnd, [IntPtr]$lParam)

        if (-not [GameWindowInputNative]::IsWindowVisible($hWnd)) {
            return $true
        }

        [uint32]$windowProcessId = 0
        [void][GameWindowInputNative]::GetWindowThreadProcessId($hWnd, [ref]$windowProcessId)
        if ($windowProcessId -eq 0) {
            return $true
        }

        if ($requestedHandle -ne [IntPtr]::Zero -and $hWnd -ne $requestedHandle) {
            return $true
        }

        if ($ProcessId -gt 0 -and [int]$windowProcessId -ne $ProcessId) {
            return $true
        }

        try {
            $process = Get-Process -Id $windowProcessId -ErrorAction Stop
        } catch {
            return $true
        }

        if ($process.ProcessName.ToLowerInvariant() -ne $targetProcessName) {
            return $true
        }

        $modulePath = $null
        try {
            $modulePath = [System.IO.Path]::GetFullPath($process.MainModule.FileName)
        } catch {
            return $true
        }

        if ($resolvedExpectedExecutablePath -and -not [string]::Equals($modulePath, $resolvedExpectedExecutablePath, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }

        $moduleDirectory = [System.IO.Path]::GetDirectoryName($modulePath)
        if ($resolvedExpectedWorkingDirectory -and -not [string]::Equals(
            $moduleDirectory.TrimEnd([char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)),
            $resolvedExpectedWorkingDirectory,
            [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }

        $titleLength = [GameWindowInputNative]::GetWindowTextLength($hWnd)
        $title = New-Object System.Text.StringBuilder ([Math]::Max($titleLength + 1, 1))
        if ($titleLength -gt 0) {
            [void][GameWindowInputNative]::GetWindowText($hWnd, $title, $title.Capacity)
        }

        $matches.Add([PSCustomObject]@{
            processId = [int]$windowProcessId
            processName = "$($process.ProcessName).exe"
            title = $title.ToString()
            hwndHex = ("0x{0:X}" -f $hWnd.ToInt64())
            minimized = [GameWindowInputNative]::IsIconic($hWnd)
            executablePath = $modulePath
            workingDirectory = $moduleDirectory
            handle = $hWnd
        }) | Out-Null
        return $true
    }

    [void][GameWindowInputNative]::EnumWindows($callback, [IntPtr]::Zero)
    return $matches
}

function Test-ForegroundWindow {
    param([IntPtr]$Handle)
    return ([GameWindowInputNative]::GetForegroundWindow() -eq $Handle)
}

function Set-TargetWindowForeground {
    param([IntPtr]$Handle)

    if ($Handle -eq [IntPtr]::Zero) {
        return $false
    }
    if (Test-ForegroundWindow -Handle $Handle) {
        return $true
    }

    [void][GameWindowInputNative]::ShowWindow($Handle, 9)
    Start-Sleep -Milliseconds 120
    [void][GameWindowInputNative]::BringWindowToTop($Handle)
    [void][GameWindowInputNative]::SetForegroundWindow($Handle)
    Start-Sleep -Milliseconds 160
    if (Test-ForegroundWindow -Handle $Handle) {
        return $true
    }

    $currentThreadId = [GameWindowInputNative]::GetCurrentThreadId()
    $foregroundWindow = [GameWindowInputNative]::GetForegroundWindow()
    [uint32]$foregroundProcessId = 0
    [uint32]$targetProcessId = 0
    $foregroundThreadId = [GameWindowInputNative]::GetWindowThreadProcessId($foregroundWindow, [ref]$foregroundProcessId)
    $targetThreadId = [GameWindowInputNative]::GetWindowThreadProcessId($Handle, [ref]$targetProcessId)
    $attachedForeground = $false
    $attachedTarget = $false

    try {
        if ($foregroundThreadId -ne 0 -and $foregroundThreadId -ne $currentThreadId) {
            $attachedForeground = [GameWindowInputNative]::AttachThreadInput($currentThreadId, $foregroundThreadId, $true)
        }
        if ($targetThreadId -ne 0 -and $targetThreadId -ne $currentThreadId) {
            $attachedTarget = [GameWindowInputNative]::AttachThreadInput($currentThreadId, $targetThreadId, $true)
        }

        [void][GameWindowInputNative]::ShowWindow($Handle, 9)
        [void][GameWindowInputNative]::BringWindowToTop($Handle)
        [void][GameWindowInputNative]::SetForegroundWindow($Handle)
    } finally {
        if ($attachedTarget) {
            [void][GameWindowInputNative]::AttachThreadInput($currentThreadId, $targetThreadId, $false)
        }
        if ($attachedForeground) {
            [void][GameWindowInputNative]::AttachThreadInput($currentThreadId, $foregroundThreadId, $false)
        }
    }

    Start-Sleep -Milliseconds 160
    return (Test-ForegroundWindow -Handle $Handle)
}

function Assert-TargetStillForeground {
    param([IntPtr]$Handle)

    if (-not (Test-ForegroundWindow -Handle $Handle)) {
        Write-Error "Foreground window changed before scoped input delivery; aborting global input."
        exit 1
    }
}

$matches = @(Resolve-TargetWindow)

$status = if ($matches.Count -eq 0) {
    "no-window"
} elseif ($matches.Count -gt 1) {
    "multiple-candidates"
} else {
    "ready"
}

$selected = if ($matches.Count -eq 1) { $matches[0] } else { $null }

if ($PrintOnly -or $status -ne "ready") {
    [PSCustomObject]@{
        schemaVersion = "game-window-input.v1"
        generatedAt = (Get-Date).ToString("o")
        mutation = $false
        processName = "$([System.IO.Path]::GetFileNameWithoutExtension($ProcessName)).exe"
        processId = if ($ProcessId -gt 0) { $ProcessId } else { $null }
        hwndHex = if ($selected) { $selected.hwndHex } else { $HwndHex }
        status = $status
        plannedOnly = $true
        actionCount = $actions.Count
        actions = @($actions)
        selectedWindow = if ($selected) {
            [PSCustomObject]@{
                processId = $selected.processId
                processName = $selected.processName
                title = $selected.title
                hwndHex = $selected.hwndHex
                minimized = $selected.minimized
                executablePath = $selected.executablePath
                workingDirectory = $selected.workingDirectory
            }
        } else { $null }
        note = "Planned scoped input only. No input was sent."
    } | ConvertTo-Json -Depth 8
    if ($PrintOnly) {
        exit 0
    }

    exit 1
}

if ($selected.minimized) {
    [void][GameWindowInputNative]::ShowWindow($selected.handle, 9)
    Start-Sleep -Milliseconds 120
}

$focused = Set-TargetWindowForeground -Handle $selected.handle
$useWindowMessages = -not $focused

if ($useWindowMessages -and (-not $AllowBackgroundWindowMessages -or $BackgroundWindowMessagesArm -ne $backgroundWindowMessageArmPhrase)) {
    [PSCustomObject]@{
        schemaVersion = "game-window-input.v1"
        generatedAt = (Get-Date).ToString("o")
        mutation = $false
        processName = $selected.processName
        processId = $selected.processId
        hwndHex = $selected.hwndHex
        status = "focus-required"
        plannedOnly = $true
        focused = $false
        backgroundWindowMessagesAllowed = $false
        selectedWindow = [PSCustomObject]@{
            processId = $selected.processId
            processName = $selected.processName
            title = $selected.title
            hwndHex = $selected.hwndHex
            minimized = $selected.minimized
            executablePath = $selected.executablePath
            workingDirectory = $selected.workingDirectory
        }
        note = "Focus handoff was denied by Windows; refusing background window messages without -AllowBackgroundWindowMessages and exact BackgroundWindowMessagesArm phrase."
    } | ConvertTo-Json -Depth 8
    exit 1
}

if ($canaryMode) {
    $validatedReceipt = Assert-RuntimeProcessReceipt `
        -ReceiptPath $RuntimeReceiptPath `
        -ExpectedReceiptSha256 $ExpectedReceiptSha256 `
        -RequireWindow
    if ($validatedReceipt.Process.Id -ne $selected.processId -or
        -not [string]::Equals(
            [string]$validatedReceipt.Receipt.window.hwndHex,
            [string]$selected.hwndHex,
            [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error "Runtime receipt process/window identity changed before scoped input delivery."
        exit 1
    }
}

$KEYEVENTF_KEYUP = 0x0002
$KEYEVENTF_EXTENDEDKEY = 0x0001
$KEYEVENTF_SCANCODE = 0x0008
$WM_KEYDOWN = 0x0100
$WM_KEYUP = 0x0101
$WM_LBUTTONDOWN = 0x0201
$WM_LBUTTONUP = 0x0202
$sent = 0
$sendInputEventsSent = 0
$scanKeybdEventsSent = 0
$windowMessageEventsSent = 0
$mouseEventsSent = 0
$heldKeys = [System.Collections.Generic.List[object]]::new()
try {
foreach ($action in $actions) {
    if ($action.kind -eq "wait") {
        Start-Sleep -Milliseconds $action.durationMs
        continue
    }

    if ($action.kind -eq "click") {
        [int]$clientX = [int]$action.x
        [int]$clientY = [int]$action.y
        if ($useWindowMessages) {
            [uint32]$lParam = (($clientY -band 0xFFFF) -shl 16) -bor ($clientX -band 0xFFFF)
            if ([GameWindowInputNative]::PostMessage($selected.handle, $WM_LBUTTONDOWN, [UIntPtr]::new(1), [UIntPtr]::new($lParam))) {
                $windowMessageEventsSent++
                $mouseEventsSent++
            }
            Start-Sleep -Milliseconds $StepDelayMs
            if ([GameWindowInputNative]::PostMessage($selected.handle, $WM_LBUTTONUP, [UIntPtr]::Zero, [UIntPtr]::new($lParam))) {
                $windowMessageEventsSent++
                $mouseEventsSent++
            }
        } else {
            Assert-TargetStillForeground -Handle $selected.handle
            if ([GameWindowInputNative]::SendClientMouseClick($selected.handle, $clientX, $clientY)) {
                $mouseEventsSent += 2
            } else {
                Write-Error ("Could not send scoped mouse click at client coordinates {0},{1}." -f $clientX, $clientY)
                exit 1
            }
        }
        if ($StepDelayMs -gt 0) {
            Start-Sleep -Milliseconds $StepDelayMs
        }
        continue
    }

    [byte]$vk = [byte]$action.virtualKey
    [uint16]$scanCode = [uint16]$action.scanCode
    [bool]$extended = [bool]$action.extended
    if ($action.kind -eq "tap" -or $action.kind -eq "down") {
        if ($useWindowMessages) {
            if ([GameWindowInputNative]::PostMessage($selected.handle, $WM_KEYDOWN, [UIntPtr]::new([uint32]$vk), [UIntPtr]::Zero)) {
                $sent++
                $windowMessageEventsSent++
            }
        } else {
            Assert-TargetStillForeground -Handle $selected.handle
            if ([GameWindowInputNative]::SendScanKey($scanCode, $false, $extended)) {
                $sent++
                $sendInputEventsSent++
            } else {
                $flags = $KEYEVENTF_SCANCODE
                if ($extended) {
                    $flags = $flags -bor $KEYEVENTF_EXTENDEDKEY
                }
                [GameWindowInputNative]::keybd_event(0, [byte]$scanCode, $flags, [UIntPtr]::Zero)
                $sent++
                $scanKeybdEventsSent++
            }
            $heldKeys.Add([PSCustomObject]@{
                scanCode = $scanCode
                extended = $extended
            }) | Out-Null
        }
    }
    if ($action.kind -eq "tap") {
        Start-Sleep -Milliseconds $StepDelayMs
    }
    if ($action.kind -eq "tap" -or $action.kind -eq "up") {
        if ($useWindowMessages) {
            if ([GameWindowInputNative]::PostMessage($selected.handle, $WM_KEYUP, [UIntPtr]::new([uint32]$vk), [UIntPtr]::Zero)) {
                $sent++
                $windowMessageEventsSent++
            }
        } else {
            Assert-TargetStillForeground -Handle $selected.handle
            if ([GameWindowInputNative]::SendScanKey($scanCode, $true, $extended)) {
                $sent++
                $sendInputEventsSent++
            } else {
                $flags = $KEYEVENTF_SCANCODE -bor $KEYEVENTF_KEYUP
                if ($extended) {
                    $flags = $flags -bor $KEYEVENTF_EXTENDEDKEY
                }
                [GameWindowInputNative]::keybd_event(0, [byte]$scanCode, $flags, [UIntPtr]::Zero)
                $sent++
                $scanKeybdEventsSent++
            }
            for ($heldIndex = $heldKeys.Count - 1; $heldIndex -ge 0; $heldIndex--) {
                $heldKey = $heldKeys[$heldIndex]
                if ([uint16]$heldKey.scanCode -eq $scanCode -and [bool]$heldKey.extended -eq $extended) {
                    $heldKeys.RemoveAt($heldIndex)
                    break
                }
            }
        }
    }
    if ($StepDelayMs -gt 0) {
        Start-Sleep -Milliseconds $StepDelayMs
    }
}
} finally {
    for ($index = $heldKeys.Count - 1; $index -ge 0; $index--) {
        $key = $heldKeys[$index]
        try {
            if ([GameWindowInputNative]::SendScanKey([uint16]$key.scanCode, $true, [bool]$key.extended)) {
                $sent++
                $sendInputEventsSent++
            } else {
                $releaseFlags = $KEYEVENTF_SCANCODE -bor $KEYEVENTF_KEYUP
                if ([bool]$key.extended) {
                    $releaseFlags = $releaseFlags -bor $KEYEVENTF_EXTENDEDKEY
                }
                [GameWindowInputNative]::keybd_event(0, [byte]$key.scanCode, $releaseFlags, [UIntPtr]::Zero)
                $sent++
                $scanKeybdEventsSent++
            }
        } catch {
            # Continue attempting key-up for the remaining held keys.
        }
    }
    $heldKeys.Clear()
}

[PSCustomObject]@{
    schemaVersion = "game-window-input.v1"
    generatedAt = (Get-Date).ToString("o")
    mutation = $true
    sideEffect = "issued-bounded-input-events"
    processName = $selected.processName
    processId = $selected.processId
    hwndHex = $selected.hwndHex
    status = "sent"
    plannedOnly = $false
    focused = [bool]$focused
    backgroundWindowMessagesAllowed = [bool]($useWindowMessages -and $AllowBackgroundWindowMessages -and $BackgroundWindowMessagesArm -eq $backgroundWindowMessageArmPhrase)
    actionCount = $actions.Count
    keyEventsSent = $sent
    sendInputEventsSent = $sendInputEventsSent
    scanKeybdEventsSent = $scanKeybdEventsSent
    windowMessageEventsSent = $windowMessageEventsSent
    mouseEventsSent = $mouseEventsSent
    actions = @($actions)
    selectedWindow = [PSCustomObject]@{
        processId = $selected.processId
        processName = $selected.processName
        title = $selected.title
        hwndHex = $selected.hwndHex
        minimized = $selected.minimized
        executablePath = $selected.executablePath
        workingDirectory = $selected.workingDirectory
    }
    note = if ($mouseEventsSent -gt 0 -and $sent -gt 0) {
        "Focused the selected BEA.exe top-level window, rechecked foreground before each global event, then issued bounded scan-code keyboard input and client-coordinate mouse clicks."
    } elseif ($mouseEventsSent -gt 0) {
        "Focused the selected BEA.exe top-level window, rechecked foreground before each global event, then issued bounded client-coordinate mouse clicks."
    } elseif ($useWindowMessages) {
        "Focus handoff was denied by Windows; explicit background-window-message arm phrase was supplied, so bounded key messages were issued directly to the selected BEA.exe top-level window handle."
    } else {
        "Focused the selected BEA.exe top-level window, rechecked foreground before each global event, then issued bounded scan-code keyboard input with SendInput."
    }
} | ConvertTo-Json -Depth 8
