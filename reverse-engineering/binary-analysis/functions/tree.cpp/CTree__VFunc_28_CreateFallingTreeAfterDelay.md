# CTree__Damage

Status: active static interface note; historical filename retained
Last updated: 2026-09-27
Summary: current Damage identity, bounded pristine body facts and superseded ordinal labels.

The [gameplay interface audit](../../../ghidra/README.md#re-audit-thing-gameplay-identities--september-27)
identifies this entry from the shared interface, independent retail callers and
primary RTTI. Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The former `CTree__VFunc_40_CreateFallingTreeAfterDelay` label and older hexadecimal ordinal in this filename
are superseded. The saved signature below records existing metadata; parameter
corrections are a separate cohort.

| Property | Value |
| --- | --- |
| Address | `0x004f68e0` |
| Saved signature | `void __thiscall CTree__Damage(void * this, float elapsed_time, void * other_thing, int unused_arg2, int unused_arg3)` |
| Wave | Wave520 CTree static re-audit |

**Ordinal correction, 2026-08-17.** The `_28_` in the old name was the slot
number written in hexadecimal: `0x28` is 40 decimal. The 2026-08-17 name cohort
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
re-measured CTree vtable `0x005DD9D8`, found this VA at slot 40 entry
`0x005DDA78`, and rewrote the ordinal in decimal. Nothing else moved — and note
that the body and evidence paragraphs below already said slot 40, so this
correction brings the name into line with what the page had measured all along.

The old timer/cooldown interpretation is withdrawn. This is Damage, and the
first float argument is the damage amount. The complete body is 199 bytes,
SHA-256 `0a2e55ce23c54862905c662461306fb6e55d56f92658c09456146dd0d2567da1`.
For finite inputs, it skips when `this+0x48` is nonzero or the float at
`this+0x44` is zero. Otherwise it subtracts the amount, stores the float32 result to `this+0x44`,
and compares the still-held x87 result with zero. A positive result returns; a non-positive result clears that field, forms a
vector from the source object's position toward this tree, normalizes a
nonzero vector, and passes it to `0x004f69b0`. Only the local XYZ words are
initialized; the fourth word is not written by this body. The initial field's authored name
and exceptional-float behavior are not established here. No clock value or
frame delta is read. The misleading saved parameter `elapsed_time` is queued
for a parameter-name-only correction; the four argument words remain intact.

Evidence: CTree vtable `0x005dd9d8` slot 40 points to `0x004f68e0`, body returns with `RET 0x10`, callsite `0x004f699c` calls `CTree__CreateFallingTree`, and post boundary probe read-back names the function.

Claim boundary: shared Damage identity and the stated finite static branch/argument behavior only. Full callee effects, runtime collision/destruction, exceptional float inputs and rebuild parity remain unproven.
