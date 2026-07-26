# Controlled copied-runtime observations — 2026-07-26

Date: 2026-07-26. Four questions that static reading could not settle, settled by
reading a running copy under CDB. Each had blocked for hours or days on a
decompiler limitation, an unresolvable indirect call, or a constant whose units
are simply not present in the image.

## Specimen and safety

Every observation below was taken from
`local-lab/safe-copy-bea-pristine/BEA.exe`, sha256
`E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4`. The pristine
original sits beside it as `BEA.exe.original.backup`, sha256 `74154BFA…`, and was
never opened. The Steam install was never launched, attached to, or read.
`lm m BEA` reports base `00400000`, so there is no VA translation anywhere below.

**Breakpoints and memory reads only. Nothing was ever written to the debuggee.**

Raw debugger logs are untracked by project rule and live under
`local-lab/cockpit-worldmatrix-2026-07-26/`,
`local-lab/terrain-lightstate-2026-07-26/` and
`local-lab/mesh-lighting-mode-2026-07-26/`, alongside the full working notes:
`COCKPIT-WORLD-MATRIX-RUNTIME-2026-07-26.md`,
`TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md`,
`MESH-LIGHTING-MODE-RUNTIME-2026-07-26.md` and
`COCKPIT-CLEAN-MASK-FIT-2026-07-26.md`.

## The technique, because it generalises

Two shapes, both reusable, both now committed as tools.

**Breakpoint window** — `tools/cdb_worldmatrix_probe.ps1`. Arm the expensive
breakpoint on entry to a wrapper that has exactly one caller in the image, and
disarm it on that wrapper's return address. Everything outside the window runs
untrapped. For the cockpit that is: arm at `0x0053bb50`, break at `0x00551043`,
disarm at `0x0053ec6f` — and the game still runs at ~77 fps, which is what makes
a scripted playthrough to Level 100 survivable.

**Hit-scheduled** — `tools/cdb_lightstate_probe.ps1`. For a site that fires once
per frame, no window is needed; schedule on the nth hit.

`tools/cdb_meshmode_probe.ps1` is a third instance of the same pattern.

The game is driven to Level 100 by scripted input. `Capture-Retail.ps1` kills the
target in a `finally` block and cannot be reused for an attached session, so
`local-lab/cockpit-worldmatrix-2026-07-26/Drive-RunningRetail.ps1` exists. The
one trap that blocked five earlier attempts is an idle timeout on the
click-to-start page, documented in `local-lab/STARTUP-FLOW-FINDINGS-2026-07-25.md`.

**Two address maps recovered along the way, which reduce any future "what state
was in force" question to a single read:** the render-state shadow is a
write-through array at `0x00855540` indexed `state * 4` (so `D3DRS_LIGHTING` is
`0x00855764`), and texture stage state is at `0x008557f0` indexed
`(type + stage * 30) * 4`.

## 1. The cockpit world matrix — not identity, and the contradiction never existed

`IDirect3DDevice9::SetTransform(D3DTS_WORLDMATRIX(0), M)` at the Level 100
cockpit draw. **Seven** uploads per cockpit render — seven draw batches. Batch 0,
D3D row-major, `det = +1.000000`, `|RRᵀ − I| = 1.9e-07`:

```
   0.88662648   0.46089223  -0.03836670   0
  -0.46159714   0.88701338  -0.01164191   0
   0.02866611   0.02803198   0.99919587   0
 288.67752    243.25581    -12.27214      1
```

`D3DTS_VIEW`, identical at all 21 records:

```
   0.87282735  -0.00000015  -0.48802879   0
   0.48802879   0.00000027   0.87282735   0
   0.00000000  -0.99999994   0.00000031   0
-370.68732    -12.11152    -71.42742      0.99999994
```

`D3DTS_PROJECTION` is `diag(1, 1.3333333, 1.0001428)` with `_34 = 1`,
`_43 = -0.10001428` — 90° horizontal at 4:3, near plane 0.1. That independently
reconfirms the camera FOV correction **at runtime**.

All seven matrices plus view and projection were **bit-identical across four
independent launches** and across cockpit frames 0, 2048 and 2400.

