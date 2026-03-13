# Tech Slots Investigation

> Dedicated investigation of the tech slot system at offset **0x2408** (CORRECTED Dec 2025)

## What We Know

| Property | Value |
|----------|-------|
| Offset | **0x2408** (CORRECTED - was 0x244C) |
| Size | 128 bytes (32 slots × 4 bytes) |
| Purpose | Bit-fields for mission branching, progression flags |
| Confidence | **85%** |

## Struct Layout (CONFIRMED Dec 2025)

```c
// From Career.h
#define MAX_CAREER_SLOTS 32

// 32 integers at 0x2408-0x2487, each storing 32 bits = 1024 total slots
uint32_t mSlots[MAX_CAREER_SLOTS];  // 0x2408 - 0x2487

// Bit addressing (standard bit manipulation, NOT shift-16):
// To set slot N: mSlots[N >> 5] |= (1 << (N & 31))
// To test slot N: (mSlots[N >> 5] & (1 << (N & 31))) != 0
```

## Gold Save Analysis (Dec 2025)

| mSlots Index | File Offset | Raw Value | Active Bits |
|--------------|-------------|-----------|-------------|
| mSlots[0] | 0x2408 | 0x08000000 | Bit 27 → Slot 27 |
| mSlots[1] | 0x240C | 0x01000000 | Bit 24 → Slot 56 |
| mSlots[2] | 0x2410 | 0x0007C000 | Bits 14-18 → Slots 78-82 |

## Known Slot Meanings (from Career.cpp)

| Slot | Name | Purpose |
|------|------|---------|
| 61 | `SLOT_500_ROCKET` | Mission 500: took higher/rocket path |
| 62 | `SLOT_500_SUB` | Mission 500: took lower/submarine path |
| 27 | Unknown | Set in gold save (mSlots[0] bit 27) |
| 56 | Unknown | Set in gold save (mSlots[1] bit 24) |
| 78-82 | Unknown | Set in gold save (mSlots[2] bits 14-18) |

**CRITICAL NOTE**: Offset 0x240C was previously misidentified as "god mode". It's actually mSlots[1], the second element of this tech slots array!

## Action Items

### Investigation

1. [ ] Diff saves before/after unlocking specific weapons
2. [ ] Map which bits correspond to which unlocks
3. [ ] Test in-game effects of setting unknown bits
4. [ ] Cross-reference with FEPGoodies.cpp for tech-related goodies

### Implementation

1. [ ] Add UI controls to editor for individual slot toggles
2. [ ] Add `--tech-slot N:BIT` CLI option
3. [ ] Add tech slot display to `--analyze` output
4. [ ] Add tech slot viewer showing all 32 bits per slot

## Related Analyzer Feature

From analyzer-enhancements.md:

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Tech slot bit viewer** | Show all 32 bits per slot with known bit meanings | Medium | Medium |

## Cross-References

- **Known unknowns**: Tech slot bitmap semantics remain partially unresolved and are tracked here alongside the canonical save-format docs.
- **Save format**: [../reverse-engineering/save-file/save-format.md](../reverse-engineering/save-file/save-format.md)
- **Source code**: `references/Onslaught/Career.h` defines MAX_CAREER_SLOTS

---

*Priority 2 investigation item*
