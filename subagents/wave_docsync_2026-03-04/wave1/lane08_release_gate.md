# Lane 08 - Release Allowlist Gate Audit (Read-Only)

Scope audited:
- `roadmap/release-allowlist-profile.md`
- `roadmap/release-allowlist-classification.tsv`
- `lore-book/roadmap/release-allowlist-profile.md`
- `tools/release_package.sh`

## Findings

### HIGH - R3 conditional gate is bypassed for submodule gitlink root paths
- `tools/release_package.sh:40` only classifies `references/Onslaught/*` and `references/AYAResourceExtractor/*` as `R3_CONDITIONAL`.
- In a superproject scan (`git ls-files -co`), submodules appear as gitlink entries at the root path (no trailing slash), so those paths miss the `/*` rule.
- Result in current TSV snapshot:
  - `roadmap/release-allowlist-classification.tsv:6135` -> `references/AYAResourceExtractor\tR0_ALLOW\tdefault`
  - `roadmap/release-allowlist-classification.tsv:6136` -> `references/Onslaught\tR0_ALLOW\tdefault`
- This explains why profile summaries show zero R3 despite submodule presence:
  - `roadmap/release-allowlist-profile.md:11` (`R3_CONDITIONAL | 0`)
  - `lore-book/roadmap/release-allowlist-profile.md:11` (`R3_CONDITIONAL | 0`)

Impact:
- Licensing/scope review for reference submodules is not reliably enforced by the classification model.

### MEDIUM - Profile docs are internally contradictory on references classification
- Both profile docs place references under "Hard Exclusions" while simultaneously labeling them "R3 conditional":
  - `roadmap/release-allowlist-profile.md:51`
  - `roadmap/release-allowlist-profile.md:52`
  - `lore-book/roadmap/release-allowlist-profile.md:51`
  - `lore-book/roadmap/release-allowlist-profile.md:52`
- But the dedicated conditional section says none:
  - `roadmap/release-allowlist-profile.md:56`
  - `lore-book/roadmap/release-allowlist-profile.md:56`

Impact:
- Policy interpretation is ambiguous: "hard deny" and "manual conditional" are different decisions.

### MEDIUM - R0 label semantics do not match observed classifications
- R0 is defined as "Safe source/docs/test artifacts" in both profiles:
  - `roadmap/release-allowlist-profile.md:9`
  - `lore-book/roadmap/release-allowlist-profile.md:9`
- Current TSV includes non-source binary/temp artifacts as `R0_ALLOW`:
  - `roadmap/release-allowlist-classification.tsv:5` (`.tmp_cs_tUnyKr/base.bes`)
  - `roadmap/release-allowlist-classification.tsv:6` (`.tmp_cs_tUnyKr/input.bes`)
  - `roadmap/release-allowlist-classification.tsv:7` (`.tmp_cs_tUnyKr/ovr.bes`)
  - `roadmap/release-allowlist-classification.tsv:13` (`BEA.exe.gzf`)
  - `roadmap/release-allowlist-classification.tsv:14` (`BEA_Widescreen.exe`)

Impact:
- "R0 = safe" is overstated; downstream consumers may over-trust R0 counts.

### MEDIUM - Re-run instruction implies regeneration, but script is report-only
- Profiles state re-run command:
  - `roadmap/release-allowlist-profile.md:142`
  - `roadmap/release-allowlist-profile.md:145`
  - `lore-book/roadmap/release-allowlist-profile.md:142`
  - `lore-book/roadmap/release-allowlist-profile.md:145`
- Script currently prints to stdout only and exits; it does not write/update the profile markdown or TSV artifacts:
  - `tools/release_package.sh:90` (console output start)
  - `tools/release_package.sh:131`-`tools/release_package.sh:137` (dry-run + message; no file output path logic)

Impact:
- Checked-in profile/TSV can drift from live classification without a reproducible, documented generation path.

## Denylist Behavior Validation (Observed)
- Primary `R4_DENY` prefixes are functioning in the snapshot (`game/`, `media/`, `save-attempts/`, `subagents/`):
  - Example `game/`: `roadmap/release-allowlist-classification.tsv:70`
  - Example `subagents/`: `roadmap/release-allowlist-classification.tsv:18938`
- Reason buckets in TSV are consistent with script prefixes (`game/`, `media/`, `save-attempts/`, `subagents/`) and do not currently show state-file exact hits.

## Overall Assessment
- The biggest correctness issue is submodule root misclassification (`R3` rule gap on gitlink paths).
- Documentation snapshots are mirrored correctly between roadmap and lore-book, but they mirror the same contradictions.