The translation is the camera world position, and `R_world · R_view` is the axis
map `x→x, y→z, z→−y` to within **2.8774°**. The cockpit is camera-attached, and
retail rotates its normals by the camera orientation — which is what the
reconstruction already does.

This retired a blocking contradiction rather than resolving it: the earlier
static claim that "both traceable world-matrix uploads are identity with zero
translation" was true of the **reset** at `0x0053ebb6` and false of the draw.
`CCockpit::Render` overwrites the matrix before any flush. See
[`cockpit-world-matrix-static-2026-07-26.md`](cockpit-world-matrix-static-2026-07-26.md),
a hand stack-frame trace performed blind to this capture, which independently
located the real upload at `0x004b697b` and agrees.

**Two of the seven batches carry a negative-determinant (mirrored) world
matrix** — `Rsidebit01` and `Lsidebit02`. The mirror is authored in the shipped
`HORI` bytes and retail's tool pre-reverses the index order inside mirrored
instances, so it is handled correctly.

Also confirmed: the cockpit root sits at the camera to **1.4e-4 units**, so
`RootOffset = Vector3.Zero` is right and `Camera01`'s `CPOS` is not the attach
point.

**Stated limit.** The camera does not move in Level 100 under any scripted input
— relative mouse-look, held `A` and held right-arrow all produced bit-identical
matrices. So this observes exactly **one** pose. It is the pose of the
t0+25065 ms parity frame, but it cannot demonstrate the matrix *tracking* the
camera; that rests on the structural facts above, not on observed variation.

## 2. The terrain light state — the two-light model is exact

Read on entry to `0x0053e688`, the single call site of `CDXLandscape::Render`.

**Enable array `0x009c68a0` = `[1, 1, 0, 0, 0, 0, 0, 0]` at every observation.**

| slot | direction `+0x14..+0x1c` | colour `+0x24/28/2c` | as `/256` |
| ---: | --- | --- | --- |
| 0 | `(-0.03407396, -0.90863329, +0.41620260)` | `0.73828125, 0.69140625, 0.47265625` | **(189, 177, 121)** — HFLD sun |
| 1 | `(+0.03407396, +0.90863329, -0.41620260)` | `0.13671875, 0.13671875, 0.21875000` | **(35, 35, 56)** — anti-sun |

Exact binary fractions, no rounding. Five observations — terrain draws 300 /
1200 / 2100 in run 1 (span **15.688 s**, measured with `.time`) and 200 / 2600 in
run 2 (span **17.981 s**) — with all 8 enable bytes and all 736 bytes of light
records **byte-identical** within each launch and between launches.

`sum = (224, 212, 177)/256`, so `2 × 0.8 × sum = (1.400000, 1.325000, 1.106250)`
— the reconstruction's implemented factor **to the last digit**.

Consequences: no third light, now falsified by observation rather than argument;
the two unresolved indirect calls at `0x0053e603`/`0x0053e644` provably do not
touch the enable array; retail's temporal flatness is explained, which localises
the reconstruction's terrain drift entirely to its own stages; and the constant
residual's degeneracy is broken — of "a missing stage-0 light" versus "stages 1–3
are 0.9/2.1/2.3 % dark", the first is eliminated.

Slot 2 still holds `0x3e75c290` ×3 = `0.24, 0.24, 0.24`, the `CFEPBEConfig`
back-light immediate, as **disabled stale residue** with a stale `+0x58`
(`0089be50` against `0053e5b3` for the two live slots). The front-end rig ran on
the way in and is provably not live at the draw — exactly as the static
falsification in
[`terrain-third-light-2026-07-26.md`](terrain-third-light-2026-07-26.md)
predicted.

**Stated limit.** This reads engine-side shadow state at the call, not the device
upload, `D3DRS_AMBIENT`, or the material. A transient light shorter than the gap
between dumps could go unseen; a static or slowly-varying extra light is
excluded, and that is the only kind the residual could have had.

### SCOPE CORRECTION 2026-07-26 — ITSELF WITHDRAWN, same day. See §5.

