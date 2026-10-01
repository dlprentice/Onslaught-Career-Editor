# CUnit::Hit — contact-normal admission

Status: active bounded static and isolated-execution contract
Last updated: 2026-10-01
Summary: the aggregate contact-normal test at `0x004fcc30` depends on a float spill that the current unmatched C++ reconstruction omits; authored boundary cases distinguish their decisions.
Source File: private reconstructed `bea-decomp/src/Unit.cpp` | Binary: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

The selected specimen is `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Instructions below were read directly from it. `CUnit::Hit` is the current
reconstruction label for this body; this note does not promote a Ghidra name.
The private reconstruction is `bea-decomp/src/Unit.cpp`.

| Address | Stored Ghidra label | Scope |
| --- | --- | --- |
| `0x004fcc30` | `CUnit__Hit` | Name-table provenance only; this recheck does not promote or change the name. |

## Static admission and arithmetic

The function has incoming `ECX` and two stack arguments, ending in `ret 8` at
`0x004fcdbd`. Before the normal test, it optionally calls `0x004e6640` through
the receiver's `+0x148` pointer. Partner type bit `0x10` separately sets receiver
`+0x248` to one. The normal path requires all of:

- partner `+0x34` bit `0x100000`;
- a nonnull report whose first dword is nonzero;
- the receiver's virtual `+0xb4` result strictly greater than zero.

At `0x004fcca1` the signed contact count comes from report `+0x80`. Normals start
at `+8` with a 16-byte stride and XYZ in the first three float32 words. The
per-contact loop tests `-Z > float32(0.89)`; any success admits the contact.
If none succeeds and the count exceeds one, `0x004fcce3..0x004fcd2a` sums
**exactly the first three normals**, including when the count is two. Validity
of the unused third entry for that case is a separate caller question.

The accumulated Y is stored as float32 at `0x004fcd2c`, then reloaded for the
length calculation. Accumulated X and Z remain on the x87 stack. The code
computes a square root, skips reciprocal scaling when the length is zero, and
otherwise scales the components. It retains stores of normalized X and Y at
`0x004fcd65` and `0x004fcd6f`; the normalized Z remains in x87 for the strict
`-Z > float32(0.69)` test at `0x004fcd7d..0x004fcd8e`.

Admission reaches the receiver's virtual `+0x118` with the partner, then
virtual `+0x110` at `0x004fcd90..0x004fcda3`. Both the admitted and rejected
paths finally call `0x004f4480` with partner and report. These call destinations
are static facts; their side effects were not executed in this experiment.

## Reproduced numerical difference

The lead freshly compiled and relocated the current candidate, then reproduced
the helper's native i386 experiment. It executes original instructions from
`0x004fcce3` to admission `0x004fcd90` or rejection `0x004fcda9`, and the
corresponding candidate block. Other bytes of the code page are `INT3` guards.
The experiment checks stack canaries, an empty x87 stack at exit, and unchanged
control words. It opens no game or display.

Across 13,839 authored cases, the decisions differ in 198 cases at explicitly
selected control word `0x037f`, 198 at `0x027f`, and 588 at `0x007f`.
One `0x037f` witness uses three identical normals:
`(0.642481803894043, 0.33334222435951233, -0.6899999380111694)`.
The retail block rejects the final threshold; the candidate accepts it.
These normals do not satisfy the earlier individual `0.89` threshold.

A separate three-opcode intervention widens only the retail Y spill and its
two reads to float64. That removes all `0x037f`/`0x027f` decision differences;
588 `0x007f` differences remain. A threshold-to-one negative control changes
5,646 decisions. Neither intervention is an implementation fix. The current
candidate still fails whole-function matching, and no replacement arithmetic
has been accepted.

Private reproduction owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/unit-hit-root-20261001/`.
`reproduction.json` pins the fresh source, relocated candidate and original
helper driver; `native-x87.py` is the rerunnable experiment, and
`native/receipt.json` has SHA-256
`5aee572fc271e2d3a9c0c55f6f0693ae9546df3832913e623d728cb8da18148f`.

## Limits and next falsifier

This disproves the claim that the omitted spill is merely cosmetic. It does
not demonstrate a retail gameplay bug or a reachable gameplay disagreement.
The optional squad callback, admission guards, contact generation and final
virtual calls are outside the executed block; the live game's x87 control
word was not observed. Test vectors are authored inputs, not captured contacts.

For reconstruction, preserve the observed rounding boundary and fixed
three-normal sum; a generic normalize operation is not yet demonstrated to be
interchangeable. The next cheap static check is the report producer's handling
of a two-contact report. Runtime reachability requires an admitted captured
report and its actual x87 control word, followed by replay of the exact values
through both blocks. Full body matching remains a separate open task.
