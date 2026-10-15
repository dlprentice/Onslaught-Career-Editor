# The terrain residual is not a third light — the three-light path is a front-end page, and the residual is not constant in time

> Verdict: **two independent falsifications, both precise negatives.**
> (a) The three-light setup at `0x004505b0`–`0x00450b3f` is **slot 5 of the
> `CFEPBEConfig` vtable** — a front-end page render, not gameplay — and it
> cannot run at a terrain draw because `CDXLandscape::Render` has **exactly one
> caller in the whole image** and `CEngine::SetupLights`, which unconditionally
> disables lights 2–7, **dominates** it 208 bytes earlier in the same function.
> (b) Even if it were live, its third light is a **grey `0.24`**, which would add
> `+0.384` to every channel where the residual needs `+0.016 / +0.030 / +0.027`
> — 12–24x too large and achromatic where the residual is strongly chromatic.
> (c) A measurement across ten paired frames shows the residual is **not
> constant**: retail's terrain chain gain is flat to **sd 0.0018 / 0.0032 /
> 0.0028** over 23.1–34.1 s while the reconstruction's falls monotonically at
> **−0.12 / −0.22 / −0.22 % per second**. The "implied third light" therefore
> **more than doubles**, from `(2.1, 3.7, 3.4)/256` to `(5.3, 9.1, 7.9)/256`,
> over eleven seconds in which retail's terrain colour does not change. **No
> static light can do that.** **Nothing was changed and no factor was fitted.**

Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes — the **capture target**: pristine plus the
`force_windowed` patch and nothing else.
*(Corrected 2026-07-28. This line previously read "`BEA.exe`, SHA-256
`e1436ef7…`, 2,506,752 bytes (`local-lab/safe-copy-bea-pristine/BEA.exe`, read-only)". `e1436ef7` is **not** pristine —
the pristine specimen is `BEA.exe.original.backup`, SHA-256 `74154bfa…`, in
the same directory; see
[`retail-specimen-baseline.md`](retail-specimen-baseline.md) and
[`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md),
which records that the two file names are inverted in that directory.
Re-measured 2026-07-28: the two builds differ at exactly **four** bytes,
file offsets `0x12a644`–`0x12a647` = VA `0x0052a644`–`0x0052a647`
(`a1 f0 2d 66 00` → `b8 01 00 00 00`). No address cited anywhere in this
note falls in that range — the nearest are `0x005225ec` below and `0x0053e2e0`
above — and no disassembly quoted here decodes through it, so **every byte
claim below stands unchanged.** This is a specimen-label correction, not a
re-measurement.)* Read-only.
Image
base `0x00400000`. All disassembly is `capstone` linear decode of the capture-target
file through `tools/disasm_va.py`; all reference counts are whole-file
little-endian operand scans through `tools/operand_scan.py` and
`tools/call_xref_scan.py`. **The Ghidra database was not opened.** The
mechanism itself — terrain material `[1]` at `0x0083d28c`, `LANDSCAPE_LIGHTING`,
`ApplyCachedLight`'s ambient promotion, and the term
`2 x 0.8 x sum(light colour) / 256` — is
[already established](terrain-ambient-light-material-2026-07-26.md) and is not
re-derived here.

---

## 1. `CDXLandscape::Render` has one caller, and `SetupLights` dominates it

`tools/call_xref_scan.py` over the whole image:

```
=== direct rel32 references to 0x00545410 ===   (CDXLandscape::Render)
  CALL at 0x0053e688
  total: 1

=== direct rel32 references to 0x0044a2d0 ===   (CEngine::SetupLights)
  CALL at 0x0053e5b8
  total: 1
```

`operand_scan.py` finds **no data pointer** to either address in `.rdata` or
`.data`, so neither is dispatched virtually. Both call sites are inside the same
function, `0x0053e2e0`:

```
0053e5b6  8b cd              MOV  ECX, EBP
0053e5b8  e8 13 bd f0 ff     CALL 0x0044a2d0        ; CEngine::SetupLights
0053e5bd  8b 4d 18           MOV  ECX, [EBP+0x18]
0053e5c0  e8 2b 20 f5 ff     CALL 0x004905f0        ; dynamic timed lights (slots 2..7)
...
0053e675  38 9d a8 04 00 00  CMP  byte [EBP+0x4a8], BL
0053e67b  74 2d              JE   0x0053e6aa        ; no landscape -> skip
0053e67d  8b 95 70 04 00 00  MOV  EDX, [EBP+0x470]
0053e683  8b 4d 10           MOV  ECX, [EBP+0x10]
0053e686  57                 PUSH EDI
0053e687  52                 PUSH EDX
0053e688  e8 83 6d 00 00     CALL 0x00545410        ; CDXLandscape::Render
0053e68d  b9 50 75 9c 00     MOV  ECX, 0x009c7550
0053e692  e8 c9 52 01 00     CALL 0x00553960
0053e697  a1 50 8a 88 00     MOV  EAX, [0x00888a50]
0053e69c  68 48 d2 83 00     PUSH 0x0083d248        ; restore material[0]
0053e6a1  50                 PUSH EAX
0053e6a2  8b 08              MOV  ECX, [EAX]
0053e6a4  ff 91 c4 00 00 00  CALL dword [ECX+0xc4]  ; SetMaterial
```

The `SetMaterial(0x0083d248)` immediately after the call confirms `0x00545410`
is the terrain draw whose prologue swaps in `0x0083d28c`.

**Dominance.** Disassembling `0x0053e2e0` for 500 instructions and collecting
every `j*` target, **no branch target lies in `(0x0053e5bd, 0x0053e688]`**. The
only branch that crosses the span, `JE 0x0053e6aa` at `0x0053e67b`, jumps
*past* the terrain call. Therefore every execution that reaches `0x0053e688`
reached it by falling through `0x0053e5b8`. **`SetupLights` runs before every
terrain draw in the game, without exception.**

`SetupLights` is single-exit and branch-free at its tail — 190 decoded
instructions from `0x0044a2d0` contain no `RET` before `0x0044a5e8` and no
conditional jump that can skip it — and it writes the enable array
unconditionally:

```
0044a52a  88 1d a0 68 9c 00  MOV byte [0x009c68a0], BL   ; BL = 1
0044a584  88 1d a1 68 9c 00  MOV byte [0x009c68a1], BL
0044a590  c6 05 a2 68 9c 00 00  MOV byte [0x009c68a2], 0
0044a5be  c6 05 a3 68 9c 00 00  MOV byte [0x009c68a3], 0
0044a5c5  ... a4 ... 0        0044a5cc  ... a5 ... 0
0044a5d3  ... a6 ... 0        0044a5da  ... a7 ... 0
```

So at entry to `CDXLandscape::Render` the enable array is
**`[1, 1, 0, 0, 0, 0, 0, 0]`**, whatever any earlier code left behind.

### 1.1 What can re-enable a light between `SetupLights` and the draw

Whole-image `operand_scan.py` for `0x009c68a0`–`0x009c68a7` gives every writer
of the enable array. Grouped by owning function:

| owner | writes | identity |
| --- | --- | --- |
| `0x0044a2d0` | `a0..a7` | **`CEngine::SetupLights`** — the only HFLD-fed path |
| `0x004905f0` / `0x004903a0` | `a0+i` | dynamic **timed** lights, slots 2–7 |
| `0x00490780` | `a0`, `a0+i` | global enable/disable-all helper |
| `0x004505b0` | `a0`, `a1`, `a2` | `CFEPBEConfig` vtable slot 5 |
| `0x0045e0d0` | `a0`, `a1`, `a2` | `CFEPGoodies` vtable slot 5 |
| `0x0051e1b0` | `a0`, `a1`, `a2` | `CFEPMultiplayerStart` vtable slot 5 |
| `0x00522190` | `a0`, `a1`, `a2` | `CFEPWingmen` vtable slot 5 |
| `0x00482590`, `0x004ddc3f`, `0x00540c30`, `0x005528b0` | `a0`..`a2` | other, see below |

Taking the five callees that execute between `0x0053e5bd` and `0x0053e688`
(`0x004905f0`, `0x00513bc0`, `0x005513d0`, `0x00550b10`, `0x005441b0`) and
closing the direct-`CALL` graph over them reaches **12 functions**, of which
exactly **two** are enable-array writers: `0x004905f0` and its helper
`0x004903a0`. Every `CFEP*` path and every other writer is unreachable.

`0x004905f0` is the transient-effect light manager. It walks slots 2–7
(`EDX` starts at 2, `CMP ECX, 6; JL` at `0x004906b4`), decrements a countdown at
`[record+8]`, and for each slot **disables it first and re-enables it only if
the countdown survives**:

```
0049064f  c6 82 a0 68 9c 00 00  MOV byte [EDX+0x009c68a0], 0
0049065d  f3 a5                 REP MOVSD               ; record -> 0x009c6678 + n*0x5c
0049066a  c6 82 a0 68 9c 00 01  MOV byte [EDX+0x009c68a0], 1
...
0049067a  c7 00 00 00 00 00     MOV dword [EAX], 0      ; countdown expired
00490680  c6 82 a0 68 9c 00 00  MOV byte [EDX+0x009c68a0], 0
```

So the light state at the terrain draw is *exactly* `sun + anti-sun`, plus any
transient effect light currently alive. Its colours come from live game state,
not from the shipped height field.

**One honest gap.** Two indirect calls in the span, `CALL dword [EDX+0x18]` at
`0x0053e603` and `CALL dword [EAX+0x18]` at `0x0053e644`, were not resolved.
Neither can be a `CFEP*` slot 5 (those are slot 5, offset `+0x14`, of their
vtables, not `+0x18`), but the statement "nothing else touches the enable array"
is proved only for the direct call graph.

## 2. The three-light path is `CFEPBEConfig`, a front-end page

`0x004505b0` has **zero** `CALL` or `JMP` references in the whole image
(`call_xref_scan.py`) and **exactly one** data reference (`operand_scan.py`):
file offset `0x001dba50`, section `.rdata`, VA **`0x005dba50`**.

Walking back from `0x005dba50` to the first dword pointing into the RTTI region
finds `0x006139a8` at `0x005dba38`, the MSVC complete-object-locator that always
sits at `vtable − 4`. Its `+0xc` type-descriptor pointer is `0x00629c50`, whose
name string at `+8` is:

```
0x00629c58  .?AVCFEPBEConfig@@
```

So the vtable base is `0x005dba3c` and `0x004505b0` is **slot 5**. The same
walk over the other three-light writers:

| write site | vtable base | slot | class |
| --- | --- | ---: | --- |
| `0x00450a1b` | `0x005dba3c` | 5 | `.?AVCFEPBEConfig@@` |
| `0x0045f16c` | `0x005db998` | 5 | `.?AVCFEPGoodies@@` |
| `0x0051e7c0` | `0x005db8d0` | 5 | `.?AVCFEPMultiplayerStart@@` |
| `0x005225ec` | `0x005dba10` | 5 | `.?AVCFEPWingmen@@` |

**All four three-light setups are the same virtual slot of four different
front-end page classes.** `CFEPBEConfig`'s own vtable carries a secondary
locator `0x00613a28` at `+0x58` whose type descriptor names
`.?AVCFrontEndPage@@`, and the sibling vtables in the same `.rdata` block belong
to `CFEPBriefing`, `CFEPWingmen`, `CFEPGoodies` and `CFEPCommon`. This is the
menu system, and `CFEPBEConfig` is the mech-configuration page.

### 2.1 The rig it installs is a three-point studio rig, and it is hard-coded

The three light records are built by `0x004901e0`, which lays out
`record[+0x00] = arg0` (Type), `record[+0x14..0x20] = arg1..arg4`
(Direction), and `record[+0x24/+0x28/+0x2c] = arg5/arg6/arg7` — the colour
triple that
[`ApplyCachedLight` promotes into `D3DLIGHT9.Ambient`](terrain-ambient-light-material-2026-07-26.md#3-applycachedlights-third-argument-is-d3dlight9ambient).
The colour arguments are **immediates in `.text`**:

```
; light 0 -> 0x009c65c0, enabled at 0x00450a1b
00450986  68 90 c2 f5 3d     PUSH 0x3df5c290   ; 0.12  (b)
0045098b  68 90 c2 75 3e     PUSH 0x3e75c290   ; 0.24  (g)
00450990  68 90 c2 f5 3e     PUSH 0x3ef5c290   ; 0.48  (r)

; light 1 -> 0x009c661c, enabled at 0x00450a89
004509d4  68 90 c2 f5 3e     PUSH 0x3ef5c290   ; 0.48  (b)
004509d9  68 90 c2 75 3e     PUSH 0x3e75c290   ; 0.24  (g)
004509de  68 90 c2 f5 3d     PUSH 0x3df5c290   ; 0.12  (r)

; light 2 -> 0x009c6678, enabled at 0x00450b28
00450ad0  68 90 c2 75 3e     PUSH 0x3e75c290   ; 0.24  (b)
00450ad5  68 90 c2 75 3e     PUSH 0x3e75c290   ; 0.24  (g)
00450ada  68 90 c2 75 3e     PUSH 0x3e75c290   ; 0.24  (r)
```

`0x3df5c290 = 0.12`, `0x3e75c290 = 0.24`, `0x3ef5c290 = 0.48` exactly. That is a
warm key `(0.48, 0.24, 0.12)`, a cool fill `(0.12, 0.24, 0.48)` and a neutral
back light `(0.24, 0.24, 0.24)` — a model-viewer rig, with no reference to the
height field at all. `SetupLights`, by contrast, reads `0x006fbe44` /
`0x006fbe48` (HFLD `CHFD+0x107C` / `+0x1080`) and scales each byte by
`_DAT_005db060 = 0x3b800000 = 1/256`.

### 2.2 The rig is falsified twice over, independently of liveness

Applying the established term `2 x 0.8 x sum(light colour)` to the rig gives
`sum = (0.84, 0.72, 0.84)` and a factor of **(1.344, 1.152, 1.344)** — R equal
to B — against the measured implied factor **(1.457, 1.389, 1.147)**. If this
path ran at the terrain draw, retail's terrain would be *magenta-biased*. It is
not.

And as a *third* light on top of the two HFLD lights, `(0.24, 0.24, 0.24)` adds
`2 x 0.8 x 0.24 = +0.384` to all three channels, where the measured residual
needs `+0.016 / +0.030 / +0.027`. That is **12x to 24x too large**, and
achromatic where the residual is strongly chromatic. **The hypothesis fails on
the bytes even before liveness is considered.**

## 3. What colour a third light would have to be

The implemented factor is
`F = 2 x 0.8 x (224, 212, 177) / 256 = (1.400, 1.325, 1.106)` and the measured
shortfall at `t0+25065 ms` is
[`ours/retail = 0.9886 / 0.9776 / 0.9758`](terrain-ambient-light-applied-2026-07-26.md#2-the-transfer-function-before-and-after).
Since any additional light enters the same flat term, the required extra colour
is `C = 160 x (F / ratio − F)`:

```
t0+25065 ms   C = (2.59, 4.86, 4.39) / 256      normalised to R  (1.00, 1.88, 1.69)
```

**The shape is not what a plausible light looks like.** Nothing in the Level 100
height field is near it, in magnitude or in chromaticity:

```
CHFD+0x1078 fog           (216, 216, 252)      normalised to R  (1.00, 1.00, 1.17)
CHFD+0x107C sun           (189, 177, 121)                       (1.00, 0.94, 0.64)
CHFD+0x1080 anti-sun      ( 35,  35,  56)                       (1.00, 1.00, 1.60)
CHFD+0x1084               (232, 232, 255)                       (1.00, 1.00, 1.10)
CHFD+0x1088               (237, 237, 255)                       (1.00, 1.00, 1.08)
CHFD+0x108C ambient reg   ( 13,  15,  43)                       (1.00, 1.15, 3.31)
CHFD+0x109C               ( 33,  33,  61)                       (1.00, 1.00, 1.85)
```

Every candidate is either `G = R` or `G < R`; the residual demands `G ≈ 1.9 R`.
The ambient register `(13, 15, 43)` is also explicitly zeroed at `0x005454db`
and would contribute `+0.081 / +0.094 / +0.269` if it were not — five to ten
times too much, and blue-dominant. **No shipped colour reproduces the residual's
shape.**

## 4. The residual is not constant in time — the decisive measurement

`tools/terrain_transfer_probe.py` was re-run on ten frames from the same probe
capture set, against `hud-timeline-run1`, all with `--shift -1,0`. Nothing was
recaptured and no parameter was fitted.

```
   t (s)    retail chain gain        reconstruction gain      ours / retail
  23.072   1.400 1.291 1.071        1.387 1.269 1.051        0.991 0.983 0.981
  24.066   1.402 1.296 1.076        1.386 1.268 1.050        0.989 0.978 0.976
  25.065   1.400 1.295 1.075        1.384 1.266 1.049        0.989 0.978 0.976
  26.073   1.400 1.299 1.079        1.383 1.264 1.047        0.988 0.973 0.970
  27.072   1.398 1.298 1.077        1.382 1.263 1.046        0.989 0.973 0.971
  28.057   1.398 1.298 1.078        1.381 1.260 1.044        0.988 0.971 0.969
  29.072   1.400 1.300 1.079        1.379 1.258 1.042        0.985 0.968 0.966
  30.071   1.399 1.300 1.079        1.377 1.255 1.039        0.984 0.965 0.963
  32.071   1.401 1.298 1.078        1.371 1.247 1.033        0.979 0.961 0.958
  34.071   1.395 1.291 1.072        1.363 1.238 1.026        0.977 0.959 0.957

  retail  sd over the window        0.0018  0.0032  0.0028
  ours    sd over the window        0.0070  0.0093  0.0076
  ours/retail least squares slope  -0.122  -0.218  -0.219  percent per second
```

Retail's terrain chain gain is **flat to one part in 500** across eleven seconds.
The reconstruction's falls monotonically over the same frames, and the
reconstruction's own macro-probe input is unchanged
(`[108.1, 113.3, 158.9]` at 25.065 s, `[108.4, 113.6, 159.2]` at 34.071 s), so
the drift is inside the reconstruction's post-macro stages. Retail's gain
staying flat is simultaneously the control that frame alignment did **not**
degrade — a desync would move retail's number, not ours.

Converting each frame's residual into the third light it would require:

```
  t = 23.072 s   C = (2.10, 3.68, 3.37) / 256
  t = 25.065 s   C = (2.59, 4.86, 4.39) / 256
  t = 34.071 s   C = (5.26, 9.08, 7.93) / 256
```

**The required light more than doubles in eleven seconds while retail's terrain
colour does not change at all.** A static third light contributes a constant
`2 x 0.8 x C / 256`; it cannot produce this. A *transient* light (slots 2–7, the
only in-gameplay mechanism that could add one) is excluded too: those are
countdown-driven and would switch on and off, not ramp linearly for eleven
seconds — and the ramp is present continuously from at least `t = 16 s`, where
the reconstruction's own gain is 1.396 R, to `t = 38 s`, where it is 1.348 R, at
a constant `−0.00218 /s`.

**Therefore the third-light hypothesis is falsified as the explanation of the
measured residual.** At most it could account for a constant part, and the
constant part cannot be isolated from this data because the drift crosses
retail's flat value inside the window: extrapolating the reconstruction's linear
decline backwards puts `ours = retail` near `t ≈ 17.4 s`, which would mean the
reconstruction is *too bright* before that time and too dark after it.

## 5. A degeneracy this measurement cannot break

Even setting the drift aside, the transfer probe cannot distinguish a missing
stage-0 light from a too-dark stage-1..3 chain, because both are flat
multipliers over exactly the same pixels. The same numbers read the other way:

```
  retail total / predicted stage-0 factor   1.0000  0.9774  0.9720
  reconstruction stage-1..3 chain           0.9910  0.9570  0.9500
  ratio (retail's implied rest of chain)    1.0091  1.0213  1.0232
```

which says the reconstruction's stages 1–3 are 0.9 / 2.1 / 2.3 % dark — the
identical residual, attributed elsewhere, with the stage-0 lighting term exact
in R. **Nothing in a single-frame flat-gain measurement can separate these.**
The residual therefore remains open and is attributed honestly to "a flat
2 % deficit somewhere in the terrain chain, plus a real time-linear drift on the
reconstruction side", not to a light.

## 6. What would settle it

**One observation, and it is a runtime one:** read the eight bytes at
`0x009c68a0` and the eight `0x5c`-byte light records at `0x009c65c0` from a
copied-runtime instance at the moment `0x0053e688` is entered, at two level
times ten seconds apart. That gives the enabled set and every light colour
directly and ends the question in both directions — it confirms
`[1, 1, 0, 0, 0, 0, 0, 0]` (in which case there is no third light and the whole
residual belongs to the reconstruction) or it names the extra light and its
colour.

Failing that, the cheapest static discriminator is already spent: the
time-series above. The next most valuable thing is **not** more light work — it
is finding what in the reconstruction's terrain stages 1–3 changes at
`−0.22 % per second`, because that is a larger and better-evidenced defect than
the constant part.

## Reproduce

```bash
py -3 tools/call_xref_scan.py local-lab/safe-copy-bea-pristine/BEA.exe \
    0x00545410 0x0044a2d0 0x004505b0 0x0053e2e0
py -3 tools/operand_scan.py local-lab/safe-copy-bea-pristine/BEA.exe \
    0x009c68a0 0x009c68a1 0x009c68a2 0x009c68a3 0x009c68a4 0x009c68a5 0x009c68a6 0x009c68a7
py -3 tools/operand_scan.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004505b0
py -3 tools/pe_read_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x005dba38 --count 96 --as u32
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004505b0 --count 260 --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004901e0 --count 16 --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004905f0 --count 90 --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x0053e5b8 --count 80 --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x0044a4f0 --count 75 --bytes
py -3 tools/terrain_ambient_light_factor_probe.py
```

The time series, for each `t` in
`023072 024066 025065 026073 027072 028057 029072 030071 032071 034071`:

```bash
py -3 tools/terrain_transfer_probe.py \
  --retail      local-lab/retail-reference-pristine/level100-gameplay/hud-timeline-run1/level100-t${t}ms.png \
  --rebuild     local-lab/godot-captures/ambient-light-after/level100-t${t}ms.png \
  --macro-probe local-lab/godot-captures/al-probe-macro/level100-t${t}ms.png \
  --mask-probe  local-lab/godot-captures/al-probe-mask/level100-t${t}ms.png \
  --shift -1,0
```

## Gates

**No source file, asset, shader, test or pinned artefact was touched by this
work.** It is a read-only analysis of the capture-target specimen plus a re-run of an
existing probe over captures that already existed. No gate is affected and none
was re-run.

## CONFIRMED BY RUNTIME OBSERVATION, same day

The static falsification above was independently confirmed by reading the
engine's actual light state from a copied runtime. Full record and raw logs:
`local-lab/TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md` and
`local-lab/terrain-lightstate-2026-07-26/`. Reusable probe:
`tools/cdb_lightstate_probe.ps1`.

Read on entry to `0x0053e688` — the single call site of `CDXLandscape::Render` —
on the safe copy (sha256 `E1436EF7…`), base `00400000`, no VA translation.
Breakpoints and memory reads only; nothing was written to the debuggee.

**Enable array `0x009c68a0` = `[1, 1, 0, 0, 0, 0, 0, 0]` at every observation.**
The two live records:

| slot | direction `+0x14..+0x1c` | colour `+0x24/28/2c` | as `/256` |
| ---: | --- | --- | --- |
| 0 | `(-0.03407396, -0.90863329, +0.41620260)` | `0.73828125, 0.69140625, 0.47265625` | **(189, 177, 121)** — HFLD sun |
| 1 | `(+0.03407396, +0.90863329, -0.41620260)` | `0.13671875, 0.13671875, 0.21875000` | **(35, 35, 56)** — anti-sun |

Exact binary fractions, no rounding. Five observations — terrain draws 300 /
1200 / 2100 in run 1 (span **15.688 s**, measured with `.time`) and 200 / 2600 in
run 2 (span **17.981 s**) — with all 8 enable bytes and all 736 bytes of light
records **byte-identical** within each launch and between the two launches.

What this settles beyond the static argument:

- **No third light**, now falsified by observation.
- **The reconstruction's two-light model is exact.** `sum = (224, 212, 177)/256`
  gives `2 × 0.8 × sum = (1.400000, 1.325000, 1.106250)` — the implemented factor
  to the last digit. The light set, count and colours contain no error.
- **§4's honest gap is closed empirically.** The two unresolved indirect calls at
  `0x0053e603`/`0x0053e644` provably do not touch the enable array, because it
  reads `[1,1,0,…]` at the draw.
- **The residual's degeneracy is broken.** Of "a missing stage-0 light term"
  versus "our stages 1–3 are 0.9/2.1/2.3 % dark", the first is eliminated.
  Stages 1–3 are the only remaining line.
- **Retail's temporal flatness is explained and the drift is localised entirely
  to the reconstruction** — nothing on retail's lighting side moves.
- A precise positive worth keeping: slot 2 still holds `0x3e75c290` ×3 =
  `0.24, 0.24, 0.24`, the `CFEPBEConfig` back-light immediate, as **disabled
  stale residue** with a stale `+0x58` (`0089be50` against `0053e5b3` for the two
  live slots). The front-end rig ran on the way in and is provably not live at
  the draw — exactly as §5 predicted.

Stated limits: this reads engine-side shadow state at the call, not the device
upload, `D3DRS_AMBIENT`, or the material. Level 100, single camera pose,
`-skipfmv`. A transient light shorter than the gap between dumps could go
unseen; a static or slowly-varying extra light is excluded, and that is the only
kind the residual could have had.
