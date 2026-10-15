# CMissionScriptObjectCode__InitFields

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or `ScriptObjectCode.cpp.md`)
|||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Adopted `t_d14c8488` after independent
re-read (cycle 48 also re-read the child — this card lands).
The Ghidra database was not opened. Table name is a research
label. Cycle 48 accepted `6fb79dad` / `562fda84` / `1d91b9c9`
/ `a52210d3`; this wake landed `cf4c06f7` / `3ba05cb7` /
`c4a8c8a2` StartLoadAsync — not redone. Already-pinned
ClearFields `0x00539f40`
(`91dcfad8`) / ClearFields thunk `0x00539f30` (`1d91b9c9`) /
LoadAsync / FUN_0053a2d0 / FUN_0053a2f0 /
`CScriptObjectCode.cpp.md` / sibling StartLoadAsync
`0x00539dc0` were **not** rewritten.

> Address: `0x00539f00`

## Contract

`thiscall`, not SEH. First insn `mov eax, ecx`. Incoming ECX is
parked in `EAX`. Zero stack args. One bare `ret`
(`0x00539f24`). Body `0x00539f00`–`0x00539f24` is 37 bytes,
SHA-256
`8df2aa461de9376eddc00f214bd8517cd197c1848dde8b2725babad19eeed682`.
Zero `E8`, zero `E9`. Eleven nops after the `ret` are **not**
in the body (already-pinned neighbour
`CMissionScriptObjectCode__ClearFields_Thunk` starts at
`0x00539f30`). Already-pinned predecessor `FUN_00539e30`
ends `ret` at `0x00539ef2`; the thirteen nops
`0x00539ef3`–`0x00539eff` are **not** in this body.

`ecx = 0`. Measured store-0 order (no release, no call):

1. `[this+0x60]`
2. `[this+0]`
3. `[this+4]`
4. `[this+8]`
5. `[this+0x70]`
6. `[this+0x74]`
7. `[this+0x18]`
8. `[this+0xc]`
9. `[this+0x78]`
10. `[this+0x10]`
11. `[this+0x14]`

Already-pinned ClearFields (`0x00539f40`, 196 B sha
`40cae7f6…9ace`) walks ten live slots, release then store-0,
in this order: `+0`, `+4`, `+8`, `+0x70`, `+0x74`, `+0x18`,
`+0xc`, `+0x78`, `+0x10`, `+0x14`. InitFields slots 2–11 are
that same ten-slot order. InitFields additionally stores
`[this+0x60] = 0` first. ClearFields does not touch `+0x60`.
This body does not free `this`. `EAX` at the `ret` is this.
Slot types and the class of `this` are **not** this proof.

Zero body `E8`/`E9`.

One inbound `.text` `E8` and zero inbound `E9`: `0x004814df`
inside table `CHud__Init` (not claimed; table range
`0x00481450`–`0x004815b5`). Site bytes `e8 1c 8a 0b 00`.
Zero image encodings of imm `00 9f 53 00`.

Cheapest falsifier: file `0x00139f00` is not `8b`,
**or** `0x00139f24` is not `c3`, **or** body SHA-256 is not
`8df2aa46…d682`, **or** `tools/call_xref_scan.py` on
`0x00539f00` is not the one `E8` above, **or** `0x00139f04`
is not `89 48 60`, **or** `0x000814df` is not
`e8 1c 8a 0b 00`, **or** a second inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539f00` | `CMissionScriptObjectCode__InitFields` | `8bc1 33c9 894860 8908 894804 894808 894870 894874 894818 89480c 894878 894810 894814 c3` | thiscall; not SEH; bare ret ×1; 37 B; 0 E8 / 0 E9; 1 inbound E8 + 0 inbound E9. HIGH on ABI, inbound set, eleven store-0 slots, ClearFields order match on the last ten. **Not** on slot types, CHud, thunk, or class of this. |
