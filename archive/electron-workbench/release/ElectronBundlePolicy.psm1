function ConvertTo-BundleRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$BundleRoot,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $root = [System.IO.Path]::GetFullPath($BundleRoot).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $candidate = [System.IO.Path]::GetFullPath($Path)
    if (-not $candidate.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside bundle root: $candidate"
    }

    return $candidate.Substring($root.Length).Replace('\', '/')
}

function Get-ElectronBundlePolicyViolation {
    param(
        [Parameter(Mandatory = $true)][string]$BundleRoot
    )

    if (-not (Test-Path -LiteralPath $BundleRoot)) {
        throw "Bundle root does not exist: $BundleRoot"
    }

    $deniedExact = @(
        'AGENTS.md',
        'app/AGENTS.md',
        'app/developer_agent_state.json',
        'app/documentation_agent_state.json',
        'app/re_orchestrator_state.json',
        'app/USER_SANITY_CHECK.md',
        'app/MCP_DEBUGGING_OPTIONS.md',
        'app/MCP_LIMITATIONS.md'
    )

    $deniedRoots = @(
        'app/.codex',
        'app/archive',
        'app/OnslaughtCareerEditor.WinUI',
        'app/game',
        'app/media',
        'app/save-attempts',
        'app/subagents',
        'app/references',
        'app/discord_channel_dumps',
        'app/wave_online_audit',
        'app/wave_online_audit2'
    )

    Get-ChildItem -LiteralPath $BundleRoot -Force -Recurse | ForEach-Object {
        $relative = ConvertTo-BundleRelativePath -BundleRoot $BundleRoot -Path $_.FullName
        $normalized = $relative.TrimEnd('/')
        $denied = $false

        if ($deniedExact -contains $normalized) {
            $denied = $true
        }

        foreach ($root in $deniedRoots) {
            if ($normalized.Equals($root, [System.StringComparison]::OrdinalIgnoreCase) -or $normalized.StartsWith("$root/", [System.StringComparison]::OrdinalIgnoreCase)) {
                $denied = $true
                break
            }
        }

        if ($denied) {
            [pscustomobject]@{
                Path = $normalized
                Kind = if ($_.PSIsContainer) { 'directory' } else { 'file' }
            }
        }
    }
}

function Assert-ElectronBundlePolicy {
    param(
        [Parameter(Mandatory = $true)][string]$BundleRoot,
        [ValidateSet('community', 'maintainer')]
        [string]$Audience = 'community',
        [string]$ReportPath
    )

    $violations = @(Get-ElectronBundlePolicyViolation -BundleRoot $BundleRoot)
    if ($violations.Count -gt 0) {
        $preview = ($violations | Select-Object -First 20 | ForEach-Object { "  - $($_.Path) [$($_.Kind)]" }) -join [Environment]::NewLine
        throw "Electron bundle policy violation: $($violations.Count) denied path(s) found.$([Environment]::NewLine)$preview"
    }

    if ($ReportPath) {
        $report = [ordered]@{
            schema = 'electron-bundle-policy.v1'
            audience = $Audience
            checkedAtUtc = [DateTime]::UtcNow.ToString('o')
            bundleRoot = [System.IO.Path]::GetFullPath($BundleRoot)
            deniedPathCount = 0
        }
        New-Item -ItemType Directory -Path (Split-Path -Parent $ReportPath) -Force | Out-Null
        $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
    }

    return $true
}

Export-ModuleMember -Function Assert-ElectronBundlePolicy, Get-ElectronBundlePolicyViolation
