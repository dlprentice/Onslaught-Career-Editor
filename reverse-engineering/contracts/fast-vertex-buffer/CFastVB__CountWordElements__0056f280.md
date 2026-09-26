# std__vector_2byte__size

Status: active static contract; library identity and bounded behavior rechecked
Last updated: 2026-09-26
Summary: Rechecked structural identity and bounded retail behavior of std__vector_2byte__size; the former game-class attribution is superseded.
Evidence: MEASURED — pristine instructions, body digest and callers; SOURCE — structural comparison with pinned reference material; UNKNOWN — complete retail runtime equivalence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0056f280`

## Identity and evidence

The saved contiguous body is `[0x0056f280,0x0056f292)`,
18 bytes, freshly compared with the pristine specimen:
SHA-256 `234fbd720bc45562e2fa07d10ed2a776a72b5421f0cb73178b1cdf4299afa037`.

The private pinned VC6 `VECTOR` header supports the `std::vector<T>::size() for a two-byte T` algorithm role;
the element width is proven here, not the exact C++ template type.
The reference is a map to test against retail, not permission to copy its newer
API, data layout or edge behavior. The reviewed metadata change is in the
[NvTriStrip manifest](../../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv).

The former name `CFastVB__CountWordElements` and the historical filename are retained as a
cross-reference. This is library code in the strip-generation pipeline, not a
member of the game's `CFastVB` class.

## Re-derived behavior

It returns (_Last - _First) >> 1, or 0 when _First is null. Retail index consumers use words, but
the pinned source defines WordVec through long WORD; this helper alone proves width, not the
signedness or exact C++ type.

Only the observed two-byte vector operation is claimed; equivalent optimized wrappers may share it.

## Limits and retained evidence

This recheck establishes the identity and observations stated above. It does
not certify the existing Ghidra prototype, full source equivalence, malformed
mesh handling, allocation failures or observed rendering. The next behavioral
falsifier is an isolated call of these pristine instructions using the named
input structures and boundary cases, recording returns and memory writes.
Player and GPU acceptance remain separate.

The August factory draft's label and quoted analyst interpretation are
superseded here. Its frozen cohort-11 receipt remains unchanged: manifest
`6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 6.
The earlier document remains in Git history; frozen campaign packets and
name tables were not rewritten or promoted by this recheck.
