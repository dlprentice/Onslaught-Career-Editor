# SPDX-License-Identifier: GPL-3.0-or-later
#
# Deterministic frontend screenshot capture for parity comparison.
#
# Retail reference captures are 640x480 because the released frontend composes at
# 4:3 (see local-lab/HYPOTHESIS-1-VERDICT-2026-07-25.md). This script launches the
# reconstruction at the SAME resolution so output is pixel-comparable against
# local-lab/startup-parity-ghidra-ro-2026-07-23/captures/ without any rescaling
# step in between - rescaling would hide exactly the layout errors we are hunting.
#
# --fixed-fps pins one _Process call to one logical frame so FrontendCaptureRig's
# frame ordinals are reproducible across runs.

[CmdletBinding()]
param(
    [switch]$Offline,
    [string]$GameRoot,
    [string]$OutputDirectory,
    # 'mainmenu' is a dense FEP_MAIN sweep for scoring the animated underlay
    # against a no-skipfmv retail burst; see FrontendCaptureRig's plan comment.
    # 'options' walks FEP_OPTIONS and its three subpages, one settled shot each,
    # so they can be compared to the retail frames in
    # local-lab/retail-captures-options-pause-2026-07-27/.
    [ValidateSet('startup', 'gameplay', 'mainmenu', 'options')]
    [string]$Plan = 'startup',
    [string]$Resolution = '640x480',
    # gameplay plan only. Point this at
    # local-lab/retail-reference-pristine/level100-gameplay/manifest.json to
    # sample the reconstruction at retail's REALISED level offsets instead of the
    # nominal 250 ms / 1 s grid. Retail's burst scheduler drifted up to ~80 ms
    # over the 1 Hz window, so nominal-grid pairing can exceed retail's own
    # +-25 ms matched-offset validity; this removes that error entirely.
    [string]$RetailOffsetManifest,
    [string]$RetailOffsetRuns = 'opening-pan-run1,hud-timeline-run1',
    # What this capture is FOR. It is stamped into capture-manifest.json as
    # capturePurpose, and automated gates that score "the newest capture" must
    # only ever pick up 'production'.
    #
    # This exists because it already went wrong. On 2026-07-26 two experimental
    # captures - one taken with the terrain shader cut down to
    # ALBEDO = macro_color, others from a camera FOV sweep - were the newest
    # gameplay captures in local-lab/godot-captures/ and were scored by
    # Level100WaterEnvelopeTests as if they described the shipping build. A
    # deliberately modified build had its output judged as product truth.
    #
    # The default is 'probe', not 'production', deliberately: the failure mode
    # was an unlabelled experiment being treated as evidence, so an unlabelled
    # capture must be the one that is IGNORED. Claiming production costs one
    # explicit flag; forgetting it costs nothing but a skipped gate.
    [ValidateSet('production', 'probe')]
    [string]$Purpose = 'probe',
    [int]$TimeoutSeconds = 0
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# The gameplay plan holds Level 100 for 42 s of engine time plus the ~8 s
# frontend traversal, so the frontend default would abort it mid-timeline.
if ($TimeoutSeconds -le 0) {
    $TimeoutSeconds = if ($Plan -eq 'gameplay') { 600 } else { 120 }
}

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $OutputDirectory = Join-Path ([IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))) "local-lab\godot-captures\$stamp-$Plan"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)

$buildArguments = @{}
if ($Offline) {
    $buildArguments.Offline = $true
}
if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
    $buildArguments.GameRoot = $GameRoot
}

$toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))

