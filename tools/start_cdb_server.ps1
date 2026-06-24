param(
    [string]$ProcessName = "BEA.exe",
    [int]$ProcessId = 0,
    [string]$LogPath = "",
    [int]$Port = 5005,
    [string]$Password = "secret",
    [string]$CommandFile = "",
    [string]$AppOwnedProfilesRoot = "",
    [string]$ExpectedExecutablePath = "",
    [string]$ExpectedWorkingDirectory = "",
    [string]$AllowedCommandRoot = "",
    [string]$AllowedLogRoot = "",
    [switch]$AllowProcessNameAttach,
    [string]$RemoteServerArmPhrase = "",
    [int]$LogReadyTimeoutMilliseconds = 5000,
    [switch]$EnableRemoteServer,
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"
$RequiredRemoteServerArmPhrase = "ALLOW CDB REMOTE SERVER"

if ($Password -notmatch '^[A-Za-z0-9_]+$') {
    Write-Error "Password must contain only letters, digits, or underscores. CDB can exit before logging when the TCP server password contains punctuation."
    exit 1
}

if ($EnableRemoteServer) {
    if ($RemoteServerArmPhrase -ne $RequiredRemoteServerArmPhrase) {
        Write-Error ("Remote CDB server mode requires -RemoteServerArmPhrase ""{0}""." -f $RequiredRemoteServerArmPhrase)
        exit 1
    }

    if ($Password -eq "secret") {
        Write-Error "Remote CDB server mode requires a non-default alphanumeric/underscore password."
        exit 1
    }
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$cdbPath = & (Join-Path $scriptRoot "get_cdb_path.ps1") -AsLiteral

function Resolve-ExistingFilePath([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Write-Error ("{0} '{1}' does not exist." -f $Label, $Path)
        exit 1
    }

    return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).Path)
}

function Resolve-ExistingDirectoryPath([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        Write-Error ("{0} '{1}' does not exist." -f $Label, $Path)
        exit 1
    }

    return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
}

function Get-TargetProcessExecutablePath([int]$TargetProcessId) {
    $processInfo = Get-CimInstance Win32_Process -Filter ("ProcessId = {0}" -f $TargetProcessId) -ErrorAction SilentlyContinue
    if ($processInfo -and $processInfo.ExecutablePath) {
        return [System.IO.Path]::GetFullPath($processInfo.ExecutablePath)
    }

    try {
        $targetProcess = Get-Process -Id $TargetProcessId -ErrorAction Stop
        if ($targetProcess.Path) {
            return [System.IO.Path]::GetFullPath($targetProcess.Path)
        }
    } catch {
        return ""
    }

    return ""
}

