# PC demo/retail CRT/FPU gapless closure and address propagation

Status: complete, bounded cross-build closure
Last updated: 2026-08-11
Evidence: MEASURED — exact specimen hashes, complete body-union bytes,
gapless x86-32 decode, paired direct transfers, enumerated changed absolute
references, and an iterative one-to-one address-propagation audit; UNKNOWN —
runtime floating-point behavior, exact CRT/source identity, and reconstruction
parity.
Verdict: the nine address-mapped CRT/FPU rows that the original census could
not compare are normalized-identical retail/demo bodies. Their newly usable
call edges recover six more normalized-identical demo entries. At this
checkpoint, the complete 8,136-function partition is 8,079
normalized-identical bodies, 13 bounded semantic divergences, and 44
address-unmapped functions; no address-mapped body remains unresolved.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

Later accounting: the
[equal-delta frontier closure](pc-demo-retail-equal-delta-closure-2026-08-11.md)
subsequently maps 29 of these 44 rows and leaves 15 address-unmapped. The
8,079 / 13 / 44 partition below remains the exact result of this checkpoint,
not current final accounting.

The machine-readable results are:

- [`pc-demo-retail-crt-fpu-gapless-closure-2026-08-11.tsv`](pc-demo-retail-crt-fpu-gapless-closure-2026-08-11.tsv),
  nine rows, 3,594 bytes, SHA-256
  `757dc0e15e5e9e273cdefb436c641735d2e7ba4b9999199f0f80f88aeee33a67`;
- [`pc-demo-retail-propagated-address-additions-2026-08-11.tsv`](pc-demo-retail-propagated-address-additions-2026-08-11.tsv),
  six rows, 1,486 bytes, SHA-256
  `74b120a5ebd7905e6c7be0293e4d37033ac66ab35dc5639426d050eddb55be28`;
  and
- [`pc-demo-retail-address-unmapped-frontier-2026-08-11.tsv`](pc-demo-retail-address-unmapped-frontier-2026-08-11.tsv),
  44 rows, 7,048 bytes, SHA-256
  `303fafdeec23d8b2caa0c6d202670a39230ce00e510309c1c594fe9dc178e839`.

## Why nine prior comparisons were false negatives

The original whole-function map correctly recovered each of the nine demo
entries through unanimous corresponding direct transfers, but left the bodies
`not_compared`. Its Ghidra instruction rows treat an x87 `WAIT` prefix and the
following operation as one owned row. Fresh Capstone 5.0.7 decode emits the
prefix separately. The nine bodies therefore contain 339 Ghidra rows but 350
gapless instructions per build; the exact difference is eleven folded `WAIT`
rows.

Fresh decode consumes all 1,104 body bytes in each specimen. After masking only
Capstone-reported encoded immediate and displacement spans, all 350 relative
instructions agree and no normalized byte differs. Forty-six raw bytes differ
because code/data operands moved. Every one of the 25 external direct transfers
resolves through a previously proved or newly accepted canonical address pair.

| Retail -> demo | Current tracked name | Bytes | Ghidra / fresh instructions | Folded `WAIT` | Raw-different bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| `0x0055DCCD -> 0x0055E36D` | `CRT__Acos` | 174 | 48 / 49 | 1 | 12 |
| `0x0055E128 -> 0x0055E7C8` | `__ftol` | 39 | 15 / 16 | 1 | 0 |
| `0x0055F39D -> 0x0055FA3D` | `CRT__AcosCoreWithFpuGuards` | 174 | 50 / 51 | 1 | 10 |
| `0x0055FA62 -> 0x00560102` | `CRT__PowCoreWithFpuGuards` | 467 | 125 / 127 | 2 | 14 |
| `0x00562C59 -> 0x005632EC` | `CRT__FpuStatusWordToInt_00562c59` | 14 | 7 / 8 | 1 | 0 |
| `0x00562C76 -> 0x00563309` | stale `CRT__GetFpuControlWord` | 35 | 15 / 16 | 1 | 0 |
| `0x00562C99 -> 0x0056332C` | stale `CRT__ReturnVoid` | 86 | 36 / 38 | 2 | 6 |
| `0x00563A10 -> 0x00564520` | `__cintrindisp2` | 62 | 19 / 20 | 1 | 4 |
| `0x00569449 -> 0x00569B19` | `CRT__ControlFp` | 53 | 24 / 25 | 1 | 0 |

The operand check did not assume that normalized addresses imply equal data.
It separately paired every changed absolute reference in these bodies: eight
10-byte constants, one four-byte value, and six C strings are byte-equal; six
other references identify zero-filled PE storage in both builds. This accounts
for all 21 changed absolute-reference pairs observed by the decoder.

## Two stale metadata contracts are now explicitly superseded

The exact bodies confirm two corrections that the earlier independent
[W011 primary review](ghidra-fullpass-findings/W011/primary/A08.md) and
[adversarial review](ghidra-fullpass-findings/W011/adversarial/B08.md) had
already identified, but which later aggregate tables still carried under stale
names:

