# SPDX-License-Identifier: GPL-3.0-or-later
<#
.SYNOPSIS
Record one bounded TTD opening trace for every shipped, launchable BEA level.

.DESCRIPTION
This is a thin campaign wrapper over tools/ttd_record.ps1. It discovers levels
from the copied game's own data and includes only IDs present in all three
required owners:

  data/worldheaders.dat
  data/MissionScripts/levelNNN/
  data/resources/NNN_res_PC.aya

Each level launches as `BEA.exe -skipfmv -level N`, records for three minutes by
default, finalizes the trace, closes only that copied BEA process, and then moves
to the next level. Traces are written directly to G:\bea-ttd.

The campaign is resumable without an extra state file. A healthy matching
receipt is skipped; an existing partial or mismatched directory stops the run
rather than deleting or overwriting evidence.

Run this from ONE elevated PowerShell 7 window. Child recorder processes inherit
that token, so there is no UAC prompt between levels.

.EXAMPLE
pwsh -NoProfile -ExecutionPolicy Bypass -File .\tools\Record-LevelOpeningCampaign.ps1

.EXAMPLE
pwsh -NoProfile -ExecutionPolicy Bypass -File .\tools\Record-LevelOpeningCampaign.ps1 -Levels 100,110 -DryRun

.EXAMPLE
pwsh -NoProfile -ExecutionPolicy Bypass -File .\tools\Record-LevelOpeningCampaign.ps1 -CampaignName level-openings-rerun
#>

[CmdletBinding()]
param(
    [string]$TargetRoot = "$PSScriptRoot\..\local-lab\safe-copy-bea-pristine",
    [string]$TraceRoot = 'G:\bea-ttd',
    [ValidateRange(1, 86400)][int]$SecondsPerLevel = 180,
    [ValidateRange(64, 1048576)][int]$MaxFileMB = 32768,
    [ValidateRange(10, 1048576)][int]$RequireFreeGB = 40,
    [string]$CampaignName = 'level-opening-3m-v1',
    [string[]]$Levels = @(),
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Fail([string]$Message) {
    throw $Message
}

function Quote-PowerShellLiteral([string]$Value) {
    return "'" + $Value.Replace("'", "''") + "'"
}

function Get-JsonProperty(
    [object]$Object,
    [string]$Name,
    [object]$Default = $null
) {
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $Default
    }
    return $property.Value
}

function Get-ExistingCaptureState(
    [string]$Directory,
    [int]$Level,
    [string]$ExpectedTargetRoot,
    [string]$ExpectedTargetHash,
    [int]$ExpectedSeconds
) {
    if (-not (Test-Path -LiteralPath $Directory)) {
        return [pscustomobject]@{ Status = 'missing'; Reason = $null }
    }

    $receiptPath = Join-Path $Directory 'receipt.json'
    if (-not (Test-Path -LiteralPath $receiptPath)) {
        return [pscustomobject]@{
            Status = 'invalid'
            Reason = "existing directory has no receipt: $receiptPath"
        }
    }

    try {
        $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            Status = 'invalid'
            Reason = "receipt is not valid JSON: $receiptPath"
        }
    }

    $expectedArguments = @('-skipfmv', '-level', "$Level")
    $actualArguments = @(
        Get-JsonProperty $receipt 'gameArguments' @() |
        ForEach-Object { [string]$_ }
    )
    $argumentsMatch =
        $actualArguments.Count -eq $expectedArguments.Count -and
        (($actualArguments -join "`0") -ceq ($expectedArguments -join "`0"))

    $traceFile = [string](Get-JsonProperty $receipt 'traceFile' '')
    $traceExists = $traceFile -and (Test-Path -LiteralPath $traceFile)
    $traceSizeMatches =
        $traceExists -and
        (
            [int64](Get-Item -LiteralPath $traceFile).Length -eq
            [int64](Get-JsonProperty $receipt 'traceBytes' -1)
        )
    $minimumDuration = [math]::Max(1, $ExpectedSeconds - 5)
    $receiptTargetRoot = [string](Get-JsonProperty $receipt 'targetRoot' '')
    $targetRootMatches = $false
    if (-not [string]::IsNullOrWhiteSpace($receiptTargetRoot)) {
        try {
            $targetRootMatches =
                [IO.Path]::GetFullPath($receiptTargetRoot) -ieq $ExpectedTargetRoot
        }
        catch {
            $targetRootMatches = $false
        }
    }

    $checks = [ordered]@{
        schema              = [string](Get-JsonProperty $receipt 'schemaVersion' '') -ceq 'ttd-record-receipt.v3'
        cleanGuest          = [bool](Get-JsonProperty $receipt 'guestRanCleanly' $false)
        traceGrew           = [bool](Get-JsonProperty $receipt 'traceGrew' $false)
        tracePresent        = [bool]$traceExists
        traceSize           = [bool]$traceSizeMatches
        traceHashRecorded   = -not [string]::IsNullOrWhiteSpace(
            [string](Get-JsonProperty $receipt 'traceSha256' ''))
        targetRoot          = $targetRootMatches
        targetHash          = [string](Get-JsonProperty $receipt 'targetSha256' '') -ieq $ExpectedTargetHash
        gameArguments       = [bool]$argumentsMatch
        requestedDuration   = [int](Get-JsonProperty $receipt 'requestedSeconds' -1) -eq $ExpectedSeconds
        actualDuration      = [double](Get-JsonProperty $receipt 'actualRecordSeconds' 0) -ge $minimumDuration
        notLowSpace         = -not [bool](Get-JsonProperty $receipt 'stoppedForLowSpace' $false)
        notAtFileCap        = -not [bool](Get-JsonProperty $receipt 'stoppedAtFileCap' $false)
        recorderDidNotEndEarly = -not [bool](Get-JsonProperty $receipt 'recorderEndedEarly' $false)
    }

    $failed = @($checks.GetEnumerator() | Where-Object { -not $_.Value } |
        ForEach-Object { $_.Key })
    if ($failed.Count -gt 0) {
        return [pscustomobject]@{
            Status = 'invalid'
            Reason = "receipt failed: $($failed -join ', ')"
        }
    }

    return [pscustomobject]@{
        Status = 'complete'
        Reason = "{0:N1} s, {1:N0} MiB" -f
            [double](Get-JsonProperty $receipt 'actualRecordSeconds' 0),
            ([int64](Get-JsonProperty $receipt 'traceBytes' 0) / 1MB)
    }
}

