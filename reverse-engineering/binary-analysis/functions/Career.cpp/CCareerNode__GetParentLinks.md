# CCareerNode__GetParentLinks

> Source File: references/Onslaught/Career.cpp | Binary: BEA.exe (pristine specimen identified above)

Status: active — retail body rechecked; complete graph/runtime acceptance remains open
Last updated: 2026-09-27
Summary: incoming-link enumeration consumes the child-list copy and its null-item termination rule.

Address: `0x0041b9f0`. Specimen:
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The complete `[0041b9f0,0041bb14)` body is 292 bytes, SHA-256
`6670cd46172f9cfca667839fcb5e588daaf641992cb2b90e3ad26102b3b07ed3`.
Pinned source: `references/Onslaught/Career.cpp:278-302`, commit `5352a81c`.

## September 27 body recheck

The normal path constructs a temporary result set at `0041ba1a`, checks the
signed count read from `00624184`, and walks node addresses from `00660624` in
64-byte steps. For each admitted node, call `0041ba54` obtains its
[child-link result](CCareerNode__GetChildLinks.md). That result is already subject
to the copy constructor's null-item stop; it is not simply two outgoing slots.

The inlined traversal at `0041ba59–0041bab4` stops on a null node or null item.
For each link, it reads destination index at link `+0x04`; a negative index
becomes null, otherwise the body computes `00660624 + index*64` with 32-bit
arithmetic. If that pointer equals the original receiver, `0041ba96` appends
this link to the result. The body does not establish an upper-index check.
`0041babf` releases the temporary child-list nodes. It rereads the global count
at `0041bac4` before the next loop comparison.

Finally, `0041bae4` copies the accumulated list into caller-supplied result
storage and `0041bafa` returns its temporary nodes to the free pool. Normal
return places the result pointer in EAX and removes four stack bytes. This
matches the source operation while preserving the retail's physical copy steps.
No saved prototype is promoted by this document recheck.

## Consequences and evidence limits

An upper link preceded by a null lower link can be absent from this traversal
because GetChildLinks already returned an empty copy. This follows from static
caller composition and the [isolated container experiment](../../../../VALIDATION.md#original-pointer-list-operations--september-27),
not a new run of the career graph. The normal control flow preserves enumeration
order and appends matching link pointers without a uniqueness filter.

Freshly decoded ReCalcLinks at `0041bdf0` calls this routine at `0041c0ab`, then
First/Next at `0041c0b9/0041c0d5`, and releases the temporary at `0041c0e7`,
matching `Career.cpp:502-508`. This corroborates the container transport; it
is not a complete revalidation of campaign-completion policy.

The earlier claim about caller `00461a50` inspecting completion types remains
a lead requiring a complete body/caller recheck. This function reads link
`+0x04`; it does not by itself prove the save-file encoding or meanings of link
`+0x00`. Use the save-format evidence owner for those claims. Full original
GetParentLinks execution, dynamic count changes, exceptional exits, malformed
indices and actual campaign topology remain open. The cheapest next falsifier
is an owned original-code graph experiment with the real child-copy path.

Private complete bodies and eleven caller spans:
`local-data/test-runs/re-audit-20260926/sptrset/fresh-evidence-v2.json`.
