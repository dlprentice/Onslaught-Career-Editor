# CBattleEngine__Gravity

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
96 accepted WalkerPart Move through UpdateMouseLookAngles. This
wake landed Hit `efbf8e53` — not redone. Envelope, not a 19-instruction
walk. Did not mill FUN_*. Did not implement lock sets. Did not raise
the existing Gen31 `REBUILD_READY` row.

> Address: `0x004074d0`

## Contract

Incoming-ECX `thiscall`. First insn `test byte [ecx+0x2c], 4`.
Three bare `ret` (`0x00407505`, `0x0040750c`, `0x0040751e`).
Body `0x004074d0`–`0x0040751e` is 79 bytes, SHA-256
`58addc2bd10271b15ed11fd8026d652aa81583886c04ed4a7bddfd1b1694c9d8`
(PE bytes; not the C1-table Ghidra digest `5c841548…`). Capstone:
19 insns, zero `E8`, 2 `E9`, 1 unique rel32 target. Both `E9`s
tail-jmp `CBattleEngineJetPart__Gravity` `0x004114d0`. The two
switch tables at `0x00407520` / `0x00407530` sit after this body
and are **not** part of the 79-byte range. Neighbour table
`CBattleEngine__UpdateMouseLookAngles` starts at `0x00407540`
and is already pinned. Preceding table `CBattleEngine__Hit` is
already pinned.

Pinned prologue:

1. `test [ecx+0x2c], 4` then `eax = [ecx+0x260]` (same
   WALKER=2 / JET=3 polarity Init already pins). `[+0x2c]` is
   **not** named here.
2. `cmp eax, 3` / `ja` default `fld [0x005d856c]` (`00 00 00 00`
   = 0.0f) / `ret`.
3. Dying arm (`[+0x2c]` bit 2 set) indexes `[eax*4+0x00407520]`.
   Non-dying indexes `[eax*4+0x00407530]`.
4. Non-dying `eax==0` is `fld [0x005d8bac]`
   (`6f 12 03 3b` = 0.002f) / `ret`. `eax==1` and `eax==2` are
   `fld [0x005d8574]` (`0a d7 23 3c` = 0.01f) / `ret`.
5. `eax==3` is `ecx = [ecx+0x57c]` / `E9` JetPart Gravity —
   same jet-part slot Init stores.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`d0 74 40 00`: file `0x001d8a78` / VA `0x005d8a78` (vtable
slot 45, `+0xb4` from the `CBattleEngine` vtable base
`0x005d89c4` named by HandleEvent). Neighbouring dwords are
**not** this proof.

Source architecture (not proof): `CBattleEngine::Gravity`
`BattleEngine.cpp:1064-1088`. Retail bare `ret` matches zero
stack args. The 0.01 / 0.002 / JetPart split matches source;
the compiler folded `0.01*0.2` to `0x005d8bac`.

Rebuild mapping: `PARTIAL_CONTRACT` (PE envelope only). The
existing Gen31 `REBUILD_READY` row is **not** raised. See the
section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000074d0` is not `f6 41 2c 04`,
**or** `0x000074d4` is not `8b 81 60 02 00 00`, **or**
`0x000074ff` is not `d9 05 74 85 5d 00`, **or** `0x0000751e`
is not `c3`, **or** `0x001d8574` is not `0a d7 23 3c`, **or**
`0x001d8bac` is not `6f 12 03 3b`, **or** body SHA-256 is not
`58addc2b…c9d8`, **or** `tools/call_xref_scan.py` on
`0x004074d0` is not empty, **or** `0x001d8a78` is not
`d0 74 40 00`, **or** a second encoding of that imm exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not a new `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `58addc2b…c9d8`. `call_xref_scan` still empty.
File `0x001d8a78` still `d0 74 40 00`. Did not open Ghidra. Did
not edit `rebuild/**`. Did not name `[+0x2c]` bit 2. Did not
raise the existing Gen31 row.

Retail entity: `CBattleEngine` vtable slot-45 Gravity. Stuart
architecture (not proof): `BattleEngine.cpp:1064-1088`.

Nearest reconstruction owner: **existing**
`SimulationConstants` walker/jet/morph-into-walker gravity
literals (already cite this body). Not a new owner. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngine__Hit` /
`CBattleEngine__UpdateMouseLookAngles` in this folder. Next
named: `CBattleEngine__Damage` `0x0040a890` (existing C2
sibling; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004074d0` | `CBattleEngine__Gravity` | `f6412c04 8b8160020000 d90574855d00 … c3` (79 B) | incoming-ECX thiscall; bare ret ×3; 79 B; 0 E8 / 2 E9 / 1 target; 0 inbound; unique vtable slot 45 at `0x005d8a78`. HIGH on ABI, `[+0x260]` switch, 0.01/0.002 literals. Mapping `PARTIAL_CONTRACT`; existing REBUILD_READY not raised. **Not** on dying-bit name or rebuild parity. |
