# IScript__ResetSegmentHealth

> Address: `0x005354C0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md)
for the pinned-source absence behind this whole family
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 134, registered as `ResetSegmentHealth`:
byte-for-byte the native 51 shape (name + float through `vtable[+0x38]`
/ `[+0x34]`) with one different callee — `0x004444B0(name, value)`
writes **both** segment cells `+0xc` and `+0x10` to the same value, then
recomputes the cached total. This is the family's only double-cell
writer; it is also the most-authored member (54 sites). The "reset"
semantics is exactly that second cell.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. Second-pass
verification `local-lab/famD_review.py`: 68/68 green. No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 134 is `ResetSegmentHealth` / `0x005354C0` / empty
name-table cell / 54 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov ebp, 0x005354c0` (`bd c0 54 53 00`) at VA
  `0x0053300e` — exactly **one** image-wide imm32 (byte hit at
  `0x0053300f`). Zero rel32 inbound.
- Handler cell store: `mov [0x64efd0], ebp` at VA `0x00533024`.
- Name-pointer store: `mov dword ptr [0x64efa0], 0x64f2ac` at VA
  `0x00533058`; `.rdata 0x64f2ac` = `"ResetSegmentHealth\0"`.
- Descriptor: name cell `0x64efa0`, handler cell +0x30 at `0x64efd0`
  (registration order = corpus TSV order: `SetSlotSave` (133) one
  stride ahead at name `0x64ef60` / handler `0x64ef90`; `SetPos` (135),
  `SetLockable` (136), `ToggleCockpit` (137) behind at handler cells
  `0x64f010`, `0x64f050`, `0x64f090`).

## Contract (byte-exact)

Body `0x005354c0`–`0x005354fa` inclusive through the complete
`ret 0xc`, **59 bytes**, SHA-256
`c29c8cc7b83aa82edbc1fc34dacd2226252147112f977212a08eac0a49060e11`.
One `E8`, zero decoded `E9`. Instruction stream is identical to native
51's except the callee address (`0xe8 ba ef f0 ff` → `0x004444b0`);
see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) for
the annotated listing.

## Field map pinned by this body

Same field map as native 51 (gate law, `args[0]` name via
`vtable[+0x38]`, `args[1]` value via `vtable[+0x34]`, descriptor
cells); the delta is entirely in the dispatch below.

## Controller dispatch — `0x004444B0` `(name, value)` (byte-exact)

`thiscall`, `ret 8`. Same carrier gate as `0x00444450`
(`[this+0x10]` → `[[that]+0x30]` → its `vtable[+0x24]()`, nonzero), same
`0x004AA8A0` stricmp lookup, same index path `[entry+0x88]` →
`[ctrl+4][idx]`. Then the divergence:

```
004444e7  mov edx, [esp+0x10]      ; arg2 = float value
004444eb  mov ecx, edx             ; (dead copy)
004444ed  mov dword ptr [eax+0xc], edx    ; health cell   (+0xc)
004444f0  mov dword ptr [eax+0x10], ecx   ; SECOND cell   (+0x10)
004444f3  mov ecx, [esi+0xc]       ; controller root segment
004444f6  test ecx, ecx
004444f8  je 0x0044451a            ; -> bare ret 8
004444fa  call 0x00442890          ; recursive recompute (float in st0)
004444ff  fstp dword ptr [esi+0x18]; cached-total refresh
00444502  pop edi; pop esi
00444504  ret 8
```

- Cell roles, from the getter web (see Consumers): `+0xc` is the
  current per-segment health/scale state every family writer touches;
  `+0x10` is the reference/total-scale state the all-segments getters
  sum when asked for a total. Writing both with one value is what makes
  this native behave as "reset": current == reference afterwards.
- The recompute `0x00442890` walks the root's child chain
  (`[root+0x24]` head, `[child+4]` next): per node, if `[node+0x1c]`
  (the vulnerability cell) is live and the node reports not-broken via
  its own `vtable[+0x18]()`, seed from the node's **current** cell
  `[node+0xc]` when that float is nonzero (`fcomp` vs `0.0f` at
  `0x005d856c`); sum recursively into the caller's slot; result stored
  at `[controller+0x18]`. (Twin `0x00442900` seeds unconditionally —
  see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md).)

## Consumers

The script-visible health getters read back what this native writes:
native 18 `GetHealth` (`0x00535920`) forwards through thunk
`0x004f99f0` → controller getter `0x00444330`; native 111
`GetRealHealth` (`0x005359d0`) forwards through `0x004f9a40` →
`0x00444370`. Both getters scan every segment for a live vulnerability
cell (`[seg+0x1c]==1`): none vulnerable → constant `1.0f`
(`0x005d8568`) without touching cells; any vulnerable → per-segment
sums via `0x00442890` / twin `0x00442900` or the cached
`[controller+0x18]`. The sibling thunk `0x004f9a10` (no direct native
caller measured this wake) falls back to `[thing+0xf8]` /
`[[thing+0x164]+0xc0]` / `0.0f` when no controller exists.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**54 active sites** — `level521/hive.msl` 27, `level522/hive.msl` 27
(e.g. `ResetSegmentHealth("core2", core_health)`; shield segments get
`core_hive_shield_health`). Matches corpus TSV.

## Pinned-source status

Absent, like the rest of the family.

## Rebuild mapping

No Core owner yet. When one lands: name-indexed write of one float into
both `segment.health` and `segment.referenceScale`, plus cached-total
refresh — the observable "current == reference" postcondition is the
testable contract. Focused test deferred until the owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005354c0`–`0x005354fa` is not
  `c29c8cc7…060e11`, or the dispatch target is anything but
  `0x004444b0`.
- A second image-wide imm32 of `0x005354c0`, or any rel32 inbound.
- The handler store leaves `0x64efd0`, or `.rdata 0x64f2ac` stops being
  `"ResetSegmentHealth\0"`.
- The dispatch loses either store (`+0xc` or `+0x10`) or the recompute
  call.

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
  [`IScript__SetSegmentVulnerable.md`](IScript__SetSegmentVulnerable.md),
  [`IScript__SetAllSegmentsVulnerable.md`](IScript__SetAllSegmentsVulnerable.md).
