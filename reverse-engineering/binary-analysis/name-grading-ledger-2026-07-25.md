# Name-grading ledger — every function name graded by its evidence

> **Superseded in two figures and one sentence, 2026-07-26 — banner added
> 2026-07-28.** Both defects are in the grader, not in this wave, and both are
> corrected in
> [`name-grading-ledger-2026-07-26.md`](name-grading-ledger-2026-07-26.md).
>
> 1. **`SOURCE_BACKED` 1,009 is wrong.** The declaration pattern also matched
>    **elaborated type specifiers** (`class CDXTexture *image`, which uses a type
>    rather than declaring one), and `CDXTexture` — which has no definition
>    anywhere in the 106-file reference tree — alone backed **368 of the 1,009**
>    rows. The repaired count is **528**. The sentence below, "`SOURCE_BACKED` is
>    declaration-aware, not a substring match", is wrong for the same reason and
>    is likewise superseded. (07-26 note, Correction 1.)
> 2. **"Functions reached by RTTI: 2,127" over-states reach by 580 — the wrong
>    word is "Functions", not the number.** 2,127 is the correct count of
>    RTTI-reached `.text` DWORDs, and the independent 2026-07-27 scan quoted
>    further down this same file reproduces it exactly. But only **1,547** of
>    those DWORDs are inventory *function starts*; the other 580 are never
>    graded. (07-26 note, Correction 2.)
>
> **Everything else in this note stands**, and is why it is not withdrawn: the
> RTTI re-prefix wave and its before/after table, the 0x08-byte incident and its
> method lesson, and the resolver-limitation section together with its own
> 2026-07-27 supersede blockquote.
>
> *Unreconciled and left as UNKNOWN:* the 07-26 note's residual figure appears as
> **1,865** in its own prose while the amendment banner at its head tracks
> 1,866 → **1,867**. Which is right is not settled here, and nothing in *this*
> file depends on it. Re-running `tools/re_ledger.py` against the export that
> note used, and diffing the residual bucket, would settle it.

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
*(Superseded 2026-07-26 — see banner. 2,127 is the count of RTTI-reached `.text`
DWORDs, not of functions; only **1,547** are inventory function starts.)*

| grade | count | share | meaning |
| --- | ---: | ---: | --- |
| RTTI_CONFIRMED | 1,068 | 15.3% | current prefix equals the RTTI-resolved owning class |
| RTTI_CONFLICT | 367 | 5.3% | RTTI resolves an owner and the current prefix disagrees |
| RTTI_AMBIGUOUS | 104 | 1.5% | in several vtables, hierarchy could not pick one owner |
| BINARY_STRING | 217 | 3.1% | prefix appears verbatim as a string in the binary |
| SOURCE_BACKED | 1,009 | 14.5% | the pinned reference source *declares* this class or struct — ***superseded 2026-07-26: the repaired count is 528, see banner*** |
| UNNAMED | 316 | 4.5% | still a default Ghidra `FUN_`/`SUB_` name |
| UNBACKED | 3,888 | 55.8% | no supporting evidence found |

## What UNBACKED does and does not mean

**UNBACKED is "no evidence found", not "wrong".** Non-polymorphic C++ classes emit
no RTTI whatsoever, so a perfectly correct prefix for such a class scores UNBACKED
by construction. The figure bounds how much of the naming layer currently rests on
inference rather than artefact — it does not condemn any individual name.

*(Superseded 2026-07-26 — see banner. The following paragraph is wrong: the
pattern also matched elaborated type specifiers, so it was not
declaration-aware.)*

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

## Update — 332 conflicts adjudicated and applied, then re-graded from a fresh export

The 367 `RTTI_CONFLICT` rows were adjudicated per function, grouped by
(current prefix → RTTI owner) pair: **332 SAFE_REPREFIX**, 30 NEEDS_REVIEW,
4 UNCERTAIN, 1 KEEP_CURRENT. Only the 332 were applied, swapping the class prefix
and preserving the descriptive suffix.

