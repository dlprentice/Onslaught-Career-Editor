# SPDX-License-Identifier: GPL-3.0-or-later

Set-StrictMode -Version Latest

function Assert-PinnedGodotManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ManifestPath,
        [Parameter(Mandatory)]$Manifest
    )

    $expectedPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\toolchains\godot-4.7-stable-win-x64.json'))
    $observedPath = [IO.Path]::GetFullPath($ManifestPath)
    if (-not $observedPath.Equals($expectedPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Godot setup requires the tracked manifest path '$expectedPath'."
    }

    $expectedManifestHash = '634ff6c7e84977b60350127df1bbc1306158a2e95be59600676bae84ad1a5042'
    $actualManifestHash = (Get-FileHash -LiteralPath $observedPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualManifestHash -ne $expectedManifestHash) {
        throw "Pinned Godot manifest hash mismatch: expected $expectedManifestHash, observed $actualManifestHash."
    }

    $expectedValues = [ordered]@{
        'schemaVersion' = 'onslaught-godot-toolchain.v1'
        'rootDirectory' = 'Godot_v4.7-stable_mono_win64'
        'executable' = 'Godot_v4.7-stable_mono_win64.exe'
        'consoleExecutable' = 'Godot_v4.7-stable_mono_win64_console.exe'
        'archive.fileName' = 'Godot_v4.7-stable_mono_win64.zip'
        'archive.uri' = 'https://github.com/godotengine/godot/releases/download/4.7-stable/Godot_v4.7-stable_mono_win64.zip'
        'archive.size' = 114324762L
        'archive.sha256' = '73087f2ef4940be2c0bff358280053912182aca82b85891d6e42d9ebc5c26880'
        'engine.version' = '4.7-stable'
        'engine.versionOutput' = '4.7.stable.mono.official.5b4e0cb0f'
        'engine.godotNetSdkVersion' = '4.7.0'
        'engine.license' = 'MIT'
        'engine.officialReleasePage' = 'https://godotengine.org/download/archive/4.7-stable/'
    }
    $actualValues = [ordered]@{
        'schemaVersion' = [string]$Manifest.schemaVersion
        'rootDirectory' = [string]$Manifest.rootDirectory
        'executable' = [string]$Manifest.executable
        'consoleExecutable' = [string]$Manifest.consoleExecutable
        'archive.fileName' = [string]$Manifest.archive.fileName
        'archive.uri' = [string]$Manifest.archive.uri
        'archive.size' = [long]$Manifest.archive.size
        'archive.sha256' = [string]$Manifest.archive.sha256
        'engine.version' = [string]$Manifest.engine.version
        'engine.versionOutput' = [string]$Manifest.engine.versionOutput
        'engine.godotNetSdkVersion' = [string]$Manifest.engine.godotNetSdkVersion
        'engine.license' = [string]$Manifest.engine.license
        'engine.officialReleasePage' = [string]$Manifest.engine.officialReleasePage
    }
    foreach ($name in $expectedValues.Keys) {
        if ($actualValues[$name] -ne $expectedValues[$name]) {
            throw "Pinned Godot manifest value mismatch for '$name'."
        }
    }

    $expectedHosts = 'github.com|release-assets.githubusercontent.com'
    $actualHosts = (@($Manifest.archive.allowedRedirectHosts) | ForEach-Object { ([string]$_).ToLowerInvariant() } | Sort-Object) -join '|'
    if ($actualHosts -ne $expectedHosts) {
        throw "Pinned Godot manifest value mismatch for 'archive.allowedRedirectHosts'."
    }

    $fileMap = Get-ManifestFileMap -Manifest $Manifest
    if ($fileMap.Count -ne 82) {
        throw "Pinned Godot manifest value mismatch for 'files': expected 82 entries, observed $($fileMap.Count)."
    }

    return [pscustomobject]@{
        Valid = $true
        Path = $observedPath
        Sha256 = $actualManifestHash
    }
}

