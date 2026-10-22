# Reverse-Engineering Index

Status: active — the front door to the game documentation
Last updated: 2026-10-22 (patch recipes: the executable-patch catalog and its contract were retired; removed the tracked retail string table row)
Summary: where the documentation of Battle Engine Aquila lives, what each store covers, and the rules a claim about the shipped game has to meet before it is written down.

This tree documents *Battle Engine Aquila* as prose and specs: file formats, save and options layouts, mechanics,
assets and mission data, per-function notes and behaviour contracts, patch analyses, and notes on Stuart's pinned
source release (GitHub `stuart73/Onslaught`, in `references/Onslaught`). Since 2026-10-15 the byte-matching decompilation of the retail executable (private `bea-decomp`,
5,482 of 5,482 functions) is the authority behind these documents; new findings cite its functions and never quote
its code.

The Ghidra-era campaign that produced many of these notes has ended. Its records (the tracked Ghidra checkpoint,
`developer_state.json`, the evidence register, the Ghidra function ledger, the source crosswalk, the full-pass wave
record and the promotion, boundary and naming records) and the decompiler listings that used to sit in some notes
moved to the private repository `dlprentice/onslaught-re-archive`, byte-exact at their old paths. Notes that cite
them say "(private RE archive)". Generation numbers, grade counts and Ghidra database versions quoted in dated
notes are history.

## Evidence rules

- Static names, types, strings, and call relationships prove only the structures
  they directly demonstrate.
- Stuart's source release (`references/Onslaught`) and the AYA extractor are references, not proof of the
  Steam executable's implementation or complete format support.
- Controlled copied-runtime observations establish only the measured behavior
  and specimen described by their evidence.
- Deterministic rebuild agreement does not re-prove retail behavior or establish
  gameplay, visual, or rebuild parity.
- Retail executables, saves, debugger logs, and runtime frames remain untracked
  local inputs. Retail assets and conversions are locally materialized and
  ignored. The narrow save fixture is the one tracked payload exception; no Ghidra
  database or decompiler output is tracked.

## Start here

| Area | Canonical entry point |
| --- | --- |
| First-party development sources | [Development source index](DEVELOPMENT_SOURCE_INDEX.md) |
| Cross-platform engine architecture | [GDC deck / binary synthesis](ENGINE_ARCHITECTURE.md) |
| PC demo versus retail | [Build and virtual-target comparison](DEMO_VS_RETAIL.md) |
| Function and behavior contract system | [Contract front door](../CONTRACTS.md) |
| Pinned-source narrative | [Stuart source synthesis](source-code/stuart-source-synthesis.md) |
| Save and options formats | [Save-file index](save-file/_index.md) |
| Retail binary analysis | [Binary-analysis index](binary-analysis/_index.md) |
| Pinned source references | [Source-code index](source-code/_index.md) |
| Measured mechanics | [Game-mechanics index](game-mechanics/_index.md) |
| Assets and mission data | [Game-assets index](game-assets/_index.md) |
| Compact lookups | [Quick-reference index](quick-reference/_index.md) |
| Attribution and known limits | [Project metadata](project-meta/_index.md) |

Further down this page: the patch recipes, the per-subsystem static contracts, the 2026-05-26 review cohort,
the reference documents, and the retail → Core translation policies the earlier fixed-point rebuild (Core) used.

## Patch recipes — analysis documents, not write authorization

These are analysis documents. They record where a byte lives, which function
owns it, what the clean bytes are, and what was observed when an **app-owned copied**
executable carried the change. Those observations authorize only their measured
copied targets. Applying a proved recipe to an installed target is a separate
user choice behind the owning verified-backup precondition; the original
`BEA.exe.original.backup` is never a target. Documenting patch knowledge is not
write authorization, and hiding these notes would not make a game safer—only the
evidence harder to find.

The executable-patch catalog these notes were written against (`patches/`, with
its contract) was retired on 2026-10-22 together with the patching code: the
companion never modifies a game executable, and enhancements belong in Onslaught
CE as opt-in options. Git keeps the catalog (commit `86d1af7` is the last that
has it). The notes below record where each byte lives and what was observed; for
this image a file offset maps to a virtual address as `VA = file_offset +
0x400000` in every section, measured on the pristine specimen (SHA-256
`74154bfa…`).

