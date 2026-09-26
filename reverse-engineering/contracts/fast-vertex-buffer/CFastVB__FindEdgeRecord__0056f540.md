# NvStripifier__FindEdgeInfo

Status: active static contract; library identity and bounded behavior rechecked
Last updated: 2026-09-26
Summary: Rechecked structural identity and bounded retail behavior of NvStripifier__FindEdgeInfo; the former game-class attribution is superseded.
Evidence: MEASURED — pristine instructions, body digest and callers; SOURCE — structural comparison with pinned reference material; UNKNOWN — complete retail runtime equivalence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0056f540`

## Identity and evidence

The saved contiguous body is `[0x0056f540,0x0056f577)`,
55 bytes, freshly compared with the pristine specimen:
SHA-256 `34122db1aaa9d2c2aecbbbdc442d5c28f48eb378b1f3b099073f2bfcf2149f60`.

The pinned later NvTriStrip source identifies `NvStripifier::FindEdgeInfo(NvEdgeInfoVec&, int, int)` at
`NvTriStripObjects.cpp:29`, commit
`c40ad04c7fec77be6af9d4ebc0c64da80241984f`.
The reference is a map to test against retail, not permission to copy its newer
API, data layout or edge behavior. The reviewed metadata change is in the
[NvTriStrip manifest](../../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv).

The former name `CFastVB__FindEdgeRecord` and the historical filename are retained as a
cross-reference. This is library code in the strip-generation pipeline, not a
member of the game's `CFastVB` class.

## Re-derived behavior

It indexes the edge vector by v0, compares endpoints at +0xc/+0x10, and walks nextV0 (+0x14) or
nextV1 (+0x18) according to the matching endpoint; EAX returns edge or null. Three stack arguments
and plain ret distinguish it from the four-argument face query.

A plain `ret` does not independently establish cdecl arity, return type or receiver ownership.
The observed operations and callers above supply the stated parameter/return meaning.

## Limits and retained evidence

This recheck establishes the identity and observations stated above. It does
not certify the existing Ghidra prototype, full source equivalence, malformed
mesh handling, allocation failures or observed rendering. The next behavioral
falsifier is an isolated call of these pristine instructions using the named
input structures and boundary cases, recording returns and memory writes.
Player and GPU acceptance remain separate.

The August factory draft's label and quoted analyst interpretation are
superseded here. Its frozen cohort-11 receipt remains unchanged: manifest
`6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 8.
The earlier document remains in Git history; frozen campaign packets and
name tables were not rewritten or promoted by this recheck.
