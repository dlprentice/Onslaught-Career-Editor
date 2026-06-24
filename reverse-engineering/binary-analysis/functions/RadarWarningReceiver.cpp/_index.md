# RadarWarningReceiver.cpp

Debug path string: `C:\dev\ONSLAUGHT2\RadarWarningReceiver.cpp` at `0x00631784`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The Radar Warning Receiver (RWR) system alerts pilots when they are being targeted by enemy radar or missiles. It provides audio/visual warnings showing the direction and type of threats.

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x004d66b0 CRadarWarningReceiver__Update` as one of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence keeps the row tied to the event-4000 update loop, global threat state `DAT_008551a0`, and event id `0x0fa2` scheduling/notification context. No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime radar-warning/HUD/audio behavior, exact RWR/threat-entry layout, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave923 (`hud-radar-pause-render-review-wave923`) re-reviewed `0x004d66b0 CRadarWarningReceiver__Update` as part of a HUD/radar/pause/sprite/D3D visible-render support slice. Fresh metadata/tags/xref/instruction/decompile evidence kept the Wave488 event-4000 update-loop claim intact; no mutation was needed. Wave911 focused re-audit progress after this slice is `86/1408 = 6.11%`, while export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified`. Runtime radar-warning/HUD/audio behavior, concrete CRadarWarningReceiver/threat-entry layouts, exact source-body identity, patch behavior, and rebuild parity remain separate proof.

## Class: CRadarWarningReceiver

Inherits from a base class with virtual functions. Member of `CBattleEngine` (initialized during battle setup).

### Vtable

Located at `0x005d8810`:

| Offset | Address | Function |
|--------|---------|----------|
| +0x00 | 0x004d6a10 | `CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000` |
| +0x04 | 0x00405a20 | `CRadarWarningReceiver__scalar_deleting_dtor` |
| +0x08 | 0x004bacb0 | (inherited) |
| +0x0C | 0x0044a830 | `VFuncSlot_03_0044a830` (inherited/shared, owner deferred) |
| +0x10 | 0x0060c5a0 | (inherited; no function object in Wave488 read-back) |
| +0x14 | 0x004014c0 | (inherited) |
| +0x18 | 0x0053f160 | (inherited) |
| +0x1C | 0x004bacb0 | (inherited) |

### Member Offsets (from this pointer)

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| +0x00 | void** | vtable | Virtual function table pointer |
| +0x08 | void* | mOwner | Owning entity (checked for player flag at +0x34) |
| +0x14 | float | mRange | Detection range for threats |
| +0x18 | float | mUpdateInterval | Time between RWR updates |
| +0x1C | CSPtrSet | mThreats | Linked list of tracked threats |
| +0x28 | int | mThreatCount | Number of active threats |
| +0x2C | int | mNewThreatFlag | Set when new threat detected |
| +0x30 | float | mNewThreatTime | Timestamp of newest threat |

### Threat Entry Structure (24 bytes)

Allocated via `OID__AllocObject(0x18, ...)`. Each threat track contains:

| Offset | Type | Description |
|--------|------|-------------|
| +0x00 | float | Bearing angle (radians, from atan2) |
| +0x04 | float | Distance to threat |
| +0x08 | float | Threat type ID (from source +0x2e) |
| +0x0C | void* | Source entity pointer |
| +0x10 | float | Creation timestamp |
| +0x14 | int | Status/flags |

## Functions

### Wave764 RadarWarningReceiver.cpp Unwind Continuation

Wave764 static read-back (`unwind-continuation-wave764`, `wave764-readback-verified`) saved comments/tags/signatures for RadarWarningReceiver.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4880 Unwind@005d4880` through `0x005d48b6 Unwind@005d48b6` as `void __cdecl Unwind@...(void)` rows. Evidence includes DATA scope-table xrefs `0x0061d0d4`, `0x0061d0dc`, `0x0061d104`, and `0x0061d10c`, `CMonitor__Shutdown_Thunk(*(EBP-0x10))`, `CSPtrSet__Clear((*(EBP-0x10))+0x1c)`, `OID__FreeObject_Callback(*(EBP-0x44))` with RadarWarningReceiver.cpp debug path `0x00631784`, line token `0x41`, allocation/type value `0x49`, and `CGenericActiveReader__dtor((*(EBP-0x44))+0x0c)`. Verified backup: `G:\GhidraBackups\BEA_20260523-152957_post_wave764_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime RWR cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### CRadarWarningReceiver__Init

| Property | Value |
|----------|-------|
| Address | `0x004d65a0` |
| Signature | `void __thiscall CRadarWarningReceiver__Init(void * this, void * config_record)` |
| Called From | `CBattleEngine__Init` at `0x00405710` |

Wave488 hardens this existing function's signature/comment/tags from saved Ghidra read-back. It initializes the RWR system:
- Calls shared vtable-slot body `VFuncSlot_03_0044a830` to copy the first three config dwords into `this+0x08..0x10`
- Copies detection range from `config_record+0x0C`
- Copies update interval from `config_record+0x10`
- Schedules first update via sound system (ID 4000)
- Clears new-threat flag and timestamp

### VFuncSlot_03_0044a830

| Property | Value |
|----------|-------|
| Address | `0x0044a830` |
| Signature | `void __thiscall VFuncSlot_03_0044a830(void* this, void* source_vector3)` |
| Called From | `CRadarWarningReceiver__Init` at `0x004d65a9` |

