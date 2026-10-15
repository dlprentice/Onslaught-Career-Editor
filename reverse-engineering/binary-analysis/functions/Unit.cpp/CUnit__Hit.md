# CUnit::Hit — contact-normal admission

Status: active bounded static and isolated-execution contract
Last updated: 2026-10-01
Summary: the corrected contact handler now matches its complete compiled body, preserving the observed float spill and fixed three-normal sum; mesh/sphere producer reachability remains bounded separately.
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
**exactly the first three normals**, including when the count is two. The
mesh/sphere producer does not guarantee that the third entry is zero, as the
separate producer experiment below establishes.

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

## Reproduced numerical difference — former candidate

The lead freshly compiled and relocated the former candidate, then reproduced
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
5,646 decisions. Neither intervention is an implementation fix. That candidate failed whole-function
matching. The subsequent source correction below supersedes its open status.

Private reproduction owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/unit-hit-root-20261001/`.
`reproduction.json` pins the fresh source, relocated candidate and original
helper driver; `native-x87.py` is the rerunnable experiment, and
`native/receipt.json` has SHA-256
`5aee572fc271e2d3a9c0c55f6f0693ae9546df3832913e623d728cb8da18148f`.

## Exact reconstruction correction — October 1

The source now shares a downward vector between the per-contact and aggregate slope tests,
with a named float for the first-contact dot result. That ordinary source/value lifetime
restores the Y rounding and normalized X/Y stores above. The lead independently rebuilt it:
**all 400 emitted section bytes and all nine relocations match the pristine body**. Its
relocated SHA-256 is `df4d10d55db50d359a9d34e782e3f8202aedb62e6ada17dd0a21c574a8c9a0ca`.
Every one of the 166 preceding exact Unit address/symbol pairs is retained; the other 214
callable sections retain their bytes and relocation referents, allowing local-label renumbering.

The corrected threshold block also reran the same 13,839 authored native cases. No decision
differs at any of the three selected precisions; the threshold control still changes 5,646
cases. This closes the reconstructed function's demonstrated arithmetic gap. It does not
establish captured contact inputs, live precision, original source spelling or player parity.
In particular, the exact retail code still sums three normals when the count is two.

Private owner: `bea-decomp/.worktrees/codex-equiv-20260930/local-data/unit-hit-match-root-20261001/`.
`readback.json` records the fresh compile and nine targets; `native/receipt.json` SHA-256 is
`9b45d9e6e039ba119d4b8c1aad58e64cc066af72ea1d090db47532179388e9bc`.
The original driver and historical mismatches above remain preserved.

## Mesh/sphere producer — October 1 recheck

The lead separately reproduced full original and compiled
`CMeshCollisionVolume::CollideWithSphere` bodies at `0x004ac6e0` in Unicorn.
The original `ResolveContact` and vector/mesh helpers execute; the geometry
query at `0x004ac4a0` supplies a declared sequence of contacts and misses, and
the motion-controller query returns zero. Thus this measures response to a
contact sequence, not whether actual triangles generate that sequence.

At `0x004ad421..0x004ad442`, the resolver writes a normal at
`report + 8 + 16 * report.count`. The caller increments count only after the
resolution and slide-direction checks (`0x004acd55..0x004acd5e`). Two paths
therefore return count two with different third-slot behavior:

- Two successful contacts followed by a miss leave all 16 bytes of slot two
  unchanged. Two distinct initial byte patterns reproduced that retention.
- A third blocking contact writes slot two before returning with count still
  two. The authored third normal was proportional to `(-1,-1,1)`.

This also disproved an assignment in the reconstruction: clearing the
accumulated hit after a successful resolution. Retail clears the part-loop
register at `0x004acd5c`, while retaining the hit local subsequently tested at
`0x004acd7b`. Removing the erroneous assignment restores the return value and
movement publication after one or two successes followed by a miss.

The lead reproduced 48 runs: original, former candidate and corrected
candidate across eight paths and two storage patterns. The corrected candidate
agrees on return, complete report and movement bytes, and dependency sequence
in all 16 scenarios; the former candidate differs in four. Executed-address
bounds, unused-code traps, return/stack, preserved registers and canaries are
checked. All 31 existing exact addresses and three vtables survive the source
change, but the producer's complete body still does not match retail.

Dispatcher stores at `0x004266f1..0x00426759` initialize scalar report fields
and relative movement, without initializing the normal array. On an admitted
result, `0x004268bf` writes report `+0 = 1`; calls at `0x004268cb` and
`0x004268de` receive that same report pointer. A preceding callback may mutate
it; no claim here covers every callback or report producer.

Private reproduction owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/report-normal-slot-20261001/`.
`root-reproduction.json` SHA-256 is
`a3ad28737868b6b26d09a1b9544552dc938fa04096130cad5a8eff84d0faad19`.
The adjacent lead owner `integration-root-20261001/readback.json` binds the
freshly compiled and relocated producer to the exercised candidate. These are
emulator experiments, separate from the native x87 threshold experiment above.

## Limits and next falsifier

This disproves the claim that the omitted spill is merely cosmetic. It does
not demonstrate a retail gameplay bug or a reachable gameplay disagreement.
The optional squad callback, admission guards, contact generation and final
virtual calls are outside the executed block; the live game's x87 control
word was not observed. Test vectors are authored inputs, not captured contacts.

For reconstruction, preserve the observed rounding boundary and fixed
three-normal sum; a generic normalize operation is not yet demonstrated to be
interchangeable. The next bounded check is actual triangle generation of a
two-contact sequence and the report contents at each callback. Runtime
reachability requires an admitted captured report and its actual x87 control
word, followed by replay of the exact values through both blocks. The authored
storage patterns are not claimed to be ordinary retail stack contents. Full
body matching is now closed for this function; the caller/producer runtime questions remain.
