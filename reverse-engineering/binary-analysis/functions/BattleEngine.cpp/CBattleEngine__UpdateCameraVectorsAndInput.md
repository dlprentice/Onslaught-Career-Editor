# CBattleEngine__UpdateCameraVectorsAndInput

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Child `t_b3e2361c` REPORT.md is data —
every load-bearing pin below was re-derived from the specimen.
The Ghidra database was not opened. Cycle 95 accepted Morph
`46e8646f` and UpdateAutoAim `1a846174` — not redone. This wake
landed `c2d95f5c` WalkerPart Move — not redone. Envelope, not a
437-instruction walk. Did not mill FUN_*. Did not implement lock
sets. Historical alias `CMonitor__UpdateCameraVectorsAndInput`
is not rewritten.

> Address: `0x00407a50`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x6c`. `ebx = ecx`.
One bare `ret` at `0x004080eb`. Body `0x00407a50`–`0x004080eb`
is 1692 bytes, SHA-256
`110ed0845c15bc62d267c64460002c75da6bf0b3fbbdb2bbb0de8308d0f775e3`
(PE bytes; not the C1-table Ghidra digest `3711687f…`). Capstone:
437 insns, 9 `E8`, 3 `E9`, 6 unique rel32 targets. Raw `0xE8`
byte count is 14 and is not the instruction count. The three
`E9`s are intra-body (`0x00407d0d`, `0x00407d73`, `0x00407db8`)
and are not named. Neighbour table
`CBattleEngine__IsWalkerGroundedOrCollision` starts at
`0x004080f0` after alignment `nop`s and is not rewritten.
Preceding table `CBattleEngine__RandomizeOffsets4B8_4C0` ends
`ret 4` at `0x00407a40` and is not rewritten.

Pinned prologue, with `ebx = ecx` and `esi = ebx+0x114`:

1. Copy three dwords `[ebx+0x114]` → `[ebx+0x590]`. Those
   slots are **not** named here.
2. `mov eax, [ebx+0x260]` at `0x00407a7b` / `cmp eax, edi`
   with `edi = 2` (same WALKER=2 polarity Init already pins).
3. Walker arm: `vcall [edx+0x10c]` at `0x00407a8d`. That slot
   is **not** named here.
4. Counted, not contracted: three `E8`
   `ElapsedTime__BelowThreshold_D4` `0x00401fd0`; two `E8`
   `Vec3__SetXYZ` `0x00401ec0`; one `E8`
   `CMonitor__SampleHeightfieldNormalAtXY` `0x0047ec60`.
5. Integrate join: `E8` `CBattleEngine__UpdateMouseLookAngles`
   `0x00407540` at `0x00407ec7`. That helper is **not** walked.
6. `cmp [ebx+0x260], 3` (JET polarity Init already pins).
   `ecx = [ebx+0x57c]` / `E8` `CBattleEngineJetPart__AutoLevel`
   `0x00412900`. Then `E8`
   `Mat34__SetFromEulerAngles_004062d0` `0x004062d0`. Other of
   the 6 targets are counted, not contracted.

One inbound `.text` `E8`/`E9`: `CALL` at `0x004095d1` inside
table `CBattleEngine__Move` (already pinned), with
`mov ecx, ebp` immediately before. Zero encodings of imm
`50 7a 40 00` in the image (not a vtable slot).

Source architecture (not proof): `CBattleEngine::UpdateRotation`
`BattleEngine.cpp:1119-1234`, called from `Move` at line 1706.
Table name is a label only. Retail then calls already-pinned
`UpdateAutoAim`. Retail also inserts `E8 0x00407540` after the
integrate join; source `UpdateRotation` has no mouse-look call.
That is a topology note, not a value proof.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00007a50` is not `83 ec 6c`, **or**
`0x00007a54` is not `8b d9`, **or** `0x00007a7b` is not
`8b 83 60 02 00 00`, **or** `0x00007a8d` is not
`ff 92 0c 01 00 00`, **or** `0x00007ec7` is not
`e8 74 f6 ff ff`, **or** `0x000080eb` is not `c3`, **or** body
SHA-256 is not `110ed084…75e3`, **or**
`tools/call_xref_scan.py` on `0x00407a50` is not exactly one
`CALL` at `0x004095d1`, **or** a second `.text` `E8`/`E9` to
this entry exists, **or** any encoding of imm `50 7a 40 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `110ed084…75e3`. `call_xref_scan` still one
`CALL` at `0x004095d1`. Did not open Ghidra. Did not edit
`rebuild/**`. Did not walk all 9 callees. Did not name
`vcall +0x10c`.

Retail entity: per-frame BattleEngine orientation tick from
Move. Stuart architecture (not proof):
`BattleEngine.cpp:1119-1234`.

Nearest reconstruction owner: **none**. Core has no
UpdateRotation tick. Related, not this body:
`RetailBattleEngineInterpolation` interpolates the
`+0x114`/`+0x590` pair this prologue copies;
`RetailJetAutoLevel` is the already-mapped `0x00412900`
callee. Godot `FirstFlightWorldView.UpdateCamera` is
presentation, not Core.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement this from this mapping
until that lane names the arm. Campaign-scalar yaw-decay
observation was **not** re-derived.

Siblings: `CBattleEngine__Move` / `CBattleEngine__UpdateAutoAim`
/ `CBattleEngineWalkerPart__Move` in this tree. Next named:
`CBattleEngine__UpdateMouseLookAngles` `0x00407540` (this
body's E8 at `0x00407ec7`; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407a50` | `CBattleEngine__UpdateCameraVectorsAndInput` | `83ec6c 8bd9 8b8360020000 ff920c010000 … e874f6ffff … c3` (1692 B) | incoming-ECX thiscall; bare ret ×1; 1692 B; 9 E8 / 3 E9 / 6 targets; 1 inbound Move. HIGH on ABI, `[+0x114]`→`[+0x590]`, `[+0x260]==2`, `vcall +0x10c`, unique inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names or rebuild parity. |