function Get-ManifestFileMap {
    param([Parameter(Mandatory)]$Manifest)

    $map = [Collections.Generic.Dictionary[string, object]]::new([StringComparer]::OrdinalIgnoreCase)
    $files = @($Manifest.files)
    if ($files.Count -gt 1024) {
        throw "Pinned manifest exceeds the 1024-file safety limit."
    }

    [long]$totalLength = 0
    foreach ($file in $files) {
        $path = [string]$file.path
        if ([string]::IsNullOrWhiteSpace($path) -or
            $path.Contains('\') -or
            $path.StartsWith('/', [StringComparison]::Ordinal) -or
            $path.Contains(':') -or
            @($path.Split('/')) -contains '..' -or
            @($path.Split('/')) -contains '.') {
            throw "Pinned manifest contains unsafe file path '$path'."
        }

        if (-not $map.TryAdd($path, $file)) {
            throw "Pinned manifest contains duplicate file path '$path'."
        }

        $length = [long]$file.length
        if ($length -lt 0 -or $length -gt 536870912) {
            throw "Pinned manifest contains unsafe length for '$path'."
        }

        $hash = [string]$file.sha256
        if ($hash -notmatch '^[0-9a-fA-F]{64}$') {
            throw "Pinned manifest contains invalid SHA-256 for '$path'."
        }

        $totalLength += $length
    }

    if ($map.Count -eq 0) {
        throw 'Pinned manifest contains no files.'
    }

    if ($totalLength -gt 1073741824) {
        throw 'Pinned manifest exceeds the 1 GiB extraction safety limit.'
    }

    return $map
}

function Test-GodotArchiveFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ArchivePath,
        [Parameter(Mandatory)]$Manifest
    )

    if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf)) {
        throw "Godot archive does not exist: $ArchivePath"
    }

    $file = Get-Item -LiteralPath $ArchivePath
    $expectedLength = [long]$Manifest.archive.size
    if ($file.Length -ne $expectedLength) {
        throw "Godot archive length mismatch: expected $expectedLength, observed $($file.Length)."
    }

    $expectedHash = ([string]$Manifest.archive.sha256).ToLowerInvariant()
    if ($expectedHash -notmatch '^[0-9a-f]{64}$') {
        throw 'Godot archive manifest contains an invalid SHA-256.'
    }

    $actualHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $expectedHash) {
        throw "Godot archive hash mismatch: expected $expectedHash, observed $actualHash."
    }

    return [pscustomobject]@{
        Valid = $true
        Length = $file.Length
        Sha256 = $actualHash
        Path = $file.FullName
    }
}

