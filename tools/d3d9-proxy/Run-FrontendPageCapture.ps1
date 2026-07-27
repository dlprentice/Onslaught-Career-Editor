<#
.SYNOPSIS
    Drive the copied BEA build to a named frontend page and capture it from
    inside the process, with no screenshot and no global input.

.DESCRIPTION
    Two instruments, both of which exist because the obvious routes were
    measured not to work on this title:

      * CAPTURE is the proxy's Present-time back-buffer grab (src/shot.c).
        PrintWindow with PW_RENDERFULLCONTENT returns chrome and a blank client
        area here, because the Direct3D back buffer is never composited into the
        window DC. The grab needs no foreground window and cannot be raced by
        something appearing over the game.

      * NAVIGATION is posted window messages (tools/send_game_window_input.ps1
        -Transport messages). The cold frontend is message-driven. IN-LEVEL IS
        NOT -- the mouse gate at 0x0089BDF0, set by InitMouse (0x0042D397),
        switches the game to DirectInput with DISCL_EXCLUSIVE|DISCL_FOREGROUND,
        and posted positions are discarded. This script covers the FRONTEND.

    The screen-signature oracle is the proxy's own manifest.csv, not a
    screenshot: it carries the full-frame mean of every sampled frame, which is
    the same quantity the measured retail signatures are expressed in.

    The proxy is removed in a finally block. A stray one poisons the next parity
    capture and Capture-Retail.ps1 refuses to run if it finds one.

.PARAMETER Route
    frontend-options : click-to-start -> main menu -> Options (row 5).
    main-menu        : click-to-start -> main menu, then stop.
    pause-menu       : main menu -> New Game -> ... -> in level -> pause key.
                       Expected to need -ArmGlobalInput; see the notes it prints.
    none             : launch and sample only. Sends nothing.
#>
[CmdletBinding()]
param(
    [ValidateSet('frontend-options', 'main-menu', 'pause-menu', 'steps', 'none')]
    [string]$Route = 'frontend-options',
    # Used when -Route steps. One verb per element:
    #   wait <signature-name> <seconds>   block until the sampled mean matches
    #   settle <seconds>                  sleep
    #   click <x>,<y>                     WM_MOUSEMOVE then WM_LBUTTONDOWN/UP
    #   move <x>,<y>                      WM_MOUSEMOVE only
    #   key <KEYNAME>                     WM_KEYDOWN/UP with a real scan-code lParam
    #   mark <label>                      record the current mean under a label
    [string[]]$Steps = @(),
    [string]$GameDir,
    [string[]]$GameArgs = @('-skipfmv'),
    [int]$Seconds = 90,
    [string]$ShotRoot = 'G:\bea-frontend-pages',
    [int]$ShotEvery = 5,
    [int]$ShotMax = 160,
    [int]$ShotThresh = 8,
    [string]$Log,
    # Only consulted for routes that cannot be reached by posted messages.
    [string]$ArmGlobalInput = ''
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$src = Join-Path $PSScriptRoot 'build\d3d9.dll'
$inputScript = Join-Path $repo 'tools\send_game_window_input.ps1'
if (-not $GameDir) { $GameDir = Join-Path $repo 'local-lab\safe-copy-bea-pristine' }

if (-not (Test-Path $src)) { Write-Error 'build/d3d9.dll not found -- run build.ps1 first'; exit 1 }
if (-not (Test-Path $inputScript)) { Write-Error "input driver not found: $inputScript"; exit 1 }
$exe = Join-Path $GameDir 'BEA.exe'
if (-not (Test-Path $exe)) { Write-Error "BEA.exe not found in $GameDir"; exit 1 }

$full = (Resolve-Path $GameDir).Path
foreach ($bad in @('steamapps', 'Program Files', 'GOG Galaxy')) {
    if ($full -like "*$bad*") { Write-Error "refusing to operate on an installed game: $full"; exit 1 }
}
$dst = Join-Path $GameDir 'd3d9.dll'
if (Test-Path $dst) { Write-Error "a d3d9.dll is ALREADY present in $GameDir -- remove it by hand and re-run."; exit 1 }

$exeHashBefore = (Get-FileHash $exe -Algorithm SHA256).Hash
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$shotDir = Join-Path $ShotRoot "$Route-$stamp"
if (-not $Log) { $Log = Join-Path $shotDir 'd3d9-draws.log' }

Add-Type -Namespace BeaFP -Name W -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("user32.dll", SetLastError=true)]
public static extern bool PostMessage(System.IntPtr hWnd, uint Msg, System.IntPtr wParam, System.IntPtr lParam);
[System.Runtime.InteropServices.DllImport("user32.dll")]
public static extern bool GetClientRect(System.IntPtr hWnd, out RECT r);
public struct RECT { public int Left, Top, Right, Bottom; }
'@

