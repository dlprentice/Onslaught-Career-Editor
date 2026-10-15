# CMSH typed bind/current matrix order and released normal law

Status: active bounded retail contract — typed palette construction and linked-shader normal dataflow closed
Date: 2026-08-23
Verdict: **For each BONE entry, `CMeshRenderer__RenderMeshCore` samples the
part at frame zero and at the current interpolated pose, stages row-major
row-vector affine matrices, and constructs the unscaled bind-to-current palette
entry as `inverse(T_bind) * inverse(R_bind) * R_current * T_current`. It then
scales all 16 elements by binary32 `0x3EAAAAAB` and copies the result to the
renderer palette. The equivalent column-vector notation is the transposed,
reversed expression `T_current_col * R_current_col * inverse(R_bind_col) *
inverse(T_bind_col)`; it is the same operation, not a competing answer. In the
normal-bearing linked shader, the serialized normal `v3` is not deformed by the
c10 matrix palette at all: two direct `dp3` lighting consumers read `v3` against
`c89` and `c91`. There are zero normal palette rows, zero slot coefficients,
zero translation reads, and zero normal-normalization instructions. The second
linked variant neither declares nor consumes a normal.**
Evidence: MEASURED — exact pristine ranges/calls/dispatch targets, complete
instruction accounting for all six hash-pinned linked shader instances, the
landed P1 full replay, and one deterministic synthetic interpreter control over
a hash-pinned serialized normal and 42 captured palette rows.
Specimen: pristine `BEA.exe.original.backup` SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
mirror index SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`.
Machine-readable receipt:
[`cmsh-matrix-normal-deformation.tsv`](cmsh-matrix-normal-deformation.tsv),
SHA-256 `26bf50cf1ea64e50548d07c52a8d9633b82cdaa133b5d2d7e27d569b615e923f`.

No executable range, shader token stream, capture row, palette row, normal value,
or vertex payload is tracked. Only hashes, counts, typed operations, and bounded
outputs are public. The safe copy, mirror, and captures were read only. No game,
GUI, browser, debugger, Ghidra project, installed file, save, ROM, G:, or H: path
was launched or written.

## Reuse preflight and disposition

This is the narrow successor to the landed P1 position contract. It did not
repeat the 213-mesh AYA/CMSH census, the 92-row extractor audit, CPOS/CORI
identity, static VB readback, slot law, position blend, scale ownership, or
shader upload attribution.

| Disposition | Exact predecessor | SHA-256 | Use in this pass |
| --- | --- | --- | --- |
| **REUSED** | [`cmsh-matrix-palette-skinning.md`](cmsh-matrix-palette-skinning.md) | `39a4979104f5a07b5db276f085a8344822f2e90e4014ec075a0e19cf9bf6d90d` | Full P1 replay; retained `(0,2s,s)`, renderer-owned 16-element scale, c10 upload boundary, 213/7/206 meshes, 3,203 vertices, three captures, and six linked shader instances. |
| **REUSED** | [`cmsh-matrix-palette-skinning.tsv`](cmsh-matrix-palette-skinning.tsv) | `f98b2c7e501cf90702aba65481f3e879eadcc30a51f40dfa2d08c74b8b76a3af` | Exact landed public-safe P1 receipt. |
| **REUSED** | [`tools/cmsh_skinning_contract.py`](../../tools/cmsh_skinning_contract.py) / [tests](../../tools/cmsh_skinning_contract_tests.py) | `f54cbcf75fc4548c4227c695d229cbf9b212f41c7538063357d5c9cc7a30395a` / `90cc3487565470a7e489cd4e3f2310c9ecd4beefcf8d40c8c29c726faa2b94d9` | Hash/corpus/capture verification and the closed position core. |
| **REUSED** | [`aya-resource-extractor-source-audit.md`](../source-code/aya-resource-extractor-source-audit.md) / [92-row TSV](../source-code/aya-resource-extractor-contract.tsv) | `b08368a114069eae78b7dc61b00a085588188af575c74bb672ec1d5598b98af0` / `0a4a58c68f8c9d91cac27fba89d7c49a25948ac4ef5616c10fb6b0ae300a024e` | Preserved the extractor boundary; no `BONW`, `BONS`, hidden bind matrix, or source-intent claim was added. |
| **REUSED** | [`cmsh-cpos-cori-identity-2026-07-25.md`](../binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md) | `8cc27f8d467628d158b3595813ad5e0c98ef123da273ceb22b38f686daf85259` | Kept CPOS/CORI as derived model-space caches rather than bind matrices. |
| **REUSED** | [`cmsh_static_preview.py`](../../rebuild/tools/cmsh_static_preview.py) / [`cmsh_animation_usage_census.py`](../../tools/cmsh_animation_usage_census.py) | `efd14ff88315408d656e5b3605e1b3dab4a3e323118f5997934cb936f48f1cc7` / `510e03e5066f71ba1a89d604eefccb126589fcc16d27f339b90007526b02ec6c` | Fail-closed CMSH parsing, BONE/part identity, and the bounded frame-zero/current roles. |
| **EXTENDED** | ignored `local-lab/PUZZLE-SKIN-WEIGHTS-2026-07-31.md` | `f894982b2d2bc71a1eadcf0990ecb588170313a9637706035a818b6d339150c5` | Reused the captures and position-token correction; replaced the open normal residual with complete typed accounting. |
| **EXTENDED** | ignored RenderMeshCore decompile / exact disassembly | `1fef07d87011225eaf5edfd307eaf10c83f32d4008f46ede6cf8378f0f631c71` / `fb88f2ca3e4a84e2c93539df428a4db15d461af11a2202f5ab73028cb21b3fbf` | Reduced the exact per-bone call chain to typed row-major operations and pinned all reachable multiply/inverse dispatch families. |
| **NEW_MEASUREMENT** | [`tools/cmsh_matrix_normal_contract.py`](../../tools/cmsh_matrix_normal_contract.py) + focused tests | deterministic JSON/TSV reproduced twice; final hashes in Reproduce | Re-read the pristine typed ranges, all six shader instances, one serialized normal, and one captured 42-row palette block; ran adverse product/transpose/inverse and palette mutations. |

The exact capture-log identities remain:

- `vsdump-lvl800`: `5847b187e5ac8306219552a4ec56c3f48f76b453c09f74717b0c7eabaa8088fb`;
- `vskin-lvl800`: `d2966a4ec72af0dd7e8517bf51192cfd67fdde4efc575a36bf905c45b8aef88a`;
- `vsdump-lvl611`: `8caff0c638978be90ab15530bb74321200abc0725fcc1812ee634338eb32800d`.

Each contains exactly one instance of each linked shader identity, for six
instances total:

- no-normal variant: `1fb683058f29fe7cb5a4df4581d55fa6ba54b6edf4ef72526c4a2bc2401a4045`;
- normal-bearing variant: `f3b90c830f566d2d19a9f801925d400510bbe7fab5397ae9825f867d9a0d596c`.

## Typed palette operation order

`R_bind`, `t_bind`, `R_current`, and `t_current` below are the renderer-staged
4x4 rotation and translation components produced from the two named pose
samples. This notation does not re-label the raw `HORI`/`HPOS` storage layout.
The multiplication helper ABI is `out = left * right` over row-major 4x4
storage; the translation builder places xyz in the final row, so the resulting
matrices act on row vectors.

| Row | VA | Typed operation |
| --- | --- | --- |
| `MATRIX-001` | `0x0054A74E` | sample the indexed BONE part at frame zero → `R_bind`, `t_bind` |
| `MATRIX-002` | `0x0054A786` | sample the same part at current interpolation/controller inputs → `R_current`, `t_current` |
| `MATRIX-003` | `0x0054AF39` | `R_bind_inverse = inverse(R_bind)` |
| `MATRIX-004` | `0x0054AF55` | `T_current = translation(t_current)` |
| `MATRIX-005` | `0x0054AF7A` | `T_bind = translation(t_bind)` |
| `MATRIX-006` | `0x0054AF91` | `T_bind_inverse = inverse(T_bind)` |
| `MATRIX-007` | `0x0054AFAE` | `bind_inverse = T_bind_inverse * R_bind_inverse` |
| `MATRIX-008` | `0x0054AFE0` | `rotation_delta = bind_inverse * R_current` |
| `MATRIX-009` | `0x0054B012` | `P_unscaled = rotation_delta * T_current` |
| `MATRIX-010` | `0x0054B0C3..0x0054B217` | multiply all 16 elements by `float32(0x3EAAAAAB)` and copy to palette global `0x009C69D4` |

Therefore:

```text
P_row = inverse(T_bind) * inverse(R_bind) * R_current * T_current
M_palette = float32(0x3EAAAAAB) * P_row
```

For column vectors, define each `_col` matrix as the transpose of its row-vector
counterpart. Then the same mapping is:

```text
P_col = T_current_col * R_current_col * inverse(R_bind_col) * inverse(T_bind_col)
```

Calling one expression “reversed” without naming the vector convention is
wrong. The row-vector expression is the direct retail storage/call order; the
column-vector expression is its exact transpose.

### Static closure and adverse controls

The exact per-bone builder `0x0054A727..0x0054B041` is 2,331 bytes, SHA-256
`d872ab8436e562f24429b155660a1f78968a3596d2e515a64edd8091de7a4800`.
The final affine chain `0x0054AE71..0x0054B041` is 465 bytes, SHA-256
`1c4304a434d4bb5b176741e2d6afd52518609573aac51c1fde0e9c8f704d9b49`.
The scale/copy block remains the P1 range `0x0054B0AD..0x0054B224`, 376 bytes,
SHA-256 `362f12c6af54fcff8a238c5badfee7d5f7794b362af58a6585099e74821ebee2`.

The dispatch seed and every reachable selected family were pinned by range and
pointer value. Scalar, SIMD, and packed implementations preserve the same
three-pointer inverse/multiply ABI. The actual selected runtime target address
was not present in the existing logs; low-order differences caused by x87,
SSE, or packed evaluation remain unmeasured.

A synthetic control used a non-commuting shear/scale bind matrix, a current
rotation, and adverse bind/current translations. The selected, reversed,
transpose, and missing-inverse outputs were all distinct. Public-safe output
hashes are:

| Alternative | SHA-256 |
| --- | --- |
| selected retail order | `511ee304c07fdb4787419d646240e1b6e8e62d21851a1858ec01a295394f55c0` |
| reversed product mutation | `e55c6e7c6ebf092954369892aa89635372baf711646620d4b71212c3640aa31f` |
| transpose mutation | `75819295b018e7068ef4372553b24d06669f4e14af8858e9f5c2053890e54388` |
| missing-inverse mutation | `de03971ce5acb6508a3cdd6c030a205057d2ee9f30253a09a553edbb996d158c` |

## Released linked-shader normal law

The complete linked streams account for **948 tokens and 258 instructions**
across six instances, with **zero unclassified tokens and zero unclassified
instructions**. The unique no-normal stream is 143 tokens / 39 instructions;
the normal-bearing stream is 173 tokens / 47 instructions.

The normal-bearing variant declares `normal v3`. Its complete normal-consuming
block is seven typed instructions / 28 tokens:

```text
dp3 r4, v3, c89
lit r4, r4
mad r4, r4.y, c90, r2
dp3 r0, v3, c91
lit r0, r0
mad r0, r0.y, c92, r4
mul oD0, r0, v5
```

Consequences proved directly by those instructions:

- `v3` has exactly two consumers, both `dp3` lighting operations;
- neither consumer is relatively addressed and neither touches `c10..c51`;
- the normal uses **zero palette rows and zero BONE slots**, so its slot
  coefficients are exactly `(0,0,0)`;
- `dp3` consumes xyz only; no palette translation component can leak into the
  normal path;
- there is no `nrm`, `rsq`, or dependent `dp3`/`rsq`/`mul` chain normalizing
  `v3`; the later `rsq` in the full shader normalizes another temporary derived
  from `r1`, not the serialized normal;
- the no-normal variant has no normal declaration and no `v3` source operand.

Thus “normal blending,” “normal skinning,” and “same weights as position” are
not released behavior for these linked shaders. The normal remains the
serialized bind-pose vector through the shader's lighting inputs. This says
nothing about whether that was intended.

### Serialized-normal interpreter control

The control used vertex 0 from hash-pinned
`m_Sentinel Arm Big.msh.aya`
(`3c9092f3b7b16289e09e16e475303bef3fc072994ebf67b3ab7d88ed544a6967`).
The three-float normal payload was not published; its SHA-256 is
`fc736153dbb1a857f08e9d81708ffa9fa6dbbb4ddbd7fff1529c8a2135678c21`.
The first complete 42-row c10-c51 palette from the pinned `vskin-lvl800`
capture hashes to
`01a1dbf4a792173ab8a561fec465e669dd85abccb16a81d98b775213b59543ed`.

The interpreter executed the typed block with fixed synthetic lighting
constants, then reran it after negating/offsetting linear lanes and adding
`1000` to every captured translation lane. Both output hashes were exactly
`eac5ae16088fd9318a9e32af66095c3dda033e9b892f80b01de5dffecb590599`,
with zero palette reads. This is a deterministic dataflow control, not an
observed runtime normal output or pixel comparison.

## P1 facts preserved, not reopened

The focused tool replays the landed P1 contract before evaluating P2. It fails
if any of these change:

- 213 loose meshes = seven BONE carriers + 206 rigid controls;
- 3,203 skinned vertices, 9,609 slot words, and 38,436 classified field words;
- 467 runtime-readback vertices / 5,604 field comparisons / zero mismatches;
- exact position coefficients `(0, 2s, s)` for
  `s = float32(0x3EAAAAAB)`;
- the 16-element scale owner is `CMeshRenderer__RenderMeshCore`;
- `CVertexShader__ApplyCustomRenderStateShaderConstants` owns only the separate
  c7-c9 diagonal and c10+ upload.

Focused negative controls reject a reversed matrix product, transpose for
inverse, missing inverse, wrong scale owner, symmetric `(s,s,s)` slot combine,
normal `dp4` translation leakage, normal c10 palette read, unknown shader
opcode, and exact shader identity drift.

## Reproduce

```bash
python ./tools/cmsh_matrix_normal_contract.py \
  --data-root "<safe-copy>/data" \
  --mirror-index "<asset-mirror>/INDEX.jsonl" \
  --pristine-exe "<safe-copy>/BEA.exe.original.backup" \
  --capture-log "<d3d9-capture>/vsdump-lvl800-20260731-132614/d3d9-draws.log" \
  --capture-log "<d3d9-capture>/vskin-lvl800-20260731-133529/d3d9-draws.log" \
  --capture-log "<d3d9-capture>/vsdump-lvl611-20260731-134131/d3d9-draws.log" \
  --json-out ".artifacts/cmsh-matrix-normal/report.json" \
  --tsv-out ".artifacts/cmsh-matrix-normal/report.tsv"