**Two documents in this family carry a withdrawn claim.** The 2026-07-28
guard-byte correction struck a hex-edit recipe out of both
`windowed-mode-analysis.md` and `widescreen-patch-analysis.md`. Both keep the
withdrawn text visible and struck through rather than deleting it. Read the
correction before acting on either.

### The widescreen family — one external patch, fully accounted

| Document | What it settles |
| --- | --- |
| [Widescreen patch analysis](binary-analysis/widescreen-patch-analysis.md) | The `BEA_Widescreen.exe` diff: **191 changed bytes across 28 regions**, file length unchanged, code-cave-plus-trampoline technique, both SHA-256s recorded. Historical **external** patch analysis — explicitly *not* the current WinUI/AppCore catalog patch contract. Its guard-byte normalization section is **withdrawn (2026-07-28)**. |
| [28-region diff table](binary-analysis/widescreen-diff-regions-28.tsv) | The machine-readable canon: file offsets, VAs, before/after bytes, `owner_fn`, `evidence_refs`, behavior classification. A `.tsv`, not prose — read it when the exact region is what you need. |
| [Unresolved-region tracker](binary-analysis/widescreen-diff-unresolved.md) | The queue, and it is **empty**: 14 `known-functional`, 14 `known-supporting`, **0 `unknown-needs-RE`**. The part worth reading is the three reopen criteria — this is a closed queue, not a solved subject. |
| [Regions 8–11 validation](binary-analysis/widescreen-regions-8-11-validation.md) | How the last four uncertain regions were closed: hook sites and cave payloads disassembled from both binaries. |

### Per-feature patch notes

| Document | Anchor, and how far the claim reaches |
| --- | --- |
| [CLI defaults and complete parser](binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md) | September 19: initializer ownership corrected from Unit AI to CLIParams; four defaulting controls, 47 isolated original-parser cases and the 25-option static map. Separates developer, autoconfig/cheat-query and frontend override fields; pins parser/pool/logger ordering. OS/printf calls are intercepted; no trace-request consumer or later developer-selector writer identified. Actual startup and downstream acceptance remain open. |
| [Windowed mode](binary-analysis/windowed-mode-analysis.md) | **Partially superseded 2026-07-28, and the withdrawn half is the half people used.** `-forcewindowed` is real and reachable, but its parser gate `DAT_00662f3e` is **BSS — zero at load** and is set only by `-testeur` appearing *earlier on the same command line*. The old "normalize the guard byte in a hex editor" recipe was false: there is no file byte to edit. The two-gate model and the startup-flow patch at file offset `0x12A644` stand. |
| [Extra-graphics feature gate](binary-analysis/extra-graphics-feature-gate-patch.md) | `GEFORCE_FX_POWER` registers with default `0`; `0x004CDD40`, `6A 00` → `6A 01`. Carries the companion row that ignores `cardid.txt` vendor/device matching. |
| [Version overlay](binary-analysis/version-overlay-patch.md) | The opt-in `V1.00 - PATCHED` marker as a **pair**: a visible pointer row plus a hidden cave-string payload row. One bounded copied-game title/menu run confirmed the marker; no broader overlay or parity claim. |
| [Frontend clear-screen colour](binary-analysis/frontend-clear-screen-color-patch.md) | Three mutually exclusive immediates at `0x00540F88` in `CDXFrontEnd__RenderStart`; source anchor `references/Onslaught/DXFrontend.cpp`. |
| [Goodies gallery display unlock](binary-analysis/goodies-gallery-display-unlock-patch.md) | Forces the existing display flag inside `CFEPGoodies__Process` (`0x0045D7F4`). **Display only — it does not alter save progression.** Also records the earlier candidate rejected for omitting the stack repair, before any behavior claim was made. |
| [Free-camera Aurore-gate bypass](binary-analysis/free-camera-aurore-gate-bypass-patch.md) | NOPs the `IsCheatActive(4)` gate on `BUTTON_TOGGLE_FREE_CAMERA` in `CGame__ReceiveButtonAction`, plus eight mutually exclusive keyboard cave variants. **Experimental**: establishes the gate effect in one controlled comparison, not general camera safety. |
| [Pause-key default row](binary-analysis/pause-key-default-row-patch.md) | One immediate in `OptionsEntries__InitDefaultSingleBindingsTable` (`0x005144CD`, `01` → `18`). **Experimental**, one bounded pause/resume observation. |

## Static contracts — per subsystem

