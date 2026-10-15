# IScript__SetPos

> Address: `0x00536C70`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 135, registered as `SetPos`: no class gate;
evaluates one positional argument through element `vtable[+0x44]` into
a 16-byte out record, then passes it to the attached thing's position
setter vtable slot 20 (`+0x50`). Zero authored uses
(`DORMANT_CANDIDATE`) — scripts move things with Teleport instead.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 135 is `SetPos` / `0x00536C70` / empty name-table cell /
0 sites; confirmed this wake (recount zero). Registration (this block's
stores are register-carried and interleaved):

- Handler immediate: `bf 70 6c 53 00` (`mov edi, 0x00536c70`) at VA
  `0x00532fc7` — exactly **one** image-wide imm32 of `0x00536c70`.
  Zero rel32 inbound.
- Handler cell store: `mov [0x64f010], edi` at VA `0x00532fce`.
- Name cell: stride-paired `0x64efe0`; the `"SetPos\0"` string exists
  in `.rdata`; its individual storing instruction was not isolated in
  this interleaved block — honest gap, same note as SetVelocity.
- Neighbors: `SetSlotSave` (133) handler cell `0x64ef90`;
  `SetLockable` (136) `0x64f050`.

## Contract (byte-exact)

Body `0x00536c70`–`0x00536c99` inclusive through the complete
`ret 0xc`, **42 bytes**, SHA-256
`1a1ecfe8dde56ad132cc0a5d05010ebe43936f01602cc47012e4826c55ff9fa1`.
Zero `E8`, zero decoded `E9`.

```
00536c70  mov eax, [esp+4]                ; args object
00536c77  mov ecx, [eax]                  ; element 1
00536c83  call [edx+0x44]                 ; vector eval into out record
00536c86  mov ecx, [esi+0x10]             ; attached thing (no gate)
00536c8d  push out; call [edx+0x50]       ; thing slot 20 setter
00536c97  ret 0xc
```

Slot pairing mirrors SetVelocity (`[+0x44]` eval → thing slot), with
slot **20** (`+0x50`) as the position apply point.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing (no gate) | `0x00536c86` |
| `args[0]` via `vtable[+0x44]` | position vector eval | `0x00536c83` |
| thing `vtable[+0x50]` | position setter slot 20 | `0x00536c90` |
| `0x64efe0` / `0x64f010` | descriptor cells (name side by stride) | `0x00532fce` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**zero active sites** (the corpus TSV's DORMANT_CANDIDATE holds).

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: un-gated script-driven teleport-
adjacent position set through thing slot 20. Focused test deferred
until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00536c70`–`0x00536c99` is not
  `1a1ecfe8…55ff9fa1`, or either vtable offset leaves `[+0x44]`/`[+0x50]`.
- A second image-wide imm32 of `0x00536c70`, or any rel32 inbound.
- The handler store leaves `0x64f010`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famH_micro*.py`).
