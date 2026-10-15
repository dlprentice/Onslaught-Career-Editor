# CBattleEngine__AutoZoomOut

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
98 accepted Hit and Gravity — not redone. This wake landed ZoomIn
`8d714f53` and ZoomOut `35821452` — not redone. Envelope. Did not
mill FUN_*. Did not implement lock sets.

> Address: `0x00409e80`

## Contract

Incoming-ECX `thiscall`. First insn `mov dword [ecx+0x2cc],
0x3f800000` (1.0f). One bare `ret` at `0x00409e8a`. Body
`0x00409e80`–`0x00409e8a` is 11 bytes, SHA-256
`30351216ae6f04f8bbc7090253ce1b075be763458efe1d77f382005539205a2d`.
Capstone: 2 insns, zero `E8`, zero `E9`. Neighbour table
already-pinned `CBattleEngine__ZoomOut` starts at `0x00409e90`
after alignment `nop`s and is not rewritten.

No weapon gate (unlike ZoomIn/ZoomOut). `[+0x2cc]` is **not**
named here.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00411fe5` and
`CALL` at `0x00413ff9` (JetPart / WalkerPart tables). Zero
encodings of imm `80 9e 40 00` in the image (not a vtable slot).

Source architecture (not proof): `CBattleEngine::AutoZoomOut`
`BattleEngine.cpp:1919+`. Retail bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00009e80` is not
`c7 81 cc 02 00 00 00 00 80 3f`, **or** `0x00009e8a` is not
`c3`, **or** body SHA-256 is not `30351216…5a2d`, **or**
`tools/call_xref_scan.py` on `0x00409e80` is not exactly those
two `CALL`s, **or** a third `.text` `E8`/`E9` to this entry
exists, **or** any encoding of imm `80 9e 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `30351216…5a2d`. `call_xref_scan` still two
sites. Did not open Ghidra. Did not edit `rebuild/**`. Did not
name `[+0x2cc]`.

Retail entity: AutoZoomOut store of 1.0f at `[this+0x2cc]`.
Stuart architecture (not proof): `BattleEngine.cpp:1919+`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__ZoomIn` / `CBattleEngine__ZoomOut`.
Next named: `CBattleEngineWalkerPart__ChangeWeapon` `0x00413eb0`
(ChangeWeapon callee; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00409e80` | `CBattleEngine__AutoZoomOut` | `c781cc0200000000803f c3` (11 B) | incoming-ECX thiscall; bare ret ×1; 11 B; 0 E8 / 0 E9; 2 inbound Jet/Walker. HIGH on ABI and `[+0x2cc]=1.0f`. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field name or rebuild parity. |
