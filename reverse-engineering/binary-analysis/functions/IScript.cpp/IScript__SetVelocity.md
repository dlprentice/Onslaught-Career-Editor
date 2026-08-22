# IScript__SetVelocity

> Address: `0x00534340`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 129, registered as `SetVelocity`: UNIT-gated;
evaluates one positional/vector argument through element `vtable[+0x44]`
into a 16-byte out record, then passes it to the attached thing's
velocity setter vtable slot 28 (`+0x70`). Two authored uses (the
level621/622 ejector seats).
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount
(`local-lab/famH_micro*.py`). No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 129 is `SetVelocity` / `0x00534340` / empty name-table
cell / 2 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov ebp, 0x00534340` (`bd 40 43 53 00`) at VA
  `0x00532e2c` — exactly **one** image-wide imm32 (byte hit at
  `0x00532e2d`). Zero rel32 inbound.
- Handler cell store: `mov [0x64ee90], ebp` at VA `0x00532e31`.
- Descriptor: handler cell `0x64ee90`; the stride-paired name cell is
  `0x64ee60`, whose pointer store is register-carried in this block
  (the `.rdata` `"SetVelocity\0"` string exists; its storing `c7 05`
  was not individually located — honest gap, cheapest instrument is a
  full decode of the descriptor-fill run around `0x00532dxx`).
- Neighbors: `HalfDestroy` (128) handler cell `0x64ee50`;
  `TeleportOrientation` (139) `0x64eed0`.

## Contract (byte-exact)

Body `0x00534340`–`0x0053436d` inclusive through the complete
`ret 0xc`, **46 bytes**, SHA-256
`213d51e612411680f7993dde3c5e6cd763423ce88620e2bcf79589389e890711`.
Zero `E8`, zero decoded `E9`.

```
00534340  sub esp, 0x10; push esi
00534344  mov esi, [ecx+0x10]             ; attached thing
00534347  test byte ptr [esi+0x34], 0x10  ; UNIT class bit
0053434b  je exit                         ; -> bare return
          mov edi, [esi]
          mov ecx, [args]                 ; element 1
          lea eax, [esp+8]; push eax
          call [edx+0x44]                 ; vector eval into out
00534360  push eax                        ; out record
00534361  mov ecx, esi
00534363  call [edi+0x70]                 ; thing slot 28 setter
exit:     add esp, 0x10; ret 0xc
```

The `[+0x44]` element evaluator writes a multi-dword record (the same
slot `SetPos` uses for its position argument), and thing slot 28
(`+0x70`) receives it — the velocity apply point proper.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` / `[thing+0x34]&0x10` | shared UNIT gate | `0x00534347` |
| `args[0]` via `vtable[+0x44]` | vector out-record eval | `0x0053534f` region (`ff 52 44`) |
| thing `vtable[+0x70]` | velocity setter slot 28 | `0x00534363` |
| `0x64ee60` / `0x64ee90` | descriptor cells (name side inferred by stride) | `0x00532e31` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**2 active sites** — `level621/Ejector.msl`, `level622/Ejector.msl`
(`SetVelocity(pos)`). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: script-driven impulse/velocity set
through a thing-level hook, UNIT-gated. Focused test deferred until
that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00534340`–`0x0053436d` is not
  `213d51e6…890711`, or either vtable offset leaves `[+0x44]`/`[+0x70]`.
- A second image-wide imm32 of `0x00534340`, or any rel32 inbound.
- The handler store leaves `0x64ee90`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famH_micro*.py`).
