# IScript__GetWeaponAmmo

> Address: `0x00535610`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `GetWeaponAmmo` is absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 37, registered as `GetWeaponAmmo`: zero script
arguments; when the attached thing carries the class bit `0x08` of
`[thing+0x34]`, calls weapon-state getter `0x0040c3c0` and boxes the
returned float as a `CFloat`; otherwise (and on alloc failure) boxes
0.0. Zero authored uses (`DORMANT_CANDIDATE`) — the trio was shipped in
the registry but never called by any retail mission.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, callee head walk, authored `.msl`
recount (`local-lab/famG_weapons*.py`). No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 37 is `GetWeaponAmmo` / `0x00535610` / empty name-table
cell / 0 sites / `DORMANT_CANDIDATE`; confirmed this wake (recount:
zero textual sites). Registration:

- Handler immediate: `mov edi, 0x00535610` at VA `0x00530b9d` —
  exactly **one** image-wide imm32. Zero rel32 inbound.
- Handler cell store: `mov [0x64d790], edi` at VA `0x00530ba6`.
- Name-pointer store: `mov dword ptr [0x64d760], 0x64f864`;
  `.rdata 0x64f864` = `"GetWeaponAmmo\0"`.
- Descriptor: name cell `0x64d760`, handler cell +0x30 at `0x64d790`.

## Contract (byte-exact)

Body `0x00535610`–`0x0053565d` inclusive through the complete final
`ret 0xc`, **78 bytes**, SHA-256
`7e546c5b2807be6809ad8e8bef3ea3218b90600613d1fc2dae9de0428d3ea4b3`.

```
00535610  push ecx; mov ecx, [ecx+0x10]   ; attached thing
00535614  mov dword ptr [esp], 0          ; default result 0.0f
0053561c  test byte ptr [ecx+0x34], 8     ; class bit 0x08 gate
00535620  je skip
00535622  call 0x0040c3c0                 ; weapon ammo float -> st0
00535627  fstp dword ptr [esp]
skip:
0053562b  push 0x41b; push 0x64fa40 (__FILE__); push 0x18; push 8
          mov ecx, 0x9c3df0; call 0x5490e0        ; CDXMemoryManager alloc
          test eax,eax; je null-out
          mov dword ptr [eax], 0x005e4ea4         ; CFloat vptr
          mov eax, [esp]                          ; boxed value
          mov dword ptr [ecx], eax                ; out = object
          ret 0xc
```

Same CFloat boxing shape as native 18 GetHealth
([`IScript.cpp.md`](../IScript.cpp.md)); the gate differs — class bit
**`0x08`** of `[thing+0x34]`, not the UNIT bit `0x10` the segment
family uses. The bit's authored class name is open (weapon-bearing /
BattleEngine-family marker by occupancy).

## Weapon getter `0x0040C3C0` (head read)

`thiscall`, float return in ST0. Gates on a config string first:
`stricmp(0x00568390, "[this+0x4b0]+0xa8", ".rdata 0x006234f4")` — the
string at `0x006234f4` decodes as an empty/short literal this wake
(config-name compare); if equal it falls through to the arithmetic
below, otherwise branches away (not fully walked):

```
call [this-vtable+0x6c](&out)      ; out = three floats (+0/+4/+8)
st0 = sqrt(f0² + f1² + f2²) * 0.6666667f   (const 0x005d8c64)
```

then compares against `1.0f` (`0x005d8568`) — a normalized-magnitude
law scaled by 2/3, not a raw bullet count. Honest unknowns: the full
branch structure after the compare, and what `[thing+0x4b0]` (a
config object; same field ResetConfiguration's caller guards) holds.
The name "ammo" is the registration string only — the body computes a
clamped magnitude-style quantity.

## Callers

Zero rel32 inbound; dispatch-table-only; zero authored uses.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands, pin the *measured* law above rather
than the registered name; the 2/3-scaled magnitude is the observable
contract for this slice. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535610`–`0x0053565d` is not
  `7e546c5b…d3ea4b3`, or the callee leaves `0x0040c3c0` or the vptr
  leaves `0x005e4ea4`.
- A second image-wide imm32 of `0x00535610`, or any rel32 inbound.
- The handler store leaves `0x64d790`, or `.rdata 0x64f864` stops being
  `"GetWeaponAmmo\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famG_weapons*.py`).
- Cross-reference (same wake):
  [`IScript__GetWeaponName.md`](IScript__GetWeaponName.md),
  [`IScript__GetWeaponCharge.md`](IScript__GetWeaponCharge.md).