Most of the 367 were not class-vs-class disputes at all. 86 current prefixes were
`Shared*` placeholder buckets, 57 were `<Class>VFunc` (the same class with a token
welded on), 34 were offset-named inventions, 18 were not class tokens. **251 of the
current prefixes are not RTTI classes in the binary**, and 69 more are RTTI classes
unrelated by inheritance to the resolved owner.

34 invented offset names recovered real developer names one-for-one —
`CComponentScalarD8 → CComponentMaxYaw`, `CComponentFlag12C → CComponentTentacle`,
`CExplosionScalar34 → CExplosionRadius`. The offsets survive in the metadata
comments, so nothing is lost. Verified by presence: those RTTI descriptors are in
the binary; `CComponentScalarD8` is not.

Ten `CAsmInstruction → CInstructionOP_*` rows are a genuine non-circular check: the
RTTI opcode name and the prior campaign's independently-derived behavioural suffix
agree **9 of 10** (`OP_OR`/`ExecuteOr`, `OP_GREAT_EQ_THAN`/`ExecuteGreaterOrEqual`).
The tenth (`OP_RETURN`/`ExecutePop`) is consistent but unverified.

Applied live under backup → canary-20 on `project-rw` → dual readback → promote →
remainder: **renamed 332 / failed 0 / mismatched 0 / missing 0**. Backups verified
by file count, byte total and per-file SHA-256 (0 diffs).

**Readback is not proof, so the database was re-exported and re-graded from
scratch.** The prediction was stated in advance and met exactly:

| grade | before | after | delta |
| --- | ---: | ---: | ---: |
| RTTI_CONFIRMED | 1,068 | **1,400** | **+332** |
| RTTI_CONFLICT | 367 | **35** | **−332** |
| RTTI_AMBIGUOUS | 104 | 104 | 0 |
| BINARY_STRING | 217 | 217 | 0 |
| SOURCE_BACKED | 1,009 | 1,009 | 0 | *(superseded — 528, see banner)* |
| UNNAMED | 316 | 316 | 0 |
| UNBACKED | 3,888 | 3,888 | 0 |
| total | 6,969 | 6,969 | 0 |

Every changed row moved `RTTI_CONFLICT → RTTI_CONFIRMED`; no non-map address moved.
The 35 residual conflicts are an **exact set match** with the 35 deliberately
excluded rows — symmetric difference zero.

The metadata export was driven from a freshly enumerated address list rather than
the previous one, so a created or deleted function could not hide behind a stale
list. The two address sets proved identical.

### A resolver limitation this pass exposed

**A class with no emitted standalone vftable never enters the candidate set.**
`tools/re_ledger.py` builds candidates only from vftables it finds by scanning for
a dword equal to a complete-object-locator address (lines 437–462); the ancestor
map harvested from `pBaseClassArray` (lines 420–435) is used solely to break ties
*among* candidates. So a base that declares a virtual method but emits no vftable
of its own cannot win ownership, and the single emitted copy of that method is
attributed to whichever derived class's vftable carries it.

Demonstrated on `0x004bb450`, which RTTI attributes to `CPCMusic`. `CMusic` **is**
present in RTTI — type descriptor `.?AVCMusic@@` at `0x0063dfc0`, and it appears in
`CPCMusic`'s class-hierarchy descriptor (`numBaseClasses = 2`, bases `CPCMusic`,
`CMusic`) — but it has **zero** complete object locators and **zero** vftables, so
it is never a candidate. `Music.h:92-102` corroborates the shape: `CMusic` declares
nine virtuals, seven of them `=0`, and the concrete singleton is
`extern class CPCMusic MUSIC` (`Music.h:111`). `CPCMusic`'s vftable at `0x005e4934`
has exactly nine slots, of which 0–6 are a tight `CPCMusic`-local cluster
(`0x00515320`–`0x005153a0`) and 7–8 lie elsewhere — the two `CMusic`-defined
virtuals. The class prefix is right and the RTTI owner is misleading. That is the
single `KEEP_CURRENT`.

