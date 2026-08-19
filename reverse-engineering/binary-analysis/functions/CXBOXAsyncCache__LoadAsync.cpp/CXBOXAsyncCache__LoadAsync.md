# CXBOXAsyncCache__LoadAsync

Status: active static function note
Last updated: 2026-08-19
Source File: XBOXAsyncCache.cpp / CXBOXAsyncCache (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`,
`ScriptObjectCode.cpp.md`, or a `CMissionScriptObjectCode`
rename)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Adopted `t_11f04b1b` after
independent re-derivation (steward cycle 46 re-read the
child; this card owns the land). The Ghidra database was
not opened. Table name is a research label. Already-pinned
ctor2 `0x00539c80` / ClearFields `0x00539f40` /
`CVM__Destructor` / `FUN_005398c0` /
`CScriptObjectCode.cpp.md` / StartLoadAsync `0x00539dc0` /
InitFields `0x00539f00` / callee bodies were **not** written.

> Address: `0x00539ca0`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d7626` /
`fs:[0]` install. Incoming ECX is parked in `ESI`. Zero stack
args. One bare `ret` (`0x00539db6`). Body `0x00539ca0`–
`0x00539db6` is 279 bytes, SHA-256
`4174e2afa05ed8f9ef16d27b0b865e8abaed524aa78311660e32568cd63f1c04`.
Thirteen `E8`, zero `E9`. Nine nops after the `ret` are **not**
in the body (table neighbour
`CMissionScriptObjectCode__StartLoadAsync` starts at
`0x00539dc0` and is not claimed).

The body:

1. If `[this+0x1c]` live: `E8` `0x00548c00` then store `0`.
2. `ecx = 0x009c3df0` / stack `0x134`, `0x11`,
   `0x006502a0` (`C:\\dev\\ONSLAUGHT2\\XBOXAsyncCache.cpp`),
   `0x1d` / `E8` `0x005490e0`. If EAX live, `E8` `0x00547d70`
   on that ptr. `[this+0x1c] = EAX`.
3. cdecl `E8` `0x00547d40` with `[this+0x124]`.
4. `ecx = [this+0x1c]`; `edi = this+0x20`; stack that path,
   `0x11`, `1`, `0`; `E8` `0x00547ec0`. cdecl `E8`
   `0x00547d40` with `0`. Non-zero EAX skips the fail path.
5. Fail path: cdecl `0x0055e490` with `rb` + `this+0x20`;
   optional `[0x0089c808] = 1` / `E8` `0x0055e4a3`; three
   no-op `E8` `0x0040c640` (`c3` stub) with the warning
   strings + path; then thiscall `0x00547d90` /
   `E8` `0x00549220` and `[this+0x1c] = 0`.
6. Both paths: `[this+0x20] = 0` (byte), uninstall `fs:[0]`.

`EAX` at the `ret` is leftover. Slot types, callee names,
async completion, and the class of `this` are **not** this
proof.

Thirteen body `E8` sites: `0x00539cc2` `0x00548c00`,
`0x00539ce1` `0x005490e0`, `0x00539cf8` `0x00547d70`,
`0x00539d13` / `0x00539d31` `0x00547d40`, `0x00539d28`
`0x00547ec0`, `0x00539d43` `0x0055e490`, `0x00539d57`
`0x0055e4a3`, `0x00539d64` / `0x00539d6d` / `0x00539d7a`
`0x0040c640`, `0x00539d8b` `0x00547d90`, `0x00539d96`
`0x00549220`. Raw `E8`-byte scan also hits `0x00539d30`
inside `8b e8` — that is not a call.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`a0 9c 53 00` at `0x005e4f5c` (file `0x001e4f5c`). The
already-pinned neighbour `0x00539c80` is the unique encoding
of imm `0x005e4f5c`. That table and class identity are **not**
this proof.

Cheapest falsifier: file `0x00139ca0` is not `6a`,
**or** `0x00139db6` is not `c3`, **or** body SHA-256 is not
`4174e2af…1c04`, **or** `tools/call_xref_scan.py` on
`0x00539ca0` is not zero `E8`/`E9`, **or**
`0x00139cc2` is not `e8 39 ef 00 00`, **or**
`0x001e4f5c` is not `a0 9c 53 00`, **or** a first inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539ca0` | `CXBOXAsyncCache__LoadAsync` | `6aff 6826765d00 64a100000000 50 64892500000000 51 55 56 8bf1 57 8b4e1c … e839ef0000 … 83c410 c3` | thiscall SEH; bare ret ×1; 279 B; 13 E8 / 0 E9; 0 inbound E8/E9; 1 pointer encoding at `0x005e4f5c`. HIGH on ABI, inbound set, `[+0x1c]` replace walk, `[+0x20]` path then byte-0, `[+0x124]` cdecl. **Not** on callee bodies, class identity, or async completion. |
