# IScript__SetVisible

> Address: `0x00535EA0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SetVisible` is absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 22, registered as `SetVisible`: one integer
argument evaluated through element `vtable[+0x3c]`; when it equals 1,
calls the attached thing's visibility vtable slot 32 (`+0x80`) with no
arguments. Any other value (including 0) is a silent no-op — there is
no un-visible arm in this native.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, authored `.msl` recount
(`local-lab/famE_targets.py`, `famE_meat.py`, `famE_reg.py`,
`famE_reg2.py`, `famE_verify.py`, `famE_verify2.py`). No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 22 is `SetVisible` / `0x00535EA0` / empty name-table
cell / 62 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov edi, 0x00535ea0` (`bf a0 5e 53 00`) at VA
  `0x0053063f` — exactly **one** image-wide imm32 (byte hit at
  `0x00530640`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d3d0], edi` at VA `0x0053064c`.
- Name-pointer store: `mov dword ptr [0x64d3a0], 0x64f938` at VA
  `0x0053072e` (register-carried window); `.rdata 0x64f938` =
  `"SetVisible\0"`.
- Descriptor: name cell `0x64d3a0`, handler cell +0x30 at `0x64d3d0`.

## Contract (byte-exact)

Body `0x00535ea0`–`0x00535ec0` inclusive through the complete
`ret 0xc`, **33 bytes**, SHA-256
`96bcba04c009158a0dbfd3370f18b4803849464a78635aacc862593fac01acee`.
Zero `E8`, zero decoded `E9`.

```
00535ea0  8b 44 24 04        mov eax, [esp+4]           ; args object
00535ea4  56                 push esi
00535ea5  8b f1              mov esi, ecx
00535ea7  8b 08              mov ecx, [eax]             ; element 1
00535ea9  8b 11              mov edx, [ecx]
00535eab  ff 52 3c           call [edx+0x3c]            ; INT eval -> al
00535eae  8b 4e 10           mov ecx, [esi+0x10]        ; attached thing
00535eb1  3c 01              cmp al, 1
00535eb3  75 0c              jne 0x535ec1               ; not 1 -> nothing
00535eb5  8b 01              mov eax, [ecx]
00535eb7  ff 90 80 00 00 00  call [eax+0x80]            ; thing slot 32
00535ebd  5e                 pop esi
00535ebe  c2 0c 00           ret 0xc
```

The comparison is `al` only (`cmp al,1`) — consistent with the
`vtable[+0x3c]` integer evaluators returning their value in `eax` and
the boolean convention this family uses.

Boundary: next descriptor block; `SetObjective` (23) follows at
`0x00535ed0`.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing (no class gate here — unlike the segment family) | `0x00535eae` |
| `args[0]` via `vtable[+0x3c]` | integer flag | `0x00535eab` |
| thing `vtable[+0x80]` | visibility slot 32, zero-arg | `0x00535eb7` |
| `0x64d3a0` / `0x64d3d0` | registration descriptor cells | `0x0053072e`, `0x0053064c` |

Honest unknown: which concrete bodies occupy slot 32 across the thing
hierarchies (not walked this wake; cheapest instrument is a `.rdata`
slot census for each candidate).

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**62 active sites in 8 files** (`level741/742 Marshall.msl` 26+26,
level731/732 gun scripts, level621/622 Ejector.msl) — all `SetVisible(0)`
or `(TRUE)`-style calls. Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: script-driven one-way visibility
show (flag==1 only) through a thing-level visibility hook; the missing
hide arm is part of the observable contract. Focused test deferred
until the owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535ea0`–`0x00535ec0` is not
  `96bcba04…c01acee`, or the slot call leaves `[+0x80]`.
- A second image-wide imm32 of `0x00535ea0`, or any rel32 inbound.
- The handler store leaves `0x64d3d0`, or `.rdata 0x64f938` stops being
  `"SetVisible\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famE_*.py`).
- Cross-reference (same wake):
  [`IScript__SetObjective.md`](IScript__SetObjective.md),
  [`IScript__UnsetObjective.md`](IScript__UnsetObjective.md),
  [`IScript__IsObjective.md`](IScript__IsObjective.md).
