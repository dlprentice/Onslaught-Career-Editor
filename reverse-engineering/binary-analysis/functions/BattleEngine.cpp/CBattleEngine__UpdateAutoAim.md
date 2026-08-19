# CBattleEngine__UpdateAutoAim

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
94 accepted Init `9a0035f5` and Move `934efc5c` — not redone. This
wake landed `46e8646f` Morph — not redone. Envelope, not a
392-instruction walk. Did not mill FUN_*. Did not implement lock
sets.

> Address: `0x0040b120`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x78`. One bare
`ret` at `0x0040b651`. Body `0x0040b120`–`0x0040b651` is 1330
bytes, SHA-256
`820ff9324f592f58f55924b1baedd761ffe6a93602b42fe6deefc7907346dda8`.
Capstone: 392 insns, 14 `E8`, 2 `E9`, 7 unique rel32 targets.
Raw `0xE8` byte count is 18 and is not the instruction count.
The two `E9`s are intra-body (`0x0040b5f1`, `0x0040b5f7`) and
are not named. Neighbour table `AngleDifference` starts at
`0x0040b660` and is not rewritten. Preceding table
`CGeneralVolume__ctor_base` ends at `0x0040b113` and is not
rewritten. Following table `CBattleEngine__HandleAutoAim` at
`0x0040b6d0` is already pinned and is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `mov eax, [esi]` / `call dword [eax+0x1d4]`. That vcall is
   the same slot HandleAutoAim uses and is **not** named here.
2. Copy `[esi+0x114]` / `[esi+0x118]` onto the stack. Store
   `[esi+0x504]` → `[esi+0x50c]` and `[esi+0x500]` →
   `[esi+0x508]`.
3. `ecx = [esi+0x4e0]`. Zero jumps to the late epilogue. Nonzero
   tests `[ecx+0x34] bit 4` then either `vcall [edx+0x168]` or
   `E8` `CThing__GetCentrePos` `0x004f3ac0`. The `[esi+0x4e0]`
   field is **not** named here.
4. Counted, not contracted: eight `E8` `Vec3__SetXYZ`
   `0x00401ec0`; two `E8` `Vec3__Magnitude` `0x004026b0`; one
   `E8` `AngleDifference` `0x0040b660`; two `E8`
   `CRT__AcosDispatch_ST0` `0x0055dcb0`. Other of the 7 targets
   are counted, not contracted.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00409637` inside
table `CBattleEngine__Move` (already pinned). Zero encodings of
imm `20 b1 40 00` in the image (not a vtable slot).

Source architecture (not proof): `CBattleEngine::UpdateAutoAim`
`BattleEngine.cpp:2366-2445`. `GetCurrentWeapon()` is the
opening source call; retail `vcall +0x1d4` is not adopted as
that name. Retail bare `ret` matches zero stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000b120` is not `83 ec 78`, **or**
`0x0000b125` is not `8b f1`, **or** `0x0000b12a` is not
`ff 90 d4 01 00 00`, **or** `0x0000b168` is not
`0f 84 77 04 00 00`, **or** `0x0000b651` is not `c3`, **or**
body SHA-256 is not `820ff932…dda8`, **or**
`tools/call_xref_scan.py` on `0x0040b120` is not exactly one
`CALL` at `0x00409637`, **or** a second `.text` `E8`/`E9` to
this entry exists, **or** any encoding of imm `20 b1 40 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `820ff932…dda8`. `call_xref_scan` still one
`CALL` at `0x00409637`. Did not open Ghidra. Did not edit
`rebuild/**`. Did not walk all 14 callees. Did not name vcall
`+0x1d4` or `[this+0x4e0]`.

Retail entity: per-frame auto-aim tick from Move. Distinct from
already-pinned `CBattleEngine__HandleAutoAim` (Init + HandleEvent
inbound). Stuart architecture (not proof):
`BattleEngine.cpp:2366-2445`.

Nearest reconstruction owner: **none**. Core has no auto-aim
tick.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement this from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__HandleAutoAim` /
`CBattleEngine__Move` in this folder. Next named:
`CBattleEngine__UpdateCameraVectorsAndInput` `0x00407a50`
(Move callee; no function note; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040b120` | `CBattleEngine__UpdateAutoAim` | `83ec78 8bf1 ff90d4010000 … 0f8477040000 … c3` (1330 B) | incoming-ECX thiscall; bare ret ×1; 1330 B; 14 E8 / 2 E9 / 7 targets; 1 inbound Move. HIGH on ABI, `vcall +0x1d4`, `[+0x4e0]` null gate, unique inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on weapon/target field names or rebuild parity. |
