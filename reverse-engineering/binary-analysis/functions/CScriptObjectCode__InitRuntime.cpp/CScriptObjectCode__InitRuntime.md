# CScriptObjectCode__InitRuntime

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `CopyState` /
`CScriptObjectCode.cpp.md` / the inbound thunk were **not** written.

> Address: `0x005398d0`

## Contract

`thiscall`. First insn `mov eax, ecx` / `xor ecx, ecx`.
Zero stack args. One bare `ret` (`0x00539904`). Body
`0x005398d0`–`0x00539904` is 53 bytes, SHA-256
`cb0725f70b367de4f954e17e5d3e0788f47e7838a9870e2f6977235e89bec4cc`.
Zero `E8`, zero `E9`. Eleven nops after the `ret` are
**not** in the body (already-pinned neighbour
`CScriptObjectCode__CopyState` starts at `0x00539910`).

Incoming ECX is the VM. The body parks `EAX = this`,
uses `ECX` as the 0 immediate, and stores
`[this+4] = 0`, `[this+0x20c] = 0`,
`[this] = 0x005e4f1c` (`c7 00 1c 4f 5e 00`),
`[this+8] = 0`, `[this+0x214] = 0`,
`[this+0x218] = 0`, `[this+0x21c] = 0`,
`[this+0x224] = 0`, `[this+0x210] = 0`.
It does **not** write `+0x220` and does **not** drain
stack slots. `EAX = this` at the `ret`. The vptr
immediate is a byte; the CVM class label already pinned
elsewhere is **not** this proof.

One inbound `.text` `E8`, zero `E9`: `0x005398a5` inside
the unlabeled thunk at `0x005398a0` (`mov ecx, 0x0089c5e0`
then the call; not a name-table row). Zero image encodings
of imm `d0 98 53 00`.

Cheapest falsifier: file `0x001398d0` is not `8b c1`,
**or** `0x00139904` is not `c3`, **or** body SHA-256 is
not `cb0725f7…c4cc`, **or** `tools/call_xref_scan.py` on
`0x005398d0` is not the one `E8` above, **or**
`0x001398dd` is not `c7 00 1c 4f 5e 00`, **or**
`0x001398fe` is not `89 88 10 02 00 00`, **or** a second
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005398d0` | `CScriptObjectCode__InitRuntime` | `8bc1 33c9 894804 89880c020000 c7001c4f5e00 894808 898814020000 … 898810020000 c3` | thiscall; bare ret ×1; 53 B; 0 E8/E9; 1 inbound E8. HIGH on ABI, inbound set, the nine stores including vptr imm and `+0x210` last, no `+0x220` write. **Not** on the thunk or CVM slot bodies. |