function Stop-CopiedTarget([string]$TargetExe) {
    $owned = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -ieq $TargetExe })
    foreach ($process in $owned) {
        Write-Warning "Stopping residual copied target PID $($process.Id)."
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        Wait-Process -Id $process.Id -Timeout 10 -ErrorAction SilentlyContinue
    }
}

function Invoke-RecorderChild(
    [string]$PowerShellExe,
    [string]$Recorder,
    [string]$CopiedTargetRoot,
    [string]$OutputRoot,
    [string]$TraceName,
    [int]$Level,
    [int]$DurationSeconds,
    [int]$FileCapMB,
    [int]$FreeFloorGB
) {
    # ttd_record.ps1 intentionally calls `exit` with an evidence-quality status.
    # Running it in a child PowerShell preserves that status without terminating
    # this campaign after its first level.
    $invocation = @(
        '& ' + (Quote-PowerShellLiteral $Recorder)
        '-TargetRoot ' + (Quote-PowerShellLiteral $CopiedTargetRoot)
        "-GameArguments @('-skipfmv','-level','$Level')"
        '-Name ' + (Quote-PowerShellLiteral $TraceName)
        "-Seconds $DurationSeconds"
        '-TraceRoot ' + (Quote-PowerShellLiteral $OutputRoot)
        "-RequireFreeGB $FreeFloorGB"
        "-MaxFileMB $FileCapMB"
    ) -join ' '
    $encoded = [Convert]::ToBase64String(
        [Text.Encoding]::Unicode.GetBytes($invocation))

    $process = Start-Process `
        -FilePath $PowerShellExe `
        -ArgumentList @(
            '-NoProfile',
            '-ExecutionPolicy', 'Bypass',
            '-EncodedCommand', $encoded
        ) `
        -NoNewWindow `
        -Wait `
        -PassThru
    return $process.ExitCode
}

if ($CampaignName -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,47}$') {
    Fail '-CampaignName must be 1-48 ASCII letters, digits, dots, underscores, or hyphens.'
}

$TargetRoot = [IO.Path]::GetFullPath($TargetRoot)
$TraceRoot = [IO.Path]::GetFullPath($TraceRoot)
$targetExe = Join-Path $TargetRoot 'BEA.exe'
$dataRoot = Join-Path $TargetRoot 'data'
$resourcesRoot = Join-Path $dataRoot 'resources'
$missionScriptsRoot = Join-Path $dataRoot 'MissionScripts'
$worldHeadersPath = Join-Path $dataRoot 'worldheaders.dat'
$recorder = Join-Path $PSScriptRoot 'ttd_record.ps1'
$decoder = Join-Path $PSScriptRoot 'worldheaders_decode.py'

foreach ($required in @(
    $targetExe,
    $resourcesRoot,
    $missionScriptsRoot,
    $worldHeadersPath,
    $recorder,
    $decoder
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "Required campaign input is missing: $required"
    }
}

$traceDrive = [IO.Path]::GetPathRoot($TraceRoot).TrimEnd('\', ':')
if ($traceDrive -ine 'G') {
    Fail "Traces must be written to G:. Refusing -TraceRoot '$TraceRoot'."
}

$pythonLauncher = Get-Command 'py' -ErrorAction SilentlyContinue
if (-not $pythonLauncher) {
    Fail "The Python launcher 'py' is required to decode worldheaders.dat."
}

$worldHeaderJson = @(
    & $pythonLauncher.Source -3 $decoder $worldHeadersPath --dump-json
) -join "`n"
if ($LASTEXITCODE -ne 0) {
    Fail "worldheaders_decode.py exited $LASTEXITCODE."
}
$worldHeaders = $worldHeaderJson | ConvertFrom-Json
$headerLevels = @($worldHeaders.records |
    ForEach-Object { [int]$_.world_id } |
    Sort-Object -Unique)

$missionLevels = @(
    Get-ChildItem -LiteralPath $missionScriptsRoot -Directory |
    ForEach-Object {
        if ($_.Name -match '(?i)^level(?<id>\d+)$') {
            [int]$Matches['id']
        }
    } |
    Sort-Object -Unique
)

$resourceLevels = @(
    Get-ChildItem -LiteralPath $resourcesRoot -File |
    ForEach-Object {
        if ($_.Name -match '(?i)^(?<id>\d+)_res_PC\.aya$') {
            [int]$Matches['id']
        }
    } |
    Sort-Object -Unique
)

$launchableLevels = @(
    $resourceLevels |
    Where-Object {
        $missionLevels -contains $_ -and
        $headerLevels -contains $_
    } |
    Sort-Object -Unique
)
if ($launchableLevels.Count -eq 0) {
    Fail 'No level ID has a world header, mission-script directory, and resource archive.'
}

$requestedLevels = @(
    foreach ($token in $Levels) {
        foreach ($part in ([string]$token -split ',')) {
            $text = $part.Trim()
            if (-not $text) { continue }
            $parsed = 0
            if (-not [int]::TryParse(
                $text,
                [Globalization.NumberStyles]::None,
                [Globalization.CultureInfo]::InvariantCulture,
                [ref]$parsed
            )) {
                Fail "Invalid level ID '$text'. Use integers such as -Levels 100,110."
            }
            $parsed
        }
    }
)

$selectedLevels =
    if ($requestedLevels.Count -gt 0) {
        @($requestedLevels | Sort-Object -Unique)
    }
    else {
        $launchableLevels
    }

$unsupported = @($selectedLevels | Where-Object { $launchableLevels -notcontains $_ })
if ($unsupported.Count -gt 0) {
    Fail (
        "Requested level(s) are not launchable from all three shipped owners: " +
        ($unsupported -join ', ')
    )
}

$targetHash = (Get-FileHash -LiteralPath $targetExe -Algorithm SHA256).Hash
$plans = foreach ($level in $selectedLevels) {
    $traceName = '{0}-level{1:D3}' -f $CampaignName, $level
    $directory = Join-Path $TraceRoot $traceName
    $state = Get-ExistingCaptureState `
        -Directory $directory `
        -Level $level `
        -ExpectedTargetRoot $TargetRoot `
        -ExpectedTargetHash $targetHash `
        -ExpectedSeconds $SecondsPerLevel
    [pscustomobject]@{
        Level = $level
        TraceName = $traceName
        Directory = $directory
        State = $state.Status
        Detail = $state.Reason
    }
}

$invalid = @($plans | Where-Object State -eq 'invalid')
if ($invalid.Count -gt 0) {
    $details = $invalid | ForEach-Object {
        "  level $($_.Level): $($_.Detail)`n    $($_.Directory)"
    }
    Fail (
        "Existing campaign output is not safely resumable. No evidence was deleted.`n" +
        ($details -join "`n") +
        "`nUse a fresh -CampaignName or inspect/move the listed directory."
    )
}

