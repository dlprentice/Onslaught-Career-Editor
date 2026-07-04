# Ghidra Wave977 configured pickup bridge review (2026-05-29)

Status: read-only static review
Date: 2026-05-29
Branch: `main`
Tag: `configured-pickup-bridge-review-wave977`

## Scope

Wave977 re-reviewed the configured-pickup bridge centered on the top remaining Wave911 row `CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`, with adjacent Unit, UnitAI, GeneralVolume, destroyable-segment, and world-physics pickup helpers.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004ef100` | `CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` | Reviewed; no mutation |
| `0x004f9490` | `CUnit__SpawnConfiguredPickupIfAboveWater` | Reviewed; no mutation |
| `0x004fd230` | `CUnit__SpawnProfileDropPickup` | Reviewed; no mutation |
| `0x00428110` | `CUnitAI__UpdateActivationStateAndSpawnPickup` | Reviewed; no mutation |
| `0x0040dfb0` | `CGeneralVolume__SpawnPickupAndDispatch` | Reviewed; no mutation |
| `0x00442710` | `CDestroyableSegment__SpawnConfiguredPickup` | Reviewed; no mutation |
| `0x00442d40` | `CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09` | Reviewed; no mutation |
| `0x0050ff10` | `CWorldPhysicsManager__CreatePickup` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave977-configured-pickup-bridge-review/metadata.tsv
subagents/ghidra-static-reaudit/wave977-configured-pickup-bridge-review/tags.tsv
subagents/ghidra-static-reaudit/wave977-configured-pickup-bridge-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave977-configured-pickup-bridge-review/instructions.tsv
subagents/ghidra-static-reaudit/wave977-configured-pickup-bridge-review/decompile/
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
xrefs: 85 rows
instructions: 960 rows
decompile: 8/8 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. `CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` remains a CUnit-family vtable slot-64 bridge at `0x005e1610`, and fresh read-back confirms it loops three times into `CUnit__SpawnConfiguredPickupIfAboveWater`. The configured-pickup bridge remains statically connected to profile-driven Unit drops, UnitAI activation pickup creation, GeneralVolume pickup dispatch, destroyable-segment pickup spawn/update paths, and the shared `CWorldPhysicsManager__CreatePickup` factory.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260529-141500_post_wave977_configured_pickup_bridge_review_verified
files=19
bytes=173804423
MissingCount=0
ExtraCount=0
HashDiffCount=0
```

## Truth Boundary

This review confirms static Ghidra coherence for selected configured-pickup helpers. It does not prove exact source virtual names, concrete Unit/profile/init/pickup layouts, runtime pickup/drop behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave978 from the next Wave911 focused candidate.