**And the exposure is bounded.** Of the 667 RTTI type descriptors in the image,
**656 own at least one standalone vftable and 11 do not**: `CAsmInstruction`,
`CBitmapFont`, `CDetailItem`, `CFrontEndVideo`, `CLandscape`, `CMeshVB`, `CMusic`,
`CSmallAirUnit`, `CTexture`, `CThreeWay`, `CWater`. Those eleven are the entire
population of classes that can be lost this way. The functions at risk are those in
their descendants' vftables: **282** of the 2,127 functions the RTTI walk reaches,
a **13.3%** upper bound — most of those slots are genuinely the derived class's own.
"RTTI is the stronger evidence" remains a qualified claim, but the qualification is
now sized rather than open-ended.

> **Superseded 2026-07-27.** This section previously read: "**Abstract base classes
> are invisible to the ownership resolver by construction.** They have no vtable and
> no complete object locator… **How many undetected instances exist cannot be
> bounded**." Both halves are wrong.
>
> *Abstractness is not the mechanism.* Re-measured on the pristine specimen
> (sha256 `74154bfa…`, read-only): **39** classes have an emitted vftable carrying at
> least one `_purecall` slot — `0x0055df1f`, whose body is
> `6a 19 e8 63 23 00 00 59 c3` = `PUSH 0x19; CALL __amsg_exit; POP ECX; RET`, the
> MSVC R6025 stub — which makes those classes abstract, and every one of them also
> has a complete object locator. Four are pure interfaces: `IRenderableThing`
> (vftable `0x005d9540`, **29/29** slots `_purecall`, COL `0x0060cff0`, type
> descriptor `0x00622ba0` `.?AVIRenderableThing@@`, declared at `thing.h:65`),
> `CTweak`, `CWaitingThread`, `IListener`; `CController` is 15/18 and `CDataType`
> 2/20. The tracked [`functions/DataType.cpp.md`](functions/DataType.cpp.md) already
> recorded `CDataType (base)` as an "(abstract base)" with vftable `0x005e4b4c`,
> contradicting the rule from inside this repository. What actually excludes a class
> is the absence of an *emitted standalone vftable* — a link-time fact about whether
> the class was ever instantiated, not a language-level fact about pure virtuals.
>
> *And it is bounded*, by the set difference above. Method: read the specimen's type
> descriptors, complete object locators, vftables and base-class arrays directly and
> subtract. The same scan reproduces this file's own published **656** classes and
> **2,127** RTTI-reached functions exactly, which is why it is trusted to contradict
> the paragraph it replaces.

Multiple inheritance is also present and visible in the binary
(`DECLARE_MULTI_INTERFACE_CLASS(CThing, IAudibleThing, IRenderableThing)`,
`thing.h:65`; function `0x004040a0` occupies slots {0,9,10}). Ownership survives it,
but **any name encoding a slot number is unsound** — which independently
corroborates rejecting the 15 `VFuncSlot_NN_addr` suffixes as NEEDS_REVIEW.

Thunks display the name of the function they thunk. `0x00447b50` is a confirmed
case: its body is `E9 BB A4 FB FF JMP 0x00402010`, and it changed name without any
rename being issued against it. It contributed 1 cosmetic name change and **0** grade
movement, so the ±332 is neither inflated nor masked.

## What is not claimed here

- No claim that any specific name is correct. This grades evidence, not accuracy.
- `RTTI_CONFIRMED` means the class **prefix** agrees with the binary's own type
  descriptor for the owning vtable. The descriptive **suffix** on those 332 names
  remains ungraded.
- The 35 residual conflicts are unadjudicated by design and still need per-function
  decisions.
- The per-function rationale comments were dropped to satisfy the rename parser's
  two-field requirement and have not yet been applied.
