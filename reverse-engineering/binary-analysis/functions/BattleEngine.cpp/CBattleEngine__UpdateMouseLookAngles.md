# CBattleEngine__UpdateMouseLookAngles

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed `c2d95f5c` WalkerPart Move and `cdaa415d` UpdateCamera
— not redone. Cycle 95 accepted Morph and UpdateAutoAim — not
redone. Envelope, not a 273-instruction walk. Did not mill FUN_*.
Did not implement lock sets. Historical alias
`CGame__UpdateMouseLookAngles` is not rewritten.

> Address: `0x00407540`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [0x00662df4]`.
`ebx = ecx` at `0x0040754c`. One bare `ret` at `0x00407939`.
Body `0x00407540`–`0x00407939` is 1018 bytes, SHA-256
`04e4b1d0317e5a64fe7956c274e0bd5ef48035c636cda7e62195cbf078a79256`
(PE bytes; not the C1-table Ghidra digest `352fae91…`). Capstone:
273 insns, 12 `E8`, zero `E9`, 7 unique rel32 targets. Raw `0xE9`
byte count is 7 and is not the instruction count. Neighbour table
`CBattleEngine__RandomizeOffsets4B8_4C0` starts at `0x00407940`
after alignment `nop`s and is not rewritten. Preceding table
`CBattleEngine__Gravity` ends at `0x0040751e` and is not
rewritten.

Pinned prologue, with `ebx = ecx`:

1. `[0x00662df4] != 0` jumps to the epilogue. That global is
   **not** named here.
2. `[0x008a9ac4] != 0` same early-out. `cmp [0x008a9ac0], 3`
   at `0x00407579` — already-closed `EGameState`; value 3 is
   PLAYING in the IScript note. Other values early-out.
3. `test [ebx+0x2c], 4` and `[ebx+0x580] == 0` both early-out.
   Those fields are **not** named here.
4. `cmp [ebx+0x260], 2` at `0x0040759e` (same WALKER=2 polarity
   Init already pins). Non-2 early-out.
5. `vcall [edx+0x10c]` at `0x004075c7` — same slot UpdateCamera
   already counts and is **not** named here.
6. `fstp [ebx+0x114]` at `0x0040762c` after
   `fsubr [ebx+0x114]`. `fstp [ebx+0x118]` at `0x0040767a` /
   `0x0040768a`. Those slots are **not** named here.
7. Counted, not contracted: two `E8`
   `PLATFORM__GetWindowWidth` `0x00515940`; two `E8`
   `PLATFORM__GetWindowHeight` `0x00515b00`; three `E8`
   `Vec3__SetXYZ` `0x00401ec0`. Other of the 7 targets are
   counted, not contracted.

Four inbound `.text` `E8`/`E9`: `CALL` at `0x00407ec7` inside
already-pinned `CBattleEngine__UpdateCameraVectorsAndInput`;
three `CALL`s inside table `CGame__Render` (`0x0046e650`,
`0x0046e662`, `0x0046e85a`) after `ecx = [[…]+0x1c]`. Zero
encodings of imm `40 75 40 00` in the image (not a vtable slot).

Source architecture (not proof): no Stuart
`UpdateMouseLookAngles` method. Retail is a thiscall helper
called from UpdateRotation's retail sibling and from Render.
Retail bare `ret` matches zero stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00007540` is not `a1 f4 2d 66 00`,
**or** `0x00007545` is not `83 ec 7c`, **or** `0x0000754c` is
not `8b d9`, **or** `0x00007579` is not
`83 3d c0 9a 8a 00 03`, **or** `0x0000759e` is not
`83 bb 60 02 00 00 02`, **or** `0x0000762c` is not
`d9 9b 14 01 00 00`, **or** `0x00007939` is not `c3`, **or**
body SHA-256 is not `04e4b1d0…9256`, **or**
`tools/call_xref_scan.py` on `0x00407540` is not exactly those
four `CALL`s, **or** a fifth `.text` `E8`/`E9` to this entry
exists, **or** any encoding of imm `40 75 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `04e4b1d0…9256`. `call_xref_scan` still four
sites. Did not open Ghidra. Did not edit `rebuild/**`. Did not
walk all 12 callees. Did not name `vcall +0x10c` or the look
delta.

Retail entity: mouse-look helper writing BattleEngine
`+0x114`/`+0x118` from UpdateCamera and Render. No Stuart
method of this name.

Nearest reconstruction owner: **none**. Core has no mouse-look
tick. Campaign-scalar look-input 0.0226667 rad was **not**
re-derived. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement from this mapping until
that lane names the arm.

Siblings: `CBattleEngine__UpdateCameraVectorsAndInput` /
`CBattleEngine__Move` in this folder. Next named:
`CBattleEngineJetPart__Move` `0x00410c50` (Move callee; July
identity note; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407540` | `CBattleEngine__UpdateMouseLookAngles` | `a1f42d6600 83ec7c 8bd9 833dc09a8a0003 83bb6002000002 d99b14010000 … c3` (1018 B) | incoming-ECX thiscall; bare ret ×1; 1018 B; 12 E8 / 0 E9 / 7 targets; 4 inbound UpdateCamera+Render×3. HIGH on ABI, `EGameState==3`, `[+0x260]==2`, `[+0x114]`/`[+0x118]` stores. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on look-delta or rebuild parity. |
