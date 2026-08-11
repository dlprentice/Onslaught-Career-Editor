# PC demo versus PC retail

Status: active, measured cross-build evidence
Last updated: 2026-08-11
Evidence: MEASURED — exact executable/archive hashes, independently recounted
MSVC RTTI/vtables, and a 2,127-target instruction census; UNKNOWN — normalized
constant values, non-virtual functions outside the pairing, runtime behavior,
and the four incompletely bounded demo bodies listed below.
Verdict: the PC demo is a distinct build with a structurally identical virtual
class surface; 2,123 of 2,127 paired virtual targets retain the same normalized
instruction encoding shape, while four frontend/FMV targets are demonstrably
different in the bounded comparison.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`

## Specimens

| Role | Bytes | SHA-256 |
| --- | ---: | --- |
| Pristine PC retail `BEA.exe` | 2,506,752 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| PC demo `BEA.exe` | 2,510,848 | `d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2` |
| PC demo ZIP | 110,691,112 | `62e3f54a25af8049491c96123409f7ee6cc02d9326f4252d84606ffc136acd47` |
| Retail `All.gip` | 651,614,569 | `b0e6a2266a239c2cd9f0f45071c6e9b5dceb548c989714aad0712e4f353e617d` |
| Demo `All.gip` | 75,388,730 | `90b16dc8df5669bb1ed2dbd09b450c30864047c9a536ecc31bfc6aa55cb66975` |

The demo executable came from the read-only archive
`G:\BEA ROMS\Manually Downloaded\battleengine - 2003 PC DEMO.zip`. The retail
executable is the pristine project baseline and is also reproduced exactly by
the canonical PC disc image. The different executable and data-package hashes
prove that this is not merely the retail build repackaged with fewer files.

The demo PE timestamp is 2003-09-11 and the retail timestamp is 2003-05-26.
Those values are recorded as header facts, not treated as trustworthy release
chronology without corroboration.

## Structural result

The current strict RTTI parser was run independently over both executables. It
reproduced the same counts in each:

| RTTI/vtable item | Retail | Demo |
| --- | ---: | ---: |
| Type descriptors | 667 | 667 |
| Strict vtables / complete object locators | 724 | 724 |
| Classes with vtables | 656 | 656 |
| Vtable slot placements | 11,777 | 11,777 |
| Distinct virtual targets | 2,127 | 2,127 |

The 724 full structural keys are identical as sets. A key incorporates the
RTTI hierarchy/vtable structure rather than an address or a guessed function
name. Pairing each unique key and then each slot ordinal therefore produces a
one-to-one mapping of all 2,127 distinct retail targets to all 2,127 demo
targets.

The mechanical map is
[`binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv`](binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv),
1,204,103 bytes, SHA-256
`ba2db0551beeed458ea6265b87d1a5cf93bc2dd2c464da3f7f0c6702a4d4c750`.
It retains both addresses, the retail body/range and instruction counts,
placement classes, bounded semantic owner, raw and normalized stream hashes,
and the comparison verdict.

## Instruction comparison

Retail body boundaries and instructions came from a read-only Ghidra 12.1.2
export of the exact retail program. Demo instructions were decoded from the
paired entry at the same body-relative offsets. Per instruction, only the
Capstone-reported encoded immediate and displacement spans were zeroed. The
comparison retained instruction offset, size, mnemonic, prefixes, opcode,
ModRM, and SIB shape.

| Result | Count |
| --- | ---: |
| Paired targets | 2,127 |
| Full demo decode and zero normalized differences | 2,123 |
| Bounded divergent comparisons | 4 |
| Retail instructions compared | 127,921 |
| Retail instruction bytes compared | 410,441 |
| Retail body bytes covered | 410,445 |
| Targets with at least one raw-byte difference | 1,625 |

Raw address changes are expected from the build's shifted code and data. The
important result is that 2,123 streams become byte-identical after removing
only those encoded address/displacement fields. This independently
corroborates control and instruction shape across a broad, distinct build. It
does **not** prove that the removed constants point to equivalent objects or
that runtime behavior is identical.

Known high-value pairs include:

| Retail | Demo | Bounded identity |
| --- | --- | --- |
| `0x004D8AE0 CRound::Hit` | `0x004D89C0` | 734 bytes / 228 instructions; zero normalized differences |
| `0x0040A890 CBattleEngine::Damage` | `0x0040A940` | 917 bytes / 233 instructions; zero normalized differences |
| `0x00407350 CBattleEngine::Hit` | `0x004073F0` | 380 bytes / 114 instructions; zero normalized differences |
| `0x004F9A90 CUnit::ApplyDamage` | `0x004F9B50` | 2,586 bytes / 771 instructions; zero normalized differences |
| `0x0044BF10 CExplosion::Hit` | `0x0044BF90` | 479 bytes / 152 instructions; zero normalized differences |

These pairs corroborate the current retail address/body identities; they do
not replace the retail specimen as patch or runtime authority.

## Four retained divergences

The only nonzero normalized comparisons are:

| Retail -> demo | Retail name | Retail body | Normalized differences |
| --- | --- | ---: | ---: |
| `0x004568A0 -> 0x004568C0` | `CFEPDebriefing__ButtonPressed` | 139 B / 47 instructions | 22 instructions / 66 bytes |
| `0x004656E0 -> 0x00465730` | `CFMV__VFunc_3_004656e0` | 41 B / 11 instructions | 11 instructions / 31 bytes |
| `0x0051B840 -> 0x0051BB10` | `CFEPIntro__VFunc_5_0051b840` | 1,577 B / 446 instructions | 257 instructions / 743 bytes |
| `0x0053F190 -> 0x0053F7A0` | `CDXFMV__VFunc_11_0053f190` | 949 B / 267 instructions | 164 instructions / 549 bytes |

All four are marked `full_demo_decode=false`. The demo side is a bounded
fixed-offset comparison, not an independently recovered demo function body.
They are real differences in that window, but their complete demo CFG/body
must be recovered before making a whole-function change claim.

The concentration in debriefing, intro, and FMV/frontend code is a useful
build-lineage signal. It is not evidence that gameplay is globally identical.

## What this changes for the RE campaign

The demo is now an independent refuter and address-translation oracle for the
virtual surface. A retail interpretation that requires a changed opcode,
branch shape, or instruction layout in one of the 2,123 exact pairs must also
explain why the distinct demo build preserves the original shape.

The best next semantic cohort is the bounded `CUnit` owner set: 64 targets,
16,492 retail body bytes, 5,087 instructions, and 1,730 vtable placements.
Forty contain raw address differences across 447 instructions, yet all 64 have
zero normalized differences. That is a coherent place to resolve field and
callee identities using both builds, source, data, and current reconstruction
owners without repeating static-C1 accounting.

## Reproduction and limits

The ignored evidence package is
`local-lab/pc-demo-retail-virtual-target-census-20260811-v1/`. Its sealed
verification receipt is 1,204 bytes, SHA-256
`a1c29ee2aef742207453bd7270c6e9c82c89beb8cf2c404c3e9d4e9b7c17b8a2`,
and reports `PASS` for 2,127 unique pairs, 11,777 placements, 2,123 exact
normalized streams, and four divergences. The exact retail instruction export
has SHA-256
`24e642922231d7429e34d4e04d8b1d944b085ed1fb79917a70b3747593954835`.

Open boundaries remain:

- normalized immediate/displacement values and the objects they address;
- non-instruction bytes in multi-range bodies;
- non-virtual functions outside the strict RTTI pairing;
- independent demo body/CFG recovery for the four divergent targets;
- asset/configuration differences and their behavioral consequences;
- runtime equivalence, source equivalence, and rebuild parity.
