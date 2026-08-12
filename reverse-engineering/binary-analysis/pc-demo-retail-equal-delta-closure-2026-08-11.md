# PC demo/retail equal-delta frontier closure

Status: complete, bounded cross-build closure
Last updated: 2026-08-11
Evidence: MEASURED — exact specimen hashes, complete corrected body unions,
gapless x86-32 decode, all changed operands, three bounded indexed jump tables,
and a fixed-point direct-transfer replay; UNKNOWN — runtime execution, original
source identity, complete semantics, and reconstruction parity.
Verdict: 29 of the former 44 address-unmapped retail functions have one
unclaimed demo entry selected by equal-delta neighbors and a
normalized-identical complete body union. The complete 8,136-function
partition is now 8,108 normalized-identical bodies, 13 bounded semantic
divergences, and 15 address-unmapped functions.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The machine-readable results are:

- [`pc-demo-retail-equal-delta-closure-2026-08-11.tsv`](pc-demo-retail-equal-delta-closure-2026-08-11.tsv),
  29 rows, 7,687 bytes, SHA-256
  `29e4cac8d7915953d0154f830fab68ed6878f12dab4e7ff3992efba8ad9655dd`;
  and
- [`pc-demo-retail-address-unmapped-frontier-after-equal-delta-2026-08-11.tsv`](pc-demo-retail-address-unmapped-frontier-after-equal-delta-2026-08-11.tsv),
  15 rows, 3,236 bytes, SHA-256
  `3d5a3756d0962b7f398d2aeaa5efb96e69411ee6851dd498bf4ef11dd0e426f6`.

## Acceptance gate

The prior propagation checkpoint left 44 retail entries without a demo
address. For each entry, this pass examined the nearest already proved lower
and upper cross-build neighbors. A candidate existed only when both neighbors
had the same local demo-minus-retail delta and that delta selected one
unclaimed demo entry. Proximity was nomination, not acceptance.

Each nominated pair then had to satisfy all of these conditions:

1. the complete retail and demo body unions decode gaplessly;
2. both sides have the same instruction count and normalized instruction
   bytes after masking only Capstone-reported encoded immediates and
   displacements;
3. every changed immediate or displacement receives a non-conflicting paired
   classification; and
4. a replay of corresponding direct transfers introduces no alias, reverse
   collision, or unresolved proposal.

All 29 nominated pairs pass. They comprise 15 frozen-instruction unions, 12
sealed ranges completed through their final instruction, and two contiguous
post-snapshot bodies. The accepted bodies contain 3,463 instructions per build
and 11,096 corrected retail instruction bytes. There are 126 raw-different
bytes, zero normalized-different bytes, and 123 paired direct transfers. The
fixed-point replay adds no further address pair.

| Cross-build state | Before | Added | After |
| --- | ---: | ---: | ---: |
| Normalized-identical bodies | 8,079 | 29 | 8,108 |
| Bounded semantic divergences | 13 | 0 | 13 |
| Address-unmapped bodies | 44 | -29 | 15 |
| Mapped retail functions | 8,092 | 29 | 8,121 |
| Complete retail inventory | 8,136 | 0 | 8,136 |

The arithmetic is exact: `8,108 + 13 + 15 = 8,136`. No address-mapped body is
left in an unresolved comparison state.

## Six legacy body ranges omit instruction bytes

The first equal-delta attempt exposed a boundary-accounting defect rather than
a code difference. Frozen instruction rows own bytes that six legacy Ghidra
address sets omit:

| Retail entry | Current name | Legacy bytes | Corrected bytes | Omission |
| --- | --- | ---: | ---: | --- |
| `0x004AC4A0` | `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart` | 574 | 575 | byte `0x004AC6B0` inside the four-byte `LEA` at `0x004AC6AE` |
| `0x005771DD` | `Math__BuildScaleMatrix4x4` | 90 | 92 | two operand bytes of the terminal `RET imm16` |
| `0x0057726D` | `Math__BuildTranslationMatrix4x4` | 90 | 92 | two operand bytes of the terminal `RET imm16` |
| `0x005775C3` | `Math__BuildQuaternionRotationMatrix` | 224 | 226 | two operand bytes of the terminal `RET imm16` |
| `0x00577A3E` | `Math__BuildQuaternionFromEulerAngles` | 215 | 217 | two operand bytes of the terminal `RET imm16` |
| `0x00577EAA` | `Math__InterpolateVec4ByRatio` | 225 | 227 | two operand bytes of the terminal `RET imm16` |

The 29 rows therefore total 11,085 bytes under the dated Ghidra address-set
accounting and 11,096 bytes under the complete instruction union. The earlier
1,731,102-byte corpus total is likewise a legacy Ghidra-address-set aggregate,
not a corpus-wide audited instruction-byte union. This checkpoint does not
invent a corrected corpus-wide byte total.

The tracked static-C1 crosswalk remains an accurate projection of the dated
Ghidra bodies and receipts. This report supersedes those six ranges only for
byte-complete comparison work. No live or tracked Ghidra mutation was made;
repairing database bodies remains subject to the reviewed Ghidra promotion
gate.

