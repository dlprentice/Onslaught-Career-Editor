# CGeneralVolume__DispatchSelectedBurstPreset

Status: active static function note
Last updated: 2026-08-19
Source File: none under this table name | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake already landed charge sibling `0b5f9914` — not redone.
Envelope. Did not mill FUN_*. Did not mill Get*. Did not rewrite
this table name. Did not equate source
`CBattleEngineJetPart::FireWeapon`. Did not invent a Core owner.

> Address: `0x00411b90`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx+0x18]`. Two
bare `ret` (`0x00411bd3`, `0x00411bea`). Body
`0x00411b90`–`0x00411bea` is 91 bytes, SHA-256
`f8ce1178b5554b2311bae865577544f76e684d7296201525bfb28b3f8b686168`.
Capstone: 38 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.
Raw `0xE8` byte count is 1 and matches the instruction count.
Neighbour table
`CGeneralVolume__DispatchMode3BurstProgressAndSpawn` starts at
`0x00411bf0` after a 5-byte `nop` pad and is not rewritten.

Pinned body:

1. `eax = [ecx+0x18]` then store 0 at `[eax+0x588]`. Same
   `[+0x588]` slot walker FireWeapon / the charge sibling
   already write. `[+0x18]` is the already-counted jet
   main-part slot. Those slots are **not** named here.
2. Inlined current-weapon list walk on `[ecx]` / `[ecx+8]` /
   `[ecx+0x10]`. EAX==0 pops ESI and returns. Those slots are
   **not** named here.
3. After the walk match: `[eax+0x9c]==0` returns. Same
   `[+0x9c]` gate walker FireWeapon already counts. **Not**
   named here.
4. Else `ecx = eax` / `E8`
   `ProjectileBurst__SpawnFromPercentBucketFallback`
   `0x00506010`. That table name is counted, not contracted.

One inbound `.text` `E8`/`E9`: `JMP` at `0x00409f6a`. That site
is the already-settled `[ecx+0x260]==3` arm loading
`[ecx+0x57c]` (jet part) in table-named
`CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90`
`0x00409f20`. That parent table name is counted, not rewritten.
Zero encodings of imm `90 1b 41 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngineJetPart::FireWeapon`
`BattleEngineJetPart.cpp:647-656`. Retail bare `ret` matches
zero stack args. Do **not** equate this table name to that
method.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00011b90` is not `8b 41 18`, **or**
`0x00011b95` is not `c7 80 88 05 00 00 00 00 00 00`, **or**
`0x00011be4` is not `e8 27 44 0f 00`, **or** `0x00011bea` is
not `c3`, **or** body SHA-256 is not `f8ce1178…6168`, **or**
`tools/call_xref_scan.py` on `0x00411b90` is not exactly one
`JMP` at `0x00409f6a`, **or** any encoding of imm `90 1b 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `f8ce1178…6168`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x588]` / `[+0x9c]` / `[+0x18]`. Did not walk
ProjectileBurst. Did not equate this table name to source
`FireWeapon`.

Retail entity: jet-part FireWeapon-shaped body from the
`[+0x260]==3` / `[+0x57c]` dispatcher JMP. Stuart architecture
(not proof): `BattleEngineJetPart.cpp:647-656`.

Nearest reconstruction owner: **none** added. L100
playable-training diet — do not implement from this envelope.

Siblings: `CBattleEngineWalkerPart__FireWeapon` /
`CGeneralVolume__DispatchMode3BurstProgressAndSpawn`. Next
named: `ProjectileBurst__SpawnFromPercentBucketFallback`
`0x00506010` (counted by both fire/charge tails; no 2026-08-19
PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00411b90` | `CGeneralVolume__DispatchSelectedBurstPreset` | `8b4118 33d2 c7808805000000000000 … e827440f00 5ec3` (91 B) | incoming-ECX thiscall; bare ret ×2; 91 B; 1 E8 / 0 E9 / 1 target; 1 inbound JMP. HIGH on ABI, `[+0x588]=0`, `[+0x9c]` gate, ProjectileBurst E8, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on table rename or rebuild parity. |
