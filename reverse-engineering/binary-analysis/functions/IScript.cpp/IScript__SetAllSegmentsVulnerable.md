# IScript__SetAllSegmentsVulnerable

> Address: `0x00534390`

Status: active static function note
Last updated: 2026-10-22 (retail disassembly listings replaced by prose)
Source File: none — see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) for the pinned-source absence behind this whole family | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
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

In prose: the same UNIT/controller gate as native 51 (attached thing
`[this+0x10]`, class bit `[thing+0x34]&0x10`, controller `[thing+0x178]`
non-null), then the first argument element is evaluated through its
`vtable[+0x3c]` integer evaluator (call at `0x005343ac`), masked to a byte
(`0x005343af`) and passed as the single argument, with the controller as
`this`, to `0x00444620` (`E8` at `0x005343b7`); `ret 0xc`.

The evaluator call is through `edx` holding the element's vptr (signature
`ff 52 3c`), the same `[+0x3c]` integer slot as native 109.

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

It stores the flag into the vulnerability cell `[seg+0x1c]` of every
non-null segment in `[ctrl+4][0..[ctrl+8])`, then, when the root segment
`[ctrl+0xc]` is non-null, calls the recompute `0x00442890` (at `0x0044464c`) and
stores its float result into the cached total `[ctrl+0x18]`; `ret 4`.

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
