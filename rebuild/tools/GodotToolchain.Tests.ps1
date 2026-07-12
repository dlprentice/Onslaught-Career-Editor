# SPDX-License-Identifier: GPL-3.0-or-later

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'GodotToolchain.psm1') -Force

$script:Passed = 0

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

function Get-TextSha256 {
    param([Parameter(Mandatory)][string]$Text)

    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
}

function New-TestManifest {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content
    )

    return [pscustomobject]@{
        rootDirectory = 'tool'
        files = @(
            [pscustomobject]@{
                path = $Path
                length = [Text.Encoding]::UTF8.GetByteCount($Content)
                sha256 = Get-TextSha256 -Text $Content
            }
        )
    }
}

function New-TestZip {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][array]$Entries
    )

    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    try {
        $archive = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Create, $true)
        try {
            foreach ($item in $Entries) {
                $entry = $archive.CreateEntry([string]$item.Path)
                if ($null -ne $item.ExternalAttributes) {
                    $entry.ExternalAttributes = [int]$item.ExternalAttributes
                }

                if ($null -ne $item.Content) {
                    $writer = [IO.StreamWriter]::new($entry.Open(), [Text.UTF8Encoding]::new($false))
                    try {
                        $writer.Write([string]$item.Content)
                    }
                    finally {
                        $writer.Dispose()
                    }
                }
            }
        }
        finally {
            $archive.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

$scratch = Join-Path ([IO.Path]::GetTempPath()) ('onslaught-godot-toolchain-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $scratch | Out-Null

try {
    Invoke-TestCase 'safe archive extracts and verifies exact content' {
        $zip = Join-Path $scratch 'safe.zip'
        $destination = Join-Path $scratch 'safe-out'
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'
        New-TestZip -Path $zip -Entries @(
            @{ Path = 'tool/'; Content = $null; ExternalAttributes = $null },
            @{ Path = 'tool/bin/tool.exe'; Content = 'trusted'; ExternalAttributes = $null }
        )

        $null = Expand-SafeGodotArchive -ArchivePath $zip -DestinationPath $destination -Manifest $manifest
        $verification = Test-GodotToolchainTree -RootPath $destination -Manifest $manifest

        Assert-True -Condition $verification.Valid -Message 'Expected the extracted tree to verify.'
        Assert-Equal -Expected 1 -Actual $verification.FileCount -Message 'Unexpected verified file count.'
    }

    Invoke-TestCase 'path traversal is rejected before extraction' {
        $zip = Join-Path $scratch 'traversal.zip'
        $destination = Join-Path $scratch 'traversal-out'
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'
        New-TestZip -Path $zip -Entries @(
            @{ Path = 'tool/bin/tool.exe'; Content = 'trusted'; ExternalAttributes = $null },
            @{ Path = 'tool/../../escape.txt'; Content = 'escape'; ExternalAttributes = $null }
        )

        Assert-Throws -Pattern 'unsafe archive path' -Action {
            $null = Expand-SafeGodotArchive -ArchivePath $zip -DestinationPath $destination -Manifest $manifest
        }
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $scratch 'escape.txt'))) -Message 'Traversal created an outside file.'
    }

    Invoke-TestCase 'case-insensitive duplicate entries are rejected' {
        $zip = Join-Path $scratch 'duplicate.zip'
        $destination = Join-Path $scratch 'duplicate-out'
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'
        New-TestZip -Path $zip -Entries @(
            @{ Path = 'tool/bin/tool.exe'; Content = 'trusted'; ExternalAttributes = $null },
            @{ Path = 'tool/BIN/TOOL.EXE'; Content = 'other'; ExternalAttributes = $null }
        )

        Assert-Throws -Pattern 'duplicate archive path' -Action {
            $null = Expand-SafeGodotArchive -ArchivePath $zip -DestinationPath $destination -Manifest $manifest
        }
    }

    Invoke-TestCase 'symbolic-link entries are rejected' {
        $zip = Join-Path $scratch 'symlink.zip'
        $destination = Join-Path $scratch 'symlink-out'
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'
        New-TestZip -Path $zip -Entries @(
            @{ Path = 'tool/bin/tool.exe'; Content = 'trusted'; ExternalAttributes = -1610612736 }
        )

        Assert-Throws -Pattern 'symbolic link' -Action {
            $null = Expand-SafeGodotArchive -ArchivePath $zip -DestinationPath $destination -Manifest $manifest
        }
    }

    Invoke-TestCase 'unexpected archive files are rejected' {
        $zip = Join-Path $scratch 'unexpected.zip'
        $destination = Join-Path $scratch 'unexpected-out'
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'
        New-TestZip -Path $zip -Entries @(
            @{ Path = 'tool/bin/tool.exe'; Content = 'trusted'; ExternalAttributes = $null },
            @{ Path = 'tool/extra.txt'; Content = 'extra'; ExternalAttributes = $null }
        )

        Assert-Throws -Pattern 'does not match the pinned manifest' -Action {
            $null = Expand-SafeGodotArchive -ArchivePath $zip -DestinationPath $destination -Manifest $manifest
        }
    }

    Invoke-TestCase 'post-extraction mutation fails closed' {
        $zip = Join-Path $scratch 'mutation.zip'
        $destination = Join-Path $scratch 'mutation-out'
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'
        New-TestZip -Path $zip -Entries @(
            @{ Path = 'tool/bin/tool.exe'; Content = 'trusted'; ExternalAttributes = $null }
        )
        $null = Expand-SafeGodotArchive -ArchivePath $zip -DestinationPath $destination -Manifest $manifest

        [IO.File]::WriteAllText((Join-Path $destination 'bin/tool.exe'), 'hacked!')

        Assert-Throws -Pattern 'hash mismatch' -Action {
            Test-GodotToolchainTree -RootPath $destination -Manifest $manifest
        }
    }

    Invoke-TestCase 'content-addressed install path includes the full archive hash' {
        $path = Get-GodotToolchainInstallPath -CacheRoot 'C:\cache' -ArchiveSha256 ('a' * 64)

        Assert-Equal -Expected (Join-Path 'C:\cache' ('content\sha256-' + ('a' * 64))) -Actual $path -Message 'Unexpected install path.'
    }

    Invoke-TestCase 'double-click launcher requires PowerShell 7 without policy bypass' {
        $launcher = Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\Launch First Flight.cmd') -Raw

        Assert-True -Condition ($launcher -match '(?im)^where pwsh(?:\.exe)?\b') -Message 'Launcher must fail clearly when PowerShell 7 is absent.'
        Assert-True -Condition ($launcher -match '(?im)^pwsh(?:\.exe)?\b') -Message 'Launcher must invoke PowerShell 7.'
        Assert-True -Condition ($launcher -notmatch '(?i)ExecutionPolicy|Bypass') -Message 'Launcher must not bypass host execution policy.'
        Assert-True -Condition ($launcher -notmatch '(?im)^powershell(?:\.exe)?\b') -Message 'Launcher must not invoke Windows PowerShell 5.1.'
    }

    Invoke-TestCase 'normal setup accepts only the exact tracked Godot manifest' {
        $manifestPath = Join-Path $PSScriptRoot '..\toolchains\godot-4.7-stable-win-x64.json'
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

        $verified = Assert-PinnedGodotManifest -ManifestPath $manifestPath -Manifest $manifest
        Assert-True -Condition $verified.Valid -Message 'Expected the tracked pinned manifest to pass.'

        $copiedManifestPath = Join-Path $scratch 'copied-manifest.json'
        Copy-Item -LiteralPath $manifestPath -Destination $copiedManifestPath
        Assert-Throws -Pattern 'tracked manifest path' -Action {
            Assert-PinnedGodotManifest -ManifestPath $copiedManifestPath -Manifest $manifest
        }

        $substitutedManifestPath = Join-Path $scratch 'substituted-manifest.json'
        (Get-Content -LiteralPath $manifestPath -Raw).Replace('github.com', 'example.com') |
            Set-Content -LiteralPath $substitutedManifestPath -NoNewline
        $substitutedManifest = Get-Content -LiteralPath $substitutedManifestPath -Raw | ConvertFrom-Json
        Assert-Throws -Pattern 'tracked manifest path|manifest hash mismatch' -Action {
            Assert-PinnedGodotManifest -ManifestPath $substitutedManifestPath -Manifest $substitutedManifest
        }
        Assert-Throws -Pattern 'manifest value mismatch' -Action {
            Assert-PinnedGodotManifest -ManifestPath $manifestPath -Manifest $substitutedManifest
        }
    }

    Invoke-TestCase 'verified toolchain rejects a reparse-point root' {
        $target = Join-Path $scratch 'reparse-target'
        $junction = Join-Path $scratch 'reparse-root'
        New-Item -ItemType Directory -Path (Join-Path $target 'bin') | Out-Null
        [IO.File]::WriteAllText((Join-Path $target 'bin\tool.exe'), 'trusted')
        $null = New-Item -ItemType Junction -Path $junction -Target $target
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'

        Assert-Throws -Pattern 'reparse point' -Action {
            Test-GodotToolchainTree -RootPath $junction -Manifest $manifest
        }
    }

    Invoke-TestCase 'verified lease blocks mutation until disposed' {
        $root = Join-Path $scratch 'leased-tree'
        $file = Join-Path $root 'bin\tool.exe'
        New-Item -ItemType Directory -Path (Split-Path -Parent $file) | Out-Null
        [IO.File]::WriteAllText($file, 'trusted')
        $manifest = New-TestManifest -Path 'bin/tool.exe' -Content 'trusted'

        $lease = Open-VerifiedGodotToolchainLease -RootPath $root -Manifest $manifest
        try {
            Assert-Equal -Expected 1 -Actual $lease.FileCount -Message 'Unexpected leased file count.'
            Assert-Throws -Pattern 'used by another process|access.*denied|sharing violation' -Action {
                [IO.File]::WriteAllText($file, 'mutated')
            }
        }
        finally {
            $lease.Dispose()
        }

        [IO.File]::WriteAllText($file, 'released')
        Assert-Equal -Expected 'released' -Actual ([IO.File]::ReadAllText($file)) -Message 'Disposed lease still blocked mutation.'
    }

    Invoke-TestCase 'cache path validation rejects reparse-point ancestors' {
        $target = Join-Path $scratch 'cache-target'
        $junction = Join-Path $scratch 'cache-junction'
        New-Item -ItemType Directory -Path $target | Out-Null
        $null = New-Item -ItemType Junction -Path $junction -Target $target

        Assert-Throws -Pattern 'reparse point' -Action {
            Assert-GodotPathHasNoReparseComponents -Path (Join-Path $junction 'content\future')
        }
    }
}
finally {
    $resolvedScratch = [IO.Path]::GetFullPath($scratch)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedScratch.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -and
        [IO.Path]::GetFileName($resolvedScratch).StartsWith('onslaught-godot-toolchain-tests-', [StringComparison]::Ordinal)) {
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    }
}

Write-Host "Godot toolchain tests: PASS ($script:Passed cases)"
