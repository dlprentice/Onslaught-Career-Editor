# CMissionScriptObjectCode__ctor

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or `Symtab.cpp.md`)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Child report
`local-lab/hermes-kanban-campaign-2026-08-18/ctor-00538ec0/REPORT.md`
was treated as data and re-derived. The Ghidra database was not
opened. Table name is a research label. Already-pinned
`ReadSymbolTable` / `Clone` / `CMissionScriptObjectCode__dtor` /
`CMissionScriptObjectCode__scalar_deleting_dtor` /
`CScriptObjectCode.cpp.md` / the fourteen other callee bodies
were **not** written. Steward cycle 42 accepted prior three.
This wake landed `dbddd4fa` / `77bb9a17` / `8044bfe5`.

> Address: `0x00538ec0`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d7512` /
`fs:[0]` install. One stack dword. One `ret 4`
(`0x00539038`). Body `0x00538ec0`–`0x0053903a` is 379 bytes,
SHA-256
`2f8062dd4306f86d51e683f20af9db7a0cfe6be5efe7b06e209493ceca07ed3c`.
Fifteen `E8`, zero `E9`. Five nops after the `ret 4` are
**not** in the body (already-pinned neighbour
`CScriptObjectCode__Clone` starts at `0x00539040`).

Incoming ECX is parked in `ESI`. The body:

1. `E8` `0x004241a0` (`ecx = this+4`), `E8` `0x004e5840`
   (`ecx = this+0x48`).
2. Stores imm `0x005e4f54` at `[this]` (same vptr already
   cited on Clone / dtor / scalar-deleting dtor) and
   `[this+0x6c] = 0`.
3. Stream reads via `E8` `0x00548570`. A count-gated loop
   cdecl-calls `0x0052d3d0` and appends via `0x004241f0`
   at `this+4`. Thirteen dwords land at `this+0x14`.
4. `E8` `0x005490e0` alloc `0x14`. Live dest: already-pinned
   `ReadSymbolTable` `0x00539770`; `[this+0x58] =` that
   result (or 0).
5. A second stream count gates `0x20` allocs constructed
   with `0x0052fa70` and appended via `0x004e5b20` at
   `this+0x48`.
6. Stream into `[this+0x60]` then `[this+0x5c]`.
   `[this+0x64] = [this+0xc]`.

`EAX = this` at the `ret` (`8b c6`). Those unpinned callee
bodies and the class of `this` are **not** this proof.

Fifteen body `E8` sites: `0x00538eef` `0x004241a0`,
`0x00538efd` `0x004e5840`, `0x00538f1d` / `0x00538f33` /
`0x00538f64` / `0x00538fae` / `0x0053900c` / `0x00539019`
`0x00548570`, `0x00538f3e` `0x0052d3d0`, `0x00538f49`
`0x004241f0`, `0x00538f7f` / `0x00538fcf` `0x005490e0`,
`0x00538f94` `0x00539770`, `0x00538fe4` `0x0052fa70`,
`0x00538ff6` `0x004e5b20`.

One inbound `.text` `E8`, zero `E9`: `0x0050ad20` inside
table `CWorld__LoadScriptEvents` (not claimed; host starts
`push -1` at `0x0050ac70`). That site does `E8` `0x005490e0`
with stack `0x70`, then on a live dest `push ebp` /
`ecx = eax` then this call, then `esi = EAX`. Zero image
encodings of imm `c0 8e 53 00`.

Cheapest falsifier: file `0x00138ec0` is not `6a ff`,
**or** `0x00139038` is not `c2 04 00`, **or** body SHA-256
is not `2f8062dd…ed3c`, **or** `tools/call_xref_scan.py` on
`0x00538ec0` is not the one `E8` above, **or**
`0x00138f14` is not `c7 06 54 4f 5e 00`, **or**
`0x00138f94` is not `e8 d7 07 00 00`, **or** a second
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00538ec0` | `CMissionScriptObjectCode__ctor` | `6aff 6812755d00 64a100000000 50 64892500000000 83ec0c … 8bc6 894e64 8b4c241c 5f5e5d5b 64890d00000000 83c418 c20400` | thiscall SEH; ret 4 ×1; 379 B; 15 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, vptr imm `0x005e4f54`, already-pinned ReadSymbolTable into `[+0x58]`, `[+0x64]=[+0xc]`, EAX=this. **Not** on callee bodies or LoadScriptEvents. |
