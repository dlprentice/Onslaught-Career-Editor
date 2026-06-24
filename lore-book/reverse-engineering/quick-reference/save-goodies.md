Status: active quick reference
Last updated: 2026-05-08
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: Goodie/unlockable save lookup.
# Goodies System

## Offsets

Base (true dword view): 0x1F46, each 4 bytes.
```
Goodie N = 0x1F46 + (N * 4)
```

## State Values

| Value (true view) | Legacy aligned view | Enum | Display |
|-------------------|--------------------|------|---------|
| 0x00000000 | 0x00000000 | GS_UNKNOWN | Locked |
| 0x00000001 | 0x00010000 | GS_INSTRUCTIONS | Locked+hints |
| 0x00000002 | 0x00020000 | GS_NEW | Gold badge |
| 0x00000003 | 0x00030000 | GS_OLD | Blue badge |

## Categories (233 total displayable, indices 0-232)

| Range | Content | Count |
|-------|---------|-------|
| 0-7 | Character Bios | 8 |
| 8-11 | Battle Engine Units | 4 |
| 12-65 | Enemy Units | 54 |
| 66-70 | Race Levels | 5 |
| 71-73 | Intended source-level image Goodies with shipped texture-only archives (`ca_be_final01`, `ca_be_final02`, `ca_bea_battle_pic`), unlock/instruction hooks, and no known wall coordinate | 3 |
| 74-77 | Developer Items | 4 |
| 78-200 | Concept Art | 123 |
| 201-232 | FMV Cutscenes | 32 |

## Shipped Goodies Archive Census

Read-only archive census evidence from the local PC install (`release/readiness/goodies_resource_archive_census_2026-05-08.md`) parses every shipped `goodie_*_res_PC.aya` archive down to `GDIE -> GDAT` metadata:

| `GDAT` kind byte | Interpreted content family | Count |
| ---: | --- | ---: |
| 0 | Texture/artwork | 149 |
| 1 | Model/gallery | 45 |
| 2 | Video/cutscene | 33 |
| 3 | Level/metadata | 5 |

The census found 232 shipped Goodie archives for 233 displayable slots. Slot 232 is the only displayable slot without a matching `goodie_232_res_PC.aya` archive in the checked PC install. Each parsed archive has `LVLR`, `TARG`, `AYAD`, and `GDIE` top-level chunks, and every embedded `GDAT` Goodie index matches its archive index. This is static resource provenance, not runtime wall reachability or model-viewer proof.

Model-viewer alignment evidence (`release/readiness/goodies_model_viewer_alignment_2026-05-08.md`) proves the source `GT_MESH` Goodie set matches the installed `GDAT` kind-1 resource set and generated catalog Model set: indices 8-57 excluding 12, 13, 24, 33, 34, and 35, plus index 76, for 45 model Goodies. Model-viewer read-back evidence (`release/readiness/goodies_model_viewer_readback_2026-05-08.md`) also proves existing retail Ghidra exports contain the mesh deserialization branch and mesh interaction/update branches for bucket value `1`. This proves source/resource/catalog plus selected retail decompile alignment, not runtime viewer playback or final textured WinUI rendering.

## Character Bio Chain (SEQUENTIAL!)

Must unlock in order - cannot skip:

| Index | Character | Requirement |
|-------|-----------|-------------|
| 0 | Hawk | Complete Level 100 |
| 1 | Tatianna | Level 110 >= C |
| 2 | Kramer | Goodie 1 + Level 200 >= C |
| 3 | Lorenzo | Goodie 2 + Level 231/232 >= C |
| 4 | Tara | Goodie 3 + Level 321/322 >= C |
| 5 | Billy | Goodie 4 + Level 321/322 >= C |
| 6 | Carver | Goodie 5 + Level 621/622 >= C |
| 7 | Surt | Goodie 6 + Level 741/742 >= C |

## Developer Items (S-Grade Based)

| Index | Content | S-Ranks Required |
|-------|---------|------------------|
| 74 | Battle Engine Aquila Picture | 20 |
| 75 | Intro Storyboard Sequence | 40 |
| 76 | Team Photo | 43 (ALL) |
| 77 | Development | 43 |

Goodie 78 is not a developer item. Current source/static evidence maps it as the first concept-art row (`GOODIES_79`), unlocked by `GRADE(100) >= GRADE_C`.