function Save-PinnedHttpsFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][uri]$Uri,
        [Parameter(Mandatory)][string]$DestinationPath,
        [Parameter(Mandatory)][string[]]$AllowedHosts,
        [Parameter(Mandatory)][long]$ExpectedLength
    )

    if (Test-Path -LiteralPath $DestinationPath) {
        throw "Download destination already exists: $DestinationPath"
    }

    $allowed = [Collections.Generic.HashSet[string]]::new($AllowedHosts, [StringComparer]::OrdinalIgnoreCase)
    $handler = [Net.Http.HttpClientHandler]::new()
    $handler.AllowAutoRedirect = $false
    $client = [Net.Http.HttpClient]::new($handler)
    $client.DefaultRequestHeaders.UserAgent.ParseAdd('Onslaught-Rebuild-Toolchain/1.0')
    $current = $Uri

    try {
        for ($redirectCount = 0; $redirectCount -le 5; $redirectCount++) {
            if ($current.Scheme -ne 'https' -or -not $allowed.Contains($current.Host)) {
                throw "Godot download URI is not an allowed HTTPS host: $current"
            }

            $response = $client.GetAsync($current, [Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
            try {
                $status = [int]$response.StatusCode
                if ($status -in @(301, 302, 303, 307, 308)) {
                    if ($redirectCount -eq 5 -or $null -eq $response.Headers.Location) {
                        throw 'Godot download exceeded the redirect limit or returned an empty redirect.'
                    }

                    $current = [uri]::new($current, $response.Headers.Location)
                    continue
                }

                $response.EnsureSuccessStatusCode()
                if ($response.Content.Headers.ContentLength.HasValue -and
                    $response.Content.Headers.ContentLength.Value -ne $ExpectedLength) {
                    throw "Godot download length header mismatch: expected $ExpectedLength, observed $($response.Content.Headers.ContentLength.Value)."
                }

                $input = $response.Content.ReadAsStream()
                try {
                    $output = [IO.File]::Open($DestinationPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                    try {
                        $buffer = [byte[]]::new(1MB)
                        [long]$written = 0
                        while (($read = $input.Read($buffer, 0, $buffer.Length)) -gt 0) {
                            $written += $read
                            if ($written -gt $ExpectedLength) {
                                throw "Godot download exceeded expected length $ExpectedLength."
                            }

                            $output.Write($buffer, 0, $read)
                        }
                    }
                    finally {
                        $output.Dispose()
                    }
                }
                finally {
                    $input.Dispose()
                }

                $observedLength = (Get-Item -LiteralPath $DestinationPath).Length
                if ($observedLength -ne $ExpectedLength) {
                    throw "Godot download length mismatch: expected $ExpectedLength, observed $observedLength."
                }

                return
            }
            finally {
                $response.Dispose()
            }
        }
    }
    catch {
        if (Test-Path -LiteralPath $DestinationPath) {
            Remove-Item -LiteralPath $DestinationPath -Force
        }

        throw
    }
    finally {
        $client.Dispose()
        $handler.Dispose()
    }
}

function Get-GodotToolchainInstallPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$CacheRoot,
        [Parameter(Mandatory)][string]$ArchiveSha256
    )

    $normalizedHash = $ArchiveSha256.ToLowerInvariant()
    if ($normalizedHash -notmatch '^[0-9a-f]{64}$') {
        throw 'Archive SHA-256 must contain exactly 64 hexadecimal characters.'
    }

    return Join-Path $CacheRoot "content\sha256-$normalizedHash"
}

function Assert-GodotToolchainTreeHasNoReparsePoints {
    param([Parameter(Mandatory)][string]$RootPath)

    $root = Get-Item -LiteralPath $RootPath -Force
    if (($root.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Godot toolchain tree contains a reparse point at its root: $($root.FullName)"
    }

    foreach ($entry in Get-ChildItem -LiteralPath $root.FullName -Recurse -Force) {
        if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Godot toolchain tree contains a reparse point: $($entry.FullName)"
        }
    }
}

function Assert-GodotPathHasNoReparseComponents {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)

    $current = [IO.Path]::GetFullPath($Path)
    while (-not [string]::IsNullOrWhiteSpace($current)) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Godot cache path contains a reparse point: $($item.FullName)"
            }
        }

        $parent = [IO.Path]::GetDirectoryName($current)
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            break
        }
        $current = $parent
    }
}

