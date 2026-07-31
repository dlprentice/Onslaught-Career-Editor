<#
.SYNOPSIS
    Copy the proxy into a copied BEA build, run it, capture, and remove the
    proxy again so the capture target stays byte-identical between runs.

.DESCRIPTION
    The proxy is NEVER left in the game directory: removal is in a finally
    block, and the script reports the post-run directory state so a failure to
    clean up is visible rather than silent. Existing parity captures depend on
    that directory not changing.

    The game is closed by posting WM_CLOSE to its own window handle. No global
    synthetic input is sent -- see AGENTS.md.

.PARAMETER GameDir
    A COPIED build only. The script refuses to touch a Steam or Program Files
    installation.

.PARAMETER NoLog
    Run with the proxy present but logging disabled, to prove the game is
    unaffected when the instrument is inert.

.EXAMPLE
    ./Run-D3D9Capture.ps1 -Seconds 25
    ./Run-D3D9Capture.ps1 -NoLog -Seconds 20
    ./Run-D3D9Capture.ps1 -MaxFrames 5 -NoVerts
#>
[CmdletBinding()]
param(
    [string]$GameDir,
    [string[]]$GameArgs = @('-skipfmv'),
    [int]$Seconds = 25,
    [string]$Log,
    [int]$MaxFrames = 300,
    [int]$FirstFrame = 0,
    [int]$MaxVerts = 64,
    [switch]$NoVerts,
    # Refuse, rather than flag, any draw whose vertices depend on a byte range
    # whose written extent was inferred from a Lock(off, 0, ...) rather than
    # measured. See README.md, "What the coverage check actually guarantees".
    [switch]$StrictCov,
    # Vertex-dump gating. The dump is the expensive record -- an in-level frame
    # is ~1,200 draws and the largest carry ~6,000 vertices -- so these narrow
    # WHICH draws get one. Every excluded draw is still refused by the name of
    # the predicate that excluded it, and the settings are restated in the log
    # header, so a narrow capture can never be misread as an empty frame.
    [int]$VDrawFirst = 0,
    [int]$VDrawLast = -1,
    [int]$VMinVerts = 0,
    [string]$VFvf = '0',
    [int]$VBudget = 0,
    [switch]$VDedup,
    # The per-draw geometry digest: identity, hash and position bounds of the
    # bytes each draw reads. Cheap, and it is what answers whether a mesh is
    # re-written per frame (CPU skinning) or merely re-transformed.
    [switch]$NoDigest,
    # Hash level 0 of each bound texture once, to attribute a draw to a named
    # asset. This is the only setting that reads a Direct3D resource back; it
    # locks READONLY and only where the texture's own descriptor allows it.
    [switch]$TexHash,
    [switch]$NoLog,
    [string]$CaptureRoot = 'G:\bea-d3d9-capture'
)

$ErrorActionPreference = 'Stop'
$src = Join-Path $PSScriptRoot 'build\d3d9.dll'
if (-not $GameDir) {
    $GameDir = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'local-lab\safe-copy-bea-pristine'
}

if (-not (Test-Path $src)) { Write-Error 'build/d3d9.dll not found -- run build.ps1 first'; exit 1 }
if (-not (Test-Path $GameDir)) { Write-Error "game directory not found: $GameDir"; exit 1 }

$exe = Join-Path $GameDir 'BEA.exe'
if (-not (Test-Path $exe)) { Write-Error "BEA.exe not found in $GameDir"; exit 1 }

# --- refuse anything that is not a copied build -------------------------------
$full = (Resolve-Path $GameDir).Path
foreach ($bad in @('steamapps', 'Program Files', 'GOG Galaxy')) {
    if ($full -like "*$bad*") {
        Write-Error "refusing to operate on what looks like an installed game: $full"
        exit 1
    }
}

$dst = Join-Path $GameDir 'd3d9.dll'
if (Test-Path $dst) {
    Write-Error "a d3d9.dll is ALREADY present in $GameDir -- refusing to overwrite it. Remove it by hand and re-run."
    exit 1
}

