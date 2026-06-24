# Lane 03/8 - Sync/Drift Strategy Alternatives (Read-Only)

Date: 2026-03-04
Scope: canonical docs vs `lore-book` curated mirrors, existing sync/release tooling, and prior findings in `subagents/wave_docsync_2026-03-04/wave1/*`.

## Current Baseline (Observed)

- Canonical truth is split across `reverse-engineering/**`, `roadmap/**`, `lore/**`; `lore-book/**` is both mirror + curated reader surface.
- Existing mirror tooling is partial:
  - `tools/mirror_check.py` enforces strict `.md` parity only for `reverse-engineering/** -> lore-book/reverse-engineering/**`.
  - Release snapshot generation (`tools/release_profile_snapshot.py`) mirrors selected roadmap artifacts, but this is a separate flow.
- Drift has been repeatedly observed in prior lane findings:
  - stale parity claims and historical mirror reports read as current truth (`lane02_lore_parity.md`),
  - mirrored false positives/contradictions (`lane04_parity_claims.md`, `lane10_uncertainty_queue.md`),
  - release policy contradictions and generation/gating ambiguity (`lane08_release_gate.md`).

## Alternatives Compared

## 1) Manual Agentic Sync

Operating model:
- Human/agent updates canonical and mirrored docs by judgment, then spot-checks diffs.

Strengths:
- Handles nuanced curated docs naturally.
- No new tooling burden.

Weaknesses:
- Drift detection is people-dependent and inconsistent.
- Historical docs are easy to leave “apparently current.”
- Contradictions replicate into both canonical and mirror copies.

Observed/likely failure modes:
- Stale parity snapshot remains unflagged until audit (seen in lane 02).
- Same incorrect claim appears in both trees and looks “confirmed” (seen in lane 04).
- Policy docs and scripts diverge semantically without enforced reconciliation (seen in lane 08).

## 2) Scripted One-Way Sync (Canonical -> Mirror)

Operating model:
- Canonical files are authoritative; script rewrites mirror tree deterministically.
- Gate checks fail when mirror differs from generated output.

Strengths:
- Fast, repeatable, low subjective variance.
- Reduces “forgot to mirror” failures.

Weaknesses:
- Pure one-way sync can overwrite intentional curated deltas.
- Requires explicit allowlist/transform logic for path-depth rewrites and curated pages.
- If script scope is incomplete, confidence is false (coverage hole risk).

Observed/likely failure modes:
- Curated-reader content (`Start-Here`, ordered index variants) gets clobbered.
- Allowed link-depth differences become noisy false failures unless transform-aware.
- Non-markdown/support artifacts fall out of sync if not in the generator domain.

## 3) Metadata-Tag-Based Sync Gates

Operating model:
- Each mirrored doc declares sync intent, e.g.:
  - `sync: strict-mirror` (byte/normalized-equality required),
  - `sync: mirror-with-normalization` (allowed path-depth rewrite only),
  - `sync: curated` (manual ownership, no auto-overwrite).
- Gate script validates each file according to its declared mode.

Strengths:
- Makes intentional drift explicit instead of implicit.
- Preserves curated docs while enforcing strict parity where required.
- Produces auditable policy decisions at file level.

Weaknesses:
- Requires initial tagging migration and discipline.
- Metadata itself can become stale if ownership changes.

Observed/likely failure modes:
- Missing/incorrect tags cause false pass/fail.
- Tag parser regressions can silently weaken enforcement.
- “Curated” overuse can become a loophole unless reviewed.

## Recommendation

Adopt **metadata-tag-based sync gates** as the policy layer, backed by **scripted one-way sync** for `strict-mirror` files.

Why this is the best fit for this repo:
- The repo is not purely mirrored; `lore-book` intentionally mixes mirrored and curated content.
- Prior findings show both classes of failure: accidental drift and mirrored contradictions.
- Pure manual is too fragile; pure one-way sync is too blunt.

## Operational Plan

1. Define sync modes and ownership rules
- `strict-mirror`: canonical must match mirror (normalized line endings only).
- `mirror-with-normalization`: same content except approved link-depth/path rewrite transforms.
- `curated`: mirror is intentionally editorial; must carry explicit “canonical source” pointer.

2. Expand gate coverage beyond current narrow scope
- Extend checks from `reverse-engineering/**` only to include `roadmap/**` and `lore/**` mirror pairs where applicable.
- Validate both docs and required generated companion artifacts (for example release profile snapshot set).

3. Tie gate to repo-authoritative release workflow
- Run docsync gate as part of local release/runbook flow (consistent with repo policy that local scripts are authoritative).
- Keep historical mirror-check files explicitly labeled as point-in-time snapshots.

4. Add anti-drift guardrails
- Require a dated “live parity source” pointer in audit snapshots.
- Require mirror mode declaration in mirrored index/docs before accepting changes.

## Risk Register (Post-Recommendation)

- Metadata debt risk: mitigated by failing gate on missing mode declarations for mirrored paths.
- Curated loophole risk: mitigated by review rule that `curated` files must reference canonical source and rationale.
- Script drift risk: mitigated by keeping mode logic and allowlist in one tool with deterministic output and dry-run diff report.

## Bottom Line

- **Do not stay manual-only** for sync/drift management.
- **Do not use pure one-way overwrite** across all lore-book content.
- Use a **hybrid: metadata-gated policy + scripted sync for strict mirrors**, with local release-gate enforcement.
