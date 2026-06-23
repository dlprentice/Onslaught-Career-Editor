# Ghidra Air-Unit Vfunc Owner Correction - 2026-05-09

## Summary

This wave reparsed a focused saved-Ghidra tranche after vtable owner evidence showed several old labels were misleading. A clean headless dry/apply pass updated seven saved names/signatures/comments, then fresh metadata, decompile, xref, instruction, and vtable owner-map read-back verified the result.

## Corrected Targets

| Address | Saved name after correction | Evidence boundary |
| --- | --- | --- |
| `0x00402030` | `CActor__VFunc_18_SyncOldVectorAfterBaseCall` | Superseded by Wave912 as `CActor__StickToGround`; source `CActor::StickToGround()` matches the base call plus old-position copy. |
| `0x00402fa0` | `CUnit__UpdateMotionAndTrailEffects` | Air-unit slot `66` references this motion/effects pass; the body updates velocity/friction, trails, attachment effects, mesh/particle state, and low-altitude crash context. |
| `0x00403730` | `CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport` | `CAirUnit`/`CBigAirUnit`/`CFenrir`/`CCarver`/`CCarrier` slot `68` evidence replaces the old `CExplosionInitThing` owner claim. |
| `0x00403760` | `CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes` | Same air-unit family slot `69` evidence replaces the duplicate `CUnitAI__ProcessAndCrashIfNoAirOrHoverSupport` label. |
| `0x00403a50` | `CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear` | Air and plane subclass slot `117` evidence replaces the old `CFrontEndPage__HasPendingPositionLerp` label. |
| `0x004d20a0` | `CPlane__VFunc_68_CrashIfNoAirSupport` | `CPlane`/`CDiveBomber`/`CGroundAttackAircraft`/`CBomber` slot `68` evidence replaces the old `CExplosionInitThing` owner claim. |
| `0x0047bf60` | `CPlane__VFunc_69_CrashIfNoSupportModes` | Plane-family slot `69` evidence replaces the generic `CUnitAI` owner label and removes the confusing same-name call collision. |

## Validation

- Headless dry/apply: `updated=0 skipped=7 missing=0 bad=0`, then `updated=7 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `7/7` targets.
- Fresh xref read-back: `80` rows.
- Fresh instruction read-back: `931` rows.
- Vtable owner map: `69` owner/slot rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-airunit-vfunc-owner-correction` passed with `0` stale name/signature token hits.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove exact source virtual names, concrete `CActor`/`CUnit`/`CAirUnit`/`CPlane` layouts, support-field semantics, tags, local variable names, structure types, runtime aircraft behavior, crash behavior, or rebuild parity.
