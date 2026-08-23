# CMSH matrix-palette skinning and retail blend contract

Status: active bounded retail contract — serialized position skinning, palette
construction roles, and the executed position blend are closed; normal blending
and exact typed matrix-order notation remain open
Date: 2026-08-23
Verdict: **The seven shipped `BONE` carriers use one static 48-byte vertex form
and GPU-side `vs_1_1` skinning. Each vertex stores three floating-point palette
offsets, each exactly `3 * BONE-array index`; no per-vertex scalar weight is
serialized. The retail linked shader computes the slot-0 transform and discards
it, doubles slot 1, and adds slot 2. Because every palette matrix is uploaded
pre-scaled by `1/3`, the executed position weights are exactly
`(0, 2/3, 1/3)` for `(slot0, slot1, slot2)`, not symmetric slot
multiplicity. The renderer samples every indexed part once at frame zero and
again at the current interpolated pose before constructing and uploading the
palette.**
Evidence: MEASURED — corpus-static, pristine-retail-static, and copied-runtime
evidence converge: the
tracked deterministic instrument hash-verifies all 213 loose CMSH files, the
pristine executable, and three existing proxy logs; it emits a public-safe
27-data-row receipt with zero unclassified tested field words.
Specimen: mirror index SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
pristine `BEA.exe.original.backup` SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-readable receipt:
[`cmsh-matrix-palette-skinning.tsv`](cmsh-matrix-palette-skinning.tsv),
SHA-256 `e506c5bfa5381cf2b349b3a0ea20eacd14761e66fab09648dc47d1349073c1ce`.

No retail payload, executable byte range, shader token stream, capture frame, or
raw vertex row is tracked. The named safe copy, mirror, and capture corpus were
read only. Nothing was launched or modified; Ghidra was not opened or changed.

## Reuse ledger

This pass did not rediscover the AYA envelope, CMSH framing, WRES membership, or
the fact that the three words are scaled indices. It promoted an already strong
ignored working result into a replayable, public-safe contract and remeasured
only the unresolved combination, bind/current role, consumer, and exact bounded
instance.

| Disposition | Predecessor | SHA-256 / pin | What this pass did |
| --- | --- | --- | --- |
| **REUSED** | [`aya-resource-extractor-source-audit.md`](../source-code/aya-resource-extractor-source-audit.md) + [92-row contract](../source-code/aya-resource-extractor-contract.tsv) | audit commit `21fcd11bec3538fe24be61d92e5e6b4d76186adc`; files `b08368a114069eae78b7dc61b00a085588188af575c74bb672ec1d5598b98af0` / `0a4a58c68f8c9d91cac27fba89d7c49a25948ac4ef5616c10fb6b0ae300a024e` | Kept `CCUS`/`BONW`/`BONS` absent and refused the extractor's skipped-buffer guesses. |
| **REUSED** | [`cmsh-mesh.md`](cmsh-mesh.md), [`cmsh-animation-usage.md`](cmsh-animation-usage.md), and [`wres-instance-join.md`](wres-instance-join.md) | `c3ff3bd118c6cf6d9905906b5a9bb0d207488bacfc02b0b497c89015d38202be`, `310f030dad3a21fda8105082fe6d32e943cb96e912f58f1ac02c8cb3d8b5dda0`, `b6845a82849eb17eb39c751e388eb803096426c51a02963ee7cd82f1974ba588` | Reused the seven-carrier denominator, BONE-to-part names, 9,609 scaled slots, and bounded world membership. |
| **REUSED** | [`cmsh_static_preview.py`](../../rebuild/tools/cmsh_static_preview.py), [`cmsh_animation_usage_census.py`](../../tools/cmsh_animation_usage_census.py), and [`cmsh-cpos-cori-identity-2026-07-25.md`](../binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md) | `efd14ff88315408d656e5b3605e1b3dab4a3e323118f5997934cb936f48f1cc7`, `510e03e5066f71ba1a89d604eefccb126589fcc16d27f339b90007526b02ec6c`, `8cc27f8d467628d158b3595813ad5e0c98ef123da273ceb22b38f686daf85259` | Reused fail-closed parsing, mesh/part identity, and the proof that CPOS/CORI are derived caches rather than bind matrices. |
| **EXTENDED** | ignored `local-lab/PUZZLE-SKIN-WEIGHTS-2026-07-31.md` | `f894982b2d2bc71a1eadcf0990ecb588170313a9637706035a818b6d339150c5` | Retained its corrected executed shader law, then added exact current file/hash verification, complete TSV accounting, focused tests, and explicit bind/current consumer boundaries. |
| **NEW_MEASUREMENT** | [`tools/cmsh_skinning_contract.py`](../../tools/cmsh_skinning_contract.py) + focused tests | deterministic JSON `a4ef38dff962d39375f39711c6d40a9abba4707a9da89525eb2f164c86faa371`; TSV `e506c5bfa5381cf2b349b3a0ea20eacd14761e66fab09648dc47d1349073c1ce`, each reproduced twice | Re-read all 213 hash-pinned meshes, five raw pristine function ranges, six linked skinning shaders, 1,344 palette rows, and both exact Level-800 static VBs. |

