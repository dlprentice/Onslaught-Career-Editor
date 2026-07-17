param(
    [string]$ProcessName = "BEA.exe",
    [int]$ProcessId = 0,
    [string]$LogPath = "",
    [int]$Port = 5005,
    [string]$Password = "secret",
    [string]$CommandFile = "",
    [string]$RuntimeReceiptPath = "",
    [string]$ExpectedReceiptSha256 = "",
    [string]$ExpectedCommandSha256 = "",
    [string]$RequiredLogMarker = "",
    [string]$AppOwnedProfilesRoot = "",
    [string]$ExpectedExecutablePath = "",
    [string]$ExpectedWorkingDirectory = "",
    [string]$AllowedCommandRoot = "",
    [string]$AllowedLogRoot = "",
    [switch]$AllowProcessNameAttach,
    [string]$RemoteServerArmPhrase = "",
    [int]$LogReadyTimeoutMilliseconds = 5000,
    [string]$TestOnlyCdbExecutablePath = "",
    [string]$TestOnlyCdbExecutableArm = "",
    [switch]$EnableRemoteServer,
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"
$RequiredRemoteServerArmPhrase = "ALLOW CDB REMOTE SERVER"
$RequiredTestOnlyCdbExecutableArm = "ALLOW TEST-ONLY CDB EXECUTABLE"

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
$runtimeIdentityModule = Join-Path $scriptRoot "runtime_process_identity.psm1"
$canaryInputs = @(
    $RuntimeReceiptPath,
    $ExpectedReceiptSha256,
    $ExpectedCommandSha256,
    $RequiredLogMarker
)
$canaryMode = @($canaryInputs | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) }).Count -gt 0
$validatedReceipt = $null
$testOnlyCdbRequested = -not [string]::IsNullOrWhiteSpace($TestOnlyCdbExecutablePath) -or
    -not [string]::IsNullOrWhiteSpace($TestOnlyCdbExecutableArm)
if ($testOnlyCdbRequested) {
    if ([string]::IsNullOrWhiteSpace($TestOnlyCdbExecutablePath) -or
        $TestOnlyCdbExecutableArm -cne $RequiredTestOnlyCdbExecutableArm) {
        Write-Error ("Test-only CDB executable use requires -TestOnlyCdbExecutablePath and exact arm phrase '{0}'." -f
            $RequiredTestOnlyCdbExecutableArm)
        exit 1
    }
    if (-not $canaryMode) {
        Write-Error "Test-only CDB executable use is restricted to receipt-bound canary mode."
        exit 1
    }
    if (-not (Test-Path -LiteralPath $TestOnlyCdbExecutablePath -PathType Leaf)) {
        Write-Error ("Test-only CDB executable '{0}' does not exist." -f $TestOnlyCdbExecutablePath)
        exit 1
    }
    $cdbPath = [System.IO.Path]::GetFullPath(
        (Resolve-Path -LiteralPath $TestOnlyCdbExecutablePath -ErrorAction Stop).Path)
} else {
    $cdbPath = & (Join-Path $scriptRoot "get_cdb_path.ps1") -AsLiteral
}

