# Name-grading ledger — 2026-07-26 revision

> **Amended 2026-07-27 in two cells.** `0x005386d0`, which this note reports as
> false but explicitly leaves untouched, has since been demoted to
> `DestructorBody_005386d0`. `RESIDUAL_FREEFORM` 97 → **98**,
> `IMAGE_TYPE_TOKEN` 1,099 → **1,098**, honest residual 1,866 → **1,867**.
> Nothing else in this note changes. See
> [`name-grading-ledger-2026-07-27-demotion2.md`](name-grading-ledger-2026-07-27-demotion2.md).

Supersedes the counts in
[`name-grading-ledger-2026-07-25.md`](name-grading-ledger-2026-07-25.md), which
remains the record of the RTTI re-prefix wave and of the 0x08-byte incident. This
note records three corrections to the *grader itself*. The 07-25 file's
`SOURCE_BACKED` figure of 1,009 and its sentence "declaration-aware, not a
substring match" are **both wrong** and are corrected here.

Adversarial scrutiny of the **regrade** was a single independent pass, not two.
Six of its objections were checked and held, and two of them changed the shipped
tool (see `local-lab/GHIDRA-REGRADE-2026-07-26.md` §3a).

**The rename wave got two independent passes.** Between them they upheld two of
the three contested decisions on independent byte evidence and **refuted the
third**, which is recorded and acted on below.

Produced by `tools/re_ledger.py` over the same 6,969-function inventory and the
same pristine specimen (sha256 `74154bfa…`, which the tool refuses to run
without).

```
py -3 tools/re_ledger.py \
  --binary <pristine BEA.exe> \
  --inventory <exported inventory>.tsv \
  --reference-source references/Onslaught \
  --verify <re-verify>.tsv
```

The seven-cohort partition is the **default** as of 2026-07-26.
`--partition-unbacked` is retained as an accepted no-op so the invocation printed
in earlier revisions of this file keeps reproducing; `--no-partition-unbacked`
restores the undivided eight-grade view for comparison only.

Working detail and per-address diffs: `local-lab/GHIDRA-REGRADE-2026-07-26.md`.

## Update 2026-07-26 (later) — 13 renames and 1 demotion APPLIED to the live database

The sentence "no Ghidra database was opened or mutated; no function was renamed"
was true when this file was first written and is **no longer true**. Thirteen of
the proposed fifteen renames were applied to the live maintainer database under
backup → canary → dual readback → promote, with the full receipts and the
address-by-address evidence in
`local-lab/GHIDRA-RENAME-WAVE-2026-07-26.md` (lab-only, gitignored).
Two of the fifteen were **refuted by test and not applied**:

- `0x0053a050` is not `CBLTexture`'s constructor. It allocates a 0x158-byte
  object, constructs a CBLTexture into it, and stores the pointer at `[this+4]`.
  It owns a CBLTexture; it is not one. The 22-factory exclusion missed it because
  that filter matches on the **name** and this one is named `__Constructor`.
- `0x004a4e80` is called by `CConfirmMenuOptionsList`'s scalar deleting
  destructor but its body only ever installs `CMenuOptionsList`'s vtable
  `0x5dc650`, never its own `0x5dc664`. The call edge and the body disagree about
  which class the code implements, and the bytes cannot separate "a second
  non-folded copy of the base destructor" from "an empty derived destructor that
  runs only base cleanup". Naming it from the call edge would encode reachability
  as implementation identity — the same over-claim this revision exists to
  correct. **Not applied.**

A fourteenth mutation followed, of a different kind: **`0x0048c300` was demoted**,
not renamed. See "Not claimed" below and §the demotion note.

The counts below are the **post-rename, post-demotion** figures, measured from a
fresh export of the live database (`targets=6969 found=6969 missing=0`).

## Correction 1 — `SOURCE_BACKED` was over-claiming by 481 rows

The declaration pattern `\b(?:class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)`, applied
to raw file text, also matches an **elaborated type specifier** — `class
CDXTexture *image` — which is a *use* of a type, not a declaration of one.

`CDXTexture` has **no definition anywhere** in the reference tree (106 `.cpp`/`.h`
files under `references/Onslaught`). Its
only three occurrences are two pointer declarations in `XBoxMemoryCard.h` (lines
69 and 98) and one parameter in `XBoxMemoryCard.cpp:531`. It backed **368 of the
1,009 `SOURCE_BACKED` rows (36.5%)**. The 1,009 rested on **71 distinct
prefixes**, not the 188 tokens the pattern captured.

