# IScript__CreateThingRef

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
label. Callee bodies `0x005490e0` / `0x00539980` / `0x00539990`
and `IScript.cpp.md` / `CScriptEventNB.cpp.md` /
`CScriptObjectCode.cpp.md` were **not** written. Already-pinned
neighbour `0x00533660` was **not** re-done.

> Address: `0x005335d0`

## Contract

`thiscall`. First insn `mov eax, [0x0089c7f0]`, then
`mov esi, ecx`. One stack dword. Two `ret 4` sites
(`0x00533639` after Reset, `0x00533654` after CallEvent /
the early-out). Body `0x005335d0`–`0x00533656` is 135 bytes,
SHA-256
`4bd52cc54c4dcfa3903997bf7b4cc9bb1893fab32de3d75f617b9c93af1d9516`.
Three `E8`, zero `E9`. Nine `nop`s after the last `ret 4`
are **not** in the body (already-pinned
`IScript__CallEventId5_OrReset` starts at `0x00533660`).

If `[0x0089c7f0] != 0` **or** `[0x008a9ac0] == 4`, the body
jumps to `0x00533653` (`pop esi; ret 4`) with no alloc and
no CallEvent. Those two loads are **not** further named
here.

Otherwise it `E8`s table `CDXMemoryManager__Alloc`
`0x005490e0` (`0x005335f8`) with `ecx = 0x009c3df0` and
stack `push 0x10d`, `push 0x0064fa40`
(`C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp`),
`push 0x18`, `push 8`. On a live return it plants
`[eax] = 0x005e4af8` and `[eax+4] = [esp+8]`. The dword immediately
before that vptr is COL `0x00618aa0`; its TypeDescriptor
name at `0x0064c5a8+8` is `.?AVCIntDataType@@`. Alloc-fail
leaves `ecx = 0`. Then `[0x0089c528] = ecx`.

A second `[0x008a9ac0] == 4` test after the box: if set and
`ecx` live, `push 1` / `call [vtable+0]`, then `ecx =
0x0089c5e0` and `E8` table `CScriptObjectCode__Reset`
`0x00539980` (`0x00533633`), then `ret 4`. Else
`push 1`, `push 0x0089c528`, `push 1`, `push [esi+0xc]`,
`ecx = 0x0089c5e0`, `E8` table
`CScriptObjectCode__CallEvent` `0x00539990` (`0x0053364e`).
Callee bodies, the authored event name, and the
`[vtable+0]` body are **not** this proof.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x00538583` | table `CScriptEventNB__UpdateWaypointFollowing` |

The host plants `eax = [esi+0x24]`, `ecx = esi`,
`push eax`, then the `E8`. Zero image encodings of imm
`d0 35 53 00`. That host is **not** claimed.

Cheapest falsifier: file `0x001335d0` is not
`a1 f0 c7 89 00`, **or** `0x00133654` is not `c2 04 00`,
**or** body SHA-256 is not `4bd52cc5…9516`, **or**
`tools/call_xref_scan.py` on `0x005335d0` is not the one
`E8` above, **or** `0x001335dc` is not
`83 3d c0 9a 8a 00 04`, **or** `0x001335f8` is not
`e8 e3 5a 01 00`, **or** `0x00133605` is not
`c7 00 f8 4a 5e 00`, **or** `0x00133619` is not
`89 0d 28 c5 89 00`, **or** `0x00133646` is not `6a 01`,
**or** `0x0013364e` is not `e8 3d 63 00 00`, **or** the
COL name at file `0x0024c5b0` is not
`.?AVCIntDataType@@`, **or** a second inbound `E8`/`E9`
exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005335d0` | `IScript__CreateThingRef` | `a1f0c78900 56 85c0 8bf1 7577 833dc09a8a0004 … e8e35a0100 … c700f84a5e00 … 890d28c58900 … 6a01 6828c58900 6a01 … e83d630000 5e c20400` | thiscall; ret 4 ×2; 135 B; 3 E8 Alloc `0x005490e0` / Reset `0x00539980` / CallEvent `0x00539990`; 0 E9; 1 inbound E8. HIGH on ABI, inbound set, early-out pair, vptr plant `0x005e4af8` / `.?AVCIntDataType@@`, `[0x0089c528]` store, CallEvent push-1. **Not** on callee bodies, host waypoint algebra, or authored event name. |
