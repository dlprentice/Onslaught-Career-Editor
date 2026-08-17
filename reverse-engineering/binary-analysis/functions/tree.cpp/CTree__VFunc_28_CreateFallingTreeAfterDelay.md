# CTree__VFunc_28_CreateFallingTreeAfterDelay

<!-- ghidra-name-drift-accepted: 0x004f68e0 CTree__VFunc_40_CreateFallingTreeAfterDelay (2026-08-17) -->

> **The saved Ghidra name is now `CTree__VFunc_40_CreateFallingTreeAfterDelay`.**
> This page keeps its old title only so existing references still resolve; the
> ordinal in that title is withdrawn.

| Property | Value |
| --- | --- |
| Address | `0x004f68e0` |
| Saved signature | `void __thiscall CTree__VFunc_40_CreateFallingTreeAfterDelay(void * this, float elapsed_time, void * other_thing, int unused_arg2, int unused_arg3)` |
| Wave | Wave520 CTree static re-audit |

**Ordinal correction, 2026-08-17.** The `_28_` in the old name was the slot
number written in hexadecimal: `0x28` is 40 decimal. The 2026-08-17 name cohort
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
re-measured CTree vtable `0x005DD9D8`, found this VA at slot 40 entry
`0x005DDA78`, and rewrote the ordinal in decimal. Nothing else moved — and note
that the body and evidence paragraphs below already said slot 40, so this
correction brings the name into line with what the page had measured all along.

Recovered CTree vtable slot-40 boundary. The body skips when `this+0x48` already has falling data, decrements timer/cooldown field `this+0x44` by `elapsed_time`, and when the timer crosses zero computes a normalized vector from this tree position to `other_thing+0x1c` before calling `CTree__CreateFallingTree`.

Evidence: CTree vtable `0x005dd9d8` slot 40 points to `0x004f68e0`, body returns with `RET 0x10`, callsite `0x004f699c` calls `CTree__CreateFallingTree`, and post boundary probe read-back names the function.

Claim boundary: static retail-binary evidence only. Exact virtual name, source identity, caller contract, runtime collision/destruction behavior, BEA patching, and rebuild parity remain unproven.
