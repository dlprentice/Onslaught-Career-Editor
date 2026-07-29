[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\build\ttd-exec-coverage'),
    [string]$RuntimeDirectory = '',
    [string]$WindowsSdkVersion = '10.0.26100.0',
    [string]$VCToolsVersion = '14.44.35207',
    [string]$ExpectedRuntimeVersion = '1.11.584.0',
    [string]$ExpectedReplaySha256 = 'B705235016778648F2C194AA76B54669C19AE318D16D340019F8A6F6C86FABBC',
    [string]$ExpectedReplayCpuSha256 = 'B2A9A06A3C292EF58DF31DF70AB35A9440DCEB3EE36DE9C2B08FF4507DD8EF93'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$apiVersion = '0.9.5'
$apiArchiveSha256 = 'C906B99C02926CE089E1ED1BD54F1A0ABF83458DDCE4CF9BBC62403D7AA240BD'
$apiUrl = "https://www.nuget.org/api/v2/package/Microsoft.TimeTravelDebugging.Apis/$apiVersion"
$out = [System.IO.Path]::GetFullPath($OutputDirectory)
$packagesRoot = Join-Path $out 'packages'
$packageDirectory = Join-Path $packagesRoot "Microsoft.TimeTravelDebugging.Apis.$apiVersion"
$packageProps = Join-Path $packageDirectory 'build\native\Microsoft.TimeTravelDebugging.Apis.props'
$packageArchive = Join-Path $packagesRoot "Microsoft.TimeTravelDebugging.Apis.$apiVersion.nupkg"
$binaryDirectory = Join-Path $out 'bin'
$buildNonce = [Guid]::NewGuid().ToString('N')
$reproRoots = @(
    Join-Path $out "repro-$buildNonce-a"
    Join-Path $out "repro-$buildNonce-b"
)
[System.IO.Directory]::CreateDirectory($packagesRoot) | Out-Null
[System.IO.Directory]::CreateDirectory($binaryDirectory) | Out-Null

if (Test-Path -LiteralPath $packageArchive -PathType Leaf) {
    $archiveHash = (Get-FileHash -LiteralPath $packageArchive -Algorithm SHA256).Hash
    if ($archiveHash -cne $apiArchiveSha256) {
        throw "Cached API package hash mismatch: $archiveHash"
    }
} else {
    $downloadPath = "$packageArchive.download-$PID-$buildNonce"
    if (Test-Path -LiteralPath $downloadPath) {
        throw "Temporary package download already exists: $downloadPath"
    }
    Invoke-WebRequest -Uri $apiUrl -OutFile $downloadPath -UseBasicParsing
    $downloadHash = (Get-FileHash -LiteralPath $downloadPath -Algorithm SHA256).Hash
    if ($downloadHash -cne $apiArchiveSha256) {
        [System.IO.File]::Delete($downloadPath)
        throw "Downloaded API package hash mismatch: $downloadHash"
    }
    [System.IO.File]::Move($downloadPath, $packageArchive)
}

if (-not (Test-Path -LiteralPath $packageProps -PathType Leaf)) {
    if (Test-Path -LiteralPath $packageDirectory) {
        throw "Incomplete package directory already exists: $packageDirectory"
    }
    $extractDirectory = "$packageDirectory.extracting-$PID-$buildNonce"
    if (Test-Path -LiteralPath $extractDirectory) {
        throw "Temporary extraction directory already exists: $extractDirectory"
    }
    [System.IO.Compression.ZipFile]::ExtractToDirectory(
        $packageArchive,
        $extractDirectory
    )
    $extractedProps = Join-Path $extractDirectory 'build\native\Microsoft.TimeTravelDebugging.Apis.props'
    if (-not (Test-Path -LiteralPath $extractedProps -PathType Leaf)) {
        throw "API package did not contain the expected native props file"
    }
    [System.IO.Directory]::Move($extractDirectory, $packageDirectory)
}

# The archive hash alone does not prove that a previously extracted package is
# still intact.  Rehash every extracted file against the pinned NuGet archive.
$archive = [System.IO.Compression.ZipFile]::OpenRead($packageArchive)
try {
    $expectedFiles = [Collections.Generic.HashSet[string]]::new(
        [StringComparer]::OrdinalIgnoreCase
    )
    foreach ($entry in $archive.Entries) {
        if ([string]::IsNullOrEmpty($entry.Name)) {
            continue
        }
        $relative = $entry.FullName.Replace('/', [IO.Path]::DirectorySeparatorChar)
        $null = $expectedFiles.Add($relative)
        $candidate = [IO.Path]::GetFullPath((Join-Path $packageDirectory $relative))
        if (-not $candidate.StartsWith(
                ([IO.Path]::GetFullPath($packageDirectory).TrimEnd('\') + '\'),
                [StringComparison]::OrdinalIgnoreCase
            )) {
            throw "Package entry escapes extraction root: $relative"
        }
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "Extracted API package is missing: $relative"
        }
        if ((Get-Item -LiteralPath $candidate).Length -ne $entry.Length) {
            throw "Extracted API package length mismatch: $relative"
        }
        $entryStream = $entry.Open()
        $sha = [Security.Cryptography.SHA256]::Create()
        try {
            $entryHash = [Convert]::ToHexString($sha.ComputeHash($entryStream))
        } finally {
            $sha.Dispose()
            $entryStream.Dispose()
        }
        $fileHash = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
        if ($fileHash -cne $entryHash) {
            throw "Extracted API package hash mismatch: $relative"
        }
    }
    foreach ($file in Get-ChildItem -LiteralPath $packageDirectory -Recurse -File) {
        $relative = [IO.Path]::GetRelativePath($packageDirectory, $file.FullName)
        if (-not $expectedFiles.Contains($relative)) {
            throw "Extracted API package contains an unexpected file: $relative"
        }
    }
} finally {
    $archive.Dispose()
}

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
    throw "vswhere.exe was not found at $vswhere"
}
$installation = (& $vswhere -all -prerelease -latest -property installationPath |
    Select-Object -First 1).Trim()
if (-not $installation) {
    throw 'No complete Visual Studio installation was found.'
}
$msbuild = Join-Path $installation 'MSBuild\Current\Bin\MSBuild.exe'
if (-not (Test-Path -LiteralPath $msbuild -PathType Leaf)) {
    throw "MSBuild.exe was not found at $msbuild"
}

$project = Join-Path $PSScriptRoot 'ttd-exec-coverage\ttd_exec_coverage.vcxproj'
function Invoke-IsolatedBuild {
    param([Parameter(Mandatory = $true)][string]$Root)

    $laneBin = Join-Path $Root 'bin'
    $laneObj = Join-Path $Root 'obj'
    [IO.Directory]::CreateDirectory($laneBin) | Out-Null
    [IO.Directory]::CreateDirectory($laneObj) | Out-Null
    $outProperty = $laneBin.TrimEnd('\') + '\'
    $objProperty = $laneObj.TrimEnd('\') + '\'
    $buildOutput = & $msbuild $project `
        /m `
        /t:Rebuild `
        /p:Configuration=Release `
        /p:Platform=x64 `
        "/p:TTDPackageDirectory=$packageDirectory" `
        "/p:OutDir=$outProperty" `
        "/p:IntDir=$objProperty" `
        "/p:WindowsTargetPlatformVersion=$WindowsSdkVersion" `
        "/p:VCToolsVersion=$VCToolsVersion" `
        /v:minimal
    $buildOutput | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        throw "x64 TTD coverage build failed with exit code $LASTEXITCODE"
    }
    $laneCollector = Join-Path $laneBin 'ttd_exec_coverage.exe'
    if (-not (Test-Path -LiteralPath $laneCollector -PathType Leaf)) {
        throw "Build reported success but did not create $laneCollector"
    }
    return [ordered]@{
        root = $Root
        bin = $laneBin
        obj = $laneObj
        collector = $laneCollector
        bytes = (Get-Item -LiteralPath $laneCollector).Length
        sha256 = (Get-FileHash -LiteralPath $laneCollector -Algorithm SHA256).Hash
    }
}

$isolatedBuilds = @(
    Invoke-IsolatedBuild -Root $reproRoots[0]
    Invoke-IsolatedBuild -Root $reproRoots[1]
)
if ($isolatedBuilds[0].bytes -ne $isolatedBuilds[1].bytes -or
    $isolatedBuilds[0].sha256 -cne $isolatedBuilds[1].sha256) {
    throw 'Disjoint /Brepro collector builds are not byte-identical.'
}

if ([string]::IsNullOrWhiteSpace($RuntimeDirectory)) {
    $windowsApps = Join-Path $env:ProgramFiles 'WindowsApps'
    $runtimeCandidates = @(
        Get-ChildItem -LiteralPath $windowsApps -Directory -Filter 'Microsoft.WinDbg_*' -ErrorAction SilentlyContinue |
            Sort-Object -Property LastWriteTimeUtc -Descending |
            ForEach-Object { Join-Path $_.FullName 'amd64\ttd' } |
            Where-Object {
                (Test-Path -LiteralPath (Join-Path $_ 'TTDReplay.dll') -PathType Leaf) -and
                (Test-Path -LiteralPath (Join-Path $_ 'TTDReplayCPU.dll') -PathType Leaf)
            }
    )
    if ($runtimeCandidates.Count -eq 0) {
        throw 'No x64 WinDbg TTD Replay runtime was found. Pass -RuntimeDirectory.'
    }
    $RuntimeDirectory = $runtimeCandidates[0]
}
$runtime = [System.IO.Path]::GetFullPath($RuntimeDirectory)
$replaySource = Join-Path $runtime 'TTDReplay.dll'
$replayCpuSource = Join-Path $runtime 'TTDReplayCPU.dll'
foreach ($runtimeFile in @($replaySource, $replayCpuSource)) {
    if (-not (Test-Path -LiteralPath $runtimeFile -PathType Leaf)) {
        throw "Missing TTD Replay runtime file: $runtimeFile"
    }
}

$replayItem = Get-Item -LiteralPath $replaySource
$replayCpuItem = Get-Item -LiteralPath $replayCpuSource
if ($replayItem.VersionInfo.FileVersion -cne $ExpectedRuntimeVersion -or
    $replayCpuItem.VersionInfo.FileVersion -cne $ExpectedRuntimeVersion) {
    throw "TTD Replay runtime version mismatch; expected $ExpectedRuntimeVersion"
}
$replayHash = (Get-FileHash -LiteralPath $replaySource -Algorithm SHA256).Hash
$replayCpuHash = (Get-FileHash -LiteralPath $replayCpuSource -Algorithm SHA256).Hash
if ($replayHash -cne $ExpectedReplaySha256.ToUpperInvariant()) {
    throw "TTDReplay.dll hash mismatch: $replayHash"
}
if ($replayCpuHash -cne $ExpectedReplayCpuSha256.ToUpperInvariant()) {
    throw "TTDReplayCPU.dll hash mismatch: $replayCpuHash"
}

foreach ($build in $isolatedBuilds) {
    Copy-Item -LiteralPath $replaySource `
        -Destination (Join-Path $build.bin 'TTDReplay.dll') -Force
    Copy-Item -LiteralPath $replayCpuSource `
        -Destination (Join-Path $build.bin 'TTDReplayCPU.dll') -Force
    & $build.collector --self-test
    if ($LASTEXITCODE -ne 0) {
        throw "Collector self-test failed for $($build.root) with exit code $LASTEXITCODE"
    }
    $build['selfTest'] = 'PASS'
}

$collector = Join-Path $binaryDirectory 'ttd_exec_coverage.exe'
Copy-Item -LiteralPath $isolatedBuilds[0].collector -Destination $collector -Force
$firstPdb = Join-Path $isolatedBuilds[0].bin 'ttd_exec_coverage.pdb'
if (Test-Path -LiteralPath $firstPdb -PathType Leaf) {
    Copy-Item -LiteralPath $firstPdb `
        -Destination (Join-Path $binaryDirectory 'ttd_exec_coverage.pdb') -Force
}
Copy-Item -LiteralPath $replaySource `
    -Destination (Join-Path $binaryDirectory 'TTDReplay.dll') -Force
Copy-Item -LiteralPath $replayCpuSource `
    -Destination (Join-Path $binaryDirectory 'TTDReplayCPU.dll') -Force
$collectorHash = (Get-FileHash -LiteralPath $collector -Algorithm SHA256).Hash
if ($collectorHash -cne $isolatedBuilds[0].sha256) {
    throw 'Published collector hash disagrees with the reproducible build pair.'
}

$source = Join-Path $PSScriptRoot 'ttd-exec-coverage\ttd_exec_coverage.cpp'
$compiler = Join-Path $installation "VC\Tools\MSVC\$VCToolsVersion\bin\Hostx64\x64\cl.exe"
if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) {
    throw "Pinned compiler was not found: $compiler"
}
$receipt = [ordered]@{
    schemaVersion = 'bea-ttd-exec-coverage-build.v2'
    generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    architecture = 'x64'
    visualStudio = $installation
    compiler = @{
        path = $compiler
        version = (Get-Item -LiteralPath $compiler).VersionInfo.FileVersion
        sha256 = (Get-FileHash -LiteralPath $compiler -Algorithm SHA256).Hash
        vcToolsVersion = $VCToolsVersion
        windowsSdkVersion = $WindowsSdkVersion
    }
    apiPackage = @{
        id = 'Microsoft.TimeTravelDebugging.Apis'
        version = $apiVersion
        archiveSha256 = $apiArchiveSha256
        observedArchiveSha256 = (
            Get-FileHash -LiteralPath $packageArchive -Algorithm SHA256
        ).Hash
        directory = $packageDirectory
        extractedFilesVerified = $expectedFiles.Count
    }
    runtime = @{
        version = $ExpectedRuntimeVersion
        directory = $runtime
        replaySha256 = $replayHash
        replayCpuSha256 = $replayCpuHash
    }
    inputs = @(
        @{
            path = (Resolve-Path -LiteralPath $source).Path
            sha256 = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
        },
        @{
            path = (Resolve-Path -LiteralPath $project).Path
            sha256 = (Get-FileHash -LiteralPath $project -Algorithm SHA256).Hash
        }
    )
    collector = @{
        path = (Resolve-Path -LiteralPath $collector).Path
        bytes = (Get-Item -LiteralPath $collector).Length
        sha256 = $collectorHash
    }
    reproducibility = @{
        isolatedBuilds = $isolatedBuilds
        buildCount = 2
        byteIdentical = $true
        distinctOutputRoots = (
            $isolatedBuilds[0].root -cne $isolatedBuilds[1].root
        )
        pdbAlternatePath = 'ttd_exec_coverage.pdb'
        allSelfTestsPassed = $true
    }
    selfTest = 'PASS_BOTH_ISOLATED_BUILDS'
}
$receiptPath = Join-Path $out 'build-receipt.json'
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8NoBOM
$receipt
