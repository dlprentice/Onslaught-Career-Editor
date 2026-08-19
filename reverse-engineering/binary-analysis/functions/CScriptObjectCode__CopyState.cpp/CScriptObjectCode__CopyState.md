# CScriptObjectCode__CopyState

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
name is a research label. Already-pinned `RestoreStack` /
`CScriptObjectCode.cpp.md` / the inbound hosts were **not** written.

> Address: `0x00539910`

## Contract

`thiscall`. First insn `push esi` / `push edi` /
`mov edi, [esp+0xc]` / `mov esi, ecx`. One stack dword
(source VM). One `ret 4` site (`0x00539974`). Body
`0x00539910`–`0x00539976` is 103 bytes, SHA-256
`775583d8569f0bb6ccc0827023730ac975d19f3b4f8d494e437f4553e7d374e8`.
One `E8`, zero `E9`. Nine nops after the last `ret 4` are
**not** in the body (already-pinned neighbour
`CScriptObjectCode__Reset` starts at `0x00539980`).

Incoming ECX is the destination VM. The body stores
`[dst+8] = [src+8]`, `[dst+0x214] = [src+0x214]`, then
`push src+0xc` / `lea ecx, [dst+0xc]` / `E8`
already-pinned `CScriptObjectCode__RestoreStack`
`0x00539350` (`0x00539931`). Then
`[dst+0x218] = [src+0x218]`,
`[dst+0x220] = [src+0x220]`,
`[dst+0x21c] = [src+0x21c]`,
`[dst+0x224] = [src+0x224]`, and
`[dst+0x210] = 0` (zeroed; **not** copied from source).
`EAX = dest`. The RestoreStack callee body is **not**
this proof. Offset names already pinned on other notes
are research labels here.

Three inbound `.text` `E8`, zero `E9`: `0x00533850`
already-pinned `IScript__RestoreSavedStateAndGotoInstruction`,
`0x0053852a` (table `CScriptEventNB__UpdateWaypointFollowing`,
not claimed), `0x0053864f` (table `IScript__HandleMessage`,
not claimed). All three plant `ecx = 0x0089c5e0` then
push the source. Zero image encodings of imm
`10 99 53 00`.

Cheapest falsifier: file `0x00139910` is not `56 57`,
**or** `0x00139974` is not `c2 04 00`, **or** body
SHA-256 is not `775583d8…74e8`, **or**
`tools/call_xref_scan.py` on `0x00539910` is not the
three `E8` above, **or** `0x00139931` is not
`e8 1a fa ff ff`, **or** `0x00139966` is not
`c7 86 10 02 00 00 00 00 00 00`, **or** a fourth inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539910` | `CScriptObjectCode__CopyState` | `56 57 8b7c240c 8bf1 8b4708 8d570c 894608 8b8f14020000 898e14020000 52 8d4e0c e81afaffff … c7861002000000000000 8bc6 5f 5e c20400` | thiscall; ret 4 ×1; 103 B; 1 E8 already-pinned RestoreStack / 0 E9; 3 inbound E8. HIGH on ABI, inbound set, the six dword copies, `+0x210` store-0, EAX=dest. **Not** on RestoreStack internals or the two unpinned hosts. |
