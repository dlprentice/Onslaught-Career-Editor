# Lane 02 Lore Parity Audit (Read-only)

Date: 2026-03-04
Scope: `lore-book/roadmap/**` vs `roadmap/**`, and `lore-book/reverse-engineering/**` vs `reverse-engineering/**`, focused on key index/status docs.

## Method

- Compared mirrored `index/readme/status/parity/audit` docs for missing files and content drift.
- Ignored harmless ordering-only table changes unless they changed meaning or parity claims.
- Captured `file:line` evidence for contradictions, stale parity statements, and missing mirrors.

## Snapshot

- Key-doc mirror counts:
  - `roadmap`: `0` missing in lore-book, `0` extra in lore-book, `1` content diff.
  - `reverse-engineering`: `0` missing in lore-book, `0` extra in lore-book, `5` content diffs.
- Full roadmap tree has one non-key mirror gap: `roadmap/release-allowlist-classification.tsv` exists only in canonical tree.

## Findings

### 1) MEDIUM - Parity status statement is outdated vs current key-doc reality

Evidence:
- [reverse-engineering/binary-analysis/documentation-audit.md](redacted-private-source/reverse-engineering/binary-analysis/documentation-audit.md:18) states mirror parity was `0` missing / `0` extra / `0` content diffs.
- [reverse-engineering/binary-analysis/documentation-audit.md](redacted-private-source/reverse-engineering/binary-analysis/documentation-audit.md:27) states link normalization was done so canonical+lore-book copies match.
- Current key-doc content diffs now exist in at least:
  - [roadmap/ROADMAP-INDEX.md](redacted-private-source/roadmap/ROADMAP-INDEX.md:29) vs [lore-book/roadmap/ROADMAP-INDEX.md](redacted-private-source/lore-book/roadmap/ROADMAP-INDEX.md:29)
  - [reverse-engineering/binary-analysis/README.md](redacted-private-source/reverse-engineering/binary-analysis/README.md:94) vs [lore-book/reverse-engineering/binary-analysis/README.md](redacted-private-source/lore-book/reverse-engineering/binary-analysis/README.md:94)
  - [reverse-engineering/game-assets/_index.md](redacted-private-source/reverse-engineering/game-assets/_index.md:56) vs [lore-book/reverse-engineering/game-assets/_index.md](redacted-private-source/lore-book/reverse-engineering/game-assets/_index.md:56)
  - [reverse-engineering/game-mechanics/_index.md](redacted-private-source/reverse-engineering/game-mechanics/_index.md:58) vs [lore-book/reverse-engineering/game-mechanics/_index.md](redacted-private-source/lore-book/reverse-engineering/game-mechanics/_index.md:58)
  - [reverse-engineering/project-meta/_index.md](redacted-private-source/reverse-engineering/project-meta/_index.md:36) vs [lore-book/reverse-engineering/project-meta/_index.md](redacted-private-source/lore-book/reverse-engineering/project-meta/_index.md:36)
  - [reverse-engineering/save-file/_index.md](redacted-private-source/reverse-engineering/save-file/_index.md:60) vs [lore-book/reverse-engineering/save-file/_index.md](redacted-private-source/lore-book/reverse-engineering/save-file/_index.md:60)

Why this matters:
- Readers can misread the audit section as currently true parity instead of historical.

Recommended fix:
- Add a one-line “superseded by latest parity scan” banner near `documentation-audit.md:13-18`.
- Regenerate and link a fresh dated mirror-check status artifact.

### 2) MEDIUM - Mirror-check status doc wording is stale

Evidence:
- [reverse-engineering/binary-analysis/mirror-check-2026-02-12.md](redacted-private-source/reverse-engineering/binary-analysis/mirror-check-2026-02-12.md:9) says “No mirror issues detected.”
- [lore-book/reverse-engineering/binary-analysis/mirror-check-2026-02-12.md](redacted-private-source/lore-book/reverse-engineering/binary-analysis/mirror-check-2026-02-12.md:9) says the same.
- Current key-doc parity now has content diffs (see Finding 1).

Why this matters:
- Status wording reads definitive without an explicit “historical only” warning in that file.

Recommended fix:
- Keep this file as historical, but prepend a dated deprecation note and point to a newer mirror check.

### 3) LOW - Missing mirror artifact under `roadmap/**`

Evidence:
- Canonical file exists: `roadmap/release-allowlist-classification.tsv`.
- Mirror counterpart is absent: `lore-book/roadmap/release-allowlist-classification.tsv`.
- Both roadmap profile docs still reference that canonical artifact at [roadmap/release-allowlist-profile.md](redacted-private-source/roadmap/release-allowlist-profile.md:140) and [lore-book/roadmap/release-allowlist-profile.md](redacted-private-source/lore-book/roadmap/release-allowlist-profile.md:140).

Why this matters:
- Lore-book roadmap section is not self-contained for release-profile supporting data.

Recommended fix:
- Either mirror the TSV into `lore-book/roadmap/` or explicitly document that lore-book intentionally references canonical `roadmap/` artifacts.

## Non-issues (intentional drift)

- AGENTS link depth differences in lore-book mirrors (for example `../../AGENTS.md` vs `../../../AGENTS.md`) appear intentional path adjustments, not contradictions.
- ROADMAP table row order differences are mostly presentation-level and not treated as defects by themselves.