Runtime note (2026-05-07): copied-profile Goodies wall replay with an all-Goodies copied save captured Race Challenge 1-5 at indices 66-70, then the next visible slot jumped to 74. It did not expose 71-73 through the normal top-row wall navigation. Asset metadata confirms 71-73 are real shipped texture-only archives with resolved texture refs, and the fresh full install catalog resolves each of the three rows to an existing exported PNG preview. The native WinUI real-catalog smoke can select and preview all three rows as artwork entries. `Career.cpp` source inspection confirms unlock/instruction hooks for those ids. Source-topology probing confirms 71-73 have data-table, texture-helper, unlock, and instruction entries, while `get_goodie_number` still has no direct 71-73 return, direct source state/API hits remain 0, and the unlock-all save-name cheat remains a coordinate-mapped display override rather than a direct hidden-selection path. Follow-up Ghidra recovery named and signed `CFEPGoodies__ButtonPressed`, then classified the former no-function `get_goodie_number` xrefs as navigation/selection-state paths. Source-access and Ghidra xref probes currently show no direct source API call, `CCareer__GetGoodiePtr` helper path, or direct data xref for the concrete 71-73 state slots. Mission-script `SetGoodieState` / `GetGoodieState` read-back confirms a separate indexed Goodie state access surface exists; the checked repo-local and installed Steam mission-script corpora use script indices 51, 53, and 68-71, with zero calls for 72-74 (save Goodies 71-73). A follow-up installed packed-resource text scan inflated 301 top-level AYA archives with zero inflate errors and found zero literal Goodie state API calls, so the remaining 71-73 question is hidden/indirect runtime reachability rather than obvious missing asset, export absence, WinUI preview absence, unlock-code absence, ordinary wall-row coverage, direct helper/data access, or literal installed packed-resource script calls.

Focused observer note (2026-05-08): `release/readiness/goodies_input_observer_runtime_proof_2026-05-08.md` proves the ordinary copied-profile input path reaches `CFEPGoodies__ButtonPressed` and returns `66, 67, 68, 69, 70, 74` with no `71`, `72`, or `73` on that normal right-navigation path. `release/readiness/goodies_hidden_path_static_refresh_2026-05-08.md` then reruns the source, script, packed-resource, xref, and existing Ghidra-export probes; those still show no direct source/script/xref selector for 71-73. The remaining question is hidden or indirect runtime reachability, not shipped-resource presence, source unlock support, WinUI preview support, or ordinary wall navigation.

Scalar scan note (2026-05-08): `release/readiness/goodies_scalar_reference_scan_2026-05-08.md` adds a broad instruction-scalar search for `0x47`, `0x48`, and `0x49`. The full scan is noisy because those values are common offsets/constants, but the parser reduces it to a focused frontend/script/career-adjacent candidate list for later classification. It does not prove hidden Goodies reachability.

Scalar classification note (2026-05-08): `release/readiness/goodies_scalar_candidate_classification_2026-05-08.md` classifies the focused scalar candidates as non-selector evidence: source-line/object-allocation metadata, stack cleanup/stride offsets, frontend page/icon state, virtual-keyboard layout/token constants, script runtime offsets, CRT noise, or texture parser offsets.

Runtime proof planning note: `release/readiness/goodies_71_73_hidden_runtime_proof_plan_2026-05-07.md` defines the next copied-profile-only runtime matrix for 71-73. `release/readiness/goodies_frontend_selection_static_review_2026-05-07.md` records the current frontend selection static review: normal coordinate selection still flows through `get_goodie_number(mCX, mCY)`, selected-path handlers have no direct `0x47`/`0x48`/`0x49` target constants, and `StartLoadingGoody` still has an image bucket that would handle 71-73 if a hidden path selected them. `release/readiness/goodies_packed_script_probe_2026-05-07.md` records the installed loose-script plus packed-resource literal text probe. AppCore includes `BesFilePatcher.PatchGoodieStates(inputPath, outputPath, statesByIndex)` as a targeted copied-save setup helper for that proof: it refuses in-place writes, validates fixed save size/version, writes true-view Goodie offsets, permits displayable indices 0-232, and preserves neighboring/reserved slots unless explicitly targeted. This is a setup primitive and still not runtime proof.

## FMV Cutscenes (201-231)

FMVs are NOT unlocked via `UpdateGoodieStates()`. They unlock at **runtime** when the cutscene is watched during gameplay.

FMV 232 maps to cutscene file 33 (gap in sequence - no file 32).

6 FMVs are NOT localized: 209, 212, 213, 214, 215, 216 (action sequences).

## Kill-Based Unlocks

See `FEPGoodies.cpp` for thresholds. Key categories:
- Aircraft: 25/50/75/100 kills
- Vehicles: 100/200/300/400 kills
- Emplacements: 25/50/75 kills
- Infantry: 40/80/120/160 kills
- Mechs: 20/40/60/80 kills

Kill-based goodies are evaluated at **runtime/save time**, not on load.

## BUG: Goodie 228 Overlap

Offset 0x22D4 is inside the goodies area in the **legacy aligned view**. In the true view, Goodie 228 is at 0x22D6 and `mCareerInProgress` is at 0x248A. Never write to 0x22D4 as if it were a progress flag.