Bounded static maps, one subsystem each. They establish addresses, call
relationships, constants, and structures visible in the analyzed specimen, and
nothing about runtime behavior, exact object layouts, source-body identity,
patch safety, or rebuild parity.
[`binary-analysis/mapped-systems.md`](binary-analysis/mapped-systems.md) is the
routing table naming the **current** owner per system; the list below is the
flat inventory.

| Subsystem | Contract |
| --- | --- |
| MissionScript / IScript | [missionscript-iscript-static-contract.md](binary-analysis/missionscript-iscript-static-contract.md) |
| PhysicsScript | [physics-script-static-contract.md](binary-analysis/physics-script-static-contract.md), with the [copied-corpus parser proof](binary-analysis/physics-script-copied-corpus-parser-proof.md) |
| Meshes and resources | [mesh-resource-render-static-contract.md](binary-analysis/mesh-resource-render-static-contract.md) |
| Render/resource bridge | [render-resource-bridge-static-contract.md](binary-analysis/render-resource-bridge-static-contract.md) |
| Texture decode | [texture-resource-decode-static-contract.md](binary-analysis/texture-resource-decode-static-contract.md) |
| HUD and frontend overlay | [hud-frontend-overlay-static-contract.md](binary-analysis/hud-frontend-overlay-static-contract.md) |
| HUD source-method identity correction | [hud-source-identity-correction-2026-08-12.md](binary-analysis/hud-source-identity-correction-2026-08-12.md) |
| Collision-component implementation-identity correction | [collision-component-identity-correction-2026-08-12.md](binary-analysis/collision-component-identity-correction-2026-08-12.md) |
| Destroyable segments | [destroyable-segments-static-contract.md](binary-analysis/destroyable-segments-static-contract.md) |
| Units, movement, weapons | [unit-battleengine-gameplay-static-contract.md](binary-analysis/unit-battleengine-gameplay-static-contract.md) |
| Local multiplayer | [local-multiplayer-static-runtime-contract.md](binary-analysis/local-multiplayer-static-runtime-contract.md) |
| Career progression bridge | [career-progression-static-bridge-contract.md](binary-analysis/career-progression-static-bridge-contract.md) |
| Level 100 final wave: turrets, Missile Pod locks, crosshair refresh, seeking rounds and RNG-drawing owners | [level100-final-drone-wave.md](game-mechanics/level100-final-drone-wave.md) |
| Battle Engine weapon stores, charge law and firing state | [battle-engine-weapon-stores.md](game-mechanics/battle-engine-weapon-stores.md) |
| Battle Engine auto-aim, launch position and cockpit Gun emitters | [battle-engine-aiming.md](game-mechanics/battle-engine-aiming.md) |
| Level 100 construction order: shared draws, queued events and the first event flush | [level100-construction-order.md](game-mechanics/level100-construction-order.md) |
| World 110 construction order, the Level 100 to World 110 transition, first flush and player start | [world-110-construction-order.md](game-mechanics/world-110-construction-order.md) |
| Named waypoint paths: loading, start node, following and the Level 100 and World 110 routes | [waypoint-paths.md](game-mechanics/waypoint-paths.md) |
| Dropship flight: per-tick move, guide steering, turning and move orders | [dropship-flight.md](game-mechanics/dropship-flight.md) |
| Dropship landing: landing states, `Land()`, unloading, withdrawal, turret and AI schedule | [dropship-landing.md](game-mechanics/dropship-landing.md) |
| Walker dash: the retail timing window, its float32 frame table and the strafe roll | [walker-dash.md](game-mechanics/walker-dash.md) |
| CMSH `CPOS`/`CORI` identity | [cmsh-cpos-cori-identity-2026-07-25.md](binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md) |

Machine-readable siblings, for consumers that should not be parsing prose:

- [MissionScript VM datatype/opcode schema](binary-analysis/missionscript-vm-datatype-opcode-schema.v1.json)
- [First-flight camera/movement/morph contract](binary-analysis/first-flight-camera-movement-morph-contract-candidate.v1.json)
  — a **candidate**, as its own filename says; not an accepted contract.
