# Reverse-Engineering Index

Status: active — the RE evidence front door
Last updated: 2026-07-30
Summary: where RE evidence lives, what each store is authoritative for, and the
rules a claim about the shipped binary has to meet before it is written down.

This directory preserves evidence that materially supports the toolkit,
rebuild, modding work, or contributor understanding. Git history holds completed
waves, superseded plans, and generated accounting.

**Every authority figure under "Current static authority" below is dated
2026-07-27 and must be re-measured before it is used.** The residual, both
denominators, and each per-ledger count are readings taken against a live
maintainer database that has moved since. The section says so ledger by ledger;
it is said once here so that nobody quotes a number off this page without
re-running the grader that produced it.

## Evidence rules

- Static names, types, strings, and call relationships prove only the structures
  they directly demonstrate.
- Stuart Gillam's source and the AYA extractor are references, not proof of the
  Steam executable's implementation or complete format support.
- Controlled copied-runtime observations establish only the measured behavior
  and specimen described by their evidence.
- Deterministic rebuild agreement does not re-prove retail behavior or establish
  gameplay, visual, or rebuild parity.
- Retail executables, saves, debugger logs, and runtime frames remain untracked
  local inputs. Retail assets and conversions are locally materialized and
  ignored. The reviewed canonical Ghidra project and narrow save fixture are
  the explicit tracked payload exceptions.

## Start here

| Area | Canonical entry point |
| --- | --- |
| Cross-source synthesis | [Data/source/executable delta](../DELTA.md) |
| Agentic parity and function discovery | [Parity lab](../PARITY_LAB.md) |
| Installed data narrative | [Measured installation census](../BEA_DATA.md) |
| Executable/Ghidra narrative | [Ghidra function synthesis](../GHIDRA_FUNCTONS.md) |
| Pinned-source narrative | [Stuart source synthesis](../STUART_FUNCTIONS.md) |
| Save and options formats | [Save-file index](save-file/_index.md) |
| Retail binary analysis | [Binary-analysis index](binary-analysis/_index.md) |
| Canonical Ghidra project | [Distributable database](ghidra/README.md) |
| Pinned source references | [Source-code index](source-code/_index.md) |
| Measured mechanics | [Game-mechanics index](game-mechanics/_index.md) |
| Assets and mission data | [Game-assets index](game-assets/_index.md) |
| Compact lookups | [Quick-reference index](quick-reference/_index.md) |
| Attribution and known limits | [Project metadata](project-meta/_index.md) |

Further down this page, past the authority block: the patch recipes, the
per-subsystem static contracts, the 2026-05-26 review cohort, the lane
reference and runbooks, and the retail → Core translation policies.

## Current static authority

### The name-grading residual — current figure, and the flag it requires

**`1,867` of a human-namable `6,376` = 29.3 %**, as of 2026-07-27.

**This figure is meaningless without its precondition.** It is only valid when
the grader is run with `--reference-source references/Onslaught`. **Without that
flag the same inventory grades to `2,089`** — a difference of 222. A residual
quoted bare is ambiguous and must not be relied on; state the flag every time.

The denominator moved and the residual did not. Three Ghidra mutation waves and
the naming wave, all applied to the live maintainer DB on 2026-07-27, took the
graded function count `6,969 → 7,555` and the human-namable denominator
`5,790 → 6,376`, because the Instruction Finder created real functions. The
residual stayed at `1,867` throughout — these waves extend *coverage*; they
recover no developer-authored name. So the ratio improved from
`1,867 / 5,790 = 32.2 %` to `1,867 / 6,376 = 29.3 %` **without a single name
being recovered**, which is exactly the trap this metric sets.

*(Added 2026-07-27. The per-ledger figures below are dated snapshots against the
**6,969**-function inventory and are quoted as those ledgers state them; they
are not the current figure. The tracked `ghidra/` snapshot is the reviewed
6,411-function state and deliberately lags the live DB. The current 7,555-row
name projection, live/snapshot distinction, and mutation-wave reconciliation
are tracked in [`../GHIDRA_FUNCTONS.md`](../GHIDRA_FUNCTONS.md); bulky working
exports remain ignored under `local-lab/`.)*

### Specimen, coverage, and symbol ground truth

**Name the specimen and its hash on every byte finding.** There are two retail
binaries on this project and they are not interchangeable — the installed Steam
executable carries local patches. The rule and the three authoritative hashes:

- [Retail specimen baseline — which binary, which hash, and why it matters](binary-analysis/retail-specimen-baseline.md)

