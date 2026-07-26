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
    # Explicit clicks as "seconds:x:y" in CLIENT coordinates, e.g. "16:219:304".
    # Centre clicks are fine for click-to-start, but menu rows are not at the centre
    # of the frame, so reaching level select needs a real position.
    [string[]]$ClickAt = @(),
    # Key presses as "seconds:VK" using virtual-key codes, e.g. "26:13" for Enter.
    # Needed to get past pages that confirm with the keyboard rather than a click.
    [string[]]$KeyAt = @(),
    # State-driven script. Retail startup timing is NOT deterministic - disk caching
    # alone shifts click-to-start by several seconds between runs, and fixed delays
    # land on the wrong screen and silently capture it. Each step waits for the frame
    # to MATCH A SCREEN SIGNATURE before acting, so the sequence self-synchronises.
    #   "wait R,G,B TOL SECONDS"  block until the client mean is within TOL
    #   "click X,Y"               click at client coordinates
    #   "hover X,Y"               move the cursor without clicking
    #   "key VK"                  press a virtual key
    #   "keydown VK" / "keyup VK" hold a key across other steps. Sustained movement
    #                             input cannot be expressed as a tap, and the level
    #                             only accepts movement once its own script enables
    #                             the player, so the hold has to span a burst.
    #   "shot LABEL"              save a frame as LABEL.png
    #   "probe SECONDS PREFIX"    sample the client mean for SECONDS, logging every
    #                             sample and saving PREFIX-<t>.png whenever the mean
    #                             moves. This is how a NEW screen's signature is
    #                             discovered: an unknown screen cannot be waited on.
    #   "leave R,G,B TOL SECONDS" block until the client mean is NO LONGER within
    #                             TOL. An in-level frame is live 3D and has no
    #                             stable mean to wait ON, so the only crisp,
    #                             reproducible trigger available is the moment the
    #                             PRECEDING static screen stops being on screen.
    #   "mark"                    set t=0 for subsequent burst filenames. Placed
    #                             immediately after "leave", this makes the time
    #                             base of every burst frame explicit rather than
    #                             implied by wall-clock luck.
    #   "burst SECONDS INTERVAL_MS PREFIX"
    #                             save EVERY sampled frame for SECONDS as
    #                             PREFIX-t<ms>ms.png, offset from the last "mark".
    #                             Unlike "probe" it does not compute a mean and does
    #                             not skip unchanged frames: a scripted camera pan
    #                             must be sampled on a schedule, and per-frame mean
    #                             computation costs more than the sample interval.
    #                             Means are recovered offline from the saved PNGs.
    #   "sleep SECONDS"
    [string[]]$Steps = @(),
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
if (-not ('BeaCaptureNativeV2' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class BeaCaptureNativeV2 {
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
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    public const uint KEYEVENTF_KEYUP = 0x0002;
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
    [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd)
    $windowAppeared = Get-Date

    function Get-ClientFrame {
        $cr = New-Object 'BeaCaptureNativeV2+RECT'
        [void][BeaCaptureNativeV2]::GetClientRect($hwnd, [ref]$cr)
        $pt = New-Object 'BeaCaptureNativeV2+POINT'
        [void][BeaCaptureNativeV2]::ClientToScreen($hwnd, [ref]$pt)
        $w = $cr.Right - $cr.Left; $h = $cr.Bottom - $cr.Top
        [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd)
        Start-Sleep -Milliseconds 120
        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $gfx = [System.Drawing.Graphics]::FromImage($bmp)
        $gfx.CopyFromScreen($pt.X, $pt.Y, 0, 0, (New-Object System.Drawing.Size $w, $h))
        $gfx.Dispose()
        return $bmp
    }

    function Get-FrameMean([System.Drawing.Bitmap]$bmp) {
        $r = 0.0; $g = 0.0; $b = 0.0; $n = 0
        for ($y = 0; $y -lt $bmp.Height; $y += 8) {
            for ($x = 0; $x -lt $bmp.Width; $x += 8) {
                $px = $bmp.GetPixel($x, $y); $r += $px.R; $g += $px.G; $b += $px.B; $n++
            }
        }
        return [pscustomobject]@{ R = $r / $n; G = $g / $n; B = $b / $n }
    }

    # A burst must sample on a schedule, so it cannot afford the settle sleep and
    # the foreground re-assert that Get-ClientFrame pays on every call. Foreground
    # is still read per frame and recorded, so a stolen-focus frame is still
    # detectable and discardable - it is just not corrected mid-burst.
    function Get-ClientFrameFast {
        $cr = New-Object 'BeaCaptureNativeV2+RECT'
        [void][BeaCaptureNativeV2]::GetClientRect($hwnd, [ref]$cr)
        $pt = New-Object 'BeaCaptureNativeV2+POINT'
        [void][BeaCaptureNativeV2]::ClientToScreen($hwnd, [ref]$pt)
        $w = $cr.Right - $cr.Left; $h = $cr.Bottom - $cr.Top
        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $gfx = [System.Drawing.Graphics]::FromImage($bmp)
        $gfx.CopyFromScreen($pt.X, $pt.Y, 0, 0, (New-Object System.Drawing.Size $w, $h))
        $gfx.Dispose()
        return $bmp
    }

    $markTime = $windowAppeared
    if ($Steps.Count -gt 0) {
        foreach ($step in $Steps) {
            $tok = $step -split '\s+'
            switch ($tok[0]) {
                'wait' {
                    $want = $tok[1] -split ','
                    $tol = [double]$tok[2]
                    $limit = [double]$tok[3]
                    $deadline2 = (Get-Date).AddSeconds($limit)
                    $matched = $false
                    while ((Get-Date) -lt $deadline2) {
                        $bmp = Get-ClientFrame
                        $m = Get-FrameMean $bmp
                        $bmp.Dispose()
                        $d = [Math]::Abs($m.R - [double]$want[0]) + [Math]::Abs($m.G - [double]$want[1]) + [Math]::Abs($m.B - [double]$want[2])
                        if ($d -le $tol) { $matched = $true; break }
                        Start-Sleep -Milliseconds 400
                    }
                    if (-not $matched) { throw "Timed out after ${limit}s waiting for screen signature $($tok[1]); last mean was $([int]$m.R),$([int]$m.G),$([int]$m.B)." }
                }
                'sleep' { Start-Sleep -Milliseconds ([int]([double]$tok[1] * 1000)) }
                'key' {
                    [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd); Start-Sleep -Milliseconds 150
                    [byte]$vk = [int]$tok[1]; [byte]$sc = 0; [uint32]$dn = 0; [uint32]$up = [BeaCaptureNativeV2]::KEYEVENTF_KEYUP
                    [BeaCaptureNativeV2]::keybd_event($vk, $sc, $dn, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60
                    [BeaCaptureNativeV2]::keybd_event($vk, $sc, $up, [UIntPtr]::Zero)
                }
                'click' {
                    $xy = $tok[1] -split ','
                    $pt = New-Object 'BeaCaptureNativeV2+POINT'
                    [void][BeaCaptureNativeV2]::ClientToScreen($hwnd, [ref]$pt)
                    [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd); Start-Sleep -Milliseconds 150
                    [void][BeaCaptureNativeV2]::SetCursorPos($pt.X + [int]$xy[0], $pt.Y + [int]$xy[1]); Start-Sleep -Milliseconds 120
                    [BeaCaptureNativeV2]::mouse_event([BeaCaptureNativeV2]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60
                    [BeaCaptureNativeV2]::mouse_event([BeaCaptureNativeV2]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [UIntPtr]::Zero)
                }
                'hover' {
                    $xy = $tok[1] -split ','
                    $pt = New-Object 'BeaCaptureNativeV2+POINT'
                    [void][BeaCaptureNativeV2]::ClientToScreen($hwnd, [ref]$pt)
                    [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd); Start-Sleep -Milliseconds 150
                    [void][BeaCaptureNativeV2]::SetCursorPos($pt.X + [int]$xy[0], $pt.Y + [int]$xy[1])
                    Start-Sleep -Milliseconds 400
                }
                'probe' {
                    $limit = [double]$tok[1]
                    $prefix = $tok[2]
                    $end = (Get-Date).AddSeconds($limit)
                    $last = $null
                    while ((Get-Date) -lt $end) {
                        $bmp = Get-ClientFrame
                        $m = Get-FrameMean $bmp
                        $t = [int]((Get-Date) - $windowAppeared).TotalSeconds
                        $fg = [BeaCaptureNativeV2]::GetForegroundWindow()
                        $sig = "{0},{1},{2}" -f [int]$m.R, [int]$m.G, [int]$m.B
                        Write-Host ("PROBE {0} t={1}s mean={2} fg={3}" -f $prefix, $t, $sig, ($fg -eq $hwnd))
                        $moved = $true
                        if ($null -ne $last) {
                            $d = [Math]::Abs($m.R - $last.R) + [Math]::Abs($m.G - $last.G) + [Math]::Abs($m.B - $last.B)
                            # Frontend pages differ from each other by only a few
                            # units of mean, so a coarse threshold hides transitions.
                            $moved = $d -gt 2
                        }
                        if ($moved) {
                            $path = Join-Path $OutputDirectory ("{0}-t{1:d3}s.png" -f $prefix, $t)
                            $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
                            $shots += [pscustomobject]@{ label = "$prefix-t${t}s"; secondsAfterWindow = $t; width = $bmp.Width; height = $bmp.Height; printWindowOk = ($fg -eq $hwnd); mean = $sig }
                            $last = $m
                        }
                        $bmp.Dispose()
                        Start-Sleep -Milliseconds 700
                    }
                }
                'keydown' {
                    [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd); Start-Sleep -Milliseconds 150
                    [byte]$vk = [int]$tok[1]
                    [BeaCaptureNativeV2]::keybd_event($vk, 0, 0, [UIntPtr]::Zero)
                }
                'keyup' {
                    [byte]$vk = [int]$tok[1]
                    [BeaCaptureNativeV2]::keybd_event($vk, 0, [BeaCaptureNativeV2]::KEYEVENTF_KEYUP, [UIntPtr]::Zero)
                }
                'leave' {
                    $want = $tok[1] -split ','
                    $tol = [double]$tok[2]
                    $limit = [double]$tok[3]
                    $deadline3 = (Get-Date).AddSeconds($limit)
                    $left = $false
                    while ((Get-Date) -lt $deadline3) {
                        $bmp = Get-ClientFrameFast
                        $m = Get-FrameMean $bmp
                        $bmp.Dispose()
                        $d = [Math]::Abs($m.R - [double]$want[0]) + [Math]::Abs($m.G - [double]$want[1]) + [Math]::Abs($m.B - [double]$want[2])
                        if ($d -gt $tol) { $left = $true; break }
                    }
                    if (-not $left) { throw "Timed out after ${limit}s waiting for the client mean to LEAVE $($tok[1]); last mean was $([int]$m.R),$([int]$m.G),$([int]$m.B)." }
                    Write-Host ("LEAVE {0} at t={1:F2}s after window; mean now {2},{3},{4}" -f $tok[1], ((Get-Date) - $windowAppeared).TotalSeconds, [int]$m.R, [int]$m.G, [int]$m.B)
                }
                'mark' {
                    $markTime = Get-Date
                    Write-Host ("MARK t0 set at {0:F2}s after window" -f ($markTime - $windowAppeared).TotalSeconds)
                }
                'burst' {
                    $limit = [double]$tok[1]
                    $interval = [double]$tok[2]
                    $prefix = $tok[3]
                    $end = (Get-Date).AddSeconds($limit)
                    $next = Get-Date
                    while ((Get-Date) -lt $end) {
                        $now = Get-Date
                        if ($now -lt $next) { Start-Sleep -Milliseconds ([Math]::Max(1, [int](($next - $now).TotalMilliseconds))) }
                        $ms = [int]((Get-Date) - $markTime).TotalMilliseconds
                        $bmp = Get-ClientFrameFast
                        $fg = [BeaCaptureNativeV2]::GetForegroundWindow()
                        $path = Join-Path $OutputDirectory ("{0}-t{1:d6}ms.png" -f $prefix, $ms)
                        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
                        $shots += [pscustomobject]@{ label = ("{0}-t{1:d6}ms" -f $prefix, $ms); secondsAfterWindow = [int]((Get-Date) - $windowAppeared).TotalSeconds; offsetMsFromMark = $ms; width = $bmp.Width; height = $bmp.Height; printWindowOk = ($fg -eq $hwnd); mean = '' }
                        $bmp.Dispose()
                        $next = $next.AddMilliseconds($interval)
                    }
                }
                'shot' {
                    $bmp = Get-ClientFrame
                    $path = Join-Path $OutputDirectory ("{0}.png" -f $tok[1])
                    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
                    $fg = [BeaCaptureNativeV2]::GetForegroundWindow()
                    $sm = Get-FrameMean $bmp
                    $shots += [pscustomobject]@{ label = $tok[1]; secondsAfterWindow = [int]((Get-Date) - $windowAppeared).TotalSeconds; width = $bmp.Width; height = $bmp.Height; printWindowOk = ($fg -eq $hwnd); mean = ("{0},{1},{2}" -f [int]$sm.R, [int]$sm.G, [int]$sm.B) }
                    $bmp.Dispose()
                }
                default { throw "Unknown step verb '$($tok[0])' in '$step'." }
            }
        }
    }
    else {

    # Clicks and shots share one ordered timeline so a click always lands before
    # the shot that is meant to observe its effect.
    $events = @()
    foreach ($t in $ClickAtSeconds) { $events += [pscustomobject]@{ At = $t; Kind = 'click'; X = $null; Y = $null } }
    foreach ($spec in $ClickAt) {
        $parts = $spec -split ':'
        if ($parts.Count -ne 3) { throw "Malformed -ClickAt '$spec'. Expected seconds:x:y." }
        $events += [pscustomobject]@{ At = [int]$parts[0]; Kind = 'click'; X = [int]$parts[1]; Y = [int]$parts[2] }
    }
    foreach ($spec in $KeyAt) {
        $parts = $spec -split ':'
        if ($parts.Count -ne 2) { throw "Malformed -KeyAt '$spec'. Expected seconds:virtualKeyCode." }
        $events += [pscustomobject]@{ At = [int]$parts[0]; Kind = 'key'; X = [int]$parts[1]; Y = $null }
    }
    foreach ($t in $CaptureSecondsAfterWindow) { $events += [pscustomobject]@{ At = $t; Kind = 'shot'; X = $null; Y = $null } }
    $events = @($events | Sort-Object At, @{ Expression = { $_.Kind }; Descending = $false })

    foreach ($event in $events) {
        $offset = $event.At
        $wait = $offset - ((Get-Date) - $windowAppeared).TotalSeconds
        if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }

        if ($event.Kind -eq 'key') {
            [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd)
            Start-Sleep -Milliseconds 150
            [byte]$vk = $event.X
            [byte]$scan = 0
            [uint32]$down = 0
            [uint32]$up = [BeaCaptureNativeV2]::KEYEVENTF_KEYUP
            [BeaCaptureNativeV2]::keybd_event($vk, $scan, $down, [UIntPtr]::Zero)
            Start-Sleep -Milliseconds 60
            [BeaCaptureNativeV2]::keybd_event($vk, $scan, $up, [UIntPtr]::Zero)
            Write-Verbose "pressed VK $($event.X) at ${offset}s"
            continue
        }

        if ($event.Kind -eq 'click') {
            $cr = New-Object 'BeaCaptureNativeV2+RECT'
            [void][BeaCaptureNativeV2]::GetClientRect($hwnd, [ref]$cr)
            $pt = New-Object 'BeaCaptureNativeV2+POINT'
            [void][BeaCaptureNativeV2]::ClientToScreen($hwnd, [ref]$pt)
            if ($null -ne $event.X) {
                $cx = $pt.X + $event.X
                $cy = $pt.Y + $event.Y
            }
            else {
                $cx = $pt.X + [int](($cr.Right - $cr.Left) / 2)
                $cy = $pt.Y + [int](($cr.Bottom - $cr.Top) / 2) + $ClickOffsetY
            }
            [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd)
            Start-Sleep -Milliseconds 150
            [void][BeaCaptureNativeV2]::SetCursorPos($cx, $cy)
            Start-Sleep -Milliseconds 120
            [BeaCaptureNativeV2]::mouse_event([BeaCaptureNativeV2]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [UIntPtr]::Zero)
            Start-Sleep -Milliseconds 60
            [BeaCaptureNativeV2]::mouse_event([BeaCaptureNativeV2]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [UIntPtr]::Zero)
            Write-Verbose "clicked client centre at ${offset}s ($cx,$cy)"
            continue
        }

        # PrintWindow renders the WHOLE window, chrome included. Capture at full
        # window size and then crop to the client area, otherwise the title bar
        # shifts the frame and every subsequent coordinate comparison is off by the
        # border height - which would look exactly like a layout bug.
        $clientRect = New-Object 'BeaCaptureNativeV2+RECT'
        $windowRect = New-Object 'BeaCaptureNativeV2+RECT'
        [void][BeaCaptureNativeV2]::GetClientRect($hwnd, [ref]$clientRect)
        [void][BeaCaptureNativeV2]::GetWindowRect($hwnd, [ref]$windowRect)
        $w = $clientRect.Right - $clientRect.Left; $h = $clientRect.Bottom - $clientRect.Top
        if ($w -le 0 -or $h -le 0) { throw "Client rect is empty; window not ready." }

        $origin = New-Object 'BeaCaptureNativeV2+POINT'
        [void][BeaCaptureNativeV2]::ClientToScreen($hwnd, [ref]$origin)
        $offsetX = $origin.X - $windowRect.Left
        $offsetY = $origin.Y - $windowRect.Top
        # PrintWindow returns a blank (white) client area for this D3D surface, so
        # read the composited pixels off the desktop at the client rect's screen
        # position instead. This requires the window to be foreground and
        # unobstructed, which is why SetForegroundWindow is re-asserted per shot.
        [void][BeaCaptureNativeV2]::SetForegroundWindow($hwnd)
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
        $foreground = [BeaCaptureNativeV2]::GetForegroundWindow()
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
