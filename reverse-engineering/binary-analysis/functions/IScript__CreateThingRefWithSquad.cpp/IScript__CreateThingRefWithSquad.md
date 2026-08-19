# IScript__CreateThingRefWithSquad

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
label. Callee bodies `0x005490e0` / `0x004e5840` / `0x004e5a80`
/ `0x00539980` / `0x00539990` and `IScript.cpp.md` /
`CComplexThing.cpp.md` / `CScriptObjectCode.cpp.md` were
**not** written. Already-pinned neighbour `0x005337e0` was
**not** re-done.

> Address: `0x00533690`

## Contract

`thiscall` with SEH (`push -1` / `push 0x005d6d3f` /
`fs:[0]`). Saves incoming `ecx` at `[esp]` after the
`sub esp, 0xc`. One stack dword. Two `ret 4` sites
(`0x005337a4` after Reset, `0x005337d0` after CallEvent /
the early-out). Body `0x00533690`–`0x005337d2` is 323 bytes,
SHA-256
`aaa9f5741f16f4a22bed3559526277ac29e76092d660315bd9a34d7327e01c39`.
Six real `E8`, zero `E9`. Fourteen `nop`s after the last
`ret 4` are **not** in the body (already-pinned
`IScript__CallEventId3_OrReset` starts at `0x005337e0`).
A naive `E8` byte at `0x0053372e` is `mov [esp+0x2c], ebp`,
not a call.

If `[0x0089c7f0] != 0` **or** `[0x008a9ac0] == 4`, the body
jumps to the SEH teardown at `0x005337c2` with no alloc and
no CallEvent.

Otherwise first `E8` table `CDXMemoryManager__Alloc`
`0x005490e0` (`0x005336db`) with `ecx = 0x009c3df0` and
`push 0x11e` / `push 0x0064fa40` / `push 0x5d` / `push 8`.
On a live return it plants `[edi] = 0x005e4b4c` (COL
`0x00618ad0`, TypeDescriptor name `.?AVCDataType@@`) and
`[edi+4] = [esp+0x28]`. If that arg is live and
`[arg+4] == 0`, a second Alloc (`push 0x18` /
`push 0x0064fa6c` `...\monitor.h` / `push 0x5e` /
`push 0x10`) plus table `CSPtrSet__Init` `0x004e5840` and
`CSPtrSet__AddToHead` `0x004e5a80` run; those callee
bodies are **not** this proof. Then `[edi]` is overwritten
with `0x005e4df8` (COL `0x00619498`, TypeDescriptor name
`.?AVCThingPtrDataType@@`). Alloc-fail leaves `ecx = 0`.
Then `[0x0089c528] = ecx`.

A second `[0x008a9ac0] == 4` test after the box: if set and
`ecx` live, `push 1` / `call [vtable+0]`, then `E8` table
`CScriptObjectCode__Reset` `0x00539980` (`0x00533791`).
Else `push 1`, `push 0x0089c528`, `push 4`,
`push [saved-this+0xc]`, `ecx = 0x0089c5e0`, `E8` table
`CScriptObjectCode__CallEvent` `0x00539990` (`0x005337bd`).
Callee bodies and the authored event name are **not** this
proof.

Two inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004e6655` | table `CThing__CreateThingRefWithSquad` |
| `0x004f4495` | table `CComplexThing__Hit` |

Both hosts plant `ecx = [this+0x74]`, `test [arg+0x34],
0x80000000`, `push arg`, then the `E8`. Zero image
encodings of imm `90 36 53 00`. Those hosts are **not**
claimed.

Cheapest falsifier: file `0x00133690` is not `6a ff`,
**or** `0x001337d0` is not `c2 04 00`, **or** body SHA-256
is not `aaa9f574…1c39`, **or** `tools/call_xref_scan.py` on
`0x00533690` is not the two `E8` above, **or**
`0x001336f4` is not `c7 07 4c 4b 5e 00`, **or**
`0x0013375c` is not `c7 07 f8 4d 5e 00`, **or**
`0x001337b2` is not `6a 04`, **or** `0x001337bd` is not
`e8 ce 61 00 00`, **or** the COL name at file
`0x0024c598` is not `.?AVCDataType@@`, **or** the COL name
at file `0x0024cc20` is not `.?AVCThingPtrDataType@@`,
**or** a third inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00533690` | `IScript__CreateThingRefWithSquad` | `6aff 683f6d5d00 … a1f0c78900 … e8005a0100 c7074c4b5e00 … c707f84d5e00 … 6a04 … e8ce610000 … c20400` | thiscall SEH; ret 4 ×2; 323 B; 6 E8 Alloc×2 / CSPtrSet Init+Add / Reset / CallEvent; 0 E9; 2 inbound E8. HIGH on ABI, inbound set, early-out pair, both vptr plants, CallEvent push-4. **Not** on callee bodies, host `+0x34` bit, CSPtrSet algebra, or authored event name. |
