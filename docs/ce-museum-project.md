# Authored CE museum room projects

Status: experimental content adapter; bounded Linux room check, independent review passed; physical mouse, audible audio, collision/damage and native Windows unverified; usable-room menu entry pending
Last updated: 2026-11-05 (the run record points to PROGRAM.md and its receipts; launch facts and enforced bounds documented; earlier: 2026-11-04)
Summary: a CE-first exhibition description, exact local resource bindings and private generated content
Evidence: MEASURED — the authored content checks in `tools/ce_museum_stage_tests.py` and the Linux run recorded in PROGRAM.md; UNKNOWN — the complete museum experience, collision and damage, physical mouse, audible sound and Windows

This is the developer adapter behind the museum construction test ([PROGRAM.md](../PROGRAM.md#level-and-mission-tools)); it is not
the Goodies-based Museum Preview. A room project is its input, and a room check is one run of it. It is the small CE-first exhibition
stage: the required museum is an explorable, self-guided world built from scratch and reached through CE's menus
([GOAL.md](../GOAL.md)), and this adapter does not produce it.

`tools/ce_museum_stage.py` turns an authored exhibition description into two loose-world overrides in a CE
mod folder. It uses an existing level's terrain and resources, replacing that level's base and real world
contents only in a separate museum user folder. The existing world codecs are an internal adapter: the
project describes exhibition intent, without requiring future CE rooms to remain compatible with the original game.

This first implementation binds an existing static-feature record and a player start from the selected local
installation. It does not support arbitrary catalogue meshes, animated exhibits, signs, turntables, a museum
menu entry or a complete model collection. The run record is in PROGRAM.md (the museum construction test): the reviewed
staging tool and a repeated run of the exact Linux package demonstrated movement and clean exit toward three instances of one
static feature, with fresh frames inspected, inputs and package files read back unchanged and no career files created. The
independent review receipt has SHA-256 `ccb53107417183050541a5da3aa111f5dac1bf5500d35d8125529e9bb6d75b77`; the repeated-run
receipt has SHA-256 `25e70811254e85d256dc60d40969b155086f6c274604594e9381189ba13eff4b`. This sparse arrangement is a
prototype, not the complete museum. Collision, damage behaviour, physical mouse feel, audible sound and Windows runtime remain
unvalidated; the offscreen driver reported unsupported relative-mouse mode.

## The project

The JSON object has exactly these fields:

| Field | Meaning |
| --- | --- |
| `format` | `onslaught.ce.museum.v1` |
| `id` | A simple lowercase identifier for the generated mod folder. |
| `name` | An authored display name. |
| `carrier` | The local resource level and its complete archive SHA-256. |
| `start` | An exact source start binding, an authored offset and orientation. |
| `exhibits` | One to 64 authored exhibit placements, each with a unique `id`. |

`carrier` contains `level` and `sha256`. A placement contains `source`, `offset` and `orientation`; exhibits
also contain `id`. Each vector has three finite components. Offsets are relative to the bound start position,
in the game's world axes; orientation components use the existing world codec's native convention. This
developer format has not yet acquired friendly 3D editor controls or a degree-based rotation interface.

A `source` contains `world` (`BSWD` or `RLWD`), the zero-based `ordinal` in that world's decoded `things` array,
and `sha256`. The record hash is SHA-256 of the complete decoded record serialized as sorted-key, compact,
ASCII JSON with non-finite JSON numbers refused. The public helper `record_digest` in `tools/ce_museum_stage.py` computes it. The archive
pin and record pin must both match. The source start must have kind `start` and select the primary player;
the generated visitor's start has `playerNumber` 1. Every exhibit must have kind
`feature` and a nonempty feature definition. A name, basename or display label is never a substitute for that
binding. Catalogue mesh identities are not guessed or changed by this adapter.

The stage creates a new visitor start and new named feature placements. It does not copy their source script
attachments, positions, target references or spawn instructions. The feature definition and player configuration
remain resource bindings to the owner's installation; their native rendering, sound and damage properties are
not rewritten or certified by the content adapter.

## Generated content and limits

Both generated world bodies exclude the source campaign's actors, scripts, navigation paths, tree populations
and automatic named-mesh spawns. The real body contains only the authored visitor start and exhibit placements;
the base body contains no actors. Its parent-world and map references keep the carrier's resource context.
The adapter reads its encoded result back and checks
these invariants independently of the composition path. These are content checks, not evidence that every native
runtime system is inactive. Ordinary physics and input still need to run for a visit to be usable.

Terrain and resources are read from the locally owned installation; the adapter does not copy or rewrite the
resource archive. The carrier's resource-format marker, distinct base/real world filenames and parent bindings
are checked before staging. The output is an authored arrangement using existing terrain and assets, not a
newly modelled room or redistributed asset pack. Generated worlds contain game-derived bindings: keep them
private and out of Git, issue attachments and releases.

The adapter reads the selected installation and writes only a new output folder. It refuses an output in the
selected game tree, symlinked input files and replacement of existing output. It writes the two world files
first and `mod.json` last, using the shared protected-output helper. It does not launch the game,
change an enabled-mod list, access careers or modify the installation. Its mod declares `ce_min` 0.1.13; do not remove that
check to make an unversioned diagnostic build load it. The visitor start is fixed by the stage tool (`planeMode` 0,
`playerNumber` 1); whether `planeMode` 0 allows flight has not been checked in the CE source, so no flight availability is claimed.
The tool enforces these input bounds: a project file of at most 128 KiB, one to 64 exhibits, vector components that are finite
and at most 8192 in absolute value, a carrier level from 0 to 849, a source ordinal from 0 to 999, a carrier archive of at most
64 MiB, and an `id` matching `[a-z0-9][a-z0-9_-]{0,47}`.

## Developer commands

Run the authored checks without an installed game:

```sh
python3 -B tools/ce_museum_stage_tests.py
```

With a locally prepared and pinned project, stage into a new private folder outside the game:

```sh
python3 tools/ce_museum_stage.py --project museum.json --game path/to/owned-game --out private-generated
```

The JSON the command prints includes `launchLevel`, the carrier level to open. Place the generated mod under a **new,
museum-only** CE user folder's `mods/` directory and enable only its `id` with `mods=<id>` in that folder's
`ce.ini`. Leave ordinary CE profiles untouched. Use the regular launcher's argument forwarding:

```sh
BEA_USER_DIR=path/to/museum-only-user BEA_GAME_DIR=path/to/owned-game \
  path/to/onslaught-ce --no-update-check -- -level CARRIER_LEVEL -skipfmv
```

Substitute the stage's numeric `launchLevel` for `CARRIER_LEVEL`. This launches the experimental exhibition
directly; it is not a campaign menu option. Do not start a career or another level using this profile: the
overridden base world may also be shared by other levels. A production museum entry needs its own runtime
context and must not expose these profile restrictions to ordinary play.

This lane has not validated Windows content generation or Windows runtime; the current CE mod path is Linux
only. Linux staging checks alone establish neither. A usable-room menu entry must wait for independent runtime
and career-safety acceptance and removal of the developer profile restrictions above.
