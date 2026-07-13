# Ghidra Projectile / Round Spawn Tail Wave495 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004dac90` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-17

## Scope

Wave495 saved static Ghidra name/signature/comment/tag hardening for ten projectile/round spawn-tail functions:

| Address | Saved state |
| --- | --- |
| `0x004d9ef0` | `void __fastcall CRound__UpdateRoundAndTriggerLaunchEffect(void * this)` |
| `0x004d9f30` | `void __thiscall CRound__UpdateEffectTransformByMode_004d9f30(void * this, int effectMode, void * context, void * targetOrOwner)` |
| `0x004daa20` | `int __cdecl CEngine__FindPresetIndexByName(char * presetName)` |
| `0x004daab0` | `void __thiscall CRound__SetTargetReaderIfAllowed(void * this, void * targetReader, int replaceExisting)` |
| `0x004dab50` | `void __fastcall CRound__RemoveActiveReaderById(void * this)` |
| `0x004daba0` | `void * __fastcall CRound__FindNearbyHostileWithinProjectileRadius(void * this)` |
| `0x004dac90` | `void __thiscall CRound__SelectBestTargetReaderAndSyncAimState(void * this, void * eventPayload, void * unusedContext)` |
| `0x004db090` | `double __fastcall CRound__GetPresetScalarByConfigName(void * this)` |
| `0x004db150` | `void __fastcall CRound__SpawnConfiguredProjectile(void * this)` |
| `0x004db630` | `void __fastcall CRound__ArmProjectileAndSpawnTrailEffect(void * this)` |

## Evidence

- Apply script: `tools/ApplyProjectileSpawnTailWave495.java`
- Probe: `tools/ghidra_projectile_spawn_tail_wave495_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave495-projectile-spawn-tail-004d9f30/`
- Initial dry/apply/verify:
  - Dry: `updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0`
  - Apply: `updated=9 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Corrective dry/apply/verify for `0x004d9ef0`:
  - Dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
  - Apply: `updated=1 skipped=9 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `13` context metadata rows, `13` tag rows, `28` xref rows, `16` vtable rows, and `13` decompile exports.
- Focused probe: `py -3 tools\ghidra_projectile_spawn_tail_wave495_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-projectile-spawn-tail-wave495` PASS.
- Queue refresh: `6068` total functions, `2239` commented, `3829` commentless, `1673` undefined signatures, `1516` `param_N`; strict comment-plus-clean-signature proxy `2180/6068 = 35.93%`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-101321_post_wave495_projectile_spawn_tail_verified` with `19` files, `157649799` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Not Proven

- Exact source virtual names and full `Round.cpp` source-body identity.
- Concrete `CRound`, `CRoundData`, projectile-preset, active-reader, effect, trail, or init-payload layouts.
- Runtime projectile spawn, targeting, trail/effect behavior, BEA launch behavior, game patching, and rebuild parity.
