# Goodies Ghidra Comment/Tag Hardening - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra comment/tag hardening pass for eight Goodies frontend and resource-lifetime helpers:

- `0x0045ac30` `CFEPGoodies__BuildStaticGoodieDataTable`
- `0x0045c770` `CGoodieData__ctor`
- `0x0045c870` `CFEPGoodies__Deserialise`
- `0x0045c9f0` `CFEPGoodies__StartLoadingGoody`
- `0x0045cb80` `get_goodie_number`
- `0x0045cc10` `CFEPGoodies__LoadingGoodyPoll`
- `0x0045cd10` `CFEPGoodies__FreeUpGoodyResources`
- `0x0045cde0` `CFEPGoodies__ButtonPressed`

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime Goodies behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/goodies-wave395/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Hardened

| Address | Current saved name | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0045ac30` | `CFEPGoodies__BuildStaticGoodieDataTable` | PASS | Saved comments/tags record the retail Goodies metadata-table builder. Read-back shows writes into the contiguous table rooted near `DAT_00679848` and repeated `CGoodieData__ctor` calls for later records. |
| `0x0045c770` | `CGoodieData__ctor` | PASS | Saved comments/tags record the six-field `CGoodieData` initializer. Read-back writes `Method`, `Method2`, `Number`, `Number2`, `mT1`, and `mT2` into offsets `0x00`, `0x04`, `0x08`, `0x0c`, `0x10`, and `0x14`. |
| `0x0045c870` | `CFEPGoodies__Deserialise` | PASS | Saved comments/tags record resource deserialization after `CFEPGoodies__FreeUpGoodyResources`. Read-back includes `GDAT` payload handling, texture-array/height state, `CDXTexture__Deserialize`, `CMesh__Deserialize`, and mesh-slot state evidence. |
| `0x0045c9f0` | `CFEPGoodies__StartLoadingGoody` | PASS | Saved comments/tags record the selected-Goodie load starter. Read-back resets image pan offsets, calls `get_goodie_number`, builds the `-1000-goodie` resource id pattern, stores type/state fields, and starts the async 5MB resource-load path for load-backed buckets. |
| `0x0045cb80` | `get_goodie_number` | PASS | Saved comments/tags record the Goodies wall coordinate map: row `0` covers bios/race/developer ids, row `1` covers unit ids, row `2` covers FMV ids, row `3` covers artwork/model ids, and invalid cells return `-1`. |
| `0x0045cc10` | `CFEPGoodies__LoadingGoodyPoll` | PASS | Saved comments/tags record async load polling. Read-back checks loader state, tests `CBinkOpenThread__IsRunning`, reads the `-1000-goodie` resource through `CResourceAccumulator__ReadResourceFile`, closes/frees the membuffer, and marks the Goodie loaded. |
| `0x0045cd10` | `CFEPGoodies__FreeUpGoodyResources` | PASS | Saved comments/tags record Goodie payload cleanup. Read-back releases mesh/texture payloads, destroys texture backing resources, frees the texture pointer array, clears counters/slots, and resets Goodie state to `NO_GOODY`. |
| `0x0045cde0` | `CFEPGoodies__ButtonPressed` | PASS | Saved comments/tags record Goodies wall input handling. Read-back uses `mCX/mCY`-style grid coordinates, calls `get_goodie_number`, loads selectable unlocked/cheat-overridden Goodies, marks viewed entries old, and frees resources on back/close paths. |

## Commands Run

```powershell
py -3 tools\ghidra_goodies_wave395_probe_test.py
py -3 -m py_compile tools\ghidra_goodies_wave395_probe.py tools\ghidra_goodies_wave395_probe_test.py
cmd.exe /c npm run test:ghidra-goodies-wave395
py -3 tools\release_curated_manifest.py
py -3 tools\release_curated_manifest.py --check
py -3 tools\release_profile_snapshot.py
py -3 tools\release_profile_snapshot.py --check
cmd.exe /c npm run test:public-allowlist
cmd.exe /c npm run test:md-links
cmd.exe /c npm run test:doc-commands
py -3 tools\docsync_check.py
cmd.exe /c npm run test:repo-hygiene
```

Focused result: PASS after the public note and read-back token expectations were aligned with the saved Ghidra export shape.

Headless dry/apply results:

- Dry run: `updated=0 skipped=8 missing=0 bad=0`.
- Apply: `updated=8 skipped=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `8` metadata rows.
- `8` decompile exports.
- `116` xref rows.
- `8` tag rows.
- `712` instruction rows.

Release/docs validation results:

- Curated manifest selected `2148` files and the generated public allowlist check passed.
- Release profile snapshot reported `R0=2214 R2=0 R3=2 R4=18188`.
- Public allowlist safety checked `2148` rows.
- Markdown links passed.
- Documented npm command references checked `3156` rows.
- Docsync passed.
- Repo hygiene passed after `29` unit tests and live checks covering `23` text rules, `2` path rules, and `1` required marker.

## What Is Proven

- The saved Ghidra project now records hardened comments and tags for all eight Wave395 Goodies targets.
- The saved function names and signatures were preserved during this tranche.
- The focused proof script validates saved metadata, tags, selected decompile tokens, xref context, instruction tokens, dry/apply summaries, and public overclaim boundaries.
- The static source and retail read-back evidence tie the tranche to Goodies metadata construction, Goodie resource deserialization/loading/polling/freeing, Goodies wall coordinate mapping, and Goodies wall input handling.

## What Is Not Proven

- This does not prove runtime Goodies behavior.
- This does not prove hidden Goodies 71-73 reachability.
- This does not prove all Goodies assets/playback/viewer coverage.
- This does not prove exact concrete struct layouts, local variable names, local types, or all class fields.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra comment/tag hardening evidence after focused probe validation. Treat this as static retail-binary evidence and source-parity support, not as runtime behavior evidence or source-complete gameplay implementation.
