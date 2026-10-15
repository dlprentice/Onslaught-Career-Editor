# CScriptObjectCode__ClearStack

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
name is a research label. `CScriptObjectCode.cpp.md` / Reset /
the stack-helper folders landed this wake were **not** written.

> Address: `0x005393e0`

## Contract

`thiscall`. First insn `push esi` / `mov esi, ecx`. Zero
stack args. One bare `ret` at `0x00539411`. Body
`0x005393e0`–`0x00539411` is 50 bytes, SHA-256
`3be8ab43a96d27b937953ac6f79507920db370ca55211ea3547f131e259e0707`.
Zero `E8`, zero `E9`. Nops after the `ret` are **not** in
the body (neighbour `CScriptObjectCode__Push` starts at
`0x00539420`).

If `[esi+0x200] == 0`, the body `pop esi` / `ret`. Else
it walks top-down: `elem = [esi + depth*4 - 4]`; if
`elem != 0` does `push 1` / `call [vtable+0]`; then
`--[esi+0x200]` and repeats while depth stays nonzero.
That slot-0 body is **not** this proof.

One inbound `.text` `E8` and one inbound `.text` `E9`:

`0x00535378` `E8` inside table `CVM__Destructor` (host
plants `lea ecx, [esi+0xc]`; **not** claimed).
`0x00539983` `E9` inside table `CScriptObjectCode__Reset`
(`add ecx, 0xc` then tail-jmp; **not** claimed). Zero
image encodings of imm `e0 93 53 00`.

Cheapest falsifier: file `0x001393e0` is not `56 8b f1`,
**or** `0x00139411` is not `c3`, **or** body SHA-256 is
not `3be8ab43…0707`, **or** `tools/call_xref_scan.py` on
`0x005393e0` is not the one `E8` and one `E9` above,
**or** `0x001393f3` is not `8b 4c 86 fc`, **or**
`0x001393ff` is not `ff 12`, **or** a second inbound
`E8` or `E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005393e0` | `CScriptObjectCode__ClearStack` | `56 8bf1 8b8600020000 85c0 7423 … 8b4c86fc 85c9 7406 8b11 6a01 ff12 … 48 898600020000 75dd 5e c3` | thiscall; bare ret; 50 B; 0 E8/E9; 1 inbound E8 + 1 inbound E9. HIGH on ABI, inbound set, top-down slot-0(1) drain. **Not** on slot-0, Reset, or CVM dtor. |
