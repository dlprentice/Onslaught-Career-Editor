# Ghidra Top-500 Residual Pre-900 Correction Review Wave1084 Readiness Note

Status: complete read-only static review
Date: 2026-06-02
Scope: `top500-residual-pre900-correction-review-wave1084`

Wave1084 re-read six Wave911 top-500 risk-ranked rows that were corrected in pre-900 waves but had not yet been represented by a post-900 readiness note. The pass made no Ghidra mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation.

Reviewed targets:

| Address | Saved name | Older correction anchor | Wave1084 result |
| --- | --- | --- | --- |
| `0x004d1f10` | `CPlane__Hit_CheckFatalDamageAndDie` | Wave485 plane hit animation | Current metadata/comment/tags/decompile still match the bounded plane vtable slot-39 hit/death claim. |
| `0x004de1d0` | `CSafeSide__ShutdownAndUnlinkFactionAnchor` | Wave542 SafeSide shutdown | Current metadata/comment/tags/decompile still match the bounded SafeSide global faction-anchor unlink plus `CComplexThing__Shutdown` claim. |
| `0x004ea8d0` | `CRelaxedSquad__CreateIterator` | Wave510 start/respawn correction | Current metadata/comment/tags/decompile still match the bounded CSPtrSet iterator/snapshot creator claim. |
| `0x00505960` | `CWaypoint__Load` | Wave538 waypoint load | Current metadata/comment/tags/decompile still match the bounded waypoint name/object-link load claim. |
| `0x00523db0` | `Input__ResetMouseTransientState` | Wave567 input cursor correction | Current metadata/comment/tags/decompile still match the bounded mouse transient reset claim and superseded profiler label. |
| `0x005245e0` | `COggFileRead__scalar_deleting_dtor` | Wave568 Ogg/Vorbis stream correction | Current metadata/comment/tags/decompile still match the bounded scalar-deleting destructor wrapper claim. |

Read-back evidence:

- Metadata export: `6` targets, `6` found, `0` missing.
- Tag export: `6` rows, `0` missing.
- Xref export: `11` incoming xref rows.
- Function-body instruction export: `249` instruction rows, `0` missing.
- Decompile export: `6` dumped, `0` missing, `0` failed.
- Queue closure remains `6307/6307 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, `0` `param_N` signatures, `0` weak-name rows, `0` uncertain-owner rows, `0` helper-address rows, and `0` wrapper-address rows.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static re-audit surface advances to `1424/1560 = 91.28%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-122026_post_wave1084_top500_residual_pre900_correction_review_verified`, `19` files, `174820231` bytes, `DiffCount=0`.

What this proves:

- The six selected top-500 residual rows exist in the saved Ghidra project.
- Their saved names, signatures, comments, tags, incoming xrefs, instruction bodies, and decompile outputs remain coherent with their older bounded correction notes.
- No fresh mutation was needed for this tranche.

What remains separate proof:

- Runtime plane hit/death behavior.
- Runtime SafeSide/faction-anchor behavior.
- Runtime squad iterator ownership/lifetime behavior.
- Runtime waypoint navigation/load behavior.
- Runtime mouse/input behavior.
- Runtime Ogg streaming/audio behavior.
- Exact source-body identity and concrete layouts for these rows.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1084; top500-residual-pre900-correction-review-wave1084; 0x004d1f10 CPlane__Hit_CheckFatalDamageAndDie; 0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor; 0x004ea8d0 CRelaxedSquad__CreateIterator; 0x00505960 CWaypoint__Load; 0x00523db0 Input__ResetMouseTransientState; 0x005245e0 COggFileRead__scalar_deleting_dtor; 1424/1560 = 91.28%; 812/1408 = 57.67%; 500/500 = 100.00%; 6307/6307 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-122026_post_wave1084_top500_residual_pre900_correction_review_verified; no mutation.
