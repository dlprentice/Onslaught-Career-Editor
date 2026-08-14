# Text-gap 31-function library classification

Date: 2026-08-13

Status: reviewed semantic classification; exact structural admission completed
separately on 2026-08-14, while provider-qualified Ghidra metadata remains
unpromoted.

Verdict: **SUPPORTED AS BOUNDED PROVIDER-EQUIVALENT IDENTITIES; STRUCTURAL
ADMISSION IS COMPLETE AND PROVIDER METADATA REMAINS SEPARATE.** The 31 exact boundary
candidates prepared in
[`text-gap-missing-function-boundaries-2026-08-13.tsv`](text-gap-missing-function-boundaries-2026-08-13.tsv)
classify as 14 Microsoft CRT Pentium-FDIV helpers, 14 AMD 3DNow math
primitives, and three Independent JPEG Group 6b inverse-DCT routines. None is
a newly inferred game-semantic function.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The PC demo comparison specimen is 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

Evidence: **MEASURED** — the exact 31-row preparation manifest is 14,930 bytes,
SHA-256
`afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586`.
The machine-local classification report is
`local-lab/text-gap-semantic-classification-20260813-v1/REPORT.md`, 13,882
bytes, SHA-256
`3266a5d678373bbc90af7af217bff14cdee999f51279ac6c63ee0e44e5a7200f`.
An independent replay reproduced every retail body hash and instruction count,
all 31 normalized PC-demo twins, every provider identity below, zero overlap
with the then-current 8,170-function inventory, and zero collision with the
1,863-row PC source-coordinate corpus.

The later, separately backed-up
[`live-promotion ceremony`](text-gap-missing-function-ghidra-live-promotion-2026-08-14.md)
admitted these exact 31 bodies and advanced the saved census to 8,201 while
preserving every exported field of all 8,170 PRE function rows. The new rows
still carry default `FUN_*` names. This classification owner did not perform
that mutation and does not promote its provider-qualified labels into Ghidra.

The corresponding 31-row naming ledger is
[`text-gap-library-function-classification-2026-08-13.tsv`](text-gap-library-function-classification-2026-08-13.tsv).
It joins the immutable structural preparation by candidate ID and retail entry;
the preparation manifest remains the owner of ranges, bytes, instruction
counts, demo deltas, and body hashes.

## Provider joins

### Microsoft CRT FDIV package

CF-001 through CF-014 match the Pentium FDIV-workaround package in
`C:\Windows\SysWOW64\msvcrt.dll` version 7.0.26100.8875, 809,504 bytes,
SHA-256
`d72870f695fc49e1cb9f4fc3f45e202a7effa26474067b0e328ce31affd4a437`.
Twelve bodies are raw-exact and two dispatcher bodies are
address-normalized-exact. A 1,191,936-byte Microsoft Symbol Server PDB,
SHA-256
`21336d11aac1227df7d04ffcc4daf7b533b8a3553e21e9214fee4a16f5d44d2d`,
has the matching GUID and an aligned public-symbol layout that resolves all 14
entries. Its internal PDB age is 3 while the DLL RSDS age is 1, so this is an
aligned symbol-server reference, **not** an exact GUID-and-age PDB identity.

### AMD 3DNow math package

CF-015 through CF-028 match AMD's 1999 `Asdk/imath.cpp` at source commit
`1f4223a77122220d28e8670788b3f9fd6bb2c4d1`, Git blob
`77fa2b677fdca04567a8a37d94730b69da4b3018`, 58,188 bytes, SHA-256
`d5ef8363477ad19ce8efa1dca5bc3a51f851cd1b36e91dd94149b23d846529cc`.
The source names, function order, register ABI, internal `a_log10` to `a_log`
call, instruction shapes, and shared constant pool agree. This is a bounded
source-semantic identity, not a claim of a byte-identical rebuild from an
unknown compiler command line. In particular, the retail `a_fmod` variant's
zero-divisor behavior remains outside the proved contract.

### Independent JPEG Group 6b

CF-029 through CF-031 match `jpeg_idct_float`, `jpeg_idct_ifast`, and
`jpeg_idct_islow` from official IJG archive `jpegsrc.v6b.tar.gz`, 613,261
bytes, SHA-256
`75c3ec241e9996504fe02a9ed4d12f16b74ade713972f3db9e65ce95cd27e35d`.
The retail image embeds the IJG 6b version string. The inverse-DCT manager at
`0x005AE1F0` installs the three candidates in IJG's selector order—slow,
fast, float—and the raw-quantization, AA&N fixed, and AA&N float algorithms
agree with the pinned 6b sources.

## Claim boundary

The separate structural admission gate has now reproduced exact boundaries,
bytes, demo-normalized equality, and non-collateral behavior. The ledger's
provider-qualified labels therefore remain safe metadata candidates, not
original-symbol claims. This report itself:

- creates no function and changes no Ghidra metadata or current census;
- does not claim that the proposed labels were original BEA linker symbols;
- does not attribute the routines to a BEA class or source file;
- does not prove runtime execution, necessity, or every numeric corner case;
- does not create a gameplay or Godot reconstruction contract.

Any conflicting provider symbol at an exact aligned entry, body mismatch,
selector mismatch, or later collateral evidence falsifies the affected row.
After the separate structural admission, every ledger row is
`STRUCTURALLY_ADMITTED_PROVIDER_CLASSIFIED_METADATA_UNPROMOTED`.
