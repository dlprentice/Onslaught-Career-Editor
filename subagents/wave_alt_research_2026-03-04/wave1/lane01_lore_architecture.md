# Lane 01 - Lore/Canonical Documentation Architecture Review

Date: 2026-03-04
Scope reviewed: `AGENTS.md`, `lore-book/BOOK.md`, roadmap parity docs (`roadmap/csharp-python-parity.md`) plus roadmap index context (`roadmap/ROADMAP-INDEX.md`).

## Current-State Summary

The repository already encodes an intentional split architecture:

- Canonical documentation roots are explicitly defined under `reverse-engineering/`, `lore/`, and `roadmap/`.
- Lore Browser content is intentionally driven by `lore-book/BOOK.md` as a curated table of contents.
- Both GUI stacks (C# and Python) are documented as using the `lore-book/` curated tree for Lore Browser loading.
- The RE lane also carries an explicit mirror rule between canonical `reverse-engineering/**` and `lore-book/reverse-engineering/**`, with intentional link-depth differences.

Interpretation: current architecture is not accidental duplication; it is an explicit two-layer model (canonical truth + curated consumption surface) with selected mirrored content for browser/runtime convenience.

## Option A/B/C Tradeoff Comparison

| Option | Description | Benefits | Drawbacks | Fit With Current Repo/Apps |
|---|---|---|---|---|
| A | Keep intentional split: canonical docs remain authoritative; curated Lore Browser docs remain separate in `lore-book/`; keep mirroring only where currently required. | Preserves current app behavior; aligns with documented conventions; keeps user-facing narrative flow independent from technical canonical structure. | Ongoing sync burden where mirrored files exist; drift risk if updates land in only one side. | Strong fit. Matches current conventions and parity expectations. |
| B | Collapse to single canonical tree only; Lore Browser reads canonical docs directly. | Eliminates duplicate/mirror maintenance; strongest single-source-of-truth model. | Conflicts with explicit current Lore Browser design (`lore-book`-backed); requires app and content-structure migration; loses curated reading-order layer unless rebuilt another way. | Weak fit right now. Higher migration cost and behavior churn. |
| C | Fully separate and independently authored canonical vs curated file sets (no mirroring expectation). | Maximum editorial freedom for curated docs; tailored voice/structure for browser readers. | Highest divergence risk, duplicated maintenance, and conflicting truths over time; weakens canonical authority in practice. | Medium/weak fit. Feasible, but highest long-term consistency risk. |

## Risks (Current Split)

1. Mirror drift risk: explicit mirroring requirement can conflict with the “avoid divergent duplicate content” rule if updates are not synchronized quickly.
2. Link maintenance risk: intentional relative-depth differences between canonical and lore-book mirrors increase editing mistakes and link regressions.
3. Operational overhead risk: each canonical RE change may require mirrored updates, increasing doc maintenance time.
4. Parity communication drift risk: parity docs can become stale versus real UI behavior if not updated in the same change window.

## Recommended Best Option + Confidence

Recommended option: **Option A** (retain the intentional split with canonical authority + curated lore-browser surface).

Why this remains best:

- It is explicitly documented as the current architecture across conventions and parity tracking.
- It aligns with both app implementations already expecting `lore-book`-backed content.
- It preserves a curated reading experience without forcing immediate UI/documentation migration.

Suggested constraint to reduce risk while keeping Option A: treat canonical docs as source-of-truth and enforce mirror freshness checks (manual checklist or lightweight CI/script) when touching mirrored areas.

Confidence: **0.84 (high)**.

## Evidence (File:Line)

- `AGENTS.md:360` - Defines top-level canonical indexes (`RE-INDEX`, `LORE-INDEX`, `ROADMAP-INDEX`).
- `AGENTS.md:361` - `_index.md` is canonical within subfolders; warns against divergent duplicate content.
- `AGENTS.md:362` - Lore Browser uses `lore-book/BOOK.md` curated TOC.
- `AGENTS.md:310` - Directory structure labels `lore-book/` as curated lore book for Lore Browser.
- `AGENTS.md:676` - Requires mirroring `reverse-engineering/**` with `lore-book/reverse-engineering/**`.
- `AGENTS.md:678` - Notes intentional relative-link-depth differences between canonical and lore-book mirrors.
- `lore-book/BOOK.md:3` - Declares curated reading order for Lore Browser.
- `lore-book/BOOK.md:25` - Curated appendix points into lore-book-side reverse-engineering index pathing.
- `lore-book/BOOK.md:69` - Includes roadmap section in curated TOC.
- `lore-book/BOOK.md:70` - Curated roadmap points to `roadmap/ROADMAP-INDEX.md` path under lore-book tree.
- `roadmap/csharp-python-parity.md:14` - Lore Browser parity entry cites lore-book-backed content source.
- `roadmap/csharp-python-parity.md:81` - Both Python and C# documented as using `lore-book/` curated tree.
- `roadmap/ROADMAP-INDEX.md:51` - Roadmap canonical cross-reference points to canonical `reverse-engineering/RE-INDEX.md`.
- `roadmap/ROADMAP-INDEX.md:52` - Roadmap canonical cross-reference points to canonical `lore/_index.md`.
