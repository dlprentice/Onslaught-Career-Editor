# RadarWarningReceiver.cpp

Debug path string: `C:\dev\ONSLAUGHT2\RadarWarningReceiver.cpp` at `0x00631784`

## Overview

The Radar Warning Receiver (RWR) system alerts pilots when they are being targeted by enemy radar or missiles. It provides audio/visual warnings showing the direction and type of threats.

## Class: CRadarWarningReceiver

Inherits from a base class with virtual functions. Member of `CBattleEngine` (initialized during battle setup).

### Vtable

Located at `0x005d8810`:

| Offset | Address | Function |
|--------|---------|----------|
| +0x00 | 0x004d6a10 | ProcessMessage thunk (checks sound ID 0x0FA0, calls Update) |
| +0x04 | 0x00405a20 | `CRadarWarningReceiver__scalar_deleting_dtor` |
| +0x08 | 0x004bacb0 | (inherited) |
| +0x0C | 0x0044a830 | (inherited) |
| +0x10 | 0x0060c5a0 | (inherited) |
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
| +0x0C | float | Source entity pointer |
| +0x10 | float | Creation timestamp |
| +0x14 | int | Status/flags |

## Functions

### CRadarWarningReceiver__Init

| Property | Value |
|----------|-------|
| Address | `0x004d65a0` |
| Signature | `void __thiscall CRadarWarningReceiver__Init(void* owner)` |
| Called From | `CBattleEngine__Init` at `0x00405710` |

Initializes the RWR system:
- Stores owner entity reference
- Copies detection range from owner's config (+0x0C)
- Copies update interval from owner's config (+0x10)
- Schedules first update via sound system (ID 4000)
- Clears new-threat flag and timestamp

### CRadarWarningReceiver__Update

| Property | Value |
|----------|-------|
| Address | `0x004d66b0` |
| Signature | `void __thiscall CRadarWarningReceiver__Update(void)` |
| Debug Reference | Line 0x41 (65) in RadarWarningReceiver.cpp |

Main update loop that scans for threats:

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
| Signature | `void __thiscall CRadarWarningReceiver__dtor(void)` |

Destructor:
- Sets vtable pointer
- Iterates through threat list, freeing each entry
- Clears CSPtrSet collections
- Calls base class cleanup

### CRadarWarningReceiver__scalar_deleting_dtor

| Property | Value |
|----------|-------|
| Address | `0x00405a20` |
| Signature | `void __thiscall CRadarWarningReceiver__scalar_deleting_dtor(byte flags)` |

MSVC scalar deleting destructor wrapper:
- Calls `CRadarWarningReceiver__dtor`
- If `flags & 1`, frees memory via `OID__FreeObject`

### ProcessMessage Thunk (unnamed)

| Property | Value |
|----------|-------|
| Address | `0x004d6a10` |
| Size | 19 bytes (ends at 0x004d6a22) |

Virtual callback thunk:
```asm
MOV EAX, [ESP+4]        ; Get message parameter
CMP WORD PTR [EAX+4], 0x0FA0  ; Check if sound ID == 4000
JNZ skip
CALL CRadarWarningReceiver__Update
skip:
RET 4
```

Only calls Update when triggered by sound ID 4000 (the scheduled update timer).

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
| `CRadarWarningReceiver__dtor` | `0x004d6600` | Destructor |
| `CRadarWarningReceiver__scalar_deleting_dtor` | `0x00405a20` | Destructor wrapper |
| ProcessMessage thunk | `0x004d6a10` | Virtual (not a function in Ghidra) |

**Total: 4 named functions + 1 thunk**
