# NvStripifier__FindGoodResetPoint

Status: active static contract; library identity and bounded behavior rechecked
Last updated: 2026-09-26
Summary: Rechecked structural identity and bounded retail behavior of NvStripifier__FindGoodResetPoint; the former game-class attribution is superseded.
Evidence: MEASURED — pristine instructions, body digest and callers; SOURCE — structural comparison with pinned reference material; UNKNOWN — complete retail runtime equivalence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0056fdc0`

## Identity and evidence

The saved contiguous body is `[0x0056fdc0,0x0056fe6f)`,
175 bytes, freshly compared with the pristine specimen:
SHA-256 `a163ee2e20c9ee8f291b43921c85ce09545e59a6241e703fb5ed5f4997a03f74`.

The pinned later NvTriStrip source identifies `NvStripifier::FindGoodResetPoint(NvFaceInfoVec&, NvEdgeInfoVec&)` at
`NvTriStripObjects.cpp:293`, commit
`c40ad04c7fec77be6af9d4ebc0c64da80241984f`.
The reference is a map to test against retail, not permission to copy its newer
API, data layout or edge behavior. The reviewed metadata change is in the
[NvTriStrip manifest](../../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv).

The former name `CFastVB__SelectNextStripTriangle` and the historical filename are retained as a
cross-reference. This is library code in the strip-generation pipeline, not a
member of the game's `CFastVB` class.

## Re-derived behavior

It uses this+0x1c as a first-reset flag, calls FindStartPoint once and clears the flag. Otherwise or
for index -1 it converts (face count minus one) times meshJump at +0x18 through __ftol, scans
circularly for a negative face strip ID, and advances meshJump; unlike FindStartPoint it returns a
face pointer and updates receiver state.

The body returns with `ret 8`. This bounds callee stack cleanup; it does not
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
`6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 12.
The earlier document remains in Git history; frozen campaign packets and
name tables were not rewritten or promoted by this recheck.
