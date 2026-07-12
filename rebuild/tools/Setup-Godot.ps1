# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [switch]$Offline,
    [switch]$Repair
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'GodotToolchain.psm1') -Force

if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
    throw 'LOCALAPPDATA is required for the per-user Godot toolchain cache.'
}

$ManifestPath = Join-Path $PSScriptRoot '..\toolchains\godot-4.7-stable-win-x64.json'
$CacheRoot = Join-Path $env:LOCALAPPDATA 'OnslaughtToolkit\toolchains\Godot'

function Remove-ControlledCachePath {
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $resolvedRoot = [IO.Path]::GetFullPath($CacheRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $resolvedPath = [IO.Path]::GetFullPath($Path)
    $prefix = $resolvedRoot + [IO.Path]::DirectorySeparatorChar
    if (-not $resolvedPath.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove path outside the Godot cache root: $resolvedPath"
    }

    Assert-GodotPathHasNoReparseComponents -Path $resolvedPath
    if (Test-Path -LiteralPath $resolvedPath -PathType Container) {
        Assert-GodotToolchainTreeHasNoReparsePoints -RootPath $resolvedPath
    }

    Remove-Item -LiteralPath $resolvedPath -Recurse -Force
}

function Enter-SetupLock {
    param([Parameter(Mandatory)][string]$Path)

    $deadline = [DateTime]::UtcNow.AddSeconds(60)
    do {
        try {
            return [IO.File]::Open($Path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
        }
        catch [IO.IOException] {
            if ([DateTime]::UtcNow -ge $deadline) {
                throw "Timed out waiting for the Godot toolchain setup lock: $Path"
            }

            Start-Sleep -Milliseconds 200
        }
    } while ($true)
}

$manifestFullPath = [IO.Path]::GetFullPath($ManifestPath)
$manifest = Get-Content -LiteralPath $manifestFullPath -Raw | ConvertFrom-Json
$null = Assert-PinnedGodotManifest -ManifestPath $manifestFullPath -Manifest $manifest

$CacheRoot = [IO.Path]::GetFullPath($CacheRoot)
$downloadsRoot = Join-Path $CacheRoot 'downloads'
Assert-GodotPathHasNoReparseComponents -Path $CacheRoot
New-Item -ItemType Directory -Force -Path $downloadsRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $CacheRoot 'content') | Out-Null
Assert-GodotPathHasNoReparseComponents -Path $downloadsRoot
Assert-GodotPathHasNoReparseComponents -Path (Join-Path $CacheRoot 'content')

$lock = Enter-SetupLock -Path (Join-Path $CacheRoot 'setup.lock')
$stagingPath = $null
$partialPath = $null
$contentLease = $null
try {
    $archivePath = Join-Path $downloadsRoot ([string]$manifest.archive.fileName)
    $installPath = Get-GodotToolchainInstallPath -CacheRoot $CacheRoot -ArchiveSha256 ([string]$manifest.archive.sha256)

    if ($Repair) {
        Remove-ControlledCachePath -Path $installPath
    }

    $archiveReady = $false
    if (Test-Path -LiteralPath $archivePath -PathType Leaf) {
        Assert-GodotPathHasNoReparseComponents -Path $archivePath
        try {
            $null = Test-GodotArchiveFile -ArchivePath $archivePath -Manifest $manifest
            $archiveReady = $true
        }
        catch {
            if ($Offline) {
                throw "The cached Godot archive is invalid and offline mode forbids repair. $($_.Exception.Message)"
            }

            Remove-ControlledCachePath -Path $archivePath
        }
    }

    if (-not $archiveReady) {
        if ($Offline) {
            throw 'No verified Godot archive is cached. Run Setup-Godot.ps1 once while online.'
        }

        $partialPath = Join-Path $downloadsRoot ('.download-' + [guid]::NewGuid().ToString('N') + '.partial')
        Write-Host "Downloading verified Godot $($manifest.engine.version) .NET toolchain..."
        Save-PinnedHttpsFile `
            -Uri ([uri]$manifest.archive.uri) `
            -DestinationPath $partialPath `
            -AllowedHosts @($manifest.archive.allowedRedirectHosts) `
            -ExpectedLength ([long]$manifest.archive.size)
        $null = Test-GodotArchiveFile -ArchivePath $partialPath -Manifest $manifest
        Move-Item -LiteralPath $partialPath -Destination $archivePath
        $partialPath = $null
    }

    if (-not (Test-Path -LiteralPath $installPath -PathType Container)) {
        $stagingPath = Join-Path $CacheRoot ('.extract-' + [guid]::NewGuid().ToString('N'))
        $null = Expand-SafeGodotArchive -ArchivePath $archivePath -DestinationPath $stagingPath -Manifest $manifest
        Move-Item -LiteralPath $stagingPath -Destination $installPath
        $stagingPath = $null
    }

    try {
        $contentLease = Open-VerifiedGodotToolchainLease -RootPath $installPath -Manifest $manifest
    }
    catch {
        throw "The cached Godot toolchain failed pre-execution verification. Run Setup-Godot.ps1 -Repair. $($_.Exception.Message)"
    }

    $enginePath = Join-Path $installPath ([string]$manifest.executable)
    $consolePath = Join-Path $installPath ([string]$manifest.consoleExecutable)
    $versionOutput = (& $consolePath --version 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $versionOutput -ne [string]$manifest.engine.versionOutput) {
        throw "Pinned Godot runtime identity mismatch: expected '$($manifest.engine.versionOutput)', observed '$versionOutput'."
    }

    $result = [pscustomobject]@{
        EnginePath = $enginePath
        ConsolePath = $consolePath
        Version = $versionOutput
        ArchiveSha256 = [string]$manifest.archive.sha256
        ManifestSha256 = (Get-FileHash -LiteralPath $manifestFullPath -Algorithm SHA256).Hash.ToLowerInvariant()
        FileCount = $contentLease.FileCount
        CacheVerified = $true
    }
    $ownedContentLease = $contentLease
    $ownedSetupLock = $lock
    $dispose = {
        $ownedContentLease.Dispose()
        $ownedSetupLock.Dispose()
    }.GetNewClosure()
    $result | Add-Member -MemberType ScriptMethod -Name Dispose -Value $dispose
    $contentLease = $null
    $lock = $null
    return $result
}
finally {
    if ($null -ne $partialPath) {
        Remove-ControlledCachePath -Path $partialPath
    }

    if ($null -ne $stagingPath) {
        Remove-ControlledCachePath -Path $stagingPath
    }

    if ($null -ne $contentLease) {
        $contentLease.Dispose()
    }

    if ($null -ne $lock) {
        $lock.Dispose()
    }
}
