# CCareer__NodeArrayAt

> Address: `0x00421970`
>
> Source parity: compiler-emitted pointer-arithmetic helper used inside `CCareer__UpdateGoodieStates`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Partially (see note)
- **Verified vs Source:** Behavioral mapping verified from disassembly callsite (`0x0041dd3b`)

## Current Signature (Read-Back)
```c
void * CCareer__NodeArrayAt(void * this, void * node_base, int node_index);
```

## Disassembly Semantics
```asm
MOV EAX, [ESP+4]     ; node_index
SHL EAX, 6           ; * 0x40
ADD EAX, ECX         ; + node_base (passed in ECX)
RET 4
```

Effective behavior:
- Returns `node_base + node_index * 0x40` (no bounds check).
- In `CCareer__UpdateGoodieStates`, callsite sets `ECX = 0x00660624` (`&CAREER.mNode[0]`) and pushes a node index before call.

## Notes
- This helper is an internal array-index primitive used in one callsite (`CCareer__UpdateGoodieStates`).
- Signature cleanup is pending: one normalization PATCH timed out, so the current prototype retains an extra parsed parameter in metadata.

## Related
- [CCareer__GetNode](CCareer__GetNode.md)
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md)