*(Indexed 2026-07-27. These four entries were previously reachable from no
tracked document, or — for the specimen baseline — only from
`binary-analysis/_index.md`. The repo-wide link check passes on all of them
because it validates link **targets**, not document **reachability**; the two are
different failure modes and only the first was being tested.)*

- [RE coverage baseline — what the 6,411-function pass actually covers](binary-analysis/re-coverage-baseline-2026-07-25.md)
  — 2026-07-25. The functions that exist are sound; the **set** of functions is
  incomplete. 468,804 exported instructions verified against the pristine binary
  with **0 byte mismatches**, 6,351 of 6,411 functions fully clean — but only
  **79.8268 % of `.text` was covered by those 6,411 historical bodies**.
  Coverage of the current 7,555-row inventory is **UNKNOWN** until a fresh
  interval export is measured. Reproducible for the historical population in
  under a minute with `tools/re_verify.py`.
- [RTTI and source-path evidence — a documented ground truth was wrong](binary-analysis/rtti-and-source-path-evidence-2026-07-25.md)
  — 2026-07-25. **Read this before repeating "the binary has no symbols."**
  Direct ASCII scan of the pristine specimen finds **667 RTTI type descriptors**
  and **166 source-file path strings** (`C:\dev\ONSLAUGHT2\*.cpp`/`.h`). The PE
  debug directory *is* stripped and there is no `.pdb` — that half of the old
  claim holds — but "no symbols, nothing was missed" was an over-generalisation
  from it. The RTTI owners and `__FILE__` translation-unit names that the 2026-07
  naming waves are built on come from exactly this material.
- [Retail capture provenance — what the reference screenshots actually show](binary-analysis/retail-capture-provenance-2026-07-25.md)
  — 2026-07-25. The frontend/HUD reference captures were taken from a **safe copy
  of the installed `BEA.exe`, not from pristine retail**. Anything that binary
  draws differently from pristine is a false parity target that will be
  faithfully reproduced as a defect — and at least one already was. Static byte
  comparison of both binaries plus direct pixel measurement; no decompiler
  output involved.

### Ghidra name grading and the fullpass expedition

- [2026-07 fullpass expedition handoff](binary-analysis/ghidra-fullpass-expedition-handoff-2026-07-25.md)
  — **historic; the branch it reports on no longer exists.**
  `ghidra/fullpass-quality-2026-07-23` was **merged into `main` at `af22af95`**
  on 2026-07-25 and the branch ref was deleted on 2026-07-27. Its history is in
  `main`. The document still carries standing instructions for a live branch
  ("Do not merge to main unless the user asks", a worktree path that no longer
  exists); read it as a record of that expedition, not as a live work item.
  *(Corrected 2026-07-27: this entry was labelled "(branch status)" and led the
  list as current authority.)*
- [Name-grading ledger — every name graded by its evidence](binary-analysis/name-grading-ledger-2026-07-26.md)
  — 2026-07-26 revision. Corrects `SOURCE_BACKED` (1,009 → **528**; the old figure
  matched elaborated type specifiers, and `CDXTexture` alone backed 368 rows with
  no definition anywhere), partitions `UNBACKED` into seven measured cohorts of
  which **1,179 are MSVC unwind funclets that can never carry a developer name**,
  and records the 13 renames applied to the live database. Honest residual **as
  that ledger states it**: 1,866 of a human-namable 5,790 (the ledger's own
  §"honest residual"; a demotion inside the same wave took it from 1,865 to
  1,866). **Snapshot, not current** — see the current figure above:
  **1,867 of 6,376**, with `--reference-source references/Onslaught`.
- [The second demotion — `0x005386d0`, and the residual goes up again](binary-analysis/name-grading-ledger-2026-07-27-demotion2.md)
  — 2026-07-27. Amends the 07-26 ledger **in two cells only**: the false name
  `CScriptEventNB__Destructor` on `CPostEventData`'s destroy path is withdrawn to
  `DestructorBody_005386d0`, taking the honest residual to **1,867** — of 5,790
  as that document states it, **of 6,376 today**; the residual itself has not
  moved since. Also restates the limit that keeps getting dropped: the sweep behind these
  demotions sees **only the destructor channel**, so its six findings are a
  **floor, not a bound**.