> **The correction printed below was wrong and is retained only so the reasoning
> is visible.** Its premise — that `D3DRS_LIGHTING = 0` at the terrain draw — was
> an instrumentation artefact. The gate at `0x0053e688` is the `call` instruction
> *before* `CDXLandscape::Render`; lighting goes `0 → 1` **inside** `Render`,
> before any primitive, and reads 1 on leaving. Breaking on the device calls
> instead of the state shadows shows `D3DRS_LIGHTING = 1` at the terrain draw and
> at the lit mesh draws alike.
>
> **The terrain ambient-light derivation therefore SURVIVES, mechanism confirmed
> at the device** — right number *and* right reason. See §5.
>
> The one durable point below is the scoping instruction: §2's values genuinely
> are terrain-draw values and genuinely must not be carried to the mesh draws,
> because the mesh draws run a *different rig*. That turned out to matter far more
> than expected, and it is what §5 is about.

**These light values were read at `0x0053e688`, the TERRAIN draw, and §3's own
`SetRenderState` transition trace shows `D3DRS_LIGHTING = 0` at that draw.** The
light state was therefore validated at one of the few draws in the frame that is
explicitly *unlit*.

Two consequences, both live:

1. **Do not carry these values to the lit mesh draws.** The world and tree draws
   run with `D3DRS_LIGHTING = 1` and their light state was never read. The
   correct site is `0x00549570`, not `0x0053e688`. Any argument that reasons from
   §2's colours to the appearance of buildings, trees or the walker is currently
   unsupported.

2. **It sits in tension with the terrain ambient-light derivation** in
   [`terrain-ambient-light-applied-2026-07-26.md`](terrain-ambient-light-applied-2026-07-26.md),
   which concluded that retail draws terrain with lighting **active** through a
   terrain-only `D3DMATERIAL9` with ambient response 0.8. Both readings cannot be
   right as stated. That derivation produced a large measured parity gain
   (63.81 % → 52.20 % material), which is *not* evidence that its mechanism is
   correct — a wrong mechanism that lands on the right number is precisely the
   failure mode this project has hit before. **Unresolved and flagged rather than
   reconciled by argument.**

Three further quantities are unread at the lit mesh draws and any one of them
changes the answer: the enable array and records at `0x00549570`; the
`D3DLIGHT9` **Diffuse-versus-Ambient split** actually uploaded (the 0x5c-byte
engine records are not `D3DLIGHT9`, and that mapping is static-only); and the
`D3DMATERIAL9`, whose `EMISSIVE` and `SPECULARMATERIALSOURCE` are both
`D3DMCS_MATERIAL`, leaving `Emissive`, `Specular` and `Power` live and entirely
unmeasured.

## 3. Mesh lighting mode and stage-0 `COLOROP` — one fix falsified, one confirmed

Three launches, two level times, **4,393 mesh draws observed**.

| draws | mode `[0x00704e48]` | `D3DRS_LIGHTING` | inside |
| ---: | ---: | ---: | --- |
| 589 + 442 | **0** | **1** | `CRTTree::BuildRenderOutputs` — the pines |
| 493 + 134 | **0** | **1** | `CRTMesh::BuildRenderOutputs` — the static world |
| 27 + 19 | **4** | **1** | `CRTMesh`, a later pass |
| 7 | 0 | 1 | cockpit |
| 4 | 0 | 0 | first draw of each frame, before the pass turns lighting on |

The mode is **never 2, never 6, never 8**, and breakpoints planted on the mode-2
and mode-6 draw calls at `0x0054a423`/`0x0054a466` **never fired once**. A
cache-miss `SetRenderState` trace over a whole frame shows only 8
`D3DRS_LIGHTING` transitions: it goes `0→1` at the first `CRTMesh` render and
stays 1 across all 576 world and tree draws, dropping only for the terrain and
around the cockpit.

**This falsified a proposed fix before it shipped.** A static reading had
concluded that `CMeshRenderer::RenderMeshCore` clears `D3DRS_LIGHTING` for modes
2 and 6 and recommended a per-draw unlit flag. Retail's fixed-function pipeline
*is* lit for these meshes — `COLORVERTEX` default TRUE, `DIFFUSE`/`AMBIENT`
material source `D3DMCS_COLOR1`, `D3DRS_AMBIENT` = `0x000d0f2b` confirmed at
runtime. The mode-2/6 branches are dead code in Level 100; the live dispatch is
`0x00549915 → 0x0054a49e → call 0x0054d530`.