# ---- the signature oracle ----------------------------------------------------
#
# Measured retail client means. Source: local-lab/RETAIL-CAPTURE-BREAKTHROUGH
# -2026-07-25.md:76-89, restated in STARTUP-FLOW-FINDINGS-2026-07-25.md:106-114.
$signatures = @{
    'click-to-start'   = @(73, 79, 94)
    'main-menu'        = @(35, 37, 60)
    'choose-game-name' = @(31, 33, 49)
    'select-level'     = @(31, 32, 55)
    'mission-briefing' = @(56, 61, 85)
    'select-config'    = @(59, 68, 95)
    'loading'          = @(107, 115, 125)
    # NEW, measured by this instrument on 2026-07-27 -- no retail capture of any
    # options page existed before. Provisional: taken from a single run.
    'options'          = @(31, 32, 54)
}

function Get-ShotRows {
    $m = Join-Path $shotDir 'manifest.csv'
    # The proxy stamps a run subdirectory under BEA_D3D9_SHOTDIR.
    if (-not (Test-Path $m)) {
        $cand = Get-ChildItem -Path $shotDir -Recurse -Filter manifest.csv -ErrorAction SilentlyContinue |
                Select-Object -First 1
        if (-not $cand) { return @() }
        $m = $cand.FullName
    }
    $rows = @()
    foreach ($line in (Get-Content $m -ErrorAction SilentlyContinue)) {
        if ($line.StartsWith('#') -or $line.StartsWith('frame,')) { continue }
        $f = $line -split ','
        if ($f.Count -lt 10) { continue }
        $rows += [pscustomobject]@{
            frame = [int]$f[0]; written = [int]$f[1]; file = $f[2]
            w = [int]$f[3]; h = [int]$f[4]
            r = [double]$f[6]; g = [double]$f[7]; b = [double]$f[8]
            dir = (Split-Path -Parent $m)
        }
    }
    return $rows
}

function Get-LatestMean {
    $rows = Get-ShotRows
    if ($rows.Count -eq 0) { return $null }
    return $rows[-1]
}

