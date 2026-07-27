# SPDX-License-Identifier: GPL-3.0-or-later
#
# Controlled copied-runtime observation of the lower-right battleline instrument's
# portrait/noise composition.
#
# Static reading of 0x00487d10 CHud__RenderBattleline and 0x004b82b0 (the message
# object's portrait pass) says the portrait quad is issued SIX times per frame with a
# computed diffuse DWORD, and the noise quad once with another computed diffuse. Both
# diffuse values are register-computed, so they cannot be read off the image; and the
# blend they are composited under is a cached render state. This probe reads all of
# them at the instruction that issues the draw.
#
# Why the render-state SHADOW is authoritative here, unlike the mesh-lighting probe:
# 0x00513bc0 RenderState_Set is NOT deferred. It writes DAT_00855540[state] and then
# immediately CALLs the device through vtbl+0xe4 in the same body (0x00513bc0-
# 0x00513c12). The shadow is therefore write-through to the device, and reading it at
# a draw call site reads what the device has.
#
#   0x00855540 + state*4
#     0x0085555c  D3DRS_ZENABLE (0x07)          0x00855578  D3DRS_ZWRITEENABLE (0x0e)
#     0x0085557c  D3DRS_ALPHATESTENABLE (0x0f)  0x0085558c  D3DRS_SRCBLEND (0x13)
#     0x00855590  D3DRS_DESTBLEND (0x14)        0x0085559c  D3DRS_ZFUNC (0x17)
#     0x008555ac  D3DRS_ALPHABLENDENABLE (0x1b)
#
# Texture stage state shadow is 0x008557f0 + (type + stage*0n30)*4, so stage 0 type 1
# ("colour op", the slot 0x00555c17 in CVBufTexture__DrawSpriteEx tests against 5) is
# 0x008557f4. NOTE that 0x00513930 - the raw setter both 0x00482090 and 0x004b82b0
# use - does NOT update that shadow, so it is printed only as context, never as proof.
#
# CVBufTexture__DrawSpriteEx (0x00555be0) is cdecl with 15 dwords. At the CALL:
#   esp+0x00 x   esp+0x04 y   esp+0x08 z    esp+0x0c texture  esp+0x10 anchor
#   esp+0x14 uvmode esp+0x18 ?  esp+0x1c ?  esp+0x20 DIFFUSE  esp+0x24 wscale
#   esp+0x28 hscale esp+0x2c u0 esp+0x30 u1 esp+0x34 v0       esp+0x38 v1
#
# HARD RULES inherited from tools/cdb_meshmode_probe.ps1: copied target only, never
# the Steam install, never pristine BEA.exe, breakpoints and memory reads only.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RunName,

    # Gate is CHud__RenderBattleline's entry: exactly one hit per in-level frame.
    [string]$GateVa = '0x00487d10',
    [int]$GateFrame = 240,

    # The observation sites only fire while a message is playing, so the window is
    # deliberately long; -MaxHits is what actually ends the burst.
    [int]$GateWindowFrames = 1800,
    [int]$MaxHits = 420
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repo  = [IO.Path]::GetFullPath("$PSScriptRoot\..")
$drive = Join-Path $repo 'local-lab\cockpit-worldmatrix-2026-07-26\Drive-RunningRetail.ps1'
$probe = Join-Path $repo 'tools\cdb_meshmode_probe.ps1'

$runDir = Join-Path $repo "local-lab\portrait-battleline-2026-07-26\$RunName"
$null = [IO.Directory]::CreateDirectory($runDir)

$states = '.printf "    rs zen=%d zwrite=%d atest=%d src=%d dst=%d zfunc=%d ablend=%d tss0op=%x\n", poi(0x85555c), poi(0x855578), poi(0x85557c), poi(0x85558c), poi(0x855590), poi(0x85559c), poi(0x8555ac), poi(0x8557f4)'

$sites = @(
    @{ Id = 1; Va = '0x004b8697'; Commands = @(
        '.printf "PORTRAIT diffuse=%08x tex=%p z=%08x anchor=%d w=%08x h=%08x u0=%08x u1=%08x v0=%08x v1=%08x x=%08x y=%08x\n", poi(@esp+0x20), poi(@esp+0xc), poi(@esp+8), poi(@esp+0x10), poi(@esp+0x24), poi(@esp+0x28), poi(@esp+0x2c), poi(@esp+0x30), poi(@esp+0x34), poi(@esp+0x38), poi(@esp), poi(@esp+4)',
        $states) },
    @{ Id = 2; Va = '0x004b8781'; Commands = @(
        '.printf "NOISE    diffuse=%08x tex=%p z=%08x anchor=%d w=%08x h=%08x u0=%08x u1=%08x v0=%08x v1=%08x\n", poi(@esp+0x20), poi(@esp+0xc), poi(@esp+8), poi(@esp+0x10), poi(@esp+0x24), poi(@esp+0x28), poi(@esp+0x2c), poi(@esp+0x30), poi(@esp+0x34), poi(@esp+0x38)',
        $states) }
    # The darkener (0x00487e4d), z-mask (0x00487f18) and outline (0x00487fe7) quads
    # carry PUSH-immediate diffuse DWORDs (0x7fffffff, 0xffffffff, 0xff6f8faf) that
    # are already decodable from the image, and they fire on every frame including
    # message gaps. They are deliberately NOT instrumented so the whole -MaxHits
    # budget is spent on frames that actually carry a portrait.
)

$info = & $probe `
    -GateVa $GateVa -GateFrame $GateFrame -GateWindowFrames $GateWindowFrames `
    -MaxHits $MaxHits -Sites $sites `
    -GateDumpCommands @(
        '.printf "  ARM: msgobj=%p msg=%p\n", poi(0x8a9d84), poi(poi(0x8a9d84)+8)',
        '.printf "  render state block 0x855540 L20:\n"', 'dd 0x855540 L20',
        '.printf "  texture stage 0 block 0x8557f0 L8:\n"', 'dd 0x8557f0 L8') `
    -ScratchDirectory $runDir `
    -LogPath (Join-Path $runDir 'cdb.log')

$info | Format-List | Out-String | Write-Host

& $drive -ProcessId $info.TargetPid -LogPath (Join-Path $runDir 'drive.log') -Steps `
  'wait 73,79,94 15 60','click 320,240','wait 35,37,60 20 40','sleep 1', `
  'click 219,304','wait 30,32,48 8 30','sleep 2', `
  'click 618,450','wait 31,32,55 3 30','sleep 3', `
  'click 618,450','wait 56,61,85 4 40','sleep 3', `
  'click 618,450','wait 59,68,95 4 40','sleep 3', `
  'click 618,450','wait 107,115,125 6 60','leave 107,115,125 8 120'

Write-Host "in level; waiting for the debugger to finish its window..."
$log = $info.LogPath
$deadline = (Get-Date).AddSeconds(600)
while ((Get-Date) -lt $deadline) {
    $p = Get-Process -Id $info.DebuggerPid -ErrorAction SilentlyContinue
    if (-not $p) { break }
    if ((Test-Path -LiteralPath $log) -and
        (Select-String -LiteralPath $log -SimpleMatch 'ALLDONE' -Quiet)) {
        Start-Sleep -Seconds 2
        Write-Host "ALLDONE seen in log; stopping the debugger."
        Stop-Process -Id $info.DebuggerPid -Force -ErrorAction SilentlyContinue
        break
    }
    Start-Sleep -Milliseconds 500
}
Get-Process -Name BEA -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -ieq (Join-Path $info.TargetRoot 'BEA.exe') } |
    Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "done; log at $log"
