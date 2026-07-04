# Ghidra Round Config Bridge Review Wave991 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `round-config-bridge-review-wave991`

Wave991 re-audited the round/projectile configuration bridge after Wave990 and saved one bounded Ghidra comment/tag normalization at `0x00426150 CCollisionSeekingRound__Init`. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary saved normalization:

| Address | Result |
| --- | --- |
| `0x00426150 CCollisionSeekingRound__Init` | Refreshed the saved comment from the earlier "tags unproven" wording and added `round-config-bridge-review-wave991`, `wave991-readback-verified`, `tag-corrected`, and related static read-back tags. Fresh xrefs tie the row to callers `0x004269b0 CCollisionSeekingRound__InitWithSound` and `0x00426a40 CCollisionSeekingRound__CreateEffect`, plus DATA/vtable ref `0x005d9614`. |

Context targets re-exported without mutation:

- `0x00437fe0 CPhysicsRoundValue__SetOwnedAuxStringAt0C`
- `0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08`
- `0x00438b40 CRoundGridOfFear__ApplyToRoundByName`
- `0x0042ffa0 CRoundStatement__Create`
- `0x00430210 CRoundStatement__LoadFromMemBuffer`
- `0x00437490 CPhysicsScriptStatements__CreateStatementType5`
- `0x004d8410 CRound__Init`

Read-back evidence:

- `ApplyRoundConfigBridgeWave991.java` dry: `updated=0 skipped=1 comment_only_updated=1 tags_added=10 missing=0 bad=0`
- `ApplyRoundConfigBridgeWave991.java` apply: `updated=1 skipped=0 comment_only_updated=1 tags_added=10 missing=0 bad=0`
- `ApplyRoundConfigBridgeWave991.java` final dry: `updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports: `8` metadata rows, `8` tag rows, `12` xref rows, `1430` body-instruction rows, and `8` decompile rows.
- Queue closure after refresh remains `6222/6222 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress is `445/1408 = 31.61%`; expanded static surface progress is `525/1478 = 35.52%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified`, 19 files, 173837191 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved Ghidra project now records current tags and comment wording for `CCollisionSeekingRound__Init`.
- The round config bridge is statically coherent across `CCollisionSeekingRound__InitWithSound`, `CCollisionSeekingRound__CreateEffect`, `CRoundStatement__Create`, `CRoundStatement__LoadFromMemBuffer`, `CPhysicsScriptStatements__CreateStatementType5`, and `CRound__Init`.
- The existing signatures and comments for the seven context rows still read back cleanly.

What remains unproven:

- Runtime projectile behavior.
- Runtime physics-script behavior.
- Exact `CCollisionSeekingRound`, `CRound`, or PhysicsScript round-value layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
