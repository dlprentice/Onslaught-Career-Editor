# Modification Features

> Goal: Surgical precision - modify exactly what you want, nothing more.

## Individual Node Editing

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--edit-node N:FIELD:VALUE`** | Edit any field in node N by name | High | Medium |
| **Interactive node editor** | TUI for browsing and editing individual nodes | Low | High |
| **Node state presets** | `--node-preset N:completed`, `--node-preset N:fresh`, `--node-preset N:locked` | Medium | Low |
| **mNumAttempts control** | Set attempt count per node (affects some goodies) | Low | Low |
| **mWorldNumber override** | Reassign node to different level ID (experimental) | Low | Medium |

**Supported node fields for `--edit-node`:**
```
State, mComplete, mLowerLink, mHigherLink, mWorldNumber,
mBaseThingsExists[0-8], mNumAttempts, mRanking
```

## Individual Link Editing

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--edit-link N:complete`** | Mark specific link N as complete | Medium | Low |
| **`--edit-link N:incomplete`** | Mark specific link N as incomplete | Medium | Low |
| **`--edit-link N:target:M`** | Change link target node (mToNode) | Low | Low |
| **Link batch by node** | `--unlock-links-from N` to complete all links originating from node N | Medium | Medium |
| **Link dependency viewer** | Show which links must complete for which levels | Low | Medium |

## Individual Goodie Editing

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--goodie N:state`** | Set specific goodie state (LOCKED/NEW/OLD/INSTRUCTION) | High | Low |
| **`--goodie-range N-M:state`** | Bulk set goodie range (e.g., character bios 1-7) | Medium | Low |
| **Goodie chain validation** | Warn if patching goodies out of order (bios require sequential) | Medium | Medium |
| **Lower-bits preservation toggle** | `--preserve-goodie-bits` / `--clear-goodie-bits` | Low | Low |
| **Goodie name lookup** | Map goodie numbers to names from FEPGoodies.cpp | Medium | High |

**Goodie states:**
```
True dword view (authoritative):
0 = LOCKED       (0x00000000)
1 = INSTRUCTION  (0x00000001) - rarely used
2 = NEW          (0x00000002) - gold badge
3 = OLD          (0x00000003) - blue badge

Legacy 4-byte-aligned view (deprecated): the same bytes can appear as 0x00010000, 0x00020000, 0x00030000 due to 2-byte misalignment.
```

## Per-Field Hex Editing with Validation

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--raw-write OFFSET:VALUE`** | Write raw 32-bit value at offset with bounds checking | Medium | Low |
| **`--raw-write-bytes OFFSET:HEX`** | Write raw bytes (e.g., `--raw-write-bytes 0x240C:01000000`) | Medium | Low |
| **Offset validation** | Warn if writing to reserved/unmapped regions, prevent version-stamp overwrites | High | Low |
| **Legacy aligned-view helper** | Show how a true-view value appears in the legacy 4-byte aligned view (for debugging old notes) | Low | Low |
| **Float encoder** | `--encode-float 0.6` outputs `0x3F19999A (State: 0x3F19, mRanking: 0x999A)` | Low | Low |

## mBaseThingsExists Bit Manipulation

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--set-objective N:BIT`** | Set specific objective bit in mBaseThingsExists[N] | Medium | Medium |
| **`--clear-objective N:BIT`** | Clear specific objective bit | Medium | Low |
| **Objective preset files** | Load objective configurations from JSON/YAML | Low | High |
| **Cross-reference source** | Map known bits to objective names from level data | Low | Very High |
| **Bit pattern search** | Find saves with specific objective patterns | Low | Medium |

---

*See [../reverse-engineering/save-file/save-format.md](../reverse-engineering/save-file/save-format.md) for struct layouts*
