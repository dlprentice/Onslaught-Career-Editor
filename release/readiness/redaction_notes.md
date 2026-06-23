# Redaction Notes

## Hard Exclusions (R4_DENY)
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
- Path allowlisting is not sufficient content safety: candidate text payloads are scanned for private/local proof material before public export.
- Local Ghidra/proof backup roots are provenance details for the private repo only. Public candidates must exclude or sanitize those rows before export.
- This note records high-risk hard exclusions; the curated manifest remains the complete policy source.
- Curated public candidate output is generated in the private source tree from `release/readiness/curated_release_manifest.json`; that private policy input is not public candidate payload.
- `release/readiness/public_candidate_allowlist.tsv` must be manifest-derived (`python3 tools/release_curated_manifest.py`), not raw class inventory, and is the public candidate allowlist artifact.
- `roadmap/release-allowlist-profile.md`, `roadmap/release-allowlist-classification.tsv`, their lore mirrors, and `release/readiness/private_only_inventory.tsv` are private-side accounting/profile artifacts, not public candidate payload.
- `tools/release_profile_snapshot.py` classifies the hard-exclusion families above as `R4_DENY` so `release/readiness/private_only_inventory.tsv` stays aligned with this note.
- Materialize the standalone review tree with `python3 tools/export_curated_release_tree.py --dest ../Onslaught-Career-Editor-public-candidate --force-clean`.
- Keep canonical docs and lore mirrors in sync before generating release snapshots.
- Treat large/generated artifacts (R2) as opt-in only.
- Re-run dry-run gate after any file movement affecting release classifications.