- **Aggressive Ghidra analysis does not reduce that residual — measured, not
  assumed.** Six isolated analyser passes on a disposable canary (Aggressive
  Instruction Finder, Decompiler Parameter ID, address/switch-table aggression,
  external-parameter propagation, variadic override, and a combined pass) left
  the residual **unmoved: 1,866 before and 1,866 after**, that pair being the
  experiment's own canary measurement against its then-baseline of 1,866, before
  the `0x005386d0` demotion above. **The current residual is 1,867 of 6,376**;
  the "does not reduce" verdict is what carries forward, not the baseline.
  The Instruction Finder
  recovered ~4,404 bytes of real application code but those land in `UNNAMED`,
  enlarging the namable denominator without moving the residual; external-
  parameter propagation moved it *up*, to 1,867, by correctly naming one
  function. Seven of the nine analysers the exercise set out to enable were
  **already on**. Do not re-run this as an untried lever. Evidence and
  per-pass verdicts: `local-lab/GHIDRA-AGGRESSIVE-ANALYSIS-2026-07-27.md`
  (untracked); tooling is `tools/ListAnalysisOptions.java`,
  `tools/RunIsolatedAnalyzer.java`, `tools/ExportFullFunctionInventory.java`,
  `tools/ExportLooseInstructions.java`, and `tools/ghidra_inventory_diff.py`.
  The [2026-07-25 revision](binary-analysis/name-grading-ledger-2026-07-25.md) is
  **superseded in its counts** and retained as the record of the RTTI re-prefix
  wave and the 0x08-byte incident.
- [PhysicsScript round and weapon-mode value ids — resolved](binary-analysis/physics-round-value-ids-2026-07-25.md)
- [Direct3D fog render states — `D3DFOG_EXP` slot, parameters, and far plane](binary-analysis/d3d-fog-render-state-static-contract-2026-07-25.md)
- [Player camera attach, projection FOV, and mesh `HFOV`](binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md)
- [Terrain shade plane — origin, ownership, and axis order](binary-analysis/terrain-shade-plane-origin-2026-07-26.md)
- [Terrain shade interpolation — the exact 8.8 fixed-point stepping, decoded from bytes](binary-analysis/terrain-shade-bilinear-decode-2026-07-26.md)
- [Terrain draw — texture-stage flags, and the falsification of both settings](binary-analysis/terrain-draw-stage-flags-2026-07-26.md)
- [Terrain gain — frame-global falsified, and the root-map oracle is circular](binary-analysis/terrain-gain-frame-global-falsified-2026-07-26.md)
- [Terrain per-node colour light — dead builder, and a null array in all 67 shipped heightfields](binary-analysis/terrain-per-node-colour-absent-2026-07-26.md)
- [Retail's implied macro cache, inverted from its own pixels — it exceeds the compositor's ceiling](binary-analysis/terrain-implied-macro-inversion-2026-07-26.md)
- [The sun colour and the terrain draw — all ten references, and a precise negative](binary-analysis/terrain-sun-colour-route-2026-07-26.md)
- [The terrain material record and the `LANDSCAPE_LIGHTING` gate — both loose ends are live](binary-analysis/terrain-ambient-light-material-2026-07-26.md)
- [The terrain ambient-light term, implemented and measured](binary-analysis/terrain-ambient-light-applied-2026-07-26.md)
- [The terrain third light — falsified; `SetupLights` dominates every terrain draw, and the three-light rig is a front-end page](binary-analysis/terrain-third-light-2026-07-26.md)
- [No missing high-frequency terrain term — the spectra match, and the frame is half a pixel out](binary-analysis/terrain-spatial-dispersion-negative-2026-07-26.md)
- [The default render-state block `0x004EB1E0` — re-derived from bytes; the API is D3D9, `COLORVERTEX` is `0x8D` not `60`, and the function has 7 callers not 547](binary-analysis/d3d-default-render-state-block-2026-07-27.md)
  — 2026-07-27. Promotes the static block that several committed rendering
  decisions rested on while living only in agent reports. Bounded to
  `[0x004EB1E0, 0x004EB99D)`. Corrects the "Direct3D 8" attribution, the 547
  figure (`440 + 50 + 57`, where the 57 are `SetTexture`; the render-state total
  is **490**), and the `COLORVERTEX` state id. Records which of the decisions
  have a runtime capture behind them — only *lighting-on* does.