function Test-SameOrUnderRoot([string]$Path, [string]$Root) {
    $normalizedPath = [System.IO.Path]::GetFullPath($Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    $normalizedRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    return $normalizedPath.TrimEnd([System.IO.Path]::DirectorySeparatorChar) -ieq $normalizedRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) -or
        $normalizedPath.StartsWith($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-StrictlyUnderRoot([string]$Path, [string]$Root) {
    $normalizedPath = [System.IO.Path]::GetFullPath($Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $normalizedRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    return $normalizedPath -ine $normalizedRoot -and (Test-SameOrUnderRoot $normalizedPath $normalizedRoot)
}

function Test-KnownSteamInstallShape([string]$Path) {
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $parts = $fullPath.Split([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) | Where-Object { $_ }
    for ($i = 0; $i -le ($parts.Count - 3); $i++) {
        if ($parts[$i] -ieq "steamapps" -and $parts[$i + 1] -ieq "common" -and $parts[$i + 2] -ieq "Battle Engine Aquila") {
            return $true
        }
    }

    return $false
}

function Test-ProtectedInstallRoot([string]$Path) {
    foreach ($key in @("ProgramFiles", "ProgramFiles(x86)")) {
        $root = [Environment]::GetEnvironmentVariable($key)
        if ($root -and (Test-SameOrUnderRoot $Path $root)) {
            return $true
        }
    }

    return $false
}

function Assert-SafeCopyAttachIdentity(
    [System.Diagnostics.Process]$Process,
    [string]$AppRoot,
    [string]$ExpectedExe,
    [string]$ExpectedDir
) {
    if (-not $AppRoot -or -not $ExpectedExe -or -not $ExpectedDir) {
        Write-Error "CDB attach requires -AppOwnedProfilesRoot, -ExpectedExecutablePath, and -ExpectedWorkingDirectory so it can prove the target is a generated copied profile."
        exit 1
    }

    $appRootPath = Resolve-ExistingDirectoryPath $AppRoot "App-owned profiles root"
    $expectedDirectory = Resolve-ExistingDirectoryPath $ExpectedDir "Expected working directory"
    $expectedExePath = Resolve-ExistingFilePath $ExpectedExe "Expected executable path"

    if (-not (Test-StrictlyUnderRoot $expectedDirectory $appRootPath)) {
        Write-Error ("Expected working directory '{0}' must be inside app-owned profiles root '{1}'." -f $expectedDirectory, $appRootPath)
        exit 1
    }

    if ((Test-ProtectedInstallRoot $expectedDirectory) -or (Test-KnownSteamInstallShape $expectedDirectory)) {
        Write-Error ("Expected working directory '{0}' looks like an installed/protected game root, not an app-owned copied profile." -f $expectedDirectory)
        exit 1
    }

    $expectedCopiedExe = [System.IO.Path]::GetFullPath((Join-Path $expectedDirectory "BEA.exe"))
    if ($expectedExePath -ine $expectedCopiedExe) {
        Write-Error ("Expected executable path '{0}' must be the copied BEA.exe under expected working directory '{1}'." -f $expectedExePath, $expectedDirectory)
        exit 1
    }

    $actualExe = Get-TargetProcessExecutablePath $Process.Id
    if (-not $actualExe) {
        Write-Error ("Could not resolve executable path for process id '{0}'. Refusing CDB attach without process identity proof." -f $Process.Id)
        exit 1
    }

    if ($actualExe -ine $expectedExePath) {
        Write-Error ("Process id '{0}' executable '{1}' does not match expected copied executable '{2}'." -f $Process.Id, $actualExe, $expectedExePath)
        exit 1
    }

    $manifestPath = Join-Path $expectedDirectory "onslaught-profile-manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        Write-Error ("Expected working directory '{0}' is missing generated copied-profile manifest '{1}'." -f $expectedDirectory, $manifestPath)
        exit 1
    }

    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    } catch {
        Write-Error ("Generated copied-profile manifest '{0}' is not valid JSON: {1}" -f $manifestPath, $_.Exception.Message)
        exit 1
    }

    if ($manifest.schemaVersion -ne "winui-copied-game-profile.v1") {
        Write-Error ("Generated copied-profile manifest '{0}' has unsupported schema '{1}'." -f $manifestPath, $manifest.schemaVersion)
        exit 1
    }

    if ($manifest.mutation -ne $true) {
        Write-Error ("Generated copied-profile manifest '{0}' does not record a materialized copied profile." -f $manifestPath)
        exit 1
    }

    if ([string]::IsNullOrWhiteSpace([string]$manifest.targetGameRoot)) {
        Write-Error ("Generated copied-profile manifest '{0}' is missing targetGameRoot." -f $manifestPath)
        exit 1
    }

    if ($manifest.targetGameRoot -ne ".") {
        $manifestRoot = [System.IO.Path]::GetFullPath((Join-Path $expectedDirectory ([string]$manifest.targetGameRoot))).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
        if ($manifestRoot -ine $expectedDirectory) {
            Write-Error ("Generated copied-profile manifest '{0}' does not point at expected working directory '{1}'." -f $manifestPath, $expectedDirectory)
            exit 1
        }
    }

    if ($manifest.executablePath) {
        $manifestExe = [System.IO.Path]::GetFullPath((Join-Path $expectedDirectory ([string]$manifest.executablePath)))
        if ($manifestExe -ine $expectedExePath) {
            Write-Error ("Generated copied-profile manifest executable '{0}' does not match expected copied executable '{1}'." -f $manifestExe, $expectedExePath)
            exit 1
        }
    }
}

function Resolve-ExistingCommandFile([string]$Path, [string]$AllowedRoot) {
    $resolvedPath = Resolve-ExistingFilePath $Path "Command file"
    if (-not $AllowedRoot) {
        $AllowedRoot = Join-Path $scriptRoot "runtime-probes"
    }

    $resolvedRoot = Resolve-ExistingDirectoryPath $AllowedRoot "Allowed command root"
    if (-not (Test-SameOrUnderRoot $resolvedPath $resolvedRoot)) {
        Write-Error ("Command file '{0}' must stay under allowed command root '{1}'." -f $resolvedPath, $resolvedRoot)
        exit 1
    }

    return $resolvedPath
}

function Assert-LogPathUnderAllowedRoot([string]$Path, [string]$AllowedRoot) {
    if (-not $AllowedRoot) {
        return
    }

    $resolvedRoot = Resolve-ExistingDirectoryPath $AllowedRoot "Allowed log root"
    $resolvedPath = [System.IO.Path]::GetFullPath($Path)
    if (-not (Test-SameOrUnderRoot $resolvedPath $resolvedRoot)) {
        Write-Error ("Log path '{0}' must stay under allowed log root '{1}'." -f $resolvedPath, $resolvedRoot)
        exit 1
    }
}

if (-not $LogPath) {
    $timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
    $LogPath = Join-Path $env:TEMP ("bea-cdb-{0}.log" -f $timestamp)
}

Assert-LogPathUnderAllowedRoot $LogPath $AllowedLogRoot

$processNameOnly = [System.IO.Path]::GetFileNameWithoutExtension($ProcessName)

if ($ProcessId -gt 0) {
    $targetArguments = @("-p", $ProcessId.ToString())
    $targetDescription = "PID {0}" -f $ProcessId
} else {
    $targetArguments = @("-pn", $ProcessName)
    $targetDescription = "process name {0}" -f $ProcessName
}

$arguments = @()
if ($EnableRemoteServer) {
    $arguments += @("-server", ("tcp:port={0},password={1}" -f $Port, $Password))
}

$arguments += @(
    "-logo", $LogPath
) + $targetArguments + @(
    "-noio"
)

if ($CommandFile) {
    $resolvedCommandFile = Resolve-ExistingCommandFile $CommandFile $AllowedCommandRoot

    $arguments += @("-cf", $resolvedCommandFile)
}

$commandPreview = '& "{0}" {1}' -f $cdbPath, (($arguments | ForEach-Object {
    if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ }
}) -join ' ')

if ($ProcessId -gt 0) {
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $process) {
        Write-Error ("Process id '{0}' is not running. Launch the copied profile first." -f $ProcessId)
        exit 1
    }

    if ($processNameOnly -and $process.ProcessName -ne $processNameOnly) {
        Write-Error ("Process id '{0}' is '{1}', not expected process '{2}'." -f $ProcessId, $process.ProcessName, $processNameOnly)
        exit 1
    }

    Assert-SafeCopyAttachIdentity $process $AppOwnedProfilesRoot $ExpectedExecutablePath $ExpectedWorkingDirectory
} else {
    if (-not $AllowProcessNameAttach) {
        Write-Error "CDB attach now requires -ProcessId for exact copied-profile attach. Use -AllowProcessNameAttach only for an explicitly reviewed legacy diagnostic."
        exit 1
    }

    $matchingProcesses = @(Get-Process -Name $processNameOnly -ErrorAction SilentlyContinue)
    if ($matchingProcesses.Count -eq 0) {
        Write-Error ("Process '{0}' is not running. Launch the game first." -f $ProcessName)
        exit 1
    }

    if ($matchingProcesses.Count -gt 1) {
        $ids = ($matchingProcesses | ForEach-Object { $_.Id }) -join ", "
        Write-Error ("Found multiple '{0}' processes ({1}). Re-run with -ProcessId for an exact copied-profile attach." -f $ProcessName, $ids)
        exit 1
    }

    $process = $matchingProcesses[0]
    Assert-SafeCopyAttachIdentity $process $AppOwnedProfilesRoot $ExpectedExecutablePath $ExpectedWorkingDirectory
}

