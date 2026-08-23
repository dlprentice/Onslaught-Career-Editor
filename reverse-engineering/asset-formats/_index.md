# Asset format contracts — game-folder deep census

Status: active contract set
Date: 2026-08-23
Summary: routes every measured retail data/root-binary family to a bounded
format contract, count, decoder anchor, and explicit unknown ledger.
Evidence: MEASURED — counts were recomputed from the read-only
`G:\bea-asset-mirror\INDEX.jsonl` manifest (SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`).
The header declares schema `onslaught.asset-mirror-index.v1`, generated
2026-07-31, and 5,464 source files; this pass parsed exactly 5,464 data rows.

## Scope and safety boundary

This is Part B of Kanban `t_97657338`; [game-binaries.md](game-binaries.md) is
Part A. `G:\bea-asset-mirror`, the installed game, and the pristine safe copy
were read only. No binary was executed and no asset, decoded image, audio,
video, or extracted payload is tracked here.

The mirror's `_interpreted` and derived PNG/output paths are decoder products,
not specimen evidence. Static VAs are routes from named pristine-binary notes;
they do not by themselves prove runtime decode or fidelity.

## Re-verified tree census

| Installed extension/family | Files |
| --- | ---: |
| Ogg Vorbis | 3,057 |
| AYA envelope (all payload owners) | 1,361 |
| MSL script | 733 |
| Mission TXT | 130 |
| STF | 96 |
| Bink VID | 66 |
| DAT (six localization + three root schemas) | 9 |
| XAP | 5 |
| particle PAR | 3 |
| `Dial.raw` | 1 |
| `textlist.h` | 1 |
| `sounds.sfx` | 1 |
| `splash.tga` | 1 |
| **Total** | **5,464** |

AYA payload owners overlap the AYA count rather than adding to it: 301 LVLR,
213 CMSH, and 847 DDS. The family rows in
[formats-summary.tsv](formats-summary.tsv) are therefore explicitly
non-additive.

## Contract owners

| Format family | Contract | Population | Contract state |
| --- | --- | ---: | --- |
| PC AYA chunked-zlib | [aya-container.md](aya-container.md) | 1,361 | outer framing complete |
| LVLR resource streams | [lvlr-archive.md](lvlr-archive.md) | 301 | tag census complete; schemas partial |
| Numeric WRES Unit/Feature placements | [wres-instance-join.md](wres-instance-join.md) | 66 archives / 4,090 joins | definition, transform, state, physics mesh, and named-CMSH edge bounded |
| CMSH meshes + embedded animation | [cmsh-mesh.md](cmsh-mesh.md) + [animation/usage](cmsh-animation-usage.md) + [matrix-palette skinning](cmsh-matrix-palette-skinning.md) | 213 | framing, pose lanes, bone indices, released position blend, and selected usage bounded |
| DDS textures + texture-backed fonts | [dds-texture.md](dds-texture.md) | 847 | header census complete |
| Ogg/XAP/SFX audio | [ogg-audio.md](ogg-audio.md) | 3,057 + 5 + 1 | framing and identity joins bounded |
| Bink video | [bink-video.md](bink-video.md) | 66 | container/media census bounded |
| Localization DAT/TXT/STF | [localization-text.md](localization-text.md) | 6 + 130 + 96 | DAT layout strong; loose selection open |
| Root config/physics/world/Dial | [config-dat.md](config-dat.md) | 3 DAT + 1 RAW | mixed, per-file contracts |
| Particle PAR | [particle-par.md](particle-par.md) | 3 | grammar/factory bounded |
| Startup TGA | [tga-image.md](tga-image.md) | 1 | exact single-file header/layout |
| Root DLLs/helper EXE | [game-binaries.md](game-binaries.md) | 5 | static PE identity/ABI census |

MSL scripts are counted here but remain owned by
[`game-assets/msl-scripting.md`](../game-assets/msl-scripting.md) and the
MissionScript VM contracts. There is no standalone `.anim` family: animation
is embedded in CMSH (`VHFM`/`HORI`/`HPOS`/`HFOV`/bone lanes); the
[focused contract](cmsh-animation-usage.md) separates those stored lanes from
LVLR membership, the bounded [WRES instance edge](wres-instance-join.md), and
MSL name requests. The separate
[matrix-palette contract](cmsh-matrix-palette-skinning.md) closes the seven-file
GPU position blend without generalizing normal deformation or scheduling. There
is no loose
font-file family: installed font glyph resources live in texture assets and the
retail image also has a GDI/texture font owner.

The complete four-DLL ordinal/RVA export appendix is
[game-binary-exports.md](game-binary-exports.md); `Message.exe` has no exports.

## Evidence vocabulary

- **Measured:** read from the named mirror index or pristine copy in this pass.
- **Prior measurement:** a cited tracked document owns the earlier complete
  parse/census; this pass rechecked only the stated aggregate.
- **Static anchor:** VA and call shape are pinned by a cited pristine-binary
  note; runtime behavior is not implied.
- **Tool/source evidence:** tracked decoder or external source lineage bounds
  field interpretation but does not establish retail runtime behavior.
- **Unknown:** stated with a concrete next instrument or falsifier.

## Completion and non-claims

The shallow tree listing is now routed into discrete contracts with counts,
container layouts, bounded field meanings, decoder/consumer anchors, tools, and
open questions. This is not atom-level semantic completion: LVLR payloads,
CMSH PB* families, named clips, normal blend and interpolation semantics, non-Unit/
Feature WRES records, texture pixels/fonts, media selection, malformed-input
behavior, and full runtime/rebuild parity remain explicitly open.
