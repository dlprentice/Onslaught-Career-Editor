# NvStripifier__SplitUpStripsAndOptimize

Status: active static contract; library identity and bounded behavior rechecked
Last updated: 2026-09-26
Summary: Rechecked structural identity and bounded retail behavior of NvStripifier__SplitUpStripsAndOptimize; the former game-class attribution is superseded.
Evidence: MEASURED — pristine instructions, body digest and callers; SOURCE — structural comparison with pinned reference material; UNKNOWN — complete retail runtime equivalence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x005718c0`

## Identity and evidence

The saved contiguous body is `[0x005718c0,0x005721ec)`,
2,348 bytes, freshly compared with the pristine specimen:
SHA-256 `cb086a58f13d6be99e7dcaf5cb2eb5ebf8e70316b3b664182cfa07d0808f51a5`.

The pinned later NvTriStrip source identifies `NvStripifier::SplitUpStripsAndOptimize(NvStripInfoVec&, NvStripInfoVec&, NvEdgeInfoVec&, NvFaceInfoVec&)` at
`NvTriStripObjects.cpp:1191`, commit
`c40ad04c7fec77be6af9d4ebc0c64da80241984f`.
The reference is a map to test against retail, not permission to copy its newer
API, data layout or edge behavior. The reviewed metadata change is in the
[NvTriStrip manifest](../../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv).

The former name `CFastVB__MergeAndOrderStripBatches` and the historical filename are retained as a
cross-reference. This is library code in the strip-generation pipeline, not a
member of the game's `CFastVB` class.

## Re-derived behavior

It counts nondegenerate faces and uses signed division by this+0x10 at 0x00571992 to split strips.
Remainders one through three join the last full chunk (0x00571b25-0x00571b34). After
RemoveSmallStrips at 0x00571dd1 it selects by neighbor count per face, then cache hits with winding
preference for ties; +0x24 records visited strips. The later source's m_bIsFake member and its
associated cleanup must not be assumed for retail.

The body returns with `ret 16`. This bounds callee stack cleanup; it does not
by itself recover the original C++ declaration or all argument types.

## Limits and retained evidence

This recheck establishes the identity and observations stated above. It does
not certify the existing Ghidra prototype, full source equivalence, malformed
mesh handling, allocation failures or observed rendering. The next behavioral
falsifier is an isolated call of these pristine instructions using the named
input structures and boundary cases, recording returns and memory writes.
Player and GPU acceptance remain separate.

The August factory draft's label and quoted analyst interpretation are
superseded here. Its frozen cohort-11 receipt remains unchanged: manifest
`6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 20.
The earlier document remains in Git history; frozen campaign packets and
name tables were not rewritten or promoted by this recheck.