if ($PrintOnly) {
    Write-Output $commandPreview
    exit 0
}

$logDirectory = Split-Path -Parent $LogPath
if ($logDirectory -and -not (Test-Path -LiteralPath $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory | Out-Null
}

Write-Output ("Attaching x86 CDB to PID {0} ({1}) using {2}" -f $process.Id, $process.ProcessName, $targetDescription)
Write-Output ("Log: {0}" -f $LogPath)
if ($EnableRemoteServer) {
    Write-Output ("Remote server port: {0}" -f $Port)
} else {
    Write-Output "Remote server: disabled"
}
$started = Start-Process -FilePath $cdbPath -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output ("CDB PID: {0}" -f $started.Id)

$deadline = (Get-Date).AddMilliseconds([Math]::Max(0, $LogReadyTimeoutMilliseconds))
while ((Get-Date) -lt $deadline) {
    $started.Refresh()
    if ($started.HasExited) {
        Write-Error ("CDB exited before attach/log readiness. Exit code: {0}" -f $started.ExitCode)
        exit 1
    }

    if (Test-Path -LiteralPath $LogPath) {
        Write-Output ("Log ready: {0}" -f $LogPath)
        [PSCustomObject]@{
            schemaVersion = "cdb-attach-helper.v1"
            status = "log-ready"
            targetProcessId = $process.Id
            targetProcessName = $process.ProcessName
            cdbProcessId = $started.Id
            logPath = $LogPath
            remoteServerEnabled = [bool]$EnableRemoteServer
        } | ConvertTo-Json -Compress
        exit 0
    }

    Start-Sleep -Milliseconds 200
}

try {
    $started.Refresh()
    if (-not $started.HasExited) {
        Stop-Process -Id $started.Id -Force -ErrorAction SilentlyContinue
    }
} catch {
    # Best-effort cleanup after a failed debugger attach.
}

Write-Error ("CDB log was not created within {0} ms. Attach aborted; retry with the exact copied-profile -ProcessId and inspect CDB setup." -f $LogReadyTimeoutMilliseconds)
exit 1