The same pattern also **missed** a real definition: a comment on
`Controller.h:35` ends with the word "class", `\s+` spans the newline, and the
real `class IController : public CMonitor` on line 37 is consumed as the captured
token rather than matched.

This is the same failure family as the 0x08 backspace byte recorded on 07-25, and
it was found the same way — by executing the artefact against the corpus rather
than reading it. The 07-25 lesson generalises further than it was stated: reading
a pattern does not tell you what it matches, and neither does a pattern that
*looks* stricter than a substring test.

The check is now **definition-aware**: comments and string literals are blanked
(this is what repairs the `IController` miss), preprocessor conditional lines are
blanked, and a class head must be followed by `{` — optionally through a base
specifier whose character class excludes `*`, `&`, `(`, `)` and `;`. Macro class
definitions (`DECLARE_THING_CLASS`) are collected, and the file glob is now
recursive.

**188 raw captures → 120 definition tokens** (71 lost, 3 gained; 188 − 71 + 3 =
120). **481 rows across 19 prefixes lose the grade: 1,009 → 528.** Predicted in
advance and met exactly.

## Correction 2 — three grader defects that discarded or inflated evidence

- **"Functions reached by RTTI: 2,127" over-stated reach by 580.** Only **1,547**
  of those `.text` DWORDs are inventory function starts; the other 580 are never
  graded. The tool now prints both numbers.
- **14 rows were graded as disagreeing with RTTI while making no class claim at
  all** (10 `RTTI_CONFLICT`, 4 `RTTI_AMBIGUOUS`; `VFuncSlot_*`,
  `LandscapeDetail_*`, `DebugTrace`, `Return1f`). An absent claim cannot
  disagree. New grade `OWNER_PREFIX_MISSING`.
- **8 vtable-slot targets discarded their RTTI observation** because the
  `unnamed` branch ran first. New grade `UNNAMED_RTTI_TARGET`.

## Correction 3 — `UNBACKED` was one word for six different situations

`UNBACKED` at 55.8% was quoted as the headline gap. It is not a naming-quality
metric: 30% of it is compiler output that can never carry a developer name, and
the import stubs inside it carry the strongest name artefact in the file.

With `--partition-unbacked` it is replaced by seven cohorts, each a byte test or
a set membership, with no judgement and no remainder. The partition was
**reimplemented from scratch** here rather than applied from the proposed map,
and the two independent implementations agree on **3,888 of 3,888** addresses.

## Results

| grade | 2026-07-25 | 07-26 regrade | 07-26 final | what it licenses |
| --- | ---: | ---: | ---: | --- |
| RTTI_CONFIRMED | 1,400 | 1,400 | 1,400 | prefix equals the RTTI-resolved owning class |
| RTTI_CONFLICT | 35 | 25 | 25 | RTTI resolves an owner, the prefix disagrees |
| RTTI_AMBIGUOUS | 104 | 100 | 100 | in several vtables, no single ancestor |
| OWNER_PREFIX_MISSING | — | 14 | 14 | RTTI reaches it; the name makes no class claim |
| BINARY_STRING | 217 | 217 | **218** | the token exists as a string — never ownership |
| SOURCE_BACKED | 1,009 | **528** | 528 | a *different* codebase defines this class |
| UNNAMED_RTTI_TARGET | — | 8 | 8 | default name, in a vtable, owner unresolved |
| UNNAMED | 316 | 308 | 308 | default Ghidra name |
| **UNBACKED (total)** | **3,888** | **4,369** | **4,368** | **still one parent, now with seven children** |
| … COMPILER_EH_FUNCLET | — | 1,179 | 1,179 | MSVC unwind funclet; **not human-namable** |
| … PE_IMPORT | — | 36 | 36 | import-table identity (32 exact, 4 ordinal) |
| … RESIDUAL_FREEFORM | — | 96 | **97** | no `Prefix__` in the name |
| … VTABLE_VA_IN_BODY | — | 176 | **188** | that class's vtable VA appears in these bytes — **upper bound, not ownership** |
| … IMAGE_TYPE_TOKEN | — | 1,100 | **1,099** | the class exists in this build — **not ownership** |
| … IMAGE_TYPE_SUBSTRING | — | 668 | 668 | the token occurs as bytes somewhere |
| … INVENTED_PREFIX | — | 1,114 | **1,101** | **no artefact of any kind** |
| **total** | **6,969** | **6,969** | **6,969** | |

