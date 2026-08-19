# CScriptObjectCode__CloneSymbolTable

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or `Symtab.cpp.md`)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Child report
`local-lab/hermes-kanban-campaign-2026-08-18/clonesymboltable-005395b0/REPORT.md`
was treated as data and re-derived. The Ghidra database was not
opened. Table name is a research label. Already-pinned
`ClearSymbolTable` / `Clone` / `GetInstruction` /
`ReadSymbolTable` / `CScriptObjectCode.cpp.md` /
`Symtab.cpp.md` / the five callee bodies were **not** written.
Steward cycle 41 accepted GetInstruction / ReadSymbolTable —
not redone.

> Address: `0x005395b0`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d75bf` /
`fs:[0]` install. Zero stack args. One bare `ret`
(`0x00539759`). Body `0x005395b0`–`0x00539759` is 426 bytes,
SHA-256
`ea8587220b33cff8a7e65c37486640b221893edcec92be4b1d5ea8ed8724b114`.
Five `E8`, zero `E9`. Six nops after the `ret` are **not**
in the body (already-pinned neighbour
`CScriptObjectCode__GetInstruction` starts at `0x00539760`).

Incoming ECX (source) is parked in `EDI`. The body:

1. `E8` `0x005490e0` with `ecx = 0x009c3df0` and stack
   `0xb4` / `0x00650134` / `0x18` / `0x14`. The C string at
   `0x00650134` is
   `C:\\dev\\ONSLAUGHT2\\MissionScript\\Symtab.cpp`. Dest is
   that `0x14`-byte alloc. Failure zeroes dest and still
   reads `[src+8]`.
2. Live dest: `E8` `0x004241a0` (`ecx = dest`), then
   `[dest+0x10] = 0`.
3. `jle` `0x00539745` skips the row loop when `[src+8]`
   is `<= 0`. Each slot is `row = [[src] + i*4]`.
4. If `[row+8] != 0`, `call [[row+8]+0x48]` (indirect).
   Then `E8` `0x005490e0` alloc `0x18`. Live row:
   `call [[row]+0x38]`, `E8` `0x0052f690` (`ecx = new`),
   `[new+0xc] = [row+0xc]`, `[new+8] =` that `+0x48`
   result, `[new+0x10] = 0`, `byte [new+0x14] = 0`.
5. `call [[new]+0x38]` then a two-byte C-string walk
   against dest slots. A match skips the append. Else
   `E8` `0x004241f0` (`ecx = dest`, arg = new) and
   `inc [dest+0x10]`.

`EAX = dest` at the `ret` (`8b c5`). Those five callee
bodies and the `+0x38` / `+0x48` vfunc identities are
**not** this proof.

Five body `E8` sites: `0x005395e5` / `0x00539664`
`0x005490e0`, `0x00539604` `0x004241a0`, `0x00539688`
`0x0052f690`, `0x00539728` `0x004241f0`.

One inbound `.text` `E8`, zero `E9`: `0x0053911d` inside
already-pinned `CScriptObjectCode__Clone` (that host was
**not** rewritten). It plants `ecx = [src+0x58]` then
`[dest+0x58] = EAX`. Zero image encodings of imm
`b0 95 53 00`.

Cheapest falsifier: file `0x001395b0` is not `6a ff`,
**or** `0x00139759` is not `c3`, **or** body SHA-256 is
not `ea858722…b114`, **or** `tools/call_xref_scan.py` on
`0x005395b0` is not the one `E8` above, **or**
`0x001395e5` is not `e8 f6 fa 00 00`, **or** `0x0013974a`
is not `8b c5`, **or** a second inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005395b0` | `CScriptObjectCode__CloneSymbolTable` | `6aff 68bf755d00 64a100000000 50 64892500000000 83ec14 … 8bc5 5e5d5b 64890d00000000 83c420 c3` | thiscall SEH; bare ret ×1; 426 B; 5 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, 0x14 dest alloc, `[src+8]` row walk, EAX=dest. **Not** on callee bodies, vfuncs, or Clone. |