Wave 365 hardens this target's signature/comment/tags while leaving the concrete owner unresolved. The body copies three dwords from `source_vector3` into `this+0x08..this+0x10` and returns with `ret 0x4`. The RWR init caller uses it as config-vector setup before loading range/update interval context. Exact owner, concrete layout, runtime behavior, and rebuild parity remain unproven.

### CRadarWarningReceiver__Update

| Property | Value |
|----------|-------|
| Address | `0x004d66b0` |
| Signature | `void __fastcall CRadarWarningReceiver__Update(void * this)` |
| Debug Reference | Line 0x41 (65) in RadarWarningReceiver.cpp |

Wave488 hardens this existing function's signature/comment/tags. Static read-back shows the main update loop scans for threats:

1. **Reset threat tracking**: Clears all threat valid flags
2. **Scan for threats**: Iterates through potential targets:
   - Calculates distance using `SQRT(dx^2 + dy^2 + dz^2)`
   - Filters by range (`mRange` at +0x14)
   - Filters by owner match (target's +0xe8 == this->+0x08)
   - Checks threat is active (target's weapon system +0x1c > 0)
3. **Calculate bearing**: Uses `atan2(dx, dz)` to get direction to threat
4. **Update or create threat entry**:
   - If existing: update bearing and distance
   - If new: allocate 24-byte struct, populate fields, add to list
5. **Check if threat is forward**: For player entities (flag +0x34 & 8):
   - Compares threat bearing to player heading (+0x114)
   - Handles angle wraparound at +/- PI
   - If within 45 degrees (PI/4), sets "threat ahead" flag (+0x5e4)
6. **Schedule next update**: Via sound system with ID 4000
7. **New threat alert**: If threat count increased:
   - Sets new-threat flag
   - Plays alert sound (ID 0xFA2 = 4002)
8. **Cleanup stale threats**: Removes entries not updated this frame

### CRadarWarningReceiver__dtor

| Property | Value |
|----------|-------|
| Address | `0x004d6600` |
| Signature | `void __fastcall CRadarWarningReceiver__dtor(void * this)` |

Wave488 hardens this destructor body:
- Sets vtable pointer
- Iterates through the tracked threat list around `this+0x1c/this+0x24`
- Calls `CGenericActiveReader__dtor(entry+0x0c)` and frees each entry through `CDXMemoryManager__Free(&DAT_009c3df0, entry)`
- Clears CSPtrSet collections
- Calls `CMonitor__Shutdown`

### CRadarWarningReceiver__scalar_deleting_dtor

| Property | Value |
|----------|-------|
| Address | `0x00405a20` |
| Signature | `void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void * this, byte flags)` |

Wave488 refreshes this MSVC scalar deleting destructor wrapper's comment/tags:
- Calls `CRadarWarningReceiver__dtor`
- If `flags & 1`, frees `this` through `CDXMemoryManager__Free(&DAT_009c3df0, this)`
- Returns `this`

### CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000

| Property | Value |
|----------|-------|
| Address | `0x004d6a10` |
| Signature | `void __thiscall CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000(void * this, void * message)` |
| Size | 5 instructions (ends at `0x004d6a22`) |

Wave488 created the missing Ghidra function boundary for the vtable slot-0 callback:
```asm
MOV EAX, [ESP+4]        ; Get message parameter
CMP WORD PTR [EAX+4], 0x0FA0  ; Check if sound ID == 4000
JNZ skip
CALL CRadarWarningReceiver__Update
skip:
RET 4
```

It only calls `CRadarWarningReceiver__Update` when triggered by event ID 4000 (0x0FA0), preserving the ECX receiver.

## Sound IDs

| ID | Hex | Purpose |
|----|-----|---------|
| 4000 | 0x0FA0 | RWR update timer (scheduled callback) |
| 4002 | 0x0FA2 | New threat detected alert |

## Math Constants

| Value | Meaning |
|-------|---------|
| 1.5707964 | PI/2 (90 degrees) |
| 3.1415927 | PI (180 degrees) |
| 6.2831855 | 2*PI (360 degrees) |
| 0.7853982 | PI/4 (45 degrees) - threat "ahead" threshold |

## Integration Points

- **CBattleEngine**: Owns RWR instance, calls Init during battle setup
- **Sound System**: Used for scheduling updates (callback mechanism)
- **Player Entity**: RWR checks player flags and sets threat-ahead indicator
- **HUD**: Likely reads mThreats list to display threat indicators

## Summary Table

| Function | Address | Type |
|----------|---------|------|
| `CRadarWarningReceiver__Init` | `0x004d65a0` | Member |
| `CRadarWarningReceiver__Update` | `0x004d66b0` | Member |
| `VFuncSlot_03_0044a830` | `0x0044a830` | Shared inherited slot, owner deferred |
| `CRadarWarningReceiver__dtor` | `0x004d6600` | Destructor |
| `CRadarWarningReceiver__scalar_deleting_dtor` | `0x00405a20` | Destructor wrapper |
| `CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000` | `0x004d6a10` | Virtual slot 0 callback, created in Wave488 |

**Total: 5 named CRadarWarningReceiver functions plus shared inherited slot `0x0044a830`**

## Wave488 Evidence Boundary

Wave488 is static retail-binary evidence only. It verified dry/apply/read-back logs, metadata, tags, decompile, xrefs, instructions, vtable slot read-back, focused probe, queue refresh, and a verified Ghidra project backup. It does not prove the exact original source body, concrete class/threat-entry layouts beyond observed offsets, runtime HUD/audio scheduling behavior, full vtable ownership, BEA launch behavior, game patching, or rebuild parity.
