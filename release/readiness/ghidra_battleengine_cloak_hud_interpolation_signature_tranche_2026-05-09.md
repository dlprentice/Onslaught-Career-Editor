# Ghidra BattleEngine Cloak / HUD / Interpolation Signature Tranche - 2026-05-09

## Summary

This wave reparsed five already named functions after the static re-audit queue and adjacent source review showed stale owner labels in the BattleEngine cloak, HUD audio, lock percentage, and camera/interpolation area. Fresh metadata, decompile, xref, and instruction read-back showed the old `CGeneralVolume` / `CExplosionInitThing` labels were too broad or wrong for these targets.

A serial headless dry/apply pass saved corrected names, signatures, and proof-boundary comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040d4d0` | `CGeneralVolume__Update4ACLatchFromHeightAndA0` | `void __thiscall CBattleEngine__HandleCloak(void * this)` | Source-aligned cloak toggle helper; checked body touches `+0x4ac` and `+0x5dc` cloak/desired-stealth context and gates activation through configuration/energy checks. Runtime cloak activation and fire-while-cloaked behavior remain unproven. |
| `0x0040d5b0` | `CExplosionInitThing__ComputeNormalizedTimeInRange` | `float __thiscall CLockInfo__GetLockPercentage(void * this)` | Source-aligned lock percentage helper; checked body normalizes lock timer state and clamps the upper bound. Runtime lock UI behavior remains unproven. |
| `0x0040d5f0` | `CBattleEngine__AttachHudSoundEventListener` | `void __thiscall CBattleEngine__PlayHudSampleByName(void * this, char * sampleName)` | Source-aligned HUD sample helper; checked body formats the `hud\\%s` effect name, resolves a sound effect, and plays it in HUD-volume context. Runtime HUD audio behavior remains unproven. |
| `0x0040d660` | `CExplosionInitThing__InterpolateWrappedEulerFromHistory` | `void __thiscall CBattleEngine__GetInterpolatedEulerOrientation(void * this, void * outEuler)` | Source-aligned Euler interpolation helper; checked retail ABI writes the source-style return value through an output buffer. Runtime camera/HUD transform behavior remains unproven. |
| `0x0040d7c0` | `CExplosionInitThing__BuildInterpolatedViewpointTransform` | `void * __thiscall CBattleEngine__GetInterpolatedAutoAimPos(void * this, void * outPos)` | Source-aligned auto-aim position helper; checked body reads current/old player view state, interpolates by frame fraction, and applies auto-aim yaw/pitch offsets. Runtime auto-aim transform behavior remains unproven. |

## Validation

- Focused tests: `py -3 tools\ghidra_battleengine_cloak_hud_interpolation_signature_tranche_probe_test.py` passed `2/2`.
- Headless dry/apply: `updated=0 skipped=5 missing=0 bad=0`, then `updated=5 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `5/5` targets.
- Fresh xref read-back: `13` rows.
- Fresh instruction read-back: `365` rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-battleengine-cloak-hud-interpolation-signature-tranche` passed with `5` targets, `5` renamed targets, `5` signature-hardened targets, `0` `param_N` signature hits, `0` stale-token hits, and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `501` commented functions, `5365` commentless functions, `2076` undefined signatures, and `2450` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete BattleEngine, LockInfo, player-view, camera, sound, active-reader, or configuration layouts; exact retail `CBattleEngine::WeaponFired`; `weapon_fire_breaks_stealth`; runtime cloak activation; fire-while-cloaked behavior; runtime HUD audio; runtime lock UI behavior; BEA launch behavior; game patching; tags/local names/types; or rebuild parity.
