# The terrain material record and the `LANDSCAPE_LIGHTING` gate — both loose ends are live

Status: active static contract
Last updated: 2026-10-22 (retail disassembly listings replaced by prose and tables; earlier: 2026-09-26 RE audit of ALPHAOP, cardid.txt overrides and the reference count)
Summary: the terrain draw's material record, the LANDSCAPE_LIGHTING and landscape_method defaults, and the resulting lighting factor; the per-GPU tweak file can override both defaults.
Evidence: MEASURED — pristine instructions and the shipped `cardid.txt`; the runtime shadow read is cited in section 5.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; `cardid.txt` SHA-256 prefix `9855bf65364050d1`.

> Verdict: **the two loose ends interlock exactly as suspected, and together they
> are a flat, coloured, terrain-specific multiplicative factor applied outside
> the macro cache and outside the shipped texture stages.** The terrain-only
> material record at `0x0083d28c` is a real `D3DMATERIAL9` with a **black
> diffuse and an 0.8 grey ambient**; the gate at `0x008aa94c` is the value field
> of a console variable named **`LANDSCAPE_LIGHTING`** whose **default is 1**, so
> `RenderTerrain` does **not** disable lighting. With the ambient *register*
> zeroed, every enabled light's colour promoted into `D3DLIGHT9.Ambient` for this
> draw only, and terrain vertices carrying no normal, the surviving
> fixed-function term is a constant
> `0.8 x sum(light colour)`, which `D3DTOP_MODULATE2X` then doubles.
> Predicted factor from the shipped HFLD bytes: **(1.400, 1.325, 1.106)** against
> the measured **(1.457, 1.389, 1.147)** — magnitude within **3.6–4.6%**,
> chromaticity within **1.1%**. **No gain, offset, or tint was applied**; this
> note records the mechanism and its residual, not a change.

Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes — the **capture target**: pristine plus the
`force_windowed` patch and nothing else.
*(Corrected 2026-07-28. This line previously read "`BEA.exe`, SHA-256
`e1436ef7…`, 2,506,752 bytes (local pristine safe copy)". `e1436ef7` is **not** pristine —
the pristine specimen is `BEA.exe.original.backup`, SHA-256 `74154bfa…`, in
the same directory; see
[`retail-specimen-baseline.md`](retail-specimen-baseline.md) and
[`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md),
which records that the two file names are inverted in that directory.
Re-measured 2026-07-28: the two builds differ at exactly **four** bytes,
file offsets `0x12a644`–`0x12a647` = VA `0x0052a644`–`0x0052a647`
(`a1 f0 2d 66 00` → `b8 01 00 00 00`). No address cited anywhere in this
note falls in that range — the nearest are `0x00528b50` below and `0x0053e2e0`
above — and no disassembly quoted here decodes through it, so **every byte
claim below stands unchanged.** This is a specimen-label correction, not a
re-measurement.)*
Image base `0x00400000`. All
disassembly below is `capstone` linear decode of that file through
`tools/disasm_va.py`; all reference counts are whole-file little-endian operand
scans through `tools/operand_scan.py` and `tools/call_xref_scan.py`. The Ghidra
database was not opened or mutated.

## 0. The device is Direct3D **9**, and vtable `+0xc4` is `SetMaterial`

The unidentified call in
[the sun-colour note](terrain-sun-colour-route-2026-07-26.md) §6 is resolved by
the interface's own slot numbering. `0x00888a50` holds the device pointer. This
repository has already identified three of its slots from independent evidence:

| slot | prior identification | source |
| --- | --- | --- |
| `+0xac` | `Clear` | `ghidra-fullpass-findings/W009/adversarial/B03.md` |
| `+0xbc` | `SetViewport` | `ghidra-fullpass-findings/W009/adversarial/B04.md` |
| `+0xe4` | `SetRenderState` | [`d3d-fog-render-state-static-contract-2026-07-25.md`](d3d-fog-render-state-static-contract-2026-07-25.md) |

Under `IDirect3DDevice8` those methods sit at `+0x90`, `+0xa0` and `+0xc8`;
under **`IDirect3DDevice9`** they sit at exactly `+0xac`, `+0xbc` and `+0xe4`
(indices 43, 47, 57). All three agree only with D3D9. Two further slots used in
the terrain path corroborate it: `+0x10c` is index 67 =
`SetTextureStageState`, and `+0xcc` is index 51 = `SetLight` — the slot
`CDXEngine::ApplyCachedLight` calls with `(index, record)`.

Therefore **`+0xc4` is index 49 = `IDirect3DDevice9::SetMaterial`**, and the
argument is a `D3DMATERIAL9*`. `sizeof(D3DMATERIAL9)` is `0x44`, which is
precisely the difference between the terrain's argument `0x0083d28c` and every
other call site's `0x0083d248`: **the two are elements 1 and 0 of a
two-element material array.**

## 1. The material record — one writer in the whole image, and what it holds

`0x0083d248` is in the uninitialised tail of `.data` (`pe_read_va.py` refuses
it), so it is zero at load and holds its values only at runtime.

A whole-**file** scan of all 2,506,752 bytes for every little-endian dword in
`[0x0083d248, 0x0083d310)` returns **33 hits, all in `.text`**. One is a
coincidental encoding (`e9 d2 83 00 00`, `jmp 0x5c9c66` at `0x005c188f`, read as
`0x0083d2e9`); the other 32 fall on **four distinct addresses**:

| address | occurrences | form |
| --- | ---: | --- |
| `0x0083d248` | 16 | 11 `MOV ECX, imm` (thiscall), 5 `PUSH` (`SetMaterial`) |
| `0x0083d28c` | **1** | the terrain `PUSH` at `0x005454ec` |
| `0x0083d2d0` … `0x0083d2fc` | 12 | a separate 4x4 identity matrix, written by `0x004ebae0` |
| `0x0083d300` … `0x0083d308` | 3 | a separate zeroed triple, written by `0x004ebac0` |

**No address inside `0x0083d24c`–`0x0083d288` or `0x0083d290`–`0x0083d2cc`
appears anywhere in the image, in any section.** There is no `.data`/`.rdata`
pointer to the block either, so nothing can reach it except through the base.

Of the 11 `MOV ECX, 0x83d248` sites, ten call `0x004eb1e0` or `0x004eba30` —
neither of which uses `ECX` as a write base into the block (`0x004eba30`
ignores `ECX` entirely; `0x004eb1e0`'s `MOV ESI, ECX` is consumed once, at
`0x004eb568`, as a `this` for a further call). The eleventh is a thunk:

`0x004eb1d0` loads `ECX = 0x0083d248` (signature `b9 48 d2 83 00`) and jumps
to `0x004eb9a0`.

`0x004eb9a0` has exactly **one** reference in the image — that `JMP`
(`call_xref_scan.py`: 0 `CALL`, 1 `JMP`; `operand_scan.py`: 0 data pointers).
`0x004eb1d0` itself has 0 direct references and exactly one data pointer, the
dispatch-table slot at `0x00622708`. So `0x004eb9a0` is the **sole writer of the
block, always with `this = 0x0083d248`**, and it writes exactly `0x88` bytes =
two `D3DMATERIAL9`:

It stores, at `this = 0x0083d248`, the field values tabulated below: `1.0f`
(`0x3f800000`) and `0.0f` from two registers into the colour channels, `0.1f`
(`0x3dcccccd`) into `material[0].Power` at `+0x40`, and `0.8f` (`0x3f4ccccd`)
into `material[1].Ambient.rgb` at `+0x54`/`+0x58`/`+0x5c`, then returns at
`0x004eba24`.

| record | Diffuse | Ambient | Specular | Emissive | Power |
| --- | --- | --- | --- | --- | ---: |
| `[0]` `0x0083d248` — every other `SetMaterial` site | (1, 1, 1, 1) | (0, 0, 0, 1) | 0 | **0** | 0.1 |
| `[1]` `0x0083d28c` — **terrain only** | **(0, 0, 0, 1)** | **(0.8, 0.8, 0.8, 1)** | 0 | **0** | 0 |

**Emissive is zero in both, and neither record is coloured.** The
`D3DMATERIAL9`-emissive hypothesis is dead on the bytes. What is *not* dead is
the terrain record's inversion of the generic one: it deliberately kills the
diffuse term and keeps only an ambient response.

## 2. The gate — `0x008aa94c` is `LANDSCAPE_LIGHTING`, and it defaults to **1**

`0x008aa94c` is read three times in the image and written zero times by any
absolute-addressed instruction (`operand_scan.py`), all three inside
`CDXLandscape::RenderTerrain`. It is **not** `0x008aa920 + 0x2c`. The static
region `0x008aa920`–`0x008aa9a0` is an array of console-variable objects laid
out `{ +0x00 vtable, +0x04 next, +0x08 name, +0x0c value }`, registered by the
CRT static-initialiser stubs at `0x00544590`–`0x005445ff`, `0x00544600`–
`0x005446bf` and `0x00545560`:

| object | registration stub | name string | default |
| --- | --- | --- | ---: |
| `0x008aa920` | `0x00545560` | `landscape_method` (`0x00650e9c`) | 2 |
| `0x008aa940` | `0x00544690` | **`LANDSCAPE_LIGHTING`** (`0x00650ba8`) | **1** |
| `0x008aa950` | `0x00544660` | `LANDSCAPE_MAXLEVELS_USER` | 5 |
| `0x008aa960` | `0x00544630` | `LANDSCAPE_MAXLEVELS` | 5 |
| `0x008aa970` | `0x00544600` | `R32F_WORKS` | 0 |
| `0x008aa980` | `0x005445d0` | `LANDSCAPE_MINLOD_AT` | 0x100 |
| `0x008aa990` | `0x005445a0` | `LANDSCAPE_LOWRES_GEOM` | 0 |

`0x008aa940 + 0xc` = **`0x008aa94c`**. The constructor `0x00528aa0` writes the
default straight into `[this+0xc]`:

It stores the class vtable into `[this]`, the name argument into `[this+8]`,
links the object at the head of the registry `[0x0089c018]` through
`[this+4]`, replaces the vtable with `0x005e4a9c`, and writes the default-value
argument into `[this+0xc]` (`0x00528ac7`).

and `0x00544690` passes `PUSH 0x1`. So the earlier conclusion inverts on this
byte: `RenderTerrain`'s lighting-disable at `0x005455a2` is gated on
`LANDSCAPE_LIGHTING == 0`, and the default is **1**, so
**`D3DRS_LIGHTING` is left enabled for the terrain draw** unless the shipped
per-GPU table overrides it. The installer ships `cardid.txt`, and its ATI
Radeon 9700 section (devices 4145, 4146, 4E44, 4E64, 4E45 and 4E65) sets
`Tweak:LANDSCAPE_LIGHTING 0` (line 49). The executable applies a `Tweak:` line
to the named CVar when a `Device:` line has matched: the handler at
`0x005289a6-0x00528a5f` matches `Tweak:` (`0x0064bd60`) case-insensitively,
parses `%s %f`, and walks the CVar registry `[0x0089c018]` with `_stricmp`
(`0x00568390`). On those cards the terrain draws unlit.

The same value chooses the stage op at `0x00545675`. Taking the second gate
site in full:

- `0x0054564e`: if `USE_MODULATE_2X` (`[0x008554fc]`) is zero,
  `landscape_method` (`0x008aa920`) is set to 0 through `0x00528b50`.
- `0x00545661`–`0x0054566f`: unless `landscape_method == 2` (tested through
  `0x00527cc0`), it branches to the other landscape method at `0x00545af2`.
- `0x00545675`: if `LANDSCAPE_LIGHTING` (`[0x008aa94c]`) is non-zero, stage 0
  `COLOROP` becomes `MODULATE2X` (or `MODULATE` where unsupported) through
  `0x00513af0`; otherwise (`0x0054568a`) stage 0 `COLOROP` is set to
  `MODULATE` (4) through `0x00513870`.

The two branches are a coherent pair: *lighting off* means plain
`D3DTOP_MODULATE` against the implicit white vertex colour; *lighting on* means
`D3DTOP_MODULATE2X` against a lit vertex colour that is expected to sit near
0.5. The remaining stage setup is unconditional and decides the operands:

| Site | Stage 0 state | Value |
| --- | --- | --- |
| `0x00545699` | `D3DTSS_COLORARG1` (2) | `D3DTA_TEXTURE` (2) |
| `0x005456a8` | `D3DTSS_COLORARG2` (3) | `D3DTA_DIFFUSE` (0) |
| `0x005456b6` | `D3DTSS_ALPHAOP` (4) | `D3DTOP_DISABLE` (1) |
| `0x005456c5` | `D3DTSS_ALPHAARG1` (5) | `D3DTA_TEXTURE` (2) |

(`0x00513870` reads `Stage = [ESP+0x4]`, `Type = [ESP+0x8]`, `Value = [ESP+0xc]`,
shadows into `[0x008557f0 + (Type + Stage*30)*4]`, then calls device `+0x10c`.)

So stage 0 is **texture x vertex diffuse**, doubled.

`0x008554fc` is likewise a CVar value field: `0x008554f0 + 0xc`, registered at
`0x00511fe0` with name **`USE_MODULATE_2X`** (`0x0063dc24`) and **default 1**. It
is cleared only at `0x0051270f`, on the branch taken when
`[caps + 0x32f34] & 0x10` is absent — `D3DTEXOPCAPS_MODULATE2X`. On retail
hardware the flag stands and `landscape_method` keeps its default 2, except
where `cardid.txt` sets `Tweak:LANDSCAPE_METHOD 0`: the 3dfx Voodoo 5500 and
Voodoo 3 (line 250) and the S3 Savage4, Savage MX, ProSavage4 and Savage2000
(line 683). The NVIDIA section has neither tweak, so this note's factor applies
to unlisted adapters such as the NVIDIA capture host.

## 3. `ApplyCachedLight`'s third argument is `D3DLIGHT9.Ambient`

`CDXEngine::ApplyCachedLight` @ `0x00551200` zeroes a `0x68`-byte stack record
(`MOV ECX, 0x1a; REP STOSD` = 104 bytes = `sizeof(D3DLIGHT9)`), fills it from a
`0x5c`-byte cached record (`index*23*4` stride confirmed at `0x0055121d`–
`0x00551225`), and calls device `+0xcc` = `SetLight`. Mapping the stack writes
onto `D3DLIGHT9` (record base = `ESP+0x8`):

| stack | field | source |
| --- | --- | --- |
| `+0x08` | `Type` | derived from `src[+0x00]` |
| `+0x0c/0x10/0x14` | **`Diffuse.rgb`** | `src[+0x24/0x28/0x2c]` |
| `+0x1c/0x20/0x24` | `Specular.rgb` | `src[+0x24/0x28/0x2c]` |
| `+0x2c/0x30/0x34` | **`Ambient.rgb`** | `src[+0x24/0x28/0x2c]`, **only if `arg2 == 1`** |
| `+0x3c/0x40/0x44` | `Position` | `src[+0x04/0x08/0x0c]` |
| `+0x48/0x4c/0x50` | `Direction` | `src[+0x14/0x18/0x1c]` |
| `+0x54` | `Range` | `src[+0x30]` |
| `+0x64` | `Attenuation2` | `1 / (Range^2 * DAT_005d8578)` |

At `0x005512ac`–`0x005512bc` it compares the flag argument with 1 and, only when
equal, copies the cached colour triple `src[+0x24/+0x28/+0x2c]` into the
record's `Ambient.rgb` at `[ESP+0x2c/0x30/0x34]` (`0x005512be`–`0x005512cf`).

The `0x5c`-byte cached record's colour triple lives at `+0x24`, and the flag
argument decides **only** whether that triple is also promoted into the light's
**ambient** channel. It is not "one extra vector"; it is the ambient colour.

## 4. `CDXLandscape::Render`'s prologue, read as one statement

| Site | Effect |
| --- | --- |
| `0x005454ae` | stage 0 `COLOROP` := `MODULATE2X` (`0x00513af0`) |
| `0x005454ba` | stage 1 `COLOROP` := `MODULATE2X` |
| `0x005454c6` | stage 0 `ALPHAOP` := `DISABLE` (1) through `0x00513820` |
| `0x005454db` | `D3DRS_AMBIENT` shadow `0x009c68a8` := 0 (and byte `0x009c690c` := 1) |
| `0x005454ec`–`0x005454f4` | `SetMaterial` (vtable `+0xc4`) with terrain material `[1]` `0x0083d28c` |
| `0x005454fc`–`0x00545513` | for each of the 8 lights enabled in `0x009c68a0[]`, `ApplyCachedLight(i, 1)` (`0x00551200`, call at `0x0054550e`): colour promoted to Ambient |
| `0x00545520` | `RenderTerrain` (`0x00545590`) |
| `0x00545525` | `D3DRS_AMBIENT` := HFLD ambient `[0x006fbe54]` |
| `0x00545538`–`0x0054554c` | every light re-uploaded with `ApplyCachedLight(i, 0)`: Ambient := 0 |

The bracketing is symmetric and exists for no other draw in the image: **for
the terrain, and only for the terrain, the ambient register is zeroed, the
lights' colours are moved into their ambient channels, and the material is
swapped to one whose diffuse is black and whose ambient response is 0.8.**

The one further call in the prologue, `MOV ECX, 0x009c65c0; CALL 0x00550ca0` at
`0x0054547c`, writes a 16-dword matrix to `[ECX+0x354]` = `0x009c6914` and a
byte at `0x009c73e8` — past the end of the 8 x `0x5c` light array at
`0x009c68a0`. It does not touch any light colour.

## 5. What the fixed-function pipeline produces

Terrain vertices are stride `0x14` = position + one UV pair, with **no normal and
no diffuse channel**
(established in [the stage-flag note](terrain-draw-stage-flags-2026-07-26.md)),
so the `N.L` diffuse term is zero. `CDXLandscape::Render` sets
`D3DRS_DIFFUSEMATERIALSOURCE` (`0x91`) to `D3DMCS_MATERIAL` at `0x00545483`, and
`RenderTerrain` restores it to `D3DMCS_COLOR1` at `0x005461cb`.
`D3DRS_AMBIENTMATERIALSOURCE` (`0x93`) is **`D3DMCS_COLOR1` at this draw, not the
`D3DMCS_MATERIAL` default** — but that does not change the outcome, because the
terrain stream carries no vertex colour for `COLOR1` to select and D3D9 falls back
to the material when the selected colour is absent from the vertex. The material's
ambient is consumed whichever source is selected. With the material of §1 record
`[1]`:

```
vertex_diffuse = Emissive          (= 0)
               + Ambient_material  (= 0.8)  x ( D3DRS_AMBIENT (= 0)
                                              + SUM over enabled lights of light.Ambient )
               + Diffuse_material  (= 0)    x ... (N.L = 0 anyway)
               = 0.8 x SUM light.Ambient
```

which has **no positional or per-vertex dependence at all** — it is one colour
for the entire terrain. Stage 0 then computes
`texture x vertex_diffuse x 2` under `MODULATE2X`:

```
terrain_pixel = 2 x 0.8 x SUM(light colour) x texture
```

That is a **flat, coloured, terrain-specific multiplicative factor applied
outside the macro cache and outside the shipped texture stages** — the exact
shape of the measured fact.

> **Corrected 2026-07-27 — the number survives; one stated reason did not.**
> This section previously read: "`CDXLandscape::Render` sets
> `D3DRS_DIFFUSEMATERIALSOURCE` (`0x91`) to `D3DMCS_MATERIAL` and leaves
> `D3DRS_AMBIENTMATERIALSOURCE` at its `D3DMCS_MATERIAL` default." The second half
> is false.
>
> `D3DRS_AMBIENTMATERIALSOURCE` is written **exactly once in the whole image** —
> `6a 01` `68 93 00 00 00` `b9 b0 5b 85 00` `e8 be 88 02 00` at `0x004eb353`, i.e.
> `SetRenderState(0x93, D3DMCS_COLOR1)` through the forced setter `0x00513c20`
> inside the default block `0x004eb1e0` — and no site anywhere writes it back to
> `0`. It is `D3DMCS_COLOR1` at every draw, including this one. Confirmed at
> runtime: the shadow dump taken at the `TERRAINDRAW` marker reads
> `[0x0085578c] = 0x00000001` in two independent launches, and the probe's watch on
> state `0x93` never fired in either. See
> [`d3d-default-render-state-block-2026-07-27.md`](d3d-default-render-state-block-2026-07-27.md)
> §5 and §8. Because there is only one write in the entire image, no
> ordering-relative-to-the-draw question arises.
>
> **`0.8` is still consumed, and the measurement says so.** The terrain stream has
> no `COLOR1`, so the material is the fallback. Had the missing vertex colour
> instead defaulted to opaque white, the predicted factor would be
> `2 x 1.0 x (0.8750, 0.8281, 0.6914)` = `(1.750, 1.656, 1.383)` against the
> measured `(1.457, 1.389, 1.147)` — **+20.1% / +19.2% / +20.6%**, five times the
> residual the material fallback leaves (§7). §6, §7 and §8 are unaffected, as is
> the shipped `Level100TerrainCompositor.TerrainVertexDiffuse`.
>
> The first half of the sentence stands and is now byte-located, and matches the
> probe log to the return address: `PUSH 0; PUSH 0x91` at `0x00545483` → `ra =
> 0x00545492`, logged as `RS DIFFUSEMATSRC 1 -> 0 land=1 ra=00545492`; restored by
> `PUSH 1; PUSH 0x91` at `0x005461cb` → `ra = 0x005461da`, logged as
> `RS DIFFUSEMATSRC 0 -> 1 land=1 ra=005461da`.

## 6. The number

`CEngine::SetupLights` @ `0x0044a2d0` enables exactly two lights and disables
the rest:

it sets the enable bytes `0x009c68a0` (`0x0044a52a`) and `0x009c68a1`
(`0x0044a584`) to 1, and `0x009c68a2` (`0x0044a590`) and `0x009c68a3`..`a7`
(`0x0044a5be`–`0x0044a5dc`) to 0.

Light 0 is filled from `0x006fbe44` (HFLD `CHFD+0x107C`) and light 1 from
`0x006fbe48` (`CHFD+0x1080`), each byte scaled by `_DAT_005db060` =
`0x3b800000` = **1/256** (`0x0044a431`, `0x0044a457`, `0x0044a470`, and the
matching sequence at `0x0044a4f8`–`0x0044a545`), then `REP MOVSD` of `0x17`
dwords into `0x009c65c0` and `0x009c661c` (`0x0044a4c2`, `0x0044a577`).

`tools/terrain_ambient_light_factor_probe.py` reads the shipped Level 100 HFLD
and applies §5:

```
light 0  CHFD+0x107C      (189, 177, 121)
light 1  CHFD+0x1080      (35, 35, 56)
D3DRS_AMBIENT CHFD+0x108C (13, 15, 43)   (zeroed at 0x005454db)

sum of enabled light colours          (224, 212, 177)
sum light.Ambient  = sum/256          (0.8750, 0.8281, 0.6914)
x material ambient 0.8 x MODULATE2X   (1.4000, 1.3250, 1.1062)
measured implied/ours factor          (1.4570, 1.3890, 1.1470)

                                          R        G        B
magnitude error vs measured           -3.9%    -4.6%    -3.6%
predicted, normalised to blue        1.2655   1.1977   1.0000
measured,  normalised to blue        1.2703   1.2110   1.0000
chromaticity error                    -0.4%    -1.1%    +0.0%
```

Two things distinguish this from the candidates rejected in
[the sun-colour note](terrain-sun-colour-route-2026-07-26.md) §7:

- **It supplies a magnitude.** `sun + ambient` is a byte triple with no
  dimension; the Palletize reciprocal is 1.875 against a measured 1.457. This
  is 1.400/1.325/1.106 against 1.457/1.389/1.147, from a derivation that
  contains no free parameter — `2` is `MODULATE2X`, `0.8` is `0x3f4ccccd` at
  `0x0083d28c+0x10`, `1/256` is `0x3b800000`.
- **The quantity is the right one.** The earlier chromaticity test used
  `sun + HFLD ambient` = (202, 192, 164). The ambient *register* is explicitly
  set to **zero** for this draw; the correct sum is over the two **light**
  colours, (189, 177, 121) + (35, 35, 56) = **(224, 212, 177)**, which was never
  tested. Its chromaticity error is −0.4% / −1.1% against the earlier
  −3.0% / −3.3%.

## 7. The residual, stated rather than closed

**An omitted step in the promotion argument (RE audit, 2026-09-26).** Before
the draw, `RenderTerrain` flushes pending device state (`0x00550d50(0, 1)` at
`0x00545a13`). That flush re-uploads every light whose dirty byte is set, with
the Ambient term zeroed. The promotion to Ambient therefore survives only if
those bytes are clear at the draw; a reviewer traced them being cleared by the
sky pass's earlier flush, which this note has not re-derived. Cheapest
falsifier: at `0x00545a18`, read `0x009c68fc`-`0x009c6903` (expect all 0) and
`0x009c68ad` (expect 1).


The prediction is uniformly **3.6–4.6% low**. Bounds on that gap:

- The inversion note's own two validations reproduce known quantities at
  1.029/1.021/1.012 and 1.006/1.005/1.023, so the measured triple carries a
  systematic error bar of the same order and sign. Dividing the measurement by
  the first validation gives (1.416, 1.360, 1.133) and residuals of
  −1.1% / −2.6% / −2.4%.
- In light-colour units the shortfall is `(9.1, 10.2, 6.5)` out of 256 — small
  and roughly achromatic, consistent with a third contributor rather than a
  wrong coefficient. A second light-setup path at `0x00450428`–`0x00450b3f`
  enables **three** lights (`0x009c68a0`, `0x009c68a1`, `0x009c68a2` written at
  `0x00450a1d`, `0x00450a8b`, `0x00450b2a`); which of the two paths is live for
  Level 100 gameplay is not decided here.

  **SUPERSEDED 2026-07-26 — the third-light attribution above is FALSIFIED.** See
  [`terrain-third-light-2026-07-26.md`](terrain-third-light-2026-07-26.md).
  `CDXLandscape::Render` and `CEngine::SetupLights` have exactly one caller each,
  both inside `0x0053e2e0` and 208 bytes apart, and no branch target in that
  function lands between them — so `SetupLights`, which unconditionally writes
  `enable[0]=enable[1]=1` and `enable[2..7]=0`, dominates **every** terrain draw.
  The three-light path `0x004505b0` is slot 5 of `.?AVCFEPBEConfig@@`, a front-end
  page, with a hard-coded three-point model-viewer rig; its third light alone
  would add `+0.384` per channel where the residual needs `+0.016/+0.030/+0.027`.
  The residual is now known to be **degenerate** — it reads equally well as
  stages 1–3 being 0.9/2.1/2.3 % dark — and it remains open and unattributed.
- The measured distribution's own spread (sd 0.48 / 0.38 / 0.28) is far larger
  than the residual.

**No change was made to any renderer.** Closing the residual needs the runtime
light state at the terrain draw, not more static reading, and applying
`(1.400, 1.325, 1.106)` on the strength of a 4% agreement would repeat the
pattern this session has been removing.

## 8. What this settles

- **Loose end (a) is live but is not itself the colour.** The terrain material
  record is real, terrain-specific, singly-written, and fully known: black
  diffuse, 0.8 grey ambient, **zero emissive**. It supplies the `0.8`
  coefficient and the decision to respond to ambient only. There is no emissive
  term and no coloured material component anywhere in the image.
- **Loose end (b) is live and is what makes (a) matter.** `0x008aa94c` is
  `LANDSCAPE_LIGHTING`, default **1**, so lighting is **not** disabled for the
  terrain draw, and the same value selects `MODULATE2X`.
- **Lighting is active for the terrain draw**, and with no vertex normal and a
  zeroed ambient register it produces exactly one thing: a constant
  `0.8 x sum(light colour)`, doubled by the stage op.
- The search does **not** need to move to the cache texture. The factor is
  produced inside `CDXLandscape::Render`, in the six instructions at
  `0x005454ae`–`0x00545517` plus the gate at `0x00545675`.

## Reproduction

```
py -3 tools/operand_scan.py <BEA.exe> 0x0083d248 0x0083d28c 0x008aa920 0x008aa94c
py -3 tools/call_xref_scan.py <BEA.exe> 0x004eb9a0 0x004eb1d0
py -3 tools/disasm_va.py <BEA.exe> 0x004eb9a0 --count 40 --bytes
py -3 tools/disasm_va.py <BEA.exe> 0x00545410 --count 100 --bytes
py -3 tools/disasm_va.py <BEA.exe> 0x00551200 --count 80 --bytes
py -3 tools/terrain_ambient_light_factor_probe.py
```