The final column moves by exactly the 14 applied rows. The 13 renames: 13 leave
`INVENTED_PREFIX`, 12 land in `VTABLE_VA_IN_BODY` and 1 in `BINARY_STRING`. The
1 demotion: `0x0048c300` leaves `IMAGE_TYPE_TOKEN` for `RESIDUAL_FREEFORM`,
because the demoted name makes no class claim at all.

**The demotion raises the residual, and that is correct.** 1,865 → **1,866**.
Removing a false claim is not a gain in evidence; it is the withdrawal of a claim
that never had any. A ledger that fell here would be measuring confidence rather
than evidence.

**That last row is a located grader defect, not a result.** `0x004e6870`
`CNormalSquad__Constructor` graded `BINARY_STRING` rather than
`VTABLE_VA_IN_BODY` because `BINARY_STRING` is tested in the main grade chain
**before** the partition runs, and `CNormalSquad` occurs as a literal ASCII string
as well as being a type descriptor. It is a measured instance of weak point #10 in
the regrade note — `BINARY_STRING` is largely redundant with `IMAGE_TYPE_TOKEN`
and ranked above it. Left unrepaired here for the reason that note already gives:
reordering the grade chain breaks comparability with the before/after measured in
this wave.

The seven children sum to their parent with no remainder in both columns.
`UNBACKED (total)` **rose** from 3,888 to 4,369 because the `SOURCE_BACKED` repair
released 481 rows into it, then fell by 1 to 4,368 when the rename wave moved
`0x004e6870` out to `BINARY_STRING`.

RTTI reach: **2,127** `.text` DWORDs appear in a recovered vtable slot, of which
**1,547** are inventory function starts. 656 classes have a recovered hierarchy.

## What these numbers do and do not mean

**Subdividing is not progress.** Every row moved into a named cohort; none gained
evidence. The tool deliberately keeps printing the `UNBACKED (total)` parent above
the seven children, because emitting only the children makes the headline read
`UNBACKED: 0` and that would be quoted as if the naming were now backed.
`INVENTED_PREFIX` is strictly *worse* than the old
`UNBACKED`: `UNBACKED` meant "no evidence found", while `INVENTED_PREFIX` is a
positive finding of absence — no type descriptor, no byte occurrence anywhere in
2,506,752 bytes, no reference-source definition. 120 distinct tokens, `CFastVB`
alone accounting for 393 functions.

**The honest residual is 1,866, not 3,888 and not 0.** Removing the 1,179
compiler funclets leaves 5,790 functions that could in principle carry a
developer name; of those, 1,101 `INVENTED_PREFIX` + 668 `IMAGE_TYPE_SUBSTRING` +
97 `RESIDUAL_FREEFORM` = **1,866** rest on nothing image-local. That is 32.2% of
the human-namable set. It was 1,878 after the regrade — *up* by 18 from the 1,860
estimated on 07-25 because 18 rows fell out of `SOURCE_BACKED` entirely — the
rename wave took 13 off it, and the demotion put 1 back.

**Thirteen names is 0.7% of the residual, and that is the honest scale of the
result.** The technique behind it (§ the rename-wave note) is accurate — 95.2%
measured — but nearly exhausted: it works through MSVC scalar deleting
destructors, and destructor bodies in this image were already mostly named with a
real class prefix. Only 12 residual rows were reachable by it at all. The
remaining 1,866 will not fall to another vtable-shaped trick.

**`IMAGE_TYPE_TOKEN` is not ownership.** It says the class exists in this build
and the prefix spells it. A non-virtual member, a constructor and a static of
that class are indistinguishable under it, and so is a wrong guess that happens
to name a real class.

**`SOURCE_BACKED` is still evidence about a different codebase.** Repairing it
removed rows that never had evidence; it did not convert the remaining 528 into
evidence about this executable. It also still fans out: one accepted class token
licenses every suffix anyone attached to it, across 52 prefixes. The 2026-07-26
adversarial pass (and the earlier 07-26 review before it) held that the grade
should be renamed off the RTTI axis; that rename is deferred so the before/after
measured here stays comparable.

