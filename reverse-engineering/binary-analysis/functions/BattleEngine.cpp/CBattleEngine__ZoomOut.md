# CBattleEngine__ZoomOut

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
98 accepted Hit `efbf8e53` and Gravity `5f7915a1` — not redone.
This wake landed ZoomIn `8d714f53` — not redone. Envelope. Did
not mill FUN_*. Did not implement lock sets. Sibling AutoZoomOut
`0x00409e80` is not rewritten.

> Address: `0x00409e90`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. `esi = ecx`.
One bare `ret` at `0x00409eb6`. Body `0x00409e90`–`0x00409eb6`
is 39 bytes, SHA-256
`45f14d31faa6f75f4ccbbbb011baffb8ea7f13c3514a795cbda09bbdef347a38`.
Capstone: 11 insns, zero `E8`, zero `E9`. Neighbour table
already-pinned `CBattleEngine__ZoomIn` starts at `0x00409ec0`
after alignment `nop`s and is not rewritten. Preceding table
`CBattleEngine__AutoZoomOut` ends at `0x00409e8a` and is not
rewritten.

Pinned body, with `esi = ecx`:

1. `mov eax, [esi]` / `call dword [eax+0x1d4]`. Same vcall
   slot ZoomIn already counts. **Not** named here.
2. EAX==0 or `[eax+0xa4]+0x34 != 1` skips the store.
3. Else `mov [esi+0x2cc], 0x3f800000` (1.0f). Same slot ZoomIn
   writes 0.4f. **Not** named here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x004d32b8` inside
table `CPlayer__ReceiveButtonAction` (same owner Morph /
ChangeWeapon / ZoomIn already pin). Zero encodings of imm
`90 9e 40 00` in the image (not a vtable slot).

Source architecture (not proof): `CBattleEngine::ZoomOut`
`BattleEngine.cpp:1925+`. Retail bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00009e90` is not `56`, **or**
`0x00009e91` is not `8b f1`, **or** `0x00009e95` is not
`ff 90 d4 01 00 00`, **or** `0x00009eab` is not
`c7 86 cc 02 00 00 00 00 80 3f`, **or** `0x00009eb6` is not
`c3`, **or** body SHA-256 is not `45f14d31…7a38`, **or**
`tools/call_xref_scan.py` on `0x00409e90` is not exactly one
`CALL` at `0x004d32b8`, **or** a second `.text` `E8`/`E9` to
this entry exists, **or** any encoding of imm `90 9e 40 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `45f14d31…7a38`. `call_xref_scan` still one
`CALL` at `0x004d32b8`. Did not open Ghidra. Did not edit
`rebuild/**`. Did not name vcall `+0x1d4` or `[+0x2cc]`.

Retail entity: player ZoomOut request from
`CPlayer__ReceiveButtonAction`. Stuart architecture (not
proof): `BattleEngine.cpp:1925+`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__ZoomIn` in this folder. Next named:
`CBattleEngine__AutoZoomOut` `0x00409e80` (store 1.0f, no
weapon gate; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00409e90` | `CBattleEngine__ZoomOut` | `56 8bf1 ff90d4010000 … c786cc0200000000803f … c3` (39 B) | incoming-ECX thiscall; bare ret ×1; 39 B; 0 E8 / 0 E9; 1 inbound Player. HIGH on ABI, `vcall +0x1d4`, `[+0x2cc]=1.0f`. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names or rebuild parity. |
