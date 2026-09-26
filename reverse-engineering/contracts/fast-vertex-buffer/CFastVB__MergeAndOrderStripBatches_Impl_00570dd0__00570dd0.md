# NvStripifier__RemoveSmallStrips

Status: active static contract; library identity and bounded behavior rechecked
Last updated: 2026-09-26
Summary: Partitions small strips and orders their faces by cache hits; retail also allocates its temporary cache for an empty face list.
Evidence: MEASURED — pristine instructions, body digest and callers; SOURCE — structural comparison with pinned reference material; UNKNOWN — complete retail runtime equivalence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x00570dd0`

## Identity and evidence

The saved contiguous body is `[0x00570dd0,0x0057105e)`,
654 bytes, freshly compared with the pristine specimen:
SHA-256 `184005eabfbcf4cd2bf0dc87a5dd3c2caf378bd23a939c919353af30595a6294`.

The pinned later NvTriStrip source identifies `NvStripifier::RemoveSmallStrips(NvStripInfoVec&, NvStripInfoVec&, NvFaceInfoVec&)` at
`NvTriStripObjects.cpp:844`, commit
`c40ad04c7fec77be6af9d4ebc0c64da80241984f`.
The reference is a map to test against retail, not permission to copy its newer
API, data layout or edge behavior. The reviewed metadata change is in the
[NvTriStrip manifest](../../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv).

The former name `CFastVB__MergeAndOrderStripBatches_Impl_00570dd0` and the historical filename are retained as a
cross-reference. This is library code in the strip-generation pipeline, not a
member of the game's `CFastVB` class.

## Re-derived behavior

It partitions strips by the unsigned face-count comparison with this+0x14 at 0x00570e71/0x00570e74,
moves short-strip faces to a temporary vector and deletes the short strips. It greedily chooses
unvisited faces by integer cache-hit maximum at 0x00570fa5-0x00570fc7, updates the cache, then
appends. Unlike the source's nonempty guard (line 866), retail allocates visited storage at
0x00570ef5 and the cache at 0x00570f2a/0x00570f53 even for an empty temporary face vector; the empty
scan then terminates at best=-1.

The body returns with `ret 12`. This bounds callee stack cleanup; it does not
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
`6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 17.
The earlier document remains in Git history; frozen campaign packets and
name tables were not rewritten or promoted by this recheck.
