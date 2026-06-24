# Lane 04 - Release/Publication Implications (Canonical vs Curated Divergence)

Date: 2026-03-04
Mode: Read-only assessment (no state-file edits)

## Scope Reviewed
- `tools/release_package.sh`
- `roadmap/release-allowlist-profile.md`
- `roadmap/release-allowlist-classification.tsv`
- Lore-book equivalents:
  - `lore-book/roadmap/release-allowlist-profile.md`
  - `lore-book/roadmap/release-allowlist-classification.tsv`
  - `lore-book/roadmap/ROADMAP-INDEX.md`

## Selected Alternative (interpreted)
Intentionally allow canonical docs and curated docs to diverge in structure/presentation, with canonical content still declared authoritative.

Evidence of intentional divergence pattern:
- Curated index explicitly states canonical source-of-truth while using curated ordering: `lore-book/roadmap/ROADMAP-INDEX.md:29`.
- Canonical and curated roadmap indexes already differ in document ordering and cross-reference emphasis (`roadmap/ROADMAP-INDEX.md:29-47` vs `lore-book/roadmap/ROADMAP-INDEX.md:29-49`).

## Key Findings
1. `release_package.sh` is path-classification based and does not validate canonical-vs-curated content parity.
- Classification logic is only prefix/extension checks: `tools/release_package.sh:24-50`.
- No parity or authority checks between duplicate doc surfaces: `tools/release_package.sh:53-138`.

2. Current curated release profile includes both doc surfaces in the publish-candidate set.
- `lore/**`, `lore-book/**`, and `roadmap/**` are all included: `roadmap/release-allowlist-profile.md:35-37`.
- Result: if canonical and curated content diverge semantically, both are publishable simultaneously unless manually filtered.

3. Release gate artifacts are duplicated and both classified as `R0_ALLOW`.
- `lore-book/roadmap/release-allowlist-{profile,classification}` and `roadmap/release-allowlist-{profile,classification}` are all `R0_ALLOW`: `roadmap/release-allowlist-classification.tsv:6068-6069,18916-18917`.
- If the two copies drift, release readers can consume conflicting gate artifacts with no automatic failure.

4. Existing control that helps: snapshot generator writes both canonical and lore-book gate artifacts in one run.
- Dual-write behavior is explicit: `tools/release_profile_snapshot.py:4-8,199-214`.
- In current repo state, both pairs are byte-identical (`cmp` exit code 0; matching SHA256 hashes for both profile and TSV pairs).

5. Broad doc globs plus default `R0_ALLOW` can publish non-curated operational artifacts.
- Example lore-book binary-analysis JSON/JSONL artifacts classified `R0_ALLOW`: `roadmap/release-allowlist-classification.tsv:5600,5603,5604`.
- This is a publication-quality/scope risk amplified by including both canonical and curated trees.

## Risk Verdict
Yes, this alternative increases release/publication risk unless additional controls are enforced.

Risk level: **Moderate** (from a release-governance perspective).

Why:
- Intentional divergence itself is manageable for reader UX, but release tooling currently lacks machine checks to prevent contradictory canonical/curated content from being published together.
- Gate artifacts are duplicated and equally allowed, but release classification does not enforce equivalence or authority precedence.

## Mitigations (priority order)
1. Add parity gate checks to release validation.
- In `release_package.sh --dry-run`, fail when canonical vs lore-book gate artifact pairs differ:
  - `roadmap/release-allowlist-profile.md` vs `lore-book/roadmap/release-allowlist-profile.md`
  - `roadmap/release-allowlist-classification.tsv` vs `lore-book/roadmap/release-allowlist-classification.tsv`

2. Make release authority explicit in policy, not just prose.
- Treat `roadmap/release-allowlist-*` as authoritative release gate artifacts.
- Treat lore-book copies as generated mirrors only.

3. Narrow public packaging globs for docs.
- Replace broad `lore-book/**` (and potentially `roadmap/**`) with explicit allowlists for curated publication pages.
- Explicitly exclude `lore-book/reverse-engineering/binary-analysis/**/*.json*` and similar operational logs unless intentionally publishing them.

4. Enforce pre-release snapshot refresh step.
- Require `python3 tools/release_profile_snapshot.py` before packaging, then parity check, then publish.

5. Keep divergence constrained to presentation-layer differences.
- Permit ordering/reader-flow divergence (as currently documented), but require factual/policy parity for release gate docs and policy-linked guidance.

## Bottom Line
Intentional canonical-vs-curated divergence is viable, but with current release tooling it raises governance risk because both surfaces are broadly publishable and no automated parity guard exists in `release_package.sh`. Add parity checks + tighter doc allowlists to keep the risk low.
