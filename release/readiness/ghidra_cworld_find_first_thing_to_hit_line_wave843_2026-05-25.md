# Ghidra CWorld FindFirstThingToHitLine Wave843 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cworld-find-first-thing-to-hit-line-wave843`

Wave843 CWorld FindFirstThingToHitLine renamed `0x0050b030 OID__TraceLineAndSelectBestTargetHit` to `0x0050b030 CWorld__FindFirstThingToHitLine` and saved a bounded `__thiscall` signature/comment/tag treatment. The pass made no function-boundary change and no executable-byte change.

Representative anchors:

| Address / area | Evidence |
| --- | --- |
| `0x0050b030 CWorld__FindFirstThingToHitLine` | Saved as `int __thiscall CWorld__FindFirstThingToHitLine(void * this, undefined4 line_00, undefined4 line_04, undefined4 line_08, undefined4 line_0c, undefined4 line_10, undefined4 line_14, undefined4 line_18, undefined4 line_1c, undefined4 line_20, undefined4 line_24, undefined4 line_28, undefined4 line_2c, undefined4 line_30, void * ignored_owner, void * hit_result, int stop_on_first_valid_hit, int child_trace_mode, int collision_mode, uint reject_flags, int heightfield_trace_flags, uint required_thing_flags)`. |
| Source-name corroboration | Stuart source callsites use `WORLD.FindFirstThingToHitLine(...)`; retail callsites load `ECX` with `DAT_00855090` before `CALL 0x0050b030`, and existing CWorld docs identify `DAT_00855090` as the CWorld singleton. |
| Body ABI | Body ends with `RET 0x54`, matching a `0x34-byte by-value CLine-style stack copy` plus eight explicit stack fields after the ECX CWorld receiver. |
| Static collision/targeting path | Body calls `CHeightField__TraceLineAgainstHeightfield`, walks `CMapWho__GetFirstEntryWithinLine` / `CMapWho__GetNextEntryWithinLine`, resolves owners through `CMapWhoEntry__GetOwner`, filters through `CThing__GetPersistentCollisionSeekingThing`, and can return early when `stop_on_first_valid_hit` is nonzero. |
| Callsite spread | Post xrefs include `CDXEngine__Render`, `CBattleEngine__HandleAutoAim`, `CBattleEngine__CalcUnitOverCrossHair`, `CMCMech__GetFootHeight`, `CMonitor__Process`, `CCollisionSeekingRound__CreateEffect`, `OID__CanFireAtTarget_BallisticArcA/B`, and `CUnit__ApplyDamage`. |

Read-back evidence:

- Initial dry: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Initial apply deliberately stopped on `READBACK_BAD` because Ghidra auto-inserted the `__thiscall` receiver and exposed an extra explicit `world` parameter in the expected script model.
- Corrected dry: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Corrected apply: `READBACK_OK`, `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 1 metadata row, 1 tag row, 12 xref rows, 121 instruction-window rows, 385 target-deep instruction rows, 322 target-range disassembly rows, 1260 xref-site instruction rows, 1 target decompile row, 9 caller metadata/decompile rows, and 7 context metadata/tag/decompile rows.
- Queue after Wave843: 6098 total functions, 5667 commented, 431 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5667/6098 = 92.93%`, strict clean-signature proxy `5667/6098 = 92.93%`.
- Next raw commentless row: `0x0050b9c0 CWorld__LoadWorld`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-043624_post_wave843_cworld_find_first_thing_to_hit_line_verified`, 19 files, 171871111 bytes, `DiffCount=0`.

What this proves:

- The target function exists in the saved Ghidra project as `CWorld__FindFirstThingToHitLine`.
- The saved signature/comment/tags match the observed retail ABI, source-name corroboration, CWorld singleton receiver evidence, line-copy callsite pattern, xrefs, and helper calls.
- The first apply caught a signature-model issue and the corrected apply/final dry read back cleanly.

What remains unproven:

- Exact CLine layout.
- Exact CWorldLineColReport layout.
- Exact enum names for collision/status flags.
- Runtime collision/targeting behavior.
- BEA patching behavior.
- Rebuild parity.