## Complete operand audit

The 3,463 paired instructions contain 443 equal scalar immediate operands and
1,623 equal register-relative displacements. The 483 changed operand rows
classify as follows after the correction audit:

| Classification | Rows |
| --- | ---: |
| Internal control target at the same function-relative offset | 338 |
| External control target already present in the canonical map | 47 |
| Access-width pointed bytes equal | 68 |
| Anchor inside one byte-identical paired `.rdata` window | 23 |
| Bounded indexed jump table with corresponding targets | 3 |
| Mapped code reference | 2 |
| Paired zero-filled storage | 2 |
| Unresolved or conflicting | 0 |

The first operand classifier conservatively reported 26 changed relative
displacements. Inspection showed that all are 32-bit absolute image anchors
used with index registers, not ordinary structure or stack offsets. Twenty-three
land in one byte-identical `.rdata` run:

- retail `[0x005F2A9E, 0x0060BE51)`;
- demo `[0x005F3A9E, 0x0060CE51)`;
- 103,347 bytes; SHA-256
  `35bd5ba77710512c7180c1d835f1e5406aaef94f8dcd7d645f2133b8e46f52e5`.

The other three are bounded indexed jump tables. Their preceding `CMP` guards
establish 8, 7, and 7 entries. Every table target remains inside the paired
body envelope, decodes at both destinations, and has the same
function-relative offset:

| Retail table -> demo table | Entries | Paired function |
| --- | ---: | --- |
| `0x005AE5C0 -> 0x005AEC80` | 8 | `0x005AE1F0 -> 0x005AE8B0` |
| `0x005AE5E0 -> 0x005AECA0` | 7 | `0x005AE1F0 -> 0x005AE8B0` |
| `0x005B4EB0 -> 0x005B5580` | 7 | `0x005B4B20 -> 0x005B51F0` |

This closes the encoded-operand correspondence required by the cross-build
mapping. It does not turn static correspondence into an execution, data-usage,
source-equivalence, or behavioral-parity claim.

## Remaining frontier and next instrument

The 15-row frontier is a complete negative result for this instrument. None
has equal-delta mapped neighbors and none receives a collision-free proposal
from the newly closed callers. It retains:

- `con_fmv_play`, two `CGame` restart-loop bodies, and one `CTweakInt`
  constructor;
- two short jump thunks, the CRT first-call/flush pair, and one unwind entry;
  and
- six `CFastVB` vector/matrix dispatch bodies.

Repeating equal-delta or the same direct-transfer replay cannot add evidence.
The next pass must use retained source, library/compiler fingerprints,
constants and strings, exception metadata, or a newly proved control-flow
alignment.

## Reproduction and limits

The ignored evidence package is
`local-lab/pc-demo-retail-frontier-structural-20260811-v2/`. Its structural
analyzer is 33,309 bytes, SHA-256
`f82b9093a1566f4c86ff0a836a2a693e7cd1ed5eca780f5b4f793d231abc0f72`;
its result receipt is 2,373 bytes, SHA-256
`96548b39816bc7726f2e2b2b7cfd8afc686b5a1c25c116a863a52f582b62d9e0`,
with verdict `CORRECTED_BODY_UNION_CLOSURE_AND_PROPAGATION`. The complete
44-row candidate census is 8,495 bytes, SHA-256
`9c84c628ad629c540d54c4d2021cb385cf71aeca33097ed5818af360f8eeb510`.

The operand-exception correction analyzer is 19,216 bytes, SHA-256
`afec2003a16f590ba38f2b993ee44ff3d3701ab26a5aa0d5a96a5b8a599e4879`.
Its 26-row correction table is 7,509 bytes, SHA-256
`da71c88f51c3548b0681be0d8bf481d62fadd8b1e981ef9acc259530031d20db`;
its result is 3,126 bytes, SHA-256
`90d19a081be798ef9e298ffdd8357589789bc93a2e40b845e3c2e5e108188b9e`,
with verdict `OPERAND_PAIRS_CLASSIFIED`.

An independent promotion verifier lives at
`local-lab/pc-demo-retail-frontier-promotion-verify-20260811-v1/`. It rebuilds
all 29 corrected unions from the pinned specimens and range owners, rechecks
every per-row normalized hash/count, replays the equal-delta brackets and map
partition, and joins the separately pinned operand audit. The verifier is
22,692 bytes, SHA-256
`c7cd7ab02a325226b5e5bef34c4fa7187bfa48a026e167e7cea577d69154639d`;
its `PASS` receipt is 1,843 bytes, SHA-256
`8224e3096e6f3e2d87da03ea51e66289ab7c9912e7e30e26f4a4109947179e12`.

Inputs pin the pristine and demo specimens, the immutable original map, the
prior six address additions, the 44-row input frontier, the exact 8,136-row
static closure, the sealed range catalog and READY receipt, and the manifest of
18 frozen Ghidra instruction exports. The result establishes only the named
specimens' address correspondence, corrected body-union instruction shape,
enumerated encoded operands, and bounded jump-table targets. No rebuild change
is justified without a reproduced behavioral mismatch.
