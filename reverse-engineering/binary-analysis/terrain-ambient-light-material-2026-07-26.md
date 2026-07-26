# The terrain material record and the `LANDSCAPE_LIGHTING` gate — both loose ends are live

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

Specimen: `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes (local pristine safe copy). Image base `0x00400000`. All
disassembly below is `capstone` linear decode of the pristine file through
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
`[0x0083d248, 0x0083d310)` returns **33 hits, all in `.text`, and only four
distinct addresses**:

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

```
004eb1d0  b9 48 d2 83 00     MOV  ECX, 0x83d248
004eb1d5  e9 c6 07 00 00     JMP  0x4eb9a0
```

`0x004eb9a0` has exactly **one** reference in the image — that `JMP`
(`call_xref_scan.py`: 0 `CALL`, 1 `JMP`; `operand_scan.py`: 0 data pointers).
`0x004eb1d0` itself has 0 direct references and exactly one data pointer, the
dispatch-table slot at `0x00622708`. So `0x004eb9a0` is the **sole writer of the
block, always with `this = 0x0083d248`**, and it writes exactly `0x88` bytes =
two `D3DMATERIAL9`:

```
004eb9a0  8b c1              MOV  EAX, ECX                 ; EAX = 0x0083d248
004eb9a2  ba 00 00 80 3f     MOV  EDX, 0x3f800000          ; 1.0f
004eb9a7  33 c9              XOR  ECX, ECX                 ; 0.0f
004eb9a9  89 10              MOV  [EAX+0x00], EDX          ;  material[0].Diffuse.r
004eb9ab  89 50 04           MOV  [EAX+0x04], EDX          ;  .g
004eb9ae  89 50 08           MOV  [EAX+0x08], EDX          ;  .b
004eb9b1  89 50 0c           MOV  [EAX+0x0c], EDX          ;  .a
004eb9b4  89 48 10           MOV  [EAX+0x10], ECX          ;  .Ambient.r
004eb9b7  89 48 14           MOV  [EAX+0x14], ECX          ;  .g
004eb9ba  89 48 18           MOV  [EAX+0x18], ECX          ;  .b
004eb9bd  89 50 1c           MOV  [EAX+0x1c], EDX          ;  .a
004eb9c0..004eb9cf            MOV  [EAX+0x20..0x2c], ECX   ;  .Specular  = 0
004eb9cc..004eb9d5            MOV  [EAX+0x30..0x3c], ECX   ;  .Emissive  = 0
004eb9d8  c7 40 40 cd cc cc 3d  MOV [EAX+0x40], 0x3dcccccd ;  .Power = 0.1
                                                           ; -- 0x44 boundary --
