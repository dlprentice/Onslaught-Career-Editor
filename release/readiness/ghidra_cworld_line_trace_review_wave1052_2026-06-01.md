# Ghidra CWorld Line Trace Review Wave1052

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00507ab0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete read-only static review
Date: 2026-06-01
Scope: `cworld-line-trace-review-wave1052`

Wave1052 re-read `0x0050b030 CWorld__FindFirstThingToHitLine` after the Wave911 continuation queue selected the CWorld line-trace row as the next focused candidate. No mutation was needed: the saved Wave843 name, bounded signature, comment, and tags remain coherent with fresh metadata, tags, xrefs, instruction export, decompile output, and Stuart-source callsite evidence.

The wave made no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed row:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x0050b030 CWorld__FindFirstThingToHitLine` | `int __thiscall CWorld__FindFirstThingToHitLine(void * this, undefined4 line_00, undefined4 line_04, undefined4 line_08, undefined4 line_0c, undefined4 line_10, undefined4 line_14, undefined4 line_18, undefined4 line_1c, undefined4 line_20, undefined4 line_24, undefined4 line_28, undefined4 line_2c, undefined4 line_30, void * ignored_owner, void * hit_result, int stop_on_first_valid_hit, int child_trace_mode, int collision_mode, uint reject_flags, int heightfield_trace_flags, uint required_thing_flags)` | Fresh xrefs and decompile still show the CWorld singleton receiver, a `RET 0x54` by-value line-copy ABI, terrain trace through `CHeightField__TraceLineAgainstHeightfield`, spatial candidate scan through `CMapWho__GetFirstEntryWithinLine` / `CMapWho__GetNextEntryWithinLine`, candidate filtering through `CThing__GetPersistentCollisionSeekingThing`, nearest accepted thing-hit selection, hit-result writes, and early return when `stop_on_first_valid_hit` is nonzero. |

Context callsites:

- `0x0040acc0 CBattleEngine__CalcUnitOverCrossHair`
- `0x0040b6d0 CBattleEngine__HandleAutoAim`
- `0x00490a40 CHeightField__TraceLineAgainstHeightfield`
- `0x00492110 CMapWho__GetFirstEntryWithinLine`
- `0x004925a0 CMapWho__GetNextEntryWithinLine`
- `0x00492c90 CMapWhoEntry__GetOwner`
- `0x004f3d10 CThing__GetPersistentCollisionSeekingThing`
- `0x004f9a90 CUnit__ApplyDamage`
- `0x004fb500 CUnit__CanFireAtTarget_BallisticArcA`
- `0x004fb5a0 CUnit__CanFireAtTarget_BallisticArcB`
- `0x00507ab0 OID__CanFireAtTarget_BallisticArcA`
- `0x005088b0 OID__CanFireAtTarget_BallisticArcB`
- `0x0053e2e0 CDXEngine__Render`

Source callsite evidence:

- `references/Onslaught/BattleEngine.cpp` uses `CLine`, `CWorldLineColReport`, `WORLD.FindFirstThingToHitLine(...)`, `ECL_MESH`, and `kCollideThing` in ground probe, auto-aim, crosshair, and line-of-sight paths.
- `references/Onslaught/DXEngine.cpp` and `references/Onslaught/PCEngine.cpp` use `WORLD.FindFirstThingToHitLine(line_of_sight,to_ignore, &wlcr, TRUE)==kCollideNothing` for sun/line-of-sight rendering paths.
- `references/Onslaught/InitThing.h` carries the source enum anchors `ECL_MESH = 2` and `kCollideThing`.

Evidence counts:

- Primary exports: `1` metadata row, `1` tag row, `12` xref rows, `321` function-body instruction rows, and `1` decompile row.
- Context exports: `13` metadata rows, `13` tag rows, `105` xref rows, `4547` function-body instruction rows, and `13` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress advances to `745/1408 = 52.91%`; expanded static surface progress advances to `1033/1509 = 68.46%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified`, 19 files, 174623623 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved CWorld line-trace function object still exists in the loaded Ghidra database with the prior bounded Wave843 name/signature/comment/tags.
- The reviewed static evidence coheres across metadata, tags, xrefs, instruction bodies, decompile output, source callsites, context helpers, and a verified project backup.
- The older owner/name correction remains appropriate: this is a CWorld singleton line-trace query, not an owner-neutral OID helper.

What remains separate proof:

- Concrete `CLine` and `CWorldLineColReport` layouts beyond observed by-value/callsite behavior.
- Runtime collision, terrain, MapWho, auto-aim, targeting, damage, and sun line-of-sight behavior.
- Exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1052; cworld-line-trace-review-wave1052; 0x0050b030 CWorld__FindFirstThingToHitLine; CHeightField__TraceLineAgainstHeightfield; CMapWho__GetFirstEntryWithinLine; CMapWho__GetNextEntryWithinLine; CThing__GetPersistentCollisionSeekingThing; CBattleEngine__CalcUnitOverCrossHair; CBattleEngine__HandleAutoAim; CUnit__ApplyDamage; CDXEngine__Render; references/Onslaught/BattleEngine.cpp; references/Onslaught/DXEngine.cpp; references/Onslaught/PCEngine.cpp; 745/1408 = 52.91%; 1033/1509 = 68.46%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified; no mutation.