function Open-VerifiedGodotToolchainLease {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)]$Manifest
    )

    if (-not (Test-Path -LiteralPath $RootPath -PathType Container)) {
        throw "Godot toolchain root does not exist: $RootPath"
    }

    $expected = Get-ManifestFileMap -Manifest $Manifest
    $root = [IO.Path]::GetFullPath($RootPath)
    Assert-GodotToolchainTreeHasNoReparsePoints -RootPath $root
    $actual = [Collections.Generic.Dictionary[string, IO.FileInfo]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File -Force) {
        $relative = [IO.Path]::GetRelativePath($root, $file.FullName).Replace('\', '/')
        if (-not $actual.TryAdd($relative, $file)) {
            throw "Godot toolchain tree contains duplicate path '$relative'."
        }
    }

    if ($actual.Count -ne $expected.Count) {
        throw "Godot toolchain tree file count mismatch: expected $($expected.Count), observed $($actual.Count)."
    }

    $handles = [Collections.Generic.List[IO.FileStream]]::new()
    try {
        foreach ($pair in ($expected.GetEnumerator() | Sort-Object Key)) {
            $actualFile = $null
            if (-not $actual.TryGetValue($pair.Key, [ref]$actualFile)) {
                throw "Godot toolchain tree is missing '$($pair.Key)'."
            }

            $handle = [IO.File]::Open(
                $actualFile.FullName,
                [IO.FileMode]::Open,
                [IO.FileAccess]::Read,
                [IO.FileShare]::Read)
            $null = $handles.Add($handle)

            $expectedLength = [long]$pair.Value.length
            if ($handle.Length -ne $expectedLength) {
                throw "Godot toolchain length mismatch for '$($pair.Key)': expected $expectedLength, observed $($handle.Length)."
            }

            $sha256 = [Security.Cryptography.SHA256]::Create()
            try {
                $actualHash = [Convert]::ToHexString($sha256.ComputeHash($handle)).ToLowerInvariant()
            }
            finally {
                $sha256.Dispose()
            }
            $handle.Position = 0

            $expectedHash = ([string]$pair.Value.sha256).ToLowerInvariant()
            if ($actualHash -ne $expectedHash) {
                throw "Godot toolchain hash mismatch for '$($pair.Key)': expected $expectedHash, observed $actualHash."
            }
        }

        Assert-GodotToolchainTreeHasNoReparsePoints -RootPath $root
        $finalPaths = @(Get-ChildItem -LiteralPath $root -Recurse -File -Force |
            ForEach-Object { [IO.Path]::GetRelativePath($root, $_.FullName).Replace('\', '/') })
        if ($finalPaths.Count -ne $expected.Count -or
            @($finalPaths | Where-Object { -not $expected.ContainsKey($_) }).Count -ne 0) {
            throw 'Godot toolchain tree changed while its verified lease was being acquired.'
        }

        $ownedHandles = $handles.ToArray()
        $lease = [pscustomobject]@{
            Valid = $true
            FileCount = $ownedHandles.Count
            RootPath = $root
        }
        $dispose = {
            foreach ($ownedHandle in $ownedHandles) {
                $ownedHandle.Dispose()
            }
            $ownedHandles = @()
        }.GetNewClosure()
        $lease | Add-Member -MemberType ScriptMethod -Name Dispose -Value $dispose
        return $lease
    }
    catch {
        foreach ($handle in $handles) {
            $handle.Dispose()
        }
        throw
    }
}

function Test-GodotToolchainTree {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)]$Manifest
    )

    $lease = Open-VerifiedGodotToolchainLease -RootPath $RootPath -Manifest $Manifest
    try {
        return [pscustomobject]@{
            Valid = $true
            FileCount = $lease.FileCount
            RootPath = $lease.RootPath
        }
    }
    finally {
        $lease.Dispose()
    }
}