004eb9df  89 48 44           MOV  [EAX+0x44], ECX          ;  material[1].Diffuse.r
004eb9e2  89 48 48           MOV  [EAX+0x48], ECX          ;  .g
004eb9e5  89 48 4c           MOV  [EAX+0x4c], ECX          ;  .b
004eb9e8  89 50 50           MOV  [EAX+0x50], EDX          ;  .a = 1.0
004eb9eb  c7 40 54 cd cc 4c 3f  MOV [EAX+0x54], 0x3f4ccccd ;  .Ambient.r = 0.8
004eb9f2  c7 40 58 cd cc 4c 3f  MOV [EAX+0x58], 0x3f4ccccd ;  .g        = 0.8
004eb9f9  c7 40 5c cd cc 4c 3f  MOV [EAX+0x5c], 0x3f4ccccd ;  .b        = 0.8
004eba00  89 50 60           MOV  [EAX+0x60], EDX          ;  .a        = 1.0
004eba03..004eba0f            MOV  [EAX+0x64..0x70], ECX   ;  .Specular = 0
004eba12..004eba1e            MOV  [EAX+0x74..0x84], ECX   ;  .Emissive = 0, .Power = 0
004eba24  c3                 RET
```

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

```
00528aa0  8b c1              MOV  EAX, ECX
00528aa2  8b 4c 24 04        MOV  ECX, [ESP+0x4]      ; name
00528aa6  c7 00 94 4a 5e 00  MOV  [EAX], 0x5e4a94     ; vtable
00528aac  89 48 08           MOV  [EAX+0x8], ECX
00528aaf  8b 15 18 c0 89 00  MOV  EDX, [0x0089c018]   ; registry head
00528ab5  8b 4c 24 08        MOV  ECX, [ESP+0x8]      ; default value
00528ab9  89 50 04           MOV  [EAX+0x4], EDX
00528abc  a3 18 c0 89 00     MOV  [0x0089c018], EAX
00528ac1  c7 00 9c 4a 5e 00  MOV  [EAX], 0x5e4a9c
00528ac7  89 48 0c           MOV  [EAX+0xc], ECX      ; value := default
```

and `0x00544690` passes `PUSH 0x1`. So the earlier conclusion inverts on this
byte: `RenderTerrain`'s lighting-disable at `0x005455a2` is gated on
`LANDSCAPE_LIGHTING == 0`, and the shipped default is **1**, so
**`D3DRS_LIGHTING` is left enabled for the terrain draw.**

The same value chooses the stage op at `0x00545675`. Taking the second gate
site in full:

```
0054564e  39 2d fc 54 85 00  CMP  [0x008554fc], EBP        ; USE_MODULATE_2X
00545654  75 0b              JNZ  0x00545661
00545656  55                 PUSH EBP                      ; if unsupported,
00545657  b9 20 a9 8a 00     MOV  ECX, 0x008aa920          ;   landscape_method := 0
0054565c  e8 ef 34 fe ff     CALL 0x00528b50
00545661  6a 02              PUSH 0x2
00545663  b9 20 a9 8a 00     MOV  ECX, 0x008aa920
00545668  e8 53 26 fe ff     CALL 0x00527cc0               ; landscape_method == 2 ?
0054566d  84 c0              TEST AL, AL
0054566f  0f 84 7d 04 00 00  JZ   0x00545af2               ; other landscape method
00545675  39 2d 4c a9 8a 00  CMP  [0x008aa94c], EBP        ; LANDSCAPE_LIGHTING
0054567b  74 0d              JZ   0x0054568a
0054567d  55                 PUSH EBP                      ; lighting ON  ->
0054567e  b9 b0 5b 85 00     MOV  ECX, 0x00855bb0          ;   COLOROP := MODULATE2X
00545683  e8 68 e4 fc ff     CALL 0x00513af0               ;   (or MODULATE if uncapable)
00545688  eb 0f              JMP  0x00545699
0054568a  6a 04              PUSH 0x4                      ; lighting OFF ->
0054568c  6a 01              PUSH 0x1                      ;   COLOROP := MODULATE
0054568e  55                 PUSH EBP
0054568f  b9 b0 5b 85 00     MOV  ECX, 0x00855bb0
00545694  e8 d7 e1 fc ff     CALL 0x00513870
```

The two branches are a coherent pair: *lighting off* means plain
`D3DTOP_MODULATE` against the implicit white vertex colour; *lighting on* means
`D3DTOP_MODULATE2X` against a lit vertex colour that is expected to sit near
0.5. The remaining stage setup is unconditional and decides the operands:

```
00545699  SetTextureStageState(0, D3DTSS_COLORARG1 = 2, D3DTA_TEXTURE = 2)
005456a8  SetTextureStageState(0, D3DTSS_COLORARG2 = 3, D3DTA_DIFFUSE = 0)
005456b6  SetTextureStageState(0, D3DTSS_ALPHAOP   = 4, D3DTOP_SELECTARG1 = 1)
005456c5  SetTextureStageState(0, D3DTSS_ALPHAARG1 = 5, D3DTA_TEXTURE = 2)
```

(`0x00513870` reads `Stage = [ESP+0x4]`, `Type = [ESP+0x8]`, `Value = [ESP+0xc]`,
shadows into `[0x008557f0 + (Type + Stage*30)*4]`, then calls device `+0x10c`.)

So stage 0 is **texture x vertex diffuse**, doubled.

`0x008554fc` is likewise a CVar value field: `0x008554f0 + 0xc`, registered at
`0x00511fe0` with name **`USE_MODULATE_2X`** (`0x0063dc24`) and **default 1**. It
is cleared only at `0x0051270f`, on the branch taken when
`[caps + 0x32f34] & 0x10` is absent — `D3DTEXOPCAPS_MODULATE2X`. On retail
hardware the flag stands and `landscape_method` keeps its default 2.

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

```
005512ac  8b 54 24 78        MOV  EDX, [ESP+0x78]        ; arg2 ("enabled")
005512b0  3b d6              CMP  EDX, ESI               ; ESI = 1
005512bc  75 15              JNZ  0x005512d3              ; != 1 -> leave Ambient zero
005512be  8b 50 24           MOV  EDX, [EAX+0x24]
005512c1  89 54 24 2c        MOV  [ESP+0x2c], EDX        ; Ambient.r
005512c5  8b 50 28           MOV  EDX, [EAX+0x28]
005512c8  8b 40 2c           MOV  EAX, [EAX+0x2c]
005512cb  89 54 24 30        MOV  [ESP+0x30], EDX        ; Ambient.g
005512cf  89 44 24 34        MOV  [ESP+0x34], EAX        ; Ambient.b
```

The `0x5c`-byte cached record's colour triple lives at `+0x24`, and the flag
argument decides **only** whether that triple is also promoted into the light's
**ambient** channel. It is not "one extra vector"; it is the ambient colour.

## 4. `CDXLandscape::Render`'s prologue, read as one statement

```
005454ae  PUSH 0; ECX=0x00855bb0; CALL 0x00513af0   ; stage 0 COLOROP := MODULATE2X
005454ba  PUSH 1; ECX=0x00855bb0; CALL 0x00513af0   ; stage 1 COLOROP := MODULATE2X
005454c6  PUSH 1; PUSH 4; PUSH 0; CALL 0x00513820   ; stage 0 ALPHAOP := SELECTARG1
005454d6  MOV  EAX, [0x00888a50]
005454db  MOV  dword [0x009c68a8], 0x0              ; D3DRS_AMBIENT := 0
005454e5  MOV  byte  [0x009c690c], 0x1
005454ec  PUSH 0x0083d28c                           ; terrain material[1]
005454f1  MOV  EDX, [EAX]
005454f3  PUSH EAX
005454f4  CALL dword [EDX+0xc4]                     ; SetMaterial
005454fa  XOR  ESI, ESI
005454fc  MOV  AL, [ESI + 0x009c68a0]               ; light-enable array
00545502  TEST AL, AL
00545504  JZ   0x00545513
00545506  PUSH 0x1                                  ; <-- promote colour to Ambient
00545508  PUSH ESI
00545509  MOV  ECX, 0x009c65c0
0054550e  CALL 0x00551200                           ; ApplyCachedLight(i, 1)
00545513  INC  ESI ; CMP ESI, 8 ; JL 0x005454fc
00545520  CALL 0x00545590                           ; RenderTerrain
00545525  MOV  ECX, [0x006fbe54] ...                ; D3DRS_AMBIENT := HFLD ambient
00545538  XOR  ESI, ESI                             ; and re-upload every light
00545544  PUSH 0x0                                  ;   with Ambient := 0
00545547  MOV  ECX, 0x009c65c0
0054554c  CALL 0x00551200                           ; ApplyCachedLight(i, 0)
```

The bracketing is symmetric and exists for no other draw in the image: **for
the terrain, and only for the terrain, the ambient register is zeroed, the
lights' colours are moved into their ambient channels, and the material is
swapped to one whose diffuse is black and whose ambient response is 0.8.**

The one further call in the prologue, `MOV ECX, 0x009c65c0; CALL 0x00550ca0` at
`0x0054547c`, writes a 16-dword matrix to `[ECX+0x354]` = `0x009c6914` and a
byte at `0x009c73e8` — past the end of the 8 x `0x5c` light array at
`0x009c68a0`. It does not touch any light colour.

## 5. What the fixed-function pipeline produces

Terrain vertices are stride `0x14` = position + one UV pair, with no normal
(established in [the stage-flag note](terrain-draw-stage-flags-2026-07-26.md)),
so the `N.L` diffuse term is zero. `CDXLandscape::Render` sets
`D3DRS_DIFFUSEMATERIALSOURCE` (`0x91`) to `D3DMCS_MATERIAL` and leaves
`D3DRS_AMBIENTMATERIALSOURCE` at its `D3DMCS_MATERIAL` default. With the
material of §1 record `[1]`:

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

## 6. The number

`CEngine::SetupLights` @ `0x0044a2d0` enables exactly two lights and disables
the rest:

```
0044a52a  MOV  byte [0x009c68a0], BL   ; BL = 1  light 0 enabled
0044a584  MOV  byte [0x009c68a1], BL   ;         light 1 enabled
0044a590  MOV  byte [0x009c68a2], 0x0
0044a5be..0044a5dc  MOV byte [0x009c68a3..a7], 0x0
```

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
