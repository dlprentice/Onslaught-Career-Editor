# IScript__SetAllSegmentsVulnerable

> Address: `0x00534390`

Status: active static function note
Last updated: 2026-08-22
Source File: none — see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md)
for the pinned-source absence behind this whole family
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 110, registered as `SetAllSegmentsVulnerable`:
the bulk twin of native 109 — same gate, one integer element through
`vtable[+0x3c]` masked to a byte, then `0x00444620(flag)` stores the flag
into every segment's vulnerability cell `+0x1c` and recomputes the
cached total. Unlike its health twin (native 52), it **does** refresh
the cache. One authored use per hive level.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. Second-pass
verification `local-lab/famD_review.py`: 68/68 green. No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 110 is `SetAllSegmentsVulnerable` / `0x00534390` / empty
name-table cell / 2 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov ebp, 0x00534390` (`bd 90 43 53 00`) at VA
  `0x00532736` — exactly **one** image-wide imm32 (byte hit at
  `0x00532737`). Zero rel32 inbound.
- Handler cell store: `mov [0x64e9d0], ebp` at VA `0x0053273b`.
- Name-pointer store: `mov dword ptr [0x64e9a0], 0x64f428` at VA
  `0x005327c1`; `.rdata 0x64f428` = `"SetAllSegmentsVulnerable\0"`.
- Descriptor: name cell `0x64e9a0`, handler cell +0x30 at `0x64e9d0`.

## Contract (byte-exact)

Body `0x00534390`–`0x005343bf` inclusive through the complete
`ret 0xc`, **48 bytes**, SHA-256
`dd6c46dc5e3e1fbfad4b227e5d10fecf7f5b2298e1fdf5cf7cd315db0d042991`.
One `E8`, zero decoded `E9`.

```
00534390  8b 41 10           mov eax, [ecx+0x10]        ; attached thing
00534393  56                 push esi
00534394  f6 40 34 10        test byte [eax+0x34], 0x10 ; UNIT class bit
00534398  74 22              je 0x5343bc                ; -> bare return
0053439a  8b b0 78 01 00 00  mov esi, [eax+0x178]       ; segments ctrl
005343a0  85 f6              test esi, esi
005343a2  74 18              je 0x5343bc
005343a4  8b 44 24 08        mov eax, [esp+8]           ; args object
005343a8  8b 08              mov ecx, [eax]             ; element 1
005343aa  8b 11              mov edx, [ecx]
005343ac  ff 52 3c           call [edx+0x3c]            ; INT eval -> eax
005343af  25 ff 00 00 00     and eax, 0xff              ; byte mask
005343b4  8b ce              mov ecx, esi               ; this = controller
005343b6  50                 push eax                   ; arg: flag
005343b7  e8 64 02 f1 ff     call 0x00444620            ; (flag)
005343bc  5e                 pop esi
005343bd  c2 0c 00           ret 0xc
```

The eval here decodes `ff 52 3c` — element pointer in `ecx`, so the
vptr rides `edx` — same `[+0x3c]` integer slot as native 109.

Boundary: none; `AddScore` (native 85) follows immediately at
`0x005343c0` (no pad).

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| shared gate law | as native 51 | [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) |
| `args[0]` via `vtable[+0x3c]` | integer flag, masked `&0xff` (single arg) | `0x005343ac`, `0x005343af` |
| `0x64e9a0` / `0x64e9d0` | registration descriptor cells | `0x005327c1`, `0x0053273b` |

## Controller dispatch — `0x00444620` `(flag)` (byte-exact)

`thiscall`, `ret 4`. Counted loop over all segments, then recompute:

```
00444620  push esi; mov esi, ecx
00444623  xor ecx, ecx             ; i = 0
00444625  mov eax, [esi+8]         ; count
00444628  test eax, eax; jle done
0044462c  mov edx, [esp+8]         ; arg = flag
00444630  mov eax, [esi+4]; mov eax, [eax+ecx*4]   ; segments[i]
00444636  test eax, eax; je skip
0044463a  mov [eax+0x1c], edx      ; VULNERABILITY CELL (+0x1c)
0044463d  mov eax, [esi+8]; inc ecx; cmp ecx, eax; jl 0x00444630
00444645  mov ecx, [esi+0xc]       ; root segment
00444648  test ecx, ecx; je ret 4
0044464c  call 0x00442890          ; recompute
00444651  fstp dword ptr [esi+0x18]; cached-total refresh
00444654  pop esi
00444655  ret 4
```

Same cell and same recompute as native 109's dispatch, minus the name
lookup. The existing
[`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)
already carries this body as
`SetAllSegmentsActiveFlagAndRefreshMetric` ("writes field +0x1c across
the controller segment array and refreshes cached metric this+0x18") —
confirmed exactly by this read; only its Destructable/Destroyable
spelling caveat (see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md))
carries forward.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**2 active sites**, one each in `level521/hive.msl` and
`level522/hive.msl` (`SetAllSegmentsVulnerable(TRUE)` /
`(FALSE)`). Matches corpus TSV.

## Pinned-source status

Absent, like the rest of the family.

## Rebuild mapping

No Core owner yet. When one lands: bulk byte write into every
`segment.vulnerable` plus cached-total refresh; pairs with native 52's
documented missing-recompute behavior as the family's two bulk
semantics. Focused test deferred until the owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00534390`–`0x005343bf` is not
  `dd6c46dc…d042991`, or the dispatch target is anything but
  `0x00444620`.
- A second image-wide imm32 of `0x00534390`, or any rel32 inbound.
- The handler store leaves `0x64e9d0`, or `.rdata 0x64f428` stops being
  `"SetAllSegmentsVulnerable\0"`.
- The dispatch gains a name lookup or loses the recompute call.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famD_measure.py`, `famD_callees.py`, `famD_reg*.py`,
  `famD_msl3.py`); second pass `local-lab/famD_review.py` 68/68 green.
- Cross-reference (same wake):
  [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md),
  [`IScript__SetAllSegmentsHealth.md`](IScript__SetAllSegmentsHealth.md),
  [`IScript__ResetSegmentHealth.md`](IScript__ResetSegmentHealth.md),
  [`IScript__SetSegmentVulnerable.md`](IScript__SetSegmentVulnerable.md).
