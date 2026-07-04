# Ghidra Collision / Round Tail Wave494 Readiness Note

Date: 2026-05-17

## Scope

Wave494 saved static Ghidra name/signature/comment/tag hardening for seven collision-seeking / round-tail functions:

| Address | Saved state |
| --- | --- |
| `0x004d8a50` | `void * __thiscall CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50(void * this, int flags)` |
| `0x004d8a70` | `void __fastcall CCollisionSeekingRound__ShutdownMonitorAndDestruct(void * this)` |
| `0x004d8dc0` | `void __fastcall VFuncSlot_02_004d8dc0(void * this)` |
| `0x004d9d60` | `void __fastcall CEngine__InitRoundLaunchStateDefaults(void * this)` |
| `0x004d9da0` | `void * __thiscall CCSRay__ScalarDeletingDestructor_004d9da0(void * this, int flags)` |
| `0x004d9dc0` | `void __fastcall CCSRay__DestructorBody_004d9dc0(void * this)` |
| `0x004d9ef0` | `void __fastcall CEngine__UpdateRoundAndTriggerLaunchEffect(void * this)` |

## Evidence

- Apply script: `tools/ApplyCollisionRoundTailWave494.java`
- Probe: `tools/ghidra_collision_round_tail_wave494_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave494-collision-round-tail-004d8a50/`
- Dry/apply/verify:
  - Dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
  - Apply: `updated=7 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified collision-seeking vtable `0x005de950` slot 1 -> `0x004d8a50`, CRound vtable `0x005de82c` slot 2 -> `0x004d8dc0`, CMissile-style vtable `0x005e3ba4` slot 2 -> `0x004d8dc0`, adjacent CCSRay-style vtable `0x005de980` slot 1 -> `0x004d9da0`, and `0x004d9ef0` data refs at `0x005de940` and `0x005e3cb8`.
- Focused probe: `py -3 tools\ghidra_collision_round_tail_wave494_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-collision-round-tail-wave494` PASS.
- Queue refresh: `6068` total functions, `2230` commented, `3838` commentless, `1673` undefined signatures, `1525` `param_N`; strict comment-plus-clean-signature proxy `2171/6068 = 35.78%`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-093427_post_wave494_collision_round_tail_verified` with `19` files, `157617031` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Not Proven

- Exact source virtual names and full `CollisionSeekingRound.cpp`, `collisionseekingthing.cpp`, or `Round.cpp` source-body identity.
- Concrete `CCollisionSeekingRound`, `CCSRay`, `CRound`, launch-state, or helper layouts.
- Runtime projectile collision, ray/helper behavior, launch-effect behavior, BEA launch behavior, game patching, and rebuild parity.
