# CMSH `CPOS` / `CORI` identity — settled from the bytes

> Status: settled by exhaustive measurement over the released mesh corpus.
> Evidence class: static byte decode of user-supplied retail `.msh.aya` inputs.
> Nothing was launched. No retail file was modified.

## Verdict

**`CPOS` and `CORI` are a derived model-space composition cache. They are not an
independent animation track and they contain no data that `HORI` / `HPOS` /
`VHFM` / `PRNT` do not already carry.**

For every part *p* and every virtual frame *v*:

```
CORI[p][v] = M(parent(p))[v] · HORI[p][ VHFM[p][v] ]
CPOS[p][v] = M(parent(p))[v] · HPOS[p][ VHFM[p][v] ] + T(parent(p))[v]
```

where `M` / `T` are the same quantities composed root-to-leaf along the `PRNT`
chain, with the root's local pose as the base case. Storage is row-major and the
matrices act on column vectors.

Discarding `CPOS` / `CORI` on import loses nothing. Two existing importers that
skip them — `RetailAquilaWalkerAsset.cs:523-528` and the static-preview profile
parser — are correct to do so.

## Measurement

`tools/cmsh_cpos_cori_verify.py` decodes each `MESP` part, composes the local
`HORI` / `HPOS` track along `PRNT` for every virtual frame, and reports the
maximum absolute element error against the stored `CPOS` / `CORI` records.

Run over **all 213 `*.msh.aya` meshes** in
`data/resources/meshes` of the retail installation:

| Metric | Value |
| --- | --- |
| Meshes decoded | 213 |
| Meshes rejected | 0 |
| (part, virtual-frame) samples compared | 354,871 |
| Worst position element error | **5.62e-06** (`m_boss-fenrir.msh.aya`) |
| Worst orientation element error | **2.56e-07** (`m_f_dtroop.msh.aya`) |

Most meshes reproduce **exactly zero** error on the orientation basis. The
residuals are float32 rounding of a composed product, and they scale with chain
depth and coordinate magnitude, which is what a recomputed cache looks like and
not what independent authored data looks like. Full per-mesh table:
`local-lab/CPOS-CORI-CORPUS-VERIFY-2026-07-25.txt`.

Two further byte facts fix the interpretation:

1. **Record counts are indexed by `vFrames`, not `hFrames`.** `HORI` is
   `hFrames × 48` and `HPOS` is `hFrames × 16`; `CORI` is `vFrames × 48` and
   `CPOS` is `vFrames × 16` — *or exactly one record* when the part and its whole
   `PRNT` chain are static. On `m_f_be1.msh.aya`, part 4 `hinge76` has
   `hFrames = 1` (no local motion at all) yet stores 101 `CPOS` / `CORI`
   records, because its parent `leg4` has `hFrames = 101`. Motion that a part
   does not author still appears in its cache. That is only possible for a
   composition cache.
2. **`CMSP` base transform == frame 0 of the cache.** Over all 3,774 parts in
   the 213-mesh corpus, the `CMSP+0x30` orientation and `CMSP+0x70` position
   equal `CORI[0]` / `CPOS[0]` with a maximum element difference of **exactly
   0.0**, and equal the composed chain at virtual frame 0 to within 1.49e-06
   across the 28 Level 100 static meshes.

## Corrections to existing RE documents

- `reverse-engineering/quick-reference/aya-tags.md:153,161` calls `CPOS` /
  `CORI` "Animation position/orientation keyframes". That is misleading: they
  are not keyframes and are not an authoring source. They are a per-virtual-frame
  composed cache.
- `reverse-engineering/game-assets/aya-asset-format.md:77-78` calls them
  "Unknown (skipped)". Skipping is correct; "unknown" is now resolved.
- The same file describes `VHFM` as "Vertex frame data". It is the
  virtual-frame → hierarchy-frame map: one byte per virtual frame, valued in
  `[0, hFrames)`, per part.

## Record layout, as measured

| Chunk | Size | Layout |
| --- | --- | --- |
| `VHFM` | `vFrames × 1` | byte per virtual frame, selects a hierarchy pose |
| `HORI` | `hFrames × 48` | 3 rows × (3 floats + 1 pad float); rows of a 3×3 basis |
| `HPOS` | `hFrames × 16` | 3 floats + 1 pad float |
| `CORI` | `vFrames × 48` or `1 × 48` | same layout, model space, derived |
| `CPOS` | `vFrames × 16` or `1 × 16` | same layout, model space, derived |

On `m_FB_radar_station.msh.aya` part 10 `spinner01`, the 48-byte `HORI` records
have their pad float at exactly `0.0`. Other meshes carry non-zero values in
those four positions; they are not a translation column (translation is `HPOS`)
and their meaning is **not established** — see "Not decoded" below.

## Worked example — the radar dish

`m_FB_radar_station.msh.aya`, part 10 `spinner01`: `vFrames = 26`,
`hFrames = 25`, `VHFM = [24, 0, 1, 2, … 24]`.

The 25 `HORI` poses are a rotation about local Z stepping **exactly +14.400°**
per frame (`360 / 25`), with `HPOS` constant at
`(0.21739, 0.20284, 0.20800)`. Composed to model space and expressed as a delta
from the rest pose, virtual frames 0…25 rotate monotonically 0° → 360°, closing
back to identity. At the released 20 Hz base update that is one revolution per
1.25 s. The delta origin traces a circle of radius ≈ 3.7 because the spin axis is
offset from the part origin.

## Not decoded

- The fourth float in each `HORI` / `CORI` row. Zero on the meshes inspected
  closely, non-zero elsewhere; no consumer identified.
- The fourth float in each `HPOS` / `CPOS` record.
- `aFrames` (`CMSP+0xA8`), which takes values 0, 1 and 2 across the 3,774 parts
  of the corpus with no chunk confidently associated with it.
- `PBKT`. Retained opaque.
- Whether the released engine *plays* any given static-object track
  automatically or only on script trigger. This document establishes what the
  bytes contain, not what schedules them.
- The format stores **no frame rate**. The 20 Hz figure used downstream is the
  released base update rate established elsewhere in this repository
  (`OnslaughtRebuild.Core/SimulationConstants.cs`,
  `FirstFlightWorldView.RetailAquilaAnimationHz`), not a value read from a mesh.

## Reproduce

```powershell
py -3 .\tools\cmsh_track_probe.py "<install>\data\resources\meshes\m_FB_radar_station.msh.aya"
py -3 .\tools\cmsh_cpos_cori_verify.py "<install>\data\resources\meshes\m_FB_radar_station.msh.aya" --part 10
```
