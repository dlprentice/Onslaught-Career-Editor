# SPDX-License-Identifier: GPL-3.0-or-later
#
# Tests for Capture-Session.ps1. Follows the repository's hand-rolled harness
# (see GodotToolchain.Tests.ps1): no Pester dependency, Invoke-TestCase counts,
# any throw fails the run.
#
# Dot-sourcing the script under test would EXECUTE it (it resolves windows and
# starts ffmpeg at top level), so the resolver logic is tested by extracting
# its function definitions into a generated harness file in the scratch dir,
# overriding Get-CandidateWindows with synthetic windows, and invoking
# Resolve-CaptureWindow directly. Refusal paths and the happy path run the
# real script as a CHILD pwsh so its exit() cannot kill this runner.
#
# The end-to-end recording case deliberately drives a plain WinForms window,
# NOT any game: the serialized-game rule forbids a second BEA target while
# another lane holds the slot, and no game is needed to prove gdigrab
# recording + manifest writing work.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$script:Passed = 0
$script:CaptureSessionPath = Join-Path $PSScriptRoot 'Capture-Session.ps1'

function Assert-Equal {
    param(
        [Parameter(Mandatory)]$Expected,
        [Parameter(Mandatory)]$Actual,
        [Parameter(Mandatory)][string]$Message
    )
    if ($Expected -ne $Actual) {
        throw "$Message Expected '$Expected', observed '$Actual'."
    }
}

