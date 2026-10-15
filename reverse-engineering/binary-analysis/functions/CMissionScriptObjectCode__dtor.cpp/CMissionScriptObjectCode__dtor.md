# CMissionScriptObjectCode__dtor

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or `ScriptObjectCode.cpp.md`)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `ClearSymbolTable` /
`Clone` / `CloneSymbolTable` / `CScriptObjectCode.cpp.md` / the
inbound scalar-deleting host / the six other callee bodies were
**not** written. Steward cycle 42 accepted ClearSymbolTable /
Clone / CloneSymbolTable — not redone. Did not steal
`t_914bfb68` / `t_a8841217`.

> Address: `0x005391a0`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d7566` /
`fs:[0]` install. Zero stack args. One bare `ret`
(`0x00539292`). Body `0x005391a0`–`0x00539292` is 243 bytes,
SHA-256
`a90cf9ea407391adb1bd0da5c5f75536f50380189f9cf21da605cf5277ae8977`.
Seven `E8`, zero `E9`. Thirteen nops after the `ret` are
**not** in the body (neighbour table
`CScriptObjectCode__CollectSpawnThings` starts at
`0x005392a0` and is owned by `t_914bfb68`).

Incoming ECX is parked in `ESI`. The body:

1. Stores imm `0x005e4f54` at `[this]` (same vptr imm
   already-pinned `Clone` writes on its dest; RTTI of that
   slot is **not** this proof).
2. Count-gated walk of `[[this+4] + i*4]` for
   `i = 0 .. [this+0x64)`. Each live slot is `push`ed and
   `E8` `0x00549220` with `ecx = 0x009c3df0`. `jle`
   `0x005391f0` skips when `[this+0x64] <= 0`.
3. `EDI = this+0x48`. Copies `[this+0x48]` to `[this+0x50]`.
   While that cursor is live it takes `[cursor]`, then if
   that object is live `push 1` / `call [[obj]+4]`
   (indirect; not an `E8`), then advances
   `[this+0x50] = [[this+0x50]+4]`.
4. `E8` `0x004e5c60` with `ecx = this+0x48`, then `E8`
   `0x004241e0` with `ecx = this+4`, then
   `[this+0x64] = 0`.
5. `EBP = [this+0x58]`. Null skips. Else `ecx = EBP`, `E8`
   already-pinned `ClearSymbolTable` `0x00539510`, then
   `push EBP` / `E8` `0x00549220` with `ecx = 0x009c3df0`.
6. `[this+0x58] = 0` and `[this+0x5c] = 0`. `E8`
   `0x004e5c60` again (`ecx = this+0x48`), then `E8`
   `0x00465570` with `ecx = this+4`.

`EAX` at the `ret` is whatever `0x00465570` left. Those six
unpinned callee bodies, the `[obj]+4` vfunc, the `0x009c3df0`
object, and the class of the `+0x48` list are **not** this
proof.

Seven body `E8` sites: `0x005391e3` / `0x00539259`
`0x00549220`, `0x0053922f` / `0x0053926c` `0x004e5c60`,
`0x00539239` `0x004241e0`, `0x0053924e` `0x00539510`,
`0x0053927b` `0x00465570`.

One inbound `.text` `E8`, zero `E9`: `0x00538ea3` inside
table `CMissionScriptObjectCode__scalar_deleting_dtor` (not
claimed). That host does `esi = ecx` then this call, then
`test byte [esp+8], 1` and on set `E8` `0x00549220` with
`ecx = 0x009c3df0` / `push esi`, then `EAX = esi` /
`ret 4`. Zero image encodings of imm `a0 91 53 00`.

Cheapest falsifier: file `0x001391a0` is not `6a ff`,
**or** `0x00139292` is not `c3`, **or** body SHA-256 is not
`a90cf9ea…8977`, **or** `tools/call_xref_scan.py` on
`0x005391a0` is not the one `E8` above, **or**
`0x001391c0` is not `c7 06 54 4f 5e 00`, **or**
`0x0013924e` is not `e8 bd 02 00 00`, **or** a second
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005391a0` | `CMissionScriptObjectCode__dtor` | `6aff 6866755d00 64a100000000 50 64892500000000 51 … 8b4c2414 5f5e5d5b 64890d00000000 83c410 c3` | thiscall SEH; bare ret ×1; 243 B; 7 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, vptr imm `0x005e4f54`, `[+0x64]` slot Free, `+0x48` walk, already-pinned ClearSymbolTable of `[+0x58]`. **Not** on callee bodies, `[obj]+4`, or the inbound host. |
