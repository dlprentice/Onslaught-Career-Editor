# IScript__GetWeaponCharge

> Address: `0x00535750`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 39, registered as `GetWeaponCharge`: byte-for-
byte the native 37 shape (class-bit-`0x08` gate, CFloat boxing, same
alloc line-token pattern) with a different callee — `0x0040c4a0`,
which computes an absolute height-delta quantity against the global
water/terrain level (`0x006fbdfc`) instead of the 2/3-scaled magnitude.
Zero authored uses.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, callee head walk, authored `.msl`
recount. No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 39 is `GetWeaponCharge` / `0x00535750` / empty name-table
cell / 0 sites; confirmed this wake (recount zero). Registration:

- Handler immediate: `mov edi, 0x00535750` at VA `0x00530cfe` —
  exactly **one** image-wide imm32. Zero rel32 inbound.
- Handler cell store: `mov [0x64d810], edi` at VA `0x00530d08`.
- Name-pointer store: `mov dword ptr [0x64d7e0], 0x64f844`;
  `.rdata 0x64f844` = `"GetWeaponCharge\0"`.
- Descriptor: name cell `0x64d7e0`, handler cell +0x30 at `0x64d810`
  (neighbor: `SetAllegiance` behind at name `0x64d860`).

## Contract (byte-exact)

Body `0x00535750`–`0x0053579d` inclusive through the complete final
`ret 0xc`, **78 bytes**, SHA-256
`372c95a58aff3ce63bec5a9de34c85316e0aa1b92cbbe554df5f4761ca3504c9`.
Identical to [`IScript__GetWeaponAmmo.md`](IScript__GetWeaponAmmo.md)
except: callee `0x0040c4a0`, alloc line token `0x437`.

## Weapon getter `0x0040C4A0` (head read)

Same config-string gate as the ammo getter
(`stricmp([this+0x4b0]+0xa8, ".rdata 0x006234f4")` via `0x00568390`),
then on the equal arm:

```
call [esi+8 -> vtable+0](&out)          ; virtual through [thing+8]
call 0x0047eb80(0x006fadc8, &out)       ; CMonitor height sample
fld  dword ptr [0x006fbdfc]             ; global reference level
fcomp st(1); if st1 > ref keep else reload ref
fsub dword ptr [esp+0xc]; fabs          ; |ref - sampled|
```

The quantity is an absolute delta against the shared BSS reference
level at `0x006fbdfc` — the same cell the fire-gate twins compare
against ([`IScript.cpp.md`](../IScript.cpp.md) Functions table,
BallisticArc entries). Full branch structure beyond this head not
walked.

## Callers

Zero rel32 inbound; dispatch-table-only; zero authored uses.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands, pin the measured law (reference-
level delta) rather than the registered name. Focused test deferred
until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535750`–`0x0053579d` is not
  `372c95a5…ca3504c9`, or the callee leaves `0x0040c4a0`.
- A second image-wide imm32 of `0x00535750`, or any rel32 inbound.
- The handler store leaves `0x64d810`, or `.rdata 0x64f844` stops being
  `"GetWeaponCharge\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famG_weapons*.py`).
- Cross-reference (same wake):
  [`IScript__GetWeaponAmmo.md`](IScript__GetWeaponAmmo.md),
  [`IScript__GetWeaponName.md`](IScript__GetWeaponName.md).
