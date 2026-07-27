<#
.SYNOPSIS
    Build the passive Direct3D 9 proxy (32-bit) and verify it.

.DESCRIPTION
    Refuses to produce a DLL that could crash the game at load:
      1. dumps the live system d3d9.dll export table and fails if it no longer
         matches d3d9.def (a missing forward is a startup crash);
      2. regenerates the pass-through wrapper bodies from the d3d9.h the
         compiler will actually use, so no vtable slot is hand-counted;
      3. compiles with -Werror so a wrong forwarder signature cannot link;
      4. proves the output is PE32 / i386 and re-exports all 23 ordinals.

    Output: build/d3d9.dll (never committed).
#>
[CmdletBinding()]
param(
    [string]$Zig = "$env:LOCALAPPDATA\Microsoft\WinGet\Links\zig.exe",
    [string]$Python = 'python',
    [switch]$KeepIntermediate
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$build = Join-Path $here 'build'
$gen = Join-Path $build 'gen'
$sysDll = Join-Path $env:WINDIR 'SysWOW64\d3d9.dll'

function Fail($msg) { Write-Error $msg; exit 1 }

if (-not (Test-Path $Zig)) { Fail "zig not found at $Zig" }
if (-not (Test-Path $sysDll)) { Fail "system d3d9.dll not found at $sysDll" }

New-Item -ItemType Directory -Force -Path $gen | Out-Null

# --- 1. the system DLL's exports must match what we re-export -----------------

$sysRows = & $Python (Join-Path $here 'pe_exports.py') $sysDll
if ($LASTEXITCODE -ne 0) { Fail 'pe_exports.py failed on the system d3d9.dll' }
$sysExports = @{}
foreach ($row in $sysRows) {
    if ($row.StartsWith('#')) { continue }
    $f = $row -split "`t"
    $sysExports[[int]$f[0]] = $f[1]
}

$defPath = Join-Path $here 'd3d9.def'
$defExports = @{}
foreach ($line in Get-Content $defPath) {
    if ($line -match '^\s*(\S+)\s*=\s*\S+\s*@(\d+)(\s+NONAME)?\s*$') {
        $name = if ($matches[3]) { '' } else { $matches[1] }
        $defExports[[int]$matches[2]] = $name
    }
}

$problems = @()
foreach ($ord in ($sysExports.Keys + $defExports.Keys | Sort-Object -Unique)) {
    $s = if ($sysExports.ContainsKey($ord)) { $sysExports[$ord] } else { '<absent>' }
    $p = if ($defExports.ContainsKey($ord)) { $defExports[$ord] } else { '<absent>' }
    if ($s -ne $p) { $problems += "  ordinal $ord : system='$s' proxy='$p'" }
}
if ($problems.Count -gt 0) {
    Fail ("d3d9.def no longer matches $sysDll -- update the .def AND the export table in src/proxy.c:`n" + ($problems -join "`n"))
}
Write-Host ("export table verified: {0} ordinals match {1}" -f $sysExports.Count, $sysDll)

# --- 2. generate the pass-through wrappers from the real header ---------------

# `zig env` emits ZON (not JSON) as of 0.16, so read the one field we need.
$zigEnv = (& $Zig env) -join "`n"
if ($zigEnv -notmatch '\.lib_dir\s*=\s*"([^"]+)"') { Fail 'could not read lib_dir from `zig env`' }
$zigLib = $matches[1] -replace '\\\\', '\'
$header = Join-Path $zigLib 'libc\include\any-windows-any\d3d9.h'
if (-not (Test-Path $header)) { Fail "d3d9.h not found at $header" }

& $Python (Join-Path $here 'gen_wrappers.py') $header $gen
if ($LASTEXITCODE -ne 0) { Fail 'gen_wrappers.py failed' }

# --- 3. compile ---------------------------------------------------------------

$out = Join-Path $build 'd3d9.dll'
$cc = @(
    'cc', '-target', 'x86-windows-gnu', '-shared',
    '-O2', '-std=c99',
    '-Wall', '-Wextra', '-Werror',
    '-Wno-unused-parameter',
    "-I$gen", "-I$here\src",
    '-o', $out,
    "$here\src\proxy.c", "$here\src\wrap.c", $defPath
)
Write-Host "zig $($cc -join ' ')"
& $Zig @cc
if ($LASTEXITCODE -ne 0) { Fail 'compile failed' }

# --- 4. verify the artefact ---------------------------------------------------

$outRows = & $Python (Join-Path $here 'pe_exports.py') $out
$head = $outRows[0]
if ($head -notmatch 'machine=014c') { Fail "built DLL is not i386: $head" }
if ($head -notmatch 'magic=10b') { Fail "built DLL is not PE32: $head" }

$builtExports = @{}
foreach ($row in $outRows) {
    if ($row.StartsWith('#')) { continue }
    $f = $row -split "`t"
    $builtExports[[int]$f[0]] = $f[1]
}
$missing = @()
foreach ($ord in $sysExports.Keys) {
    if (-not $builtExports.ContainsKey($ord)) { $missing += $ord }
    elseif ($builtExports[$ord] -ne $sysExports[$ord]) {
        $missing += "$ord (name '$($builtExports[$ord])' != '$($sysExports[$ord])')"
    }
}
if ($missing.Count -gt 0) { Fail ("built DLL is missing forwards: " + ($missing -join ', ')) }

if (-not $KeepIntermediate) {
    Remove-Item -Recurse -Force (Join-Path $build 'd3d9.pdb') -ErrorAction SilentlyContinue
}

$fi = Get-Item $out
Write-Host ''
Write-Host ("OK  {0}" -f $out)
Write-Host ("    {0}  {1:N0} bytes" -f $head, $fi.Length)
Write-Host ("    {0} exports, all {1} system ordinals re-exported" -f $builtExports.Count, $sysExports.Count)
Write-Host ("    sha256 {0}" -f (Get-FileHash $out -Algorithm SHA256).Hash)