if ($canaryMode) {
    if (@($canaryInputs | Where-Object { [string]::IsNullOrWhiteSpace([string]$_) }).Count -gt 0 -or
        [string]::IsNullOrWhiteSpace($CommandFile)) {
        Write-Error "Canary CDB startup requires RuntimeReceiptPath, ExpectedReceiptSha256, CommandFile, ExpectedCommandSha256, and RequiredLogMarker."
        exit 1
    }
    if ($EnableRemoteServer) {
        Write-Error "Canary CDB startup is local-only and refuses remote server mode."
        exit 1
    }
    if ($AllowProcessNameAttach) {
        Write-Error "Canary CDB startup refuses process-name attach and requires the exact receipt process."
        exit 1
    }
    if ($RequiredLogMarker.Length -gt 256 -or $RequiredLogMarker -match '[\r\n]') {
        Write-Error "RequiredLogMarker must be one non-empty line of at most 256 characters."
        exit 1
    }
    Import-Module $runtimeIdentityModule -Force -ErrorAction Stop
    $validatedReceipt = Assert-RuntimeProcessReceipt `
        -ReceiptPath $RuntimeReceiptPath `
        -ExpectedReceiptSha256 $ExpectedReceiptSha256
    $receiptProcessId = [int]$validatedReceipt.Receipt.process.id
    if ($ProcessId -gt 0 -and $ProcessId -ne $receiptProcessId) {
        Write-Error ("ProcessId '{0}' does not match runtime receipt process id '{1}'." -f $ProcessId, $receiptProcessId)
        exit 1
    }
    $ProcessId = $receiptProcessId
    $receiptProcessName = [System.IO.Path]::GetFileName([string]$validatedReceipt.Receipt.process.executable.path)
    if (-not [string]::Equals($ProcessName, $receiptProcessName, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error ("ProcessName '{0}' does not match runtime receipt executable '{1}'." -f $ProcessName, $receiptProcessName)
        exit 1
    }
}

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
        Write-Error "Command-file use requires -AllowedCommandRoot so CDB input stays within an explicit task-owned directory."
        exit 1
    }

    $resolvedRoot = Resolve-ExistingDirectoryPath $AllowedRoot "Allowed command root"
    if (-not (Test-SameOrUnderRoot $resolvedPath $resolvedRoot)) {
        Write-Error ("Command file '{0}' must stay under allowed command root '{1}'." -f $resolvedPath, $resolvedRoot)
        exit 1
    }

    return $resolvedPath
}

function Assert-NoReparsePath([string]$Path, [string]$Label) {
    $currentPath = [System.IO.Path]::GetFullPath($Path)
    while (-not [string]::IsNullOrWhiteSpace($currentPath)) {
        if (Test-Path -LiteralPath $currentPath) {
            $item = Get-Item -LiteralPath $currentPath -Force -ErrorAction Stop
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw ("{0} traverses reparse point '{1}'." -f $Label, $currentPath)
            }
        }
        $parent = Split-Path -Parent $currentPath
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $currentPath) {
            break
        }
        $currentPath = $parent
    }
}

function Get-StreamSha256([System.IO.Stream]$Stream) {
    $originalPosition = $Stream.Position
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $Stream.Position = 0
        return ([System.BitConverter]::ToString($sha256.ComputeHash($Stream))).Replace("-", "").ToLowerInvariant()
    } finally {
        $Stream.Position = $originalPosition
        $sha256.Dispose()
    }
}

function Assert-HeldCommandIdentity(
    [string]$OriginalPath,
    [string]$ResolvedPath,
    [string]$ExpectedSha256,
    [System.IO.FileStream]$ReadHandle
) {
    Assert-NoReparsePath $OriginalPath "Command file path"
    Assert-NoReparsePath $ResolvedPath "Resolved command file path"
    $currentResolvedPath = [System.IO.Path]::GetFullPath(
        (Resolve-Path -LiteralPath $OriginalPath -ErrorAction Stop).Path)
    if (-not [string]::Equals(
        $currentResolvedPath,
        $ResolvedPath,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Command path identity changed: expected '{0}', found '{1}'." -f
            $ResolvedPath, $currentResolvedPath)
    }
    $actualSha256 = Get-StreamSha256 $ReadHandle
    if ($actualSha256 -cne $ExpectedSha256) {
        throw ("Command SHA-256 mismatch: expected {0}, found {1}." -f
            $ExpectedSha256, $actualSha256)
    }
    return $actualSha256
}

