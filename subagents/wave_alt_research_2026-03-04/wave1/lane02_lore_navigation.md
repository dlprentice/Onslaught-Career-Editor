# Lane 02 - Lore Browser Navigation Audit (Curated Split)

Date: 2026-03-04
Scope audited: `lore-book/BOOK.md`, `lore-book/Start-Here.md`, `lore-book/roadmap/*`, `lore-book/reverse-engineering/*` index files

## Navigation pain points

1. Top-level wayfinding is overloaded and duplicated.
- `BOOK.md` is a full deep tree (68 links counted in-file), including many leaf-level appendix links, not just chapter hubs ([lore-book/BOOK.md:23](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/BOOK.md:23), [lore-book/BOOK.md:25](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/BOOK.md:25), [lore-book/BOOK.md:69](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/BOOK.md:69)).
- `Start-Here.md` is also a second route map (25 links counted), with long arrow chains that duplicate BOOK intent ([lore-book/Start-Here.md:14](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/Start-Here.md:14), [lore-book/Start-Here.md:19](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/Start-Here.md:19)).
- Result: users choose between two “start points” that both act as TOCs, reducing confidence in the canonical path.

2. “Active vs archival” scent is often only visible after click-through.
- Roadmap index presents active and archival docs in one flat table ([lore-book/roadmap/ROADMAP-INDEX.md:33](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/ROADMAP-INDEX.md:33), [lore-book/roadmap/ROADMAP-INDEX.md:47](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/ROADMAP-INDEX.md:47), [lore-book/roadmap/ROADMAP-INDEX.md:49](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/ROADMAP-INDEX.md:49)).
- Several pages are archival-heavy but only announce that at page top (for example [lore-book/roadmap/re-investigation.md:1](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/re-investigation.md:1), [lore-book/roadmap/executable-modding.md:5](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/executable-modding.md:5)).
- Result: information scent before click is weaker than needed for “current plan” vs “historical notes”.

3. Index pages mix navigation and high-density reference content.
- `RE-INDEX.md` functions as both nav and technical quick reference, which increases cognitive load for first-pass navigation ([lore-book/reverse-engineering/RE-INDEX.md:29](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/RE-INDEX.md:29), [lore-book/reverse-engineering/RE-INDEX.md:130](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/RE-INDEX.md:130)).
- `binary-analysis/functions/_index.md` is effectively a large report (798 lines measured) with migration/history logs in the same file as index navigation ([lore-book/reverse-engineering/binary-analysis/functions/_index.md:164](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/binary-analysis/functions/_index.md:164), [lore-book/reverse-engineering/binary-analysis/functions/_index.md:592](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/binary-analysis/functions/_index.md:592)).
- Result: “find where to go next” competes with “read all historical detail now”.

4. At least four broken internal links in scoped RE indexes.
- These index pages link to `../../AGENTS.md`, which is missing from the mirrored lore-book path:
  - [lore-book/reverse-engineering/save-file/_index.md:60](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/save-file/_index.md:60)
  - [lore-book/reverse-engineering/game-assets/_index.md:56](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/game-assets/_index.md:56)
  - [lore-book/reverse-engineering/game-mechanics/_index.md:58](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/game-mechanics/_index.md:58)
  - [lore-book/reverse-engineering/project-meta/_index.md:36](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/project-meta/_index.md:36)
- Result: trust hit when users encounter dead “See Also” paths in index hubs.

5. Some roadmap content is operationally correct but weakly reader-oriented inside Lore Browser.
- Example: `release-allowlist-profile.md` includes extremely long deny lists directly in the browsing flow ([lore-book/roadmap/release-allowlist-profile.md:58](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/release-allowlist-profile.md:58), [lore-book/roadmap/release-allowlist-profile.md:180](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/release-allowlist-profile.md:180)).
- Result: high scroll cost and low immediate scent for typical Lore Browser users.

## Is the intentional split helping or hurting?

### Helping
- The split does establish reader intent and narrative flow up front ([lore-book/Start-Here.md:5](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/Start-Here.md:5), [lore-book/Start-Here.md:23](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/Start-Here.md:23)).
- Domain indexes are present and generally comprehensive (`RE-INDEX`, `ROADMAP-INDEX`) ([lore-book/reverse-engineering/RE-INDEX.md:1](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/RE-INDEX.md:1), [lore-book/roadmap/ROADMAP-INDEX.md:1](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/ROADMAP-INDEX.md:1)).

### Hurting
- The split leaks too much raw/ops detail into index surfaces, so “curated” and “raw engineering” are not sharply separated in practice.
- Multiple TOCs and mixed active/archive labels reduce confidence about where to start and what is current.
- Broken links in index hubs undercut navigation reliability.

Assessment: the split is directionally correct but currently under-executed; net effect is slightly hurting navigation quality for non-expert readers.

## Alternative structures and likely impact

### Option A: Single canonical entry + strict tiering
- Keep `Start-Here.md` as the only first-hop entry.
- Trim `BOOK.md` to chapter-level hubs only (no deep appendix leaf links).
- Keep leaf links in domain indexes only.
- Impact: faster first decision, less duplicate TOC scanning, clearer “broad then deep” navigation.

### Option B: Roadmap triage lanes
- Split roadmap index into explicit groups: `Active`, `Reference`, `Archive`.
- Move clearly archival pages (`re-investigation`, historical patch notes) under an `Archive` subsection at index level.
- Impact: much stronger information scent before click; fewer wrong clicks into historical content.

### Option C: RE index decomposition
- Keep `RE-INDEX.md` as a short navigation hub.
- Move heavy quick-reference blocks and long operational/migration logs to dedicated pages linked from that hub.
- Split `binary-analysis/functions/_index.md` into:
  - concise navigation catalog
  - historical migration log
- Impact: better scanability, lower cognitive load, easier mobile/embedded-browser reading.

## Recommendation (with evidence)

Recommend a hybrid of **Option B + Option C**, while preserving the curated split concept:

1. Keep the curated split.
- It already communicates intent and narrative framing ([lore-book/Start-Here.md:3](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/Start-Here.md:3), [lore-book/Start-Here.md:5](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/Start-Here.md:5)).

2. Make “current vs archive” explicit at index level.
- Needed because archive status is currently discovered too late ([lore-book/roadmap/ROADMAP-INDEX.md:33](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/ROADMAP-INDEX.md:33), [lore-book/roadmap/re-investigation.md:1](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/roadmap/re-investigation.md:1)).

3. De-densify major index pages.
- `RE-INDEX` and especially `functions/_index` are currently dual-purpose and oversized for navigation-first use ([lore-book/reverse-engineering/RE-INDEX.md:130](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/RE-INDEX.md:130), [lore-book/reverse-engineering/binary-analysis/functions/_index.md:592](/mnt/c/users/david/source/onslaught-career-editor-private/lore-book/reverse-engineering/binary-analysis/functions/_index.md:592)).

4. Fix broken index links immediately.
- Four broken AGENTS links are low-effort, high-trust fixes (references above).

If only one change is made this week, prioritize **index-level active/archive labeling**; it yields the largest information-scent improvement without major content refactors.
