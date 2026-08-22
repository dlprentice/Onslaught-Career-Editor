# IScript__GotoPlayerCamera

> Address: `0x00533B70`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 116, registered as `GotoPlayerCamera`: zero
script arguments; SEH-framed; resolves the player BattleEngine via the
attached thing's element `vtable[+0x40]` and hands the result to the
camera director; a null result prints a console warning and no-ops.
Zero authored uses (`DORMANT_CANDIDATE`) — the retail cutscenes build
explicit camera paths instead.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 116 is `GotoPlayerCamera` / `0x00533B70` / empty
name-table cell / 0 sites; confirmed this wake (recount zero).
Registration:

- Handler immediate: `bd 70 3b 53 00` (`mov ebp, 0x00533b70`) at VA
  `0x005328d0` — exactly **one** image-wide imm32 (byte hit at
  `0x005328d1`). Zero rel32 inbound.
- Handler cell store: `mov [0x64ead0], ebp` at VA `0x005328d5`.
- Name-pointer store: `mov dword ptr [0x64eb20], 0x64f3b4` at VA
  `0x005329c7`; `.rdata 0x64f3b4` = `"GotoPlayerCamera\0"`.
- Descriptor: name cell `0x64eb20`, handler cell +0x30 at `0x64eb50`
  (stride law; the sibling `Goto4PointPanCamera` descriptor follows).

## Contract (measured head; tail not walked)

Body `0x00533b70`–`0x00533bc1` inclusive through the complete final
`ret 0xc`, **82 bytes**, SHA-256
`61c4171f60b170e2ab1dbdd99575136a222919a99066dbb2c662bad6c521da96`.
SEH-framed.

```
00533b88  mov eax, [esp+0x38]             ; args object
00533b91  call [edx+0x40]                 ; player-BattleEngine eval
00533b96  mov [esp+4], eax; cmp eax, ebx(0)
00533b9c  jne continue (0x00533bc2)       ; camera handoff (not walked)
null arm:
00533b9e  push 0x0064fa9c; push 0x0066f580
00533ba8  call 0x00441740                 ; CConsole__Printf warning
          ret 0xc
```

The `[+0x40]` element slot is the player-reference evaluator (distinct
from the `[+0x38]` name and `[+0x3c]` int slots); its returned pointer
is the hand-off argument. The camera-director call beyond `0x00533bc2`
is not walked this wake — honest unknown, cheapest instrument a
continue-arm decode.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `args[0]` via `vtable[+0x40]` | player BattleEngine reference | `0x00533b91` |
| null → `CConsole__Printf` warn | `0x00441740`, file `0x0064fa9c` | `0x00533ba8` |
| `0x64eb20` / `0x64ead0`+0x30 | registration descriptor cells | `0x005329c7`, `0x005328d5` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**zero active sites** (DORMANT_CANDIDATE holds).

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet; pairs with the camera natives family
(`Create3PointPanCamera` et al.) when a camera owner lands. Focused
test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00533b70`–`0x00533bc1` is not
  `61c4171f…6c521da96`, or the element eval leaves `[+0x40]`.
- A second image-wide imm32 of `0x00533b70`, or any rel32 inbound.
- The handler store leaves `0x64ead0`, or `.rdata 0x64f3b4` stops being
  `"GotoPlayerCamera\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famI_final*.py`).