function Assert-True {
    param(
        [Parameter(Mandatory)][bool]$Condition,
        [Parameter(Mandatory)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

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

function Invoke-TestCase {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][scriptblock]$Action
    )
    & $Action
    $script:Passed++
    Write-Host "PASS $Name"
}

# Runs Capture-Session.ps1 in a CHILD pwsh; returns @{ ExitCode; StdOut; StdErr }.
function Invoke-CaptureSessionChild {
    param([Parameter(Mandatory)][string[]]$ScriptArguments)
    $tag = [guid]::NewGuid().ToString('N')
    $out = Join-Path $env:TEMP ("cap-session-out-{0}.txt" -f $tag)
    $err = Join-Path $env:TEMP ("cap-session-err-{0}.txt" -f $tag)
    try {
        $allArgs = @('-NoLogo', '-NoProfile', '-File', $script:CaptureSessionPath) + $ScriptArguments
        $proc = Start-Process -FilePath 'pwsh' -ArgumentList $allArgs `
            -RedirectStandardOutput $out -RedirectStandardError $err -NoNewWindow -PassThru -Wait
        $stdOut = Get-Content -LiteralPath $out -Raw -ErrorAction SilentlyContinue
        $stdErr = Get-Content -LiteralPath $err -Raw -ErrorAction SilentlyContinue
        return @{
            ExitCode = $proc.ExitCode
            StdOut   = (($null -eq $stdOut) ? '' : $stdOut)
            StdErr   = (($null -eq $stdErr) ? '' : $stdErr)
        }
    }
    finally {
        Remove-Item -LiteralPath $out, $err -ErrorAction SilentlyContinue
    }
}

# Builds a standalone harness script containing the REAL resolver functions
# from Capture-Session.ps1 plus a synthetic Get-CandidateWindows override, so
# Resolve-CaptureWindow can be exercised without touching real desktop state.
function New-ResolverHarness {
    param(
        [Parameter(Mandatory)][object[]]$SyntheticWindows,
        [Parameter(Mandatory)][string]$HarnessPath
    )

    $scriptText = Get-Content -LiteralPath $script:CaptureSessionPath -Raw
    $start = $scriptText.IndexOf('function Get-CandidateWindows')
    $end = $scriptText.IndexOf('# --- resolve the target')
    if ($start -lt 0 -or $end -le $start) {
        throw 'Could not locate the resolver region in Capture-Session.ps1.'
    }
    $region = $scriptText.Substring($start, $end - $start)

    $candidateLiteral = (@($SyntheticWindows | ForEach-Object {
                '[pscustomobject]@{{ Hwnd = [IntPtr]{0}; Title = ''{1}''; Left = 0; Top = 0; Width = 100; Height = 80 }}' -f $_.Hwnd.ToInt64(), ($_.Title -replace "'", "''")
            }) -join ",`n        ")

    $harness = @"
$region

# Test double: this later definition of Get-CandidateWindows wins over the
# real enumerator copied above, so resolution sees only synthetic windows.
# Plain return, NO comma guard: the resolver wraps the call in @( ) itself,
# and a comma-wrapped array here is what member-enumeration turned into a
# fake "match" before the real script was fixed.
function Get-CandidateWindows {
    return @(
        $candidateLiteral
    )
}
"@
    Set-Content -LiteralPath $HarnessPath -Value $harness -Encoding UTF8
}

$scratchRoot = Join-Path ([IO.Path]::GetTempPath()) ("onslaught-capture-session-tests-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $scratchRoot | Out-Null

try {
    Invoke-TestCase 'script parses cleanly and declares its surface' {
        $text = Get-Content -LiteralPath $script:CaptureSessionPath -Raw
        $tokens = $null; $errors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseInput($text, [ref]$tokens, [ref]$errors)
        Assert-Equal -Expected 0 -Actual @($errors).Count -Message 'Capture-Session.ps1 must parse without errors.'
        foreach ($name in @('Get-CandidateWindows', 'Resolve-CaptureWindow')) {
            Assert-True -Condition ($text -match "function\s+$name\b") -Message "Expected function $name."
        }
    }

    Invoke-TestCase 'resolver prefers an exact title over substring matches' {
        $harnessPath = Join-Path $scratchRoot 'resolver-exact.ps1'
        New-ResolverHarness -HarnessPath $harnessPath -SyntheticWindows @(
            [pscustomobject]@{ Hwnd = [IntPtr]11; Title = 'Some BEA thing' },
            [pscustomobject]@{ Hwnd = [IntPtr]22; Title = 'BEA' }
        )
        $result = pwsh -NoLogo -NoProfile -Command ". '$harnessPath'; (Resolve-CaptureWindow -TitleSubstring 'BEA').Hwnd"
        Assert-Equal -Expected '22' -Actual "$result".Trim() -Message 'Exact title must win over substring match.'
    }

    Invoke-TestCase 'resolver accepts a unique case-insensitive substring' {
        $harnessPath = Join-Path $scratchRoot 'resolver-substr.ps1'
        New-ResolverHarness -HarnessPath $harnessPath -SyntheticWindows @(
            [pscustomobject]@{ Hwnd = [IntPtr]31; Title = 'Onslaught Rebuild - Battle Engine Aquila' },
            [pscustomobject]@{ Hwnd = [IntPtr]32; Title = 'Totally Unrelated' }
        )
        $result = pwsh -NoLogo -NoProfile -Command ". '$harnessPath'; (Resolve-CaptureWindow -TitleSubstring 'onslaught rebuild').Hwnd"
        Assert-Equal -Expected '31' -Actual "$result".Trim() -Message 'Unique substring must resolve.'
    }

    Invoke-TestCase 'resolver refuses ambiguity naming the candidates' {
        $harnessPath = Join-Path $scratchRoot 'resolver-ambig.ps1'
        New-ResolverHarness -HarnessPath $harnessPath -SyntheticWindows @(
            [pscustomobject]@{ Hwnd = [IntPtr]41; Title = 'Menu Probe A' },
            [pscustomobject]@{ Hwnd = [IntPtr]42; Title = 'Menu Probe B' }
        )
        # Backtick-escape `$_` so the CHILD sees the variable instead of this
        # script's StrictMode-guarded expansion.
        $childCommand = ". '$harnessPath'; try { Resolve-CaptureWindow -TitleSubstring 'Menu Probe' } catch { Write-Host `$_.Exception.Message; exit 7 }"
        $out = pwsh -NoLogo -NoProfile -Command $childCommand 2>&1
        $joined = ($out | Out-String)
        Assert-True -Condition ($LASTEXITCODE -eq 7) -Message ('Ambiguity must throw in the child pwsh. Observed: ' + $joined)
        Assert-True -Condition ($joined -match 'Ambiguous -WindowTitle') -Message ('Ambiguity must be refused. Observed: ' + $joined)
        Assert-True -Condition ($joined -match 'Menu Probe B') -Message 'Refusal must name candidate titles.'
    }

    Invoke-TestCase 'window-not-found exits 2 and lists visible titles' {
        $missing = Invoke-CaptureSessionChild -ScriptArguments @(
            '-WindowTitle', 'DEFINITELY-NOT-A-REAL-WINDOW-8f3c',
            '-DurationSeconds', '2',
            '-OutputPath', (Join-Path $scratchRoot 'never.mp4'))
        Assert-Equal -Expected 2 -Actual $missing.ExitCode -Message 'Missing window must exit 2.'
        Assert-True -Condition ($missing.StdErr -match 'No visible window title contains') -Message ('Stderr should name the substring; observed: ' + $missing.StdErr)
    }

    Invoke-TestCase 'existing clip without -Force exits 3' {
        $existingClip = Join-Path $scratchRoot 'existing.mp4'
        Set-Content -LiteralPath $existingClip -Value 'stub'
        $exists = Invoke-CaptureSessionChild -ScriptArguments @(
            '-WindowTitle', 'DEFINITELY-NOT-A-REAL-WINDOW-8f3c',
            '-DurationSeconds', '2',
            '-OutputPath', $existingClip)
        Assert-Equal -Expected 3 -Actual $exists.ExitCode -Message 'Existing clip must be refused with exit 3.'
        Assert-True -Condition ($exists.StdErr -match 'Refusing to overwrite') -Message 'Refusal should say why.'
    }

    Invoke-TestCase 'non-mp4 output exits 3 before window lookup' {
        $badExt = Invoke-CaptureSessionChild -ScriptArguments @(
            '-WindowTitle', 'anything-at-all',
            '-DurationSeconds', '2',
            '-OutputPath', (Join-Path $scratchRoot 'clip.avi'))
        Assert-Equal -Expected 3 -Actual $badExt.ExitCode -Message 'Non-.mp4 output must exit 3.'
    }

    Invoke-TestCase 'missing ffmpeg exits 3 before window lookup' {
        $noFf = Invoke-CaptureSessionChild -ScriptArguments @(
            '-FfmpegPath', 'definitely-not-ffmpeg-9f21',
            '-WindowTitle', 'anything-at-all',
            '-DurationSeconds', '2',
            '-OutputPath', (Join-Path $scratchRoot 'x.mp4'))
        Assert-Equal -Expected 3 -Actual $noFf.ExitCode -Message 'Missing ffmpeg must exit 3.'
    }

    Invoke-TestCase 'duration outside 1..3600 is rejected nonzero' {
        # Parameter binding errors under pwsh -File are environment-owned; the
        # contract asserted here is "refused", not a specific code.
        $zero = Invoke-CaptureSessionChild -ScriptArguments @(
            '-WindowTitle', 'anything-at-all',
            '-DurationSeconds', '0',
            '-OutputPath', (Join-Path $scratchRoot 'y.mp4'))
        Assert-True -Condition ($zero.ExitCode -ne 0) -Message 'DurationSeconds=0 must fail.'
        Assert-True -Condition ($zero.StdErr -match 'DurationSeconds') -Message 'Failure should name the offending parameter.'
    }

    Invoke-TestCase 'end-to-end: records a real NON-game window to mp4 + manifest' {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $form = New-Object System.Windows.Forms.Form
        $form.Text = 'CAPTURE-SESSION-TEST-WINDOW'
        $form.StartPosition = 'Manual'
        $form.Location = New-Object System.Drawing.Point -ArgumentList 40, 40
        $form.Size = New-Object System.Drawing.Size -ArgumentList 420, 300
        $label = New-Object System.Windows.Forms.Label
        $label.Text = 'capture-session end-to-end test subject'
        $label.Dock = 'Fill'
        $label.TextAlign = 'MiddleCenter'
        $form.Controls.Add($label)
        $form.Show()
        $form.Refresh()
        try {
            $clip = Join-Path $scratchRoot 'e2e.mp4'
            $result = Invoke-CaptureSessionChild -ScriptArguments @(
                '-WindowTitle', 'CAPTURE-SESSION-TEST-WINDOW',
                '-DurationSeconds', '2',
                '-OutputPath', $clip)
            Assert-Equal -Expected 0 -Actual $result.ExitCode -Message ('End-to-end recording failed: ' + $result.StdErr + ' ||STDOUT|| ' + $result.StdOut)

            Assert-True -Condition (Test-Path -LiteralPath $clip) -Message 'Clip was not produced.'
            Assert-True -Condition ((Get-Item -LiteralPath $clip).Length -gt 4KB) -Message 'Clip suspiciously small.'
            $manifestPath = "$clip.manifest.json"
            Assert-True -Condition (Test-Path -LiteralPath $manifestPath) -Message 'Manifest sidecar missing.'
            $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
            Assert-Equal -Expected 'CAPTURE-SESSION-TEST-WINDOW' -Actual $manifest.windowTitle -Message 'Manifest windowTitle mismatch.'
            Assert-Equal -Expected 15 -Actual ([int]$manifest.frameRate) -Message 'Manifest frameRate mismatch.'
            Assert-True -Condition ($manifest.clipSha256 -match '^[0-9a-f]{64}$') -Message 'Manifest sha256 not lowercase hex SHA-256.'
            Assert-Equal -Expected 2 -Actual ([int]$manifest.durationSeconds) -Message 'Manifest duration mismatch.'
            $hash = (Get-FileHash -LiteralPath $clip -Algorithm SHA256).Hash.ToLowerInvariant()
            Assert-Equal -Expected $hash -Actual $manifest.clipSha256 -Message 'Manifest hash does not match clip bytes.'
        }
        finally {
            $form.Close(); $form.Dispose()
        }
    }
}
finally {
    $resolvedScratch = [IO.Path]::GetFullPath($scratchRoot)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedScratch.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -and
        [IO.Path]::GetFileName($resolvedScratch).StartsWith('onslaught-capture-session-tests-', [StringComparison]::Ordinal)) {
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    }
}

Write-Host "Capture-Session tests: PASS ($script:Passed cases)"
