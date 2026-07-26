# The reconstruction's terrain drift is the cloud-shadow scroll, and the origin of that scroll is wrong

> Verdict: **the prime suspect is confirmed, quantitatively, and the residual is
> a different and much smaller defect.**
> (a) Over 16.06–42.06 s the reconstruction's post-macro terrain chain falls
> **−4.89 / −6.87 / −6.67 %**. A model built only from the shipped 256x256
> cloud-shadow texture, the captured per-pixel world UVs, and the scroll rates
> decoded from `.rdata`, reproduces **−4.73 / −6.59 / −6.33 %** — **96.5 / 95.8 /
> 95.0 %** of it, with **nothing fitted**.
> (b) Camera motion is eliminated as a cause to **0.2 %**: re-sampling the same
> pixels with the scroll frozen gives **+0.010 %** over the same 26 s.
> (c) The mechanism is retail's own — stage 2's texture matrix is
> `_11 = _22 = 1/256` with its translation row taken from two accumulators
> advanced by `dt x 0.001` and `dt x 0.0005` — but the reconstruction drives it
> from Godot's global `TIME`, whereas **retail's accumulators live at
> `0x008c0294`/`0x008c0298`, are referenced from nowhere but
> `CDXLandscape__RenderTerrain`, and are never reset**. Using the level clock
> instead of the engine clock drops the model from 96 % to **63 %**, which is how
> the origin was caught.
> (d) The unexplained 3–5 % remainder is **not a ramp**. It is six discrete
> **steps** of ±0.2–0.55 %, each landing on a frame where the terrain's screen
> coverage and mean world UV change, and it **nets to only −0.17 / −0.29 /
> −0.34 %** across the whole window.
> (e) With the runtime light dump having eliminated stage 0, **one scalar — the
> scroll phase — satisfies both of retail's stage-1..3 observables at once**: the
> constant `1.0091 / 1.0213 / 1.0232` brightness ratio *and* the flatness. The
> admissible phase is **5.0–13.5 s of accumulated scroll at level t = 25.065 s**,
> against the reconstruction's **33.233 s** — **1.1 % of the 1000-second cycle**.
> The constant residual and the drift look like **one defect**.
> **No constant, gain, offset or time-compensation term was introduced.**