- Retail specimen manifest (private RE archive: `reverse-engineering/binary-analysis/retail-specimen-manifest-2026-03-14.json`)
- 2026-08-31 current function name table (private RE archive: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-31.tsv`)
  — the address-to-saved-name resolution authority for this dated projection,
  produced from the verified mutable `db.18635` activation POST export. That export is
  byte-identical to the reviewed tracked `db.18634` PRE export; the table has the
  same addresses and body bounds as 2026-08-17 and exactly 37 later name changes.
- 2026-08-17 function name table (private RE archive: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`)
  — a frozen 8,329-row address-to-name projection from the read-only
  **db.18626** POST readback after the five-row `name-cohort5`. It carries the
  four HUD route demotions, the 158 renames of the 2026-08-17 name cohort, the
  CTentacle chain's two rows (`0x004f07e0`
  `CTentacle__CreateTentacleGuide`, `0x004f0860`
  `CTentacle__CreateTentacleAI`), and the five `name-cohort5` rows. It is
  intentionally 37 later SET_NAME rows behind the preserved `db.18634`
  checkpoint and is provenance, not a current name oracle.
- 2026-08-13 function name table (private RE archive: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-13.tsv`)
  — frozen 8,329-row provenance from the 2026-08-14 D3DX two-function db.18618
  readback, retained for the checks and receipts pinned to it.
- 2026-08-12 function name table (private RE archive: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-12.tsv`)
  — frozen 8,136-row provenance retained for Generations 20–23 and its other
  pinned consumers.