**`VTABLE_VA_IN_BODY` is an upper bound, and is deliberately not called
`VTABLE_STORE_OWN`.** The proposal named it `..._OWN`; `OWN` asserts ownership and
the test proves only that the class's vtable VA appears in these bytes — equally
true of a constructor, of a factory building an instance, and of a member seating
a sibling subobject's vptr. Measured: **4 of the 176** rows are Create/Spawn-shaped
(`CSpawnerData__CreateAndRegisterByName`). The sound version needs a backward
slice proving the store's destination is entry `ECX` plus a known subobject
offset; that was not run **for the cohort**. It *was* run by hand on the six
constructor-shaped rename candidates, and it refuted one of them (`0x0053a050`),
which is direct evidence that the cohort over-collects as this paragraph says.

## Not claimed

- No claim that any specific name is correct. This grades evidence, not accuracy.
- The 13 renames applied on 2026-07-26 change the class **prefix** only. Each is
  supported by a byte chain recorded per address in
  `local-lab/GHIDRA-RENAME-WAVE-2026-07-26.md` (lab-only, gitignored).
  Two of the 15 proposed were refuted by test and not applied. The three
  "family-level leads" (`CSquadNormal`, `CScriptObjectCode`, `CSpawnerThng`)
  were **not** applied as families: only the individually adjudicated members
  were renamed, and the sibling functions carrying those prefixes still carry
  them.
- **`0x0048c300` was DEMOTED, not retained and not reassigned.** It was named
  `CInfluenceMap__dtor` and that name is positively **false** by RTTI. Measured,
  and independently reached by both adversarial passes: its wrapper `0x0048c2e0`
  carries the canonical scalar-deleting-destructor bytes and is slot 1 of
  **`CInfluenceNode`**'s vtable `0x5dc050`; `CInfluenceMap`'s own vtable
  `0x5dfcb4` slot 1 is `0x0050b930`, whose wrapper calls `0x0050b950`, and *that*
  body stores `0x5dfcb4` into entry-`this`; `CInfluenceNode`'s RTTI hierarchy does
  not contain `CInfluenceMap` (they share only `CMonitor`/`IListener`); and
  `0x0048c300` stores no recovered vtable at all.

  The first version of this note **retained** the false name and merely warned
  about it here, on the grounds that the only alternative — asserting
  `CInfluenceNode` — fails the ancestor-shadow gate that licensed the rename wave.
  `gpt-5.6-sol` refuted that as a false binary and it was right: the third option
  lowers no gate at all. The symbol is now the class-neutral
  **`DestructorBody_0048c300`**, which asserts only what is proven (it is a
  destructor body), with all of the above attached as a function comment in the
  database itself.

  **A known-false class name is worse than an unknown one**, because it
  contaminates decompiler output, symbol search, and every automated ownership
  pass built on top — none of which read this file. A warning in a document does
  not repair a false assertion living in the database.

- **A mechanical sweep for the same class of error found 6 more, of which 2 are
  strong.** Criterion: a function named `P__*` where `P` is a real RTTI class,
  which sits uniquely on class `Q`'s destroy path with `P != Q`, and where `P`
  has a destructor body of its own that is uniquely claimed by `P` — so the
  function cannot be `P`'s. Six rows qualify. In four the two classes are related
  by RTTI, which is the same undecidable base/derived situation as `0x004a4e80`
  and is **not** demonstrably false. In **two** the classes are RTTI-unrelated,
  which is the strong form: `0x0048c300` (now demoted) and **`0x005386d0`
  `CScriptEventNB__Destructor`**, which sits on `CPostEventData`'s destroy path
  (`CPostEventData` vtable `0x5e4f34` slot 1 `0x5386b0` → `0x005386d0`) while
  `CScriptEventNB` has its own body at `0x00538950`; the two classes share only
  `CMonitor`/`IListener`. **`0x005386d0` was not touched** — it is reported, not
  applied. *(Superseded 2026-07-27: it has since been re-verified from bytes and
  demoted to `DestructorBody_005386d0`; see the 07-27 note.)*
  `RTTI_CONFLICT`'s 25 rows are the separate, already-graded channel
  where direct vtable membership contradicts the prefix.

- The suffix of every name remains ungraded, under every grade in the table.
- The misattribution recorded on 07-25 is unchanged in effect, but *(superseded
  2026-07-27)* it is not an abstract-base rule and it is no longer unbounded: the
  cause is the absence of an emitted standalone vftable, and exactly **11** of the
  667 type descriptors lack one, putting **282** of 2,127 RTTI-reached functions
  inside the upper bound. See
  [`name-grading-ledger-2026-07-25.md`](name-grading-ledger-2026-07-25.md),
  "A resolver limitation this pass exposed".
