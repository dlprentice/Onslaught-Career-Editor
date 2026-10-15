# IScript__GetWeaponName

> Address: `0x00535670`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 38, registered as `GetWeaponName`: zero script
arguments; behind the class-bit-`0x08` gate, calls weapon-name getter
`0x0040c570` and clones the returned string into a `CStringDataType`
(vptr `0x005e4e4c`) via the clone helper `0x0052f690`; alloc failure or
gate miss yields an out-null. SEH-framed. Zero authored uses.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, callee walks, authored `.msl`
recount (`local-lab/famG_weapons*.py`). No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 38 is `GetWeaponName` / `0x00535670` / empty name-table
cell / 0 sites; confirmed this wake (recount zero). Registration:

- Handler immediate: `mov edi, 0x00535670` at VA `0x00530ce0` —
  exactly **one** image-wide imm32. Zero rel32 inbound.
- Handler cell store: `mov [0x64d7d0], edi` at VA `0x00530ce9`.
- Name-pointer store: `mov dword ptr [0x64d7a0], 0x64f854`;
  `.rdata 0x64f854` = `"GetWeaponName\0"`.
- Descriptor: name cell `0x64d7a0`, handler cell +0x30 at `0x64d7d0`.

## Contract (byte-exact)

Body `0x00535670`–`0x005356e2` inclusive through the complete final
`ret 0xc`, **115 bytes**, SHA-256
`88b7f8cd5c890ccc99e58690376de952447576c3f5bbd6303644db3af3582472`.
SEH frame installed (`push -1 / push 0x005d7072 / fs:[0]` dance) and
torn down on every exit.

```
00535687  mov edi, [ecx+0x10]             ; attached thing
0053568a  test byte ptr [edi+0x34], 8     ; class bit 0x08 gate
0053568e  je null-out-tail (0x5356fe)
          alloc 0x18 via 0x5490e0 (__FILE__ 0x64fa40, line 0x424)
          test eax,eax; mov [esp+0x14], 0 ; je null-out
005356bd  mov ecx, edi; call 0x0040c570   ; char* weapon name -> eax
005356c2  push eax; mov ecx, esi; call 0x0052f690  ; CStringDataType clone
          mov ecx, [esp+0x24]; mov [ecx], eax      ; out = string object
          ret 0xc
null-out: mov dword ptr [out], 0; ret 0xc
```

The clone target `0x0052f690` installs vptr `0x005e4e4c` — exactly the
`CStringDataType` vtable pinned in [`IScript.cpp.md`](../IScript.cpp.md)
(the event-name key object's class). So this native returns a proper
script string value.

## Weapon-name getter `0x0040C570` (read)

```
0040c570  cmp dword ptr [ecx+0x260], 3    ; configuration == 3?
0040c577  je use +0x57c                   ; jet-side name table
0040c579  mov ecx, [ecx+0x578]            ; walker-side name table
0040c57f  jmp 0x004145d0                  ; fetch name from table
```

A configuration selector over `[thing+0x260]` with two per-mode name
tables at `[thing+0x578]`/`[thing+0x57c]` — same configuration-dual
shape the Family C ResetConfiguration work recorded for the weapon
runtime. Table-entry fetchers not walked further.

## Callers

Zero rel32 inbound; dispatch-table-only; zero authored uses.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: configuration-selected weapon name,
returned as a cloned script string; the dual-table selector is part of
the observable contract. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535670`–`0x005356e2` is not
  `88b7f8cd…af3582472`, or either callee leaves `0x0040c570`/`0x0052f690`.
- A second image-wide imm32 of `0x00535670`, or any rel32 inbound.
- The handler store leaves `0x64d7d0`, or `.rdata 0x64f854` stops being
  `"GetWeaponName\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famG_weapons*.py`).
- Cross-reference (same wake):
  [`IScript__GetWeaponAmmo.md`](IScript__GetWeaponAmmo.md),
  [`IScript__GetWeaponCharge.md`](IScript__GetWeaponCharge.md).