function Read-BoundedLogText([string]$Path, [int64]$MaximumBytes) {
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete)
    $memory = New-Object System.IO.MemoryStream
    try {
        $buffer = New-Object byte[] 8192
        [int64]$total = 0
        while ($total -le $MaximumBytes) {
            $remaining = [Math]::Min([int64]$buffer.Length, ($MaximumBytes + 1) - $total)
            if ($remaining -le 0) {
                break
            }
            $read = $stream.Read($buffer, 0, [int]$remaining)
            if ($read -eq 0) {
                break
            }
            $memory.Write($buffer, 0, $read)
            $total += $read
        }
        if ($total -gt $MaximumBytes) {
            throw "CDB readiness log exceeded the 16 MiB bound before the required marker appeared."
        }
        $bytes = $memory.ToArray()
        $text = [System.Text.Encoding]::UTF8.GetString($bytes)
        return $text.TrimStart([char]0xFEFF)
    } finally {
        $memory.Dispose()
        $stream.Dispose()
    }
}

function Get-ProcessExecutablePath([System.Diagnostics.Process]$Process, [string]$Label) {
    $Process.Refresh()
    $pidResolvedPath = Get-TargetProcessExecutablePath $Process.Id
    if ($pidResolvedPath) {
        return [System.IO.Path]::GetFullPath($pidResolvedPath)
    }
    try {
        if ($Process.Path) {
            return [System.IO.Path]::GetFullPath($Process.Path)
        }
    } catch {
        # Fall through to MainModule when PID and Process.Path queries are unavailable.
    }
    try {
        return [System.IO.Path]::GetFullPath($Process.MainModule.FileName)
    } catch {
        throw ("Could not resolve {0} executable path for process id {1}: {2}" -f
            $Label, $Process.Id, $_.Exception.Message)
    }
}

