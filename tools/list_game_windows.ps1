param(
    [string]$ProcessName = "BEA.exe",
    [int]$Limit = 20
)

$ErrorActionPreference = "Stop"

if ($Limit -lt 1 -or $Limit -gt 100) {
    Write-Error "Limit must be between 1 and 100."
    exit 1
}

$runningOnWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows
)

if (-not $runningOnWindows) {
    [PSCustomObject]@{
        schemaVersion = "game-window-scan-helper.v1"
        generatedAt = (Get-Date).ToString("o")
        processName = $ProcessName
        status = "unsupported"
        windows = @()
        note = "Window scanning is currently implemented only for Windows top-level windows."
    } | ConvertTo-Json -Depth 8
    exit 0
}

$nativeType = "GameWindowScanNative"
if (-not ([System.Management.Automation.PSTypeName]$nativeType).Type) {
    Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public static class GameWindowScanNative {
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
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }
}
"@
}

$targetProcessName = [System.IO.Path]::GetFileNameWithoutExtension($ProcessName).ToLowerInvariant()
$windows = New-Object System.Collections.Generic.List[object]

$callback = [GameWindowScanNative+EnumWindowsProc]{
    param([IntPtr]$hWnd, [IntPtr]$lParam)

    if ($windows.Count -ge $Limit) {
        return $false
    }

    if (-not [GameWindowScanNative]::IsWindowVisible($hWnd)) {
        return $true
    }

    $titleLength = [GameWindowScanNative]::GetWindowTextLength($hWnd)
    if ($titleLength -le 0) {
        return $true
    }

    [uint32]$windowProcessId = 0
    [void][GameWindowScanNative]::GetWindowThreadProcessId($hWnd, [ref]$windowProcessId)
    if ($windowProcessId -eq 0) {
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

    $title = New-Object System.Text.StringBuilder ($titleLength + 1)
    [void][GameWindowScanNative]::GetWindowText($hWnd, $title, $title.Capacity)

    $rect = New-Object GameWindowScanNative+RECT
    [void][GameWindowScanNative]::GetWindowRect($hWnd, [ref]$rect)
    $handle = $hWnd.ToInt64()

    $windows.Add([PSCustomObject]@{
        processId = [int]$windowProcessId
        processName = "$($process.ProcessName).exe"
        title = $title.ToString()
        hwndHex = ("0x{0:X}" -f $handle)
        visible = $true
        minimized = [GameWindowScanNative]::IsIconic($hWnd)
        bounds = [PSCustomObject]@{
            left = $rect.Left
            top = $rect.Top
            right = $rect.Right
            bottom = $rect.Bottom
            width = [Math]::Max(0, $rect.Right - $rect.Left)
            height = [Math]::Max(0, $rect.Bottom - $rect.Top)
        }
        captureSourceHint = ("window:{0}:{1}" -f $windowProcessId, ("0x{0:X}" -f $handle))
    }) | Out-Null

    return $true
}

[void][GameWindowScanNative]::EnumWindows($callback, [IntPtr]::Zero)

$status = if ($windows.Count -eq 0) {
    "no-window"
} elseif ($windows.Count -eq 1) {
    "ready"
} else {
    "multiple-candidates"
}

[PSCustomObject]@{
    schemaVersion = "game-window-scan-helper.v1"
    generatedAt = (Get-Date).ToString("o")
    processName = "$targetProcessName.exe"
    status = $status
    windows = $windows
    note = "Read-only top-level window scan. No capture stream or input injection was started."
} | ConvertTo-Json -Depth 8
