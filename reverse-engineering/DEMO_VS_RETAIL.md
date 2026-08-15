# PC demo versus PC retail

Status: active, measured cross-build evidence over the dated 2026-08-12 census
Last updated: 2026-08-14
Evidence: MEASURED — exact executable/archive hashes, independently recounted
MSVC RTTI/vtables, a 2,127-target virtual census, a conservative 8,086-row
cross-build function-address map, and exact multi-range, opcode-factory, and
gapless CRT/FPU, caller-propagation, equal-delta body-union, and whole-demo
exact-fingerprint replay, plus final source/call/metadata frontier closure;
UNKNOWN — normalized constant values outside the explicitly checked cohorts
and runtime/source/rebuild equivalence.
Verdict: the PC demo is a distinct build with a structurally identical virtual
class surface. Across the dated 8,136-function population, 8,119 retail
functions have a complete normalized-identical demo instruction stream. Another
16 have independently bounded semantic lineage differences. One compiler-EH
cleanup package is proven retail-only because its parent controls-screen block
and metadata are absent from the demo. All 8,135 retail functions with a demo
counterpart are mapped; zero rows in that population remain address-unresolved.
The 34 functions admitted to Ghidra on 2026-08-13, 31 text-gap functions, 79
external-table functions, 24 JPEG/IJG callback functions, and 23 CRT P0
functions admitted on 2026-08-14 are outside this frozen map. Two later D3DX
functions are outside it as well. The 79, 24, and 23 have separate bounded demo
correlations; the D3DX pair instead has separate PC/Xbox compatibility evidence.
Integration into the frozen whole-population demo map remains open. The current
structural census is 8,329.
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

The original 8,021 normalized-identical rows have unique retail and demo
entries. Their contiguous body-overlap graph is also identical: the sole
nested-entry pair is present on both sides, with no demo-only or retail-only
overlap. Exact non-contiguous replay subsequently adds 42 multi-range rows: the
two text-core functions described below and the forty-row
[multi-range closure](binary-analysis/pc-demo-retail-multirange-closure-2026-08-11.md).

The immutable first-pass mechanical map is
[`binary-analysis/pc-demo-retail-function-map-2026-08-11.tsv`](binary-analysis/pc-demo-retail-function-map-2026-08-11.tsv),
1,314,885 bytes, SHA-256
`cdb26380bb6b29e82edd601bb95dfc215f62813d925e2f4c4c78452a7af7c68a`.
It remains evidence of where that instrument abstained. Accounting over the
dated map and its narrower exact closure reports is:

| Whole-function result | Count |
| --- | ---: |
| Dated retail functions covered by this map | 8,136 |
| Entries in the original conservative address map | 8,086 |
| Newly propagated demo entries | 6 |
| Equal-delta body-union demo entries | 29 |
| Exact-fingerprint demo entries | 11 |
| Final divergent demo entries | 3 |
| Mapped demo entries in the dated population | 8,135 |
| Original single-range normalized-identical body streams | 8,021 |
| Multi-range normalized-identical corrections | 42 |
| Opcode-factory normalized-identical correction | 1 |
| CRT/FPU `WAIT`-aware normalized-identical corrections | 9 |
| Propagated normalized-identical additions | 6 |
| Equal-delta normalized-identical additions | 29 |
| Exact-fingerprint normalized-identical additions | 11 |
| Semantically resolved non-identical bodies | 16 |
| Proven retail-only compiler-EH packages | 1 |
| Address mapped, still changed or incompletely bounded | 0 |
| Address-unresolved rows | 0 |
| Current functions outside this dated map | 34 |
| Prior legacy Ghidra address-set byte aggregate | 1,731,102 |
| New equal-delta legacy / corrected instruction bytes | 11,085 / 11,096 |
| Exact-fingerprint complete body bytes / instructions | 1,884 / 545 |
| Normalized-identical retail instructions | 525,729 |

The 1,731,102-byte value is the dated Ghidra address-set aggregate from the
prior checkpoint, not a corpus-wide audited instruction-byte union. The
equal-delta pass found six bodies whose address sets omit 11 bytes owned by
complete instructions, so this document does not manufacture a corrected
whole-corpus byte total.

The original 65 address-only/different rows were the four strict-vtable
divergences below, 60 entries independently fixed by unanimous corresponding
direct transfers, and one isolated compiler-unwind entry fixed by its
equal-delta neighbors. Fifty-two were comparison false negatives: 42
multi-range bodies, the linearly re-decoded opcode factory, and nine x87 bodies
whose Ghidra rows folded `WAIT` prefixes. Thirteen initially mapped rows have
edition-specific behavior accounted for by the reports below; the terminal
frontier adds three more bounded divergences, and no mapped row remains
unresolved.
Replaying corresponding transfers from the newly closed callers then recovers
six of the former 50 address-unmapped entries. Equal-delta neighbor nomination,
followed by complete corrected-body and operand audits, recovers another 29. A
complete demo-text exact-fingerprint scan, with mapped caller/target and ordered
block evidence for ambiguous shapes, recovers another 11.
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

