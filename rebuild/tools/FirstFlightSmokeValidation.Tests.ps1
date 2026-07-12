# SPDX-License-Identifier: GPL-3.0-or-later

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'FirstFlightSmokeValidation.psm1') -Force

function Assert-Throws {
    param(
        [Parameter(Mandatory)][scriptblock]$Action,
        [Parameter(Mandatory)][string]$Pattern
    )

    try {
        & $Action
    }
    catch {
        if ($_.Exception.Message -notmatch $Pattern) {
            throw "Expected error matching '$Pattern', observed '$($_.Exception.Message)'."
        }

        return
    }

    throw "Expected action to fail with '$Pattern'."
}

try {
    Add-Type -AssemblyName System.Drawing.Common -ErrorAction Stop
}
catch {
    Add-Type -AssemblyName System.Drawing -ErrorAction Stop
}

$scratch = Join-Path ([IO.Path]::GetTempPath()) ('onslaught-first-flight-validation-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $scratch | Out-Null

try {
    $screenshot = Join-Path $scratch 'smoke.png'
    $bitmap = [Drawing.Bitmap]::new(1280, 720)
    try {
        $graphics = [Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.Clear([Drawing.Color]::Black)
            $graphics.FillRectangle([Drawing.Brushes]::White, 36, 35, 240, 24)
            $graphics.FillRectangle([Drawing.Brushes]::Cyan, 100, 92, 240, 18)
            $graphics.FillRectangle([Drawing.Brushes]::Blue, 100, 118, 240, 18)
            $graphics.FillRectangle([Drawing.Brushes]::Green, 100, 144, 240, 18)
            $graphics.FillRectangle([Drawing.Brushes]::White, 520, 43, 230, 18)
            $graphics.FillRectangle([Drawing.Brushes]::White, 1050, 40, 170, 18)
            $graphics.FillRectangle([Drawing.Brushes]::White, 1060, 73, 155, 10)
            $graphics.FillRectangle([Drawing.Brushes]::Cyan, 690, 285, 32, 36)
            $graphics.FillRectangle([Drawing.Brushes]::White, 675, 300, 62, 22)
            $graphics.FillEllipse([Drawing.Brushes]::Yellow, 395, 515, 58, 58)
            $graphics.FillEllipse([Drawing.Brushes]::Yellow, 1120, 575, 58, 58)
            $graphics.FillRectangle([Drawing.Brushes]::Yellow, 95, 690, 1090, 6)
        }
        finally {
            $graphics.Dispose()
        }

        for ($y = 0; $y -lt $bitmap.Height; $y += 32) {
            for ($x = 0; $x -lt $bitmap.Width; $x += 32) {
                $bitmap.SetPixel($x, $y, [Drawing.Color]::FromArgb(255, ($x / 5) % 256, ($y / 3) % 256, (($x + $y) / 7) % 256))
            }
        }
        $bitmap.Save($screenshot, [Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $bitmap.Dispose()
    }

    $hash = (Get-FileHash -LiteralPath $screenshot -Algorithm SHA256).Hash.ToLowerInvariant()
    $report = [ordered]@{
        schemaVersion = 'onslaught-first-flight-smoke.v1'
        engineVersion = '4.7-stable (official)'
        exitReason = 'smoke-complete'
        tick = 120
        stateHash = '87b9d09a3afec0bebd97f06793b83baabe3ff330b2378ff149194d6d6a4f779d'
        targetsDestroyed = 1
        mode = 'Walker'
        totalSteps = 120
        toggleEdgesConsumed = 1
        resetEdgesConsumed = 1
        resetGeneration = 1
        fireHeldTicksSampled = 61
        firePulseEdgesConsumed = 0
        movementPulseEdgesConsumed = 0
        cappedFrameCount = 0
        droppedElapsedTicks = 0
        playerVisualPresent = $true
        targetVisualCount = 3
        hudReady = $true
        focusLossHandlerInputCleared = $true
        focusLossHandlerNeutralRearmed = $true
        screenshotFileName = 'smoke.png'
        screenshotWidth = 1280
        screenshotHeight = 720
        screenshotSha256 = $hash
    }
    $reportPath = Join-Path $scratch 'smoke.json'
    $logPath = Join-Path $scratch 'smoke.log'
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json))
    [IO.File]::WriteAllText($logPath, "Godot Engine v4.7`n")

    $valid = Test-FirstFlightSmokeEvidence -ReportPath $reportPath -ScreenshotPath $screenshot -LogPath $logPath
    if (-not $valid.Valid) {
        throw 'Expected valid synthetic evidence to pass.'
    }
    Write-Host 'PASS valid evidence'

    $report.stateHash = '00' * 32
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json))
    Assert-Throws -Pattern 'stateHash.*mismatch' -Action {
        Test-FirstFlightSmokeEvidence -ReportPath $reportPath -ScreenshotPath $screenshot -LogPath $logPath
    }
    Write-Host 'PASS wrong state hash fails closed'

    $report.stateHash = '87b9d09a3afec0bebd97f06793b83baabe3ff330b2378ff149194d6d6a4f779d'
    $report.screenshotFileName = 'C:\private\smoke.png'
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json))
    Assert-Throws -Pattern 'absolute or user-specific path' -Action {
        Test-FirstFlightSmokeEvidence -ReportPath $reportPath -ScreenshotPath $screenshot -LogPath $logPath
    }
    Write-Host 'PASS private path fails closed'

    $report.screenshotFileName = 'smoke.png'
    $report.focusLossHandlerInputCleared = $false
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json))
    Assert-Throws -Pattern 'focusLossHandlerInputCleared.*mismatch' -Action {
        Test-FirstFlightSmokeEvidence -ReportPath $reportPath -ScreenshotPath $screenshot -LogPath $logPath
    }
    Write-Host 'PASS uncleared focus-loss input fails closed'

    $forgedScreenshot = Join-Path $scratch 'forged.png'
    $forgedBitmap = [Drawing.Bitmap]::new(1280, 720)
    try {
        $forgedGraphics = [Drawing.Graphics]::FromImage($forgedBitmap)
        try {
            $forgedGraphics.Clear([Drawing.Color]::Black)
            $forgedGraphics.FillRectangle([Drawing.Brushes]::White, 36, 35, 240, 24)
            $forgedGraphics.FillRectangle([Drawing.Brushes]::Cyan, 100, 92, 240, 18)
            $forgedGraphics.FillRectangle([Drawing.Brushes]::Blue, 100, 118, 240, 18)
            $forgedGraphics.FillRectangle([Drawing.Brushes]::Green, 100, 144, 240, 18)
            $forgedGraphics.FillRectangle([Drawing.Brushes]::White, 520, 43, 230, 18)
            $forgedGraphics.FillRectangle([Drawing.Brushes]::White, 1050, 40, 170, 18)
        }
        finally {
            $forgedGraphics.Dispose()
        }

        for ($y = 0; $y -lt $forgedBitmap.Height; $y += 32) {
            for ($x = 0; $x -lt $forgedBitmap.Width; $x += 32) {
                $forgedBitmap.SetPixel($x, $y, [Drawing.Color]::FromArgb(255, ($x / 5) % 256, ($y / 3) % 256, (($x + $y) / 7) % 256))
            }
        }
        $forgedBitmap.Save($forgedScreenshot, [Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $forgedBitmap.Dispose()
    }

    $report.focusLossHandlerInputCleared = $true
    $report.screenshotFileName = 'forged.png'
    $report.screenshotSha256 = (Get-FileHash -LiteralPath $forgedScreenshot -Algorithm SHA256).Hash.ToLowerInvariant()
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json))
    Assert-Throws -Pattern 'world anchors' -Action {
        Test-FirstFlightSmokeEvidence -ReportPath $reportPath -ScreenshotPath $forgedScreenshot -LogPath $logPath
    }
    Write-Host 'PASS forged HUD rectangles without world anchors fail closed'

    $report.screenshotFileName = 'smoke.png'
    $report.screenshotSha256 = (Get-FileHash -LiteralPath $screenshot -Algorithm SHA256).Hash.ToLowerInvariant()
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json))
    [IO.File]::WriteAllText($logPath, "Unhandled exception in native client`n")
    Assert-Throws -Pattern 'log contains an error' -Action {
        Test-FirstFlightSmokeEvidence -ReportPath $reportPath -ScreenshotPath $screenshot -LogPath $logPath
    }
    Write-Host 'PASS unhandled native exception log fails closed'
}
finally {
    $resolvedScratch = [IO.Path]::GetFullPath($scratch)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedScratch.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -and
        [IO.Path]::GetFileName($resolvedScratch).StartsWith('onslaught-first-flight-validation-', [StringComparison]::Ordinal)) {
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    }
}

Write-Host 'First Flight smoke validation tests: PASS (6 cases)'