$pending = @($plans | Where-Object State -eq 'missing')
$complete = @($plans | Where-Object State -eq 'complete')
$estimatedGB = [math]::Round(
    ($pending.Count * $SecondsPerLevel * 35MB) / 1GB,
    1)
$recordingHours = [math]::Round(
    ($pending.Count * $SecondsPerLevel) / 3600,
    2)
$freeGB = [math]::Round(
    (Get-PSDrive -Name 'G' -ErrorAction Stop).Free / 1GB,
    1)

Write-Host ''
Write-Host 'BEA LEVEL-OPENING TTD CAMPAIGN' -ForegroundColor Cyan
Write-Host ("shipped launchable levels : {0}" -f $launchableLevels.Count)
Write-Host ("selected levels           : {0}" -f $selectedLevels.Count)
Write-Host ("already complete          : {0}" -f $complete.Count)
Write-Host ("pending                   : {0}" -f $pending.Count)
Write-Host ("recording time            : {0} h + launch/hash overhead" -f $recordingHours)
Write-Host ("high-rate size estimate   : {0} GiB (not a quota)" -f $estimatedGB)
Write-Host ("G: free now               : {0} GiB" -f $freeGB)
Write-Host ("output                    : {0}\{1}-levelNNN\" -f $TraceRoot, $CampaignName)
Write-Host ''

foreach ($plan in $complete) {
    Write-Host ("SKIP level {0}: {1}" -f $plan.Level, $plan.Detail) -ForegroundColor DarkGray
}

if ($pending.Count -eq 0) {
    Write-Host 'All selected level-opening traces are already complete.' -ForegroundColor Green
    return
}

if ($DryRun) {
    foreach ($plan in $pending) {
        Write-Host ("WOULD RECORD level {0} -> {1}" -f $plan.Level, $plan.Directory)
    }
    return
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$elevated = (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $elevated) {
    Fail 'Run this campaign from an elevated PowerShell 7 window. It will not raise unattended UAC prompts.'
}

$pwsh = Get-Command 'pwsh' -ErrorAction SilentlyContinue
if (-not $pwsh) {
    Fail "PowerShell 7 ('pwsh') is required for isolated recorder children."
}

$running = @(Get-Process -Name 'BEA' -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
    Fail (
        "BEA.exe is already running (PID(s) " +
        (($running | ForEach-Object Id) -join ', ') +
        '). Close it before starting the unattended campaign.'
    )
}

$completedThisRun = 0
foreach ($plan in $pending) {
    Write-Host ''
    Write-Host (
        "=== LEVEL {0} ({1}/{2} pending) ===" -f
        $plan.Level,
        ($completedThisRun + 1),
        $pending.Count
    ) -ForegroundColor Cyan
    Write-Host ("trace: {0}" -f $plan.Directory)

    $exitCode = $null
    try {
        $exitCode = Invoke-RecorderChild `
            -PowerShellExe $pwsh.Source `
            -Recorder $recorder `
            -CopiedTargetRoot $TargetRoot `
            -OutputRoot $TraceRoot `
            -TraceName $plan.TraceName `
            -Level $plan.Level `
            -DurationSeconds $SecondsPerLevel `
            -FileCapMB $MaxFileMB `
            -FreeFloorGB $RequireFreeGB
    }
    finally {
        Stop-CopiedTarget -TargetExe $targetExe
    }

    if ($exitCode -ne 0) {
        Fail (
            "Recorder failed for level $($plan.Level) with exit code $exitCode. " +
            "Completed traces remain resumable; rerun the same command after inspecting " +
            "$($plan.Directory)."
        )
    }

    $finished = Get-ExistingCaptureState `
        -Directory $plan.Directory `
        -Level $plan.Level `
        -ExpectedTargetRoot $TargetRoot `
        -ExpectedTargetHash $targetHash `
        -ExpectedSeconds $SecondsPerLevel
    if ($finished.Status -ne 'complete') {
        Fail (
            "Level $($plan.Level) returned success but its receipt is not complete: " +
            $finished.Reason
        )
    }

    $completedThisRun++
    Write-Host ("COMPLETE level {0}: {1}" -f $plan.Level, $finished.Reason) -ForegroundColor Green
}

Write-Host ''
Write-Host (
    "CAMPAIGN COMPLETE: {0}/{1} selected level openings have healthy matching receipts." -f
    $selectedLevels.Count,
    $selectedLevels.Count
) -ForegroundColor Green
