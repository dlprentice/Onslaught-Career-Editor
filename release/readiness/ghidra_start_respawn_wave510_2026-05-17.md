# Ghidra Start / Respawn Wave510 Readiness Note

Date: 2026-05-17

## Summary

Wave510 saved static Ghidra names, signatures, comments, and tags for 7 adjacent start/respawn helpers. The tranche includes 7 renames: one `CRelaxedSquad` stale-purpose correction and six `CStart` lifecycle, spawn, and availability corrections that move two stale `CGame` labels onto the start-point object they operate on.

This is static retail Ghidra evidence only. It does not prove exact `CRelaxedSquad`, `CStart`, `CStartInitThing`, BattleEngine init/effect, active-reader, map-who, global-list, or spawn/start object layouts. It also does not prove runtime respawn behavior, runtime AI behavior, BEA launch behavior, game patching, or rebuild parity.

## Targets

| Address | Saved signature |
| --- | --- |
| `0x004ea8d0` | `void * __fastcall CRelaxedSquad__CreateIterator(void * this)` |
| `0x004eacc0` | `void * __thiscall CStart__Constructor(void * this)` |
| `0x004ead70` | `void * __thiscall CStart__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004ead90` | `void __fastcall CStart__Destructor(void * this)` |
| `0x004eae10` | `void __thiscall CStart__Init(void * this, void * init)` |
| `0x004eaf20` | `void * __thiscall CStart__SpawnBattleEngine(void * this, int play_effect)` |
| `0x004eb130` | `bool __fastcall CStart__Available(void * this)` |

## Evidence

- `CRelaxedSquad__CreateIterator` corrects the stale `CRelaxedSquad__Create` purpose/signature. The ECX-only body allocates a 0x10-byte `CSPtrSet`, walks `this+0xa4`, adds non-null members through `CSPtrSet__AddToHead`, and returns the set pointer, mirroring the already-hardened `CSquadNormal` iterator pattern.
- `CStart__Constructor`, `CStart__ScalarDeletingDestructor`, `CStart__Destructor`, and `CStart__Init` harden the CStart lifecycle cluster. Vtable read-back places the scalar-deleting destructor and init at `0x005df2ec` slots 1 and 9, with matching secondary-table slots at `0x005df274` slots 31 and 39.
- `CStart__Init` clamps start height through `CStaticShadows__SampleShadowHeightBilinear`, calls `CComplexThing__Init`, links the start into `DAT_00855100`, copies `CStartInitThing`-style player/position/orientation/config/plane-mode fields, and seeds the initial BattleEngine with `CStart__SpawnBattleEngine(play_effect=0)`.
- `CStart__SpawnBattleEngine` corrects stale `CGame__SetupRespawnReaderAndEffect` ownership. It creates OID type 3, binds it through the active-reader cell at `this+0x7c`, initializes it from embedded start init data at `this+0x84`, seeds respawn/default fields, and optionally creates `BE_Respawn_Ground_Effect` or `BE_Respawn_Air_Effect`.
- `CStart__Available` corrects stale `CGame__HasNearbyHostileWithinRadius` ownership. `CGame::RespawnPlayer` calls it while falling back to start points, and the body uses `CMapWho` to reject active hostile/non-excluded owners near the start.

Artifacts are under `subagents/ghidra-static-reaudit/wave510-start-respawn-004ea8d0/`.

## Verification

- `ApplyStartRespawnWave510.java` dry: `updated=0 skipped=7 renamed=0 would_rename=7 missing=0 bad=0`.
- `ApplyStartRespawnWave510.java` apply: `updated=7 skipped=0 renamed=7 would_rename=0 missing=0 bad=0`.
- `ApplyStartRespawnWave510.java` verify dry: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`.
- All three mutation passes reported `REPORT: Save succeeded`.
- Post-readback exports verified `7` metadata rows, `7` tag rows, `8` xref rows, `2247` instruction rows, `7` decompile exports, and `192` vtable-slot rows.
- `py -3 tools\ghidra_start_respawn_wave510_probe.py --check` passed.
- `cmd.exe /c npm run test:ghidra-start-respawn-wave510` passed.
- Queue refresh passed and reports `6078` functions, `2370` commented, `3708` commentless, `1628` exact-undefined signatures, and `1444` `param_N` signatures.
- Current telemetry proxies are comment-backed `2370/6078 = 38.99%` and strict comment-plus-clean-signature `2316/6078 = 38.10%`; these are progress telemetry only, not completion certification.
- Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-180231_post_wave510_start_respawn_verified` with `19` files, `158272391` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

- Runtime respawn/start-point selection behavior.
- Runtime relaxed-squad AI behavior or iterator ownership/lifetime.
- Exact source-body identity for the checked helpers.
- Concrete CRelaxedSquad/CStart/CStartInitThing/BattleEngine/init/effect/active-reader/map-who/global-list layouts.
- BEA launch behavior, game patching behavior, or rebuild parity.
