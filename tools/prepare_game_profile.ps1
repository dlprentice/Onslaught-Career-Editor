param(
    [Parameter(Mandatory = $true)]
    [string]$SourceGameRoot,
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,
    [string]$ProfileName = "bea-safe-profile",
    [string]$ExecutableOverridePath = "",
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"

function Resolve-RequiredDirectory([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        Write-Error ("{0} '{1}' does not exist." -f $Label, $Path)
        exit 1
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Resolve-RequiredFile([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Write-Error ("{0} '{1}' does not exist." -f $Label, $Path)
        exit 1
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Assert-SafeName([string]$Name) {
    if ($Name -notmatch '^[A-Za-z0-9._-]{1,64}$') {
        Write-Error "ProfileName may contain only letters, numbers, dot, underscore, and dash."
        exit 1
    }
}

function Normalize-ForPrefix([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
}

function Test-SameOrUnderRoot([string]$Path, [string]$Root) {
    $normalizedPath = Normalize-ForPrefix $Path
    $normalizedRoot = Normalize-ForPrefix $Root
    return $normalizedPath.TrimEnd([System.IO.Path]::DirectorySeparatorChar) -ieq $normalizedRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) -or
        $normalizedPath.StartsWith($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)
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

function Assert-SafeOutputRoot([string]$SourceRoot, [string]$OutputRoot) {
    if (Test-SameOrUnderRoot $OutputRoot $SourceRoot) {
        Write-Error "OutputRoot must not be inside the source game root."
        exit 1
    }

    if (Test-SameOrUnderRoot $SourceRoot $OutputRoot) {
        Write-Error "SourceGameRoot must not be inside OutputRoot."
        exit 1
    }

    if (Test-ProtectedInstallRoot $OutputRoot) {
        Write-Error "OutputRoot must not be under Program Files or another protected install root."
        exit 1
    }

    if (Test-KnownSteamInstallShape $OutputRoot) {
        Write-Error "OutputRoot must not be under a steamapps/common/Battle Engine Aquila install root."
        exit 1
    }
}

function Assert-ExecutableOverridePath([string]$SourceRoot, [string]$ExecutablePath) {
    if (-not (Test-SameOrUnderRoot $ExecutablePath $SourceRoot)) {
        Write-Error "ExecutableOverridePath must be inside SourceGameRoot."
        exit 1
    }

    $fileName = [System.IO.Path]::GetFileName($ExecutablePath)
    if ($fileName -ine "BEA.exe" -and $fileName -ine "BEA.exe.original.backup") {
        Write-Error "ExecutableOverridePath must point to BEA.exe or BEA.exe.original.backup."
        exit 1
    }

    $item = Get-Item -LiteralPath $ExecutablePath
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Error "ExecutableOverridePath must not be a reparse point."
        exit 1
    }
}

$sourceRoot = Resolve-RequiredDirectory $SourceGameRoot "Source game root"
Assert-SafeName $ProfileName
$executableSource = $null
if ($ExecutableOverridePath) {
    $executableSource = Resolve-RequiredFile $ExecutableOverridePath "Executable override"
    Assert-ExecutableOverridePath $sourceRoot $executableSource
}

$requiredEntries = @("data", "defaultoptions.bea", "binkw32.dll", "ogg.dll", "vorbis.dll", "zlib.dll")
if (-not $executableSource) {
    $requiredEntries = @("BEA.exe") + $requiredEntries
}
foreach ($entry in $requiredEntries) {
    $candidate = Join-Path $sourceRoot $entry
    if (-not (Test-Path -LiteralPath $candidate)) {
        Write-Error ("Required game entry '{0}' is missing under '{1}'." -f $entry, $sourceRoot)
        exit 1
    }
}

if (Test-Path -LiteralPath $OutputRoot -PathType Leaf) {
    Write-Error ("OutputRoot '{0}' is a file, not a directory." -f $OutputRoot)
    exit 1
} elseif (Test-Path -LiteralPath $OutputRoot -PathType Container) {
    $resolvedOutputRoot = (Resolve-Path -LiteralPath $OutputRoot).Path
} else {
    $resolvedOutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
}

Assert-SafeOutputRoot $sourceRoot $resolvedOutputRoot

if ((-not $PrintOnly) -and (-not (Test-Path -LiteralPath $resolvedOutputRoot -PathType Container))) {
    New-Item -ItemType Directory -Path $resolvedOutputRoot | Out-Null
    $resolvedOutputRoot = (Resolve-Path -LiteralPath $resolvedOutputRoot).Path
}

$targetRoot = Join-Path $resolvedOutputRoot $ProfileName
if ((Test-Path -LiteralPath $targetRoot) -and -not $PrintOnly) {
    Write-Error ("Target profile '{0}' already exists; refusing to overwrite." -f $targetRoot)
    exit 1
}

$entries = @(
    "BEA.exe",
    "data",
    "defaultoptions.bea",
    "savegames",
    "binkw32.dll",
    "ogg.dll",
    "vorbis.dll",
    "zlib.dll",
    "steam_appid.txt"
)

$plan = [PSCustomObject]@{
    schemaVersion = "game-profile-prepare.v1"
    generatedAt = (Get-Date).ToString("o")
    mutation = $false
    sourceGameRoot = $sourceRoot
    outputRoot = $resolvedOutputRoot
    targetGameRoot = $targetRoot
    profileName = $ProfileName
    executableOverride = [bool]$executableSource
    entries = @()
    note = "Copies a validated local game profile. Existing targets are never overwritten."
}

foreach ($entry in $entries) {
    if (($entry -eq "BEA.exe") -and $executableSource) {
        $sourcePath = $executableSource
    } else {
        $sourcePath = Join-Path $sourceRoot $entry
    }
    if (Test-Path -LiteralPath $sourcePath) {
        $plan.entries += [PSCustomObject]@{
            name = $entry
            source = $sourcePath
            target = (Join-Path $targetRoot $entry)
        }
    }
}

if ($PrintOnly) {
    $plan | ConvertTo-Json -Depth 6
    exit 0
}

New-Item -ItemType Directory -Path $targetRoot | Out-Null
foreach ($entry in $plan.entries) {
    Copy-Item -LiteralPath $entry.source -Destination $entry.target -Recurse
}

$plan.mutation = $true
$plan | ConvertTo-Json -Depth 6