The
[shell/FMV lineage report](binary-analysis/pc-demo-retail-shell-fmv-lineage-2026-08-11.md)
then closes the three changed shell-lifecycle bodies around those rows. Demo
factors its startup sequence into a 500-byte helper, inserts `publisher` into
all startup/attract paths, and requests one of two language-selected promotional
movies before shutdown. Retail retains inline startup policy and no promotional
shutdown call.

The
[text-core lineage report](binary-analysis/pc-demo-retail-text-core-lineage-2026-08-11.md)
also resolves two conservative false negatives. `CText::Init` and the localized
fatal wrapper each have two Ghidra body ranges, so the original single-range
mapper abstained. Direct range-for-range decoding proves zero normalized
instruction differences, identical language literals, and identical
body-relative switch targets.

The
[MissionScript opcode-factory lineage report](binary-analysis/pc-demo-retail-asm-instruction-lineage-2026-08-11.md)
resolves one more conservative false negative. The original map retained
`CAsmInstruction__SpawnFromOpcode` as `not_compared` because its 401 exported
Ghidra instruction rows do not form one gapless linear stream around the final
case. Fresh complete decode proves 400 equal relative instructions, all 27
jump-table targets, and the same strict-RTTI instruction class and slot-0
executor for every opcode `0x00..0x1a`. This also replaces the schema's eight
remaining `UNPROMOTED_*` class placeholders without claiming their runtime
effects.

The
[CRT/FPU gapless closure and address-propagation report](binary-analysis/pc-demo-retail-gapless-closure-2026-08-11.md)
closes the final nine mapped false negatives. Their 1,104 bytes decode to 350
instructions per build with zero normalized differences; eleven separate
`WAIT` prefixes explain the prior Ghidra-row count mismatch. It also supersedes
the false `CRT__GetFpuControlWord(void)` and `CRT__ReturnVoid(void)` semantic
plates, checks all 21 changed absolute-reference pairs, and uses the now-usable
call edges to recover six more exact demo entries. The tracked
[44-row post-gapless frontier](binary-analysis/pc-demo-retail-address-unmapped-frontier-2026-08-11.tsv)
is the exact queue at that checkpoint.

The
[equal-delta frontier closure](binary-analysis/pc-demo-retail-equal-delta-closure-2026-08-11.md)
then maps 29 of those rows. All 3,463 paired instructions have zero normalized
differences, and a complete 483-row changed-operand audit closes every encoded
reference, including one 103,347-byte equal `.rdata` window and three bounded
indexed jump tables. It also identifies six legacy Ghidra body sets that omit
11 instruction bytes.

The
[exact-fingerprint frontier closure](binary-analysis/pc-demo-retail-exact-fingerprint-closure-2026-08-11.md)
then maps 11 of the remaining 15 rows. It scans every byte of demo `.text` for
the complete normalized retail bodies, resolves repeated shapes through mapped
caller/code-pointer, unique-callee, and ordered raw-block evidence, and
classifies all 17 changed operand pairs. Its independent replay passes across
1,884 body bytes and 545 instructions. The current
[four-row frontier](binary-analysis/pc-demo-retail-address-unmapped-frontier-after-exact-fingerprint-2026-08-11.tsv)
is the exact queue at that checkpoint.

The
[final function frontier closure](binary-analysis/pc-demo-retail-final-frontier-closure-2026-08-12.md)
then assigns all four rows a terminal state. `con_fmv_play`,
`CGame::ShutdownRestartLoop`, and `CGame::RestartLoopRunLevel` receive bounded
demo entries through complete bodies, mapped call sequences, paired strings and
callers, and retained-source ownership. The final unwind funclet is not forced
onto one of 59 generic matches: its parent controls-screen block, exact
32-byte compiler package, and one `FuncInfo` record are all absent from the
demo, whose mapped neighboring code and metadata become adjacent. The address
frontier is therefore closed with one proven retail-only package rather than a
fabricated demo address.

The
[credits/localization lineage report](binary-analysis/pc-demo-retail-credits-localization-lineage-2026-08-11.md)
then resolves two large changed table builders logically rather than masking
their constants. The demo inserts 25 credits rows while retaining all 222
retail rows unchanged and in order. Across 1,245 hard-coded language/ID slots,
only diagnostic ID 183 changes—from DirectX 8 to DirectX 9 in all five
languages. Demo's extra American-English table is an exact alias of ordinary
English.

The concentration in debriefing, intro, and FMV/frontend code is a useful
build-lineage signal. It is not evidence that gameplay is globally identical.

## What this changes for the RE campaign

The demo is now an independent refuter and address-translation oracle for most
of the executable, not only the virtual surface. A retail interpretation that
requires a changed opcode, register form, branch shape, or instruction layout
in one of the 8,119 exact rows must also explain why the independently linked
demo preserves that shape.

The earlier `CUnit`, `CBattleEngine`, `CThing`, `CComplexThing`, `CActor`, PC
controller, PC music, PC shell, FMV/startup, and frontend semantic cohorts have
now used that oracle. The function-address frontier no longer owns a queue. Any
next cross-build work should target unresolved semantics, constants, runtime
causality, or reconstruction mismatches rather than repeat address recovery.

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
- runtime meaning for normalized constants outside the audited cohorts;
- asset/configuration differences and their behavioral consequences;
- runtime equivalence, source equivalence, and rebuild parity.
