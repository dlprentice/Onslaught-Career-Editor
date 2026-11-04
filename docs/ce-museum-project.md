# Authored CE museum room projects

Status: experimental content adapter; native room acceptance pending
Last updated: 2026-11-04
Summary: a CE-first exhibition description, exact local resource bindings and private generated content
Evidence: MEASURED — authored content checks in `tools/ce_museum_stage_tests.py`; UNKNOWN — native room behaviour

`tools/ce_museum_stage.py` turns an authored exhibition description into an added-level mod folder. It uses
the existing world codecs as an internal adapter. The project describes exhibition intent; it is not an
original-game level format or a requirement that future CE rooms remain compatible with the original game.

This first implementation binds an existing static-feature record and a player start from the selected local
installation. It does not support arbitrary catalogue meshes, animated exhibits, signs, turntables, a museum
menu entry or a complete model collection. A staged archive is not proof that a player can enter or walk through
the room. Native movement, rendering, exit, collision, damage behaviour and career isolation still need acceptance.

## The project

The JSON object has exactly these fields:

| Field | Meaning |
| --- | --- |
| `format` | `onslaught.ce.museum.v1` |
| `id` | A simple lowercase identifier for the generated mod folder. |
| `name` | An authored display name. |
| `targetLevel` | An unused CE added-level slot, from 850 through 899. |
| `carrier` | The local resource level and its complete archive SHA-256. |
| `start` | An exact source start binding, an authored offset and orientation. |
| `exhibits` | One to 64 authored exhibit placements, each with a unique `id`. |

`carrier` contains `level` and `sha256`. A placement contains `source`, `offset` and `orientation`; exhibits
also contain `id`. Each vector has three finite components. Offsets are relative to the bound start position,
in the game's world axes; orientation components use the existing world codec's native convention. This
developer format has not yet acquired friendly 3D editor controls or a degree-based rotation interface.

A `source` contains `world` (`BSWD` or `RLWD`), the zero-based `ordinal` in that world's decoded `things` array,
and `sha256`. The record hash is SHA-256 of the complete decoded record serialized as sorted-key, compact,
ASCII JSON with non-finite JSON numbers refused. The public helper `record_digest` computes it. The archive
pin and record pin must both match. The source start must have kind `start`; every exhibit must have kind
`feature` and a nonempty feature definition. A name, basename or display label is never a substitute for that
binding. Catalogue mesh identities are not guessed or changed by this adapter.

The stage creates a new visitor start and new named feature placements. It does not copy their source script
attachments, positions, target references or spawn instructions. The feature definition and player configuration
remain resource bindings to the owner's installation; their native rendering, sound and damage properties are
not rewritten or certified by the content adapter.

## Generated content and limits

Both generated world bodies exclude the source campaign's actors, scripts, navigation paths, tree populations,
automatic named-mesh spawns and progression-level references. The real body contains only the authored visitor
start and exhibit placements; the base body contains no actors. The packer reads its result back and checks
these invariants independently of the composition path. These are content checks, not evidence that every native
runtime system is inactive. Ordinary physics and input still need to run for a visit to be usable.

Terrain and other supported resource sections are retained from the locally owned carrier. Unknown resource
sections are refused. The output is therefore an authored arrangement using existing terrain and assets, not a
newly modelled room or redistributed asset pack. Generated archives contain game content: keep them private and
out of Git, issue attachments and releases.

The adapter reads the selected installation and writes only a new output folder. It refuses an existing target
level, an output in the selected game tree, symlinked input files and replacement of existing output. It writes
the archive first and `mod.json` last, using the shared protected-output helper. It does not launch the game,
change an enabled-mod list, access careers or modify the installation. Its archive declares a minimum CE version;
do not remove that check to make an unversioned diagnostic build load it.

## Developer commands

Run the authored checks without an installed game:

```sh
python3 -B tools/ce_museum_stage_tests.py
```

With a locally prepared and pinned project, stage into a new private folder outside the game:

```sh
python3 tools/ce_museum_stage.py --project museum.json --game path/to/owned-game --out private-generated
```

The current stage is for an isolated CE user folder and the supported added-level mod route. It is not exposed
as a normal campaign option. Windows content generation and Windows runtime have not been validated by this
lane; Linux staging checks alone establish neither. A usable-room menu entry must wait for native room and
career-safety acceptance.
