# Ghidra Attachment / Escape / Pause Signature Correction - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence

## Summary

Serialized headless Ghidra dry/apply/read-back hardened `6` attachment, escape-pod, Euler-angle, and pause-menu targets after focused metadata, decompile, xref, instruction, tag, source, and caller-context review.

This pass keeps the unresolved shared vtable-slot owner deferred, hardens two OID attachment transform helper signatures, corrects the stale `CEscapePod__VFunc_09_0044aab0` label to the evidence-bounded escape-pod init/effect helper, corrects the stale `CExplosionInitThing` owner at `0x0044adb0` to a CEulerAngles constructor-style matrix conversion helper, and hardens the pause-menu active-reader binding helper.

## Targets

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0044a830` | `VFuncSlot_03_0044a830` | Signature/comment/tag hardening only; copies three dwords from `source_vector3` into `this+0x08..0x10` and is called by `CRadarWarningReceiver__Init`. Owner remains unresolved. |
| `0x0044a850` | `OID__GetAttachmentOrOriginTransform` | Reads attachment id at `this+0x0c`, falls back to base object position, otherwise queries vfunc `+0x160` to populate `out_origin`. |
| `0x0044a930` | `OID__GetAttachmentOrBaseOrientationMatrix` | Reads attachment id at `this+0x0c`, falls back to base orientation matrix, otherwise queries vfunc `+0x160` to populate `out_matrix`. |
| `0x0044aab0` | `CEscapePod__InitRocketMeshAndEngineEffect` | Corrected from stale vfunc-slot wording; adjusts init flags, creates `m_rocket.msh` render/resource context, calls `CActor__Init`, and attaches `Muspell_Engine_Small_Effect` when available. |
| `0x0044adb0` | `CEulerAngles__ctor_from_FMatrix` | Corrected from stale `CExplosionInitThing` owner; derives Euler-angle fields from an `FMatrix` using `OID__AcosWrapper` and `fpatan`, with a singular fallback that zeroes yaw/roll. |
| `0x0044ae20` | `CPauseMenu__InitAndSetActiveReader` | Signature/comment/tag hardening; stores `action_id`, binds `reader` through `CGenericActiveReader__SetReader`, returns `this`, and ends with `ret 0x8`. |

## Validation

- Headless dry run: `targets=6 updated=0 skipped=6 failed=0`.
- Headless apply: `targets=6 updated=6 skipped=0 failed=0`, with `REPORT: Save succeeded`.
- Read-back exports: `6` metadata rows, `6` decompile exports, `61` xref rows, `270` focused instruction rows, and `6` tag rows.
- Focused probe: `PASS`; `7` xref evidence hits, `8` instruction evidence hits, `0` stale name hits, `0` stale signature hits, and `0` overclaim hits.
- Whole-database refresh: `6008` functions, `1264` commented functions, `4744` commentless functions, `1948` `undefined` signatures, and `2005` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1264/6008 = 21.04%`; strict clean-signature `1202/6008 = 20.01%`. These values are not milestones.
- Actual live Ghidra backup: `G:\GhidraBackups\BEA_20260513_064724_post_wave365_attachment_escape_pause_verified`, verified at `19` files, `153160583` bytes, and `HashDiffCount=0`.

## Claim Boundary

This proves saved static retail Ghidra names, signatures, comments, tags, selected xrefs, and selected instruction/decompile read-back for the `6` listed targets.

It does not prove exact Stuart-source method identity for every target, concrete class/global layouts, local variables/types, runtime attachment/escape-pod/pause-menu behavior, BEA launch behavior, game patching, or rebuild parity. The `21.04%` / `20.01%` proxy values remain triage telemetry only; the target remains as close to `100%` evidence-grade static RE as possible.
