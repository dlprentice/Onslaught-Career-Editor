# Lane 9/10 Scratch Artifact Relevance Audit (2026-03-01)

## Scope
- Target: `reverse-engineering/binary-analysis/scratch`
- Method: top-level folder inventory + targeted path-reference scan across:
  - `developer_agent_state.json`
  - `documentation_agent_state.json`
  - `re_orchestrator_state.json`
  - `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
  - coverage index docs

## Snapshot
- Top-level folders: **69**
- Total files under scratch: **13,416**
- Total size: **230.1 MB**
- Classification output: `phase2_lane9_relevance_classification.tsv`

## Classification Summary
- `keep_now`: **11 folders** (~169.5 MB)
- `archive_after_rewrite`: **29 folders** (~46.8 MB)
- `archive_now`: **26 folders** (~12.0 MB)
- `keep_infra`: **3 folders** (`archive`, `_retired`, `program_2026-03-01`)

## Keep Now (high break risk)
- `deep_semantic_tail_2026-02-26` (refs=141, state=23, backlog=118)
- `deep_semantic_tail_2026-02-27` (refs=135, state=61, backlog=74)
- `cdxtexture_owner_correction_2026-02-25` (refs=17)
- `cfastvb_owner_correction_2026-02-25` (refs=15)
- `ctexture_owner_correction_2026-02-25` (refs=14)
- `cunit_owner_correction_2026-02-25` (refs=11)
- `wave217_signature_pass1..4`, `wave217_comment_pass1` (each refs=4, but state/backlog anchored)

Rationale: These are still heavily embedded in active state/backlog/history narratives. Moving now would create immediate broken anchors and harder resume paths.

## Archive Now Candidates (low break risk)
No targeted external path references found; safe to move under a dated archive subtree immediately.

Largest `archive_now` candidates by size:
- `options_entries_callers_deeppass_2026-02-25` (1.9 MB)
- `owner_scout_2026-02-26` (1.4 MB)
- `headless-2026-02-25` (1.2 MB)
- `headless_live_verify_2026-02-25_controllerdef` (1.0 MB)
- `cexplosion_owner_correction_2026-02-25` (0.8 MB)
- `coverage_refresh_2026-02-25_*` (3 dirs, ~2.3 MB total)
- `wave217_signature_pass2_prep`, `wave217_signature_pass3_prep`
- `cconsole-*`, `cfrontend-*`, `cgame-*`, `cegine-*` exploratory decompile snapshots

## Archive After Rewrite (medium/high break risk)
These have active path anchors in state/backlog docs and should be moved only after link rewrites:
- `cunitai_owner_correction_2026-02-25`
- `cengine_owner_correction_2026-02-25`
- `cdxtexture_owner_correction_2026-02-26`
- `ctexture_owner_correction_2026-02-26`
- `cfastvb_owner_correction_2026-02-26`
- `owner_mixed_strict_correction_2026-02-26`
- `cgeneralvolume_owner_correction_2026-02-26`
- remaining 2026-02-26 owner-correction waves with refs>=1

Rationale: their evidence artifacts are already summarized in docs, but exact folder paths are still linked by resume/backlog text.

## Existing Broken-Reference Risk Found
One stale path is already present (artifact already archived, references not updated):
- stale: `reverse-engineering/binary-analysis/scratch/cgame-semantic-rename-map-2026-02-25.txt`
- current location: `reverse-engineering/binary-analysis/scratch/archive/2026-03-01-doc-hygiene/root-orphans/cgame-semantic-rename-map-2026-02-25.txt`
- stale references found in:
  - `documentation_agent_state.json`
  - `re_orchestrator_state.json`

## Recommended Execution Order
1. Move `archive_now` folders first (low risk, immediate hygiene gain).
2. Rewrite stale and medium-risk path anchors in state/backlog files.
3. Move `archive_after_rewrite` folders.
4. Keep `keep_now` set in place until lane 10 doc cleanup fully stabilizes references.
