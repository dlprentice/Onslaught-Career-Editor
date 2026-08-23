# Documentation standard — five fields, derived from what this repository already does, and mechanically enforced

Status: active — the header contract for tracked documentation
Date: 2026-07-28
Summary: every tracked document declares whether it is live, how old its claim
is, and what it settles; a finding additionally declares whether its evidence is
MEASURED, SOURCE, INFERRED or UNKNOWN, and names its specimen when it quotes
shipped bytes. Enforced by [`tools/doc_header_check.py`](tools/doc_header_check.py).

---

## Why this exists, and why it is a checker rather than a style guide

Two conventions in this repository have already rotted for the same reason: they
were written down and never gated. So the deliverable here is not the prose — it
is [`tools/doc_header_check.py`](tools/doc_header_check.py). This document
explains what that tool enforces and why each rule earned its place.

Nothing below was imported from outside the project. Every field is a pattern
already in practice here, measured across the 1,046 tracked `*.md` files on
2026-07-28; the prevalence of each is recorded in
[What was measured](#what-was-measured) so a reader can tell an established
convention from a one-off. The standard's job is to make the good documents'
habits universal, not to replace them.

The one thing it **adds** rather than codifies is the `Evidence:` field. That is
deliberate and it is the largest measured gap: the MEASURED-versus-INFERRED
partition that [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md) both require
is practised as an explicit all-caps marker in **28 of 564 untracked `local-lab/`
notes and in zero tracked documents** — `grep -lw MEASURED` over
`git ls-files '*.md'` returns nothing at all. The habit exists; it has simply
never survived promotion.

## The fields

Five fields, at most. Three apply to every hand-written document; two more apply
to findings. Each answers a question a reader actually has, and a field that
answers no question is not here.

| Field | Question it answers | Classes |
| --- | --- | --- |
| `Status:` | Is this live, or has it been superseded? | all |
| `Date:` / `Last updated:` | How old is this claim? | all |
| `Verdict:` / `Summary:` | What does it settle, so I can stop reading? | all |
| `Evidence:` | Is this measured, source-backed, inferred, or unknown? | FINDING |
| `Specimen:` | Which binary were these bytes read from? | FINDING, when it quotes a retail address |

They live in the **header block**: everything from the top of the file down to
the first `##` heading, within the first 60 lines. That is where a checker can
find them and where a reader already looks. Any of these decorations is
accepted, because all four are already in use:

```markdown
Status: active
> Status: active
- Status: active
> **Status:** active
```

A field's value may wrap onto following lines; it ends at the first blank line.
That is not a concession — the two strongest patterns here, the verdict
blockquote and the specimen declaration, both wrap in practice, and the SHA-256
routinely lands on the continuation line.

### `Status:` — is this live?

Free text, non-empty, not a placeholder. Deliberately **not** a closed
vocabulary: the 63 documents already carrying a `Status:` use it to say things a
fixed token cannot, and the sharpest of them is
`reverse-engineering/game-mechanics/shield-retail-to-core-translation-policy.md`:

> Status: **source-backed ownership accepted; rate remains blocked**

A closed vocabulary would have flattened that to `active` and destroyed the only
useful thing the line says. Lifecycle grading is carried instead by the
supersede marker in the body, where it belongs.

### `Date:` / `Last updated:` — how old is this claim?

One ISO `YYYY-MM-DD` date, which must be a real calendar date. Two spellings,
because they mean different things and both are already in use:

- **`Date:`** on a dated write-up — the date the measurement was taken. The
  document is a record of a moment and does not change.
- **`Last updated:`** on a living document — an index, a reference table, a
  governance file. It is revised in place.

Before this standard there was no single field a checker could read to tell how
old a claim was: 19 tracked documents used `Date:`, 39 used a `Last updated`
trailer, and most encoded the date only in the filename — which a reader sees
and a tool cannot rely on.

### `Verdict:` / `Summary:` — what does it settle?

One line (it may wrap), non-empty, not a placeholder. Again two spellings for
two different jobs:

- **`Verdict:`** when the document makes a claim about the game. Put it first,
  in a blockquote, and make the **title a claim rather than a topic**. This is
  the strongest pattern in the repository and the one that lets a reader stop
  after ten lines. `binary-analysis/terrain-third-light-2026-07-26.md`:

  > Verdict: **two independent falsifications, both precise negatives.**

  A negative verdict is a first-class verdict. `cockpit-lighting-law-2026-07-26.md`
  states its own uselessness up front — "No renderer change is warranted by this
  note" — and names the premises it falsified in the same block. That is a good
  document.

- **`Summary:`** when the document makes no claim — an index, a guide, a
  reference table. `quick-reference/cli-parameters.md` already does this.

The best practice of this pattern lives in `local-lab/` as a **"What this
settles"** block, and it is worth quoting into the standard because the corpus
has no sharper line of doctrine:

> **Status of the numbers here:** every retail-side value was read by this pass
> from `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` … Nothing below
> rests on a prior note alone. Where a prior note agreed, that is corroboration,
> not the evidence.
>
> — `local-lab/DEFAULTS-RULE-SWEEP-2026-07-27.md`

Say what your verdict rests on, and say explicitly when a prior note is
corroboration rather than evidence.

### `Evidence:` — measured, source-backed, inferred, or unknown?

**FINDING class only.** The value must begin with one of four grades, followed
by what the evidence actually is:

| Grade | Means | Example |
| --- | --- | --- |
| `MEASURED` | Read from the shipped artefact — a controlled runtime capture, a byte comparison, a table read out of shipped data, or a test that asserts a recovered law. | `Evidence: MEASURED — three arms at 0x004DD6B0 write 10.0/30.0/70.0; the image's own initialisers are uniquely the middle arm.` |
| `SOURCE` | Backed by the pinned GPL source, **with file and line**. Establishes shape, ownership and intent; does not by itself establish that the Steam build agrees. | `Evidence: SOURCE — references/Onslaught/Camera.cpp:214; no retail capture.` |
| `INFERRED` | Reasoned from something else. Provisional reconstruction design lives here. | `Evidence: INFERRED — from the shipped script's 0.5 s dispatch; the endpoint was not sampled.` |
| `UNKNOWN` | Not settled, **and here is what would settle it.** | `Evidence: UNKNOWN — a CDB stop at 0x0040C990 would settle it.` |

The four grades are not invented: they are
[`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md)'s own authority order, with its
top two rungs (controlled runtime observation, retail binary/static evidence)
collapsing into `MEASURED` because both read the shipped artefact.

Two rules the checker enforces, both of which exist because of specific failures
here:

- **A bare grade is rejected.** `Evidence: MEASURED` with nothing after it is a
  label, not evidence. Name the capture, the byte comparison, the test, or the
  source file and line. Per [`AGENTS.md`](AGENTS.md): "a measured number and its
  method are" the deliverable.
- **`UNKNOWN` is a passing value.** An honest unknown with a route to settling it
  is a good outcome; a plausible guess dressed as a fact is the failure mode that
  got a previous generation of documentation deleted wholesale. This mirrors the
  `UNSCORED` return in `tools/score_frontend_capture.py`, and the reasoning is
  identical: "I found no gap" and "I was unable to look" must not render as the
  same sentence.

When a document mixes grades, grade it by its **weakest load-bearing claim** and
partition the body — the structural form
`## Measured retail input` / `## Source-backed ownership`, already used by
`game-mechanics/shield-retail-to-core-translation-policy.md`, is the model.

### `Specimen:` — which binary?

**Required on a FINDING that quotes a retail virtual address** in
`0x00400000`–`0x006FFFFF`. Must name a file and carry a hash prefix of at least
eight hex characters.

**This is the highest-priority rule in this document and it is not a formatting
rule.** There are two retail binaries on this machine and they are not
interchangeable: the installed Steam `BEA.exe` is deliberately patched, and the
pristine original sits beside it as `BEA.exe.original.backup`. A byte finding
that does not name which one it read may simply be **false** — category 1, not
category 4. At least one parity target has already been set from the wrong
binary; see
[`binary-analysis/retail-capture-provenance-2026-07-25.md`](reverse-engineering/binary-analysis/retail-capture-provenance-2026-07-25.md).

The checker additionally **rejects a `Specimen:` that cites a path under
`steamapps`** unless that same path is the `.original.backup` or a `safe-copy`.
The exemption is judged per path, not per field, so naming the pristine backup
elsewhere in the line does not license citing the live install.

Follow the shape already in use, and keep the negative assurances — they are as
load-bearing as the hash:

```markdown
Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfa…`, 2,506,752 bytes
(`local-lab/safe-copy-bea-pristine/`, read-only). Disassembly is `capstone`
linear decode through `tools/disasm_va.py`. The Ghidra database was not opened
or mutated. `BEA.exe` was not launched.
```

## Document classes

Class is resolved from the path, so nothing has to declare its own type.

| Class | What it is | Detected by | Required fields |
| --- | --- | --- | --- |
| `FINDING` | A dated write-up that claims something about the game | default for in-scope prose | Status, Date, Verdict, Evidence, + Specimen when it quotes a retail address |
| `INDEX` | A front door or reference that makes no claim of its own | `_index.md`, `README.md`, `*INDEX*.md` | Status, Date, Summary |
| `GOVERNANCE` | States what is wanted or required, not what is true | explicit list in the checker | Status, Date, Summary |
| `FUNCTION-NOTE` | Per-function RE note | `binary-analysis/functions/*.md` | `Source File:` trailer naming its `Binary:`, `Last updated:` |
| `WAVE-SHARD` | Fullpass wave review shard | `ghidra-fullpass-findings/W*/{primary,adversarial}/*.md` | `Phase:`, `Function count:`, `Reviewed at:` (ISO 8601) |

Three of those class rules are narrower than they could be, each for a measured
reason. They are stated here rather than buried, because a silently narrowed
gate is how a check stops covering the thing it was built for.

- **`GOVERNANCE` carries no `Evidence:` and no `Verdict:`.** These documents say
  what is wanted or required. [`GOAL.md`](GOAL.md) is explicitly not superseded
  by measurement; grading it as evidence would be a category error.
- **`FUNCTION-NOTE` is exempt from the `Specimen:` rule.** 321 of 322 quote a
  retail address, so the rule would fire on all but one while adding no truth:
  they index a Ghidra database rather than establish a byte finding, their own
  trailer already names the binary, and their category-1 risk — asserting a name
  the database no longer carries — is already gated by
  [`tools/re_function_doc_names_check.py`](tools/re_function_doc_names_check.py)
  against a dated name table. A gate that punishes correct documents gets
  switched off.
- **`WAVE-SHARD` gates `Export root:` and `Primary:` only on shards reviewed on
  or after 2026-07-28.** Measured: 107 of 514 shards carry no `Export root:`, and
  181 of 257 adversarial shards carry no `Primary:` — the exemplar `W001/B01.md`
  is the exception, not the rule. Those come from the 2026-07-23 expedition,
  which closed on 2026-07-25 and will not be re-reviewed. Gating them would
  freeze a 288-entry backlog that can never shrink, and a backlog that cannot
  move stops being read. The shard's own `Reviewed at:` stamp is the ratchet
  instead, so the next wave is gated without a single backlog line.

## Two body patterns that are required but not gated

Both are stated here because they matter more than any header field. Neither is
mechanically checkable without producing false failures, and a check that
punishes a correct document is worse than no check — so they are reviewed by
humans, not by the tool. That limit is admitted rather than papered over.

**Supersede in place.** Never silently overwrite a claim. A reader who checks the
old value and finds it simply gone cannot tell whether it was corrected or lost.
Quote the old text, date the correction, say what changed — **and say what is
unchanged.** [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) is the model:

> **Superseded 2026-07-27 — over-claim withdrawn.** This previously read
> "Enhanced Copy now writes and reads back **the retail minimum `0.1`**" … The
> demonstrated capability is unchanged: AppCore writes the value into a safe copy
> and reads it back. Only the attribution of `0.1` to retail was wrong.

**Scope an amendment.** A correction that does not say what it leaves standing
voids a whole document by implication. `name-grading-ledger-2026-07-27-demotion2.md`
amends its predecessor "**in its counts only**", which is what stops the older
ledger from being read as retracted.

## Scope

Applies to **tracked** files only; the file list comes from `git ls-files`.
The live checker classifies the tracked corpus and defers the explicit
pre-standard backlog. Run it for exact counts; this file deliberately does not
copy them.

**`local-lab/` is out of scope, deliberately.** It is gitignored, so it is
structurally invisible to the checker, and it is additionally excluded by path so
the rule is legible rather than accidental. Working notes there stay loose on
purpose: they are where a claim is allowed to be wrong before it is tested.
Promotion out of `local-lab/` into tracked evidence is exactly where this
standard starts applying — conforming to the header is part of what promotion
means.

Also excluded, each for a stated reason in the checker: `.github/` (templates,
not documents), `lore/` and `lore-book/` (narrative/archive material governed by
their own source notes rather than the RE-finding header schema), `references/`
(pinned third-party submodule), generated notices, and build output.

## The checker

```powershell
py -3 tools\doc_header_check.py              # gate
py -3 tools\doc_header_check.py --self-test  # self-tests, no repository needed
py -3 tools\doc_header_check.py --show-backlog
npm run test:doc-headers                     # both of the above, wired
npm run test:docs                            # links, headers, names, authority drift
```

`tools/doc_current_authority_check.py` is the living-authority ratchet. It
rejects root/RE synthesis documents that copy a numbered "current generation",
next-valid generation, rolling `db.N`, current/rolling Ghidra population or
body-accounting counts, or stale live/readback selectors instead of pointing to
`developer_state.json` → `current_re_authority` and
`reverse-engineering/ghidra/README.md`. Dated findings keep their exact historical
numbers; living front doors must not turn those snapshots back into live claims.

Reachability is a separate diagnostic:
`py -3 tools\md_reachability_check.py`. It is not part of `npm run test:docs`.

| Exit | Meaning |
| --- | --- |
| `0` | every enforced document conforms |
| `1` | an enforced document violates the standard, or the backlog has gone stale |
| `2` | **the check could not run** — no git, no backlog file, bad arguments |

Exit 2 abstains rather than passing. Per [`AGENTS.md`](AGENTS.md): "A critic that
cannot return UNSCORED is not a gate."

### The ratchet

[`tools/doc_header_backlog.txt`](tools/doc_header_backlog.txt) lists the
documents that predate this standard. They are reported and do not fail.
Everything else is enforced, so **a newly added document is gated from the moment
it exists** — which is the only property that matters for stopping the corpus
getting worse.

The list can only shrink. The checker fails if an entry is stale (the path no
longer exists) **or if an entry now conforms**, which forces the line to be
deleted rather than left as a permanent exemption. Never add a line to silence a
new failure; `--write-backlog` exists for the one-time generation and is not a
routine command.

## What was measured

Measured 2026-07-28 across 1,046 tracked `*.md` files. This is the evidence the
standard was derived from, not an assertion about what people ought to do.

**Pattern prevalence before the standard**, counting only header-block
occurrences in the 190 hand-written documents:

| Pattern | Documents |
| --- | --- |
| `Status:` — the most widespread | 63 |
| `Last updated` trailer | 25 |
| `Date:` | 19 |
| `Source:` | 13 |
| `Verdict:` blockquote — the strongest | 12 |
| `Summary:` | 12 |
| `Specimen:` declaration | 10 |
| `MEASURED` / `INFERRED` marker | **0** — 28 of 564 `local-lab/` notes use `MEASURED`, 30 use either |
| No header field at all | 99 |

Two of the brief's exemplars turned out to be **atypical rather than
conventional**, which is why the class rules above are narrower than they first
looked: the per-function provenance trailer is present in **17 of 323** notes,
not the class norm, and the five-field wave-shard trailer is complete in **76 of
257** adversarial shards.

**Conformance to this standard on the day it was written:**

| Class | In scope | Conforming | Backlog |
| --- | --- | --- | --- |
| `WAVE-SHARD` | 514 | 514 | 0 |
| `FUNCTION-NOTE` | 322 | 2 | 320 |
| `FINDING` | 150 | 0 | 150 |
| `INDEX` | 31 | 1 | 30 |
| `GOVERNANCE` | 12 | 1 | 11 |

That is an honest number, not a target that was gamed: **511 documents start in
the backlog.** Almost nothing was retrofitted in this pass, because retrofitting
511 documents is a separate judgement that belongs in the main loop and not in
the pass that writes the gate. The two exceptions are this file and
[`tools/README.md`](tools/README.md), which were brought up to standard to
exercise the ratchet in both directions — the gate rejected the backlog until
`tools/README.md`'s line was deleted from it.

**The 54 documents worth fixing first** are the FINDING-class documents that
quote a retail address and declare no `Specimen:`. Those are the only entries in
the backlog whose defect is category 1 — a claim that may be false — rather than
category 4. List them with:

```powershell
py -3 tools\doc_header_check.py --show-backlog
```

The next-cheapest batch is the 11 `GOVERNANCE` files: three lines each, and they
are the documents most readers meet first.

## Known limits

- The checker validates **presence and shape, never truth.** It cannot tell that
  a `Verdict:` is wrong, that an `Evidence: MEASURED` grade is a fit to an
  artefact, or that a `Status: active` document was superseded yesterday. Ranked
  against the maintainer's order — WRONG, then STALE, then BROKEN, then SHAPE —
  this tool addresses category 4 and exactly one slice of category 1 (the
  specimen rule). It is not a substitute for reading.
- The `Specimen:` rule fires on FINDING documents only. An `INDEX` or
  `GOVERNANCE` document that quotes addresses is not gated, on the reasoning that
  those cite findings which carry their own specimen. If that assumption ever
  stops holding, this is where it breaks.
- The backlog's date ratchet for wave shards trusts the shard's own
  `Reviewed at:` stamp. A future wave that back-dates its stamp would escape the
  gate.
- Nothing here checks reachability. A conforming document that no index links to
  is still invisible; that is `tools/md_reachability_check.py`'s job, and the two
  failure modes are different.

## See also

- [`VALIDATION.md`](VALIDATION.md) — choosing the smallest gate for a change.
- [`AGENTS.md`](AGENTS.md) — the contributor guide, and the evidence rules this
  standard mechanises.
- [`GOAL.md`](GOAL.md) — the evidence partition the `Evidence:` grades follow.
- [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) — the authority order the four
  grades were taken from.
- [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) — the RE
  evidence front door, and the specimen rule in its original form.
