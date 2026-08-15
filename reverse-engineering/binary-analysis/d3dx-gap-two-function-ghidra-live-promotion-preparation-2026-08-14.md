# D3DX two-function Ghidra live-promotion preparation

Date: 2026-08-14

Status: reviewed historical preparation; consumed by the completed
[live promotion](d3dx-gap-two-function-ghidra-live-promotion-2026-08-14.md).

Evidence: **MEASURED** — exact pristine bodies, the reviewed D3DX compatibility
owner, two fresh dry/apply/readback replicas, four adverse controls with
separate PRE readbacks, six exact physical project trees, retained historical
scratch evidence, and read-only backup openability.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
current byte-identical live and tracked 19-file / 187,009,925-byte Ghidra
projects, canonical inventory SHA-256
`a7916b5642b808f468ef113e731a4cfcf225287c94264009fde1034edd9b91cf`,
with `db.18617.gbf` SHA-256
`52cedb3555f418ea8000b0f8bb4c14cddc8c88954b3a5f3104e7600c487b52b0`.

Verdict: **PREPARATION_READY_LIVE_FORBIDDEN.** At preparation time, the two
exact loose-code bodies were safe structural candidates on db.18617 geometry. Two fresh
disposable saves independently reach the same 8,329-function semantic state
while preserving every field of all 8,327 PRE function rows. This preparation
opened neither live nor tracked Ghidra and authorizes no mutation.

## Exact prospective result

The current two-row manifest is
[`d3dx-gap-two-function-current-manifest-2026-08-14.tsv`](d3dx-gap-two-function-current-manifest-2026-08-14.tsv),
622 bytes, SHA-256
`48da3f9e6c6606a5a7c14443e6fe5f3191a24fb35dfc40ec67f886f27d0351e7`.

| Entry | Exact body | Prepared structural result | Static compatibility owner |
|---|---:|---|---|
| `0x00595fc9` | 95 B / 35 instructions | `FUN_00595fc9`, `DEFAULT`, one range | `D3DXVec3TransformNormal`-compatible |
| `0x00596028` | 153 B / 57 instructions | `FUN_00596028`, `DEFAULT`, one range | `D3DXVec4Transform`-compatible |

| Metric | Current PRE | Disposable POST | Delta |
|---|---:|---:|---:|
| Internal functions | 8,327 | 8,329 | +2 |
| Body ranges | 8,457 | 8,459 | +2 |
| Owned `.text` bytes | 1,811,443 | 1,811,691 | +248 |
| `.text` ownership | 93.900110776% | 93.912966399% | +0.012855623 points |
| Ghidra instructions | 551,143 | 551,143 | 0 |
| References | 234,478 | 234,478 | 0 |

Both bodies were already fully decoded as loose instructions, so creating their
body owners adds neither instructions nor references. The full program export
changes only `functions`. Program bytes, memory identity, defined and undefined
data, stored non-function symbols, comments, relocations, and all other exported
program metrics remain exact.

Both readback function inventories are byte-identical at 7,194,298 bytes and
SHA-256
`7b343b3578a01562daca02ec431586cf39e042d0daab9d6aa9448b779f880ef0`.
Their 8,327 PRE rows compare byte-for-byte equal; only the two manifest entries
are new. Their body-range, direct-call, listing, and name-projection exports are
also byte-identical. The exact 8,459-range union owns 1,811,691 bytes with zero
overlap, and the listing proves each terminal `RET 0x0c` remains inside its
prepared function.

## Mutation boundary and controls

`GhidraApplyD3dxGapBoundariesV2.java` is 46,410 bytes, SHA-256
`124fead4f8729bc1ef484cc09eae2b871b5117535a1bfbcb377120883afd30c9`.
It exact-requires the retail identity, db.18617 PRE counts, current manifest,
body sets, range/body hashes, and instruction/reference totals. Its only allowed
change is creating the two default-source functions. Names beyond the default
`FUN_` labels, signatures, comments, tags, grades, data, bytes, and explicit
references remain forbidden.

The current campaign proves:

- two independent positive copies, each with dry, saved apply, and separate
  readback phases;
