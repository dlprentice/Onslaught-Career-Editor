# IScript__IsObjective

> Address: `0x00535EF0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 31, registered as `IsObjective`: the query twin
of the Set/Unset pair. Zero script arguments; reads the attached thing's
objective bit through `CComplexThing` vtable slot 13 (`+0x68`,
`0x004014e0`: `(byte[thing+0x2c] & 0x20) >> 5`) and boxes the result as
a `CBool` (vptr `0x005e4d50`, byte payload at +4). 9 authored sites, all
TargetZone/FiringRange scripts.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, slot walk, authored `.msl` recount.
No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 31 is `IsObjective` / `0x00535EF0` / empty name-table
cell / 9 sites; confirmed this wake. Registration:

- Handler immediate: `mov edi, 0x00535ef0` (`bf f0 5e 53 00`) at VA
  `0x005309c9` — exactly **one** image-wide imm32 (byte hit at
  `0x005309ca`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d610], edi` at VA `0x005309d8`.
- Name-pointer store: `mov dword ptr [0x64d5e0], 0x64f8d0` at VA
  `0x00530a71`; `.rdata 0x64f8d0` = `"IsObjective\0"`.
- Descriptor: name cell `0x64d5e0`, handler cell +0x30 at `0x64d610`.

## Contract (byte-exact)

Body `0x00535ef0`–`0x00535f6f` inclusive through the complete final
`ret 0xc`, **128 bytes**, SHA-256
`3d3daf9668d78a0064b70bde3b6c696ec522ae319055ed89e8850d60f475344f`.
Two internal `E8`, both to the shared allocator helper `0x005490e0`
(one per return path), zero decoded `E9`.

```
00535ef0  8b 49 10           mov ecx, [ecx+0x10]        ; attached thing
00535ef3  8b 01              mov eax, [ecx]
00535ef5  ff 50 68           call [eax+0x68]            ; slot 13 predicate
00535ef8  85 c0              test eax, eax
00535efa  je 0x535f36                                   ; false path
true path @0x00535efc:
          push 0x565; push 0x64fa40 (__FILE__); push 0x18; push 8
          mov ecx, 0x9c3df0; call 0x5490e0            ; CDXMemoryManager alloc
          test eax,eax; je null-out
          mov ecx, [esp+0xc]
          mov dword ptr [eax], 0x005e4d50             ; CBool vptr
          mov byte  ptr [eax+4], 1                    ; payload TRUE
          mov dword ptr [ecx], eax                    ; out = object
          ret 0xc
false path @0x00535f36:
          identical alloc with line token 0x569;
          mov dword ptr [eax], 0x005e4d50
          mov byte  ptr [eax+4], 0                    ; payload FALSE
```

Both paths are the same boxed-return shape as native 18 GetHealth's
`CFloat` boxing (`IScript.cpp.md` Functions table), with a `CBool`
(vptr `0x005e4d50`) instead.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing (no gate) | `0x00535ef0` |
| thing `vtable[+0x68]` | objective-bit predicate slot 13 | `0x00535ef5` |
| `[thing+0x2c]` bit `0x20` | the objective flag (read via predicate) | `0x004014e0` |
| `0x005e4d50` / `+4 byte` | `CBool` vptr / payload | `0x00535f1c`, `0x00535f56` |
| `0x64d5e0` / `0x64d610` | registration descriptor cells | `0x00530a71`, `0x005309d8` |

Slot identity: the predicate at `0x004014e0` occupies exactly 26
`.rdata` vtables (thing-hierarchy-wide), consistent with slot 13 of a
26+-slot shared layout; on `CComplexThing` it sits at `0x5df784+0x68 =
0x5df7ec`. The bit it reads is the same one
[`IScript__SetObjective.md`](IScript__SetObjective.md)'s setter
maintains — the three natives close a state machine: set/clear mutate,
query observes.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**9 active sites in 9 files** (`level022`/`level100` TargetZone*.mssl +
FiringRange.msl). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet; shares the future owner with Set/UnsetObjective.
Observable contract: returns the live flag value at call time, boxed as
CBool. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535ef0`–`0x00535f6f` is not
  `3d3daf96…75344f`, or the slot call leaves `[+0x68]`.
- A second image-wide imm32 of `0x00535ef0`, or any rel32 inbound.
- The handler store leaves `0x64d610`, or `.rdata 0x64f8d0` stops being
  `"IsObjective\0"`.
- The predicate body at `0x004014e0` changes its shift/mask.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, slot census, authored
  `.msl` recount (`local-lab/famE_*.py`).
- Cross-reference (same wake):
  [`IScript__SetObjective.md`](IScript__SetObjective.md),
  [`IScript__UnsetObjective.md`](IScript__UnsetObjective.md),
  [`IScript__SetVisible.md`](IScript__SetVisible.md).
