[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$ReferenceRoot = (Join-Path $PSScriptRoot '..\references\Onslaught'),
    [string]$OutputRoot = (Join-Path $PSScriptRoot '..\build\bsim-stuart-pilot'),
    [string]$VisualStudioInstallation = '',
    [string]$VCToolsVersion = '14.44.35207'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$expectedCommit = '5352a81cdb838b145a57f7febc5d9fc4b0129ebb'
$expectedTree = '7a8d0a83257ff7a2e9831455eca576ade11decbd'
$expectedPatchedSptrSet = '3956987023DE376A7DD6F3CE329F79D6E9AF21316711004CAD65A22D6818D695'
$sourceHashes = [ordered]@{
    'activereader.cpp' = 'B47E66767D767CFA934E95E54A5E0DA2A9891C47652D491CE4944D0BC4E2A944'
    'activereader.h' = '26FA65DA89D5DDA48080EB26DBBB2FAD59C0E5C831B0B5B8B403E4BBDA544C1F'
    'event.cpp' = '55A7AB3EEC78B3A634EFD3BD80EFFBED44C648EF04FFE06298F3FFA26A53B4E5'
    'event.h' = '411B3AC014B66A455CAE8D47186F660253553AA798802368D84DB42F43744232'
    'scheduledevent.cpp' = '510107937400260DE4BB233483DA6B01A6DD5DA4B1584BD3C2E8F32118AD447E'
    'scheduledevent.h' = '1F568C7E1B71A4FBBF98E59A3C3EE55A71D60C0AA4313E1620426F3E52D0E4B1'
    'SPtrSet.cpp' = '49D40AA009DAB4D0747560D30BE27814FE6BC18A59B301860FA18A59A7644623'
    'SPtrSet.h' = '2AB86140CD8DF5AD035B297BBBAB737E0C75FC5D88245873C8972B462E47D029'
}

$reference = [System.IO.Path]::GetFullPath($ReferenceRoot)
$output = [System.IO.Path]::GetFullPath($OutputRoot)
if (-not (Test-Path -LiteralPath $reference -PathType Container)) {
    throw "Pinned Stuart reference tree was not found: $reference"
}
$referencePrefix = $reference.TrimEnd('\') + '\'
if ($output.StartsWith($referencePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'BSim build output must not be inside the Stuart reference tree.'
}

$git = (Get-Command git -ErrorAction Stop).Source
$actualCommit = (& $git -C $reference rev-parse HEAD).Trim()
$actualTree = (& $git -C $reference rev-parse 'HEAD^{tree}').Trim()
if ($LASTEXITCODE -ne 0 -or
    $actualCommit -cne $expectedCommit -or
    $actualTree -cne $expectedTree) {
    throw "Stuart source pin mismatch: commit=$actualCommit tree=$actualTree"
}

if ([string]::IsNullOrWhiteSpace($VisualStudioInstallation)) {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
        throw "vswhere.exe was not found: $vswhere"
    }
    $VisualStudioInstallation = (
        & $vswhere -all -prerelease -latest -property installationPath |
            Select-Object -First 1
    ).Trim()
}
$visualStudio = [System.IO.Path]::GetFullPath($VisualStudioInstallation)
$devCmd = Join-Path $visualStudio 'Common7\Tools\VsDevCmd.bat'
$compiler = Join-Path $visualStudio "VC\Tools\MSVC\$VCToolsVersion\bin\Hostx64\x86\cl.exe"
if (-not (Test-Path -LiteralPath $devCmd -PathType Leaf) -or
    -not (Test-Path -LiteralPath $compiler -PathType Leaf)) {
    throw "Pinned Visual C++ environment was not found under $visualStudio"
}

# Import only the process-local developer environment needed by cl.exe.
$environmentLines = & $env:ComSpec /d /s /c "`"$devCmd`" -no_logo -arch=x86 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) {
    throw 'VsDevCmd.bat failed.'
}
foreach ($line in $environmentLines) {
    $separator = $line.IndexOf('=')
    if ($separator -gt 0) {
        [Environment]::SetEnvironmentVariable(
            $line.Substring(0, $separator),
            $line.Substring($separator + 1),
            [EnvironmentVariableTarget]::Process
        )
    }
}

$sourceRoot = Join-Path $output 'src'
$compatRoot = Join-Path $output 'compat'
$objectRoot = Join-Path $output 'objects'
foreach ($directory in @($output, $sourceRoot, $compatRoot, $objectRoot)) {
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
}

$sourceReceipt = @()
foreach ($entry in $sourceHashes.GetEnumerator()) {
    $sourcePath = Join-Path $reference $entry.Key
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Stuart pilot source is missing: $sourcePath"
    }
    $sourceHash = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    if ($sourceHash -cne $entry.Value) {
        throw "Stuart source hash mismatch for $($entry.Key): $sourceHash"
    }
    $copiedPath = Join-Path $sourceRoot $entry.Key
    [System.IO.File]::Copy($sourcePath, $copiedPath, $true)
    $sourceReceipt += [ordered]@{
        name = $entry.Key
        sourcePath = $sourcePath
        sourceSha256 = $sourceHash
        copiedPath = $copiedPath
    }
}

$sptrSetPath = Join-Path $sourceRoot 'SPtrSet.cpp'
$sptrSetText = [System.IO.File]::ReadAllText($sptrSetPath)
$legacyPattern = 'static count = 0 ;'
$legacyCount = ([regex]::Matches(
        $sptrSetText,
        [regex]::Escape($legacyPattern)
    )).Count
if ($legacyCount -ne 2) {
    throw "Expected exactly two legacy implicit-int repairs; found $legacyCount"
}
$sptrSetText = $sptrSetText.Replace($legacyPattern, 'static int count = 0 ;')
[System.IO.File]::WriteAllText(
    $sptrSetPath,
    $sptrSetText,
    [System.Text.UTF8Encoding]::new($false)
)
$patchedHash = (Get-FileHash -LiteralPath $sptrSetPath -Algorithm SHA256).Hash
if ($patchedHash -cne $expectedPatchedSptrSet) {
    throw "Patched SPtrSet.cpp hash mismatch: $patchedHash"
}

$trackedCompatRoot = Join-Path $PSScriptRoot 'bsim-stuart\compat'
$compatReceipt = @()
foreach ($compatName in @('common.h', 'debuglog.h', 'Monitor.h', 'profile.h', 'stdafx.h')) {
    $compatSource = Join-Path $trackedCompatRoot $compatName
    $compatTarget = Join-Path $compatRoot $compatName
    if (-not (Test-Path -LiteralPath $compatSource -PathType Leaf)) {
        throw "Tracked compatibility declaration is missing: $compatSource"
    }
    [System.IO.File]::Copy($compatSource, $compatTarget, $true)
    $compatReceipt += [ordered]@{
        name = $compatName
        sourcePath = $compatSource
        sha256 = (Get-FileHash -LiteralPath $compatSource -Algorithm SHA256).Hash
    }
}

$commonFlags = @(
    '/nologo',
    '/c',
    '/TP',
    '/O2',
    '/GS-',
    '/GR',
    '/EHsc',
    '/arch:IA32',
    '/fp:precise',
    '/Gy',
    '/Brepro',
    '/DPC=1',
    '/DTARGET=PC',
    '/D_DIRECTX=1',
    "/I$compatRoot",
    "/I$sourceRoot"
)
$profiles = @(
    [ordered]@{ name = 'ob1'; inline = '/Ob1' },
    [ordered]@{ name = 'ob2'; inline = '/Ob2' }
)
$translationUnits = @(
    'activereader.cpp',
    'event.cpp',
    'scheduledevent.cpp',
    'SPtrSet.cpp'
)

function Invoke-PilotCompile {
    $result = @()
    foreach ($profile in $profiles) {
        $profileRoot = Join-Path $objectRoot $profile.name
        [System.IO.Directory]::CreateDirectory($profileRoot) | Out-Null
        foreach ($sourceName in $translationUnits) {
            $sourcePath = Join-Path $sourceRoot $sourceName
            $objectName = [IO.Path]::GetFileNameWithoutExtension($sourceName) + '.obj'
            $objectPath = Join-Path $profileRoot $objectName
            $compilerMessages = & $compiler @commonFlags $profile.inline "/Fo$objectPath" $sourcePath 2>&1
            if ($LASTEXITCODE -ne 0) {
                $compilerMessages | ForEach-Object { Write-Host $_ }
                throw "Compiler failed for $sourceName / $($profile.name)"
            }
            $compilerMessages | ForEach-Object { Write-Verbose $_ }
            $result += [ordered]@{
                profile = $profile.name
                source = $sourceName
                path = $objectPath
                bytes = (Get-Item -LiteralPath $objectPath).Length
                sha256 = (Get-FileHash -LiteralPath $objectPath -Algorithm SHA256).Hash
                md5 = (Get-FileHash -LiteralPath $objectPath -Algorithm MD5).Hash
            }
        }
    }
    return $result
}

$firstBuild = @(Invoke-PilotCompile)
$secondBuild = @(Invoke-PilotCompile)
if ($firstBuild.Count -ne 8 -or $secondBuild.Count -ne 8) {
    throw 'The Stuart pilot did not emit all eight expected COFF objects.'
}
for ($index = 0; $index -lt $firstBuild.Count; $index++) {
    if ($firstBuild[$index].sha256 -cne $secondBuild[$index].sha256) {
        throw "Same-path /Brepro mismatch: $($firstBuild[$index].path)"
    }
}

$compilerItem = Get-Item -LiteralPath $compiler
$receipt = [ordered]@{
    schemaVersion = 'bea-stuart-bsim-pilot-build.v1'
    generatedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    source = [ordered]@{
        root = $reference
        commit = $actualCommit
        tree = $actualTree
        files = $sourceReceipt
    }
    copiedSourceRepairs = @(
        [ordered]@{
            file = 'SPtrSet.cpp'
            original = 'static count = 0 ;'
            replacement = 'static int count = 0 ;'
            occurrences = 2
            patchedSha256 = $patchedHash
        }
    )
    compatibilityDeclarations = $compatReceipt
    compiler = [ordered]@{
        path = $compiler
        fileVersion = $compilerItem.VersionInfo.FileVersion
        sha256 = (Get-FileHash -LiteralPath $compiler -Algorithm SHA256).Hash
        vcToolsVersion = $VCToolsVersion
    }
    flags = $commonFlags
    profiles = $profiles
    objects = $secondBuild
    reproducibility = [ordered]@{
        sameFixedPathBuilds = 2
        byteIdenticalObjects = 8
        passed = $true
        note = 'COFF hashes are fixed-output-path identities, not path-independent identities.'
    }
    evidenceBoundary = @(
        'Compatibility files contain declarations only; unresolved services remain COFF externals.',
        'Objects are BSim candidate-generation inputs, not a retail-compatible executable.',
        'No source file under references/Onslaught is modified.'
    )
}
$receiptPath = Join-Path $output 'build-receipt.json'
[System.IO.File]::WriteAllText(
    $receiptPath,
    ($receipt | ConvertTo-Json -Depth 20) + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)
$receipt