function Expand-SafeGodotArchive {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ArchivePath,
        [Parameter(Mandatory)][string]$DestinationPath,
        [Parameter(Mandatory)]$Manifest
    )

    if (Test-Path -LiteralPath $DestinationPath) {
        throw "Extraction destination already exists: $DestinationPath"
    }

    $expected = Get-ManifestFileMap -Manifest $Manifest
    $rootDirectory = ([string]$Manifest.rootDirectory).TrimEnd('/')
    if ([string]::IsNullOrWhiteSpace($rootDirectory) -or
        $rootDirectory.Contains('/') -or
        $rootDirectory.Contains('\') -or
        $rootDirectory.Contains(':') -or
        $rootDirectory -in @('.', '..')) {
        throw "Pinned manifest contains unsafe root directory '$rootDirectory'."
    }

    $stream = [IO.File]::Open($ArchivePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        $archive = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Read, $false)
        try {
            $archiveFiles = [Collections.Generic.Dictionary[string, IO.Compression.ZipArchiveEntry]]::new([StringComparer]::OrdinalIgnoreCase)
            foreach ($entry in $archive.Entries) {
                $path = $entry.FullName
                $segments = @($path.Split('/'))
                if ([string]::IsNullOrWhiteSpace($path) -or
                    $path.Contains('\') -or
                    $path.StartsWith('/', [StringComparison]::Ordinal) -or
                    $path.Contains(':') -or
                    $segments -contains '..' -or
                    $segments -contains '.') {
                    throw "Godot archive contains unsafe archive path '$path'."
                }

                $unixType = (($entry.ExternalAttributes -shr 16) -band 0xF000)
                if ($unixType -eq 0xA000) {
                    throw "Godot archive contains symbolic link entry '$path'."
                }

                $prefix = "$rootDirectory/"
                if (-not $path.StartsWith($prefix, [StringComparison]::Ordinal)) {
                    if ($path -eq "$rootDirectory/") {
                        continue
                    }

                    throw "Godot archive entry '$path' is outside the pinned root '$rootDirectory'."
                }

                $relative = $path.Substring($prefix.Length)
                if ([string]::IsNullOrEmpty($entry.Name)) {
                    continue
                }

                if (-not $archiveFiles.TryAdd($relative, $entry)) {
                    throw "Godot archive contains duplicate archive path '$relative'."
                }
            }

            if ($archiveFiles.Count -ne $expected.Count) {
                throw "Godot archive does not match the pinned manifest: expected $($expected.Count) files, observed $($archiveFiles.Count)."
            }

            foreach ($pair in $expected.GetEnumerator()) {
                $entry = $null
                if (-not $archiveFiles.TryGetValue($pair.Key, [ref]$entry)) {
                    throw "Godot archive does not match the pinned manifest: missing '$($pair.Key)'."
                }

                if ($entry.Length -ne [long]$pair.Value.length) {
                    throw "Godot archive does not match the pinned manifest: length mismatch for '$($pair.Key)'."
                }
            }

            $destinationRoot = [IO.Path]::GetFullPath($DestinationPath)
            New-Item -ItemType Directory -Path $destinationRoot | Out-Null
            foreach ($pair in $archiveFiles.GetEnumerator()) {
                $relativeOsPath = $pair.Key.Replace('/', [IO.Path]::DirectorySeparatorChar)
                $outputPath = [IO.Path]::GetFullPath((Join-Path $destinationRoot $relativeOsPath))
                $requiredPrefix = $destinationRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
                if (-not $outputPath.StartsWith($requiredPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                    throw "Godot archive contains unsafe archive path '$($pair.Key)'."
                }

                $parent = Split-Path -Parent $outputPath
                if (-not (Test-Path -LiteralPath $parent)) {
                    New-Item -ItemType Directory -Path $parent | Out-Null
                }

                $input = $pair.Value.Open()
                try {
                    $output = [IO.File]::Open($outputPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                    try {
                        $input.CopyTo($output)
                    }
                    finally {
                        $output.Dispose()
                    }
                }
                finally {
                    $input.Dispose()
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

    Test-GodotToolchainTree -RootPath $DestinationPath -Manifest $Manifest
}

Export-ModuleMember -Function @(
    'Assert-GodotPathHasNoReparseComponents',
    'Assert-GodotToolchainTreeHasNoReparsePoints',
    'Assert-PinnedGodotManifest',
    'Expand-SafeGodotArchive',
    'Get-GodotToolchainInstallPath',
    'Open-VerifiedGodotToolchainLease',
    'Save-PinnedHttpsFile',
    'Test-GodotArchiveFile',
    'Test-GodotToolchainTree'
)
