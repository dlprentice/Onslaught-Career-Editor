# Mesh-LOD camera/draw attribution gate

Status: active — offline comparison prerequisite for patch-surface runtime rows
Last updated: 2026-08-22
Summary: a fail-closed proxy-v2 method for comparing selected mesh geometry at
one repeated Level-100 camera transform without using frame-number or pointer
coincidence.
Evidence: MEASURED — proxy-v2 `M`/`D`/`G` contracts are exercised by the existing
proxy self-test, and this gate's synthetic 33-case suite proves normalization,
matching, exact negatives, and named refusal paths without launching BEA.
Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfa…`, 2,506,752 bytes
(`local-lab/safe-copy-bea-pristine/`, read-only). The offline gate reads neither
the specimen nor the copied product; runtime sidecars must name both exactly.

## Scope

This gate is the retained prerequisite for patch-surface rows `0x00631E8C`,
`0x00631E90`, and `0x00631EA0`. It does not stage a row, launch the game, or
promote a TSV confidence. It compares two already captured logs and writes a
deterministic receipt. Runtime work remains serialized, copied-profile only,
and lease-gated.

The existing passive proxy already owns every required hook:

- each `D` row names the world, view, and projection matrix ids in force;
- each `M` row serializes the corresponding matrix value at six decimals;
- `G` rows carry the exact VB/IB byte-range hashes and counts used by a draw;
- `BEA_D3D9_TEXHASH=1` gives bound textures a content identity; and
- `P` rows delimit complete presented frames.

No `tools/**` change is required. Batch 5 armed back-buffer capture but set
`maxframes=0`; its logs therefore contain sampled back-buffer `G` rows but no
`D`, `M`, or per-draw `G` rows. Those retained logs cannot be retrofitted into
attribution evidence.

## Identities

All identities are SHA-256 over canonical JSON, not over process-local ids.

1. **Camera identity** is the direct (not `MultiplyTransform`-derived) `view`
   plus `proj` matrix value. Decimal tokens are normalized to exactly six
   places, including `-0.000000` → `0.000000`. A checkpoint is admissible only
   when that exact identity occurs in both runs for at least three consecutive
   presented frames.
2. **Draw identity** is direct `world0`, bound texture content hash(es), the
   canonical texture-factor value, draw kind and primitive type, FVF, stream-0
   stride, and fixed-function material state. When stage 0 enables a texture
   transform, the identity also includes its direct `tex0` matrix value and
   transform flags; absent `tm0`/`tmflags` is the disabled case. COM pointers,
   wrapper generations, matrix ids, texture serials, frame/draw numbers,
   primitive counts, and vertex counts are excluded. The anchor must be unique
   within every selected frame; duplicates fail rather than being paired by
   draw order.
3. **Mesh identity** is the primitive/vertex count plus canonical VB and, for
   indexed draws, IB count, byte count, stride/element size, and FNV content
   hash. Pointers, offsets, generations, unlock counts, and last-unlock frame
   are excluded. A draw must keep one mesh identity through the three-frame
   window on each side before the sides are compared.

The split is deliberate: draw identity answers “is this the same placed,
textured draw?”, while mesh identity answers “which geometry did that draw
select?”. A LOD swap may change mesh identity without destroying the anchor
needed to compare it.

## Required run sidecar

Each log has a `bea-lod-attribution-run.v1` JSON sidecar. The validator requires
and cross-checks:

- role (`stock` or `staged`), PID, Level 100, quality `high`, exact
  `-skipfmv -level 100` argument vector, and one checkpoint name;
- row VA, original bytes, patched bytes, and the bytes applied on that side;
- exact pristine, product, executable, options, both copied-save, and log
  SHA-256 values;
- proxy version 2, positive `firstframe`/`maxframes`, digest, texture hash, and
  strict-coverage settings; and
- copied-profile truth, one-process peak, `collision=false`, terminal-zero
  process list, and confirmed proxy removal.

The stock executable must equal the named product hash and have zero staged
rows. The staged executable must differ from product and list exactly the one
requested row. Stock and staged pristine/product/options/save hashes must match.
The log header must agree with the sidecar, and `# detach` must be its final
non-empty line.

## Fail-closed boundaries

A draw is excluded by a named count when it is screen-space/unknown FVF, uses an
UP path, lacks a bound-texture content hash, lacks a required digest, is
provisional, lacks stream stride, or has no matching `P` row. Unknown,
missing, default, multiply-derived, or wrong-slot matrices reject the run. A
missing/unknown texture factor, any nonzero or invalid `mtxuntracked`, a partial
or invalid active texture-transform record, and content after `# detach` also
reject. Duplicate draw anchors reject the run. Fault-injection logs, zero-frame
draw windows, hash drift, process collisions, non-terminal process state, and
a proxy left in place reject before comparison.

If more than one common stable camera ties for the largest match set, the tool
rejects until its printed camera identity is supplied explicitly. A complete
matched comparison with no mesh delta is valid negative evidence; it reports
`no_geometry_delta_at_matched_camera` rather than failing or inventing a visual
change. A changed mesh whose primitive/vertex/index/byte counts do not order
consistently reports `geometry_delta_detail_order_ambiguous`.

## Offline self-test

The fixtures are synthetic and stamped “not retail evidence”. Their stock and
staged logs deliberately use different matrix ids, pointers, generations,
texture serials, offsets, PIDs, and frame ranges while retaining the same
matrix and draw values. The staged fixture selects consistently larger
geometry.

```powershell
py -3 patches/validate_lod_attribution_tests.py
```

The suite covers the accepted comparison, deterministic/path-free receipts, an
exact no-delta negative, sidecar/log hash mismatch, `maxframes=0`, missing
matrix, non-static camera, missing IB digest, provisional digest, duplicate
anchor/digest, missing texture hash, unidentified shader/material state,
viewport drift, texture-factor drift/missing/unknown input, nonzero/invalid
untracked matrices, active texture-matrix value/flag drift, missing/unknown/
derived/wrong-slot texture transforms, invalid texture flags, terminal-detach
enforcement, missing refusal summary, and a failed CLI receipt. A failure still
writes `bea-lod-attribution-receipt.v1` with `ok=false` and a stable error code.

## Runtime comparison command

After the board steward grants the sole product GUI slot, capture one row family
at a time with positive draw windowing, digest, texture hashing, strict coverage,
and no vertex dump. Keep the complete raw logs, sidecars, and receipts under
ignored `local-lab/patch-surface-phase2/lod-attribution/`.

```powershell
py -3 patches/validate_lod_attribution.py `
  --stock-log <stock.log> --stock-run <stock.run.json> `
  --staged-log <staged.log> --staged-run <staged.run.json> `
  --row-va 0x00631E8C --min-stable-frames 3 --min-matched-draws 1 `
  --output <receipt.json>
```

Exit `0` means the receipt is internally comparable, not that the named patch
effect is promoted. Promotion still requires the exact staged bytes, a matched
camera and unique draw anchor, a changed mesh with direction consistent with
the row’s retained falsifier, complete terminal-zero restore receipts, TSV
validation/histogram/pristine sweep, and independent same-card review. Any
other outcome remains `STATIC_ONLY` and records the exact negative/error code.
