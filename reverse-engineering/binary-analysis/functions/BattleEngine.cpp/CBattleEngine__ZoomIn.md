# CBattleEngine__ZoomIn

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
97 accepted JetPart Move and GroundParticleEffect. This wake
landed ChangeWeapon `abe0302b` — not redone. Envelope, not a
walk. Did not mill FUN_*. Did not implement lock sets. Siblings
`ZoomOut` `0x00409e90` and `AutoZoomOut` `0x00409e80` are not
rewritten.

> Address: `0x00409ec0`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. `esi = ecx`.
One bare `ret` at `0x00409ee6`. Body `0x00409ec0`–`0x00409ee6`
is 39 bytes, SHA-256
`4a5ccf60234b369fb6c2dbb67375867286315755056941a15c48335dab6d2f8c`.
Capstone: 11 insns, zero `E8`, zero `E9`. Neighbour table
`CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0` starts
after alignment `nop`s and is not rewritten. Preceding table
`CBattleEngine__ZoomOut` ends at `0x00409eb6` and is not
rewritten.

Pinned body, with `esi = ecx`:

1. `mov eax, [esi]` / `call dword [eax+0x1d4]`. Same vcall slot
   HandleAutoAim / UpdateAutoAim already count. **Not** named
   here.
2. EAX==0 or `[eax+0xa4]+0x34 != 1` skips the store.
3. Else `mov [esi+0x2cc], 0x3ecccccd` (0.4f). `[+0x2cc]` is
   **not** named here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x004d32b1` inside
table `CPlayer__ReceiveButtonAction` (same owner Morph /
ChangeWeapon already pin). Zero encodings of imm `c0 9e 40 00`
in the image (not a vtable slot).

Source architecture (not proof): `CBattleEngine::ZoomIn`
`BattleEngine.cpp:1937+`. Retail bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00009ec0` is not `56`, **or**
`0x00009ec1` is not `8b f1`, **or** `0x00009ec5` is not
`ff 90 d4 01 00 00`, **or** `0x00009edb` is not
`c7 86 cc 02 00 00 cd cc cc 3e`, **or** `0x00009ee6` is not
`c3`, **or** body SHA-256 is not `4a5ccf60…2f8c`, **or**
`tools/call_xref_scan.py` on `0x00409ec0` is not exactly one
`CALL` at `0x004d32b1`, **or** a second `.text` `E8`/`E9` to
this entry exists, **or** any encoding of imm `c0 9e 40 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `4a5ccf60…2f8c`. `call_xref_scan` still one
`CALL` at `0x004d32b1`. Did not open Ghidra. Did not edit
`rebuild/**`. Did not name vcall `+0x1d4` or `[+0x2cc]`.

Retail entity: player ZoomIn request from
`CPlayer__ReceiveButtonAction`. Stuart architecture (not
proof): `BattleEngine.cpp:1937+`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__ChangeWeapon` in this folder. Next
named: `CBattleEngine__ZoomOut` `0x00409e90` (same shape; store
1.0f; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00409ec0` | `CBattleEngine__ZoomIn` | `56 8bf1 ff90d4010000 … c786cc020000cdcccc3e … c3` (39 B) | incoming-ECX thiscall; bare ret ×1; 39 B; 0 E8 / 0 E9; 1 inbound Player. HIGH on ABI, `vcall +0x1d4`, `[+0x2cc]=0.4f`. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names or rebuild parity. |
