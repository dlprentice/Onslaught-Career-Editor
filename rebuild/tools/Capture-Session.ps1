# SPDX-License-Identifier: GPL-3.0-or-later
#
# Record a WINDOW REGION to mp4 with ffmpeg gdigrab, for parity EVIDENCE.
#
# Why this exists: screenshot pairs prove single settled frames, but several
# frontend parity questions are about TRANSITIONS - click-to-start reaching the
# main menu, a hover highlight appearing, an animated underlay moving. A clip
# answers those in one artifact where a frame burst cannot prove ordering. The
# pipeline was verified end-to-end by the integration owner (gdigrab -> mp4 ->
# multimodal clip review) before this script existed; this script makes that
# pipeline reproducible instead of folklore (see Capture-Retail.ps1's header on
# evidence whose method did not survive).
#
# Contract:
#   ./Capture-Session.ps1 -WindowTitle <substring> -DurationSeconds <n> `
#       -OutputPath <clip.mp4>
# Resolves ONE visible top-level window by title substring, records exactly
# that screen rectangle for the requested duration at 15 fps, and writes a
# sidecar manifest (<clip>.manifest.json) carrying the clip's SHA-256, the
# resolved window identity, and the exact ffmpeg arguments. VIDEO-EVIDENCE.md
# defines how a parity claim references that manifest.
#
# Refusals are deliberate, matching this repository's consumer-side posture:
#   * Ambiguous title match -> refused. Recording the WRONG window would mint
#     confident-looking evidence about the wrong pixels; listing candidates
#     costs one rerun, mislabelled evidence costs a review cycle.
#   * Minimized or zero-area window -> refused; there is nothing to record.
#   * Existing output clip -> refused without -Force. An evidence clip is
#     never silently overwritten (same reasoning as the d3d9.dll stray check
#     in Capture-Retail.ps1).
#   * ffmpeg missing -> refused before any window is touched.
#
# Known limitation (documented in VIDEO-EVIDENCE.md): gdigrab here captures a
# FIXED SCREEN RECTANGLE sampled at start. If the window moves, resizes,
# occludes itself, or closes mid-recording, the clip keeps showing whatever now
# occupies that rectangle. Reviewers must treat post-hoc "the window moved"
# explanations as invalid; re-record instead.
#
# Exit codes: 0 success; 2 window not found / ambiguous; 3 environment or
# target problem (no ffmpeg, minimized, zero-area, output exists); 4 ffmpeg
# failed or timed out.

