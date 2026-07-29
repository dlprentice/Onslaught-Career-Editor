[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\build\bea-ttd-symbols')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
    throw "vswhere.exe was not found at $vswhere"
}
$installation = (& $vswhere -all -prerelease -latest -property installationPath |
    Select-Object -First 1).Trim()
if (-not $installation) {
    throw 'No complete Visual Studio installation was found.'
}
$vsDevCmd = Join-Path $installation 'Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path -LiteralPath $vsDevCmd -PathType Leaf)) {
    throw "VsDevCmd.bat was not found at $vsDevCmd"
}

$source = Join-Path $PSScriptRoot 'bea_ttd_symbols.cpp'
$exports = Join-Path $PSScriptRoot 'bea_ttd_symbols.def'
$out = [System.IO.Path]::GetFullPath($OutputDirectory)
[System.IO.Directory]::CreateDirectory($out) | Out-Null
$dll = Join-Path $out 'bea_ttd_symbols.dll'
$pdb = Join-Path $out 'bea_ttd_symbols.pdb'
$obj = Join-Path $out 'bea_ttd_symbols.obj'
$importLibrary = Join-Path $out 'bea_ttd_symbols.lib'

$command = @(
    "call `"$vsDevCmd`" -arch=x86 -host_arch=x64 >nul &&"
    'cl.exe /nologo /std:c++20 /EHsc /W4 /WX /O2 /MD /LD /Brepro'
    "`"/Fo$obj`" `"/Fd$pdb`""
    "`"$source`""
    '/link'
    '/Brepro'
    "`"/DEF:$exports`" `"/OUT:$dll`""
    "`"/IMPLIB:$importLibrary`" `"/PDB:$pdb`""
    'dbgeng.lib'
) -join ' '

& $env:COMSPEC /d /s /c $command
if ($LASTEXITCODE -ne 0) {
    throw "x86 extension build failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path -LiteralPath $dll -PathType Leaf)) {
    throw "Build reported success but did not create $dll"
}

$hash = (Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash
$item = Get-Item -LiteralPath $dll
[pscustomobject]@{
    Dll = $item.FullName
    Bytes = $item.Length
    SHA256 = $hash
    Architecture = 'x86'
    VisualStudio = $installation
}
