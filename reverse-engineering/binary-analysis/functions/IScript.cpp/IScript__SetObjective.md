# IScript__SetObjective

> Address: `0x00535ED0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 23, registered as `SetObjective`: a 12-byte
stub — calls the attached thing's objective-flag setter `0x004f3970`
with argument 1. That setter maintains bit `0x20` of the thing's state
byte `[thing+0x2c]` and adds/removes the thing on the global objective
marker set at `0x00855140` (`CSPtrSet` add `0x4e5a80` / remove
`0x4e5bd0`). The highest-traffic native in the corpus (298 authored
sites across 221 files).
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, callee walk, authored `.msl`
recount. No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 23 is `SetObjective` / `0x00535ED0` / empty name-table
cell / 298 sites; confirmed this wake. Registration:

- Handler immediate: `mov edi, 0x00535ed0` (`bf d0 5e 53 00`) at VA
  `0x0053066a` — exactly **one** image-wide imm32 (byte hit at
  `0x0053066b`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d410], edi` at VA `0x005307ad`.
- Name-pointer store: `mov dword ptr [0x64d3e0], 0x64f928` at VA
  `0x00530771`; `.rdata 0x64f928` = `"SetObjective\0"`.
- Descriptor: name cell `0x64d3e0`, handler cell +0x30 at `0x64d410`.

## Contract (byte-exact)

Body `0x00535ed0`–`0x00535edc` inclusive through the complete
`ret 0xc`, **13 bytes**, SHA-256
`e1e368b83a8c664935143709b40f4ad2bf7c6217003492b5d64c2562a48f666b`.

```
00535ed0  8b 49 10           mov ecx, [ecx+0x10]        ; attached thing
00535ed3  6a 01              push 1                     ; set
00535ed5  e8 96 da fb ff     call 0x004f3970            ; objective flag
00535eda  c2 0c 00           ret 0xc
```

Zero args consumed from the script stack; no class gate. The script's
"objective marker" is purely thing-state + global-set membership.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing (no gate) | `0x00535ed0` |
| `0x64d3e0` / `0x64d410` | registration descriptor cells | `0x00530771`, `0x005307ad` |

## Objective-flag setter — `0x004F3970(flag)` (byte-exact)

`thiscall`, `ret 4`, body `0x004f3970`–`0x004f39ac`, SHA-256
`da733fdd7e7575a433875b1f7179c538834892d555e8d02db320a269353980b0`.
Exactly two inbound `E8`: this native and
[`IScript__UnsetObjective.md`](IScript__UnsetObjective.md).

```
004f3977  cmp eax, 1               ; eax = arg
004f397a  mov al, [esi+0x2c]       ; thing state byte
004f397d  jne clear-arm            ; arg != 1 -> clear
set arm:  test al, 0x20; jne done  ; already marked
          push esi; mov ecx, 0x00855140; call 0x004e5a80   ; CSPtrSet add
          or [esi+0x2c], 0x20
clear arm: test al, 0x20; je done   ; not marked
          push esi; mov ecx, 0x00855140; call 0x004e5bd0   ; CSPtrSet remove
          and [esi+0x2c], 0xdf
```

Cross-anchors:

- `0x004e5bd0` is pinned repo-wide as `CSPtrSet__Remove`
  ([`IScript.cpp.md`](../IScript.cpp.md) HandleMessage 2001 arm);
  `0x004e5a80` is its add twin (null-pool warning via `CConsole__Printf`
  `0x00441740`, free-list pop at `0x0083d130/34`). So `0x00855140` is a
  global `CSPtrSet` holding every currently-objective-marked thing.
- Bit `0x20` of `[thing+0x2c]` is read back by the exact-slot predicate
  `0x004014e0` (`movsx eax, byte [ecx+0x2c]; and eax,0x20; shr eax,5`),
  which occupies slot 13 (`+0x68`) of the `CComplexThing` vtable
  `0x005df784` — the same slot
  [`IScript__IsObjective.md`](IScript__IsObjective.md) dispatches
  through.
- Authored-name caveat: "objective" here is the mission-marker sense
  (this set drives HUD/objective listing consumers), not the
  PrimaryObjectiveComplete event family (`IScript__PrimaryObjectiveComplete`
  et al., separate natives).

## Callers

Zero rel32 inbound to the native; dispatch-table-only. Authored recount
this wake: **298 active sites across 221 files** — the widest-authored
native in the corpus (every checkpoint, target-zone, fuel-tank,
vital-building and boss script). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: a thing-level objective-marker flag
(bit in thing state) plus global marker-set membership with idempotent
add/remove — the setter is already exactly that shape. Focused test
deferred until the owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535ed0`–`0x00535edc` is not
  `e1e368b8…48f666b`, or the callee leaves `0x004f3970` or the constant
  leaves `1`.
- A second image-wide imm32 of `0x00535ed0`, or any rel32 inbound.
- The handler store leaves `0x64d410`, or `.rdata 0x64f928` stops being
  `"SetObjective\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famE_*.py`).
- Cross-reference (same wake):
  [`IScript__UnsetObjective.md`](IScript__UnsetObjective.md),
  [`IScript__IsObjective.md`](IScript__IsObjective.md),
  [`IScript__SetVisible.md`](IScript__SetVisible.md).
