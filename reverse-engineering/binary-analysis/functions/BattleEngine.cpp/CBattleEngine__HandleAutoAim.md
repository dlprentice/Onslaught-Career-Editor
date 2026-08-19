# CBattleEngine__HandleAutoAim

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
92 accepted StartLock/LockHit — not redone. This wake landed
`eed9a440` HandleEvent — not redone. Envelope, not a 652-instruction
walk. Did not mill FUN_*. Did not implement lock sets.

> Address: `0x0040b6d0`

## Contract

Incoming-ECX `thiscall`. First insn `push -1` (SEH cookie). One
`ret 0x4` at `0x0040bfbf`. Body `0x0040b6d0`–`0x0040bfc1` is
2290 bytes, SHA-256
`f00d0f3a2cd6d056b9b2feaf5ac42efe9b6ecc6e2e6c9ed0e9005ec81df3a97b`.
Capstone: 652 insns, 26 `E8`, 2 `E9`, 15 unique rel32 targets.
Neighbour table `CBattleEngine__StartDieProcess` starts at
`0x0040bfd0` and is not rewritten. Preceding table
`AngleDifference` ends at `0x0040b6ca` and is not rewritten.

Pinned prologue:

1. SEH frame (`push 0x005d1268` / `fs:[0]`), then `sub esp, 0xc0`.
2. `ebp = ecx`. `mov eax, [ebp]` / `call dword [eax+0x1d4]`.
   That vcall is **not** named here.
3. Five `E8` `CGenericActiveReader__SetReader` `0x00401000` in
   the body (count only). Other of the 15 targets are counted,
   not contracted.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x004058ba` inside
table `CBattleEngine__Init` `0x00404dd0`–`0x004058f9`; `CALL` at
`0x0040c2ad` inside table `CBattleEngine__HandleEvent` (the
`0x1773` arm already pinned). Zero encodings of imm
`d0 b6 40 00` in the image.

Source architecture (not proof): `CBattleEngine::HandleAutoAim`
`BattleEngine.cpp:2446+` (`CEvent* inEvent`). `Init` calls
`HandleAutoAim(NULL)`; HandleEvent passes the event. Retail
`ret 0x4` matches one stack arg.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000b6d0` is not `6a ff`, **or**
`0x0000b6f4` is not `ff 90 d4 01 00 00`, **or** `0x0000bfbf` is
not `c2 04 00`, **or** body SHA-256 is not `f00d0f3a…a97b`, **or**
`tools/call_xref_scan.py` on `0x0040b6d0` is not exactly those
two `CALL`s, **or** a third `.text` `E8`/`E9` to this entry
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `f00d0f3a…a97b`. `call_xref_scan` still two `CALL`s.
Did not open Ghidra. Did not edit `rebuild/**`. Did not walk all
26 callees.

Retail entity: auto-aim tick from Init and from HandleEvent.
Stuart architecture (not proof): `BattleEngine.cpp:2446+`.

Nearest reconstruction owner: **none**. Core has no auto-aim
event path.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement this from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__HandleEvent` in this folder. Next named:
`CBattleEngine__Init` `0x00404dd0` (the other inbound; existing
note, no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040b6d0` | `CBattleEngine__HandleAutoAim` | `6aff 6868125d00 … ff90d4010000 … c20400` (2290 B) | incoming-ECX thiscall; SEH; ret 0x4 ×1; 2290 B; 26 E8 / 2 E9 / 15 targets; 2 inbound Init+HandleEvent. HIGH on ABI, unique two-site inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on vcall `+0x1d4` name or rebuild parity. |
