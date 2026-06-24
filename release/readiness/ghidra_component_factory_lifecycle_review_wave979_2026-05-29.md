# Ghidra Wave979 Component factory/lifecycle review (2026-05-29)

Status: read-only static review
Date: 2026-05-29
Branch: `main`
Tag: `component-factory-lifecycle-review-wave979`

## Scope

Wave979 re-reviewed Component factory/lifecycle helpers from the Wave911 focused queue, including Component weapon/subcomponent creation, ComponentBomberAI and FenrirMainGunAI lifecycle wrappers, and the shared ComponentAI reader-forwarding slot.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00427b80` | `CComponent__VFunc_09_00427b80` | Reviewed; no mutation |
| `0x00427cd0` | `CComponent__CreateSubComponent1` | Reviewed; no mutation |
| `0x00427d50` | `CComponent__CreateSubComponent2` | Reviewed; no mutation |
| `0x00427dd0` | `CComponent__CreateWeaponComponent` | Reviewed; no mutation |
| `0x00427f90` | `CComponentBomberAI__scalar_deleting_dtor` | Reviewed; no mutation |
| `0x00427fb0` | `CComponentBomberAI__dtor_base` | Reviewed; no mutation |
| `0x00428050` | `CFenrirMainGunAI__scalar_deleting_dtor` | Reviewed; no mutation |
| `0x00428070` | `CFenrirMainGunAI__dtor_base` | Reviewed; no mutation |
| `0x00428e80` | `CComponentAI__ClearReaderIfTargetDestroyedThenForward` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave979-component-factory-lifecycle-review/metadata.tsv
subagents/ghidra-static-reaudit/wave979-component-factory-lifecycle-review/tags.tsv
subagents/ghidra-static-reaudit/wave979-component-factory-lifecycle-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave979-component-factory-lifecycle-review/instructions.tsv
subagents/ghidra-static-reaudit/wave979-component-factory-lifecycle-review/decompile/
```

Read-back result:

```text
metadata: 9/9 OK
tags: 9/9 OK
xrefs: 14 rows
instructions: 437 rows
decompile: 9/9 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. `CComponent__CreateWeaponComponent` still branches through Fenrir Bomb Launcher, Fenrir Main Gun, Carrier Health Pad, and fallback component paths. The ComponentBomberAI and FenrirMainGunAI scalar-deleting destructors and destructor bases remain tied to RTTI/vtable context, and `CComponentAI__ClearReaderIfTargetDestroyedThenForward` remains the shared Component AI reader-clear/forwarding slot.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260529-143700_post_wave979_component_factory_lifecycle_review_verified
files=19
bytes=173804423
MissingCount=0
ExtraCount=0
HashDiffCount=0
```

## Truth Boundary

This review confirms static Ghidra coherence for selected Component factory/lifecycle helpers. It does not prove exact Component.cpp source-body identity, concrete Component/AI/weapon layouts, runtime component or weapon behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave980 from the next Wave911 focused candidate.
