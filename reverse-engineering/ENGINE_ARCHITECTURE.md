# Battle Engine Aquila engine architecture

Status: active, first-party architecture synthesis
Last updated: 2026-08-11
Evidence: SOURCE — Jeremy Longley's first-party contemporary 47-slide Lost Toys
GDC deck; MEASURED — exact PC retail strings, RTTI, source-path remnants, and
the current function inventory; UNKNOWN — console-binary joins and every
proposed or simplified deck identifier not independently found.
Verdict: Lost Toys deliberately organized BEA around shared subsystem
interfaces with platform-dependent implementations. The strongest recovered
PC instance is the generic `SoundManager.cpp` / PC-specific
`pcsoundmanager.cpp` split; rendering and controller evidence support the same
pattern, while the deck's exact `CShader` and console sound-manager names remain
unconfirmed proposals/search seeds.

## First-party source

The primary source is:

`G:\BEA ROMS\Lore\09_Wayback_Websites\full_domains\losttoys.com\GDC\20030412092159_GDC_GDCE02_20-_20Cross_20Platform_20Console_20Development.ppt`

| Property | Value |
| --- | --- |
| Title | *Cross-Platform Console Development: Our Experiences With Battle Engine Aquila* |
| Presenter | Jeremy Longley, Lost Toys |
| Slides | 47 |
| PPT bytes | 195,072 |
| PPT SHA-256 | `3b2e08607fd881dfeefb31395b49de91a68ec02dee9554714f6a97d029165713e` |
| Archived presentation directory | 77 files / 751,853 bytes |
| Sorted directory-manifest SHA-256 | `1254ffd317766b395eef9d61473db8ce274868032eb5c663099c49df36abc0e0` |

All 47 archived slide pages were recoverable. The local ordered transcript and
terminology index remain ignored under
`local-lab/gdc-cross-platform-deck-analysis-20260811-v1/`; they are working
evidence, not redistributed presentation content.

The deck describes production experience, but its code examples are explicitly
edited/simplified and sometimes intentionally place logic where it would not
really live. This report therefore separates architecture claims, illustrative
pseudocode, and independently recovered production identities.

## Recovered architectural model

Slide 24 states that BEA's subsystems used cross-platform interfaces over
platform-dependent code. Its explicit production subsystem list is:

| Area | Subsystems named in the deck |
| --- | --- |
| Rendering/presentation | meshes, textures, render states, cameras, particle systems, lights, custom/procedural systems, fonts, 2D/HUD/front end |
| Game/platform services | sound manager, file access, memory management, timers/interrupts, controller support, collision |

The architectural implication is not “one universal implementation.” Shared
game policy and data-facing interfaces coexist with console-specific device,
rendering, input, memory, and certification behavior. The deck specifically
contrasts Xbox DirectX render states and shader paths with PS2 VU1 pipelines,
and recommends semantic interfaces rather than leaking platform commands into
game code.

## Independent PC joins

### Sound: strong shared/platform split

The pristine PC executable contains the following exact ASCII remnants:

| Raw file offset | Retail evidence | Meaning |
| ---: | --- | --- |
| `0x00232428` | `C:\dev\ONSLAUGHT2\SoundManager.cpp` | generic/shared source owner |
| `0x0023E46C` | `C:\dev\ONSLAUGHT2\pcsoundmanager.cpp` | PC-specific implementation owner |
| `0x002322A8` | `.?AVCSample@@` | exact `CSample` RTTI |
| `0x0023E2D8` | `.?AVCPCSample@@` | exact PC-specific sample RTTI |
| `0x00222BF8` | `.?AVIAudibleThing@@` | exact `IAudibleThing` RTTI |
| `0x002324D8` | `Warning : out of sound events!` | bounded event-pool behavior exists |

This is the strongest direct architecture join: generic and PC-specific source
owners survive beside the same interface/sample vocabulary shown in the deck.
All 34 shared `CSoundManager__*` production bodies are now semantically
crosswalked against retained source and normalized-identical demo twins in the
[`CSoundManager` report](binary-analysis/csoundmanager-shared-semantics-2026-08-11.md).
They prove the 256-event pool, shared sample/effect and spatial policy, and
calls into the PC backend for device and channel operations. The inventory also
contains 20 `CPCSoundManager__*` device-side bodies.

