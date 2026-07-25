# Name-grading ledger — every function name graded by its evidence

Date: 2026-07-25. Produced by `tools/re_ledger.py` over the live 6,969-function
inventory and the pristine specimen (sha256 `74154bfa…`, which the tool refuses to
run without). Reproducible:

```
py -3 tools/re_ledger.py --binary <pristine BEA.exe> \
  --inventory <exported inventory>.tsv --reference-source references/Onslaught
```

## What this measures

Not whether a name is *right* — whether there is **evidence** behind it. The
project's goal for the RE lane is "every name graded by its evidence", not "every
name replaced". A name like `CUnitAI__SetStateTimestampCCToNow` carries a
behavioural hypothesis that may well be correct; replacing it with
`CActor__vfunc_0` would trade a useful description for a correct prefix and lose
the description. So the tool emits a grade and leaves the names alone.

Ownership is resolved through the full MSVC RTTI hierarchy rather than by vtable
membership alone. A base class's virtual methods appear in every derived class's
vtable, so membership alone attributes inherited methods to the wrong class. The
tool walks `CompleteObjectLocator +16 → RTTIClassHierarchyDescriptor →
pBaseClassArray → RTTIBaseClassDescriptor` to build each class's ancestor set, then
attributes a shared function to the candidate that is an ancestor of all the others.

## Results

Classes with a recovered hierarchy: **656**. Functions reached by RTTI: **2,127**,
of which owner resolved for **1,982** and **145** remain ambiguous.

| grade | count | share | meaning |
| --- | ---: | ---: | --- |
| RTTI_CONFIRMED | 1,068 | 15.3% | current prefix equals the RTTI-resolved owning class |
| RTTI_CONFLICT | 367 | 5.3% | RTTI resolves an owner and the current prefix disagrees |
| RTTI_AMBIGUOUS | 104 | 1.5% | in several vtables, hierarchy could not pick one owner |
| BINARY_STRING | 217 | 3.1% | prefix appears verbatim as a string in the binary |
| SOURCE_BACKED | 1,009 | 14.5% | the pinned reference source *declares* this class or struct |
| UNNAMED | 316 | 4.5% | still a default Ghidra `FUN_`/`SUB_` name |
| UNBACKED | 3,888 | 55.8% | no supporting evidence found |

## What UNBACKED does and does not mean

**UNBACKED is "no evidence found", not "wrong".** Non-polymorphic C++ classes emit
no RTTI whatsoever, so a perfectly correct prefix for such a class scores UNBACKED
by construction. The figure bounds how much of the naming layer currently rests on
inference rather than artefact — it does not condemn any individual name.

`SOURCE_BACKED` is declaration-aware, not a substring match. An earlier substring
version scored 31.4% by counting any incidental occurrence of a prefix — inside a
comment, inside a longer identifier, inside a string literal. Only a prefix the
reference source actually declares as a `class` or `struct` now counts.

## Correction history — and the method lesson

This tool reported `SOURCE_BACKED = 0` and `UNBACKED = 70.3%` for part of the day.
That figure was published, then retracted, then fixed.

Root cause: a **literal backspace byte (0x08)** at the head of the declaration
regex, left by an editing pass that wrote the word-boundary escape through a
non-raw string. The pattern therefore required a literal backspace immediately
before `class`, matched nothing across all 106 reference files, and left the
declaration set empty.

The byte is invisible in rendered file output. It survived three rounds of
inspection in which the line was *read* and pronounced correct. It was found in one
line by printing `repr(decl.pattern)`.

The control experiment that appeared to exonerate the regex was worse than useless:
it **retyped** the pattern into a standalone snippet instead of executing the one on
disk, so it tested a different pattern and its agreement with expectation meant
nothing.

Two rules follow, and they generalise beyond this file:

1. To check what a value **is**, print its `repr`. Do not read it.
2. To test an artefact, execute **that artefact** — never a retyped copy of it. A
   control reconstructed from memory is not a control.

Both are the same failure this project already bans in its parity work: trusting a
code path instead of a measurement.

Corroboration for the fix: the corrected `SOURCE_BACKED` count of 1,009 exactly
equals the number of stranded rows found by an independent direct check *before* the
cause was known (4,897 = 3,888 + 1,009). An adversarial reviewer, given only the
symptom and the list of previously "ruled out" causes, independently reproduced the
same root cause and the same corrected counts.

## What is not claimed here

- No claim that any specific name is correct. This grades evidence, not accuracy.
- The 367 `RTTI_CONFLICT` rows are **not** yet adjudicated. RTTI is the stronger
  evidence for the class prefix, but a conflicting name may still describe the
  function's behaviour correctly under the wrong class, so each needs a decision
  rather than a bulk overwrite.
- No naming change was applied to the live database on the strength of this
  document.