python ./tools/cmsh_matrix_normal_contract_tests.py
```

Two independent runs were byte-identical. JSON SHA-256 was
`578990300592d974a59cf3d3c28a6ed993164a451792c59f38a18071b0d07a54`;
TSV SHA-256 was
`26bf50cf1ea64e50548d07c52a8d9633b82cdaa133b5d2d7e27d569b615e923f`.
Generated reports stay under ignored `.artifacts` or `local-lab`; the tracked
TSV is the exact generated public-safe receipt.

## Remaining unknowns and cheapest falsifiers

1. **Selected CPU dispatch address and rounding:** the existing captures do not
   record the live matrix-helper target. Falsifier: one read-only trace of slots
   `0x00656F3C` and `0x00656F78` after dispatch initialization, followed by a
   non-commuting matrix comparison at that exact implementation.
2. **Runtime normal output/pixels:** the token dataflow is exact, but no
   transformed normal or pixel was captured. Falsifier: a copied-runtime shader
   output instrument comparing one named vertex's `v3`-dependent lighting with
   and without an adverse c10 translation mutation.
3. **Handedness and semantic axes:** storage and product order do not name world
   handedness or artist-axis meaning. Falsifier: one oriented, asymmetric asset
   joined to a captured world transform and rendered directional output.
4. **Intent:** no source statement proves whether undeformed normals or slot-0
   position loss were intended. A proxy mutation can prove visual effect, not
   author intent.

## Claim boundary

Closed for the named PC specimen and exact six linked shaders: frame-zero/current
roles; row-major row-vector operation order; equivalent column notation; exact
inverse/multiply/translation/scale sequence; reachable dispatch implementation
families; full shader token/instruction accounting; the normal-bearing and
no-normal variant split; zero normal palette rows/slots/translation/normalization;
and one hash-only serialized-normal/palette invariance control.

Still open: the live CPU helper address and low-order rounding in the captured
sessions, runtime transformed-normal/pixel observation, handedness/semantic
axes, malformed input behavior, infantry draw observation, other builds or
platforms, intent, and rebuild parity. This contract does not add weights,
normal matrices, `BONW`/`BONS`, source intent, or a parity claim.