[CmdletBinding()]
param(
    # Substring of a VISIBLE top-level window title (case-insensitive). An
    # exact title match wins over substring matches.
    [Parameter(Mandatory)]
    [string]$WindowTitle,

    # Seconds of footage. The clip is exactly this long unless ffmpeg dies.
    [Parameter(Mandatory)]
    [ValidateRange(1, 3600)]
    [int]$DurationSeconds,

    # Output clip path (.mp4). A sibling .manifest.json and .ffmpeg.log are
    # written next to it.
    [Parameter(Mandatory)]
    [string]$OutputPath,

    [int]$FrameRate = 15,

    # Override only for tests / non-PATH ffmpeg installs.
    [string]$FfmpegPath = 'ffmpeg',

    # Allow overwriting an existing clip. Evidence clips should normally be
    # append-only in local-lab; -Force exists for retakes after a spoiled run.
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# --- exit-code helpers -------------------------------------------------------

function Write-Fail {
    param(
        [Parameter(Mandatory)][int]$Code,
        [Parameter(Mandatory)][string]$Message
    )
    Write-Error -Message $Message -Category ([System.Management.Automation.ErrorCategory]::InvalidOperation) -ErrorAction Continue
    exit $Code
}

# --- preflight: ffmpeg -------------------------------------------------------

$ffCommand = Get-Command -Name $FfmpegPath -ErrorAction SilentlyContinue
if ($null -eq $ffCommand) {
    Write-Fail -Code 3 -Message "ffmpeg was not found as '$FfmpegPath'. Install ffmpeg or pass -FfmpegPath with a full path."
}

# --- preflight: output location ----------------------------------------------

$OutputPath = [IO.Path]::GetFullPath($OutputPath)
if ([IO.Path]::GetExtension($OutputPath) -ine '.mp4') {
    Write-Fail -Code 3 -Message "OutputPath must end in .mp4 (got '$OutputPath'); the evidence protocol keys manifests off .mp4 clips."
}
if (-not $Force -and (Test-Path -LiteralPath $OutputPath)) {
    Write-Fail -Code 3 -Message "Refusing to overwrite existing clip '$OutputPath'. Pass -Force only for a deliberate retake."
}
$outputDir = Split-Path -Parent $OutputPath
if ([string]::IsNullOrEmpty($outputDir)) { $outputDir = (Get-Location).Path }
if (-not (Test-Path -LiteralPath $outputDir)) {
    $null = [IO.Directory]::CreateDirectory($outputDir)
}

# --- win32 interop -----------------------------------------------------------

if (-not ('CaptureSessionNative' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class CaptureSessionNative {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    // gdigrab measures in PHYSICAL pixels. A non-DPI-aware caller gets
    // virtualized coordinates and the recording drifts off the window on any
    // scaled display, so opt this process in before measuring.
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
'@
}
[void][CaptureSessionNative]::SetProcessDPIAware()

function Get-CandidateWindows {
    # Returns one record per VISIBLE top-level window: hwnd, title, rect.
    # Factored out so tests can inject synthetic candidates.
    $candidates = New-Object System.Collections.ArrayList
    $cb = [CaptureSessionNative+EnumWindowsProc]{
        param($hWnd, $lParam)
        if ([CaptureSessionNative]::IsWindowVisible($hWnd)) {
            $len = [CaptureSessionNative]::GetWindowTextLength($hWnd)
            if ($len -gt 0) {
                $sb = New-Object System.Text.StringBuilder ($len + 1)
                [void][CaptureSessionNative]::GetWindowText($hWnd, $sb, $sb.Capacity)
                $rect = New-Object 'CaptureSessionNative+RECT'
                if ([CaptureSessionNative]::GetWindowRect($hWnd, [ref]$rect)) {
                    [void]$candidates.Add([pscustomobject]@{
                        Hwnd  = $hWnd
                        Title = $sb.ToString()
                        Left = $rect.Left; Top = $rect.Top
                        Width = $rect.Right - $rect.Left; Height = $rect.Bottom - $rect.Top
                    })
                }
            }
        }
        return $true
    }
    [void][CaptureSessionNative]::EnumWindows($cb, [IntPtr]::Zero)
    # Plain return: the ArrayList unrolls into the pipeline element-by-element,
    # so the caller's @(Get-CandidateWindows) collects a FLAT record array.
    # (A comma-protected `return ,$candidates` would hand the caller a
    # one-element array CONTAINING the list; member enumeration on that made
    # every Where-Object filter match the whole list at once.)
    return $candidates
}

function Resolve-CaptureWindow {
    # Pick THE window for a recording. Exact title beats substring; anything
    # else is ambiguous and refused with the candidate list.
    param([Parameter(Mandatory)][string]$TitleSubstring)

    $candidates = @(Get-CandidateWindows)
    $exact = @($candidates | Where-Object { $_.Title -ceq $TitleSubstring })
    if ($exact.Count -eq 1) { return $exact[0] }

    # `$matches` is a read-only-ish automatic variable (last -match results);
    # shadowing it is a trap, so this uses its own name.
    $substringHits = @($candidates | Where-Object { $_.Title.ToLowerInvariant().Contains($TitleSubstring.ToLowerInvariant()) })
    if ($substringHits.Count -eq 1) { return $substringHits[0] }

    $known = @($candidates | Select-Object -First 12 -ExpandProperty Title)
    if ($substringHits.Count -gt 1) {
        throw ("Ambiguous -WindowTitle '{0}': matches {1} visible windows ({2}). " +
               'Refining the substring is cheaper than reviewing evidence from the wrong window.') -f
              $TitleSubstring, $substringHits.Count, (($substringHits | Select-Object -First 8 -ExpandProperty Title) -join ' | ')
    }
    throw ("No visible window title contains '{0}'. Visible titles include: {1}.") -f
           $TitleSubstring, (($known -join ' | '))
}

# --- resolve the target ------------------------------------------------------

try {
    $target = Resolve-CaptureWindow -TitleSubstring $WindowTitle
}
catch {
    Write-Fail -Code 2 -Message $_.Exception.Message
}

$native = New-Object 'CaptureSessionNative+RECT'
[void][CaptureSessionNative]::GetWindowRect($target.Hwnd, [ref]$native)
$left = $native.Left; $top = $native.Top
$width = $native.Right - $native.Left; $height = $native.Bottom - $native.Top

if ([CaptureSessionNative]::IsIconic($target.Hwnd)) {
    Write-Fail -Code 3 -Message ("Window '{0}' is minimized; restore it before recording." -f $target.Title)
}
if ($width -le 0 -or $height -le 0) {
    Write-Fail -Code 3 -Message ("Window '{0}' reports a degenerate client area {1}x{2}; refusing to record." -f $target.Title, $width, $height)
}

# --- encode ------------------------------------------------------------------

$startedUtc = (Get-Date).ToUniversalTime()
# Precompute values that need operators OUTSIDE the array literal. A binary
# operator mid-literal ("-video_size", "{0}x{1}" -f $w, $h, ...) corrupted the
# parse of every following element here: the array silently collapsed to its
# first chunk, ffmpeg received a mangled command line, and the failure surfaced
# only as a confusing muxer error. Measured, not assumed - see the bisect in
# this lane's notes.
$videoSizeArg = '{0}x{1}' -f $width, $height
$ffmpegArgs = @(
    '-y',
    '-f', 'gdigrab',
    '-framerate', "$FrameRate",
    '-offset_x', "$left",
    '-offset_y', "$top",
    '-video_size', $videoSizeArg,
    '-draw_mouse', '1',
    '-i', 'desktop',
    '-t', "$DurationSeconds",
    '-c:v', 'libx264',
    '-preset', 'veryfast',
    '-crf', '23',
    # libx264+yuv420p rejects odd dimensions, and real window rects are often
    # odd (e.g. 641x481). Scale to even rather than fail; rectScaledToEven in
    # the manifest says when this fired so a reviewer knows the clip can be
    # 1px narrower/shorter than the recorded rectangle.
    '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
    '-pix_fmt', 'yuv420p',
    $OutputPath
)
if ($ffmpegArgs.Count -lt 10) {
    # Guard against the silent-collapse class of bug ever returning.
    Write-Fail -Code 3 -Message ("ffmpeg argument array built wrong (count {0}); refusing to launch." -f $ffmpegArgs.Count)
}

Write-Host ("Recording '{0}' (hwnd {1}) at {2}x{3}+({4},{5}) for {6}s @ {7} fps -> {8}" -f
    $target.Title, $target.Hwnd, $width, $height, $left, $top, $DurationSeconds, $FrameRate, $OutputPath)

# Launch ffmpeg with an EXPLICIT arguments string via ProcessStartInfo.
# Start-Process was tried here first: its ArgumentList joining proved opaque
# (a single pre-joined string arrived as ONE quoted argument; the raw array
# form mangled the option block in ways the ffmpeg banner exposed only as
# "Unrecognized option"/"format not known"). A raw argument string leaves
# nothing for a helper to reinterpret: spaces separate options, and ONLY the
# output path carries quotes because it is the only element that may contain
# spaces.
$ffmpegArgsForCli = ($ffmpegArgs[0..($ffmpegArgs.Count - 2)] -join ' ') + (' "{0}"' -f $OutputPath)

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $ffCommand.Source
$psi.Arguments = $ffmpegArgsForCli
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$proc = [System.Diagnostics.Process]::Start($psi)
# Drain both pipes concurrently: an undrained pipe fills (~4 KB) and stalls
# ffmpeg mid-encode, which would look exactly like a timeout below.
$outTask = $proc.StandardOutput.ReadToEndAsync()
$errTask = $proc.StandardError.ReadToEndAsync()
$timeoutMs = $DurationSeconds * 1000 + 60000
if (-not $proc.WaitForExit($timeoutMs)) {
    try { $proc.Kill(); $proc.WaitForExit(5000) | Out-Null } catch { }
    Write-Fail -Code 4 -Message "ffmpeg did not finish within $([int]($timeoutMs / 1000))s and was killed."
}
$ffmpegLog = "$OutputPath.ffmpeg.log"
Set-Content -LiteralPath $ffmpegLog -Value $errTask.GetAwaiter().GetResult() -Encoding UTF8
if ($proc.ExitCode -ne 0) {
    $tail = (Get-Content -LiteralPath $ffmpegLog -Tail 12) -join "`n"
    Write-Fail -Code 4 -Message "ffmpeg exited $($proc.ExitCode). Log tail:`n$tail"
}

if (-not (Test-Path -LiteralPath $OutputPath)) {
    Write-Fail -Code 4 -Message 'ffmpeg exited 0 but produced no clip file.'
}

# --- sidecar manifest --------------------------------------------------------

$finishedUtc = (Get-Date).ToUniversalTime()
$bytes = (Get-Item -LiteralPath $OutputPath).Length
$sha = (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLowerInvariant()

$manifest = [pscustomobject]@{
    schemaVersion    = 1
    clipPath         = $OutputPath
    clipSha256       = $sha
    clipBytes        = $bytes
    windowTitle      = $target.Title
    hwnd             = $target.Hwnd
    rect             = [pscustomobject]@{ x = $left; y = $top; w = $width; h = $height }
    rectScaledToEven = (($width % 2) -ne 0 -or ($height % 2) -ne 0)
    frameRate        = $FrameRate
    durationSeconds  = $DurationSeconds
    drawMouse        = $true
    audio            = $false
    startedUtc       = $startedUtc.ToString('o')
    finishedUtc      = $finishedUtc.ToString('o')
    ffmpegArgs       = ($ffmpegArgs -join ' ')
}
$manifestPath = "$OutputPath.manifest.json"
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

Write-Host ('Clip: {0}' -f $OutputPath)
Write-Host ('SHA-256: {0} ({1} bytes)' -f $sha, $bytes)
Write-Host ('Manifest: {0}' -f $manifestPath)