- Retail `0x00562C76` is not `CRT__GetFpuControlWord(void)`. It accepts
  `newBits` and `mask`, snapshots the old x87 control word, computes
  `(old & ~mask) | (newBits & mask)`, loads the merged word with `FLDCW`, and
  returns the prior word in `EAX`. `CRT__ControlFpuWord` is a bounded
  descriptive direction, not a recovered original symbol or proof of complete
  `_control87` behavior.
- Retail `0x00562C99` is not `CRT__ReturnVoid(void)` and is not a no-op. It
  accepts one `flagBits` value, tests bits `0x1`, `0x8`, `0x10`, `0x4`, and
  `0x20`, and executes five visible x87 load/store/status/divide side-effect
  paths. All five direct callers are in
  `CRT__AdjustFloatingPointForFormatFlags`. The descriptive identity
  `CRT__ApplyFpExceptionFlagSideEffects` is bounded static interpretation, not
  an original source name or observed runtime effect.

This report supersedes those two names, void-arity plates, and return-only/no-op
descriptions as semantic authority. It does not mutate live or tracked Ghidra;
the reviewed database promotion gate remains separate. The static-C1 closure
table retains the old labels only as dated identity keys, not as endorsed
contracts.

## Six addresses recovered from the closed callers

The analyzer re-scanned 88 normalized-identical callers, including the
multi-range, text-core, opcode-factory, and CRT/FPU overlays that became usable
after the original map. For an unmapped retail target, it accepted a demo entry
only when every corresponding direct `CALL`/`JMP` selected one candidate, no
canonical demo entry was already claimed, no reverse candidate collided, and
the complete target bodies then compared normalized-identical. A final audit
replayed all proven callers after convergence.

| Retail -> demo | Current name | Corresponding caller evidence | Bytes / fresh instructions |
| --- | --- | --- | ---: |
| `0x0055FC35 -> 0x005602D5` | `CRT__IsFloat10Integral_0055fc35` | two transfers from `CRT__PowCoreWithFpuGuards` | 40 / 21 |
| `0x005613C7 -> 0x00561A67` | `__trandisp2` | `__cintrindisp2 + 0x1B` | 140 / 45 |
| `0x0056163B -> 0x00561CDB` | `__math_exit` | one transfer each from `CRT__Acos` and `CRT__AcosCoreWithFpuGuards` | 42 / 16 |
| `0x00561679 -> 0x00561D19` | `CRT__HandleFpuExceptionForMathOp` | `CRT__PowCoreWithFpuGuards + 0x73` | 163 / 57 |
| `0x00563ADA -> 0x005645EA` | `CRT__FpuIntDispatch2_Handle` | `__cintrindisp2 + 0x27` | 305 / 94 |
| `0x0056E8AA -> 0x005667A7` | `CRT__StrNLen` | three transfers from the paired locale-map/compare bodies | 43 / 20 |

All six accepted in the first propagation round. Together they cover 733
retail bytes and 253 fresh instructions per build with zero normalized
differences. No proposed alias was accepted or needed.

## Updated accounting and next instrument

| Cross-build state | Functions | Retail body bytes | Retail instructions |
| --- | ---: | ---: | ---: |
| Normalized-identical before this checkpoint | 8,064 | 1,729,265 | 521,118 |
| Nine CRT/FPU false negatives closed | 9 | 1,104 | 350 |
| Newly propagated normalized-identical entries | 6 | 733 | 253 |
| **Normalized-identical after this checkpoint** | **8,079** | **1,731,102** | **521,721** |
| Bounded semantic divergences | 13 | — | — |
| Address-unmapped frontier | 44 | — | — |
| **Complete retail inventory** | **8,136** | — | — |

The 44-row frontier is a complete negative result for this propagation pass:
each row had no corresponding-transfer proposal. It includes gameplay and
restart-loop bodies, CRT dispatch/stream helpers, five math helpers, JPEG and
`CFastVB` routines, callback-install targets, thunks, and one unwind entry.
Repeating generic normalized-signature search or this same call-edge pass would
fit the instrument rather than add evidence. The next useful pass must join
constants, strings, retained-source or library fingerprints, exception/unwind
metadata, or a newly proved corresponding caller.

## Reproduction and limits

The ignored evidence package is
`local-lab/pc-demo-retail-gapless-propagation-20260811-v1/`. Its analyzer is
55,337 bytes, SHA-256
`613330f659cdea2257ffca600361ef2525545a77e438384267706b6fa5ec0b69`.
The result receipt is 6,472 bytes, SHA-256
`cf456d98d0a5f1850d97d38ec24fea2e4e195a762a2750d99d476d2fb49e83c8`,
with verdict `STATIC_GAPLESS_CLOSURE_AND_PROPAGATION`. Inputs include the exact
8,136-function static closure, the immutable 8,086-row original map, the 40-row
multi-range and two-row text-core overlays, prior caller-propagation evidence,
and 18 pinned read-only Ghidra instruction exports.

This result proves only the named specimens' body boundaries, normalized
instruction shapes, enumerated operands, direct-transfer correspondence, and
the two visible static metadata corrections. It does not establish execution,
all floating-point edge values or exception effects, source equivalence,
semantic equivalence outside the 13 separately bounded divergences, or Godot
parity. No rebuild change is justified without a reproduced behavioral
mismatch.