The slide spellings `CXBOXSoundManager`, `SSoundEvent`, `GetSoundEvent`,
`ShouldIBePlaying`, and `DevicePlay` were not found as exact ASCII in the
bounded PC corpus. They remain console search seeds or pseudocode, not promoted
production symbols.

### Rendering: concrete subsystem, proposed unifying name

PC retail contains exact `CVertexShader` RTTI, `VertexShader.cpp`, vertex-shader
configuration/status strings, compact pixel-shader resource terminology, and
engine render-state constants. The current function inventory has 23
`CVertexShader__*` envelopes.

The deck's `CShader` abstraction is presented as a proposed semantic wrapper
for DirectX vertex/pixel shaders and PS2 VU1 code. Exact `CShader` ASCII was not
found in the PC executable or installed data. The production conclusion is
therefore narrower: PC retail has concrete shader/render-state owners, but the
exact cross-platform class name and whether the proposal shipped are open.

### Controller and other platform services

The generic `Controller.cpp` source path and exact `CPCController` RTTI survive
in PC retail; the current inventory has 15 `CPCController__*` functions. This
is consistent with the deck's controller boundary but still needs call/layout
evidence before declaring a particular abstract interface.

Additional source-path remnants independently align with the deck's production
subsystems: `Camera.cpp`, collision-seeking owners, `MemoryManager.cpp`,
`MeshCollisionVolume.cpp`, `ParticleDescriptor.cpp`, `ParticleManager.cpp`,
`ParticleSet.cpp`, `TokenArchive.cpp`, and `DXParticleTexture.cpp`.

### Building example

The deck's sound example names `CBuilding`; PC retail contains exact
`CBuilding` and `CBuildingNamedMesh` RTTI, and the current inventory has 16
`CBuilding__*` envelopes. That proves the class token is production-real. It
does not prove the shown `CBuilding::Explode()` code is a literal retail body.
Likewise, the deck's `LARGE_EXPLOSION` spelling is absent while shipped
`default physics.dat` contains `Large Explosion`; the relationship is useful
terminology, not an exact constant mapping.

## Rendering and content-production implications

The deck records several development constraints that should guide format and
asset comparison:

- high-resolution source textures were reduced per platform and needed visual
  review after scaling/compression;
- Xbox and PS2 used materially different texture/compression expectations;
- tiled textures, light maps, detail textures, texel density, gamma, palette
  depth, and television filtering were production concerns;
- mesh and LOD evaluation was intended to run on actual console hardware and
  consumer televisions, not only PC tools;
- shadows, lighting, materials, particles, sound, AI, collision, memory, and
  processor use were explicit scalability axes.

These claims justify comparing logical assets as well as container bytes. A
smaller or differently encoded console texture is not automatically an earlier
asset, and a common filename does not prove identical platform data.

## Development-process evidence

The deck recommends keeping a current PC development build even when a retail
PC version was not yet planned. The distinct PC demo/retail census now shows
that the class surface remained highly stable across two PC builds: 724 strict
vtables, 11,777 placements, and 2,127 paired virtual targets, with 2,123
zero-normalized instruction streams. See
[`DEMO_VS_RETAIL.md`](DEMO_VS_RETAIL.md).

The deck also treats Xbox TRCs and PlayStation TCRs as separate production
schedules and requirements. Platform-specific input, startup, save, display,
and error-handling differences may therefore be certification work rather than
evidence of a different high-level engine.

## Evidence boundaries and next joins

Positive PC matches do not establish the Xbox or PS2 implementation. The next
cheapest architecture work is:

1. search Xbox XBE strings/RTTI for sound-manager/sample subclasses and compare
   their vtable/call shape with PC;
2. search PS2 ELF strings for the generic sound owner, PS2-specific sample or
   manager names, VU1 pipeline vocabulary, and matching data records;
3. map deck subsystem terms to the PC demo as a second-build refuter;
4. compare platform asset manifests for texture/model format and quality
   decisions described by the deck;
5. keep exact `CShader`, `CXBOXSoundManager`, and `SSoundEvent` negative until a
   console binary, debug remnant, or structure recovery proves them.
