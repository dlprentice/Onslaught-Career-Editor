# CTree__Hit

Status: active static interface note; historical filename retained
Last updated: 2026-09-27
Summary: current Hit identity, bounded pristine body facts and superseded ordinal labels.

The [gameplay interface audit](../../../ghidra/README.md#re-audit-thing-gameplay-identities--september-27)
identifies this entry from the shared interface, independent retail callers and
primary RTTI. Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The former `CTree__VFunc_39_CreateFallingTreeFromThing` label and older hexadecimal ordinal in this filename
are superseded. The saved signature below records existing metadata; parameter
corrections are a separate cohort.

| Property | Value |
| --- | --- |
| Address | `0x004f6aa0` |
| Saved signature | `void __thiscall CTree__Hit(void * this, void * other_thing, int unused_context)` |
| Wave | Wave520 CTree static re-audit |

**Ordinal correction, 2026-08-17.** The `_27_` in the old name was the slot
number written in hexadecimal: `0x27` is 39 decimal. The 2026-08-17 name cohort
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
re-measured CTree vtable `0x005DD9D8`, found this VA at slot 39 entry
`0x005DDA74`, and rewrote the ordinal in decimal. Nothing else moved — and note
that the body and evidence paragraphs below already said slot 39, so this
correction brings the name into line with what the page had measured all along.

Recovered CTree vtable slot-39 boundary. The body checks the peer word at `+0x34`, skips when falling-tree data already exists at `this+0x48`, computes a vector between this tree position and `other_thing+0x1c`, applies an alternate distance threshold when flag `0x01000000` is set, normalizes the vector, and calls `CTree__CreateFallingTree` when the threshold gate passes.

Evidence: CTree vtable `0x005dd9d8` slot 39 points to `0x004f6aa0`, body returns with `RET 0x8`, callsite `0x004f6b6f` calls `CTree__CreateFallingTree`, and post boundary probe read-back names the function.

The shared call interface is `Hit(peer, report)` with two pointer arguments and RET 8. This complete body never reads the report; its saved `int unused_context` is therefore an interface-type defect, not evidence that the argument is absent. Runtime collision/destruction behavior and rebuild parity remain unproven.
