<#
.SYNOPSIS
    Prove the Present-time back-buffer grab against KNOWN colours.

.DESCRIPTION
    Drives the proxy through a real HAL device on an off-screen window that is
    never shown, clearing each frame to an exact colour, then checks:

      * the manifest's full-frame mean is that exact colour;
      * the PNG decodes -- independently, in Python -- to that exact colour on
        every pixel, which is what proves the channel order and the hand-rolled
        stored-deflate encoder rather than assuming them;
      * `change` mode writes only the frames where the picture changed.

    Two of the four colours are the measured retail screen signatures this
    instrument exists to reproduce (main menu 35,37,60 and click-to-start
    73,79,94), so a wrong reading is a wrong NUMBER here, not a picture someone
    has to eyeball later.

    Nothing appears on screen, no focus is taken, and the game directory is not
    touched.
#>
[CmdletBinding()]
param(
    [string]$Zig = "$env:LOCALAPPDATA\Microsoft\WinGet\Links\zig.exe",
    [string]$Python = 'python',
    [string]$WorkDir = (Join-Path $env:TEMP ('bea-d3d9-shottest-' + [guid]::NewGuid().ToString('N').Substring(0, 8)))
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dll = Join-Path $here 'build\d3d9.dll'
if (-not (Test-Path $dll)) { Write-Error 'build/d3d9.dll not found -- run build.ps1 first'; exit 1 }

New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
$exe = Join-Path $WorkDir 'shottest.exe'
& $Zig cc -target x86-windows-gnu -O1 -o $exe (Join-Path $here 'test\shottest.c') -lgdi32
if ($LASTEXITCODE -ne 0) { Write-Error 'shot self-test build failed'; exit 1 }
Copy-Item $dll (Join-Path $WorkDir 'd3d9.dll')

$fail = 0
function Check($name, $cond) {
    if ($cond) { Write-Host "  PASS  $name" }
    else { Write-Host "  FAIL  $name"; $script:fail++ }
}

function Get-Manifest($dir) {
    $m = Get-ChildItem -Path $dir -Recurse -Filter manifest.csv | Select-Object -First 1
    if (-not $m) { return $null }
    $rows = @()
    foreach ($line in Get-Content $m.FullName) {
        if ($line.StartsWith('#') -or $line.StartsWith('frame,')) { continue }
        $f = $line -split ','
        if ($f.Count -lt 10) { continue }
        $rows += [pscustomobject]@{
            frame = [int]$f[0]; written = [int]$f[1]; file = $f[2]
            w = [int]$f[3]; h = [int]$f[4]; fmt = [int]$f[5]
            r = [double]$f[6]; g = [double]$f[7]; b = [double]$f[8]
            delta = [int]$f[9]
            dir = $m.Directory.FullName
        }
    }
    return $rows
}

function Clear-ShotEnv {
    Remove-Item Env:BEA_D3D9_SHOT, Env:BEA_D3D9_SHOTDIR, Env:BEA_D3D9_SHOTEVERY,
                Env:BEA_D3D9_SHOTMAX, Env:BEA_D3D9_SHOTTHRESH, Env:BEA_D3D9_LOG,
                Env:BEA_D3D9_CAPTURE -ErrorAction SilentlyContinue
}

# ---- (0) inert unless BEA_D3D9_SHOT is set -----------------------------------

Write-Host "`n[0] no BEA_D3D9_SHOT: nothing is grabbed"
Clear-ShotEnv
$inert = Join-Path $WorkDir 'inert'
$env:BEA_D3D9_SHOTDIR = $inert
$out = & $exe 2>&1
Clear-ShotEnv
Check 'host exits 0' ($LASTEXITCODE -eq 0)
Check 'loads the proxy, not the system DLL' (($out -join "`n") -match [regex]::Escape($WorkDir))
Check 'no shot directory is created' (-not (Test-Path $inert))

# ---- (1) every frame ---------------------------------------------------------

Write-Host "`n[1] BEA_D3D9_SHOT=all"
Clear-ShotEnv
$allDir = Join-Path $WorkDir 'all'
$env:BEA_D3D9_SHOT = 'all'
$env:BEA_D3D9_SHOTDIR = $allDir
$out = & $exe 2>&1
Clear-ShotEnv
Write-Host ($out | ForEach-Object { "      $_" })
Check 'host exits 0' ($LASTEXITCODE -eq 0)

$rows = Get-Manifest $allDir
Check 'manifest has 4 rows' ($rows -and $rows.Count -eq 4)
if (-not $rows -or $rows.Count -ne 4) { Write-Host "`n$fail failure(s)"; exit 1 }

Check 'all 4 frames written' (@($rows | Where-Object { $_.written -eq 1 }).Count -eq 4)
Check 'surface is 64x48' (@($rows | Where-Object { $_.w -eq 64 -and $_.h -eq 48 }).Count -eq 4)

# The whole point: the mean must be the colour that was cleared, exactly.
$expect = @(@(35, 37, 60), @(35, 37, 60), @(73, 79, 94), @(73, 79, 94))
for ($i = 0; $i -lt 4; $i++) {
    $e = $expect[$i]; $r = $rows[$i]
    Check ("frame $i mean is exactly $($e -join ',') (got $([math]::Round($r.r,3)),$([math]::Round($r.g,3)),$([math]::Round($r.b,3)))") `
        ([math]::Abs($r.r - $e[0]) -lt 0.001 -and
         [math]::Abs($r.g - $e[1]) -lt 0.001 -and
         [math]::Abs($r.b - $e[2]) -lt 0.001)
}

# ---- (2) the PNG itself, decoded independently -------------------------------

Write-Host "`n[2] PNG decodes to the same pixels"
$py = @'
import sys, zlib, struct, os, json
d = sys.argv[1]
want = json.loads(sys.argv[2])
res = []
for frame, rgb in want:
    p = os.path.join(d, "f%06d.png" % frame)
    if not os.path.exists(p):
        res.append([frame, "missing", None, None]); continue
    b = open(p, "rb").read()
    assert b[:8] == b"\x89PNG\r\n\x1a\n", "signature"
    o, w, h, idat = 8, None, None, b""
    while o < len(b):
        ln = struct.unpack(">I", b[o:o+4])[0]
        typ = b[o+4:o+8]
        data = b[o+8:o+8+ln]
        crc = struct.unpack(">I", b[o+8+ln:o+12+ln])[0]
        assert crc == zlib.crc32(typ + data) & 0xFFFFFFFF, "crc %s" % typ
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[:10])
            assert bd == 8 and ct == 2, "not 8-bit RGB"
        elif typ == b"IDAT":
            idat += data
        o += 12 + ln
    raw = zlib.decompress(idat)
    assert len(raw) == h * (w * 3 + 1), "raw length"
    px = set()
    for y in range(h):
        row = raw[y*(w*3+1):(y+1)*(w*3+1)]
        assert row[0] == 0, "filter type"
        for x in range(w):
            px.add(tuple(row[1+x*3:4+x*3]))
    res.append([frame, "ok", sorted(px), [w, h]])
print(json.dumps(res))
'@
$pyFile = Join-Path $WorkDir 'checkpng.py'
Set-Content -Path $pyFile -Value $py -Encoding UTF8
$want = ConvertTo-Json @(, @(0, @(35, 37, 60))) -Compress
$want = '[[0,[35,37,60]],[2,[73,79,94]]]'
$dir = $rows[0].dir
$json = & $Python $pyFile $dir $want
Check 'python decoder ran' ($LASTEXITCODE -eq 0 -and $json)
if ($LASTEXITCODE -eq 0 -and $json) {
    $dec = $json | ConvertFrom-Json
    foreach ($d in $dec) {
        $frame = $d[0]; $status = $d[1]; $px = $d[2]; $dim = $d[3]
        Check "frame $frame PNG parses (chunk CRCs, zlib, IHDR)" ($status -eq 'ok')
        if ($status -eq 'ok') {
            Check "frame $frame PNG is 64x48" ($dim[0] -eq 64 -and $dim[1] -eq 48)
            Check "frame $frame PNG holds exactly ONE distinct colour" ($px.Count -eq 1)
            if ($px.Count -eq 1) {
                $e = if ($frame -eq 0) { @(35, 37, 60) } else { @(73, 79, 94) }
                Check ("frame $frame PNG colour is $($e -join ',') (got $($px[0] -join ','))") `
                    ($px[0][0] -eq $e[0] -and $px[0][1] -eq $e[1] -and $px[0][2] -eq $e[2])
            }
        }
    }
}

# ---- (3) change mode ---------------------------------------------------------

Write-Host "`n[3] BEA_D3D9_SHOT=change writes only when the picture changes"
Clear-ShotEnv
$chDir = Join-Path $WorkDir 'change'
$env:BEA_D3D9_SHOT = 'change'
$env:BEA_D3D9_SHOTDIR = $chDir
$env:BEA_D3D9_SHOTEVERY = '1'
$env:BEA_D3D9_SHOTTHRESH = '6'
$out = & $exe 2>&1
Clear-ShotEnv
Check 'host exits 0' ($LASTEXITCODE -eq 0)
$rows = Get-Manifest $chDir
Check 'all 4 frames are candidates' ($rows -and $rows.Count -eq 4)
if ($rows -and $rows.Count -eq 4) {
    $written = @($rows | Where-Object { $_.written -eq 1 } | ForEach-Object { $_.frame })
    Check ('only frames 0 and 2 are written (got ' + ($written -join ',') + ')') `
        ($written.Count -eq 2 -and $written[0] -eq 0 -and $written[1] -eq 2)
    Check 'frame 1 reports a zero cell delta' ($rows[1].delta -eq 0)
    Check 'frame 2 reports a delta at or above the threshold' ($rows[2].delta -ge 6)
    Check 'means are still recorded for the frames NOT written' `
        ([math]::Abs($rows[1].r - 35) -lt 0.001 -and [math]::Abs($rows[3].r - 73) -lt 0.001)
    $files = @(Get-ChildItem -Path $rows[0].dir -Filter '*.png')
    Check 'exactly 2 PNGs on disk' ($files.Count -eq 2)
}

# ---- (4) frame list and the write cap ----------------------------------------

Write-Host "`n[4] frame list and BEA_D3D9_SHOTMAX"
Clear-ShotEnv
$selDir = Join-Path $WorkDir 'sel'
$env:BEA_D3D9_SHOT = '1,3'
$env:BEA_D3D9_SHOTDIR = $selDir
& $exe > $null 2>&1
Clear-ShotEnv
$rows = Get-Manifest $selDir
Check 'only the two listed frames are candidates' ($rows -and $rows.Count -eq 2)
if ($rows -and $rows.Count -eq 2) {
    Check 'the listed frames are 1 and 3' ($rows[0].frame -eq 1 -and $rows[1].frame -eq 3)
}

Clear-ShotEnv
$capDir = Join-Path $WorkDir 'cap'
$env:BEA_D3D9_SHOT = 'all'
$env:BEA_D3D9_SHOTDIR = $capDir
$env:BEA_D3D9_SHOTMAX = '2'
& $exe > $null 2>&1
Clear-ShotEnv
$rows = Get-Manifest $capDir
Check 'SHOTMAX stops the run at 2 images' `
    ($rows -and @($rows | Where-Object { $_.written -eq 1 }).Count -eq 2)

Write-Host ''
if ($fail -eq 0) { Write-Host "all checks passed. Work dir: $WorkDir" }
else { Write-Host "$fail failure(s). Work dir: $WorkDir"; exit 1 }