$exeHashBefore = (Get-FileHash $exe -Algorithm SHA256).Hash

if (-not $Log -and -not $NoLog) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $Log = Join-Path $CaptureRoot "d3d9-$stamp.log"
}

Add-Type -Namespace BeaWin -Name Msg -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("user32.dll", SetLastError=true)]
public static extern bool PostMessage(System.IntPtr hWnd, uint Msg, System.IntPtr wParam, System.IntPtr lParam);
'@

# NOTE: window-DC capture does not work for this title. PrintWindow with
# PW_RENDERFULLCONTENT returns the window chrome and a BLANK white client area,
# because the Direct3D 9 back buffer is never composited into the window DC.
# Screenshots therefore still require a desktop-region grab (which needs
# foreground and is unsafe while the maintainer is at the machine), or a
# back-buffer grab from inside the process. See README.md.

$proc = $null
try {
    Copy-Item $src $dst
    Write-Host "proxy installed: $dst"

    if ($NoLog) {
        Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_CAPTURE -ErrorAction SilentlyContinue
        Write-Host 'logging DISABLED (inert pass-through)'
    } else {
        $env:BEA_D3D9_LOG = $Log
        $env:BEA_D3D9_MAXFRAMES = "$MaxFrames"
        $env:BEA_D3D9_FIRSTFRAME = "$FirstFrame"
        $env:BEA_D3D9_MAXVERTS = "$MaxVerts"
        $env:BEA_D3D9_NOVERTS = if ($NoVerts) { '1' } else { '0' }
        $env:BEA_D3D9_STRICTCOV = if ($StrictCov) { '1' } else { '0' }
        $env:BEA_D3D9_VDRAWFIRST = "$VDrawFirst"
        $env:BEA_D3D9_VDRAWLAST = if ($VDrawLast -lt 0) { '4294967295' } else { "$VDrawLast" }
        $env:BEA_D3D9_VMINVERTS = "$VMinVerts"
        $env:BEA_D3D9_VFVF = $VFvf
        $env:BEA_D3D9_VBUDGET = "$VBudget"
        $env:BEA_D3D9_VDEDUP = if ($VDedup) { '1' } else { '0' }
        $env:BEA_D3D9_DIGEST = if ($NoDigest) { '0' } else { '1' }
        $env:BEA_D3D9_TEXHASH = if ($TexHash) { '1' } else { '0' }
        # Never inherited from the caller: a capture must not be a test artefact.
        $env:BEA_D3D9_FAULT_NOCLEARBIND = '0'
        Write-Host "logging to: $Log (frames $FirstFrame..$($FirstFrame + $MaxFrames - 1), maxverts $MaxVerts, strictcov $([int][bool]$StrictCov))"
        Write-Host ("  vertex gate: draws [{0},{1}] minverts {2} fvf {3} budget {4} dedup {5}; digest {6}; texhash {7}" -f
            $VDrawFirst, $(if ($VDrawLast -lt 0) { 'end' } else { $VDrawLast }), $VMinVerts, $VFvf, $VBudget,
            [int][bool]$VDedup, [int](-not $NoDigest), [int][bool]$TexHash)
    }

    Write-Host ("launching: {0} {1}" -f $exe, ($GameArgs -join ' '))
    $proc = Start-Process -FilePath $exe -ArgumentList $GameArgs -WorkingDirectory $GameDir -PassThru

    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Milliseconds 500
    }

    if (-not $proc.HasExited) {
        $proc.Refresh()
        $hwnd = $proc.MainWindowHandle
        if ($hwnd -ne [IntPtr]::Zero) {
            Write-Host ("closing window 0x{0:X} with WM_CLOSE" -f [int64]$hwnd)
            [BeaWin.Msg]::PostMessage($hwnd, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
            $proc.WaitForExit(10000) | Out-Null
        }
    }
    if (-not $proc.HasExited) {
        Write-Host 'window did not close; terminating the copied build'
        $proc.Kill()
        $proc.WaitForExit(5000) | Out-Null
    }
    Write-Host ("game exited (code {0})" -f $(if ($proc.HasExited) { $proc.ExitCode } else { 'still running' }))
}
finally {
    Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_CAPTURE, Env:BEA_D3D9_MAXFRAMES,
                Env:BEA_D3D9_FIRSTFRAME, Env:BEA_D3D9_MAXVERTS, Env:BEA_D3D9_NOVERTS,
                Env:BEA_D3D9_STRICTCOV, Env:BEA_D3D9_FAULT_NOCLEARBIND,
                Env:BEA_D3D9_VDRAWFIRST, Env:BEA_D3D9_VDRAWLAST,
                Env:BEA_D3D9_VMINVERTS, Env:BEA_D3D9_VFVF, Env:BEA_D3D9_VBUDGET,
                Env:BEA_D3D9_VDEDUP, Env:BEA_D3D9_DIGEST, Env:BEA_D3D9_TEXHASH `
                -ErrorAction SilentlyContinue

    # The proxy must never be left behind. Retry briefly in case the loader has
    # not released the file yet.
    for ($i = 0; $i -lt 20 -and (Test-Path $dst); $i++) {
        Remove-Item $dst -Force -ErrorAction SilentlyContinue
        if (Test-Path $dst) { Start-Sleep -Milliseconds 250 }
    }
    if (Test-Path $dst) {
        Write-Warning "COULD NOT REMOVE $dst -- remove it before any parity capture."
    } else {
        Write-Host "proxy removed: $dst"
    }
}

$exeHashAfter = (Get-FileHash $exe -Algorithm SHA256).Hash
if ($exeHashBefore -ne $exeHashAfter) {
    Write-Warning "BEA.exe hash CHANGED: $exeHashBefore -> $exeHashAfter"
} else {
    Write-Host "BEA.exe unchanged (sha256 $($exeHashAfter.Substring(0,8)))"
}

if ($Log -and (Test-Path $Log)) {
    $fi = Get-Item $Log
    $lines = (Get-Content $Log | Measure-Object -Line).Lines
    Write-Host ''
    Write-Host ("log: {0}" -f $Log)
    Write-Host ("     {0:N0} bytes, {1:N0} lines" -f $fi.Length, $lines)
    Write-Host ("     frames presented: {0}" -f (Select-String -Path $Log -Pattern '^P ' | Measure-Object).Count)
    Write-Host ("     draws recorded:   {0}" -f (Select-String -Path $Log -Pattern '^D ' | Measure-Object).Count)
    Write-Host ("     transforms (M):   {0}" -f (Select-String -Path $Log -Pattern '^M ' | Measure-Object).Count)
    Write-Host ("     digests (G):      {0}" -f (Select-String -Path $Log -Pattern '^G ' | Measure-Object).Count)
    Write-Host ("     textures (T):     {0}" -f (Select-String -Path $Log -Pattern '^T create ' | Measure-Object).Count)

    # What was NOT recorded matters as much as what was. The proxy tallies this
    # itself; surface it here so an incomplete capture is visible at the console
    # rather than only to whoever greps the log later.
    $tally = @(Select-String -Path $Log -Pattern '^#\s+\S+ = \d+$' | Select-Object -Last 32)
    $totals = @(Select-String -Path $Log -Pattern '^# refusals total=' | Select-Object -Last 1)
    if ($totals.Count -gt 0) {
        Write-Host ("     {0}" -f $totals[0].Line.TrimStart('#', ' '))
        foreach ($t in $tally) { Write-Host ("       {0}" -f $t.Line.TrimStart('#', ' ')) }
    }
    if (-not (Select-String -Path $Log -Pattern '^# detach' -Quiet)) {
        Write-Warning "log has no '# detach' line: the process did not exit cleanly and the tail may be truncated."
    }
} elseif (-not $NoLog) {
    Write-Warning "no log was produced at $Log"
}
