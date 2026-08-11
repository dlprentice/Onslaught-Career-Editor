# PC demo versus PC retail

Status: active, measured cross-build evidence
Last updated: 2026-08-11
Evidence: MEASURED — exact executable/archive hashes, independently recounted
MSVC RTTI/vtables, a 2,127-target virtual census, and a conservative 8,086-row
cross-build function-address map; UNKNOWN — normalized constant values, 50
retail functions without a demo address, runtime behavior, and 57 of the 65
address-mapped bodies not shown normalized-identical below.
Verdict: the PC demo is a distinct build with a structurally identical virtual
class surface. Across virtual and non-virtual code, 8,021 of 8,136 retail
functions have a normalized-identical demo body and 65 more have an
independently fixed demo entry but a different or initially incompletely
bounded body. Five startup/FMV and three frontend bodies are now independently
bounded and semantically resolved; 57 remain in that queue.
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

## Whole-function address expansion

The strict vtable pairs are also relocation anchors. A sequence of conservative
passes extended them to ordinary functions without assigning semantics from
proximity alone:

1. A non-virtual body was tried at `retail + delta` only when the nearest lower
   and upper structurally paired functions had the same local delta.
2. Changed-delta intervals were searched for one unique full normalized body
   signature inside their paired-anchor bounds.
3. Short bodies were accepted only when one candidate remained between two
   already accepted neighbors.
4. Corresponding direct `CALL`/`JMP` operands in accepted caller pairs propagated
   another three rounds of callee identities.
5. The expanded anchor set was replayed to convergence across local relocation
   regions and the continuous compiler-unwind suffix.
6. A global call-edge and body-overlap audit refuted three weak short-body
   matches. Unanimous call targets corrected them. Strict RTTI then displaced
   one remaining interior-suffix match for `CFMV__VFunc_3_004656e0`.
7. The one clean compiler-unwind delta transition was decoded on both sides;
   214 additional bodies survived exact instruction-shape comparison, while
   the ambiguous non-unwind transition candidates stayed out.
8. Same-relative `.rdata`/`.data` function pointers were accepted only when a
   36-byte normalized context matched in both images. A final direct-transfer
   replay then reached its fixed point.

The 8,021 normalized-identical rows have unique retail and demo entries. Their
contiguous body-overlap graph is also identical: the sole nested-entry pair is
present on both sides, with no demo-only or retail-only overlap.

The resulting mechanical map is
[`binary-analysis/pc-demo-retail-function-map-2026-08-11.tsv`](binary-analysis/pc-demo-retail-function-map-2026-08-11.tsv),
1,314,885 bytes, SHA-256
`cdb26380bb6b29e82edd601bb95dfc215f62813d925e2f4c4c78452a7af7c68a`.

| Whole-function result | Count |
| --- | ---: |
| Retail functions | 8,136 |
| Independently mapped demo entries | 8,086 |
| Normalized-identical body streams | 8,021 |
| Address mapped, body changed or incompletely bounded | 65 |
| No demo entry yet recovered | 50 |
| Normalized-identical retail body bytes | 1,702,495 |
| Normalized-identical retail instructions | 512,925 |

The 65 address-only/different rows are the four strict-vtable divergences below,
60 entries independently fixed by unanimous corresponding direct transfers,
and one isolated compiler-unwind entry fixed by its equal-delta neighbors.
For example, corresponding direct callers select demo entry `0x004F0110` for
`0x004F00E0 CLTShell__ShutdownRuntimeAndReleaseResources`, while the retail body
matches only a later demo suffix. Address identity and body equivalence are
therefore separate columns in the map.

This is cross-build corroboration, not a semantic grade increase by itself.
Encoded immediates and displacements remain masked, and an identical compiler
shape does not establish equal data, side effects, runtime reach, source text,
or reconstruction parity.

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

## Four strict-vtable divergences

The only nonzero comparisons in the independently bounded 2,127-target strict
vtable census are:

| Retail -> demo | Retail name | Retail body | Normalized differences |
| --- | --- | ---: | ---: |
| `0x004568A0 -> 0x004568C0` | `CFEPDebriefing__ButtonPressed` | 139 B / 47 instructions | 22 instructions / 66 bytes |
| `0x004656E0 -> 0x00465730` | `CFMV__VFunc_3_004656e0` | 41 B / 11 instructions | 11 instructions / 31 bytes |
| `0x0051B840 -> 0x0051BB10` | `CFEPIntro__VFunc_5_0051b840` | 1,577 B / 446 instructions | 257 instructions / 743 bytes |
| `0x0053F190 -> 0x0053F7A0` | `CDXFMV__VFunc_11_0053f190` | 949 B / 267 instructions | 164 instructions / 549 bytes |

All four were marked `full_demo_decode=false` by the original vtable census.
That label remains an accurate description of that instrument: its demo side
was a fixed-offset window, not an independently recovered demo function body.

A second instrument has since recovered complete demo bodies for the two FMV
rows and three related startup functions. The
[FMV/startup lineage report](binary-analysis/pc-demo-retail-fmv-startup-lineage-2026-08-11.md)
resolves the removed per-playback skip field and guards, demo-only language
fallback, initialized playable-demo state, publisher FMV, and retail-only
demo-loading transaction. A separate
[frontend lineage report](binary-analysis/pc-demo-retail-frontend-lineage-2026-08-11.md)
recovers the other two divergent bodies plus their shared-resource producer.
It fixes slot 5 as `CFEPIntro::Render`, proves the extra demo publisher-surface
draw, and distinguishes demo `FEP_DEMOMAIN` debrief routing from retail's
playable-demo quit/result path. All four original strict-vtable divergences now
have complete independently bounded bodies and a semantic explanation.

The concentration in debriefing, intro, and FMV/frontend code is a useful
build-lineage signal. It is not evidence that gameplay is globally identical.

## What this changes for the RE campaign

The demo is now an independent refuter and address-translation oracle for most
of the executable, not only the virtual surface. A retail interpretation that
requires a changed opcode, register form, branch shape, or instruction layout
in one of the 8,021 exact rows must also explain why the independently linked
demo preserves that shape.

The earlier `CUnit`, `CBattleEngine`, `CThing`, `CComplexThing`, `CActor`, PC
controller, PC music, PC shell, FMV/startup, and frontend semantic cohorts have
now used that oracle. The next cross-build work should change instruments
again: independently bound the remaining 57 address-only bodies, then use calls,
exception metadata, strings,
retained source, and platform builds on the 50 address-unmapped rows. Repeating the
same normalized-signature search would only fit the remaining ambiguity.

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
- independent demo body/CFG and semantic recovery for the 57 address-mapped
  changed or incompletely bounded targets not closed by the FMV/startup and
  frontend reports;
- demo entry recovery for the remaining 50 retail functions;
- asset/configuration differences and their behavioral consequences;
- runtime equivalence, source equivalence, and rebuild parity.
