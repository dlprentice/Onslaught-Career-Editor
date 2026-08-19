# CBattleEngine__Move

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x004081c0` | Prior saved Ghidra name: `CMonitor__Process`

## Status

- Current static owner/source identity: high confidence
- Saved live Ghidra correction: applied and exactly read back on 2026-07-13
- Copied-runtime behavior proof: pending

## Static Basis

The `CBattleEngine` RTTI vtable at `0x005d89c4` points to this body from slot 66
at `0x005d8acc`. Neighboring slots resolve to known BattleEngine methods. The
body uses BattleEngine state and WalkerPart/JetPart fields, dispatches both
movement parts, and reaches BattleEngine and actor movement helpers in the same
broad order as Stuart's `CBattleEngine::Move` source.

See [the 2026-07-12 movement crosswalk](../../battleengine-movement-static-crosswalk-2026-07-12.md)
for the complete evidence and non-claims.

## Boundaries

- The corrected live Ghidra name/signature/comment match this page.
- The metadata correction does not prove exact field types or retail runtime
  behavior.
- Static identity does not prove retail timing, values, camera, controls, or
  gameplay behavior.
- No executable or installed-game file was changed.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed `9a0035f5` Init — not redone. Cycle 93 accepted
HandleLocks through HandleAutoAim — not redone. Name-correction
history above is not rewritten. This is an envelope, not a
1487-instruction walk. Did not mill FUN_*. Did not implement
lock sets.

Incoming-ECX `thiscall`. First insn `push -1` (SEH cookie). One
bare `ret` at `0x00409751`. Body `0x004081c0`–`0x00409751` is
5522 bytes, SHA-256
`6ea00887045c25292f9830e1b2262230979614b616093f0f6453afbcf4493f0a`.
Capstone: 1487 insns, 63 `E8`, 3 `E9`, 43 unique rel32 targets.
Raw `0xE8` byte count is 65 and is not the instruction count.
The three `E9`s are intra-body to `0x00408d75` and are not
named. Neighbour table `LinkedPtrCursor__MoveFirstAndGet`
starts at `0x00409760` after alignment `nop`s and is not
rewritten. Preceding table
`CBattleEngine__ProcessStateSwapAndDeathChecks` ends at
`0x004081b0` and is not rewritten.

Pinned prologue:

1. SEH frame (`push 0x005d122b` / `fs:[0]`), then
   `sub esp, 0x23c`. `ebp = ecx`.
2. `lea edi, [ebp+0x250]` / `E8`
   `LinkedPtrCursor__MoveFirstAndGet` `0x00409760` at
   `0x004081ef`. That list walk is counted, not contracted.
3. `cmp [ebp+0x260], 3` at `0x0040841d` (same JET polarity
   Init already pins). Walker part loaded from `[ebp+0x578]`;
   jet from `[ebp+0x57c]` — same slots Init stores.
4. `mov ecx, ebp` / `E8` `CBattleEngine__HandleLocks`
   `0x00406560` at `0x00408b84` — the unique inbound already
   pinned on `9ced05c0`. Immediately after:
   `mov eax, [ebp+0x260]` / `cmp eax, 3`.
5. Two `E8` `CBattleEngineWalkerPart__Move` `0x00413760` at
   `0x00408c4b` / `0x00408c83`. One `E8`
   `CBattleEngineJetPart__Move` `0x00410c50` at `0x00408d61`.
   One `E8` `CBattleEngine__Morph` `0x0040a580` at
   `0x00408d70`. Tail counts (not contracted):
   `CBattleEngine__UpdateCameraVectorsAndInput` `0x00407a50`
   at `0x004095d1`; `CBattleEngine__UpdateAutoAim`
   `0x0040b120` at `0x00409637` (not HandleAutoAim);
   `CBattleEngine__GroundParticleEffect` `0x0040ef20` at
   `0x0040971e`. Other of the 43 targets are counted, not
   contracted.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`c0 81 40 00`: file `0x001d8acc` / VA `0x005d8acc` (vtable
slot 66, `+0x108` from the `CBattleEngine` vtable base
`0x005d89c4` named by HandleEvent). Neighbouring dwords are
**not** this proof.

Source architecture (not proof): `CBattleEngine::Move`
`BattleEngine.cpp:1270-1762`. `HandleLocks()` is source
line 1476. Retail bare `ret` matches zero stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000081c0` is not `6a ff`, **or**
`0x000081c2` is not `68 2b 12 5d 00`, **or** `0x000081dd` is
not `8b e9`, **or** `0x0000841d` is not
`83 bd 60 02 00 00 03`, **or** `0x00008b84` is not
`e8 d7 d9 ff ff`, **or** `0x00009751` is not `c3`, **or**
body SHA-256 is not `6ea00887…3f0a`, **or**
`tools/call_xref_scan.py` on `0x004081c0` is not empty, **or**
`0x001d8acc` is not `c0 81 40 00`, **or** a second encoding
of that imm exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `6ea00887…3f0a`. `call_xref_scan` still empty.
File `0x001d8acc` still `c0 81 40 00`. Did not open Ghidra. Did
not edit `rebuild/**`. Did not walk all 63 callees.

Retail entity: `CBattleEngine` vtable slot-66 per-frame Move,
including the already-pinned HandleLocks call. Stuart
architecture (not proof): `BattleEngine.cpp:1270-1762`.

Nearest reconstruction owner: **none**. Core has no BattleEngine
Move tick and no `+0x578`/`+0x57c` part dispatch.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement this from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__HandleLocks` /
`CBattleEngine__Init` in this folder. Next named:
`CBattleEngine__Morph` `0x0040a580` (historical alias note
only; no 2026-08-19 PE envelope; Move callee).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004081c0` | `CBattleEngine__Move` | `6aff 682b125d00 … 8be9 … 83bd6002000003 … e8d7d9ffff … c3` (5522 B) | incoming-ECX thiscall; SEH; bare ret ×1; 5522 B; 63 E8 / 3 E9 / 43 targets; 0 inbound; unique vtable slot 66 at `0x005d8acc`. HIGH on ABI, `+0x260==3` arm, `+0x578`/`+0x57c` part loads, HandleLocks site. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on camera/sound/morph parity or rebuild. |
