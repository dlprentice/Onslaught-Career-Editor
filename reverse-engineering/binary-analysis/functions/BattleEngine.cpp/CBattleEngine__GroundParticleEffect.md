# CBattleEngine__GroundParticleEffect

> Address: `0x0040ef20` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngine__GroundParticleEffect(void * this)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

BattleEngine ground-effect helper that samples water/terrain height, chooses the land or water particle effect, and positions the effect near the BattleEngine instance position when altitude is below the source threshold.

The current Ghidra correction supersedes the older `CMonitor__SpawnGroundOrAirImpactEffect` label. Source/decompile evidence supports `CBattleEngine::GroundParticleEffect()`.

## Evidence

- Source anchor: `CBattleEngine::GroundParticleEffect()` in `references/Onslaught/BattleEngine.cpp`.
- Read-back tokens include the water/terrain height comparison, static ground-effect resources, particle creation, and position fields around `this+0x1c..0x28`.
- Saved signature uses a `this` pointer and removes the old generic `param_1` signature.

## Boundaries

- Does not prove runtime particle behavior in a mission.
- Does not prove concrete `CBattleEngine` layout, tags, local variable names, or structure types.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
96 accepted WalkerPart Move through UpdateMouseLookAngles. This
wake landed JetPart Move `e54e2d77` — not redone. Name history
above is not rewritten. Envelope, not a 148-instruction walk.
Did not mill FUN_*. Did not implement lock sets.

Incoming-ECX `thiscall`. First insn `push -1` (SEH cookie).
`edi = ecx`. One bare `ret` at `0x0040f10f`. Body
`0x0040ef20`–`0x0040f10f` is 496 bytes, SHA-256
`e569b61cf37514b2cb460f3d605506521af21a092dfd93cab0f051d089f3fbc7`
(PE bytes; not the C1-table Ghidra digest `ed3983dd…`). Capstone:
148 insns, 4 `E8`, zero `E9`, 4 unique rel32 targets. Raw `0xE8`
byte count is 7 and is not the instruction count. Neighbour table
`CEngine__ClampBurstStartTimeFloorNow` starts at `0x0040f110`
and is not rewritten. Preceding table
`CBattleEngine__FinishedPlayingCurrentAnimation` is not
rewritten.

Pinned prologue, with `edi = ecx` and `esi = edi+0x1c`:

1. SEH frame (`push 0x005d12a8` / `fs:[0]`), then
   `sub esp, 0x24`.
2. `ecx = 0x006fadc8` / `E8`
   `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80`.
   Compare that sample to `[0x006fbdfc]`. The globals are
   **not** named here.
3. `fsub [edi+0x24]` then `fcomp [0x005d85cc]`
   (`00 00 20 41` = 10.0f). CF-clear jumps to the epilogue.
4. `fmul [0x005d8bd8]` (`00 00 c0 3f` = 1.5f). Counted, not
   contracted: `E8` `ParticleEffectLink_T3_004cb040`
   `0x004cb040`; `E8` `CParticleManager__CreateEffect`
   `0x004cb3d0`; `E8`
   `CParticleManager__RemoveOwnerLinkFromGlobalList`
   `0x004cb050`.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x0040971e` inside
already-pinned `CBattleEngine__Move` (`ecx = ebp`); `CALL` at
`0x004114b6` inside already-pinned
`CBattleEngineJetPart__Move` (`ecx = [ebx+0x18]`). Zero
encodings of imm `20 ef 40 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngine::GroundParticleEffect`
`BattleEngine.cpp:3638-3665`. Retail SEH + bare `ret` matches
zero stack args. The 10.0f / 1.5f constants match source
`altitude<10` and `altitude*1.5f`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000ef20` is not `6a ff`, **or**
`0x0000ef22` is not `68 a8 12 5d 00`, **or** `0x0000ef41` is
not `8b f9`, **or** `0x0000ef4c` is not `8d 77 1c`, **or**
`0x0000ef7a` is not `d8 1d cc 85 5d 00`, **or** `0x0000f10f`
is not `c3`, **or** `0x001d85cc` is not `00 00 20 41`, **or**
body SHA-256 is not `e569b61c…fbc7`, **or**
`tools/call_xref_scan.py` on `0x0040ef20` is not exactly those
two `CALL`s, **or** a third `.text` `E8`/`E9` to this entry
exists, **or** any encoding of imm `20 ef 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `e569b61c…fbc7`. `call_xref_scan` still two
sites. File `0x001d85cc` still `00 00 20 41`. Did not open
Ghidra. Did not edit `rebuild/**`. Did not walk the particle
callees. Did not name the water/land descriptors.

Retail entity: near-ground particle kick from Move and JetPart
Move. Stuart architecture (not proof):
`BattleEngine.cpp:3638-3665`.

Nearest reconstruction owner: **none**. Core has no
GroundParticleEffect tick. L100 card `t_aa5586e5` is on a
playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__Move` /
`CBattleEngineJetPart__Move`. Next named:
`CBattleEngine__Hit` `0x00407350` (Stuart-backed; no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040ef20` | `CBattleEngine__GroundParticleEffect` | `6aff 68a8125d00 8bf9 8d771c d81dcc855d00 … c3` (496 B) | incoming-ECX thiscall; SEH; bare ret ×1; 496 B; 4 E8 / 0 E9 / 4 targets; 2 inbound Move+JetPart. HIGH on ABI, `[+0x1c]`/`[+0x24]`, 10.0f gate, unique inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on particle descriptors or rebuild parity. |