try {
    $null = [IO.Directory]::CreateDirectory($OutputDirectory)
    $logPath = Join-Path $OutputDirectory 'capture.log'

    # The rig sets the viewport to $Resolution itself and disables content scaling,
    # so the frame is composed 1:1. --resolution alone is not enough: project.godot
    # pins viewport_width/height plus window_*_override, which win over the flag.
    $engineArgs = @(
        '--log-file', $logPath,
        '--path', $projectRoot,
        '--windowed',
        '--resolution', $Resolution,
        '--fixed-fps', '60',
        '--',
        "--capture-dir=$OutputDirectory",
        "--capture-plan=$Plan",
        "--capture-size=$Resolution")

    # In-level capture runs the tutorial music and voice for the full timeline.
    # Audio is not in the viewport texture, so silencing the mixer cannot change
    # a captured pixel; it only stops a 50-second capture from taking over the
    # operator's speakers. Left alone for the frontend plan so the 13 existing
    # startup shots are produced by an unchanged invocation.
    if ($Plan -eq 'gameplay') {
        $engineArgs = @('--audio-driver', 'Dummy') + $engineArgs
    }

    if (-not [string]::IsNullOrWhiteSpace($RetailOffsetManifest)) {
        if ($Plan -ne 'gameplay') {
            throw "-RetailOffsetManifest applies only to -Plan gameplay."
        }
        $wantedRuns = @($RetailOffsetRuns -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        $retail = Get-Content -LiteralPath $RetailOffsetManifest -Raw | ConvertFrom-Json
        $offsets = @($retail.frames |
            Where-Object { $wantedRuns -contains ($_.path -split '/')[0] } |
            ForEach-Object { [int]$_.levelOffsetMs } |
            Sort-Object -Unique)
        if ($offsets.Count -eq 0) {
            throw "No frames from runs '$RetailOffsetRuns' in $RetailOffsetManifest."
        }
        $engineArgs += "--capture-offsets-ms=$($offsets -join ',')"
    }

    $process = Start-Process -FilePath $toolchain.EnginePath -ArgumentList $engineArgs -PassThru -NoNewWindow
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $process.Kill($true)
        throw "Capture timed out after $TimeoutSeconds seconds. Partial output: $OutputDirectory"
    }

    $manifestPath = Join-Path $OutputDirectory 'capture-manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Capture produced no manifest. The rig did not reach its final shot. See $logPath"
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

    # Provenance stamp. -Purpose is an operator declaration and an operator can
    # be wrong, so it is backed by one mechanical fact: whether the Godot
    # project the frames came out of was the committed source or a working-tree
    # edit. A capture taken over uncommitted renderer changes cannot describe
    # the shipping build no matter what the operator meant, so it is forced to
    # 'probe'. That is exactly the case that fooled the water gate: the
    # macro-colour terrain probe was an uncommitted one-line shader edit.
    #
    # CLEANLINESS IS TRI-STATE AND FAILS CLOSED, because the two-state version
    # lied. `git status --porcelain` outside a work tree prints nothing and exits
    # non-zero, and the old code read that empty output as "no changes" - so a
    # capture run from a `git archive` extraction of MODIFIED renderer source
    # stamped itself `godotSourceDirty: False`. That happened on 2026-07-27 (task
    # #135); see local-lab/godot-captures/t105-objmarker-*, whose manifests carry
    # a null sourceCommit and a "clean" flag from a tree that had no .git at all.
    # A flag that silently reads clean when it cannot tell is worse than no flag,
    # so "cannot tell" is now its own value and is never treated as clean.
    $repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
    $godotSource = Join-Path $repoRoot 'rebuild\OnslaughtRebuild.Godot'
    $sourceCommit = $null
    $sourceCleanliness = 'unknown'
    $dirtyEntries = @()
    try {
        $insideWorkTree = (& git -C $repoRoot rev-parse --is-inside-work-tree 2>$null)
        if ($LASTEXITCODE -eq 0 -and "$insideWorkTree".Trim() -eq 'true') {
            $head = (& git -C $repoRoot rev-parse HEAD 2>$null)
            if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($head)) {
                $sourceCommit = "$head".Trim()
            }
            $status = @(& git -C $repoRoot status --porcelain -- $godotSource 2>$null |
                Where-Object { $_ })
            if ($LASTEXITCODE -eq 0) {
                $dirtyEntries = $status
                $sourceCleanliness = if ($dirtyEntries.Count -gt 0) { 'dirty' } else { 'clean' }
            }
        }
    }
    catch {
        # git absent or unusable. That is precisely the case that must not read
        # as clean.
        $sourceCleanliness = 'unknown'
    }

    # Retained for readers that already consume it, and deliberately NOT a
    # faithful "is dirty": it is "is not provably clean". Under the tri-state
    # above, unknown reports $true here so an old consumer inherits the
    # conservative answer rather than the silent pass. godotSourceCleanliness is
    # the field that distinguishes the three cases.
    $sourceDirty = $sourceCleanliness -ne 'clean'

    $effectivePurpose = $Purpose
    $downgradeReason = $null
    if ($Purpose -eq 'production' -and $sourceCleanliness -ne 'clean') {
        $effectivePurpose = 'probe'
        $downgradeReason = if ($sourceCleanliness -eq 'dirty') {
            "rebuild/OnslaughtRebuild.Godot has $($dirtyEntries.Count) uncommitted change(s); a capture of modified renderer source is not the shipping build."
        }
        else {
            "git could not determine whether rebuild/OnslaughtRebuild.Godot is clean at $repoRoot (no work tree, or git unavailable). Cleanliness is UNKNOWN, and a build whose source cannot be identified is not the shipping build."
        }
        Write-Warning "Purpose downgraded to 'probe': $downgradeReason"
    }

    $manifest | Add-Member -NotePropertyName 'capturePurpose' -NotePropertyValue $effectivePurpose -Force
    $manifest | Add-Member -NotePropertyName 'requestedPurpose' -NotePropertyValue $Purpose -Force
    $manifest | Add-Member -NotePropertyName 'purposeDowngradeReason' -NotePropertyValue $downgradeReason -Force
    $manifest | Add-Member -NotePropertyName 'sourceCommit' -NotePropertyValue $sourceCommit -Force
    $manifest | Add-Member -NotePropertyName 'godotSourceCleanliness' -NotePropertyValue $sourceCleanliness -Force
    $manifest | Add-Member -NotePropertyName 'godotSourceDirty' -NotePropertyValue $sourceDirty -Force
    $manifest | ConvertTo-Json -Depth 64 | Set-Content -LiteralPath $manifestPath -Encoding utf8

    # A shot taken on the wrong screen is not evidence, so surface it loudly
    # rather than letting a mislabeled PNG into a parity comparison.
    $mismatched = @($manifest.shots | Where-Object { -not $_.screenMatched })
    $failedSaves = @($manifest.shots | Where-Object { $null -ne $_.saveError })

    # A frame that is not the requested size was resampled somewhere, and comparing
    # it against the retail reference would silently launder away layout error.
    $wanted = $Resolution -split 'x'
    $wrongSize = @($manifest.shots | Where-Object {
        $_.width -ne [int]$wanted[0] -or $_.height -ne [int]$wanted[1] })

    # A short manifest means the rig stopped before the end of its plan - the
    # reconstruction could not reach part of the timeline. That is a legitimate
    # and reportable outcome, but it is never a PASS, and the frames that WERE
    # captured must not be mistaken for a complete set.
    $planned = if ($manifest.PSObject.Properties.Name -contains 'plannedShots') { [int]$manifest.plannedShots } else { $manifest.shots.Count }
    $missing = [Math]::Max(0, $planned - $manifest.shots.Count)
    $boundary = if ($manifest.PSObject.Properties.Name -contains 'boundary') { $manifest.boundary } else { $null }

    # RETAIL COMPARISON. Everything above this line is a property of our own
    # capture run - right screen, right size, saved, complete. Until 2026-07-27
    # that WAS the whole gate, so it reported PASS without comparing a single
    # pixel against retail and could not detect divergence from the target: the
    # only thing a parity gate appears to guarantee (task #113).
    #
    # The generic scorer supplies the parity verdict. Options remains UNSCORED
    # there because only one retail run exists, so no cross-run noise floor can
    # support an overall parity claim. A separate phase-resistant ink-mask
    # diagnostic reports Options row-placement differences without promoting
    # that narrow, single-run measurement to a gate or page-parity result.
    # Shared verdict meanings:
    #   PASS      every gated region is at or under its regression ceiling
    #   FAIL      at least one is above it
    #   ERROR     the comparison could not be made soundly (pairing out of
    #             tolerance, size mismatch, missing frame)
    #   UNSCORED  no retail reference set present, or no plan page targets this
    #             capture plan
    #
    # UNSCORED is deliberately NOT folded into PASS. A fresh clone has no
    # retail material - it is gitignored, retail-derived - and "no evidence"
    # rendering as "no problem" is precisely the defect being closed here.
    $repoRootPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
    $scorer = Join-Path $repoRootPath 'tools\score_frontend_capture.py'
    $parityReport = Join-Path $OutputDirectory 'frontend-parity.json'
    $allowedVerdicts = @('PASS', 'FAIL', 'ERROR', 'UNSCORED')
    $parityVerdict = 'UNSCORED'
    if (Test-Path -LiteralPath $scorer) {
        Remove-Item -LiteralPath $parityReport -Force -ErrorAction SilentlyContinue
        & python $scorer --capture-dir $OutputDirectory --json-out $parityReport
        if (Test-Path -LiteralPath $parityReport) {
            try {
                $candidateVerdict =
                    [string](Get-Content -LiteralPath $parityReport -Raw |
                        ConvertFrom-Json).verdict
                if ($allowedVerdicts -contains $candidateVerdict) {
                    $parityVerdict = $candidateVerdict
                }
                else {
                    $parityVerdict = 'ERROR'
                    Write-Warning "Frontend parity scorer wrote an invalid verdict."
                }
            }
            catch {
                $parityVerdict = 'ERROR'
                Write-Warning "Frontend parity scorer wrote an unreadable report."
            }
        }
        else {
            $parityVerdict = 'ERROR'
        }
    }
    else {
        $parityVerdict = 'ERROR'
        Write-Warning "Frontend parity scorer not found at $scorer; parity was NOT measured."
    }

    $optionsInkVerdict = $null
    $optionsInkReport = $null
    if ($Plan -eq 'options') {
        $optionsScorer = Join-Path $repoRootPath 'rebuild\tools\compare_options_capture.py'
        $optionsInkReport = Join-Path $OutputDirectory 'options-ink-regression.json'
        if (Test-Path -LiteralPath $optionsScorer) {
            Remove-Item -LiteralPath $optionsInkReport -Force -ErrorAction SilentlyContinue
            & python $optionsScorer $OutputDirectory --json-out $optionsInkReport
            if (Test-Path -LiteralPath $optionsInkReport) {
                try {
                    $candidateVerdict =
                        [string](Get-Content -LiteralPath $optionsInkReport -Raw |
                            ConvertFrom-Json).verdict
                    if ($allowedVerdicts -contains $candidateVerdict) {
                        $optionsInkVerdict = $candidateVerdict
                    }
                    else {
                        $optionsInkVerdict = 'ERROR'
                        Write-Warning "Options ink scorer wrote an invalid verdict."
                    }
                }
                catch {
                    $optionsInkVerdict = 'ERROR'
                    Write-Warning "Options ink scorer wrote an unreadable report."
                }
            }
            else {
                $optionsInkVerdict = 'ERROR'
            }
        }
        else {
            $optionsInkVerdict = 'ERROR'
            Write-Warning "Options ink scorer not found at $optionsScorer."
        }
    }

    $captureHealthy = $mismatched.Count -eq 0 -and $failedSaves.Count -eq 0 -and
        $wrongSize.Count -eq 0 -and $missing -eq 0
    $status =
        if (-not $captureHealthy) { 'SUSPECT' }
        elseif ($optionsInkVerdict -eq 'ERROR') { 'SUSPECT' }
        elseif ($parityVerdict -eq 'PASS') { 'PASS' }
        elseif ($parityVerdict -eq 'FAIL') { 'FAIL' }
        elseif ($parityVerdict -eq 'UNSCORED') { 'UNSCORED' }
        else { 'SUSPECT' }

    [pscustomobject]@{
        Status = $status
        ParityVerdict = $parityVerdict
        ParityReport = if (Test-Path -LiteralPath $parityReport) { $parityReport } else { $null }
        OptionsInkVerdict = $optionsInkVerdict
        OptionsInkReport =
            if ($optionsInkReport -and (Test-Path -LiteralPath $optionsInkReport)) {
                $optionsInkReport
            }
            else {
                $null
            }
        Purpose = $effectivePurpose
        GodotSourceCleanliness = $sourceCleanliness
        GodotSourceDirty = $sourceDirty
        WrongSizeShots = $wrongSize.Count
        MissingShots = $missing
        Boundary = $boundary
        Plan = $manifest.plan
        EngineVersion = $manifest.engineVersion
        Viewport = "$($manifest.viewportWidth)x$($manifest.viewportHeight)"
        RetailReferenceSize = $manifest.retailReferenceSize
        Shots = $manifest.shots.Count
        ScreenMismatches = $mismatched.Count
        FailedSaves = $failedSaves.Count
        OutputDirectory = $OutputDirectory
    }
}
finally {
    $toolchain.Dispose()
}
