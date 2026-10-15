# IScript__SetHealth

> Address: `0x00535C10`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 46, registered as `SetHealth`: UNIT-gated; one
float element through `vtable[+0x34]`, scaled by the profile factor
`[[thing+0x164]+0xc0]`, stored to the thing's life cell
`[thing+0xf8]` — the same cell the damage path repairs and the getter
thunks fall back to. Three authored uses.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount
(`local-lab/famI_final*.py`). No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 46 is `SetHealth` / `0x00535C10` / empty name-table
cell / 3 authored sites; confirmed this wake. Registration:

- Handler immediate: `bf 10 5c 53 00` (`mov edi, 0x00535c10`) at VA
  `0x00530f01` — exactly **one** image-wide imm32 (byte hit at
  `0x00530f02`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d9d0], edi` at VA `0x00530f0b`.
- Name-pointer store: `mov dword ptr [0x64d9a0], 0x64f7d8` at VA
  `0x00530fc7`; `.rdata 0x64f7d8` = `"SetHealth\0"`.
- Descriptor: name cell `0x64d9a0`, handler cell +0x30 at `0x64d9d0`.

## Contract (byte-exact)

Body `0x00535c10`–`0x00535c3e` inclusive through the complete
`ret 0xc`, **47 bytes**, SHA-256
`d078ab8bb31e678b1b12f1c1cbdd19812d6af450d7e383c15b26e658b1f8ac02`.
Zero `E8`, zero decoded `E9`.

```
00535c10  push esi
00535c11  mov esi, [ecx+0x10]             ; attached thing
00535c14  test byte ptr [esi+0x34], 0x10  ; UNIT class bit
00535c18  je exit
          mov eax, [args]; mov ecx, [eax]
00535c22  call [edx+0x34]                 ; float eval -> st0
00535c25  mov eax, [esi+0x164]            ; unit profile object
00535c2b  test eax, eax; je exit
00535c2f  fmul dword ptr [eax+0xc0]       ; * profile health factor
00535c35  fstp dword ptr [esi+0xf8]       ; life cell
exit:     pop esi; ret 0xc
```

The `[thing+0x164]` profile object and its `+0xc0` scale factor are the
same fields the CUnitAI notes consume ([`IScript.cpp.md`](../IScript.cpp.md)
Waypoint section); `[thing+0xf8]` is the life cell `CUnit__ApplyDamage`
repairs for non-positive damage and the sibling thunk `0x004f9a40`'s
no-controller fallback returns.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` / `[thing+0x34]&0x10` | shared UNIT gate | `0x00535c14` |
| `args[0]` via `vtable[+0x34]` | float fraction/value | `0x00535c22` |
| `[thing+0x164]+0xc0` | profile health-scale factor | `0x00535c2f` |
| `[thing+0xf8]` | thing life cell | `0x00535c35` |
| `0x64d9a0` / `0x64d9d0` | registration descriptor cells | `0x00530fc7`, `0x00530f0b` |

Authored uses pass raw values (`SetHealth(500)`) and a near-zero
(`SetHealth(0.001)`) — the script value is multiplied by the profile
factor before landing in the life cell, so authored numbers are
profile-relative.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**3 active sites** (`level331/332 Carrier.msl`, `level500
Level500script.msl`). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet; the Level100 actor-health registry is a different
slice (per-actor ints, no profile scaling). Focused test deferred until
an owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535c10`–`0x00535c3e` is not
  `d078ab8b…1f8ac02`, or the scale cell leaves `+0xc0` / store leaves
  `[+0xf8]`.
- A second image-wide imm32 of `0x00535c10`, or any rel32 inbound.
- The handler store leaves `0x64d9d0`, or `.rdata 0x64f7d8` stops being
  `"SetHealth\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famI_final*.py`).
