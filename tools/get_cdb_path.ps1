param(
    [switch]$AsLiteral
)

$ErrorActionPreference = "Stop"

function Get-CandidatePaths {
    $paths = [System.Collections.Generic.List[string]]::new()

    $command = Get-Command cdb -ErrorAction SilentlyContinue
    if ($command -and $command.Source) {
        $paths.Add($command.Source)
    }

    $windowsKitCandidates = @(
        "C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\cdb.exe",
        "C:\Program Files\Windows Kits\10\Debuggers\x86\cdb.exe",
        "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe",
        "C:\Program Files\Windows Kits\10\Debuggers\x64\cdb.exe"
    )

    foreach ($candidate in $windowsKitCandidates) {
        $paths.Add($candidate)
    }

    $windbgPackages = Get-AppxPackage Microsoft.WinDbg -ErrorAction SilentlyContinue
    foreach ($package in $windbgPackages) {
        if (-not $package.InstallLocation) {
            continue
        }

        $paths.Add((Join-Path $package.InstallLocation "x86\cdb.exe"))
        $paths.Add((Join-Path $package.InstallLocation "amd64\cdb.exe"))
    }

    return $paths
}

foreach ($candidate in (Get-CandidatePaths | Select-Object -Unique)) {
    if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
        if ($AsLiteral) {
            Write-Output $candidate
        } else {
            Write-Output ('"{0}"' -f $candidate)
        }

        exit 0
    }
}

Write-Error "Unable to locate cdb.exe via PATH, Windows Kits, or the Microsoft.WinDbg app package."
exit 1