- [The cockpit lighting law — decoded, and already what the reconstruction computes](binary-analysis/cockpit-lighting-law-2026-07-26.md)
- [The cockpit world matrix — the third upload site, traced by hand and confirmed at runtime](binary-analysis/cockpit-world-matrix-static-2026-07-26.md)
- [Controlled copied-runtime observations — four questions static reading could not settle](binary-analysis/controlled-runtime-observations-2026-07-26.md)
- [The terrain chain's temporal drift — the cloud scroll identified; its RATE partially superseded, origin since fixed and confirmed](binary-analysis/terrain-chain-temporal-drift-2026-07-26.md)
- [The half-pixel pixel-centre offset, corrected in the projection and measured](binary-analysis/pixel-centre-projection-offset-applied-2026-07-26.md)
- [View distance, cull, and LOD constants](binary-analysis/view-distance-and-lod-constants-2026-07-25.md)


- [2026-07-13 full Ghidra re-audit closeout](binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md)
- [Per-address reviewed correction plan](binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json)
- [2026-07 fullpass discovery findings](binary-analysis/ghidra-fullpass-findings/) (waves W001–W018)
- [Battle Engine movement crosswalk](binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md)
- [Battle Engine morph observer design](binary-analysis/battleengine-morph-runtime-observer-design-2026-07-12.md)
- [Pinned reference-submodule audit](source-code/reference-submodule-audit-2026-07-12.md)

The `6,411/6,411` closeout is a metadata/export accounting result, not a claim
that every function is semantically correct. Fullpass wave notes are discovery
evidence only; they do not claim complete semantic correctness of the database.
Current per-function notes live under
[`binary-analysis/functions/`](binary-analysis/functions/_index.md).

### 2026-07 fullpass correction expedition (authority map)

| Layer | Location | Role |
| --- | --- | --- |
| Discovery findings | [`binary-analysis/ghidra-fullpass-findings/`](binary-analysis/ghidra-fullpass-findings/) | Tracked wave reviews (W001–W018) |
| Correction ops | `local-lab/ghidra-fullpass-2026-07-23/` (gitignored) | Queues, dual QC, apply logs; closeout 2026-07-25 |
| Live applied DB | Maintainer Ghidra Projects (machine-local) | Working database that may receive dual-cleared applies |
| Tracked snapshot | [`ghidra/`](ghidra/README.md) (snapshot date 2026-07-18) | Distributable reviewed snapshot; may lag the live maintainer DB |

Host install paths, headless entry, and local project layout:
[`ghidra/README.md`](ghidra/README.md). Expedition overlays stay under ignored
`local-lab/`; do not treat discovery notes as proof that the tracked snapshot
or live DB was mutated.

## Patch recipes — analysis documents, not a mutation workflow

The closing line of this page says mutation of the installed game or original
`BEA.exe` is never an RE workflow. That line and this section do not conflict,
and the reconciliation is stated here rather than left to inference: **these are
analysis documents.** They record where a byte lives, which function owns it,
what the clean bytes are, and what was observed when an **app-owned copied**
executable carried the change. Every recipe below applies only to a verified
copied target — never the install, never the original, never
`BEA.exe.original.backup`. The closing line governs **workflows**; it does not
forbid documenting patch knowledge, and a front door that hid these notes would
not make the installed game any safer, only the evidence harder to find.

The normative authority for the byte definitions and for the copied-target
boundary is the [patch catalog contract](../patches/CATALOG_CONTRACT.md), with
[`patches/README.md`](../patches/README.md). The notes below explain why the
rows exist and what was actually observed; where a note and the catalog
disagree, the catalog wins.

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
| Destroyable segments | [destroyable-segments-static-contract.md](binary-analysis/destroyable-segments-static-contract.md) |
| Units, movement, weapons | [unit-battleengine-gameplay-static-contract.md](binary-analysis/unit-battleengine-gameplay-static-contract.md) |
| Local multiplayer | [local-multiplayer-static-runtime-contract.md](binary-analysis/local-multiplayer-static-runtime-contract.md) |
| Career progression bridge | [career-progression-static-bridge-contract.md](binary-analysis/career-progression-static-bridge-contract.md) |
| CMSH `CPOS`/`CORI` identity | [cmsh-cpos-cori-identity-2026-07-25.md](binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md) |

Machine-readable siblings, for consumers that should not be parsing prose:

- [MissionScript VM datatype/opcode schema](binary-analysis/missionscript-vm-datatype-opcode-schema.v1.json)
- [First-flight camera/movement/morph contract](binary-analysis/first-flight-camera-movement-morph-contract-candidate.v1.json)
  — a **candidate**, as its own filename says; not an accepted contract.
- [Retail specimen manifest](binary-analysis/retail-specimen-manifest-2026-03-14.json)
- [2026-07-27 function name table](binary-analysis/ghidra-function-name-table-2026-07-27.tsv)
  — the newer address-to-name authority.

The MissionScript **command-descriptor** schema that used to sit beside these
was deleted in `981c3379`; the 144-entry native registry it duplicated now lives
in [`../GHIDRA_FUNCTONS.md`](../GHIDRA_FUNCTONS.md). Most of the contracts above
have no `.json` sibling at all. Do not go looking for one.

## The 2026-05-26 static-review cohort — the oldest layer here

Six system slices from the May 2026 wave era, all dated `2026-05-26`. **This is
the oldest cohort in the store and the one most likely to mislead.** Read them
for subsystem shape, not for numbers: their prose carries live-database
accounting (`6113/6113`, `6411/6411`, wave and candidate counts) that was a
reading of the maintainer's database at the time. For what a function count can
mean today, use the
[RE coverage baseline](binary-analysis/re-coverage-baseline-2026-07-25.md); for
anything at function granularity,
[`binary-analysis/functions/`](binary-analysis/functions/_index.md) supersedes
these slices wherever a note exists.

The standing column below is read off `mapped-systems.md`'s owner table, not
asserted here — where that table still names the 05-26 document, so does this one.

| Slice | Standing |
| --- | --- |
| [Save and options](binary-analysis/save-options-static-review-2026-05-26.md) | **Still current.** The cited owner for options and control bindings, and the contract behind the save/options persistence chains. |
| [Audio, media, cutscene](binary-analysis/audio-media-cutscene-static-review-2026-05-26.md) | **Still the cited owner** for audio, media, cutscenes, and camera. The wave counts inside it are snapshots. |
| [Frontend, input, game loop](binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md) | Superseded for frontend/HUD by [hud-frontend-overlay-static-contract.md](binary-analysis/hud-frontend-overlay-static-contract.md). Its companion proof-plan file no longer exists in the tree; the 2026-07-28 correction inside it gives the `git show` needed to recover it. |
| [Unit / BattleEngine gameplay](binary-analysis/unit-battleengine-gameplay-static-review-2026-05-26.md) | Superseded by [unit-battleengine-gameplay-static-contract.md](binary-analysis/unit-battleengine-gameplay-static-contract.md) (2026-07-16). |
| [Mesh, motion, world, particle](binary-analysis/mesh-motion-world-particle-static-review-2026-05-26.md) | Superseded for meshes and resources by [mesh-resource-render-static-contract.md](binary-analysis/mesh-resource-render-static-contract.md) and [render-resource-bridge-static-contract.md](binary-analysis/render-resource-bridge-static-contract.md). |
| [Texture and render](binary-analysis/texture-render-static-review-2026-05-26.md) | Superseded for decode by [texture-resource-decode-static-contract.md](binary-analysis/texture-resource-decode-static-contract.md), and for render state by the 2026-07 terrain and D3D notes above. |

## Operating the lane — reference, routing, and runbooks

| Document | Use it for |
| --- | --- |
| [Ghidra workflow reference](binary-analysis/GHIDRA-REFERENCE.md) | The active workflow for the Steam `BEA.exe` database: record specimen and database identity, export the smallest slice that answers the question, keep observed bytes separate from inferred names. The reviewed snapshot under `ghidra/` and narrow metadata projections are the tracked exceptions; the maintainer's loaded database is not. |
| [Mapped systems](binary-analysis/mapped-systems.md) | The routing table from a system to its current smallest evidence owner *and* to the code that consumes it. Start here when you know the subsystem but not the document. Not a function-completion ledger. |
| [High-impact call chains](binary-analysis/high-impact-call-chain-appendix.md) | Static chains with the product consequence spelled out — that loading a retail save can rewrite the boot-time options snapshot, that resume/exit can persist both career and `defaultoptions.bea`. This is the appendix explaining *why* AppCore patches real baselines and preserves unknown bytes instead of synthesizing saves. |
| [Executable analysis](binary-analysis/executable-analysis.md) | PE identity, hashes, size, DLL imports, the D3D9 confirmation, and the Lost Toys/Encore branding note. Its function-count row now carries the whole moving chain — 5,771 → 6,411 → **6,969** — and says plainly that this is a recovery count, not a property of the binary. |
| [WinDbg/CDB runbook](binary-analysis/windbg-cdb-runbook.md) | The only sanctioned debugger workflow: a copied `BEA.exe` from an app-owned profile, specimen hashes confirmed first, attach by exact PID and identity, command files deliberately untracked. Never the installed directory. |

## Retail → Core translation policies

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

Reusable read-only Ghidra exporters, guarded asset tools, parsers, and copied-
runtime helpers live under [`tools/`](../tools/README.md). Mutation of the
installed game or original `BEA.exe` is never an RE workflow.
