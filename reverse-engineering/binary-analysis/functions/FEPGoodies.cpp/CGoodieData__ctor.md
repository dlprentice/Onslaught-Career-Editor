# CGoodieData__ctor

> Address: `0x0045c770`
> Source: `references/Onslaught/FEPGoodies.cpp`

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
void CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)
```

## Behavior

- Writes 6 consecutive fields on the destination object:
  - `Method`
  - `Method2`
  - `Number`
  - `Number2`
  - `mT1`
  - `mT2`
- This matches the constructor body for `CGoodieData` in source.

## Notes

- Called repeatedly by the static goodie-table builder path (`CFEPGoodies__BuildStaticGoodieDataTable`) to materialize entries.

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `void __thiscall CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)`.
- Saved function comment now records the six 4-byte field writes as static/source-parity evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `goodie-data-table`, `goodie-record`, `retail-binary-evidence`, and `comment-hardened`.
- Instruction/decompile read-back includes writes through `this + 0x00`, `+0x04`, `+0x08`, `+0x0c`, `+0x10`, and `+0x14`, followed by `RET 0x18`.
- This does not prove concrete enum names, a fully typed structure definition, or rebuild parity.
