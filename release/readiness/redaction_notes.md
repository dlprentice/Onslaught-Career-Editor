# Redaction Notes

Status: portable app ZIP / legacy curated export redaction notes. This is not
the public-source tracking policy.

These notes describe material excluded from portable app ZIPs and legacy
curated export payloads. The public source repo is now the primary working
repo and may track useful non-secret source, docs, tools, RE notes, wave notes,
state batons, agent reports, readiness notes, and compact proof summaries.

## Portable ZIP / Legacy Curated Export Hard Exclusions (R4_DENY)
- `game/**`
- `media/**`
- `.codex/**`
- `archive/**`
- `save-attempts/**`
- `subagents/**`
- `release/artifacts/**`
- `release/out/**`
- `reverse-engineering/binary-analysis/scratch/**`
- `lore-book/reverse-engineering/binary-analysis/scratch/**`
- `discord_channel_dumps/**`
- `wave_online_audit/**`
- `wave_online_audit2/**`
- `OnslaughtCareerEditor.UiTests/TestResults/**`
- `**/*.trx`
- `.tmp_cs_*/**`
- `**/__pycache__/**`
- `**/*.exe`
- `**/*.dll`
- `**/*.bes`
- `**/*.bea`
- `**/*.gzf`
- `reverse-engineering/game-assets/mission-text-map.tsv`
- `lore-book/reverse-engineering/game-assets/mission-text-map.tsv`
- `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
- `lore-book/reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
- `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md`
- `lore-book/reverse-engineering/binary-analysis/ghydra-mcp-runbook.md`
- `reverse-engineering/binary-analysis/documentation-audit.md`
- `lore-book/reverse-engineering/binary-analysis/documentation-audit.md`
- `reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md`
- `lore-book/reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md`
- `reverse-engineering/binary-analysis/*.json`
- `reverse-engineering/binary-analysis/*.jsonl`
- `lore-book/reverse-engineering/binary-analysis/*.json`
- `lore-book/reverse-engineering/binary-analysis/*.jsonl`
- `reverse-engineering/source-code/*-file-manifest-2026-02-11.tsv`
- `lore-book/reverse-engineering/source-code/*-file-manifest-2026-02-11.tsv`
- `tools/run_ghidra_batch_rename_headless.sh`
- `tools/run_ghidra_headless_postscript.sh`
- `tools/semantic_audit_online.py`
- `AGENTS.md`
- `onslaught_codex_directive.md`
- `MCP_DEBUGGING_OPTIONS.md`
- `MCP_LIMITATIONS.md`
- `developer_agent_state.json`
- `documentation_agent_state.json`
- `re_orchestrator_state.json`
- `archive/historical-docs/USER_SANITY_CHECK.md`
- `setuphistory.txt`
- local proof/backup-root payloads and machine-specific backup paths

## Conditional Families (R3_CONDITIONAL)
- `references/Onslaught`
- `references/AYAResourceExtractor`
Action required: decide include/retarget/exclude based on licensing and public availability.

## Operational Guidance
- Use allowlist-first packaging; do not invert this into denylist-only publishing.
- Path allowlisting is not sufficient content safety: app ZIP/export candidate
  text payloads are scanned for private/local proof material before publishing.
- Local Ghidra/proof backup roots are provenance details for local overlays only.
  ZIP/export candidates must exclude or summarize those rows before publishing.
- This note records high-risk ZIP/export exclusions; the curated manifest remains
  the complete package/export policy source.
- Curated package candidate output is generated in the public-primary source
  tree from `release/readiness/curated_release_manifest.json`.
- `release/readiness/public_candidate_allowlist.tsv` must be manifest-derived
  (`py -3 tools/release_curated_manifest.py`), not raw class inventory, and is
  the package/export allowlist artifact.
- `roadmap/release-allowlist-profile.md`,
  `roadmap/release-allowlist-classification.tsv`, their lore mirrors, and
  `release/readiness/private_only_inventory.tsv` are release-accounting/profile
  artifacts, not portable app ZIP payload.
- `tools/release_profile_snapshot.py` classifies the ZIP/export exclusion
  families above as `R4_DENY` so `release/readiness/private_only_inventory.tsv`
  stays aligned with this note.
- Materialize the legacy standalone review tree with
  `py -3 tools/export_curated_release_tree.py --dest ../Onslaught-Career-Editor-public-candidate --force-clean`.
- Keep canonical docs and lore mirrors in sync before generating release snapshots.
- Treat large/generated artifacts (R2) as opt-in only.
- Re-run dry-run gate after any file movement affecting release classifications.
