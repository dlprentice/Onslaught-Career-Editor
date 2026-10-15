# CCareerNode__SetBaseThingExistTo

> Address: `0x0041b770`
>
> Source: `references/Onslaught/Career.cpp` (`CCareerNode::SetBaseThingExistTo(int, BOOL)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Set/clear one of the 288 “base thing exists” persistence bits for a node (`mBaseThingsExists[9]`).

## Signature
```c
// val: TRUE => set bit, FALSE => clear bit
void CCareerNode::SetBaseThingExistTo(int offset, int val);
```

## Algorithm (Source-Parity)
```c
int i = offset >> 5;
int b = offset & 31;
uint32_t m = 1u << b;

if (val) mBaseThingsExists[i] |= m;
else     mBaseThingsExists[i] &= ~m;
```

## Notes
- In the retail node layout, `mBaseThingsExists[]` begins at node offset `+0x14` and spans 9 dwords (36 bytes).
- This is not a “node state” bitfield; it is objective/object persistence tracking carried forward between missions.

## Related Functions
- [CCareerNode__Blank](CCareerNode__Blank.md) - Initializes `mBaseThingsExists[]` to all 1s
- [CCareer__DoesBaseThingExist](CCareer__DoesBaseThingExist.md) - Queries these bits by world number + offset