# Tolerance 4: select-level and choose-game-name differ by 7, so anything above
# 4 merges two distinct pages (RETAIL-CAPTURE-BREAKTHROUGH-2026-07-25.md:96-98).
function Wait-Signature {
    param([string]$Name, [int]$TimeoutSeconds = 40, [int]$Tolerance = 4)
    $want = $signatures[$Name]
    if (-not $want) { throw "no measured signature for '$Name'" }
    $end = (Get-Date).AddSeconds($TimeoutSeconds)
    $last = $null
    while ((Get-Date) -lt $end) {
        $m = Get-LatestMean
        if ($m) {
            $last = $m
            $d = [Math]::Abs($m.r - $want[0]) + [Math]::Abs($m.g - $want[1]) + [Math]::Abs($m.b - $want[2])
            if ($d -le $Tolerance) {
                Write-Host ("  reached '{0}' at frame {1}: mean {2},{3},{4} (want {5}, d={6})" -f `
                    $Name, $m.frame, [int]$m.r, [int]$m.g, [int]$m.b, ($want -join ','), [int]$d)
                return $true
            }
        }
        Start-Sleep -Milliseconds 400
    }
    $seen = if ($last) { "{0},{1},{2}" -f [int]$last.r, [int]$last.g, [int]$last.b } else { '<no frames sampled>' }
    Write-Warning ("timed out after {0}s waiting for '{1}' ({2}); last mean was {3}" -f `
        $TimeoutSeconds, $Name, ($want -join ','), $seen)
    return $false
}

# The arm phrase and the paths contain spaces, and native-command argument
# passing mangles them. -EncodedCommand takes one base64 UTF-16LE blob and has
# no quoting surface at all.
function Send-Frontend {
    param([string]$Sequence, [switch]$Verify)
    $verifyFlag = if ($Verify) { '-VerifyCursorGlobals' } else { '' }
    $cmd = @"
& '$inputScript' ``
  -ProcessId $($proc.Id) -HwndHex '$hwndHex' ``
  -ExpectedExecutablePath '$exe' -ExpectedWorkingDirectory '$full' ``
  -Sequence '$Sequence' ``
  -Transport messages ``
  -AllowBackgroundWindowMessages ``
  -BackgroundWindowMessagesArm 'ALLOW BACKGROUND BEA WINDOW MESSAGES' ``
  -StepDelayMs 90 $verifyFlag
"@
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
    Write-Host "  posting: $Sequence"
    # Start-Process with redirected streams, so the driver's own stderr survives
    # intact instead of being reformatted into a truncated RemoteException by
    # the host's native-command error rendering.
    $so = [IO.Path]::GetTempFileName()
    $se = [IO.Path]::GetTempFileName()
    $p = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $enc" `
        -Wait -PassThru -NoNewWindow -RedirectStandardOutput $so -RedirectStandardError $se
    $text = Get-Content $so -Raw -ErrorAction SilentlyContinue
    $err = Get-Content $se -Raw -ErrorAction SilentlyContinue
    Remove-Item $so, $se -Force -ErrorAction SilentlyContinue
    if ($err -and $err.Trim()) { Write-Host "  driver stderr: $($err.Trim())" }
    if (-not $text) { Write-Host "  driver produced no stdout (exit $($p.ExitCode))"; return $null }
    try { return $text | ConvertFrom-Json } catch { Write-Host $text; return $null }
}

$proc = $null
$hwndHex = $null
$navLog = [System.Collections.Generic.List[object]]::new()
$marks = [System.Collections.Generic.List[object]]::new()
try {
    New-Item -ItemType Directory -Force -Path $shotDir | Out-Null
    Copy-Item $src $dst
    Write-Host "proxy installed: $dst"

    $env:BEA_D3D9_SHOT = 'change'
    $env:BEA_D3D9_SHOTDIR = $shotDir
    $env:BEA_D3D9_SHOTEVERY = "$ShotEvery"
    $env:BEA_D3D9_SHOTMAX = "$ShotMax"
    $env:BEA_D3D9_SHOTTHRESH = "$ShotThresh"
    $env:BEA_D3D9_LOG = $Log
    $env:BEA_D3D9_MAXFRAMES = '0'      # draw log off; the shot manifest is the instrument
    $env:BEA_D3D9_FAULT_NOCLEARBIND = '0'
    Write-Host "shots -> $shotDir (change mode, every $ShotEvery frames, max $ShotMax, thresh $ShotThresh)"

    Write-Host ("launching: {0} {1}" -f $exe, ($GameArgs -join ' '))
    $proc = Start-Process -FilePath $exe -ArgumentList $GameArgs -WorkingDirectory $GameDir -PassThru

    # Wait for a window.
    $end = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $end) {
        $proc.Refresh()
        if ($proc.HasExited) { throw 'the game exited before showing a window' }
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) { break }
        Start-Sleep -Milliseconds 300
    }
    if ($proc.MainWindowHandle -eq [IntPtr]::Zero) { throw 'no window appeared within 30s' }
    $hwndHex = "0x{0:X}" -f [int64]$proc.MainWindowHandle
    $rc = New-Object 'BeaFP.W+RECT'
    [void][BeaFP.W]::GetClientRect($proc.MainWindowHandle, [ref]$rc)
    Write-Host ("window {0}, client {1}x{2}, pid {3}" -f $hwndHex, ($rc.Right - $rc.Left), ($rc.Bottom - $rc.Top), $proc.Id)
    if (($rc.Right - $rc.Left) -ne 640) {
        Write-Warning "client width is $($rc.Right - $rc.Left), not the expected 640 -- menu coordinates are in 640x480 client space."
    }

    if ($Route -ne 'none' -and $Route -ne 'steps') {
        # click-to-start goes BLACK at t=32s with no input, and the target loses
        # foreground at t=44s (RETAIL-CAPTURE-BREAKTHROUGH-2026-07-25.md:28-34).
        # Click promptly; do not design a wait longer than that budget.
        if (Wait-Signature -Name 'click-to-start' -TimeoutSeconds 25) {
            $navLog.Add((Send-Frontend -Sequence 'move:320x240,wait:150,click:320x240' -Verify)) | Out-Null
        } else {
            Write-Warning 'click-to-start signature never appeared; clicking centre anyway.'
            $navLog.Add((Send-Frontend -Sequence 'move:320x240,wait:150,click:320x240' -Verify)) | Out-Null
        }
        $onMenu = Wait-Signature -Name 'main-menu' -TimeoutSeconds 25
    }

    switch ($Route) {
        'frontend-options' {
            # Main-menu rows: x = 219 (a CENTRE anchor), y = 304 + 20k.
            # Drawn order: New Game, Continue, Load, Multiplayer, Goodies,
            # Options, Quit -- so Options is index 5 => y = 404.
            # (RetailFrontendSession.cs:11-31; STARTUP-FLOW-FINDINGS:158-160.)
            Write-Host 'navigating to Options (main-menu row 5, client 219,404)'
            $navLog.Add((Send-Frontend -Sequence 'move:219x404,wait:250,click:219x404' -Verify)) | Out-Null
            Start-Sleep -Seconds 4
            $m = Get-LatestMean
            if ($m) { Write-Host ("  post-click mean: {0},{1},{2}" -f [int]$m.r, [int]$m.g, [int]$m.b) }
            Start-Sleep -Seconds 3
        }
        'main-menu' { Start-Sleep -Seconds 5 }
        'steps' {
            foreach ($step in $Steps) {
                $tok = $step -split '\s+'
                switch ($tok[0]) {
                    'wait'   { [void](Wait-Signature -Name $tok[1] -TimeoutSeconds ([int]$tok[2])) }
                    'settle' { Start-Sleep -Seconds ([double]$tok[1]) }
                    'click'  {
                        $xy = $tok[1] -split ','
                        $navLog.Add((Send-Frontend -Sequence ("move:{0}x{1},wait:250,click:{0}x{1}" -f $xy[0], $xy[1]) -Verify)) | Out-Null
                    }
                    'move'   {
                        $xy = $tok[1] -split ','
                        $navLog.Add((Send-Frontend -Sequence ("move:{0}x{1}" -f $xy[0], $xy[1]) -Verify)) | Out-Null
                    }
                    'key'    {
                        $navLog.Add((Send-Frontend -Sequence ("tap:{0}" -f $tok[1]) -Verify)) | Out-Null
                    }
                    'mark'   {
                        $m = Get-LatestMean
                        if ($m) {
                            Write-Host ("  MARK {0}: frame {1} mean {2},{3},{4}" -f $tok[1], $m.frame, [int]$m.r, [int]$m.g, [int]$m.b)
                            $marks.Add([PSCustomObject]@{ label = $tok[1]; frame = $m.frame; r = $m.r; g = $m.g; b = $m.b }) | Out-Null
                        } else {
                            Write-Host ("  MARK {0}: no frames sampled yet" -f $tok[1])
                        }
                    }
                    default  { Write-Warning "unknown step verb '$($tok[0])'" }
                }
            }
        }
        'pause-menu' {
            Write-Host 'pause-menu route: New Game (219,304)'
            $navLog.Add((Send-Frontend -Sequence 'move:219x304,wait:250,click:219x304' -Verify)) | Out-Null
            Start-Sleep -Seconds 3
        }
    }

    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline -and -not $proc.HasExited) { Start-Sleep -Milliseconds 500 }
}
finally {
    if ($proc -and -not $proc.HasExited) {
        $proc.Refresh()
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
            [void][BeaFP.W]::PostMessage($proc.MainWindowHandle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)
            $proc.WaitForExit(10000) | Out-Null
        }
        if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit(5000) | Out-Null }
    }
    Remove-Item Env:BEA_D3D9_SHOT, Env:BEA_D3D9_SHOTDIR, Env:BEA_D3D9_SHOTEVERY,
                Env:BEA_D3D9_SHOTMAX, Env:BEA_D3D9_SHOTTHRESH, Env:BEA_D3D9_LOG,
                Env:BEA_D3D9_MAXFRAMES, Env:BEA_D3D9_FAULT_NOCLEARBIND `
                -ErrorAction SilentlyContinue

    for ($i = 0; $i -lt 20 -and (Test-Path $dst); $i++) {
        Remove-Item $dst -Force -ErrorAction SilentlyContinue
        if (Test-Path $dst) { Start-Sleep -Milliseconds 250 }
    }
    if (Test-Path $dst) { Write-Warning "COULD NOT REMOVE $dst -- remove it before any parity capture." }
    else { Write-Host "proxy removed: $dst" }
}

$exeHashAfter = (Get-FileHash $exe -Algorithm SHA256).Hash
if ($exeHashBefore -ne $exeHashAfter) { Write-Warning "BEA.exe hash CHANGED: $exeHashBefore -> $exeHashAfter" }
else { Write-Host "BEA.exe unchanged (sha256 $($exeHashAfter.Substring(0,8)))" }

$rows = Get-ShotRows
Write-Host ''
Write-Host ("sampled {0} frames, wrote {1} images" -f $rows.Count, @($rows | Where-Object { $_.written -eq 1 }).Count)
if ($rows.Count) {
    Write-Host ("shot dir: {0}" -f $rows[0].dir)
    Write-Host 'distinct written frames (frame  mean  file):'
    foreach ($r in ($rows | Where-Object { $_.written -eq 1 })) {
        $name = ''
        foreach ($k in $signatures.Keys) {
            $s = $signatures[$k]
            if (([Math]::Abs($r.r - $s[0]) + [Math]::Abs($r.g - $s[1]) + [Math]::Abs($r.b - $s[2])) -le 4) { $name = "  <= $k" }
        }
        Write-Host ("  {0,6}  {1,3},{2,3},{3,3}  {4}{5}" -f $r.frame, [int]$r.r, [int]$r.g, [int]$r.b, $r.file, $name)
    }
}
if ($marks.Count) {
    Write-Host ''
    Write-Host 'marks:'
    foreach ($k in $marks) {
        Write-Host ("  {0,-22} frame {1,6}  mean {2,3},{3,3},{4,3}" -f $k.label, $k.frame, [int]$k.r, [int]$k.g, [int]$k.b)
    }
}
if ($navLog.Count) {
    $navDir = if ($rows.Count) { $rows[0].dir } else { $shotDir }
    $navPath = Join-Path $navDir 'navigation.json'
    $navLog | ConvertTo-Json -Depth 10 | Set-Content -Path $navPath -Encoding UTF8
    Write-Host ("navigation receipts: {0}" -f $navPath)
    foreach ($n in $navLog) {
        if (-not $n) { continue }
        $occ = if ($n.occlusionBefore) { "occluded=$(-not $n.occlusionBefore.unoccluded) fg=$($n.occlusionBefore.foreground)" } else { 'n/a' }
        Write-Host ("  status={0} wmSent={1} {2}" -f $n.status, $n.windowMessageEventsSent, $occ)
        foreach ($p in @($n.cursorProbes)) {
            Write-Host ("    posted {0},{1} -> A {2} int={3} f={4} | B {5} int={6} f={7} | gate {8}" -f `
                $p.postedClientX, $p.postedClientY,
                $p.globals.a.hex, $p.globals.a.asInt32, [math]::Round($p.globals.a.asFloat, 2),
                $p.globals.b.hex, $p.globals.b.asInt32, [math]::Round($p.globals.b.asFloat, 2),
                $p.globals.mouseGate.asInt32)
        }
    }
}