- a forced failure after one creation and a complete-batch nested commit,
  explicit two-function compensation, then forced outer failure, each followed
  by exact PRE semantic readback;
- independent output-path and READY-path escape attempts refused before
  publication, again followed by exact PRE semantic readback;
- exact initial PRE copy receipts for all six disposable projects; and
- a retained copy/compare/read-only-open proof of the tracked PRE project.

Ghidra's rolling database serialization is not deterministic across saves. The
positive projects have distinct canonical hashes `8c71ff41…b2570` and
`06411067…d7803`; each of the four failure/compensation/containment controls
likewise has its own exact physical project and db.18618 hash. The authority
pins all six physical trees. The four control *semantic* function/program
readbacks are byte-identical to PRE; it does not misstate their rolling database
files as physically equal to PRE.

## Sealed preparation authority

The ignored evidence root is
`local-lab/d3dx-gap-two-boundary-current-preparation-20260814-v1`. Excluding its
aggregate receipt, it contains 223 files / 1,366,092,719 bytes with tree SHA-256
`f8689877ded68fc8e0eb4804d2c2808370e371cc1346a52a9f040c326c98f664`.
It contains no reparse points or Python cache artifacts.

The 18,831-byte `preparation-authority.ready.json` has SHA-256
`4c5c45dcd68c04a0679371a0e392e38331ebd945c115e3a59abc8a548cf34f00`.
The packaged authority is 58,010 bytes, SHA-256
`f6e932736298ecb070b1762f96e999b7b7d37d3b3c0320633e9b8b7ef7bc0406`.
Two consecutive saved verifies passed without tree or cache drift:

```powershell
python -I -B tools\ghidra_d3dx_gap_boundary_current_preparation_authority.py verify `
  --package-root local-lab\d3dx-gap-two-boundary-current-preparation-20260814-v1 `
  --receipt local-lab\d3dx-gap-two-boundary-current-preparation-20260814-v1\preparation-authority.ready.json `
  --repo-root . `
  --live-root "$env:USERPROFILE\Ghidra\Projects" `
  --scratch-package local-lab\d3dx-gap-two-boundary-scratch-20260814-v1
```

The retained db.18613 scratch package remains byte-exact at 236 files /
1,553,501,478 bytes and tree SHA-256
`655f53d43cd2afe2fab7912197e3d20f15ed21b538b6607d2b538d4f3ffa63f0`.
Its original verifier intentionally pins the then-current 8,280 tracked project
and therefore refuses after later promotions. The current authority honestly
rehashes that complete historical tree and relies on the new db.18617 replicas,
not the expired current-root assertion, for the present preparation.

Focused validation is:

```powershell
python -B tools\ghidra_d3dx_gap_boundary_mutator_tests.py
python -B tools\ghidra_d3dx_gap_boundary_current_preparation_authority_tests.py
```

## Claim boundary

Prepared here:

- exact disposable creation of two default-source functions on db.18617;
- exact PRE-row preservation and prospective function/range/byte arithmetic;
- exact instruction/reference and collateral semantic invariants;
- two saved replicas, two forced-failure controls (one outer rollback and one
  explicit post-inner-commit compensation), two containment controls, six
  physically pinned project trees, and copied-project read-only openability; and
- a create-new, read-only aggregate authority with policy `PREPARATION_ONLY`.

Not promoted here:

- any live, tracked, shared, canonical, or distributable Ghidra write;
- semantic Ghidra names, signatures, comments, tags, or grades;
- an original linker symbol or exact upstream D3DX version;
- runtime reachability, dispatch choice, numerical corner-case parity, source
  equivalence, or rebuild behavior; or
- a change to the then-current 8,327-function census or Generation 28 campaign.

The compatibility-scoped identities remain owned by the separate
[three-body current reconciliation](d3dx-gap-cohort-current-reconciliation-2026-08-14.md).
The later reviewed live promotion supplied the separately authorized one-save
ceremony, fresh PRE backup, live apply/readback, POST recovery, tracked
refresh/restore, projection, and aggregate authority. This preparation remains
the immutable decision evidence; it did not itself authorize or perform that
write.
