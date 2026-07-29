[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$')]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [string]$TargetExe,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedTargetSha256,

    [Parameter(Mandatory = $true)]
    [string]$ApiTraceExe,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedApiTraceSha256,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedD3DRetraceSha256,

    [ValidateRange(1, 60)]
    [int]$CaptureSeconds = 5,

    [string]$OutputRoot = 'G:\bea-parity-lab\apitrace'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Facts {
    param([Parameter(Mandatory = $true)][string]$Path)

    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = $item.FullName
        bytes = $item.Length
        sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
        lastWriteUtc = $item.LastWriteTimeUtc.ToString('o')
    }
}

function Assert-Unchanged {
    param(
        [Parameter(Mandatory = $true)]$Before,
        [Parameter(Mandatory = $true)]$After,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($Before.bytes -ne $After.bytes -or
        $Before.sha256 -cne $After.sha256 -or
        $Before.lastWriteUtc -cne $After.lastWriteUtc) {
        throw "$Label changed during the apitrace experiment."
    }
}

function Invoke-Redirected {
    param(
        [Parameter(Mandatory = $true)][string]$FileName,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [ValidateRange(1, 600)][int]$TimeoutSeconds = 120
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FileName
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    foreach ($argument in $Arguments) {
        $startInfo.ArgumentList.Add($argument)
    }
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw "Failed to start $FileName"
    }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $timedOut = -not $process.WaitForExit($TimeoutSeconds * 1000)
    if ($timedOut) {
        $process.Kill($true)
        $process.WaitForExit()
    }
    $result = [ordered]@{
        exitCode = $process.ExitCode
        timedOut = $timedOut
        stdout = $stdoutTask.GetAwaiter().GetResult()
        stderr = $stderrTask.GetAwaiter().GetResult()
    }
    $process.Dispose()
    return $result
}

function Test-ProcessDescendsFrom {
    param(
        [Parameter(Mandatory = $true)][int]$ProcessId,
        [Parameter(Mandatory = $true)][int]$AncestorProcessId
    )

    $parents = @{}
    foreach ($row in Get-CimInstance Win32_Process -ErrorAction Stop) {
        $parents[[int]$row.ProcessId] = [int]$row.ParentProcessId
    }
    $current = $ProcessId
    $visited = [Collections.Generic.HashSet[int]]::new()
    while ($current -gt 0 -and $visited.Add($current)) {
        if ($current -eq $AncestorProcessId) {
            return $true
        }
        if (-not $parents.ContainsKey($current)) {
            return $false
        }
        $current = [int]$parents[$current]
    }
    return $false
}

$targetPath = (Resolve-Path -LiteralPath $TargetExe).Path
$apiTracePath = (Resolve-Path -LiteralPath $ApiTraceExe).Path
$retracePath = Join-Path (Split-Path -Parent $apiTracePath) 'd3dretrace.exe'
if (-not (Test-Path -LiteralPath $retracePath -PathType Leaf)) {
    throw "No sibling d3dretrace.exe found beside apitrace: $retracePath"
}
$retracePath = (Resolve-Path -LiteralPath $retracePath).Path
if ([IO.Path]::GetFileName($targetPath) -ine 'BEA.exe') {
    throw "Expected a copied BEA.exe target: $targetPath"
}
$targetLower = $targetPath.ToLowerInvariant()
if ($targetLower.Contains('\steamapps\') -or
    $targetLower.StartsWith(
        [Environment]::GetFolderPath('ProgramFiles').ToLowerInvariant()
    ) -or
    $targetLower.StartsWith(
        [Environment]::GetFolderPath('ProgramFilesX86').ToLowerInvariant()
    )) {
    throw 'Refusing to trace an installed or Program Files target.'
}
$targetDirectory = Split-Path -Parent $targetPath
$localD3D9 = Join-Path $targetDirectory 'd3d9.dll'
if (Test-Path -LiteralPath $localD3D9) {
    throw "A local d3d9.dll is already armed beside the copied target: $localD3D9"
}
if (Get-Process -Name BEA -ErrorAction SilentlyContinue) {
    throw 'Refusing to start while another BEA process exists.'
}

$targetBefore = Get-Facts -Path $targetPath
$apiTraceFacts = Get-Facts -Path $apiTracePath
$d3dRetraceFacts = Get-Facts -Path $retracePath
if ($targetBefore.sha256 -cne $ExpectedTargetSha256.ToUpperInvariant()) {
    throw "Target SHA-256 mismatch: $($targetBefore.sha256)"
}
if ($apiTraceFacts.sha256 -cne $ExpectedApiTraceSha256.ToUpperInvariant()) {
    throw "apitrace SHA-256 mismatch: $($apiTraceFacts.sha256)"
}
if (
    $d3dRetraceFacts.sha256 -cne
        $ExpectedD3DRetraceSha256.ToUpperInvariant()
) {
    throw "d3dretrace SHA-256 mismatch: $($d3dRetraceFacts.sha256)"
}

$outputBase = [IO.Path]::GetFullPath($OutputRoot)
[IO.Directory]::CreateDirectory($outputBase) | Out-Null
$output = Join-Path $outputBase $Name
if (Test-Path -LiteralPath $output) {
    throw "Refusing to overwrite an existing apitrace run: $output"
}
[IO.Directory]::CreateDirectory($output) | Out-Null
$tracePath = Join-Path $output "$Name.trace"

$apiProcess = $null
$bea = $null
$startedAt = $null
$scriptExitCode = 0
$receipt = $null
$primaryProblem = $null
$beaId = $null
$forcedTermination = $false
$primaryCaptureTreeKillAttemptCount = 0
$primaryCaptureTreeKillSuccessCount = 0
$samePathSurvivorCount = 0
$cleanupSurvivorCount = 0
$cleanupProblems = [System.Collections.Generic.List[string]]::new()
try {
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $apiTracePath
$startInfo.WorkingDirectory = $targetDirectory
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
foreach ($argument in @(
        'trace',
        '--api=d3d9',
        "--output=$tracePath",
        $targetPath
    )) {
    $startInfo.ArgumentList.Add($argument)
}
$apiProcess = [System.Diagnostics.Process]::new()
$apiProcess.StartInfo = $startInfo
$startedAt = (Get-Date).ToUniversalTime()
if (-not $apiProcess.Start()) {
    throw 'Failed to start apitrace.'
}
$stdoutTask = $apiProcess.StandardOutput.ReadToEndAsync()
$stderrTask = $apiProcess.StandardError.ReadToEndAsync()

$bea = $null
$launchDeadline = [DateTime]::UtcNow.AddSeconds(20)
while ([DateTime]::UtcNow -lt $launchDeadline -and $null -eq $bea) {
    if ($apiProcess.HasExited) {
        throw "apitrace exited before copied-target BEA appeared (exit $($apiProcess.ExitCode))."
    }
    $pathCandidates = @(
        Get-Process -Name BEA -ErrorAction SilentlyContinue |
            Where-Object {
                try {
                    $_.Path -ieq $targetPath -and
                    $_.StartTime.ToUniversalTime() -ge
                        $startedAt.AddSeconds(-1)
                } catch {
                    $false
                }
            }
    )
    $ownedCandidates = @(
        $pathCandidates | Where-Object {
            Test-ProcessDescendsFrom `
                -ProcessId $_.Id `
                -AncestorProcessId $apiProcess.Id
        }
    )
    if ($ownedCandidates.Count -eq 1) {
        $bea = $ownedCandidates[0]
        break
    }
    if ($ownedCandidates.Count -gt 1) {
        throw 'More than one copied-target BEA descendant appeared.'
    }
    if ($null -eq $bea) {
        Start-Sleep -Milliseconds 100
    }
}
if ($null -eq $bea) {
    if (-not $apiProcess.HasExited) {
        $forcedTermination = $true
        $primaryCaptureTreeKillAttemptCount++
        $apiProcess.Kill($true)
        $apiProcess.WaitForExit()
        $primaryCaptureTreeKillSuccessCount++
    }
    throw 'apitrace did not launch the exact copied BEA target within 20 seconds.'
}
$beaId = $bea.Id

$beaObservedAt = (Get-Date).ToUniversalTime()
$requestedCaptureEnd = $beaObservedAt.AddSeconds($CaptureSeconds)
Start-Sleep -Seconds $CaptureSeconds
$guestExitTimeUtc = $null
$guestExitedBeforeWindow = $false
if ($bea.HasExited) {
    $guestExitTimeUtc = $bea.ExitTime.ToUniversalTime()
    $guestExitedBeforeWindow = $guestExitTimeUtc -lt $requestedCaptureEnd
}
$closeRequested = $false
if (-not $bea.HasExited) {
    $closeRequested = $bea.CloseMainWindow()
    if (-not $bea.WaitForExit(15000)) {
        $forcedTermination = $true
        $primaryCaptureTreeKillAttemptCount++
        $bea.Kill($true)
        $bea.WaitForExit()
        $primaryCaptureTreeKillSuccessCount++
    }
}
$beaExitCode = $bea.ExitCode
$bea.Dispose()
$bea = $null

if (-not $apiProcess.WaitForExit(30000)) {
    $forcedTermination = $true
    $primaryCaptureTreeKillAttemptCount++
    $apiProcess.Kill($true)
    $apiProcess.WaitForExit()
    $primaryCaptureTreeKillSuccessCount++
}
$apiExitCode = $apiProcess.ExitCode
$apiStdout = $stdoutTask.GetAwaiter().GetResult()
$apiStderr = $stderrTask.GetAwaiter().GetResult()
$apiProcess.Dispose()
$apiProcess = $null
$finishedAt = (Get-Date).ToUniversalTime()

[IO.File]::WriteAllText(
    (Join-Path $output 'apitrace-stdout.txt'),
    $apiStdout,
    [Text.UTF8Encoding]::new($false)
)
[IO.File]::WriteAllText(
    (Join-Path $output 'apitrace-stderr.txt'),
    $apiStderr,
    [Text.UTF8Encoding]::new($false)
)

$targetAfter = Get-Facts -Path $targetPath
Assert-Unchanged -Before $targetBefore -After $targetAfter -Label 'Target executable'
if (Test-Path -LiteralPath $localD3D9) {
    throw 'apitrace left an unexpected d3d9.dll beside the copied target.'
}
if (-not (Test-Path -LiteralPath $tracePath -PathType Leaf)) {
    throw 'apitrace produced no trace file.'
}
$traceFacts = Get-Facts -Path $tracePath
if ($traceFacts.bytes -eq 0) {
    throw 'apitrace produced an empty trace file.'
}

$dump = Invoke-Redirected `
    -FileName $apiTracePath `
    -Arguments @('dump', '--calls=frame', '--color=never', $tracePath) `
    -WorkingDirectory $output
[IO.File]::WriteAllText(
    (Join-Path $output 'frame-calls.txt'),
    $dump.stdout,
    [Text.UTF8Encoding]::new($false)
)
[IO.File]::WriteAllText(
    (Join-Path $output 'dump-stderr.txt'),
    $dump.stderr,
    [Text.UTF8Encoding]::new($false)
)
$presentCount = ([regex]::Matches(
        $dump.stdout,
        '(?m)IDirect3DDevice9::Present\('
    )).Count

$health = if (
    $beaExitCode -eq 0 -and
    -not $guestExitedBeforeWindow -and
    $apiExitCode -eq 0 -and
    $dump.exitCode -eq 0 -and
    -not $dump.timedOut -and
    -not $forcedTermination -and
    $presentCount -gt 0
) {
    'COMPLETE'
} elseif (
    $traceFacts.bytes -gt 0 -and
    $dump.exitCode -eq 0 -and
    -not $dump.timedOut
) {
    'PARTIAL'
} else {
    'ERROR'
}

$recovery = $null
$recoveredTraceFacts = $null
$recoveredTracePath = $null
if ($health -eq 'PARTIAL' -and $presentCount -gt 0) {
    $presentMatches = [regex]::Matches(
        $dump.stdout,
        '(?m)^(?<call>[0-9]+)\s+IDirect3DDevice9::Present\('
    )
    $lastCompletePresentCall = [UInt64]::Parse(
        $presentMatches[$presentMatches.Count - 1].Groups['call'].Value,
        [Globalization.CultureInfo]::InvariantCulture
    )
    $recoveredTracePath = Join-Path $output "$Name.complete-frames.trace"
    if (Test-Path -LiteralPath $recoveredTracePath) {
        throw "Refusing to replace recovered trace: $recoveredTracePath"
    }

    $trim = Invoke-Redirected `
        -FileName $apiTracePath `
        -Arguments @(
            'trim',
            "--calls=0-$lastCompletePresentCall",
            "--output=$recoveredTracePath",
            $tracePath
        ) `
        -WorkingDirectory $output
    [IO.File]::WriteAllText(
        (Join-Path $output 'trim-stdout.txt'),
        $trim.stdout,
        [Text.UTF8Encoding]::new($false)
    )
    [IO.File]::WriteAllText(
        (Join-Path $output 'trim-stderr.txt'),
        $trim.stderr,
        [Text.UTF8Encoding]::new($false)
    )

    $recoveredDump = $null
    $retraceFacts = $null
    $retrace = $null
    $rawRetrace = $null
    $recoveredPresentCount = 0
    $snapshotMd5Count = 0
    $snapshotUniqueMd5Count = 0
    $rawSnapshotMd5Count = 0
    $rawSnapshotUniqueMd5Count = 0
    $rawHasUnexpectedEof = $false
    $frameMd5Exact = $false
    $frameMd5ComparedRows = 0
    $frameMd5FirstMismatch = $null
    $recoveredHasUnexpectedEof = $true
    if ($trim.exitCode -eq 0 -and
        (Test-Path -LiteralPath $recoveredTracePath -PathType Leaf) -and
        (Get-Item -LiteralPath $recoveredTracePath).Length -gt 0) {
        $recoveredTraceFacts = Get-Facts -Path $recoveredTracePath
        $recoveredDump = Invoke-Redirected `
            -FileName $apiTracePath `
            -Arguments @(
                'dump',
                '--calls=frame',
                '--color=never',
                $recoveredTracePath
            ) `
            -WorkingDirectory $output
        [IO.File]::WriteAllText(
            (Join-Path $output 'complete-frames-calls.txt'),
            $recoveredDump.stdout,
            [Text.UTF8Encoding]::new($false)
        )
        [IO.File]::WriteAllText(
            (Join-Path $output 'complete-frames-dump-stderr.txt'),
            $recoveredDump.stderr,
            [Text.UTF8Encoding]::new($false)
        )
        $recoveredPresentCount = ([regex]::Matches(
                $recoveredDump.stdout,
                '(?m)IDirect3DDevice9::Present\('
            )).Count

        if (Test-Path -LiteralPath $retracePath -PathType Leaf) {
            $retraceFacts = $d3dRetraceFacts
            $rawRetrace = Invoke-Redirected `
                -FileName $retracePath `
                -Arguments @(
                    '--snapshot-format=MD5',
                    '-s',
                    '-',
                    $tracePath
                ) `
                -WorkingDirectory $output
            [IO.File]::WriteAllText(
                (Join-Path $output 'raw-complete-prefix-md5.txt'),
                $rawRetrace.stdout,
                [Text.UTF8Encoding]::new($false)
            )
            [IO.File]::WriteAllText(
                (Join-Path $output 'raw-complete-prefix-retrace-stderr.txt'),
                $rawRetrace.stderr,
                [Text.UTF8Encoding]::new($false)
            )
            $retrace = Invoke-Redirected `
                -FileName $retracePath `
                -Arguments @(
                    '--snapshot-format=MD5',
                    '-s',
                    '-',
                    $recoveredTracePath
                ) `
                -WorkingDirectory $output
            [IO.File]::WriteAllText(
                (Join-Path $output 'complete-frames-md5.txt'),
                $retrace.stdout,
                [Text.UTF8Encoding]::new($false)
            )
            [IO.File]::WriteAllText(
                (Join-Path $output 'complete-frames-retrace-stderr.txt'),
                $retrace.stderr,
                [Text.UTF8Encoding]::new($false)
            )
            $snapshotRows = @(
                [regex]::Matches(
                    $retrace.stdout,
                    '(?im)^[0-9a-f]{32}\r?$'
                ) |
                    ForEach-Object {
                        $_.Value.Trim().ToLowerInvariant()
                    }
            )
            $rawSnapshotRows = @(
                [regex]::Matches(
                    $rawRetrace.stdout,
                    '(?im)^[0-9a-f]{32}\r?$'
                ) |
                    ForEach-Object {
                        $_.Value.Trim().ToLowerInvariant()
                    }
            )
            $snapshotMd5Count = $snapshotRows.Count
            $snapshotUniqueMd5Count = @(
                $snapshotRows | Sort-Object -Unique
            ).Count
            $rawSnapshotMd5Count = $rawSnapshotRows.Count
            $rawSnapshotUniqueMd5Count = @(
                $rawSnapshotRows | Sort-Object -Unique
            ).Count
            $frameMd5ComparedRows = [Math]::Min(
                $snapshotMd5Count,
                $rawSnapshotMd5Count
            )
            for ($index = 0; $index -lt $frameMd5ComparedRows; $index++) {
                if ($snapshotRows[$index] -cne $rawSnapshotRows[$index]) {
                    $frameMd5FirstMismatch = $index
                    break
                }
            }
            $frameMd5Exact = (
                $null -eq $frameMd5FirstMismatch -and
                $snapshotMd5Count -eq $rawSnapshotMd5Count
            )
            $rawHasUnexpectedEof = (
                $rawRetrace.stderr.Contains('unexpected end of file')
            )
            $recoveredHasUnexpectedEof = (
                $recoveredDump.stderr.Contains('unexpected end of file') -or
                $retrace.stderr.Contains('unexpected end of file')
            )
        }
    }

    $recoveryHealth = if (
        $null -ne $recoveredTraceFacts -and
        $null -ne $recoveredDump -and
        $null -ne $retrace -and
        $null -ne $rawRetrace -and
        -not $trim.timedOut -and
        $recoveredDump.exitCode -eq 0 -and
        -not $recoveredDump.timedOut -and
        $retrace.exitCode -eq 0 -and
        -not $retrace.timedOut -and
        -not $rawRetrace.timedOut -and
        $recoveredPresentCount -eq $presentCount -and
        $snapshotMd5Count -eq $recoveredPresentCount -and
        $rawSnapshotMd5Count -eq $presentCount -and
        $frameMd5Exact -and
        -not $recoveredHasUnexpectedEof
    ) {
        'COMPLETE'
    } else {
        'ERROR'
    }
    $recovery = [ordered]@{
        method = 'trim-through-last-complete-present'
        lastCompletePresentCall = $lastCompletePresentCall.ToString(
            [Globalization.CultureInfo]::InvariantCulture
        )
        trimExitCode = $trim.exitCode
        trimTimedOut = $trim.timedOut
        trimSourceWarning = $trim.stderr.Trim()
        trace = $recoveredTraceFacts
        dumpExitCode = if ($null -ne $recoveredDump) {
            $recoveredDump.exitCode
        } else {
            $null
        }
        dumpTimedOut = if ($null -ne $recoveredDump) {
            $recoveredDump.timedOut
        } else {
            $null
        }
        presentCalls = $recoveredPresentCount
        d3dretrace = $retraceFacts
        retraceExitCode = if ($null -ne $retrace) {
            $retrace.exitCode
        } else {
            $null
        }
        retraceTimedOut = if ($null -ne $retrace) {
            $retrace.timedOut
        } else {
            $null
        }
        rawRetraceExitCode = if ($null -ne $rawRetrace) {
            $rawRetrace.exitCode
        } else {
            $null
        }
        rawRetraceTimedOut = if ($null -ne $rawRetrace) {
            $rawRetrace.timedOut
        } else {
            $null
        }
        snapshotMd5Rows = $snapshotMd5Count
        uniqueSnapshotMd5Rows = $snapshotUniqueMd5Count
        rawSnapshotMd5Rows = $rawSnapshotMd5Count
        rawUniqueSnapshotMd5Rows = $rawSnapshotUniqueMd5Count
        rawUnexpectedEndOfFile = $rawHasUnexpectedEof
        frameMd5Comparison = [ordered]@{
            algorithm = 'ordered-lowercase-md5-lines-v1'
            comparedRows = $frameMd5ComparedRows
            exact = $frameMd5Exact
            firstMismatchIndex = $frameMd5FirstMismatch
        }
        unexpectedEndOfFile = $recoveredHasUnexpectedEof
        frameBoundedHealth = $recoveryHealth
    }
}

Assert-Unchanged `
    -Before $apiTraceFacts `
    -After (Get-Facts -Path $apiTracePath) `
    -Label 'apitrace executable'
Assert-Unchanged `
    -Before $d3dRetraceFacts `
    -After (Get-Facts -Path $retracePath) `
    -Label 'd3dretrace executable'
Assert-Unchanged `
    -Before $traceFacts `
    -After (Get-Facts -Path $tracePath) `
    -Label 'raw apitrace'
if ($null -ne $recoveredTraceFacts) {
    Assert-Unchanged `
        -Before $recoveredTraceFacts `
        -After (Get-Facts -Path $recoveredTracePath) `
        -Label 'recovered apitrace'
}
Assert-Unchanged `
    -Before $targetBefore `
    -After (Get-Facts -Path $targetPath) `
    -Label 'Target executable'
if (Test-Path -LiteralPath $localD3D9) {
    throw 'apitrace left an unexpected d3d9.dll beside the copied target.'
}

$receipt = [ordered]@{
    schemaVersion = 'bea-apitrace-d3d9-receipt.v5'
    name = $Name
    generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    startedAtUtc = $startedAt.ToString('o')
    finishedAtUtc = $finishedAt.ToString('o')
    requestedCaptureSeconds = $CaptureSeconds
    target = $targetBefore
    apitrace = $apiTraceFacts
    d3dretrace = $d3dRetraceFacts
    trace = $traceFacts
    process = [ordered]@{
        beaProcessId = $beaId
        beaExitCode = $beaExitCode
        beaObservedAtUtc = $beaObservedAt.ToString('o')
        requestedCaptureEndUtc = $requestedCaptureEnd.ToString('o')
        guestExitTimeUtc = if ($null -ne $guestExitTimeUtc) {
            $guestExitTimeUtc.ToString('o')
        } else {
            $null
        }
        guestExitedBeforeWindow = $guestExitedBeforeWindow
        apitraceExitCode = $apiExitCode
        closeMainWindowRequested = $closeRequested
        forcedTermination = $forcedTermination
    }
    validation = [ordered]@{
        dumpExitCode = $dump.exitCode
        dumpTimedOut = $dump.timedOut
        presentCalls = $presentCount
        frameCallBytes = ([Text.UTF8Encoding]::new($false)).GetByteCount($dump.stdout)
        targetUnchanged = $true
        localD3D9AbsentBeforeAndAfter = $true
    }
    captureHealth = $health
    frameBoundedRecovery = $recovery
    problem = $null
    limits = @(
        'This is a translated capture/replay instrument, not the retail parity oracle.',
        'The run was wall-clock bounded and contains startup activity, not an event-gated scenario.',
        'Windows apitrace does not capture D3D call stacks.'
    )
}
    if ($health -eq 'ERROR' -or
    $beaExitCode -ne 0 -or
    $guestExitedBeforeWindow -or
    ($health -eq 'PARTIAL' -and
        ($null -eq $recovery -or
            $recovery.frameBoundedHealth -ne 'COMPLETE'))) {
        $scriptExitCode = 1
    }
}
catch {
    $primaryProblem = $_.Exception.Message
    $scriptExitCode = 1
}
finally {
    if ($null -ne $bea) {
        try {
            if (-not $bea.HasExited) {
                $forcedTermination = $true
                $primaryCaptureTreeKillAttemptCount++
                $bea.Kill($true)
                $bea.WaitForExit()
                $primaryCaptureTreeKillSuccessCount++
            }
        } catch {
            $cleanupProblems.Add(
                "Failed to clean owned BEA PID $($bea.Id): $($_.Exception.Message)"
            )
        } finally {
            try { $bea.Dispose() } catch {}
        }
    }
    if ($null -ne $apiProcess) {
        try {
            if (-not $apiProcess.HasExited) {
                $forcedTermination = $true
                $primaryCaptureTreeKillAttemptCount++
                $apiProcess.Kill($true)
                $apiProcess.WaitForExit()
                $primaryCaptureTreeKillSuccessCount++
            }
        } catch {
            $cleanupProblems.Add(
                "Failed to clean apitrace PID $($apiProcess.Id): $($_.Exception.Message)"
            )
        } finally {
            try { $apiProcess.Dispose() } catch {}
        }
    }
    if ($null -ne $startedAt) {
        $samePathSurvivors = @(
            Get-Process -Name BEA -ErrorAction SilentlyContinue |
                Where-Object {
                    try {
                        $_.Path -ieq $targetPath -and
                        $_.StartTime.ToUniversalTime() -ge
                            $startedAt.AddSeconds(-1)
                    } catch {
                        $false
                    }
                }
        )
        $samePathSurvivorCount = $samePathSurvivors.Count
        foreach ($survivor in $samePathSurvivors) {
            $survivor.Dispose()
        }
        $cleanupSurvivorCount = $samePathSurvivorCount
        if ($samePathSurvivorCount -ne 0) {
            $cleanupProblems.Add(
                "$samePathSurvivorCount same-path copied-target BEA process(es) " +
                'remain; they were not killed because path and launch time do ' +
                'not prove ownership.'
            )
        }
    }
}

if ($null -eq $receipt) {
    $receipt = [ordered]@{
        schemaVersion = 'bea-apitrace-d3d9-receipt.v5'
        name = $Name
        generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        startedAtUtc = if ($null -ne $startedAt) {
            $startedAt.ToString('o')
        } else {
            $null
        }
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        requestedCaptureSeconds = $CaptureSeconds
        target = $targetBefore
        apitrace = $apiTraceFacts
        d3dretrace = $d3dRetraceFacts
        trace = $null
        process = [ordered]@{
            beaProcessId = $beaId
            beaExitCode = $null
            beaObservedAtUtc = $null
            requestedCaptureEndUtc = $null
            guestExitTimeUtc = $null
            guestExitedBeforeWindow = $null
            apitraceExitCode = $null
            closeMainWindowRequested = $false
            forcedTermination = $forcedTermination
        }
        validation = [ordered]@{
            dumpExitCode = $null
            dumpTimedOut = $null
            presentCalls = $null
            frameCallBytes = $null
            targetUnchanged = $null
            localD3D9AbsentBeforeAndAfter = $null
        }
        captureHealth = 'ERROR'
        frameBoundedRecovery = $null
        problem = $primaryProblem
        limits = @(
            'This is a translated capture/replay instrument, not the retail parity oracle.',
            'The run was wall-clock bounded and contains startup activity, not an event-gated scenario.',
            'Windows apitrace does not capture D3D call stacks.'
        )
    }
} else {
    $receipt.problem = $primaryProblem
}
if ($null -ne $primaryProblem) {
    $receipt.captureHealth = 'ERROR'
}
$receipt.process.forcedTermination = $forcedTermination
$receipt.generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
$receipt.cleanup = [ordered]@{
    primaryCaptureProcessTreeKillAttemptCount =
        $primaryCaptureTreeKillAttemptCount
    primaryCaptureProcessTreeKillSuccessCount =
        $primaryCaptureTreeKillSuccessCount
    samePathSweepPerformed = ($null -ne $startedAt)
    samePathSurvivorsWereKilled = $false
    samePathSurvivorCount = $samePathSurvivorCount
    survivorCount = $cleanupSurvivorCount
    problems = @($cleanupProblems)
}
if ($cleanupSurvivorCount -ne 0 -or
    $cleanupProblems.Count -ne 0) {
    $receipt.captureHealth = 'ERROR'
    $scriptExitCode = 1
}

$receiptPath = Join-Path $output 'receipt.json'
$receiptJson = (
    $receipt | ConvertTo-Json -Depth 12
) + [Environment]::NewLine
$receiptBytes = [Text.UTF8Encoding]::new($false).GetBytes($receiptJson)
$receiptStream = [IO.File]::Open(
    $receiptPath,
    [IO.FileMode]::CreateNew,
    [IO.FileAccess]::Write,
    [IO.FileShare]::None
)
try {
    $receiptStream.Write($receiptBytes, 0, $receiptBytes.Length)
    $receiptStream.Flush($true)
} finally {
    $receiptStream.Dispose()
}
$receipt
if ($scriptExitCode -ne 0) {
    exit $scriptExitCode
}
