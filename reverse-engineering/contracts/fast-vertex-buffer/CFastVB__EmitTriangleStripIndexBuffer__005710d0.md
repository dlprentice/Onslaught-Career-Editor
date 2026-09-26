# NvStripifier__CreateStrips

Status: active static contract; library identity and bounded behavior rechecked
Last updated: 2026-09-26
Summary: Emits strip indices with winding correction, optional stitching and -1 separators; retail takes four explicit arguments.
Evidence: MEASURED — pristine instructions, body digest and callers; SOURCE — structural comparison with pinned reference material; UNKNOWN — complete retail runtime equivalence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x005710d0`

## Identity and evidence

The saved contiguous body is `[0x005710d0,0x005715a2)`,
1,234 bytes, freshly compared with the pristine specimen:
SHA-256 `97211dfbc1abc81ca1e41433cdc2d49019ffdc2c5a73ba235b3559d20c5f09e4`.

The pinned later NvTriStrip source identifies `NvStripifier::CreateStrips` at
`NvTriStripObjects.cpp:961`, commit
`c40ad04c7fec77be6af9d4ebc0c64da80241984f`.
That source declaration has six arguments, including `bRestart` and
`restartVal`; retail has the four-argument interface described below.
The reference is a map to test against retail, not permission to copy its newer
API, data layout or edge behavior. The reviewed metadata change is in the
[NvTriStrip manifest](../../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv).

The former name `CFastVB__EmitTriangleStripIndexBuffer` and the historical filename are retained as a
cross-reference. This is library code in the strip-generation pipeline, not a
member of the game's `CFastVB` class.

## Re-derived behavior

It reorders the initial face using unique/shared vertices (0x0057119e/0x00571203), corrects winding
through NextIsCW and IsCW, then emits later unique vertices or degenerate-face indices. Unstitched
output appends -1 and increments the fourth argument's separate-strip count at
0x0057155e/0x0057155f; stitched exit writes one at 0x00571596. The newer restart arguments/path are
absent.

It pops 16 bytes: four parameters, where the pinned source's CreateStrips has six (bRestart and restartVal were added later; the game's API block has no EnableRestart or DisableRestart).

## Limits and retained evidence

This recheck establishes the identity and observations stated above. It does
not certify the existing Ghidra prototype, full source equivalence, malformed
mesh handling, allocation failures or observed rendering. The next behavioral
falsifier is an isolated call of these pristine instructions using the named
input structures and boundary cases, recording returns and memory writes.
Player and GPU acceptance remain separate.

The August factory draft's label and quoted analyst interpretation are
superseded here. Its frozen cohort-11 receipt remains unchanged: manifest
`6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 18.
The earlier document remains in Git history; frozen campaign packets and
name tables were not rewritten or promoted by this recheck.
