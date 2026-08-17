# CTree__VFunc_27_CreateFallingTreeFromThing

<!-- ghidra-name-drift-accepted: 0x004f6aa0 CTree__VFunc_39_CreateFallingTreeFromThing (2026-08-17) -->

> **The saved Ghidra name is now `CTree__VFunc_39_CreateFallingTreeFromThing`.**
> This page keeps its old title only so existing references still resolve; the
> ordinal in that title is withdrawn.

| Property | Value |
| --- | --- |
| Address | `0x004f6aa0` |
| Saved signature | `void __thiscall CTree__VFunc_39_CreateFallingTreeFromThing(void * this, void * other_thing, int unused_context)` |
| Wave | Wave520 CTree static re-audit |

**Ordinal correction, 2026-08-17.** The `_27_` in the old name was the slot
number written in hexadecimal: `0x27` is 39 decimal. The 2026-08-17 name cohort
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
re-measured CTree vtable `0x005DD9D8`, found this VA at slot 39 entry
`0x005DDA74`, and rewrote the ordinal in decimal. Nothing else moved — and note
that the body and evidence paragraphs below already said slot 39, so this
correction brings the name into line with what the page had measured all along.

Recovered CTree vtable slot-39 boundary. The body checks `other_thing` flags at `+0x34`, skips when falling-tree data already exists at `this+0x48`, computes a vector between this tree position and `other_thing+0x1c`, applies an alternate distance threshold when flag `0x01000000` is set, normalizes the vector, and calls `CTree__CreateFallingTree` when the threshold gate passes.

Evidence: CTree vtable `0x005dd9d8` slot 39 points to `0x004f6aa0`, body returns with `RET 0x8`, callsite `0x004f6b6f` calls `CTree__CreateFallingTree`, and post boundary probe read-back names the function.

Claim boundary: static retail-binary evidence only. Exact virtual name, caller contract, runtime collision/destruction behavior, BEA patching, and rebuild parity remain unproven.
