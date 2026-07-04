# Ghidra BattleEngine Jet/Animation Review Wave974 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `battleengine-jet-animation-review-wave974`

Wave974 re-read six source-backed BattleEngine animation and jet-control helpers, then recovered one previously missing source-backed Player input function boundary at `0x004d3110 CPlayer__ReceiveButtonAction`. The pass created one function object, saved a `void __thiscall CPlayer__ReceiveButtonAction(void * this, void * from_controller, int button, float value)` signature plus comment/tags, made no executable-byte change, and did not launch BEA.

Mutation status: function-boundary recovery.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00409e80 CBattleEngine__AutoZoomOut` | Source parity with `references/Onslaught/BattleEngine.cpp` lines 1919-1922; writes desired zoom to max zoom and is called by walker/jet weapon-change paths. |
| `0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation` | Source parity with `BattleEngine.cpp` lines 3617-3635; checks transition animation names and switches to walk/fly. |
| `0x0040ef20 CBattleEngine__GroundParticleEffect` | Source parity with `BattleEngine.cpp` lines 3638-3665; samples water/ground height and spawns land/water ground effect. |
| `0x00410310 CBattleEngineJetPart__Thrust` | Source parity with `BattleEngineJetPart.cpp` lines 64-106; updates thruster value and loop-start state. |
| `0x00410490 CBattleEngineJetPart__Turn` | Source parity with `BattleEngineJetPart.cpp` lines 109-147; updates yaw/roll velocity with zoom, low-speed, slow-movement, and transform interpolation. |
| `0x00410670 CBattleEngineJetPart__Pitch` | Source parity with `BattleEngineJetPart.cpp` lines 150-171; updates pitch velocity with zoom, slow-movement, and transform interpolation. |
| `0x004d3110 CPlayer__ReceiveButtonAction` | Source parity with `references/Onslaught/Player.cpp` lines 283-511; `RET 0x0c`; DATA pointer `0x005de77c`; dispatches jet inputs to `CBattleEngineJetPart__Turn/Pitch/YawLeft/YawRight/Thrust`. |

Read-back evidence:

- `ApplyBattleEngineJetAnimationWave974.java dry`: `updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- `ApplyBattleEngineJetAnimationWave974.java apply`: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0`
- `ApplyBattleEngineJetAnimationWave974.java final dry`: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Pre exports: 6 metadata rows, 6 tag rows, 9 xref rows, 511 body-instruction rows, and 6 decompile rows.
- Post exports: 7 metadata rows, 7 tag rows, 10 xref rows, 749 body-instruction rows, and 7 decompile rows.
- Queue after Wave974: `6211` total, `6211` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `6211/6211 = 100.00%`, strict clean-signature proxy `6211/6211 = 100.00%`.
- Wave911 focused re-audit progress: `356/1408 = 25.28%`.
- Expanded static surface progress: `415/1467 = 28.29%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-210511_post_wave974_battleengine_jet_animation_review_verified`, 19 files, 173771655 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra database now has a function object at `0x004d3110` with the saved `CPlayer__ReceiveButtonAction` name/signature/comment/tags.
- The six reviewed BattleEngine/JetPart helper rows still read back with their expected source-backed names/signatures/comments.
- The JetPart call xrefs now resolve from `0x004d3110 CPlayer__ReceiveButtonAction`.

What remains unproven:

- Exact `CPlayer`, `CController`, `CBattleEngine`, walker-part, or jet-part layouts.
- Exact button enum names beyond source/static mapping.
- Runtime controller/input behavior, camera behavior, jet flight feel, animation behavior, BEA patching, and rebuild parity.
