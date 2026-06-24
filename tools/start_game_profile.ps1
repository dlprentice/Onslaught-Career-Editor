param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,
    [string]$Arguments = "",
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"

$resolvedGameRoot = (Resolve-Path -LiteralPath $GameRoot).Path
$executablePath = Join-Path $resolvedGameRoot "BEA.exe"

if (-not (Test-Path -LiteralPath $executablePath -PathType Leaf)) {
    Write-Error ("BEA.exe was not found under '{0}'." -f $resolvedGameRoot)
    exit 1
}

$rawTokens = @()
if ($Arguments) {
    $rawTokens = @($Arguments -split '\s+' | Where-Object { $_ })
}

# Keep retail arguments allowlisted for diagnostics/probes only; windowed mode is
# owned by the patch catalog, and startup-movie skipping is useful for bounded
# runtime replay captures. Level selection is intentionally numeric-only so
# copied-profile runtime proofs can target a known mission without exposing the
# broader retail/debug command line. Controller configuration is bounded to the
# four retail control presets and remains launch-argument proof only.
$tokens = New-Object System.Collections.Generic.List[string]
for ($index = 0; $index -lt $rawTokens.Count; $index++) {
    $token = $rawTokens[$index]
    if (@("-forcewindowed", "-skipfmv") -contains $token) {
        $tokens.Add($token) | Out-Null
        continue
    }

    if ($token -eq "-level") {
        if (($index + 1) -ge $rawTokens.Count) {
            Write-Error "-level requires a numeric mission id."
            exit 1
        }

        $levelId = 0
        $levelToken = $rawTokens[$index + 1]
        if (-not [int]::TryParse($levelToken, [ref]$levelId) -or $levelId -lt 1 -or $levelId -gt 9999) {
            Write-Error "-level requires a numeric mission id between 1 and 9999."
            exit 1
        }

        $tokens.Add("-level") | Out-Null
        $tokens.Add($levelId.ToString([System.Globalization.CultureInfo]::InvariantCulture)) | Out-Null
        $index++
        continue
    }

    if ($token -eq "-configuration") {
        if (($index + 1) -ge $rawTokens.Count) {
            Write-Error "-configuration requires a controller configuration between 1 and 4."
            exit 1
        }

        $configurationId = 0
        $configurationToken = $rawTokens[$index + 1]
        if (-not [int]::TryParse($configurationToken, [ref]$configurationId) -or $configurationId -lt 1 -or $configurationId -gt 4) {
            Write-Error "-configuration requires a controller configuration between 1 and 4."
            exit 1
        }

        $tokens.Add("-configuration") | Out-Null
        $tokens.Add($configurationId.ToString([System.Globalization.CultureInfo]::InvariantCulture)) | Out-Null
        $index++
        continue
    }

    if ($token -match '^-') {
        Write-Error ("Unsupported launch argument '{0}'." -f $token)
        exit 1
    }

    Write-Error ("Unexpected launch argument value '{0}'." -f $token)
    exit 1
}

$argumentArray = @($tokens)
$argumentString = $argumentArray -join " "
if ($argumentString) {
    $commandPreview = 'Start-Process -FilePath "{0}" -WorkingDirectory "{1}" -ArgumentList "{2}"' -f $executablePath, $resolvedGameRoot, $argumentString
}
else {
    $commandPreview = 'Start-Process -FilePath "{0}" -WorkingDirectory "{1}"' -f $executablePath, $resolvedGameRoot
}

if ($PrintOnly) {
    Write-Output $commandPreview
    exit 0
}

Write-Error "Direct launch through tools/start_game_profile.ps1 is retired for real starts. Use the WinUI/AppCore managed safe-copy launch path so manifest, app-owned-root, patch-byte, and process-stop gates are enforced. PrintOnly remains available for command-shape probes."
exit 1

$startProcessArgs = @{
    FilePath = $executablePath
    WorkingDirectory = $resolvedGameRoot
    PassThru = $true
}
if ($argumentString) {
    $startProcessArgs.ArgumentList = $argumentString
}
$process = Start-Process @startProcessArgs

[PSCustomObject]@{
    schemaVersion = "game-launch-process.v1"
    processId = $process.Id
    executablePath = $executablePath
    workingDirectory = $resolvedGameRoot
    arguments = $argumentArray
    commandPreview = $commandPreview
} | ConvertTo-Json -Depth 4