The ignored decompile predecessors were also pinned before use:
`CMeshPart__LoadVerticesWithBones` `47d2cae5254c2b82a92943a3b7e212d85f96108456a277380ed64473c69e5aa2`,
`CMeshRenderer__RenderMeshCore`
`1fef07d87011225eaf5edfd307eaf10c83f32d4008f46ede6cf8378f0f631c71`,
and `CDXMeshVB__BuildSkeletalVB`
`2737becbe0a7bf69182bb76f094b18bab3a84c99b47e6a892f83414403bad5db`.
They are interpretation aids, not substitutes for the instrument's direct
pristine-byte pins.

## Exact bounded family

The family denominator is **213 loose `resources/meshes/*.msh.aya` files**.
Exactly seven have one `BONE` carrier; all other **206** are rigid controls.
Every carrier is part 1, uses `CMVB` stride/FVF/topology **48 / 0 / 4**, and
uses every declared BONE slot at least once.

| Serialized stride-48 word(s) | Role | Tested disposition |
| --- | --- | --- |
| `+0x00..+0x08` | bind-pose position `float3` | decoded and compared in both runtime instances |
| `+0x0C..+0x14` | three float palette offsets | each is exactly `3 *` an in-range index in this part's `BONE` array |
| `+0x18..+0x20` | normal `float3` | decoded and compared at runtime; animated normal-combine law remains open |
| `+0x24` | packed diffuse/ARGB word | decoded and compared exactly |
| `+0x28..+0x2C` | texture coordinate `float2` | decoded and compared at runtime |

That is **12 classified 32-bit words per vertex**, **3,203 vertices**, and
**38,436 classified field words**. The tested serialized family has **zero
unclassified words**. `BONE` is an array of same-mesh CMSP part indices; the
part names are the skeleton names. No `BONW` or `BONS` occurs in the complete
213-file corpus, and no hidden scalar weight is inferred.

The slot equality census is:

| Shape | Vertices | Meaning before applying the shader |
| --- | ---: | --- |
| `AAA` | 2,252 | all three offsets name one matrix |
| `AAB` | 135 | slots 0 and 1 match |
| `ABA` | 809 | slots 0 and 2 match |
| `BAA` | 0 | slots 1 and 2 match; adverse generator control |
| `ABC` | 7 | all three offsets differ |

All **816 `ABA` + `ABC` vertices** discriminate the executed shader from a
symmetric multiplicity interpretation. The zero `BAA` count supports the old
loader's greedy exporter/quantizer fingerprint; it does not change what the GPU
executes.

## Palette addressing and executed position law

For a stored slot float `q`, the BONE-array index is `i = q / 3`. The linked
shader moves `q` directly into the `vs_1_1` address register, so the three rows
for bone `i` are:

```text
c[10 + q + 0]
c[10 + q + 1]
c[10 + q + 2]
```

Let `P_i` be the unscaled bind-to-current 3x4 position transform the renderer
constructs for BONE entry `i`. Retail uploads `M_i = (1/3) * P_i`, including the
translation component. The six hash-pinned linked skinning shaders all execute:

```text
slot 0: r0.xyz = M[s0] * position       # computed, then overwritten
slot 1: r0.xyz = M[s1] * position
        r1     = r0 + r0
slot 2: r0.xyz = M[s2] * position
        r1     = r1 + r0
```

Therefore the exact released **position** law is:

```text
position' = 2 * M[s1] * position + M[s2] * position
          = (2/3) * P[s1] * position + (1/3) * P[s2] * position
```

The effective slot weights are **`(0, 2/3, 1/3)`**. Slot 0 has no position
contribution. This equals symmetric multiplicity only for some patterns:

| Shape | Executed result |
| --- | --- |
| `AAA` | `A` |
| `AAB` | `(2/3)A + (1/3)B` |
| `ABA` | `(2/3)B + (1/3)A` — opposite dominant bone from multiplicity |
| `ABC` | `(2/3)B + (1/3)C` — slot-0 bone absent |

Calling the asymmetry a bug is **UNKNOWN**. The pristine pre-link
`f_skeletal_animation` fragment appears intended to accumulate all three, but
the only released-behavior contract is the linked token stream handed to D3D.

## Bind/current transform roles

There is no separately serialized bind-matrix array in `BONE`, the 48-byte
vertex, `BONW`, or `BONS`. The runtime obtains the two transform roles from the
indexed CMSP parts:

1. `CMeshRenderer__RenderMeshCore @ 0x00549570` calls
   `CMCMech__BuildInterpolatedPoseAndAnchor @ 0x004B0FB0` at `0x0054A74E`
   with the frame-zero path for each BONE part. This is the bind/rest sample.
2. It calls the same pose builder again at `0x0054A786` with current frame,
   interpolation, and controller inputs. This is the current sample.
3. The body constructs one 4x4 palette matrix from those samples, scales all 16
   elements by `1/3`, and copies the matrices to the global palette later
   uploaded from `c10` in three-register rows.
4. `CVertexShader__ApplyCustomRenderStateShaderConstants @ 0x00502920`
   uploads the palette. Four exact `0x3EAAAAAB` immediate stores create the
   diagonal one-third scale, and the copied-runtime rows independently measure
   norms `0.333333222..0.333333423`.

This proves the **frame-zero bind role**, **current interpolated role**, and
**one-third pre-scale**. The dense untyped matrix body has not been reduced to a
reviewed row/column multiplication equation, so the exact notation/order of the
bind-to-current product remains **UNKNOWN**. `P_i` above deliberately names the
observed output of that construction rather than inventing an order. CPOS/CORI
are not substitutes: the loader recomputes those derived model-space caches
before use.

## Exact consumers and call sites

Raw range hashes below are over the named bytes in the pristine PE, not the
relocation-normalized hashes in broader function ledgers.

| Function | Range / raw SHA-256 | Contract contribution |
| --- | --- | --- |
| `CMeshPart__LoadVerticesWithBones` | `0x004AFBB0`, 3,139 bytes, `2e2541a66ff58b4e6fff4aced3fdbfb685c6628e641134d600fd395dd3a7b316` | Legacy/dev input path normalizes weights, greedily selects three influences by subtracting exact `1/3`, and establishes the exporter fingerprint; it is not the shipped CMSH VBUF consumer. |
| `CMCMech__BuildInterpolatedPoseAndAnchor` | `0x004B0FB0`, 2,692 bytes, `54997c37d712cfcdb7ab8cb6980eb5c4624fa387a227ad442dd984d13ddf1d4c` | Shared frame-zero/current pose sampler used by the palette constructor. |
| `CVertexShader__ApplyCustomRenderStateShaderConstants` | `0x00502920`, 4,512 bytes, `f5625793a5e4493280d3d380ec81488e9fb7e10f4d1a2b5ce8ab94c4b9bd5e34` | Scales and uploads the matrix palette from the renderer globals. |
| `CMeshRenderer__RenderMeshCore` | `0x00549570`, 8,844 bytes, `e1371a73aaa0da2f502b54d4eb830f50b6913662cce6416ac057a361b298d2fb` | Exact skeletal render consumer: samples bind/current poses, builds palette matrices, and dispatches layer rendering. |
| `CDXMeshVB__BuildSkeletalVB` | `0x0054C920`, 2,254 bytes, `fa71ca9eee533a891fbf1658145f70578546e7be43a4ef294d89db07a73ef8f0` | Builds the static 48-byte skeletal VB; exact `FILD` + multiply-by-`3.0f` emits the three palette offsets. |

`CDXMeshVB__VFunc_1_0054D210` dispatches to `BuildSkeletalVB` at
`0x0054D3AC` when the part mode is 3 and the skeletal gate is enabled. The
shipped serialized route is `CMeshPart__LoadFromStream` / `CDXMeshVB__Load` to
that builder and renderer; the old `LoadVerticesWithBones` path explains source
quantization but does not own the current VBUF bytes.

## Runtime instance and controls

The exact bounded runtime instance is Level 800:

