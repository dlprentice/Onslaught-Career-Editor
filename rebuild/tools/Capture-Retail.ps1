# SPDX-License-Identifier: GPL-3.0-or-later
#
# Deterministic retail frame capture from a COPIED, non-installed target.
#
# Why this exists: the reference PNGs in
# local-lab/startup-parity-ghidra-ro-2026-07-23/captures/ are real evidence, but the
# script that produced them did not survive. Evidence whose method is unreproducible
# decays into folklore, and this project has already been bitten by a reference frame
# nobody could re-derive (the "V1.00 - PATCHED" version overlay).
#
# Target contract: this script REFUSES to run against the Steam install or against
# pristine BEA.exe. It only accepts a copied build, and it records the target hash in
# the manifest so any frame can be traced back to the exact bytes that drew it.
#
# The recommended target is the "capture build": pristine BEA.exe with ONLY
# force_windowed applied (5 bytes at file offset 0x12A644). That is the minimum
# change needed to get a grabbable window, and it provably does not alter frontend
# geometry - the windowed path takes the backbuffer from the window client rect and
# never consults the display-mode list. The version overlay and the 4:3 reject gate
# are deliberately left pristine so nothing cosmetic leaks into the reference.

[CmdletBinding()]
param(
    [string]$TargetRoot = "$PSScriptRoot\..\..\local-lab\safe-copy-bea-pristine",
    [string]$OutputDirectory,
    [int[]]$CaptureSecondsAfterWindow = @(2, 6, 10),
    # Seconds after the window appears at which to click the client centre.
    # The released frontend advances click-to-start on a real mouse click; the game
    # polls input rather than reading the message queue, so a posted message is not
    # enough and synthetic SendInput-level events are required.
    [int[]]$ClickAtSeconds = @(),
    [int]$ClickOffsetY = 0,
    [int]$TimeoutSeconds = 90,
    [switch]$SkipFmv = $true
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$TargetRoot = [IO.Path]::GetFullPath($TargetRoot)
$exe = Join-Path $TargetRoot 'BEA.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw "No BEA.exe under $TargetRoot" }

# --- refuse to touch anything that is not a copied target -------------------
$installRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila'
if ($TargetRoot.TrimEnd('\') -ieq $installRoot.TrimEnd('\')) {
    throw "Refusing to run against the Steam install. Use a copied target."
}
$hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
if ($hash -ieq '74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750') {
    throw ("Target is unmodified pristine BEA.exe. It runs fullscreen (m_bWindowed is " +
           "BSS with no writer), which this window-grab capture cannot read. Apply " +
           "force_windowed (0x12A644) to the COPY first.")
}

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $OutputDirectory = Join-Path ([IO.Path]::GetFullPath("$PSScriptRoot\..\..")) "local-lab\retail-captures\$stamp"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
$null = [IO.Directory]::CreateDirectory($OutputDirectory)

Add-Type -AssemblyName System.Drawing
if (-not ('Win32CaptureNative' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Win32CaptureNative {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT lpPoint);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP   = 0x0004;
}
'@
}

$arguments = @()
if ($SkipFmv) { $arguments += '-skipfmv' }

$process = Start-Process -FilePath $exe -WorkingDirectory $TargetRoot -ArgumentList $arguments -PassThru
$shots = @()
try {
    # Wait for a real main window handle rather than sleeping a fixed amount.
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $process.Refresh()
        if ($process.HasExited) { throw "Target exited before presenting a window." }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) { break }
        Start-Sleep -Milliseconds 250
    }
    $hwnd = $process.MainWindowHandle
    if ($hwnd -eq [IntPtr]::Zero) { throw "No window appeared within $TimeoutSeconds s." }
    [void][Win32CaptureNative]::SetForegroundWindow($hwnd)
    $windowAppeared = Get-Date

    # Clicks and shots share one ordered timeline so a click always lands before
    # the shot that is meant to observe its effect.
    $events = @()
    foreach ($t in $ClickAtSeconds) { $events += [pscustomobject]@{ At = $t; Kind = 'click' } }
    foreach ($t in $CaptureSecondsAfterWindow) { $events += [pscustomobject]@{ At = $t; Kind = 'shot' } }
    $events = @($events | Sort-Object At, @{ Expression = { $_.Kind }; Descending = $false })

    foreach ($event in $events) {
        $offset = $event.At
        $wait = $offset - ((Get-Date) - $windowAppeared).TotalSeconds
        if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }

        if ($event.Kind -eq 'click') {
            $cr = New-Object 'Win32CaptureNative+RECT'
            [void][Win32CaptureNative]::GetClientRect($hwnd, [ref]$cr)
            $pt = New-Object 'Win32CaptureNative+POINT'
            [void][Win32CaptureNative]::ClientToScreen($hwnd, [ref]$pt)
            $cx = $pt.X + [int](($cr.Right - $cr.Left) / 2)
            $cy = $pt.Y + [int](($cr.Bottom - $cr.Top) / 2) + $ClickOffsetY
            [void][Win32CaptureNative]::SetForegroundWindow($hwnd)
            Start-Sleep -Milliseconds 150
            [void][Win32CaptureNative]::SetCursorPos($cx, $cy)
            Start-Sleep -Milliseconds 120
            [Win32CaptureNative]::mouse_event([Win32CaptureNative]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [UIntPtr]::Zero)
            Start-Sleep -Milliseconds 60
            [Win32CaptureNative]::mouse_event([Win32CaptureNative]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [UIntPtr]::Zero)
            Write-Verbose "clicked client centre at ${offset}s ($cx,$cy)"
            continue
        }

        # PrintWindow renders the WHOLE window, chrome included. Capture at full
        # window size and then crop to the client area, otherwise the title bar
        # shifts the frame and every subsequent coordinate comparison is off by the
        # border height - which would look exactly like a layout bug.
        $clientRect = New-Object 'Win32CaptureNative+RECT'
        $windowRect = New-Object 'Win32CaptureNative+RECT'
        [void][Win32CaptureNative]::GetClientRect($hwnd, [ref]$clientRect)
        [void][Win32CaptureNative]::GetWindowRect($hwnd, [ref]$windowRect)
        $w = $clientRect.Right - $clientRect.Left; $h = $clientRect.Bottom - $clientRect.Top
        if ($w -le 0 -or $h -le 0) { throw "Client rect is empty; window not ready." }

        $origin = New-Object 'Win32CaptureNative+POINT'
        [void][Win32CaptureNative]::ClientToScreen($hwnd, [ref]$origin)
        $offsetX = $origin.X - $windowRect.Left
        $offsetY = $origin.Y - $windowRect.Top
        # PrintWindow returns a blank (white) client area for this D3D surface, so
        # read the composited pixels off the desktop at the client rect's screen
        # position instead. This requires the window to be foreground and
        # unobstructed, which is why SetForegroundWindow is re-asserted per shot.
        [void][Win32CaptureNative]::SetForegroundWindow($hwnd)
        Start-Sleep -Milliseconds 200

        $bitmap = New-Object System.Drawing.Bitmap $w, $h
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($origin.X, $origin.Y, 0, 0, (New-Object System.Drawing.Size $w, $h))
        $graphics.Dispose()

        # A frame that is a single flat colour means the grab missed the surface
        # (occluded, minimised, or not yet presented). Record it rather than
        # letting a blank PNG enter the reference set as though it were a frame.
        $probe = @($bitmap.GetPixel(4, 4), $bitmap.GetPixel([int]($w / 2), [int]($h / 2)), $bitmap.GetPixel($w - 5, $h - 5))
        $notFlat = @($probe | Select-Object -Unique).Count -gt 1

        # A desktop-region grab reads whatever is physically on screen. If the
        # workstation locks, or another window steals focus, that is the lock screen
        # or the intruding window - not the game - and it will look like a perfectly
        # valid, non-flat frame. This has already happened once and produced
        # Windows lock-screen PNGs sitting in a retail reference directory.
        $foreground = [Win32CaptureNative]::GetForegroundWindow()
        $isTarget = $foreground -eq $hwnd
        if (-not $isTarget) {
            Write-Warning ("Shot at ${offset}s: target window is NOT foreground " +
                "(got handle $foreground). The session may be locked. This frame is " +
                "NOT trustworthy as a retail reference.")
        }
        $ok = $notFlat -and $isTarget

        $name = 'retail-t{0:d3}s.png' -f $offset
        $path = Join-Path $OutputDirectory $name
        $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        $bitmap.Dispose()

        $shots += [pscustomobject]@{ label = $name; secondsAfterWindow = $offset; width = $w; height = $h; printWindowOk = $ok }
    }
}
finally {
    if (-not $process.HasExited) { $process.Kill($true); $null = $process.WaitForExit(5000) }
}

$manifest = [pscustomobject]@{
    schema = 'onslaught-retail-capture.v1'
    targetRoot = $TargetRoot
    targetSha256 = $hash
    targetNote = 'pristine BEA.exe + force_windowed only (0x12A644); version overlay and 4:3 gate left pristine'
    skipFmv = [bool]$SkipFmv
    shots = $shots
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $OutputDirectory 'retail-capture-manifest.json')

[pscustomobject]@{
    Status = if (@($shots | Where-Object { -not $_.printWindowOk }).Count -eq 0 -and @($shots).Count -gt 0) { 'PASS' } else { 'SUSPECT' }
    TargetSha256 = $hash
    Shots = $shots.Count
    Sizes = ($shots | ForEach-Object { "$($_.width)x$($_.height)" } | Sort-Object -Unique) -join ','
    OutputDirectory = $OutputDirectory
}
