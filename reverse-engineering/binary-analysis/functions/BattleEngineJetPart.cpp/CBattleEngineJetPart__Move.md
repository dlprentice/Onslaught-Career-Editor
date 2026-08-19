# CBattleEngineJetPart__Move

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x00410c50` | Prior saved Ghidra name: `CMonitor__UpdateMovementTransitionAndEffects`

## Status

- Current static owner/source identity: high confidence
- Saved live Ghidra correction: applied and exactly read back on 2026-07-13
- Copied-runtime behavior proof: pending

## Static Basis

`CBattleEngine__Move` calls this body through the JetPart stored at BattleEngine
`+0x57c`; initialization and constructor evidence independently establish that
object relationship and the JetPart main-part backpointer at `+0x18`. The body
sequence matches Stuart's JetPart movement method across energy use, engine
state, stall/morph, ground effect, flight motion, auto-return, shield clearing,
particle effects, and skimming.

See [the 2026-07-12 movement crosswalk](../../battleengine-movement-static-crosswalk-2026-07-12.md)
for the complete child-helper map and non-claims.

## Boundaries

- The corrected live Ghidra owner, rendered signature parameter, and comment
  match this page.
- Source constants remain hypotheses until copied-runtime measurement.
- This does not establish authentic handling, timing, camera, animation,
  presentation, or rebuild parity.
- No executable or installed-game file was changed.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed WalkerPart Move `c2d95f5c`, UpdateCamera `cdaa415d`,
and UpdateMouseLookAngles `a6faa8a4` — not redone. Cycle 95
accepted Morph and UpdateAutoAim — not redone. Name-correction
history above is not rewritten. Envelope, not a 635-instruction
walk. Did not mill FUN_*. Did not implement lock sets.

Incoming-ECX `thiscall`. First insn `sub esp, 0x94`. `ebx = ecx`.
One bare `ret` at `0x004114ca`. Body `0x00410c50`–`0x004114ca`
is 2171 bytes, SHA-256
`0de35d19b47b1f11bd70b4c16313db461247c1232eb2c1a77a9bd91634b97484`
(PE bytes; not the C1-table Ghidra digest `f1df0226…`). Capstone:
635 insns, 8 `E8`, 2 `E9`, 9 unique rel32 targets. Raw `0xE8`
byte count is 9 and is not the instruction count. The two `E9`s
are intra-body (`0x00411066`, `0x0041114e`) and are not named.
Neighbour table `CBattleEngineJetPart__Gravity` starts at
`0x004114d0` after alignment `nop`s and is not rewritten.
Preceding table `CBattleEngineJetPart__YawRight` is not
rewritten.

Pinned prologue, with `ebx = ecx` and `ebp = 0`:

1. `eax = [ebx+0x18]` (already-cited JetPart main-part
   backpointer). `eax = [eax+0x574]`. Nonzero increments
   `[eax+0x40]`. The stat slot is **not** named here.
2. Counted list walk on `[ebx]` / `[ebx+8]` calling table
   `CMonitor__UpdateTrackedRenderPair` `0x005078f0` with
   push 1. That table name is **not** adopted as
   `MoveEmitter`.
3. Two `E8` `CBattleEngine__Morph` `0x0040a580` (already
   pinned). Counted, not contracted: `E8`
   `CBattleEngineJetPart__HandleGroundEffect` `0x00411630`;
   `E8` `CBattleEngineJetPart__GetFriction` `0x00411aa0`
   (existing Gen31 `REBUILD_READY` callee — not re-derived);
   `E8` `CBattleEngine__GroundParticleEffect` `0x0040ef20`;
   `E8` `CBattleEngineJetPart__HandleSkimming` `0x00411500`.
   Other of the 9 targets are counted, not contracted.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00408d61` inside
already-pinned `CBattleEngine__Move`, with
`ecx = [ebp+0x57c]` — the jet-part slot Init already stores.
Zero encodings of imm `50 0c 41 00` in the image (not a
vtable slot).

Source architecture (not proof): `CBattleEngineJetPart::Move`
`BattleEngineJetPart.cpp:305+`. Retail bare `ret` matches zero
stack args. `IncStat` / `MoveEmitter(TRUE)` match the
`+0x574` increment and the push-1 list walk.

Rebuild mapping: `PARTIAL_CONTRACT` (named; existing GetFriction
row is a callee). See the section below. Do not implement Core
from this RE root.

Cheapest falsifier: file `0x00010c50` is not `81 ec 94 00 00 00`,
**or** `0x00010c57` is not `8b d9`, **or** `0x00010c5c` is not
`8b 43 18`, **or** `0x00010c69` is not `ff 40 40`, **or**
`0x000114ca` is not `c3`, **or** body SHA-256 is not
`0de35d19…7484`, **or** `tools/call_xref_scan.py` on
`0x00410c50` is not exactly one `CALL` at `0x00408d61`, **or**
a second `.text` `E8`/`E9` to this entry exists, **or** any
encoding of imm `50 0c 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `0de35d19…7484`. `call_xref_scan` still one Move
site. Did not open Ghidra. Did not edit `rebuild/**`. Did not
walk all 8 callees. Did not name `[+0x40]` or redo GetFriction.

Retail entity: per-frame jet-part Move from the already-pinned
`CBattleEngine__Move` `[+0x57c]` site. Stuart architecture (not
proof): `BattleEngineJetPart.cpp:305+`.

Nearest reconstruction owner: **existing** jet energy / friction
path (`SimulationConstants` air-energy cost;
`CBattleEngineJetPart__GetFriction` is already Gen31
`REBUILD_READY`). Not a new owner. This envelope does not raise
that callee. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement from this mapping until
that lane names the arm.

Siblings: `CBattleEngine__Move` / `CBattleEngine__Morph` /
`CBattleEngineWalkerPart__Move`. Next named:
`CBattleEngine__GroundParticleEffect` `0x0040ef20` (Move tail
and this body; July identity note; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00410c50` | `CBattleEngineJetPart__Move` | `81ec94000000 8bd9 8b4318 ff4040 … c3` (2171 B) | incoming-ECX thiscall; bare ret ×1; 2171 B; 8 E8 / 2 E9 / 9 targets; 1 inbound Move `[+0x57c]`. HIGH on ABI, `[+0x18]`/`[+0x574]` increment, unique inbound. Mapping `PARTIAL_CONTRACT`; existing GetFriction callee only. **Not** on stall/morph values or rebuild parity. |
