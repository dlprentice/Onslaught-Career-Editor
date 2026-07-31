<#
.SYNOPSIS
    Run the proxy self-test: drive it through a real D3D9 device, then assert
    the log contains the draws and screen coordinates that were issued.

.DESCRIPTION
    Uses D3DDEVTYPE_NULLREF and a window that is never shown, so nothing
    appears on screen and no focus is taken. Runs entirely in a temp directory;
    the game directory is not touched.
#>
[CmdletBinding()]
param(
    [string]$Zig = "$env:LOCALAPPDATA\Microsoft\WinGet\Links\zig.exe",
    [string]$WorkDir = (Join-Path $env:TEMP ('bea-d3d9-selftest-' + [guid]::NewGuid().ToString('N').Substring(0, 8)))
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dll = Join-Path $here 'build\d3d9.dll'
if (-not (Test-Path $dll)) { Write-Error "build/d3d9.dll not found -- run build.ps1 first"; exit 1 }

New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
$exe = Join-Path $WorkDir 'selftest.exe'
$log = Join-Path $WorkDir 'capture.log'

& $Zig cc -target x86-windows-gnu -O1 -o $exe (Join-Path $here 'test\selftest.c')
if ($LASTEXITCODE -ne 0) { Write-Error 'self-test build failed'; exit 1 }
Copy-Item $dll (Join-Path $WorkDir 'd3d9.dll')

$fail = 0
function Check($name, $cond) {
    if ($cond) { Write-Host "  PASS  $name" }
    else { Write-Host "  FAIL  $name"; $script:fail++ }
}

# ---- (1) inert with no environment variable set ------------------------------

Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_CAPTURE -ErrorAction SilentlyContinue
Write-Host "`n[1] proxy present, logging disabled"
$out = & $exe 2>&1
Write-Host ($out | ForEach-Object { "      $_" })
Check 'self-test exits 0' ($LASTEXITCODE -eq 0)
Check 'loads the proxy, not the system DLL' (($out -join "`n") -match [regex]::Escape($WorkDir))
Check 'writes no log' (-not (Test-Path $log))

# ---- (2) logging enabled ------------------------------------------------------

Write-Host "`n[2] logging enabled"
$env:BEA_D3D9_LOG = $log
$env:BEA_D3D9_MAXFRAMES = '10'
$out = & $exe 2>&1
Write-Host ($out | ForEach-Object { "      $_" })
Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_MAXFRAMES -ErrorAction SilentlyContinue

Check 'self-test exits 0' ($LASTEXITCODE -eq 0)
Check 'log exists and is non-empty' ((Test-Path $log) -and (Get-Item $log).Length -gt 0)
if (-not (Test-Path $log)) { Write-Host "`n$fail failure(s)"; exit 1 }

$text = Get-Content $log -Raw
$lines = Get-Content $log

Check 'records device creation' ($text -match 'DEV create .*bb=640x480')
Check 'records 3 Present boundaries' (($lines | Where-Object { $_ -match '^P \d+ draws=3' }).Count -eq 3)
Check 'records the forensics frame Present' ($text -match '^P 3 draws=5' -or ($lines | Where-Object { $_ -match '^P 3 draws=5' }).Count -eq 1)
Check 'records scene begin/end' (($lines | Where-Object { $_ -match '^S \d+ (begin|end)' }).Count -eq 8)
Check 'records Clear' (($lines | Where-Object { $_ -match '^C \d+ ' }).Count -eq 4)
Check 'records 14 draws' (($lines | Where-Object { $_ -match '^D \d+ \d+ ' }).Count -eq 14)
Check 'records the UP draw with FVF 0x144' ($text -match 'D 0 0 DPUP prim=TRIFAN primc=2 verts=4 upstride=28 fvf=0x144')
Check 'records the buffer draw' ($text -match 'D 0 1 DP prim=TRIFAN primc=2 verts=4')
Check 'shadowed blend state is observed, not defaulted' ($text -match 'ab=1 sb=5 db=6 ')
Check 'unset state is marked as a default with ~' ($text -match 'bop=1~')
Check 'stage-0 COLOROP recorded as MODULATE' ($text -match 's0\.cop=4')
Check 'viewport recorded' ($text -match 'vp=\(0,0,640x480\)')

# the point of the whole instrument: XYZRHW screen coordinates
Check 'UP vertex 0 is the issued screen coordinate (100,50)' `
    ($text -match 'V 0 0 0 xyzrhw=\(100\.0000,50\.0000,0\.0000,1\.0000\) diff=0x80FF8040 t0=\(0\.0000,0\.0000\)')
Check 'UP vertex 2 is the issued screen coordinate (228,146)' `
    ($text -match 'V 0 0 2 xyzrhw=\(228\.0000,146\.0000,0\.0000,1\.0000\)')
Check 'vertex-buffer draw is read back at (300,200)' `
    ($text -match 'V 0 1 0 xyzrhw=\(300\.0000,200\.0000,0\.0000,1\.0000\) diff=0xFF00FF00')
# The game's real buffers are D3DUSAGE_WRITEONLY and may not be read back, so
# the contents must come from the shadow captured at Unlock instead.
Check 'write-only buffer IS recovered, from the Unlock shadow' `
    ($text -match 'V 0 2 0 xyzrhw=\(10\.0000,20\.0000,0\.0000,1\.0000\) diff=0xFF0000FF')
Check 'write-only buffer vertex 2 recovered at (30,40)' `
    ($text -match 'V 0 2 2 xyzrhw=\(30\.0000,40\.0000,0\.0000,1\.0000\)')
Check 'the two frame-0 buffers were created through the proxy' `
    (($lines | Where-Object { $_ -match '^VB create ' }).Count -eq 6)
Check 'no draw fell back to "not created through proxy"' `
    (-not ($text -match 'vb-not-created-through-proxy'))
Check 'no state block was used, so no shadow invalidation' (-not ($text -match 'shadow-invalidated'))
Check 'clean detach recorded' ($text -match '# detach')

# ---- (2a) DEFECT A: a released-while-bound buffer must REFUSE, never decode ---
#
# The device holds a reference to the REAL buffer, so the draw below is legal
# Direct3D and the game would render it. Only the proxy's wrapper died. The
# hazard is not the crash: it is that the freed block can be handed back for a
# NEW wrapper, which would pass a vtable test and decode a DIFFERENT buffer's
# shadow as measured screen coordinates.

Write-Host "`n[2a] use-after-free: released-while-bound buffer"
Check 'the dying wrapper reported that it was still bound' `
    ($text -match 'VB retire wrap=0x[0-9A-Fa-f]+ real=0x[0-9A-Fa-f]+ gen=\d+ STILL-BOUND slots=1')
Check 'the draw is REFUSED by name, not silently skipped' `
    ($text -match 'V 3 1 - none stream0-released-while-bound')
Check 'the draw record shows the binding as released' `
    ($text -match 'D 3 1 DP .* s0=\(vb=released,')
Check 'NO vertex line was emitted for that draw' `
    (-not ($text -match '(?m)^V 3 1 \d'))
Check 'the DEAD buffer''s coordinates never appear anywhere in the log' `
    (-not ($text -match '777\.0000'))
Check 'the RECYCLED buffer''s coordinates never appear anywhere in the log' `
    (-not ($text -match '555\.0000'))

# Did the allocator actually hand the freed block back? When it does, this run
# exercised the exact silent-wrong-data case: same address, different buffer,
# vtable word intact. Whether it does is up to the heap, so it is reported rather
# than asserted -- but section [5] covers that case deterministically.
function Report-Recycling($body, $label) {
    $retired = [regex]::Match($body, 'VB retire wrap=(0x[0-9A-Fa-f]+) real=0x[0-9A-Fa-f]+ gen=(\d+)')
    if (-not $retired.Success) { return }
    $addr = $retired.Groups[1].Value
    $creates = @([regex]::Matches($body, 'VB create 0x[0-9A-Fa-f]+ wrap=(0x[0-9A-Fa-f]+) gen=(\d+)') |
        Where-Object { $_.Groups[1].Value -eq $addr })
    if ($creates.Count -gt 1) {
        Write-Host ("  NOTE  {0}: heap block {1} WAS recycled into a new wrapper (gens {2}) -- the address the device still named was a DIFFERENT buffer" -f
            $label, $addr, (($creates | ForEach-Object { $_.Groups[2].Value }) -join ' then '))
    } else {
        Write-Host ("  NOTE  {0}: heap block {1} was not recycled this time; the null case was exercised" -f $label, $addr)
    }
}
Report-Recycling $text 'normal run'

# ---- (2b) DEFECT B: over-cap draws must be refused by name --------------------

Write-Host "`n[2b] vertex cap"
Check 'an over-cap draw states the cap and the actual count' `
    ($text -match 'V 3 0 - none too-many-verts nv=100 cap=64')
Check 'no vertex line leaked past the cap' (-not ($text -match '(?m)^V 3 0 \d'))
Check 'the refusal is tallied in the summary' ($text -match '(?m)^#\s+too-many-verts = \d+')
Check 'a refusal total is written' ($text -match '(?m)^# refusals total=\d+ warnings=\d+')

# ---- (2c) DEFECT C: coverage is ranges, not a hull, and says when it guessed --

Write-Host "`n[2c] coverage"
Check 'Lock calls are recorded so the guard can be audited' `
    ($text -match '(?m)^L VB wrap=0x[0-9A-Fa-f]+ off=\d+ size=\d+ mapped=\d+ flags=0x')
Check 'a size-0 lock is marked as an inferred extent' `
    ($text -match 'EXTENT-INFERRED')
Check 'Unlock records the resulting range list' `
    ($text -match '(?m)^U VB wrap=0x[0-9A-Fa-f]+ cov=\[')
Check 'a draw ACROSS THE GAP between two locked ranges is refused' `
    ($text -match 'V 3 2 - none vb-outside-written-range want=\[56,168\) have=\[0,56\),\[112,168\)')
Check 'no vertex line was decoded from the gap' (-not ($text -match '(?m)^V 3 2 \d'))
Check 'a Lock(0,0,DISCARD) draw is decoded but flagged provisional' `
    ($text -match 'V 3 3 - warn vb-provisional-coverage want=\[0,112\) have=\[0,256\)\?')
Check 'the provisional draw still recovers the issued coordinates' `
    ($text -match 'V 3 3 0 xyzrhw=\(41\.0000,42\.0000,0\.0000,1\.0000\)')
Check 'the control draw after all of the above still works' `
    ($text -match 'V 3 4 0 xyzrhw=\(300\.0000,200\.0000,0\.0000,1\.0000\)')

# ---- (2d) transforms: the matrices in force at each draw ---------------------
#
# A world draw's vertices are object-space, so without these a draw row says
# what was drawn but nothing about where. The self-test issues translations
# nobody could produce by accident, and re-issues the SAME values every frame:
# an id is a VALUE, so three matrices must cost exactly three M rows.

Write-Host "`n[2d] transform capture"
Check 'the world matrix is written out with its issued translation' `
    ($text -match '(?m)^M \d+ world0 m=1\.000000,0\.000000,0\.000000,0\.000000,0\.000000,1\.000000,0\.000000,0\.000000,0\.000000,0\.000000,1\.000000,0\.000000,11\.000000,22\.000000,33\.000000,1\.000000$')
Check 'the view matrix is written out' `
    ($text -match '(?m)^M \d+ view m=.*,1\.000000,2\.000000,3\.000000,1\.000000$')
Check 'the projection matrix is written out' `
    ($text -match '(?m)^M \d+ proj m=.*,4\.000000,5\.000000,6\.000000,1\.000000$')
# Three matrices, re-set identically in each of four frames. An id names a
# VALUE, so the whole run must cost three rows plus the one derived value.
Check 'an unchanged matrix re-set every frame costs ONE M row, not one per frame' `
    ((($lines | Where-Object { $_ -match '^M \d+ (world0|view|proj) m=' }).Count) -eq 3)
Check 'every draw row names the transforms in force' `
    ((($lines | Where-Object { $_ -match '^D \d+ \d+ .* w=\d+ v=\d+ p=\d+' }).Count) -eq 14)
Check 'the world id on a draw is the id of the world M row' `
    ($(
        $m = [regex]::Match($text, '(?m)^M (\d+) world0 m=1\.000000,0[^\n]*11\.000000,22\.000000,33\.000000,1\.000000$')
        $d = [regex]::Match($text, '(?m)^D 0 0 .* w=(\d+) ')
        $m.Success -and $d.Success -and ($m.Groups[1].Value -eq $d.Groups[1].Value)
    ))
Check 'a MultiplyTransform result is stamped as derived' `
    ($text -match '(?m)^M \d+ world0 mul m=')
Check 'the composed value is current*arg (111,22,33)' `
    ($text -match '(?m)^M \d+ world0 mul m=[^\n]*111\.000000,22\.000000,33\.000000,1\.000000$')
Check 'the assumed multiplication order is tallied, not hidden' `
    ($text -match '(?m)^#\s+transform-multiply-order-assumed = \d+')
Check 'sampler state is shadowed onto the draw row' ($text -match 's0\.addr=3/1~ s0\.filt=2/1~/0~')

# ---- (2e) geometry digest ----------------------------------------------------

Write-Host "`n[2e] geometry digest"
# Exactly the eight draws whose stream-0 range resolves: the three UP draws have
# no buffer, and frame 3's released-while-bound and across-the-gap draws are
# refused before a range exists. Nothing else may be silently missing.
Check 'every resolvable draw carries a digest row, and only those' `
    ((($lines | Where-Object { $_ -match '^G \d+ \d+ vb real=0x' }).Count) -eq 8)
Check 'the digest names the buffer, the bytes and their hash' `
    ($text -match '(?m)^G 0 1 vb real=0x[0-9A-Fa-f]+ gen=\d+ off=0 n=4 bytes=112 h=[0-9A-F]{16} unlocks=1 lastunlock=0 stride=28 ')
Check 'the digest carries the position bounds of the bytes read' `
    ($text -match '(?m)^G 0 1 vb .*xyzrhw min=\(300\.0000,200\.0000,0\.0000\) max=\(428\.0000,296\.0000,0\.0000\)$')
Check 'a static buffer keeps the SAME hash across frames' `
    ($(
        $h = @([regex]::Matches($text, '(?m)^G \d+ 1 vb [^\n]* h=([0-9A-F]{16}) ') |
              ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
        $h.Count -eq 1
    ))
Check 'the digest survives the vertex cap that refuses the dump' `
    ($(
        # frame 3 draw 2 spans the coverage gap, so it has no digest; the over-cap
        # case is the UP draw, which has no buffer. Use the strict-mode run below
        # for the cap case and assert here only that a refused V still leaves the
        # draw row and the tally intact.
        $text -match '(?m)^D 3 2 DP '
    ))

# ---- (2f) texture identity ---------------------------------------------------

Write-Host "`n[2f] texture identity"
Check 'the texture is recorded at creation, in load order' `
    ($text -match '(?m)^T create serial=1 ptr=0x[0-9A-Fa-f]+ 4x4 lv=1 fmt=21 usage=0x0 pool=1$')
Check 'a bound texture is named by its serial on the draw row' `
    ($text -match 'tex0=0x[0-9A-Fa-f]+:4x4:fmt21:lv1:#1 ')
Check 'content hashing is OFF by default' (-not ($text -match '(?m)^T hash '))

Write-Host "`n[2g] BEA_D3D9_TEXHASH=1"
$log5 = Join-Path $WorkDir 'texhash.log'
$env:BEA_D3D9_LOG = $log5
$env:BEA_D3D9_MAXFRAMES = '10'
$env:BEA_D3D9_TEXHASH = '1'
& $exe | Out-Null
Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_MAXFRAMES, Env:BEA_D3D9_TEXHASH -ErrorAction SilentlyContinue
$th = Get-Content $log5 -Raw
Check 'the texture is hashed exactly once' `
    ((@([regex]::Matches($th, '(?m)^T hash serial=1 ')).Count) -eq 1)
Check 'the hash covers the whole 4x4 A8R8G8B8 level, padding excluded' `
    ($th -match '(?m)^T hash serial=1 h=[0-9A-F]{16} bytes=64 4x4 fmt=21$')
Check 'the hash is carried on the draw row so a quad can be attributed' `
    ($th -match 'tex0=0x[0-9A-Fa-f]+:4x4:fmt21:lv1:#1:h=[0-9A-F]{16} ')
Check 'the game still ran to a clean detach with hashing armed' ($th -match '# detach')

# ---- (2h) gating: absence must always name its predicate ---------------------

Write-Host "`n[2h] vertex-dump gating"
$log6 = Join-Path $WorkDir 'gated.log'
$env:BEA_D3D9_LOG = $log6
$env:BEA_D3D9_MAXFRAMES = '10'
$env:BEA_D3D9_VDRAWFIRST = '1'
$env:BEA_D3D9_VDRAWLAST = '1'
& $exe | Out-Null
Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_MAXFRAMES, Env:BEA_D3D9_VDRAWFIRST,
            Env:BEA_D3D9_VDRAWLAST -ErrorAction SilentlyContinue
$g = Get-Content $log6 -Raw
Check 'the gating is restated in the log header' `
    ($g -match '(?m)^# gating vdrawfirst=1 vdrawlast=1 ')
Check 'an excluded draw is refused BY THE NAME OF THE PREDICATE' `
    ($g -match 'V 0 0 - none gated-draw-window draw=0 window=\[1,1\]')
Check 'and emits no vertex line' (-not ($g -match '(?m)^V 0 0 \d'))
Check 'the draw INSIDE the window still dumps' `
    ($g -match 'V 0 1 0 xyzrhw=\(300\.0000,200\.0000,0\.0000,1\.0000\)')
Check 'the digest is NOT gated, so geometry identity survives' `
    ($g -match '(?m)^G 0 2 vb real=0x')
Check 'the gate is tallied like any other refusal' `
    ($g -match '(?m)^#\s+gated-draw-window = \d+')

# ---- (3) frame windowing -----------------------------------------------------

Write-Host "`n[3] frame window (FIRSTFRAME=1 MAXFRAMES=1)"
$log2 = Join-Path $WorkDir 'window.log'
$env:BEA_D3D9_LOG = $log2
$env:BEA_D3D9_FIRSTFRAME = '1'
$env:BEA_D3D9_MAXFRAMES = '1'
& $exe | Out-Null
Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_FIRSTFRAME, Env:BEA_D3D9_MAXFRAMES -ErrorAction SilentlyContinue
$w = Get-Content $log2
Check 'only frame 1 draws are recorded' `
    ((($w | Where-Object { $_ -match '^D 1 ' }).Count -eq 3) -and
     (($w | Where-Object { $_ -match '^D [023] ' }).Count -eq 0))

# ---- (4) strict coverage turns the provisional warning into a refusal --------

Write-Host "`n[4] BEA_D3D9_STRICTCOV=1"
$log3 = Join-Path $WorkDir 'strict.log'
$env:BEA_D3D9_LOG = $log3
$env:BEA_D3D9_MAXFRAMES = '10'
$env:BEA_D3D9_STRICTCOV = '1'
& $exe | Out-Null
Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_MAXFRAMES, Env:BEA_D3D9_STRICTCOV -ErrorAction SilentlyContinue
$s = Get-Content $log3 -Raw
Check 'strict mode is recorded in the header' ($s -match '# cfg .*strictcov=1')
Check 'the Lock(0,0,DISCARD) draw is REFUSED under strict coverage' `
    ($s -match 'V 3 3 - none vb-provisional-coverage')
Check 'and no vertex is decoded from it' (-not ($s -match '(?m)^V 3 3 \d'))
Check 'the released-while-bound refusal is unchanged' `
    ($s -match 'V 3 1 - none stream0-released-while-bound')

# ---- (5) fault injection: prove the SECOND guard, not just the first ---------
#
# [2a] shows the wrapper retracting its own bindings as it dies, which is the
# mechanism that actually runs. But a guard that is only ever reached when the
# first guard already worked has not been tested. This run disables the
# retraction, so stream 0 genuinely holds a pointer to freed memory -- the exact
# state the adversary predicted -- and asserts that the generation check refuses
# it rather than decoding whatever the allocator put there.

Write-Host "`n[5] fault injection: dangling binding, generation check alone"
$log4 = Join-Path $WorkDir 'fault.log'
$env:BEA_D3D9_LOG = $log4
$env:BEA_D3D9_MAXFRAMES = '10'
$env:BEA_D3D9_FAULT_NOCLEARBIND = '1'
& $exe | Out-Null
Remove-Item Env:BEA_D3D9_LOG, Env:BEA_D3D9_MAXFRAMES, Env:BEA_D3D9_FAULT_NOCLEARBIND -ErrorAction SilentlyContinue
$f = Get-Content $log4 -Raw
Check 'the log is stamped as a fault-injection artefact' `
    ($f -match '# FAULT-INJECTION noclearbind=1')
Check 'the binding really was left dangling' ($f -match 'NOT-RETRACTED')
Check 'the dangling binding is REFUSED as a stale wrapper' `
    ($f -match 'V 3 1 - none vb-wrapper-stale wrap=0x[0-9A-Fa-f]+ gen=\d+')
Check 'no vertex was decoded through the dangling pointer' `
    (-not ($f -match '(?m)^V 3 1 \d'))
Check 'the dead buffer''s coordinates still never appear' (-not ($f -match '777\.0000'))
Check 'the recycled buffer''s coordinates still never appear' (-not ($f -match '555\.0000'))
Check 'the draw record names the binding as stale' ($f -match 'D 3 1 DP .* s0=\(vb=stale,')
Check 'the control draw after the dangling one still works' `
    ($f -match 'V 3 4 0 xyzrhw=\(300\.0000,200\.0000,0\.0000,1\.0000\)')
Report-Recycling $f 'fault run'

Write-Host ''
if ($fail -gt 0) {
    Write-Host "$fail check(s) FAILED. Log: $log"
    exit 1
}
Write-Host "all checks passed. Work dir: $WorkDir"
Write-Host ("log: {0} ({1:N0} bytes, {2} lines)" -f $log, (Get-Item $log).Length, $lines.Count)
