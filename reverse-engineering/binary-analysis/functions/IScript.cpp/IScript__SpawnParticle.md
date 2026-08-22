# IScript__SpawnParticle

> Address: `0x00536B70`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 50, registered as `SpawnParticle`: two
arguments — a name string (`vtable[+0x38]`) and a position
(`vtable[+0x44]` out-record) — forwarded to particle-system factory
`0x004cd7a0` on the manager singleton `0x0082b400`; unknown names print
a console warning and no-op. Six authored uses, all hive boss effects.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 50 is `SpawnParticle` / `0x00536B70` / empty name-table
cell / 6 authored sites; confirmed this wake. Registration:

- Handler immediate: `bf 70 6b 53 00` (`mov edi, 0x00536b70`) at VA
  `0x0053107c` — exactly **one** image-wide imm32 (byte hit at
  `0x0053107d`). Zero rel32 inbound.
- Handler cell store: `mov [0x64da14], edi` at VA `0x00531081`.
- Name-pointer store: `mov dword ptr [0x64daa0], 0x64f79c` at VA
  `0x0053115e`; `.rdata 0x64f79c` = `"SpawnParticle\0"`.
- Descriptor: name cell `0x64daa0`, handler cell +0x30 at `0x64dad0`
  (the stride-paired handler cell; its store is register-carried in the
  same block).

## Contract (byte-exact)

Body `0x00536b70`–`0x00536bb8` inclusive through the complete final
`ret 0xc`, **73 bytes**, SHA-256
`19368ba11e894b5d42c0f4cfbb05fdd1587a6a9e3639c8f527c42b7931b76b93`.
One internal `E8` (the factory), zero decoded `E9`.

```
00536b75  mov edi, [esp+0x1c]             ; args object
          mov ecx, [edi]; call [eax+0x38] ; arg1 name -> eax
00536b80  mov ecx, [edi+4]                ; arg2 element
00536b85  lea eax, [esp+8]; push eax
00536b8c  call [edx+0x44]                 ; vector eval into out
00536b8f  push esi (name); mov ecx, 0x0082b400
00536b95  call 0x004cd7a0                 ; spawn(name, pos) -> eax
00536b9c  test eax, eax; jne done
          push name; push 0x0064fd04 (__FILE__); push 0x0066f580
00536ba9  call 0x00441740                 ; CConsole__Printf warning
done:     ret 0xc
```

No class gate on the thing; the native works from any script context.
The factory's lookup semantics (name → effect template) are not walked
this wake.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `args[0]` via `vtable[+0x38]` | effect name string | `0x00536b7d` |
| `args[1]` via `vtable[+0x44]` | world-position record | `0x00536b8c` |
| `0x0082b400` | particle-manager singleton | `0x00536b90` |
| `0x004cd7a0` | spawn factory | `0x00536b95` |
| `0x64daa0` / `0x64dad0` | registration descriptor cells | `0x0053115e`, stride |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**6 active sites** — `level521/522/530 hive.msl` ×2 each
(`"Hive Boss Power Spike Effect"`, `"Hive Boss Launch Effect"`).
Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: named-effect lookup + world-spawn
with warn-and-noop on miss. Focused test deferred until that owner
exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00536b70`–`0x00536bb8` is not
  `19368ba1…31b76b93`, or the factory leaves `0x004cd7a0` / singleton
  leaves `0x0082b400`.
- A second image-wide imm32 of `0x00536b70`, or any rel32 inbound.
- The handler store leaves `0x64da14`, or `.rdata 0x64f79c` stops being
  `"SpawnParticle\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famI_final*.py`).