- 2026-07-27 function name table (private RE archive: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv`)
  — dated 7,555-row provenance retained for its pinned consumers.

The MissionScript **command-descriptor** schema that used to sit beside these
was deleted in `981c3379`; the 144-entry native registry it duplicated now lives
in `ghidra-functions.md` (private RE archive). Most of the contracts above
have no `.json` sibling at all. Do not go looking for one.

## The 2026-05-26 static-review cohort — the oldest layer here

Six system slices from the May 2026 wave era, all dated `2026-05-26`. **This is
the oldest cohort in the store and the one most likely to mislead.** Read them
for subsystem shape, not for numbers: their prose carries live-database
accounting (`6113/6113`, `6411/6411`, wave and candidate counts) that was a
reading of the maintainer's database at the time. For what a function count can
mean today, use the
RE coverage baseline (private RE archive: `reverse-engineering/binary-analysis/re-coverage-baseline-2026-07-25.md`); for
anything at function granularity,
[`binary-analysis/functions/`](binary-analysis/functions/_index.md) supersedes
these slices wherever a note exists.

The standing column below is read off `mapped-systems.md`'s owner table, not
asserted here — where that table still names the 05-26 document, so does this one.

| Slice | Standing |
| --- | --- |
| [Save, options and startup](binary-analysis/save-options-static-review-2026-05-26.md) | September 19–20 independent recheck: original startup/serialization and menu-to-startup handoff distinguish live from next-boot settings. Direct presets and 19 composed loader cases establish binding replacement and same-process metadata effects. Sixteen composed language cases distinguish the requested selector from the active header serialized by Save. Real language loading, audio and complete real-file compatibility remain open; older evidence is identified separately. |
| [Audio, media, cutscene](binary-analysis/audio-media-cutscene-static-review-2026-05-26.md) | **Still the cited owner** for audio, media, cutscenes, and camera. The wave counts inside it are snapshots. |
| [Frontend, input, game loop](binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md) | Superseded for frontend/HUD by [hud-frontend-overlay-static-contract.md](binary-analysis/hud-frontend-overlay-static-contract.md). Its companion proof-plan file no longer exists in the tree; the 2026-07-28 correction inside it gives the `git show` needed to recover it. |
| [Unit / BattleEngine gameplay](binary-analysis/unit-battleengine-gameplay-static-review-2026-05-26.md) | Superseded by [unit-battleengine-gameplay-static-contract.md](binary-analysis/unit-battleengine-gameplay-static-contract.md) (2026-07-16). |
| [Mesh, motion, world, particle](binary-analysis/mesh-motion-world-particle-static-review-2026-05-26.md) | Superseded for meshes and resources by [mesh-resource-render-static-contract.md](binary-analysis/mesh-resource-render-static-contract.md) and [render-resource-bridge-static-contract.md](binary-analysis/render-resource-bridge-static-contract.md). |
| [Texture and render](binary-analysis/texture-render-static-review-2026-05-26.md) | Superseded for decode by [texture-resource-decode-static-contract.md](binary-analysis/texture-resource-decode-static-contract.md), and for render state by the 2026-07 terrain and D3D notes above. |

## Reference and routing

| Document | Use it for |
| --- | --- |
| [Mapped systems](binary-analysis/mapped-systems.md) | The routing table from a system to its current smallest evidence owner *and* to the code that consumes it. Start here when you know the subsystem but not the document. Not a function-completion ledger. |
| [High-impact call chains](binary-analysis/high-impact-call-chain-appendix.md) | Static chains with the product consequence spelled out — that loading a retail save can rewrite the boot-time options snapshot, that resume/exit can persist both career and `defaultoptions.bea`. This is the appendix explaining *why* AppCore patches real baselines and preserves unknown bytes instead of synthesizing saves. |
| [Executable analysis](binary-analysis/executable-analysis.md) | PE identity, hashes, size, DLL imports, the D3D9 confirmation, and the Lost Toys/Encore branding note. Its function-count row now carries the whole moving chain — 5,771 → 6,411 → **6,969** — and says plainly that this is a recovery count, not a property of the binary. |

## Retail → Core translation policies

These policies belong to the earlier fixed-point rebuild (Core), now reference material; they stay as a record of
how its Core constants were derived.
[`game-mechanics/_index.md`](game-mechanics/_index.md) lists the measurements.
It does not list the **policies** that convert a measured retail quantity into a
deterministic-Core constant — and those are the documents a Core edit is
supposed to cite.

**Four of the seven were superseded on 2026-07-28, and the supersession is
partial in a way that is easy to misread.** In each case the *retail
measurement* stands and the *Core mapping* does not: the authority for the Core
value moved from copied-runtime measurement pairs to the shipped
`data/battle engine configurations.dat` bytes, and flat scalars became
two-ended envelopes. Citing one of these for its measurement is fine; citing it
to authorise a Core constant is not.

| Policy | Status, as the document itself now states it |
| --- | --- |
| [Jet forward scalar](game-mechanics/jet-forward-retail-to-core-translation-policy.md) | Accepted (2026-07-14) **for the retail measurement**; **superseded 2026-07-28 for the Core mapping.** `JetSpeedPerTick` no longer exists; Core carries a min/max envelope read from shipped data. |
| [Jet energy drain](game-mechanics/jet-energy-drain-retail-to-core-translation-policy.md) | Accepted (2026-07-14) **for the retail measurement**; **superseded 2026-07-28 for the Core mapping.** The flat scalar became a thruster-interpolated pair. |
| [Energy drain/regen](game-mechanics/energy-retail-to-core-translation-policy.md) | **Superseded 2026-07-28 for both halves.** The `energy-p02` measurement stands; walker regen is no longer provisional — and the old "provisional" label had become actively misleading. |
| [Projectile speed](game-mechanics/projectile-speed-retail-to-core-translation-policy.md) | **Draft — but a Core constant shipped anyway; superseded in part 2026-07-28.** Whether the measurement clears the dual-accept bar is recorded as an explicit `UNKNOWN` maintainer decision. |
| [Walker ↔ jet transform/morph](game-mechanics/walker-transform-morph-retail-to-core-translation-policy.md) | **Accepted bounded mapping.** Unchanged. |
| [Shield](game-mechanics/shield-retail-to-core-translation-policy.md) | **Ownership source-backed; the rate remains blocked.** Unchanged. |
| [Fire cooldown](game-mechanics/fire-cooldown-retail-to-core-translation-policy.md) | **Draft — blocked on a dual-accept that has not landed.** Authorization for nothing. |

Three of the seven have a machine-readable measurement behind them. The other
four do not, and the policy `.md` is the whole record — there is no
`*-translation-policy.json`:

- [jet-forward-scalar-response-v1](game-mechanics/jet-forward-scalar-response-v1.md)
  / [`.json`](game-mechanics/jet-forward-scalar-response-v1.json)
- [jet-energy-drain-scalar-response-v1](game-mechanics/jet-energy-drain-scalar-response-v1.md)
  / [`.json`](game-mechanics/jet-energy-drain-scalar-response-v1.json)
- [walker-transform-morph-timing-v1](game-mechanics/walker-transform-morph-timing-v1.md)
  / [`.json`](game-mechanics/walker-transform-morph-timing-v1.json)

## Product-facing summaries

- [Save/options boundary](public-save-options.md)
- [Assets and modding boundary](public-assets-and-modding.md)
- [Static contracts](public-static-contracts.md)

Guarded asset tools, parsers and capture analysis live under [`tools/`](../tools/README.md). Applying a proved patch
to an installed target is a separate, explicit user choice behind a verified
pre-write backup. The pristine `74154bfa…` specimen is never writable.
