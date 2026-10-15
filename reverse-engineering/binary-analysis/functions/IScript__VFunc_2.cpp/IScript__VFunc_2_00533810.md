# IScript__VFunc_2_00533810

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
label. Callee bodies `0x00539980` / `0x00539990` and
`IScript.cpp.md` were **not** written. Sibling wrappers
`0x005335a0` / `0x00533660` / `0x005337e0` were **not**
re-done.

> Address: `0x00533810`

## Contract

`thiscall`. Reads `[ecx+0xc]`. Zero stack args. Bare `ret` at
`0x0053383a`. Body `0x00533810`–`0x0053383a` is 43 bytes,
SHA-256
`390b06069f39b83e6e7fa41b5f3364000f26b33de0463f694415b0cd19dcdfcf`.
One `E9` (`0x0053381e` → table `CScriptObjectCode__Reset`
`0x00539980`) when `[0x008a9ac0] == 4`. One `E8`
(`0x00533835` → table `CScriptObjectCode__CallEvent`
`0x00539990`) after `push 0`, `push 0x0089c528`, `push 7`,
`push [this+0xc]`, `ecx = 0x0089c5e0`. Those callee bodies
and the authored event name are **not** this proof.

Zero inbound `.text` `E8`/`E9`. Imm `10 38 53 00` occurs
once, at `0x005e4f10`. That site is **not** this body.

Cheapest falsifier: file `0x00133810` is not
`83 3d c0 9a 8a 00 04`, **or** `0x0013383a` is not `c3`,
**or** body SHA-256 is not `390b0606…dfcf`, **or**
`tools/call_xref_scan.py` on `0x00533810` is not zero
`E8`/`E9`, **or** `0x0013382d` is not `6a 07`, **or**
`0x0013381e` is not `e9 5d 61 00 00`, **or** the image
contains a second `10 38 53 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00533810` | `IScript__VFunc_2_00533810` | `833dc09a8a0004 750a b9e0c58900 e95d610000 8b410c 6a00 6828c58900 6a07 … e856610000 c3` | thiscall; bare ret; 43 B; 1 E9 Reset `0x00539980` if `[0x008a9ac0]==4`; 1 E8 CallEvent `0x00539990` with imm 7; 0 inbound E8/E9; unique imm at `0x005e4f10`. HIGH on ABI, that cmp, that push 7, inbound-empty. **Not** on callee bodies, authored event name, or vtable identity. |

## Moved from developer_state.json (_HERMES_SLICE_20260819_533810) — original wording preserved (2026-08-23):

Hermes integration-owner. Independently re-read official 74154bfa. VM-family 0x00533810 thiscall bare ret, 43 B sha 390b0606, 1 E9 Reset 0x00539980 when [0x008a9ac0]==4, 1 E8 CallEvent 0x00539990 push 7, 0 inbound E8/E9. Unique imm at 0x005e4f10. New folder — did not pile IScript.cpp.md. Steward cycle 34 forbade completing this keep-going root. Did not steal t_f082a4e9 / t_9e2c3720 / t_11bcf1cf. No Ghidra, no Core.
