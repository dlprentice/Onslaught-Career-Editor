# CFEPGoodies__BuildStaticGoodieDataTable

> Address: `0x0045ac30`
> Source: `references/Onslaught/FEPGoodies.cpp` (behavior/source-parity match)

## Status
- Named in Ghidra: Yes
- Signature set: Yes (`void CFEPGoodies__BuildStaticGoodieDataTable(void)`)
- Verified vs source: Yes (table-construction behavior)

## Behavior

- Writes a large contiguous global table of goody metadata records.
- Repeatedly emits 6-field entry payloads that match `CGoodieData` layout:
  - `Method`
  - `Method2`
  - `Number`
  - `Number2`
  - `mT1`
  - `mT2`
- Values include sentinel `-1` fields and per-entry type/count constants, matching a static initializer pass rather than per-frame runtime logic.

## Evidence

- Decompile at `0x0045ac30` is a bulk global initializer with repeated fixed-pattern writes.
- `CGoodieData__ctor` docs already identified this call path as the static builder (`CGoodieData__ctor.md` note).
- No gameplay-side callers; this is setup/materialization logic for goodies metadata.

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved name/signature preserved as `void CFEPGoodies__BuildStaticGoodieDataTable(void)`.
- Saved function comment now records the table-materialization claim as static/source-parity evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `goodie-data-table`, `retail-binary-evidence`, and `comment-hardened`.
- Instruction/decompile read-back includes the contiguous global table writes and `CGoodieData__ctor` call evidence.
- This does not prove runtime unlock/display behavior, exact table ownership/layout, or rebuild parity.

## Notes

- This function was previously weak-named as `CFrontEnd__Unk_0045ac30` and promoted in headless semantic wave9 (2026-02-26).
