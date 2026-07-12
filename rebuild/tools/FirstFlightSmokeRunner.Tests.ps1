# SPDX-License-Identifier: GPL-3.0-or-later

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'FirstFlightSmokeRunner.psm1') -Force

$script:Passed = 0

function Assert-True {
    param(
        [Parameter(Mandatory)][bool]$Condition,
        [Parameter(Mandatory)][string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
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

$scratch = Join-Path ([IO.Path]::GetTempPath()) ('onslaught-first-flight-runner-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $scratch | Out-Null
$unrelated = $null
$escapedChildPid = $null

try {
    Invoke-TestCase 'bounded output roots are unique and remain below local-proofs' {
        $repoRoot = Join-Path $scratch 'repo'
        New-Item -ItemType Directory -Path $repoRoot | Out-Null

        $first = New-BoundedFirstFlightSmokeRoot -RepoRoot $repoRoot
        $second = New-BoundedFirstFlightSmokeRoot -RepoRoot $repoRoot
        $expectedParent = [IO.Path]::GetFullPath((Join-Path $repoRoot 'local-proofs\rebuild-godot')) + [IO.Path]::DirectorySeparatorChar

        Assert-True -Condition ($first.StartsWith($expectedParent, [StringComparison]::OrdinalIgnoreCase)) -Message 'First output escaped the bounded proof root.'
        Assert-True -Condition ($second.StartsWith($expectedParent, [StringComparison]::OrdinalIgnoreCase)) -Message 'Second output escaped the bounded proof root.'
        Assert-True -Condition ($first -ne $second) -Message 'Smoke output roots must be unique.'
    }

    Invoke-TestCase 'bounded output root rejects a reparse-point proof directory' {
        $repoRoot = Join-Path $scratch 'reparse-repo'
        $outside = Join-Path $scratch 'outside'
        New-Item -ItemType Directory -Path (Join-Path $repoRoot 'local-proofs') | Out-Null
        New-Item -ItemType Directory -Path $outside | Out-Null
        $null = New-Item -ItemType Junction -Path (Join-Path $repoRoot 'local-proofs\rebuild-godot') -Target $outside

        Assert-Throws -Pattern 'reparse point' -Action {
            New-BoundedFirstFlightSmokeRoot -RepoRoot $repoRoot
        }
    }

    Invoke-TestCase 'timeout kills only the owned process and leaves an unrelated process running' {
        $sleeperScript = Join-Path $scratch 'sleeper.ps1'
        $pidFile = Join-Path $scratch 'owned.pid'
        [IO.File]::WriteAllText($sleeperScript, "[IO.File]::WriteAllText(`$args[0], [string][Environment]::ProcessId)`r`nStart-Sleep -Seconds 30`r`n")
        $pwsh = (Get-Command pwsh).Source
        $unrelated = Start-Process -FilePath $pwsh -ArgumentList @('-NoLogo', '-NoProfile', '-Command', 'Start-Sleep -Seconds 30') -WindowStyle Hidden -PassThru

        Assert-Throws -Pattern 'timed out' -Action {
            Invoke-BoundedProcess `
                -FileName $pwsh `
                -Arguments @('-NoLogo', '-NoProfile', '-File', $sleeperScript, $pidFile) `
                -TimeoutMilliseconds 750 `
                -Description 'owned test sleeper'
        }

        Assert-True -Condition (Test-Path -LiteralPath $pidFile -PathType Leaf) -Message 'Owned process did not record its PID.'
        $ownedPid = [int][IO.File]::ReadAllText($pidFile)
        Assert-True -Condition ($null -eq (Get-Process -Id $ownedPid -ErrorAction SilentlyContinue)) -Message 'Timed-out owned process remained running.'
        Assert-True -Condition ($null -ne (Get-Process -Id $unrelated.Id -ErrorAction SilentlyContinue)) -Message 'Unrelated process was terminated.'
    }

    Invoke-TestCase 'nonzero owned process fails with captured exit code' {
        Assert-Throws -Pattern 'exited with code 7' -Action {
            Invoke-BoundedProcess `
                -FileName (Get-Command pwsh).Source `
                -Arguments @('-NoLogo', '-NoProfile', '-Command', 'exit 7') `
                -TimeoutMilliseconds 5000 `
                -Description 'nonzero test process'
        }
    }

    Invoke-TestCase 'nonzero root cleanup terminates its recorded child process' {
        $parentScript = Join-Path $scratch 'parent-with-child.ps1'
        $childPidFile = Join-Path $scratch 'child.pid'
        $parentSource = @'
$child = Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList @('-NoLogo', '-NoProfile', '-Command', 'Start-Sleep -Seconds 30') -WindowStyle Hidden -PassThru
[IO.File]::WriteAllText($args[0], [string]$child.Id)
Start-Sleep -Milliseconds 500
exit 7
'@
        [IO.File]::WriteAllText($parentScript, $parentSource)

        Assert-Throws -Pattern 'exited with code 7' -Action {
            Invoke-BoundedProcess `
                -FileName (Get-Command pwsh).Source `
                -Arguments @('-NoLogo', '-NoProfile', '-File', $parentScript, $childPidFile) `
                -TimeoutMilliseconds 5000 `
                -Description 'nonzero parent with child'
        }

        Assert-True -Condition (Test-Path -LiteralPath $childPidFile -PathType Leaf) -Message 'Parent did not record its child PID.'
        $escapedChildPid = [int][IO.File]::ReadAllText($childPidFile)
        Assert-True -Condition ($null -eq (Get-Process -Id $escapedChildPid -ErrorAction SilentlyContinue)) -Message 'Owned child survived its nonzero parent cleanup.'
        $escapedChildPid = $null
    }

    Invoke-TestCase 'runner uses a suspended root and kill-on-close Windows job' {
        $runnerSource = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'FirstFlightSmokeRunner.psm1') -Raw

        Assert-True -Condition ($runnerSource -match 'CREATE_SUSPENDED') -Message 'Owned process must start suspended before job assignment.'
        Assert-True -Condition ($runnerSource -match 'JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE') -Message 'Owned process job must use kill-on-close.'
        Assert-True -Condition ($runnerSource -match 'AssignProcessToJobObject') -Message 'Owned process must be assigned to a Windows job.'
        Assert-True -Condition ($runnerSource -notmatch 'Toolhelp32|ParentProcessId|GetDescendantProcessIds') -Message 'Runner must not infer ownership from reusable PIDs.'
    }
}
finally {
    if ($null -ne $unrelated -and -not $unrelated.HasExited) {
        $unrelated.Kill($true)
        $unrelated.WaitForExit()
    }

    if ($null -ne $escapedChildPid) {
        $escapedChild = Get-Process -Id $escapedChildPid -ErrorAction SilentlyContinue
        if ($null -ne $escapedChild) {
            $escapedChild.Kill($true)
            $escapedChild.WaitForExit()
        }
    }

    $resolvedScratch = [IO.Path]::GetFullPath($scratch)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedScratch.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -and
        [IO.Path]::GetFileName($resolvedScratch).StartsWith('onslaught-first-flight-runner-tests-', [StringComparison]::Ordinal)) {
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    }
}

Write-Host "First Flight smoke runner tests: PASS ($script:Passed cases)"
