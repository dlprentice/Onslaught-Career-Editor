# D3DX two-function Ghidra scratch admission

Date: 2026-08-14

Status: reviewed historical scratch admission; current-geometry re-grounding
required, with live and tracked Ghidra promotion forbidden.

Evidence: **MEASURED** — exact pristine bodies, the reviewed dated-state
reconciliation, two independent dry/apply/readback replicas, four adverse
controls with separate PRE readbacks, and copied-project read-only openability.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
scratch copies of the then-current tracked 19-file / 186,960,773-byte Ghidra project,
whose `db.18613.gbf` is 68,337,664 bytes with SHA-256
`615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`.

Verdict: **SCRATCH_READY_LIVE_FORBIDDEN.** Two complete D3DX-compatible loose
bodies can be admitted as exact default-source functions on isolated copies.
Both saved replicas independently reach 8,282 functions while preserving every
field of all 8,280 PRE function rows. This report authorized neither live nor
tracked to change; both later advanced independently to 8,304 functions.

## Exact structural result

The two-row input is
[`d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv`](d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv),
608 bytes, SHA-256
`2d8f16415206538d0377fafe70c210bf8de65b442e2162ad5f5909d01c21fefd`.

| Entry | Exact body | Scratch result | Static compatibility owner |
|---|---:|---|---|
| `0x00595fc9` | 95 B / 35 instructions | `FUN_00595fc9`, `DEFAULT`, one range | `D3DXVec3TransformNormal`-compatible |
| `0x00596028` | 153 B / 57 instructions | `FUN_00596028`, `DEFAULT`, one range | `D3DXVec4Transform`-compatible |

The structural projection is therefore:

| Metric | Current PRE | Saved scratch POST | Delta |
|---|---:|---:|---:|
| Internal functions | 8,280 | 8,282 | +2 |
| Body ranges | 8,400 | 8,402 | +2 |
| Owned `.text` bytes | 1,794,212 | 1,794,460 | +248 |
| Ghidra instructions | 550,991 | 550,991 | 0 |
| References | 234,495 | 234,495 | 0 |

The instruction count does not increase because both bodies were already fully
decoded loose instructions. The separate full-program export changes only its
function-count metric. Instruction layout, references, defined and undefined
data, stored non-function symbols, comments, relocations, program bytes, and
memory identity stay exact.

Both readback function inventories are byte-identical at 7,163,259 bytes and
SHA-256
`1a269f886c7cc7c11c854aa1219b81384102a530550277e88b83e9b3c043916d`.
Their program inventories are byte-identical at 1,267 bytes and SHA-256
`9d224178c0a4b85418364b47be996d48f83c970e399ab5fc28383858d1f0ff2a`.
The exact join finds 8,280 unchanged PRE rows and only the two manifest entries
as new rows.

## Mutation boundary and controls

`GhidraApplyD3dxGapBoundaries.java` is 46,399 bytes, SHA-256
`8767c361207de1718c3d3742fa43f76e9d897772ecd6a8123116299277a3f710`.
It exact-requires the retail identity, current PRE counts, manifest hash, body
bytes and ranges, and instruction/reference snapshots. Its only allowed change
is creation of the two explicit body sets with default names and default
signatures. It does not authorize names, semantic metadata, comments, tags,
data, bytes, or explicit references.

The formal campaign contains:

- two fresh positive copies, each with a dry run, saved apply, and separate
  read-only full-inventory readback;
- a forced failure after creating the first boundary, followed by a separate
  readback exactly equal to PRE;
- a complete validated batch followed by a nested commit request, explicit
  compensation, and forced outer failure, again followed by an exact PRE
  readback;
- separate output-path and READY-path escape attempts, each refused before any
  mutation or publication and each followed by an exact PRE readback; and
- a retained copy/compare/read-only-open proof of the exact tracked PRE project.

The earlier exploratory project and its three runs are retained in the sealed
tree but explicitly superseded. They are not used to satisfy any formal count,
replica, rollback, or containment claim.

## Sealed authority

The complete ignored package is
`local-lab/d3dx-gap-two-boundary-scratch-20260814-v1`. Excluding its aggregate
receipt, it contains 236 files / 1,553,501,478 bytes with deterministic tree
SHA-256
`655f53d43cd2afe2fab7912197e3d20f15ed21b538b6607d2b538d4f3ffa63f0`.
It contains no reparse points or Python cache artifacts.

The 14,021-byte `scratch-authority.ready.json` has SHA-256
`f68ae99ed352b1f3087a8f0b61eb53dff95d978450a929e70e2d428451216a5d`.
The packaged authority rehashes the entire evidence tree, validates every
retained boundary-result field, rejoins PRE and POST inventories, checks exact
run and project topology, binds the recovery log and safe read-only argv, and
rebinds the retained ceremony-time project roles to the current repository and
package roots. Two verifies from distinct working directories passed with zero
tree or cache drift:

```powershell
py -3 -I -B `
  local-lab\d3dx-gap-two-boundary-scratch-20260814-v1\tools\ghidra_d3dx_gap_boundary_scratch_authority.py `
  verify `
  --package-root local-lab\d3dx-gap-two-boundary-scratch-20260814-v1 `
  --receipt local-lab\d3dx-gap-two-boundary-scratch-20260814-v1\scratch-authority.ready.json
```

Focused validation is:

```powershell
py -3 -B tools\ghidra_d3dx_gap_boundary_mutator_tests.py
py -3 -B tools\ghidra_d3dx_gap_boundary_scratch_authority_tests.py
```

## Claim boundary

Promoted here:

- exact disposable-project creation of the two default-source functions;
- exact PRE preservation and POST function/range/byte arithmetic;
- exact instruction/reference and collateral invariants;
- two saved replicas, two rollback controls, two containment controls, and
  copied-project read-only openability; and
- a portable, read-only aggregate verifier with policy
  `SCRATCH_READY_LIVE_FORBIDDEN`.

Not promoted here:

- a live, tracked, shared, or canonical Ghidra write;
- semantic Ghidra names, signatures, comments, tags, or grades;
- an original linker symbol or exact upstream D3DX version;
- runtime reachability, dispatch choice, numerical corner-case parity, source
  equivalence, or rebuild behavior; or
- any change to the then-current 8,280-function census.

The compatibility-scoped API identities remain owned by the separate
[three-body current reconciliation](d3dx-gap-cohort-current-reconciliation-2026-08-14.md).
A future live promotion must start from a fresh current-state preparation,
reconfirm live/tracked equality and absence of conflicting later boundaries,
then use the normal one-save backup/readback/restore authority. This scratch
receipt is necessary evidence for that later decision, not permission to make
it.
