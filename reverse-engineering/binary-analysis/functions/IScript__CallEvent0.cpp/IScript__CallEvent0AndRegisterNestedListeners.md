# IScript__CallEvent0AndRegisterNestedListeners

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / IScript (wrapper only; do not
read this as a pin of `IScript.cpp.md`) | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies `0x00539980` / `0x00539990` / `0x00538960`
and `IScript.cpp.md` / `CComplexThing.cpp.md` /
`CScriptObjectCode.cpp.md` / `CScriptEventNB.cpp.md` were
**not** written. Already-pinned siblings `0x005335a0` /
`0x00533660` / `0x005337e0` / `0x00533810` were **not**
re-done.

> Address: `0x00533500`

## Contract

`thiscall`. First insn `mov eax, [0x008a9ac0]`, then
`mov esi, ecx`. Zero stack args. Bare `ret` at `0x0053359a`.
Body `0x00533500`–`0x0053359a` is 155 bytes, SHA-256
`95216247fca8cdd51b940d7cdab60d515c23572293cd4a2d07a3bfce161561d6`.
Three `E8`, zero `E9`. Five `nop`s after the `ret` are
**not** in the body (neighbour already-pinned
`IScript__CallEventId6_OrReset` starts at `0x005335a0`).

Unlike the already-pinned id-3/5/6/7 wrappers, `[0x008a9ac0] == 4`
does **not** tail-`E9` Reset. It `E8`s table
`CScriptObjectCode__Reset` `0x00539980` (`0x00533514`) with
`ecx = 0x0089c5e0` and then falls into the same walk as the
non-4 arm. The other arm (`0x0053351b`) does
`push 0`, `push 0`, `push 0`, `push [esi+0xc]`,
`ecx = 0x0089c5e0`, `E8` table `CScriptObjectCode__CallEvent`
`0x00539990` (`0x0053352a`). Those four immediate-0 pushes are
**not** the `(0, 0x0089c528, imm-id)` plant the id-3/5/6/7
wrappers use. Callee bodies and the authored event name are
**not** this proof.

After either arm, `ebp = [esi+0xc] + 0x48`. The walk stores
`[ebp]` into `[ebp+8]`, takes `[eax]` as the outer node, and
for each live node walks `[ebx+0xc]`. Each live inner
`edi` is planted `push ebx` / `push edi` /
`ecx = 0x0089c590` into table
`CScriptEventNB__RegisterEventListener` `0x00538960`
(`0x00533564`); the return is stored at `[edi+4]`. Inner
advance is `[esi+4]`; outer advance is `[[ebp+8]+4]`. List
element types and that callee body are **not** this proof.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004f4359` | table `CComplexThing__HandleEvent` |

The host plants `ecx = [esi+0x74]` then `test ecx` /
`je` / `E8`. Zero image encodings of imm `00 35 53 00`.
That host is **not** claimed.

Cheapest falsifier: file `0x00133500` is not
`a1 c0 9a 8a 00`, **or** `0x0013359a` is not `c3`,
**or** body SHA-256 is not `95216247…61d6`, **or**
`tools/call_xref_scan.py` on `0x00533500` is not the one
`E8` above, **or** `0x00133508` is not `83 f8 04`, **or**
`0x00133514` is not `e8 67 64 00 00`, **or** `0x00133522`
is not `6a 00`, **or** `0x0013352a` is not
`e8 61 64 00 00`, **or** `0x00133532` is not `83 c5 48`,
**or** `0x00133564` is not `e8 f7 53 00 00`, **or**
`0x00133569` is not `89 47 04`, **or** a second inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00533500` | `IScript__CallEvent0AndRegisterNestedListeners` | `a1c09a8a00 53 55 56 83f804 8bf1 750c … e867640000 … 6a00 6a00 6a00 50 … e861640000 8b6e0c 83c548 … e8f7530000 894704 … c3` | thiscall; bare ret; 155 B; 3 E8 Reset `0x00539980` / CallEvent `0x00539990` / RegisterEventListener `0x00538960`; 0 E9; 1 inbound E8. HIGH on ABI, inbound set, cmp-4, those three plants, `+0x48` walk start, `[edi+4]` store. **Not** on callee bodies, list types, authored event name, or the host. |