function Stop-ExactStartedProcess(
    [System.Diagnostics.Process]$StartedProcess,
    [DateTime]$StartedAtUtc,
    [string]$ExecutablePath
) {
    $StartedProcess.Refresh()
    if ($StartedProcess.HasExited) {
        return
    }
    $candidatePath = Get-ProcessExecutablePath $StartedProcess "cleanup candidate"
    $StartedProcess.Refresh()
    if ($StartedProcess.HasExited) {
        return
    }
    $candidateStartedAtUtc = $StartedProcess.StartTime.ToUniversalTime()
    if ($candidateStartedAtUtc.Ticks -ne $StartedAtUtc.Ticks -or
        -not [string]::Equals($candidatePath, $ExecutablePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("CDB cleanup identity mismatch for process id {0}; refusing to stop a reused or replaced process." -f
            $StartedProcess.Id)
    }
    $StartedProcess.Kill()
    if (-not $StartedProcess.WaitForExit(5000)) {
        throw ("CDB cleanup timed out waiting for process id {0} to exit." -f $StartedProcess.Id)
    }
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
$commandReadHandle = $null
if ($EnableRemoteServer) {
    $arguments += @("-server", ("tcp:port={0},password={1}" -f $Port, $Password))
}
if ($canaryMode) {
    $arguments += @("-pd", "-noshell", "-ee", "masm")
}

$arguments += @(
    "-logo", $LogPath
) + $targetArguments + @(
    "-noio"
)

if ($CommandFile) {
    $resolvedCommandFile = Resolve-ExistingCommandFile $CommandFile $AllowedCommandRoot
    if ($canaryMode) {
        if ($ExpectedCommandSha256 -cnotmatch '^[0-9a-f]{64}$') {
            Write-Error "ExpectedCommandSha256 must be a lowercase 64-character SHA-256 digest."
            exit 1
        }
        try {
            Assert-NoReparsePath $CommandFile "Command file path"
            Assert-NoReparsePath $resolvedCommandFile "Resolved command file path"
            $commandReadHandle = [System.IO.File]::Open(
                $resolvedCommandFile,
                [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::Read,
                [System.IO.FileShare]::Read)
            $actualCommandSha256 = Assert-HeldCommandIdentity `
                $CommandFile $resolvedCommandFile $ExpectedCommandSha256 $commandReadHandle
        } catch {
            if ($null -ne $commandReadHandle) {
                $commandReadHandle.Dispose()
            }
            Write-Error $_.Exception.Message
            exit 1
        }
        if ([string]$validatedReceipt.Receipt.generatedCommandSha256 -cne $ExpectedCommandSha256) {
            Write-Error "Runtime receipt generatedCommandSha256 does not match ExpectedCommandSha256."
            exit 1
        }
    }

    $arguments += @("-cf", $resolvedCommandFile)
}

$commandPreview = '& "{0}" {1}' -f $cdbPath, (($arguments | ForEach-Object {
    if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ }
}) -join ' ')

if ($ProcessId -gt 0) {
    $process = if ($canaryMode) {
        $validatedReceipt.Process
    } else {
        Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    }
    if (-not $process) {
        Write-Error ("Process id '{0}' is not running. Launch the copied profile first." -f $ProcessId)
        exit 1
    }

    if ($processNameOnly -and $process.ProcessName -ne $processNameOnly) {
        Write-Error ("Process id '{0}' is '{1}', not expected process '{2}'." -f $ProcessId, $process.ProcessName, $processNameOnly)
        exit 1
    }

    if ($canaryMode) {
        $receiptWorkingDirectory = [string]$validatedReceipt.Receipt.process.workingDirectory
        $receiptExecutablePath = [string]$validatedReceipt.Receipt.process.executable.path
        $derivedProfilesRoot = Split-Path -Parent $receiptWorkingDirectory
        Assert-SafeCopyAttachIdentity $process $derivedProfilesRoot $receiptExecutablePath $receiptWorkingDirectory
    } else {
        Assert-SafeCopyAttachIdentity $process $AppOwnedProfilesRoot $ExpectedExecutablePath $ExpectedWorkingDirectory
    }
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

if ($canaryMode) {
    try {
        [void](Assert-HeldCommandIdentity `
            $CommandFile $resolvedCommandFile $ExpectedCommandSha256 $commandReadHandle)
    } catch {
        $commandReadHandle.Dispose()
        Write-Error ("Command identity drifted before CDB attach: {0}" -f $_.Exception.Message)
        exit 1
    }
    try {
        $validatedReceipt = Assert-RuntimeProcessReceipt `
            -ReceiptPath $RuntimeReceiptPath `
            -ExpectedReceiptSha256 $ExpectedReceiptSha256
    } catch {
        $commandReadHandle.Dispose()
        throw
    }
    $process = $validatedReceipt.Process
}

if ($PrintOnly) {
    if ($null -ne $commandReadHandle) {
        $commandReadHandle.Dispose()
    }
    Write-Output $commandPreview
    exit 0
}

if ($canaryMode -and (Test-Path -LiteralPath $LogPath)) {
    $commandReadHandle.Dispose()
    Write-Error ("Canary CDB startup requires a fresh log path; '{0}' already exists." -f $LogPath)
    exit 1
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
$resolvedCdbPath = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $cdbPath -ErrorAction Stop).Path)
try {
    $started = Start-Process -FilePath $resolvedCdbPath -ArgumentList $arguments -WindowStyle Hidden -PassThru
} catch {
    if ($null -ne $commandReadHandle) {
        $commandReadHandle.Dispose()
    }
    throw
}
Write-Output ("CDB PID: {0}" -f $started.Id)
$requiredLogMarkerFound = $false
$maximumReadinessLogBytes = 16MB
$failureMessage = ""
$cdbStartedAtUtcValue = [DateTime]::MinValue
$cdbStartedAtUtc = ""
$cdbExecutablePath = ""

try {
    $started.Refresh()
    $cdbStartedAtUtcValue = $started.StartTime.ToUniversalTime()
    $cdbStartedAtUtc = $cdbStartedAtUtcValue.ToString("o")
    $cdbExecutablePath = Get-ProcessExecutablePath $started "started CDB"
    if (-not [string]::Equals(
        $cdbExecutablePath,
        $resolvedCdbPath,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Started debugger executable path '{0}' does not match resolved CDB path '{1}'." -f
            $cdbExecutablePath, $resolvedCdbPath)
    }
} catch {
    $failureMessage = "Could not validate started CDB process identity: {0}" -f $_.Exception.Message
}

$deadline = (Get-Date).AddMilliseconds([Math]::Max(0, $LogReadyTimeoutMilliseconds))
while (-not $failureMessage -and (Get-Date) -lt $deadline) {
    $started.Refresh()
    if ($started.HasExited) {
        $failureMessage = "CDB exited before attach/log readiness. Exit code: {0}" -f $started.ExitCode
        break
    }

    if (Test-Path -LiteralPath $LogPath) {
        if ($canaryMode) {
            try {
                $logText = Read-BoundedLogText $LogPath $maximumReadinessLogBytes
                $requiredLogMarkerFound = @($logText -split "`r?`n" | Where-Object {
                    $_.Trim() -ceq $RequiredLogMarker
                }).Count -gt 0
            } catch {
                if ($_.Exception.Message -like "*16 MiB*") {
                    $failureMessage = $_.Exception.Message
                    break
                }
                $requiredLogMarkerFound = $false
            }
            if (-not $requiredLogMarkerFound) {
                Start-Sleep -Milliseconds 200
                continue
            }
            try {
                $validatedReceipt = Assert-RuntimeProcessReceipt `
                    -ReceiptPath $RuntimeReceiptPath `
                    -ExpectedReceiptSha256 $ExpectedReceiptSha256
                $process = $validatedReceipt.Process
                [void](Assert-HeldCommandIdentity `
                    $CommandFile $resolvedCommandFile $ExpectedCommandSha256 $commandReadHandle)
            } catch {
                $failureMessage = "Runtime receipt or command identity changed before CDB marker readiness: {0}" -f $_.Exception.Message
                break
            }
        }

        if ($null -ne $commandReadHandle) {
            $commandReadHandle.Dispose()
            $commandReadHandle = $null
        }
        Write-Output ("Log ready: {0}" -f $LogPath)
        [PSCustomObject]@{
            schemaVersion = "cdb-attach-helper.v1"
            status = if ($canaryMode) { "marker-ready" } else { "log-ready" }
            targetProcessId = $process.Id
            targetProcessName = $process.ProcessName
            cdbProcessId = $started.Id
            cdbStartedAtUtc = $cdbStartedAtUtc
            cdbExecutablePath = $cdbExecutablePath
            targetReceiptSha256 = if ($canaryMode) { $ExpectedReceiptSha256 } else { $null }
            commandSha256 = if ($canaryMode) { $ExpectedCommandSha256 } else { $null }
            requiredLogMarkerFound = [bool]$requiredLogMarkerFound
            logPath = $LogPath
            effectiveArguments = if ($canaryMode) { @($arguments) } else { $null }
            remoteServerEnabled = [bool]$EnableRemoteServer
        } | ConvertTo-Json -Compress
        exit 0
    }

    Start-Sleep -Milliseconds 200
}

if (-not $failureMessage) {
    if ($canaryMode) {
        $failureMessage = "CDB required log marker '{0}' did not appear within {1} ms." -f $RequiredLogMarker, $LogReadyTimeoutMilliseconds
    } else {
        $failureMessage = "CDB log was not created within {0} ms. Attach aborted; retry with the exact copied-profile -ProcessId and inspect CDB setup." -f $LogReadyTimeoutMilliseconds
    }
}

try {
    if ($cdbStartedAtUtcValue -eq [DateTime]::MinValue) {
        throw "Started CDB start time was not captured, so exact cleanup identity cannot be proven."
    }
    Stop-ExactStartedProcess $started $cdbStartedAtUtcValue $resolvedCdbPath
} catch {
    $failureMessage = "{0} Cleanup failure: {1}" -f $failureMessage, $_.Exception.Message
} finally {
    if ($null -ne $commandReadHandle) {
        $commandReadHandle.Dispose()
        $commandReadHandle = $null
    }
}
Write-Error $failureMessage
exit 1