**Stage-0 `D3DTSS_COLOROP`, and this one confirmed a fix.** `4` =
`D3DTOP_MODULATE` on **all seven cockpit batches**, read 16 times inside the
cockpit window with **zero transitions**, against `5` = `MODULATE2X` for the 134
world and 442 tree draws. Independently confirmed on pixels by a geometric
intersection mask over 31,546 px: build × 0.5 takes clean-mask meanD from 42.51
to 11.42 and material from 98.93 % to 25.35 %, and exact 0.5 beats both the
least-squares scale 0.5249 and free per-channel scales `(0.478, 0.500, 0.557)`.

The 19 mode-4 static-world draws also run `MODULATE` in the same frame as 134
mode-0 `MODULATE2X` ones — a second measured site where an unconditional
doubling is 2× too bright. They were **not** mapped to any reconstruction draw:
they are a varying-count post-cockpit pass from `CRTMesh` objects that do not
correspond to the manifest's 28 authored meshes, and assigning them would have
been a fit rather than a measurement.

**Open, and not fitted:** `Lsidebit02` (batch 3, 366 px) wants the doubling kept
on pixels, but reads `MODULATE` like the other six batches with no per-batch
variation. Stage-0 `COLOROP` does not explain it.

## 4. The cloud-shadow scroll — a rate with no static derivation

`CDXLandscape__RenderTerrain` at `0x00545590` opens at `0x005455d2` with
`FLD [0x008a9e20]; FMUL [0x005d8580]; FADD [0x008c0294]; FST; FCOMP [0x005d8568]`
and the same for v via `[0x005e50e4]` into `[0x008c0298]` — rates `0.001` and
`0.0005`, wrapping at `1.0`.

Those constants are **per advance**, and they are multiplied by `[0x008a9e20]`
whose **26 references are all reads with no absolute writer anywhere in the
image**. Its units are therefore not present in the file, and neither is the
per-second rate. Whole-image scans find exactly five references to each
accumulator, all ten inside `RenderTerrain`, with no initialiser and no reset,
both addresses in the uninitialised tail of `.data`.

Read live at three level times: u = 0.058181878 / 0.20878051 / 0.35480464
(dwords `3d6e501f` / `3e55ca8f` / `3eb5a8f4`), with v exactly u/2 at all three,
and `[0x008a9e20]` = 0.14289856 / 0.14312744 / 0.14154053.

**du/dt = 0.0199944 and 0.0200088 per second** over the two intervals — 0.07 %
apart — while the per-*draw* rate differs by 3.1 %. Wall time is the stable
parameterisation, because the accumulator advances once per terrain draw and
terrain draws many tiles per frame.

Back-extrapolation puts u = 0 at process uptime 26.15 s against a level start of
≈26.3 s: **the accumulator's zero is the level's first frame, not process
start.**

