# IScript__SetSegmentVulnerable

> Address: `0x00534300`

Status: active static function note
Last updated: 2026-10-22 (retail disassembly listings replaced by prose)
Source File: none — see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) for the pinned-source absence behind this whole family | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 109, registered as `SetSegmentVulnerable`: the
by-name segment vulnerability writer. Same UNIT/controller gate and
`0x004AA8A0` stricmp dispatch as the health pair, but the value element
is evaluated through `vtable[+0x3c]` (integer, masked to a byte) and
stored to the segment's **vulnerability** cell `+0x1c`, then the cached
total recomputes. The cell is the same one the controller getters scan
for `[seg+0x1c]==1` and the recursive recompute requires to be live.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. Second-pass
verification `local-lab/famD_review.py`: 68/68 green. No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 109 is `SetSegmentVulnerable` / `0x00534300` / empty
name-table cell / 54 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov ebp, 0x00534300` (`bd 00 43 53 00`) at VA
  `0x00532712` — exactly **one** image-wide imm32 (byte hit at
  `0x00532713`). Zero rel32 inbound.
- Handler cell store: `mov [0x64e990], ebp` at VA `0x0053271c`.
- Name-pointer store: `mov dword ptr [0x64e960], 0x64f444` at VA
  `0x005326e2`; `.rdata 0x64f444` = `"SetSegmentVulnerable\0"`.
- Descriptor: name cell `0x64e960`, handler cell +0x30 at `0x64e990`
  (neighbor: `IsFiring` (107) one stride ahead at name `0x64e920` /
  handler `0x64e950`; `GetRealHealth` (111) behind at name `0x64ea00` /
  handler `0x64ea30`).

## Contract (byte-exact)

Body `0x00534300`–`0x0053433c` inclusive through the complete
`ret 0xc`, **61 bytes**, SHA-256
`822c04d3deb5d77da96b356f4f76a23c2332ac4cd0eb51ca0c8ab601e61c4556`.
One `E8`, zero decoded `E9`.

In prose: the same UNIT/controller gate as native 51. The second argument
element is evaluated as an integer through `vtable[+0x3c]` (call at
`0x00534320`) and masked to a byte (`0x00534325`); the first element is fetched
as a `char*` name through `vtable[+0x38]` (call at `0x0053432d`); then
`0x004445b0(name, flag)` is called with the controller as `this` (`E8` at
`0x00534333`); `ret 0xc` at `0x0053433a`.

The value element uses `vtable[+0x3c]` (integer), **not** the
`vtable[+0x34]` float slot the health natives use — the byte encodings
`ff 50 3c` here vs `ff 50 34` in 51/134 pin the split. Authored scripts
pass `TRUE`.

Boundary: three `nop` then `SetVelocity` (native 129) at `0x00534340`.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| shared gate law | as native 51 | [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) |
| `args[0]` via `vtable[+0x38]` | `char*` segment name | `0x0053432d` |
| `args[1]` via `vtable[+0x3c]` | integer flag, masked `&0xff` | `0x00534320`, `0x00534325` |
| `0x64e960` / `0x64e990` | registration descriptor cells | `0x005326e2`, `0x0053271c` |

## Controller dispatch — `0x004445B0` `(name, flag)` (byte-exact)

`thiscall`, `ret 8`. Same carrier gate, `0x004AA8A0` lookup, and
`[entry+0x88]` index path as `0x00444450`. Then:

After the lookup it stores the flag into the segment's vulnerability cell
`[seg+0x1c]` (store at `0x004445eb`); when the root segment `[ctrl+0xc]` is
non-null it calls the recompute `0x00442890` (at `0x004445f5`) and stores the
float result into the cached total `[ctrl+0x18]`; `ret 8`.

Cell `+0x1c` cross-anchors this wake:

- The controller all-segments getters (`0x00444330`/`0x00444370`/
  `0x004443b0`) scan for `[seg+0x1c]==1` to decide whether to return
  the constant `1.0f` or walk sums — this cell is their switch.
- The recursive recompute `0x00442890` requires `[node+0x1c]` live
  before seeding from `[node+0x10]`.
- The existing
  [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)
  calls `+0x1c` the "active flag" written by
  `0x00444620 SetAllSegmentsActiveFlagAndRefreshMetric` — same cell;
  this note's dispatch read confirms the writer side and the getter
  scan. (The old contract's controller name spelling carries the
  Destructable/Destroyable caveat recorded in
  [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md).)

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**54 active sites** — `level521/hive.msl` 27, `level522/hive.msl` 27
(`SetSegmentVulnerable("core2", TRUE)` pattern). Matches corpus TSV.

## Pinned-source status

Absent, like the rest of the family.

## Rebuild mapping

No Core owner yet. When one lands: name-indexed byte write into
`segment.vulnerable` plus cached-total refresh; the getters'
`1.0f`-when-none-vulnerable law consumes it. Focused test deferred
until the owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00534300`–`0x0053433c` is not
  `822c04d3…61c4556`, or the dispatch target is anything but
  `0x004445b0`.
- A second image-wide imm32 of `0x00534300`, or any rel32 inbound.
- The handler store leaves `0x64e990`, or `.rdata 0x64f444` stops being
  `"SetSegmentVulnerable\0"`.
- The value element's eval moves to `vtable[+0x34]`, or the dispatch
  store leaves `[seg+0x1c]`.

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
  [`IScript__SetAllSegmentsVulnerable.md`](IScript__SetAllSegmentsVulnerable.md).
