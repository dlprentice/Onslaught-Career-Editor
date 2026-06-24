[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$modulePath = Join-Path $PSScriptRoot "ElectronBundlePolicy.psm1"
Import-Module $modulePath -Force

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("onslaught-bundle-policy-" + [Guid]::NewGuid().ToString("N"))
$safeRoot = Join-Path $tempRoot "safe"
$unsafeRoot = Join-Path $tempRoot "unsafe"

try {
    New-Item -ItemType Directory -Path (Join-Path $safeRoot "app\electron\dist") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $safeRoot "app\ui") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $safeRoot "app\patches\catalog") -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $safeRoot "app\electron\dist\main.js") -Value "console.log('ok')" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $safeRoot "app\ui\index.html") -Value "<main>ok</main>" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $safeRoot "app\patches\catalog\patches.v2.json") -Value "{}" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $safeRoot "app\README.MD") -Value "# Onslaught Toolkit" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $safeRoot "LICENSE") -Value "fixture" -Encoding UTF8

    $reportPath = Join-Path $safeRoot "bundle-policy.v1.json"
    Assert-ElectronBundlePolicy -BundleRoot $safeRoot -Audience community -ReportPath $reportPath | Out-Null
    if (-not (Test-Path -LiteralPath $reportPath)) {
        throw "Expected policy report was not written: $reportPath"
    }

    New-Item -ItemType Directory -Path (Join-Path $unsafeRoot "app\game") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $unsafeRoot "app\.codex\state") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $unsafeRoot "app\subagents") -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $unsafeRoot "app\AGENTS.md") -Value "private instructions" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $unsafeRoot "app\.codex\state\repo-hardening-progress.md") -Value "agent state" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $unsafeRoot "app\game\BEA.exe") -Value "private binary" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $unsafeRoot "app\subagents\note.md") -Value "scratch" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $unsafeRoot "app\developer_agent_state.json") -Value "{}" -Encoding UTF8

    $threw = $false
    try {
        Assert-ElectronBundlePolicy -BundleRoot $unsafeRoot -Audience community | Out-Null
    }
    catch {
        $threw = $true
        if (-not ($_.Exception.Message -match "Electron bundle policy violation")) {
            throw
        }
    }

    if (-not $threw) {
        throw "Expected unsafe bundle fixture to fail policy validation."
    }

    Write-Host "Electron bundle policy smoke: PASS"
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
