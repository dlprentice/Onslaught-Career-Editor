# CMissionScriptObjectCode__StartLoadAsync

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`,
`ScriptObjectCode.cpp.md`, or a `CXBOXAsyncCache` rename)
|||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Adopted `t_e0fcea14` after independent
re-read (cycle 48 also re-read the child — this card lands).
The Ghidra database was not opened. Table name is a research
label. Cycle 48 accepted `6fb79dad` / `562fda84` / `1d91b9c9`
/ `a52210d3`; this wake landed `cf4c06f7` / `3ba05cb7` —
not redone. Already-pinned LoadAsync `0x00539ca0` /
FUN_0053a2d0 / FUN_0053a2f0 / FUN_00539e10 / FUN_00539e30 /
ClearFields thunk / `CScriptObjectCode.cpp.md` / InitFields
`0x00539f00` / callee bodies were **not** written. Did not
steal `t_d14c8488`.

> Address: `0x00539dc0`

## Contract

`thiscall`, not SEH. First insn `push ebx`. Incoming ECX is
parked in `EBX` (`8b d9` at `0x00539dc3`). Two stack dwords.
One `ret 8` (`0x00539e02`, `c2 08 00`). Body `0x00539dc0`–
`0x00539e04` is 69 bytes, SHA-256
`69a733ad109dbe5810e42ccd104f865ee52ebfc7f7dc117a3144958392ffc8dd`.
Two `E8`, zero `E9`. Raw `E9`-byte scan also hits `c1 e9 02`
(`shr ecx, 2` at `0x00539de2`); that is not a jump. Eleven
nops after the `ret` are **not** in the body (already-pinned
neighbour `FUN_00539e10` starts at `0x00539e10`).

The body:

1. `E8` `0x00528d10` with `ecx` still this.
2. Copy stack arg0 (`[esp+0x10]` after the three pushes) as a
   NUL-terminated byte string into `this+0x20`
   (`repne scasb` / `rep movsd` / `rep movsb`).
3. Store stack arg1 (`[esp+0x14]`) at `[this+0x124]`.
4. `ecx = this` / `E8` `0x00528d50`.

`EAX` at the `ret` is leftover (last callee). Slot types,
callee names, async completion, and the class of `this` are
**not** this proof.

Two body `E8` sites: `0x00539dc5` `0x00528d10`, `0x00539dfa`
`0x00528d50`.

One inbound `.text` `E8` and zero inbound `E9`: `0x0045cb5d`
inside table `CFEPGoodies__StartLoadingGoody` (not claimed;
table range `0x0045c9f0`–`0x0045cb7d`). Site bytes
`e8 5e d2 0d 00`. Zero image encodings of imm `c0 9d 53 00`.

Cheapest falsifier: file `0x00139dc0` is not `53`,
**or** `0x00139e02` is not `c2 08 00`, **or** body SHA-256 is
not `69a733ad…c8dd`, **or** `tools/call_xref_scan.py` on
`0x00539dc0` is not the one `E8` above, **or**
`0x00139dc5` is not `e8 46 ef fe ff`, **or**
`0x00139dfa` is not `e8 51 ef fe ff`, **or** a second inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539dc0` | `CMissionScriptObjectCode__StartLoadAsync` | `53 56 57 8bd9 e846effeff … 8b7c2410 … 8d5320 f2ae … 8b4c2414 898b24010000 8bcb e851effeff 5f5e5b c20800` | thiscall; ret 8 ×1; 69 B; 2 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, arg0 copy to `[+0x20]`, arg1 store to `[+0x124]`. **Not** on callee bodies, inbound host, or class of this. |
