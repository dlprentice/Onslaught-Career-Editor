# IScript__SpawnEscapePod

> Address: `0x005371E0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 132, registered as `SpawnEscapePod`: zero
script arguments; a 556-byte SEH-framed orchestrator that resolves the
attached thing's name-list carrier (`[thing+0x30]`, same carrier the
segment dispatches use), calls its `vtable[+0x1c]` with the literal
name at `.rdata 0x0064fd24`, then builds an 0xe8-byte object through
the debug allocator. Four authored uses, all level741/742 escape-pod
cutscenes.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly (head + shape), raw byte reads, image-wide imm32 census,
descriptor walk, whole-`.text` rel32 xref scan, authored `.msl` recount.
No `FUN_*` milled; full body walk not claimed.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 132 is `SpawnEscapePod` / `0x005371E0` / empty name-table
cell / 4 authored sites; confirmed this wake. Registration:

- Handler immediate: `bd e0 71 53 00` (`mov ebp, 0x005371e0`) at VA
  `0x00532e89` — exactly **one** image-wide imm32 (byte hit at
  `0x00532e8a`). Zero rel32 inbound.
- Handler cell store: `mov [0x64ef50], ebp` at VA `0x00532e8e`.
- Name-pointer store: `mov dword ptr [0x64ef20], 0x64f2cc` at VA
  `0x00532f5a`; `.rdata 0x64f2cc` = `"SpawnEscapePod\0"`.
- Descriptor: name cell `0x64ef20`, handler cell +0x30 at `0x64ef50`.

## Contract (measured head; body not fully walked)

Body `0x005371e0`–`0x0053740b` inclusive through the complete final
`ret 0xc`, **556 bytes**, SHA-256
`444f98f24256f66428bc26861568b9a2f531738ac981e0ee0db10f2f2adb39fd`.
SEH-framed; 0x410-byte stack frame.

```
005371ff  mov eax, [ebx+0x10]             ; attached thing
00537202  mov ecx, [eax+0x30]             ; name-list carrier
00537207  test ecx, ecx; je exit          ; no carrier -> bail
00537224  call [edx+0x1c]                 ; carrier vtable slot 7:
          args (&out, 1, ".rdata 0x0064fd24", 0, 0)
0053723a  alloc 0xe8 via 0x5490e0 (__FILE__ 0x00662b2c, line 0)
```

The literal string argument at `0x0064fd24` is the pod thing-name this
native spawns (its exact text is in the specimen's data section; the
spawn path beyond the allocator is not walked this wake). The carrier +
slot shape mirrors the segment family's `[this+0x10]→[+0x30]` law.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` → `[thing+0x30]` | name-list carrier (null-checked) | `0x00537202` |
| `.rdata 0x0064fd24` | pod spawn-name literal | `0x0053721f` |
| carrier `vtable[+0x1c]` | spawn-by-name slot 7 | `0x00537224` |
| `0x64ef20` / `0x64ef50` | registration descriptor cells | `0x00532f5a`, `0x00532e8e` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**4 active sites in 4 files** (`level741/742 Cutscene_Lost.msl` and
`camera.msl`; bare `SpawnEscapePod()` calls). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: fixed-name pod spawn behind a
carrier-presence gate; the remaining body is a follow-up question, not
a blocker for the owner's contract. Focused test deferred until that
owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005371e0`–`0x0053740b` is not
  `444f98f2…adb39fd`, or the carrier slot leaves `[+0x1c]`.
- A second image-wide imm32 of `0x005371e0`, or any rel32 inbound.
- The handler store leaves `0x64ef50`, or `.rdata 0x64f2cc` stops being
  `"SpawnEscapePod\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly (head),
  raw byte reads, imm32/rel32 censuses, descriptor walk, authored
  `.msl` recount (`local-lab/famI_final*.py`).
