# CVM__Destructor

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CVM (first gates only; do not
read this as a pin of `CScriptObjectCode.cpp.md` /
`ScriptObjectCode.cpp.md` / `CMonitor.cpp.md`)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `ClearStack` /
`FUN_005398c0` / `CScriptObjectCode.cpp.md` / table
`CMonitor__Shutdown` / table `CVM__ScalarDeletingDestructor`
were **not** written. Steward cycle 43 accepted prior four.
This wake landed `da0426b4`. Did not steal `t_15e3a6ed` /
`t_c7affed5`.

> Address: `0x00535350`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d7028` /
`fs:[0]` install. Zero stack args. One bare `ret`
(`0x0053539b`). Body `0x00535350`–`0x0053539b` is 76 bytes,
SHA-256
`e64810806b0d5c0e48bb98a3cdc4f54fbdff6d49175b6e29cd65c44ed3e72055`.
Two `E8`, zero `E9`. Four nops after the `ret` are **not**
in the body (neighbour table
`IScript__GetRatioBattleLineNodes` starts at `0x005353a0`;
low neighbour table `CVM__ScalarDeletingDestructor` ends
at `0x0053534f`).

Incoming ECX is parked in `ESI` and also stored at
`[esp+4]`. The body:

1. Does **not** write `[this]` (no vptr immediate in this
   body).
2. `lea ecx, [esi+0xc]` then `E8` already-pinned
   `ClearStack` `0x005393e0`.
3. `ecx = esi` then `E8` table `CMonitor__Shutdown`
   `0x004bac40`.

`EAX` at the `ret` is whatever `0x004bac40` left. That
callee body, the `0x005d7028` SEH cookie, and the inbound
host are **not** this proof.

Two body `E8` sites: `0x00535378` `0x005393e0`,
`0x00535387` `0x004bac40`.

Two inbound `.text` sites (1 `E8` + 1 `E9`), zero image
encodings of imm `50 53 53 00`:

`0x00535333` `E8` inside table
`CVM__ScalarDeletingDestructor` (host does `esi = ecx`
then this call, then `test byte [esp+8], 1` and on set
`E8` `0x00549220` with `ecx = 0x009c3df0` / `push esi`,
then `EAX = esi` / `ret 4`; not claimed).
`0x005398c5` `E9` inside already-pinned `FUN_005398c0`
(`mov ecx, 0x0089c5e0` then this tail).

Cheapest falsifier: file `0x00135350` is not `6a ff`,
**or** `0x0013539b` is not `c3`, **or** body SHA-256 is not
`e6481080…2055`, **or** `tools/call_xref_scan.py` on
`0x00535350` is not the two sites above, **or**
`0x00135378` is not `e8 63 40 00 00`, **or**
`0x00135387` is not `e8 b4 58 f8 ff`, **or** a third
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00535350` | `CVM__Destructor` | `6aff 6828705d00 64a100000000 50 64892500000000 51 56 8bf1 … e863400000 8bce … e8b458f8ff … 83c410 c3` | thiscall SEH; bare ret ×1; 76 B; 2 E8 / 0 E9; 2 inbound (1 E8 + 1 E9). HIGH on ABI, inbound set, no vptr write, already-pinned ClearStack of `this+0xc` then table Shutdown. **Not** on `0x004bac40` or the scalar-deleting host. |