Follows [terrain-third-light-2026-07-26.md](terrain-third-light-2026-07-26.md)
§6, which measured the drift and asked what changes at −0.22 % per second. §1–§4
answer that question from the drift alone and do not touch the constant
residual. §5 then takes the constant residual back up, because the runtime
light-state dump in `local-lab/TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md` broke
the [degeneracy](terrain-third-light-2026-07-26.md#5-a-degeneracy-this-measurement-cannot-break)
by observation: stage 0 is exact, so the residual is stages 1–3, and the same
scroll phase that produces the drift is tested against it. **No factor was
fitted to close the residual; one phase was solved for and reported with its
admissible interval.**

Specimen: `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes (`local-lab/safe-copy-bea-pristine/BEA.exe`, read-only). Image
base `0x00400000`. Disassembly is `capstone` linear decode through
`tools/disasm_va.py`; reference counts are whole-file little-endian operand
scans through `tools/operand_scan.py`. **No capture was taken, no build was run
interactively, and the Ghidra database was not opened.**

---

## 1. Localising the drift: it is in the post-macro chain, and it is measurable directly

The reconstruction already ships an analysis-only fragment tail, `chain`, that
replaces `ALBEDO` with `0.25 * detail1 * cloud * 2 * detail2 * 2` — the whole
post-macro chain with the macro term forced to one and both saturating `min()`
stages removed. `local-lab/godot-captures/inv-probe-chain/` holds it at 92
deterministic offsets, captured 2026-07-26 03:02, **after** the cloud-scroll
constants were corrected in `1806304f` (2026-07-25 23:33), so these frames carry
`0.001`/`0.0005` and not the earlier `0.02`/`0.01`.

Over the ten frames of the third-light measurement, the mean of that probe over
the paired terrain pixels falls monotonically:

```
   t (s)     chain probe (R G B)        ratio to t0
  23.072     0.9700  0.9469  0.9475     1.0000 1.0000 1.0000
  25.065     0.9678  0.9438  0.9448     0.9977 0.9967 0.9971
  29.072     0.9581  0.9321  0.9331     0.9877 0.9844 0.9848
  34.071     0.9518  0.9218  0.9225     0.9812 0.9734 0.9735

  least-squares slope   -0.1789  -0.2493  -0.2492  percent per second
```

against the shipping build's `−0.158 / −0.224 / −0.218 %/s` over the same
frames. The shipping path is *less* steep because its two `min()` stages clamp
part of the excursion away; the ordering **R shallower than G ≈ B** is identical
in both. The macro probe's mean over the same pixels is `113.3 / 118.6 / 163.9`
at 23.072 s and `113.4 / 118.7 / 164.1` at 34.071 s, so **the drift is entirely
inside `detail1 x cloud x detail2`.** Within that product only the cloud term
carries a clock.

## 2. What the bytes say the cloud stage is

`CDXLandscape__RenderTerrain` @ `0x00545590` opens by advancing two globals:

```
005455d2  d9 05 20 9e 8a 00   FLD   dword [0x008a9e20]     ; frame delta
005455d8  d8 0d 80 85 5d 00   FMUL  dword [0x005d8580]     ; 0x3a83126f = 0.001
005455de  d8 05 94 02 8c 00   FADD  dword [0x008c0294]     ; u accumulator
005455e4  d9 15 94 02 8c 00   FST   dword [0x008c0294]
005455ea  d8 1d 68 85 5d 00   FCOMP dword [0x005d8568]     ; 0x3f800000 = 1.0
005455f5  75 12               JNE   0x00545609
005455f7  d9 05 94 02 8c 00   FLD   dword [0x008c0294]
005455fd  d8 25 68 85 5d 00   FSUB  dword [0x005d8568]
00545603  d9 1d 94 02 8c 00   FSTP  dword [0x008c0294]
00545609  ...                 ; the same nine instructions for v, with
0054560f  d8 0d e4 50 5e 00   FMUL  dword [0x005e50e4]     ; 0x3a03126f = 0.0005
                              ; into 0x008c0298
```

`pe_read_va.py` reads `0x005d8580` as `6f 12 83 3a`, `0x005e50e4` as
`6f 12 03 3a` and `0x005d8568` as `00 00 80 3f` — `0.001`, `0.0005`, `1.0`. A
single conditional subtraction of 1.0 on a monotonically increasing accumulator
is `fract()`.

The matrix buffer at `0x00628258` is then zeroed whole
(`0x00545640: MOV ECX,0x10; XOR EAX,EAX; MOV EDI,0x628258; REP STOSD`) and
refilled per stage. For stage 2 (`D3DTS_TEXTURE2` = `0x12`):

```
0054591a  a1 94 02 8c 00      MOV  EAX, [0x008c0294]
0054591f  8b 0d 98 02 8c 00   MOV  ECX, [0x008c0298]
00545925  a3 78 82 62 00      MOV  [0x00628278], EAX        ; _31 = u
0054592f  c7 05 68 82 62 00 0 MOV  [0x00628268], 0          ; _21 = 0
00545939  c7 05 5c 82 62 00 0 MOV  [0x0062825c], 0          ; _12 = 0
00545943  c7 05 58 82 62 00 . MOV  [0x00628258], 0x3b800000 ; _11 = 1/256
0054594d  c7 05 6c 82 62 00 . MOV  [0x0062826c], 0x3b800000 ; _22 = 1/256
00545957  89 0d 7c 82 62 00   MOV  [0x0062827c], ECX        ; _32 = v
00545964  6a 12               PUSH 0x12
00545967  ff 92 b0 00 00 00   CALL dword [EDX+0xb0]         ; SetTransform
```

and `0x005458f6` sets `TEXCOORDINDEX` for stage 2 to `0`, the same landscape
X/Y pair stage 0 uses. So retail's stage-2 coordinate is exactly

```
    cloud_uv = world_uv / 256 + (u_accumulator, v_accumulator)
```

which is, line for line, what the reconstruction's shader already computes. The
`1/256` here is independently the same value
[the stage-flag census recorded](terrain-draw-stage-flags-2026-07-26.md#2-cdxlandscape__renderterrain--0x00545590--complete-stage-argument-census).

### 2.1 The accumulators only advance when terrain is drawn, and never reset

Whole-file operand scans:

```
=== 0x008c0294 ===  occurrences: 5   va 0x005455e0 0x005455e6 0x005455f9 0x00545605 0x0054591b
=== 0x008c0298 ===  occurrences: 5   va 0x00545617 0x0054561d 0x00545630 0x0054563c 0x00545921
```

**All ten references lie inside `CDXLandscape__RenderTerrain`.** There is no
initialiser, no reset on level load, and no other writer; `pe_read_va.py`
refuses both addresses, so they are in the uninitialised tail of `.data` and are
zero at image load. Retail's cloud phase at any moment is therefore
`0.001 x (sum of frame deltas over every terrain draw since the process
started)`, and terrain draws happen only through the single call site at
`0x0053e688` under the `has-landscape` branch — not while a `CFEP*` front-end
page is up.

## 3. The measurement: the scroll reproduces the drift

The model is a direct offline evaluation of the same expression, over the same
pixels:

* the cloud texture is the shipped
  `Assets/Level100/Textures/terrain-cloud-shadow.texture.aya`, inflated from its
  AYA records and decoded as a 256x256 DXT1 DDS;
* each terrain pixel's world position is recovered exactly from the existing
  `uv` probe (`fract(world/512)`, 2-unit resolution) refined by the `uvfine`
  probe (`fract(world/2)`, 1/128-unit resolution) as
  `world = 2*round((coarse - fine)/2) + fine`;
* the sample is bilinear with `repeat`, at `world/256 + scroll(TIME)`;
* `TIME` is the engine frame ordinal from the capture manifest divided by 60,
  because the rig launches with `--fixed-fps 60` (`FrontendCaptureRig.cs`,
  `CaptureFramesPerSecond`) and gameplay is armed at frame 490.

```
   t(s)  frame      n   measured chain          cloud model            residual meas/model
  16.060   1454   78338   0.9729  0.9531  0.9529    0.9704  0.9495  0.9491     1.00000  1.00000  1.00000
  17.067   1514   78338   0.9719  0.9517  0.9515    0.9694  0.9481  0.9477     1.00004  1.00002  0.99998
  18.060   1574   78338   0.9709  0.9502  0.9501    0.9683  0.9465  0.9463     1.00013  1.00004  1.00003
  19.074   1634   78338   0.9697  0.9486  0.9486    0.9671  0.9449  0.9448     1.00019  1.00006  1.00001
  20.080   1695   78338   0.9686  0.9470  0.9471    0.9658  0.9432  0.9432     1.00034  1.00017  1.00002
  21.073   1754   78338   0.9675  0.9454  0.9457    0.9647  0.9416  0.9418     1.00045  1.00023  1.00006
  22.080   1815   78335   0.9711  0.9485  0.9489    0.9635  0.9400  0.9402     1.00537  1.00520  1.00515
  23.072   1874   78335   0.9700  0.9469  0.9475    0.9623  0.9385  0.9388     1.00542  1.00516  1.00524
  24.066   1934   78335   0.9689  0.9454  0.9462    0.9612  0.9369  0.9373     1.00544  1.00516  1.00538
  25.065   1994   78335   0.9678  0.9438  0.9448    0.9600  0.9354  0.9358     1.00551  1.00523  1.00551
  26.073   2054   78335   0.9666  0.9422  0.9433    0.9588  0.9336  0.9342     1.00567  1.00544  1.00566
  27.072   2114   78553   0.9608  0.9360  0.9370    0.9575  0.9318  0.9326     1.00087  1.00062  1.00063
  28.057   2173   78553   0.9596  0.9342  0.9352    0.9561  0.9298  0.9307     1.00108  1.00087  1.00076
  29.072   2234   78553   0.9581  0.9321  0.9331    0.9545  0.9276  0.9285     1.00120  1.00111  1.00096
  30.071   2294   78553   0.9565  0.9299  0.9308    0.9529  0.9252  0.9260     1.00122  1.00125  1.00107
  31.058   2353   78553   0.9548  0.9274  0.9282    0.9511  0.9227  0.9233     1.00126  1.00135  1.00123
  32.071   2414   78552   0.9564  0.9283  0.9290    0.9490  0.9197  0.9202     1.00523  1.00553  1.00554
  33.071   2474   78552   0.9541  0.9251  0.9259    0.9468  0.9164  0.9169     1.00524  1.00561  1.00577
  34.071   2534   78396   0.9518  0.9218  0.9225    0.9443  0.9130  0.9134     1.00536  1.00578  1.00583
  35.064   2594   78393   0.9513  0.9203  0.9212    0.9419  0.9096  0.9101     1.00746  1.00791  1.00804
  36.063   2654   78393   0.9485  0.9165  0.9175    0.9392  0.9062  0.9068     1.00730  1.00758  1.00773
  37.063   2714   78393   0.9455  0.9127  0.9138    0.9364  0.9026  0.9034     1.00712  1.00729  1.00743
  38.063   2774   78220   0.9410  0.9072  0.9085    0.9339  0.8993  0.9004     1.00511  1.00496  1.00494
  39.070   2834   78220   0.9381  0.9034  0.9048    0.9314  0.8961  0.8974     1.00463  1.00434  1.00412
  40.064   2894   78220   0.9354  0.8997  0.9011    0.9291  0.8929  0.8945     1.00419  1.00373  1.00326
  41.063   2954   78187   0.9280  0.8913  0.8929    0.9269  0.8899  0.8918     0.99871  0.99774  0.99720
  42.062   3014   78187   0.9253  0.8876  0.8894    0.9246  0.8870  0.8890     0.99823  0.99692  0.99643

  total excursion   measured   model     explained   unexplained
    R               -4.894 %   -4.725 %   96.5 %      -0.169 %
    G               -6.873 %   -6.585 %   95.8 %      -0.288 %
    B               -6.666 %   -6.331 %   95.0 %      -0.335 %
```

The residual column is **flat to about 1e-4 within each block** — over
16.060–21.073 it moves by 4.5e-4, over 27.072–31.058 by 3.9e-4 — and moves only
in jumps. There is no leftover ramp to attribute to anything else.

### 3.1 Three controls

| control | result |
| --- | --- |
| **Camera motion.** Re-sample the same pixels and the same world UVs with the scroll frozen at the first frame. | `+0.010 %` over 26 s in all three channels, against `−4.9 / −6.9 / −6.7 %`. Camera motion and terrain re-tessellation contribute **0.2 %** of the excursion. Every candidate that moves with the camera — detail-layer UV drift, LOD ring re-composite as a *ramp*, macro-level selection — is eliminated by this one number. |
| **Time origin.** Re-run with `TIME` = the level offset instead of the engine frame. | Explains only `63.4 / 66.4 / 67.6 %`. The correct origin is the engine clock, which leads the level clock by `490/60 = 8.167 s`. |
| **Chromaticity.** The drift's shape is R shallower than G ≈ B. | The cloud texture's mean over the sampled region is `(0.9716, 0.9511, 0.9507)` — R distinct, G and B equal to 4e-4. A grey layer could not produce the measured ordering; this one does, without being asked to. |

### 3.2 The remainder is steps, not a ramp — which is the LOD discriminator, resolved

Six frames carry a discontinuity in the residual, and every one of them is a
frame where the terrain's screen coverage **and** its mean world UV change:

```
  frame pair        residual step (R)    n            mean world U
  21.073 -> 22.080     +0.49 %       78338 -> 78335   284.1325 -> 284.1324
  26.073 -> 27.072     -0.48 %       78335 -> 78553   284.1334 -> 284.1485
  31.058 -> 32.071     +0.40 %       78553 -> 78552
  34.071 -> 35.064     +0.21 %       78396 -> 78393
  37.063 -> 38.063     -0.20 %       78393 -> 78220
  40.064 -> 41.063     -0.55 %       78220 -> 78187   284.2202 -> 284.2141
```

Between them the mean world UV is constant to 1e-4 world units — the camera is
effectively parked over this window — and then steps. This is exactly the
signature the LOD hypothesis predicts and the cloud hypothesis does not: a
re-composite at a ring crossing **steps**, it does not ramp. The steps alternate
in sign, do not accumulate, and net to `−0.17 / −0.29 / −0.34 %` over 26 s
against the scroll's `−4.7 / −6.6 / −6.3 %`. **They are a real second defect,
roughly 20x smaller, and they are left open.**

## 4. Why retail is flat over 23–34 s, and why that is not yet settled

Retail's terrain chain gain is flat over `23.072–34.071 s` to sd
`0.0018 / 0.0032 / 0.0028`. Retail runs the same scrolling cloud stage — §2 is
retail's own code — so flatness is a statement about **phase**, not about
absence.

Sweeping the model over a full 1000-second scroll cycle (the wrap period of
`u` at `0.001/s`) over the terrain pixels of `t = 25.065 s`:

```
  spatial mean of the cloud layer, peak to peak   14.4 / 18.2 / 16.7 % of its mean
  per-second slope of that mean, rms              0.068 / 0.086 / 0.078 % per second
  fraction of the cycle with |slope| < 0.02 %/s   59.0 / 49.0 / 47.5 %
  fraction of the cycle with |slope| < 0.12 %/s   88.0 / 83.5 / 87.0 %
```

Roughly half the cycle is flat to well inside retail's measured sd, and the
reconstruction's captured window sits at scroll `u = 0.0242..0.0502`, close to
the steepest part of the curve. **Retail being flat and the reconstruction
ramping are consistent with one texture, one rate and two different phases.**

This is not proof, and it is deliberately not claimed as any. Retail's phase at
level `t = 0` is `0.001 x (accumulated terrain-draw time since process start)`,
a quantity nothing in the captures records. Retail's own gain over the wider
`16–42 s` window is not flat either — it rises 3–5 % to `t = 24 s` and falls
7 % after `t = 38 s` — but that window also has retail's terrain coverage moving
from 76,050 to 71,150 paired pixels, so it cannot be read as a clean phase
signal.

**What would settle it, and it is one runtime read:** dump the two floats at
`0x008c0294` and `0x008c0298` from a copied-runtime instance at two known level
offsets. That gives retail's phase and its rate at once, confirms or refutes
`0.001/0.0005 per second of terrain-draw time`, and turns the phase argument
above into a measurement. The breakpoint is already in use — the light-state
probe in `local-lab/TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md` halts at
`0x0053e688`, which is 208 bytes past the accumulator update and inside the same
function. Adding `dd 0x008c0294 L2` and `dd 0x008a9e20 L1` to that same dump
costs nothing and answers §5 outright.

## 5. One scalar explains both of retail's stage-1..3 observables

The runtime light dump (`local-lab/TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md`)
reads `0x009c68a0` as `[1,1,0,0,0,0,0,0]` at every observation and the two live
colours as exactly `(189,177,121)/256` and `(35,35,56)/256`, so
`2 x 0.8 x sum = (1.400000, 1.325000, 1.106250)` — the reconstruction's
implemented stage-0 factor to the last digit. That **breaks the degeneracy**
recorded in [terrain-third-light §5](terrain-third-light-2026-07-26.md#5-a-degeneracy-this-measurement-cannot-break):
the residual is not a missing light, it is entirely stages 1–3, and retail's
implied stage-1..3 chain is **`1.0091 / 1.0213 / 1.0232`** times the
reconstruction's.

Retail therefore presents two independent stage-1..3 observables: that constant
ratio, and flatness to sd `0.0018 / 0.0032 / 0.0028` over 23–34 s. If the
reconstruction's **only** stage-1..3 error is the scroll phase, then a single
scalar `phi` — retail's accumulated scroll at that frame — must satisfy both,
with no per-channel freedom. Testing that over the whole 1000-second cycle, on
the terrain pixels of `t = 25.065 s`, where the reconstruction's own phase is
`1994 / 60 = 33.233 s`:

```
   phi (s)   cloud mean ratio to ours      max abs error     local slope %/s
             R       G       B             vs the target     R        G        B
      0.0   1.0128  1.0207  1.0218           0.00371       +0.025  +0.049  +0.042
      5.0   1.0142  1.0230  1.0235           0.00506       +0.020  +0.028  +0.022
     10.0   1.0152  1.0241  1.0243           0.00615       +0.020  +0.012  +0.003
     15.0   1.0158  1.0240  1.0235           0.00670       -0.011  -0.037  -0.052
     20.0   1.0143  1.0207  1.0198           0.00523       -0.057  -0.103  -0.104
     25.0   1.0101  1.0140  1.0131           0.01010       -0.112  -0.156  -0.150
     33.2   1.0003  1.0004  1.0004           0.02281       -0.123  -0.173  -0.164   <- ours

  target ratio (retail stage-1..3 / ours)   1.0091  1.0213  1.0232
  ratio span over the whole cycle           R 0.896-1.042  G 0.884-1.069  B 0.898-1.068
  admissible phi: ratio matched to <0.01 in every channel AND |slope| < 0.03 %/s
      phi in [5.0, 13.5] s, plus a 1-second sliver at 361.5 s
      = 1.1 % of the 1000-second cycle
```

**One scalar, three channels, two observables, and the admissible set is
1.1 % of the cycle.** The reconstruction's phase, `33.233 s`, is not in it; the
level clock alone, `25.065 s`, is not in it either (it is at the boundary,
already predicting a `−0.11 / −0.16 / −0.15 %/s` drift retail does not show).
Retail's accumulator holds **5.0–13.5 s** of scroll where ours holds 33.2 s.

This is a fit of one parameter, and it is reported as one. What makes it worth
stating is that the parameter was not free to move: it had to hit a
three-channel ratio *and* a slope bound simultaneously, and nowhere else in the
cycle does. Two caveats bound it: it assumes the whole stage-1..3 residual is
the cloud term (if the detail layers carry part of it the interval moves), and
it uses the reconstruction's pixel set as a proxy for retail's.

The consequence for the reconstruction is that **removing the 8.167 s front-end
lead is necessary but not sufficient** — `phi = 25.065` is still excluded. Either
retail's accumulator starts partway into the level, or `0x008a9e20` is not the
frame delta in seconds. Its 26 whole-image references are **all reads**; like
`DAT_008554fc` it has no absolute writer and is reached through a base pointer,
so its units cannot be settled from the file. That is the second half of what
the runtime read above would answer.

## 6. What this changes, and what it deliberately does not

The scroll's **rate, scale, texture and coordinate are already byte-exact** and
were not touched. What is wrong is the **origin**: the shader drives the offset
from Godot's `TIME`, which is engine time since launch. In the capture rig that
already leads retail's clock by the 490 front-end frames — 8.167 s at
`--fixed-fps 60` — and in ordinary play it leads by however long the player
spent in menus, without bound, because retail's accumulators advance only inside
`RenderTerrain` (§2.1). Two runs of the same mission that differ only in menu
time would render the terrain at different brightness.

The correct implementation is a pair of accumulators advanced once per terrain
draw by that frame's delta. `Level100TerrainAppearanceAsset.Update` is not given
a frame delta, and its only caller is `FirstFlightWorldView`, which is owned
elsewhere and which already has `frameDelta` in hand at the call site. **The
change therefore has to be made together with that caller and is reported, not
made here.** What was changed is documentation and a test:

- `Level100TerrainAppearanceAsset.cs` — the cloud-scroll comment now carries the
  full stage-2 matrix derivation (`0x0054591a`–`0x00545967`), the accumulator
  addresses and their five-reference scan, and the origin divergence as a named
  known defect. No shader expression changed.
- `Level100TerrainCompositorTests.TerrainShaderPinsTheRetailDetailRotationAndCloudScrollConstants`
  — extended to pin `world_uv / 256.0 + cloud_scroll` and the two accumulator
  addresses, so the coordinate cannot silently acquire a compensation term.

**No gain, offset, fudge factor or time-compensation constant was added, and the
constant part of the terrain residual was not touched.**

## Reproduce

```bash
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x005455d2 --count 45 --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x00545800 --count 90 --bytes
py -3 tools/operand_scan.py local-lab/safe-copy-bea-pristine/BEA.exe 0x008c0294 0x008c0298
py -3 tools/pe_read_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x005d8580 --count 4 --as u32
py -3 tools/pe_read_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x005e50e4 --count 4 --as u32
py -3 tools/pe_read_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x005d8568 --count 4 --as u32
py -3 tools/pe_read_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x008c0294 --count 8   # refuses: uninitialised .data
```

The pixel measurement is the script below. It reads only
`local-lab/godot-captures/inv-probe-{chain,macro,mask,uv,uvfine}/` and the
shipped cloud texture, and writes nothing. Save it as
`tools/terrain_cloud_scroll_probe.py` to run it in place; `--frozen-scroll` and
`--time-origin level` are the two controls in §3.1.

```python
#!/usr/bin/env python3
"""Reproduce the reconstruction's terrain temporal drift from the cloud-shadow
scroll alone. Read-only over existing captures and the shipped texture.

  measured  = mean of the 'chain' probe (0.25 * detail1 * cloud*2 * detail2*2)
              over the terrain pixels of each frame, x4.
  model     = mean of the shipped cloud texture, sampled bilinearly at
              (world_uv / 256 + scroll(TIME)) over exactly those pixels, with
              world_uv recovered from the 'uv' + 'uvfine' probes and
              TIME = engine frame ordinal / 60 (--fixed-fps 60).

Nothing is fitted. --frozen-scroll re-samples with the first frame's scroll to
isolate camera motion; --time-origin level uses the level offset instead of the
engine frame, which is the divergence the finding is about.
"""
import argparse
import io
import json
import struct
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
CAP = REPO / "local-lab/godot-captures"
CLOUD_AYA = REPO / (
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/"
    "terrain-cloud-shadow.texture.aya")
# .rdata 0x005d8580 = 0.001, 0x005e50e4 = 0.0005, wrap 0x005d8568 = 1.0;
# stage-2 texture matrix _11 = _22 = 0x3b800000 = 1/256 at 0x00545943.
SCROLL_U, SCROLL_V, CLOUD_SCALE = 0.001, 0.0005, 256.0
OFFSETS = [16060, 17067, 18060, 19074, 20080, 21073, 22080, 23072, 24066,
           25065, 26073, 27072, 28057, 29072, 30071, 31058, 32071, 33071,
           34071, 35064, 36063, 37063, 38063, 39070, 40064, 41063, 42062]


def load_png(path):
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"), dtype=np.float64)


def load_cloud():
    source = CLOUD_AYA.read_bytes()
    dds, pos = bytearray(), 0
    while pos < len(source):
        (n,) = struct.unpack_from("<I", source, pos)
        pos += 4
        dds += zlib.decompress(source[pos:pos + n])
        pos += n
    assert dds[:4] == b"DDS " and bytes(dds[84:88]) == b"DXT1"
    with Image.open(io.BytesIO(bytes(dds))) as image:
        return np.asarray(image.convert("RGB"), dtype=np.float64) / 255.0


def bilinear(tex, u, v):
    h, w, _ = tex.shape
    x, y = u * w - 0.5, v * h - 0.5
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    x0, y0 = x0 % w, y0 % h
    x1, y1 = (x0 + 1) % w, (y0 + 1) % h
    return ((tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx) * (1 - fy) +
            (tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx) * fy)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-scroll", action="store_true")
    parser.add_argument("--time-origin", choices=["engine", "level"],
                        default="engine")
    args = parser.parse_args(argv)

    cloud = load_cloud()
    frame_of = {s["levelOffsetMs"]: s["frame"] for s in
                json.loads((CAP / "inv-probe-chain" / "capture-manifest.json")
                           .read_text())["shots"]
                if s.get("levelOffsetMs") is not None}

    rows = []
    for ms in OFFSETS:
        name = f"level100-t{ms:06d}ms.png"
        uv = load_png(CAP / "inv-probe-uv" / name) / 255.0
        fine = load_png(CAP / "inv-probe-uvfine" / name) / 255.0
        mask = load_png(CAP / "inv-probe-mask" / name)
        macro = load_png(CAP / "inv-probe-macro" / name)
        chain = load_png(CAP / "inv-probe-chain" / name) / 255.0 * 4.0
        keep = ((mask[:, :, 0] >= 250.0) & (mask[:, :, 2] <= 5.0) &
                (mask[:, :, 1] / 255.0 > 0.5) & (macro.min(axis=2) > 8.0))
        # world = 2*round((coarse - fine)/2) + fine, exact to 1/128 unit
        coarse = uv[keep][:, :2] * 512.0
        small = fine[keep][:, :2] * 2.0
        world = 2.0 * np.round((coarse - small) / 2.0) + small
        seconds = (frame_of[ms] / 60.0 if args.time_origin == "engine"
                   else ms / 1000.0)
        rows.append((ms, seconds, world, chain[keep].mean(axis=0),
                     int(keep.sum())))

    model = []
    for _, seconds, world, _, _ in rows:
        s = rows[0][1] if args.frozen_scroll else seconds
        u = np.mod(world[:, 0] / CLOUD_SCALE + (s * SCROLL_U) % 1.0, 1.0)
        v = np.mod(world[:, 1] / CLOUD_SCALE + (s * SCROLL_V) % 1.0, 1.0)
        model.append(bilinear(cloud, u, v).mean(axis=0))
    model = np.array(model)
    measured = np.array([r[3] for r in rows])

    print(f"time origin: {args.time_origin}"
          f"{'   scroll frozen at the first frame' if args.frozen_scroll else ''}")
    print("   t(s)  frame      n   measured chain          cloud model"
          "            residual measured/model")
    base = measured[0] / model[0]
    for i, (ms, _, _, m, n) in enumerate(rows):
        res = (m / model[i]) / base
        print(f"  {ms / 1000:6.3f} {frame_of[ms]:6d} {n:7d}  "
              f"{m[0]:7.4f}{m[1]:8.4f}{m[2]:8.4f}   "
              f"{model[i][0]:7.4f}{model[i][1]:8.4f}{model[i][2]:8.4f}   "
              f"{res[0]:9.5f}{res[1]:9.5f}{res[2]:9.5f}")

    print()
    print("total excursion over the window, first frame to last")
    for i, name in enumerate("RGB"):
        me = measured[-1, i] / measured[0, i] - 1.0
        mo = model[-1, i] / model[0, i] - 1.0
        print(f"  {name}: measured {100 * me:+.3f} %   model {100 * mo:+.3f} %   "
              f"explained {100 * mo / me:.1f} %   unexplained "
              f"{100 * (me - mo):+.3f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

## Gates

No shader expression, asset, pinned artefact or capture was changed. The only
source changes are a comment block in
`rebuild/OnslaughtRebuild.Godot/Level100TerrainAppearanceAsset.cs` and three
added assertions in
`rebuild/OnslaughtRebuild.Client.Tests/Level100TerrainCompositorTests.cs`. The
gate for those is the rebuild client test suite.
