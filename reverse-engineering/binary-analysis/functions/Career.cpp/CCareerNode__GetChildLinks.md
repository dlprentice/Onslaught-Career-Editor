# CCareerNode__GetChildLinks

> Source File: references/Onslaught/Career.cpp | Binary: BEA.exe (pristine specimen identified above)

Status: active — retail body rechecked; full career execution remains open
Last updated: 2026-09-27
Summary: child-link return construction uses a null-terminated item traversal, not a two-item copy.

Address: `0x0041b940`. Specimen:
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The complete `[0041b940,0041b9e6)` body is 166 bytes, SHA-256
`2dc1be9d609ef23fc90bcbcbdc6ffbd7d3eab6278d851cf3d9a6d2f5cedd27bf`.
Pinned source: `references/Onslaught/Career.cpp:268-273`, commit `5352a81c`.

## September 27 correction

The earlier description said the function appends both pointers and returns the
set. That omitted a consequential copy step. Direct instruction inspection shows:

1. Call `004e5840` to construct a temporary list.
2. Read the lower/higher indices at receiver `+0x08/+0x0c`. Negative indices
   become null; otherwise compute `00661f24 + index*8`. This body has no upper
   index check. Calls `0041b98b` and `0041b9a7` append both values, lower first.
3. At `0041b9b7`, copy the temporary into caller-supplied result storage through
   `004e5850`. That copy stops at the first null **item**, as well as a null node.
4. At `0041b9cd`, return the temporary nodes to the free pool through `004e5c60`.
   EAX returns the result-storage pointer, and normal return removes four stack bytes.

For valid backing pointers and pool state, the normal-path composition is:

| Temporary items | Returned items |
| --- | --- |
| lower, higher | lower, higher |
| lower, null | lower |
| null, higher | empty |
| null, null | empty |

This is a static composition of the complete caller with independently executed
container code. The [original list experiment](../../../../VALIDATION.md#original-pointer-list-operations--september-27)
ran unchanged copy, assignment, Append, Contains and RemoveAll bodies in 42 cases
and two altered-code controls: copy-through-null and search-through-null.
A null-first list copied as empty; a middle null
truncated the copy. It did **not** execute this career caller, Windows exception
handling, a real save or an authored campaign graph.

## Reconstruction and remaining limits

Filtering null values out of both slots would preserve an upper link that retail
normal-path copying discards when the lower slot is negative. Preserve this
ordering/termination rule wherever reproducing the retail career algorithm;
this is not permission to change save bytes or claim that shipped careers contain
that slot combination. The cheapest next falsifier is a complete original
GetChildLinks run on owned node/pool/result memory, followed by a read-only check
of admitted career-node definitions for those combinations.

The conceptual source result is `SPtrSet<CCareerNodeLink>`. The physical hidden
result argument and EAX transport above do not certify every saved Ghidra type,
exception edge, allocator failure or invalid-index behavior. The shared functions
are owned by GenericSPtrSet; concrete template identity is established at this
caller, not assigned exclusively to their shared entry points.

See [GetParentLinks](CCareerNode__GetParentLinks.md) for the consuming traversal.
Private complete body/caller evidence and execution receipts are under
`local-data/test-runs/re-audit-20260926/sptrset/`.
