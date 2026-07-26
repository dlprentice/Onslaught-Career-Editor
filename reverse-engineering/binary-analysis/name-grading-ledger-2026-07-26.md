# Name-grading ledger — 2026-07-26 revision

Supersedes the counts in
[`name-grading-ledger-2026-07-25.md`](name-grading-ledger-2026-07-25.md), which
remains the record of the RTTI re-prefix wave and of the 0x08-byte incident. This
note records three corrections to the *grader itself*. The 07-25 file's
`SOURCE_BACKED` figure of 1,009 and its sentence "declaration-aware, not a
substring match" are **both wrong** and are corrected here.

Cross-model scrutiny of these changes was **one model, not two**: `grok-4.5`
(effort `high`) returned in full, and `codex exec` / `gpt-5.6-sol` (effort `max`,
`-s read-only`) **failed to converge** — every shell invocation died inside the
Windows sandbox before executing. Six of grok's objections were checked and held,
and two of them changed the shipped tool (see
`local-lab/GHIDRA-REGRADE-2026-07-26.md` §3a). A missing consult is not agreement,
and this revision has had half the scrutiny the protocol asks for.

Produced by `tools/re_ledger.py` over the same 6,969-function inventory and the
same pristine specimen (sha256 `74154bfa…`, which the tool refuses to run
without). No Ghidra database was opened or mutated; no function was renamed.

```
py -3 tools/re_ledger.py \
  --binary <pristine BEA.exe> \
  --inventory <exported inventory>.tsv \
  --reference-source references/Onslaught \
  --verify <re-verify>.tsv --partition-unbacked
```

Working detail, per-address diffs and the proposed (unapplied) rename wave:
`local-lab/GHIDRA-REGRADE-2026-07-26.md`.

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

| grade | 2026-07-25 | 2026-07-26 | what it licenses |
| --- | ---: | ---: | --- |
| RTTI_CONFIRMED | 1,400 | 1,400 | prefix equals the RTTI-resolved owning class |
| RTTI_CONFLICT | 35 | 25 | RTTI resolves an owner, the prefix disagrees |
| RTTI_AMBIGUOUS | 104 | 100 | in several vtables, no single ancestor |
| OWNER_PREFIX_MISSING | — | 14 | RTTI reaches it; the name makes no class claim |
| BINARY_STRING | 217 | 217 | the token exists as a string — never ownership |
| SOURCE_BACKED | 1,009 | **528** | a *different* codebase defines this class |
| UNNAMED_RTTI_TARGET | — | 8 | default name, in a vtable, owner unresolved |
| UNNAMED | 316 | 308 | default Ghidra name |
| **UNBACKED (total)** | **3,888** | **4,369** | **still one parent, now with seven children** |
| … COMPILER_EH_FUNCLET | — | 1,179 | MSVC unwind funclet; **not human-namable** |
| … PE_IMPORT | — | 36 | import-table identity (32 exact, 4 ordinal) |
| … RESIDUAL_FREEFORM | — | 96 | no `Prefix__` in the name |
| … VTABLE_VA_IN_BODY | — | 176 | that class's vtable VA appears in these bytes — **upper bound, not ownership** |
| … IMAGE_TYPE_TOKEN | — | 1,100 | the class exists in this build — **not ownership** |
| … IMAGE_TYPE_SUBSTRING | — | 668 | the token occurs as bytes somewhere |
| … INVENTED_PREFIX | — | 1,114 | **no artefact of any kind** |
| **total** | **6,969** | **6,969** | |

The seven children sum to the 4,369 parent with no remainder. `UNBACKED (total)`
**rose** from 3,888 to 4,369, because the `SOURCE_BACKED` repair released 481 rows
into it.

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

**The honest residual is 1,878, not 3,888 and not 0.** Removing the 1,179
compiler funclets leaves 5,790 functions that could in principle carry a
developer name; of those, 1,114 `INVENTED_PREFIX` + 668 `IMAGE_TYPE_SUBSTRING` +
96 `RESIDUAL_FREEFORM` = **1,878** rest on nothing image-local. That is 32.4% of
the human-namable set. The figure is *up* by 18 from the 1,860 estimated on
07-25, because 18 rows fell out of `SOURCE_BACKED` entirely.

**`IMAGE_TYPE_TOKEN` is not ownership.** It says the class exists in this build
and the prefix spells it. A non-virtual member, a constructor and a static of
that class are indistinguishable under it, and so is a wrong guess that happens
to name a real class.

**`SOURCE_BACKED` is still evidence about a different codebase.** Repairing it
removed rows that never had evidence; it did not convert the remaining 528 into
evidence about this executable. It also still fans out: one accepted class token
licenses every suffix anyone attached to it, across 52 prefixes. The 2026-07-26
consult (and the 07-26 cross-model note before it) held that the grade should be
renamed off the RTTI axis; that rename is deferred so the before/after measured
here stays comparable.

**`VTABLE_VA_IN_BODY` is an upper bound, and is deliberately not called
`VTABLE_STORE_OWN`.** The proposal named it `..._OWN`; `OWN` asserts ownership and
the test proves only that the class's vtable VA appears in these bytes — equally
true of a constructor, of a factory building an instance, and of a member seating
a sibling subobject's vptr. Measured: **4 of the 176** rows are Create/Spawn-shaped
(`CSpawnerData__CreateAndRegisterByName`). The sound version needs a backward
slice proving the store's destination is entry `ECX` plus a known subobject
offset; that was not run.

## Not claimed

- No claim that any specific name is correct. This grades evidence, not accuracy.
- No rename was applied and no Ghidra database was opened. A proposed wave of 15
  ctor/dtor-shaped functions (3 of them family-level) is recorded in
  `local-lab/GHIDRA-REGRADE-2026-07-26.md` and is explicitly **not applied**; the
  22 factory-shaped functions in the same set are excluded because the vtable
  they store is the object being constructed, not their owner.
- The suffix of every name remains ungraded, under every grade in the table.
- The abstract-base misattribution recorded on 07-25 is unchanged and still
  unbounded.
