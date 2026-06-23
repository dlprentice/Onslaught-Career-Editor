# Ghidra BattleEngine D0-Tail Signature Tranche - 2026-05-09

## Summary

This wave reparsed six already named functions in the `0x0040d0f0` to `0x0040dce0` BattleEngine-adjacent tail after fresh metadata, decompile, xref, instruction, caller, source, and vtable/RTTI read-back. The saved Ghidra names were useful in several places, but five owner labels were stale or too broad, and all six signatures/comments needed stronger proof boundaries.

A serial headless dry/apply pass saved corrected names, hardened signatures, and comments. Fresh read-back plus a focused probe then verified the saved state.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040d0f0` | `CEngine__CanUseBallisticArcNoLocks` | `int __thiscall CWeaponStatement__UsesBallisticArcNoLocks(void * this, void * weaponStatement)` | Caller evidence comes from CUnit ballistic range and OID aim/fire checks; the body gates projectile gravity plus lock fields `+0x50` and `+0x6c`. Runtime weapon-fire and stealth behavior remain unproven. |
| `0x0040d470` | `CGeneralVolume__ctor_like_0040d470` | `void __thiscall CLine__ctor_fromEndpoints(void * this, void * startPoint, void * endPoint)` | Vtable/RTTI read-back confirms `CGeneralVolume` base vtable then `CLine` vtable, with two 16-byte endpoint/vector copies. Runtime collision behavior remains unproven. |
| `0x0040da30` | `CExplosionInitThing__BuildInterpolatedWorldTransform` | `void * __thiscall CBattleEngine__BuildInterpolatedWorldTransform(void * this, void * outWorldTransform, void * unusedContext)` | `CExplosionInitThing__RenderTargetMarkers3D` passes the BattleEngine pointer at `+0x50`; the body builds an interpolated BattleEngine world transform from current/old position and orientation state. Runtime render behavior remains unproven. |
| `0x0040dc90` | `CExplosionInitThing__CountFlag9CBySelectionMode` | `int __thiscall CBattleEngine__CountFlag9CBySelectionMode(void * this)` | Objective-panel caller plus tail-call evidence shows selection-state counting: `+0x260 == 3` uses the `+0x57c` list, otherwise the `+0x578` list. Objective completion runtime behavior remains unproven. |
| `0x0040dcb0` | `CCockpit__SetFlag58C_Enabled` | `void __thiscall CBattleEngine__SetFlag58CEnabled(void * this)` | Tiny BattleEngine state setter writes `1` to `+0x58c`, adjacent to neighboring transition/selection helpers. Runtime behavior remains unproven. |
| `0x0040dce0` | `CBattleEngine__HostileEnvironment` with stale parameter debt | `void __thiscall CBattleEngine__HostileEnvironment(void * this)` | Source bridge and retail decompile match the hostile-environment HUD sample/log/timestamp context, including timestamp write at `+0x510`. Runtime HUD audio behavior remains unproven. |

## Validation

- Focused tests: `py -3 tools\ghidra_battleengine_d0_tail_signature_tranche_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_battleengine_d0_tail_signature_tranche_probe.py tools\ghidra_battleengine_d0_tail_signature_tranche_probe_test.py` passed.
- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `11` rows.
- Fresh instruction read-back: `222` rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-battleengine-d0-tail-signature-tranche` passed with `6` targets, `5` corrected names, `6` hardened signatures, and `0` comment overclaims.
- Refreshed queue probe after this and the BattleEngineData/configuration tranche: `5866` functions, `509` commented functions, `5357` commentless functions, `2071` undefined signatures, and `2443` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete weapon-statement, BattleEngine, CLine, linked-list, hostile-environment, transform, collision, HUD-audio, or objective layouts; exact source identity for every target; exact retail `CBattleEngine::WeaponFired`; `weapon_fire_breaks_stealth`; runtime weapon firing; runtime cloak activation; fire-while-cloaked behavior; BEA launch behavior; game patching; tags/local names/types; or rebuild parity.