This corrected two separate errors in the reconstruction — an origin taken from
engine time since launch (carrying the front end's 8.167 s), and a rate that had
been "corrected" from 0.02/0.01 down to 0.001/0.0005 on the strength of the
`.rdata` constants alone. **The original rates were right.** Only a runtime read
could distinguish them.

## Method note

Four of these observations either falsified a hypothesis outright or reversed an
earlier change. Two of them — the unlit flag and the cloud-scroll rate — would
have shipped as well-argued static readings and been wrong. On this codebase, a
static reading of a constant establishes what the bytes *are*; it does not
establish what they *mean* when the units are supplied at runtime by something
the image never writes.

## 5. The lit mesh draws — read at the DEVICE, and the trees run their own rig

Full record: `local-lab/LIT-MESH-LIGHT-STATE-2026-07-26.md`. Probe:
`local-lab/mesh-lighting-mode-2026-07-26/Run-LitMeshLightProbe.ps1`. Two launches,
gate frames 2400 and 800, same specimen and same read-only envelope.

This one broke on the **device calls rather than the state shadows**, which is
what made it decisive. `SetLight` has exactly three call sites in the image
(`0x005512e1` is the in-level one, inside `0x00551200`, which builds a 0x68-byte
`D3DLIGHT9` on the stack); `SetMaterial` has seven, all instrumented;
`LightEnable` is at `0x00551101`.

**`D3DRS_LIGHTING` is 1 at the lit mesh draws AND at the terrain draw.** The
earlier "terrain is unlit" reading was an artefact of gating on the `call`
instruction before `CDXLandscape::Render`. The same one-flush staleness makes
4–6 `RenderMeshCore`-entry reads per frame report a wrong ambient, which is worth
remembering for any future shadow-array read.

**The terrain ambient-light derivation is confirmed at the device.** `Render`
uploads both lights with `D3DLIGHT9.Ambient` = the light colour, sets
`D3DRS_AMBIENT := 0` and `DIFFUSEMATERIALSOURCE := MATERIAL`, installs the
material at `0x0083d28c` (`Diffuse = (0,0,0,1)`, `Ambient = (0.8,0.8,0.8,1)`),
draws, then re-uploads both lights with `Ambient = 0` and restores. So
`2 × 0.8 × sum(light.Ambient) = (1.400000, 1.325000, 1.106250)` is right for the
right reason, and **the terrain is the only consumer of a light ambient term in
the frame.**

**At the mesh draws the Ambient term is ZERO on both lights**; `Diffuse` carries
sun and anti-sun as recorded. The `D3DMATERIAL9` at every non-terrain draw
(`0x0083d248`, read at five sites in both runs) is `Diffuse = (1,1,1,1)`,
`Ambient = (0,0,0,1)`, **`Specular = (0,0,0,0)`, `Emissive = (0,0,0,0)`**,
`Power = 0.1`, with `SPECULARENABLE = 0`. That is a precise negative: the two
channels flagged as "live and unmeasured" are both zero.

### `D3DRS_AMBIENT` is not constant, and that is the answer

| draws | `D3DRS_AMBIENT` | light 0 | light 1 |
| ---: | --- | --- | --- |
| 130 `CRTMesh` static world | `0x000d0f2b` | HFLD sun, as recorded | anti-sun |
| **442 `CRTTree` close pines** | **`0x0039293e` = (57,41,62)/255** | **sun × 0.1, pointing straight DOWN `(0,0,+1)`** | **full anti-sun, pointing straight UP `(0,0,-1)`** |

The `0.1` is a shipped constant at `0x005d85c0`, applied in
`CRTTree::BuildRenderOutputs` at `0x004ddcb8`–`0x004ddd2f` alongside `1/256`; the
anti-sun block at `0x004ddd59` gets `1/256` only.

**So the buildings' law in the reconstruction already matches retail exactly,
3.32x step included — and the trees do not.** Under the tree rig,
`2 × (ambient + light)` gives up-face `(0.59472, 0.45985, 0.58081)` and down-face
`(0.72050, 0.59501, 0.92377)`: a step of `(1.21, 1.29, 1.59)`, luminance
**1.304**, against the reconstruction's 2.714 and retail's measured median
**1.144**. Predicted gains match gains measured off retail's own pixels to within
5 % on five of six channels.

**Retail's foliage undersides are BRIGHTER and BLUER than its tops. The
reconstruction has the sign backwards.** That is the black-slab cause, and it is
a per-draw rig difference rather than anything wrong with the geometry — the
world-path normal space was independently proven correct to float64 epsilon.

### The mode-4 draws are resolved, and must not be treated as visible geometry

Every mode-4 object pointer is also in the same frame's mode-0 `CRTMesh` set
(15/15 in run 4, 10/10 in run 5). Their state: `LIGHTING = 1`, **enable array all
zero**, `D3DRS_AMBIENT = 0`, `Emissive = 0` — so the lit vertex colour is
**exactly black** — with stage-0 `MODULATE`. It is a black second pass, shadow or
decal shaped. **Do not simply apply `MODULATE` to them**: their contribution
lives in the blend state, which was not read.

### Open caveat, stated rather than assumed away

`AMBIENT` and `DIFFUSEMATERIALSOURCE` are both `D3DMCS_COLOR1`, and the vertex
`COLOR1` values and the blend state were not read. If the tree cards carry
non-white vertex colour, the predicted gains move. Read those before scoring any
fix on pixels.