| Mesh / part | Runtime VB | Comparison |
| --- | --- | --- |
| `m_Sentinel Arm Big.msh.aya`, part 1 `Tentacle` | 233 vertices; FNV-1a-64 `728853A3DB40EE3E`; one unlock | all 2,796 field words match the asset at logger precision |
| `m_Sentinel Arm Small.msh.aya`, part 1 `Tentacle` | 234 vertices; FNV-1a-64 `924CEA5B6FA76954`; one unlock | all 2,808 field words match the asset at logger precision |

Together they provide **467 vertices / 5,604 field-word comparisons / zero
mismatches**. One unlock and stable digests make these static bind-pose VBs;
the changing pose is in shader constants, not CPU vertex rewrites.

Controls are deliberately adverse or alternative:

- all 206 non-BONE meshes are negative serialized controls;
- the five infantry carriers reproduce the same 48/0/4 and slot-pattern family,
  while remaining honest non-draw controls in these captures;
- Level 611 links the same two skinning shader variants but produces no palette
  block or observed skinned draw in the sampled frame;
- `BAA = 0` tests the greedy quantizer fingerprint;
- the 809 `ABA` and seven `ABC` vertices refute symmetric multiplicity as the
  released position law;
- a one-token symmetric-combine mutation is rejected by the focused parser test.

The three exact log hashes are recorded in the TSV. Across them: **144 shader
creates, six linked skinning shaders, 32 complete palette uploads, and 1,344
palette rows**.

## Reproduce

```powershell
py -3 tools/cmsh_skinning_contract.py `
  --data-root "<safe-copy>\data" `
  --mirror-index "G:\bea-asset-mirror\INDEX.jsonl" `
  --pristine-exe "<safe-copy>\BEA.exe.original.backup" `
  --capture-log "G:\bea-d3d9-capture\vsdump-lvl800-20260731-132614\d3d9-draws.log" `
  --capture-log "G:\bea-d3d9-capture\vskin-lvl800-20260731-133529\d3d9-draws.log" `
  --capture-log "G:\bea-d3d9-capture\vsdump-lvl611-20260731-134131\d3d9-draws.log" `
  --json-out ".artifacts\cmsh-skinning\report.json" `
  --tsv-out ".artifacts\cmsh-skinning\report.tsv"

py -3 tools/cmsh_skinning_contract_tests.py
```

Two independent runs produced byte-identical JSON and TSV. JSON was 17,323 bytes,
SHA-256 `a4ef38dff962d39375f39711c6d40a9abba4707a9da89525eb2f164c86faa371`;
TSV was 12,640 bytes, SHA-256
`e506c5bfa5381cf2b349b3a0ea20eacd14761e66fab09648dc47d1349073c1ce`.
Generated reports are restricted to ignored `local-lab` or `.artifacts` paths.
The tracked TSV is the exact generated public-safe receipt.

## Remaining unknowns and focused falsifiers

1. **Exact matrix notation/order:** frame-zero/current roles and output are proved,
   but row/column multiplication notation is not. Falsifier: typed
   instruction-level reduction of the bounded palette block, or a controlled
   matrix trace that disagrees with the proposed product.
2. **Low-order VB bytes:** all 5,604 printed field words agree, not the raw byte
   stream. Falsifier: enable the existing exact hexdump path for recognized FVF
   `0x15A` and compare all `467 * 48` bytes.
3. **Bug versus convention:** slot-0 loss is executed behavior; author intent is
   unknown. Falsifier: a primary source statement or authenticated fixed linker
   output. A proxy-only token patch can show pixel/shape effect, not intent.
4. **Infantry runtime route:** five meshes share serialized structure and Level
   611 links the shader, but no infantry draw was captured. Falsifier: one copied
   runtime capture that joins a named infantry instance to FVF `0x15A`, c10
   palette, and the same shader core.
5. **Normal deformation:** the normal field is decoded and read back, but this
   contract decodes only the exact position combine. Falsifier: decode the linked
   normal block and compare one transformed runtime normal against the captured
   palette.

## Claim boundary

Closed: the seven-file/3,203-vertex serialized denominator; all 38,436 tested
field words; BONE/part identity; slot addressing; static VB ownership; one-third
palette scale; the released asymmetric position law; frame-zero/current pose
roles; exact static consumers/call sites; two bounded runtime instances; and the
three-capture shader/palette denominator.

Open: exact typed bind-product order, normal blending, raw runtime VB byte
identity, infantry draw observation, malformed-input behavior, shader intent,
other platforms/builds, and rebuild parity. No claim here adds `CCUS`, `BONW`,
or `BONS`, generalizes beyond the named PC specimen, or treats a source/exporter
formula as released behavior.
