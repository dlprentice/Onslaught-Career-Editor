# The second demotion — `0x005386d0`, and the residual goes up again

Date: 2026-07-27. Amends, in its counts only, the
[2026-07-26 ledger](name-grading-ledger-2026-07-26.md), which remains the record
of the grader corrections, the 13-rename wave, and the first demotion.

**What changed in the database:** exactly one function name.

| address | before | after |
| --- | --- | --- |
| `0x005386d0` | `CScriptEventNB__Destructor` | **`DestructorBody_005386d0`** |

The 07-26 ledger reported this address as the strongest outstanding false name
and explicitly said it "was not touched — it is reported, not applied". It is
applied now, on the same reasoning that licensed `0x0048c300`: a known-false
class name is worse than an unknown one, because it contaminates decompiler
output, symbol search and every automated ownership pass, none of which read this
file.

`FUN_005386d0` was rejected — the repo's own preflight refuses `FUN_` targets as
`WEAK_NAME`, and it would discard the one thing that *is* proven, that this is a
destructor body reached by a canonical scalar deleting destructor.

## The premise was re-verified from bytes before anything was mutated

The 07-26 claim was agent-reported. Every element was re-measured here against
the pristine specimen (sha256 `74154bfa…`), and all five hold:

| claim | measured |
| --- | --- |
| `CPostEventData`'s vtable `0x005e4f34` slot 1 is `0x005386b0` | slot 1 = `0x005386b0` |
| `0x005386b0` is a canonical MSVC scalar deleting dtor targeting `0x005386d0` | head `56 8B F1 E8 18 00 00 00 F6 44 24 08 01` → `0x005386d0` |
| `CScriptEventNB` has its own separate body | vtable `0x005e4f44` slot 1 `0x00538780` → `0x00538950` |
| `0x00538950` is CScriptEventNB's own | 16 bytes: `MOV [ECX],0x005e4f44` then `JMP 0x004bac40` |
| the classes share only `CMonitor`/`IListener` | base arrays `{CMonitor, CPostEventData, IListener}` and `{CMonitor, CScriptEventNB, IListener}`; neither contains the other |

Two measurements were added beyond the 07-26 report:

- **Bounded to its own extent** `[0x005386d0, 0x00538740)` — 112 bytes — the body
  contains exactly one recovered vtable VA, `0x005e4f34`, **CPostEventData's
  own**, and no other. An unbounded scan appears to show `0x005e4f44` too; that
  occurrence is at `0x0053876c`, inside `CScriptEventNB__Init`, past the end of
  this function. Bounding matters, and an unbounded scan here would have produced
  the opposite reading.
- **Image-wide uniqueness**: `0x005386d0` is the scalar-deleting-destructor target
  of exactly one class (`CPostEventData`), and `0x00538950` of exactly one
  (`CScriptEventNB`).

### A live loose end, recorded rather than acted on

Unlike `0x0048c300` — which stored no vtable at all, leaving demotion as the only
honest option — **the positive attribution `CPostEventData__Destructor` would
pass the own-vtable arm of the 07-26 wave's ancestor-shadow gate**, because this
body stores CPostEventData's own vtable. It was left class-neutral because this
task's scope was withdrawal of a false name, not promotion of a new one.
Promoting it is a separate, evidenced decision, and it is noted in the function
comment in the database so the next reader meets it there.

## Counts — amending the 07-26 table

Only two cells move. Everything else in the 07-26 results table stands.

| cohort | 07-26 final | **07-27** |
| --- | ---: | ---: |
| … RESIDUAL_FREEFORM | 97 | **98** |
| … IMAGE_TYPE_TOKEN | 1,099 | **1,098** |
| **honest residual** | **1,866** | **1,867** |
| human-namable | 5,790 | 5,790 |
| total | 6,969 | 6,969 |

**The residual rose, and it was predicted to rise before the rename was applied,
not explained afterwards.** Withdrawing an unsupported claim cannot lower a count
of unsupported names. A ledger that improved here would be measuring confidence,
not evidence. Every one of twenty pre-registered values was met; the
pre-registration is `local-lab/re-ledger/demote2-2026-07-27/PREREGISTERED.md`
(untracked) and was written before the first mutating step.

Discipline receipts: pre-backup 19 files / 181,537,671 B / 0 diffs with
`ReadOnlyOpen=PASS`; preflight self-test PASS and the 1-row map 0 findings;
canary applied on a clone first, `applied=1 skipped=0 missing=0 bad=0`, dual
readback over **all 6,969** functions showing 1 name changed and **0 unintended**;
live apply identical, and the live name map **byte-identical to the canary across
all 6,969** (sha256 `0e868eaf6790…`); comment `applied=1 bad=0`;
`total_functions=6969` and `weak_functions=316` both unchanged; post-backup
verified with `ReadOnlyOpen=PASS`.

## The limit on the sweep, restated because it keeps getting dropped

The sweep that produced these candidates sees **only the destructor channel** —
names contradicted through a class's vtable destroy path. A function named
`CFoo__DoThing` that is really `CBar`'s non-virtual member is **invisible** to it,
because neither class's vtable reaches either function.

**Six is a floor on known-false names, not a bound.** "The sweep found six" must
not become "there are six". Of the six, two were RTTI-unrelated and both are now
demoted; the remaining four are base/derived pairs where the name may be right and
the evidence does not decide.

### What a wider sweep would take (scoped, not run)

The destructor channel is cheap because RTTI hands over a class→function edge for
free. No other channel does. A non-destructor sweep would need, for each named
`CFoo__Method`, an independent owner for that function — the tractable sources
being (a) the vtable slot it occupies, if any, which is the already-graded
`RTTI_CONFLICT` channel of 25 rows; (b) the vtable VA stored in its own body,
bounded to the function extent, which is the `VTABLE_VA_IN_BODY` cohort of 188
and is an upper bound rather than ownership; and (c) the `this`-pointer class at
its call sites, which requires type propagation the database does not currently
carry. Only (c) is new work, and it is the expensive one. Channels (a) and (b)
are already measured and neither is a proof of ownership on its own, so a wider
sweep would mostly re-partition rows already known to be weak. That is the
argument for scoping it deliberately rather than assuming it is a quick pass.
