# CMissionScriptObjectCode__ClearFields

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or `ScriptObjectCode.cpp.md`)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Adopted `t_c7affed5` after
independent re-derivation (steward cycle 44 re-read the
child; this card owns the land). The Ghidra database was
not opened. Table name is a research label. Already-pinned
ctor / `CVM__Destructor` / `CScriptObjectCode.cpp.md` /
InitFields `0x00539f00` / ClearFields_Thunk `0x00539f30` /
sibling `0x00539c80` / callee bodies were **not** written.

> Address: `0x00539f40`

## Contract

`thiscall`, not SEH. First insn `push ebx`. Incoming ECX is
parked in `ESI`. Zero stack args. One bare `ret`
(`0x0053a003`). Body `0x00539f40`–`0x0053a003` is 196 bytes,
SHA-256
`40cae7f6c05c66adf958b90143482f154ac573820bc71ed860edaddf633f9ace`.
Eight `E8`, zero `E9`. Twelve nops after the `ret` are **not**
in the body (table neighbour `CBLTexture__VFunc_1_0053a010`
starts at `0x0053a010` and is not claimed).

`ebx = 0`. Measured walk order; each live slot is released
then stored `0`:

1. `[this+0]`: `E8` `0x004f7440` then `ecx = 0x009c3df0` /
   `push` the same ptr / `E8` `0x00549220`.
2. `[this+4]`: `lea ecx, [ptr+8]` / `E8` `0x004f27e0`.
3. `[this+8]`: same `+8` / `0x004f27e0`.
4. `[this+0x70]`: `push 1` / `call [[ptr]+0]`.
5. `[this+0x74]`: same vfunc.
6. `[this+0x18]`: `ecx = 0x009c3df0` / `push` that ptr /
   `E8` `0x00549220`.
7. `[this+0xc]`: `+8` / `0x004f27e0`.
8. `[this+0x78]`: `push 1` / `call [[ptr]+0]`.
9. `[this+0x10]`: `+8` / `0x004f27e0`.
10. `[this+0x14]`: `+8` / `0x004f27e0`.

This body does not free `this`. `EAX` at the `ret` is leftover.
Slot types, callee names, and the three vfuncs are **not**
this proof.

Eight body `E8` sites: `0x00539f4f` `0x004f7440`,
`0x00539f5a` / `0x00539fb2` `0x00549220`, `0x00539f6b` /
`0x00539f7d` / `0x00539fc4` / `0x00539fe6` / `0x00539ff8`
`0x004f27e0`.

One inbound `.text` `E8` and one inbound `E9`: `0x00481b0e`
inside table `CHud__ShutDown` (not claimed; host
`0x00481b00`–`0x00481f3b` does `ecx = [esi+0x30]`, null
skips), and `0x00539f30` (unclaimed thunk `e9 0b 00 00 00`
into this VA). Zero image encodings of imm `40 9f 53 00`.

Cheapest falsifier: file `0x00139f40` is not `53`,
**or** `0x0013a003` is not `c3`, **or** body SHA-256 is not
`40cae7f6…9ace`, **or** `tools/call_xref_scan.py` on
`0x00539f40` is not the one `E8` and one `E9` above, **or**
`0x00139f4f` is not `e8 ec d4 fb ff`, **or** `0x00081b0e`
is not `e8 2d 84 0b 00`, **or** a second inbound `E8` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539f40` | `CMissionScriptObjectCode__ClearFields` | `53 56 8bf1 57 33db 8b3e 3bfb 7414 8bcf e8ecd4fbff … 5f5e5b c3` | thiscall; bare ret ×1; 196 B; 8 E8 / 0 E9; 1 inbound E8 + 1 inbound E9. HIGH on ABI, inbound set, ordered slot-null then store-0. **Not** on callee bodies, CHud, thunk, or class of this. |
