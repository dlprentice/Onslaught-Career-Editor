# Onslaught Toolkit player value, UX, mods, and patch audit

Status: candid read-only product audit
Date: 2026-07-13
Scope: current WinUI 3 player product, AppCore-backed workflows, patch and safe-copy profile catalogs, packaged Lore posture, and public player signals
Branch: `codex/player-value-ux-patch-quality`

## Executive verdict

Onslaught Toolkit's strongest product feature is not its patch count. It is the
copy-first safety model: the installed game remains read-only, the app creates a
playable copy, verifies exact executable bytes, records what changed, and can
restore from a verified full-file backup.

The main product defect is curation. The few jobs with broad player value—make
the old game run in a window, inspect or edit a copied save, browse its media,
and distinguish a modded copy—share nearly equal prominence with incomplete
camera experiments, proof-artifact loaders, contributor asset packaging, raw
music staging, and BEA.exe-only diagnostics. The result is evidence-rich but
decision-heavy. It can make a strong safety engine feel risky.

The clearest misleading surface is **Enhanced Profile Preview**. It combines
the compatibility base, legacy graphics flags with no proven visible benefit,
a title marker, an arbitrary red frontend color, a bounded Goodies display
override, and copied controller/sensitivity defaults whose runtime feel is
explicitly unproven. The name implies a coherent upgrade that the evidence does
not establish.

The safest first product change is curation without binary changes: make the
normal path a stable compatibility-and-recovery workflow, retain existing
experiments as explicitly labeled legacy/research recipes in a proof-stratified
Lab, and stop presenting Enhanced and Debug Camera as peer player outcomes.

## Evidence and limits

This audit used:

- native WinUI inspection of all eight top-level pages on the current Debug
  build;
- XAML and code-behind control/handler inventory;
- AppCore, UI test, patch catalog, safe-copy profile, patch contract, and
  current-capability inspection;
- one independent Codex normal review and one independent Codex adversarial
  review;
- serial sanitized Cursor/Grok normal and adversarial consultations using
  `cursor-grok-4.5-high-fast`; and
- bounded public research.

Public research provides demand signals, not popularity estimates:

- A Steam developer post documents a commonly encountered right-stick problem
  and recommends a Steam Input mouse-aim configuration plus manual in-game
  binding and sensitivity setup: [Gamepad Optimization
  Tips](https://steamcommunity.com/app/1346400/discussions/0/2942494909163878759/).
- A public Steam thread gives a manual replacement-file workflow for widescreen
  resolutions: [Widescreen
  patch](https://steamcommunity.com/app/1346400/discussions/0/3033725780707286842/).
- A 42-comment Steam thread discusses the difficult last Goodie and requests a
  100% save: [100%
  Goodies](https://steamcommunity.com/app/1346400/discussions/0/5064850575736632552/).
- A small four-comment thread asks for a remaster with graphics, online/co-op,
  maps, and larger battles: [Remastered
  Edition?](https://steamcommunity.com/app/1346400/discussions/0/591768952135255488/).
- PCGamingWiki separately records right-stick, pause/cutscene, and controller
  menu limitations: [Battle Engine
  Aquila](https://www.pcgamingwiki.com/wiki/Battle_Engine_Aquila).

No usage analytics, survey, interview, support-ticket corpus, or statistically
representative player sample was available. Persona scores and opportunity
rankings remain product judgments constrained by the evidence above.

## Persona-by-capability matrix

| Persona | Jobs to be done | Current high-value capabilities | Would they want it? | Understand and trust it? | Main gap |
| --- | --- | --- | --- | --- | --- |
| First-time nontechnical user | Point the app at the game; make a safe copy; make one understandable change; know the original is safe | Home setup states, Compatibility Copy, guarded save/options outputs, safe-copy receipt | Yes, if the first path stays short | Home and safety language are strong; Windowed & Mods quickly exceeds a normal user's decision budget | Too many equal-looking presets, rows, experiments, and technical concepts; no single guided save journey |
| Casual returning player | Make the Steam release behave on a modern desktop; recover old saves; use a controller; revisit media | Windowed compatibility pair, Save Lab, Media, local split-screen preset | Strong observed need for display/controller help | Compatibility wording is mostly honest; graphics and Enhanced names imply more benefit than proven | Controller guidance and widescreen clarity matter more than debug-camera rows or proof loaders |
| Die-hard fan / preservationist | Inspect completion state, Goodies, mission media, story material, and retail data | Save Analyzer/Editor, Goodies preview/state, 629 audio and 66 video rows, curated Lore reading order | Yes | Copy-first save safety and in-app Lore/Media are credible | Goodies, saves, Lore, and media are siloed; no completion-oriented journey or cross-links |
| Patch/mod user | Choose a useful outcome, apply reversibly, distinguish the copy, recover from failure | Exact specimen/byte verification, dependencies/conflicts, backup/restore, PATCHED marker | Yes | Engineering is unusually trustworthy; catalog presentation is not curated by outcome | Twenty visible patch rows include eleven experiments; evidence existence is mistaken for user value |
| Technical researcher/modder | Inspect row semantics, try bounded experiments, load proof summaries, use executable-only copies | Per-row evidence, Custom selection, online status loaders, launch flags, BEA.exe-only diagnostics | Yes | Strong when presented as research | Research tools compete with the player journey instead of living in a clearly scoped Lab |
| Lore reader | Discover characters, factions, missions, studio history, and preservation work | Searchable offline reader, history controls, curated book sections, browser-labeled external links | Yes | The visible book is coherent and readable | The 949-document package breadth is not proof of editorial completeness, freshness, rights review, or uniform quality |

## Page and control action/reaction map

### Shell

| Control | Prerequisite | Reaction | Failure/safety behavior | First-time comprehension |
| --- | --- | --- | --- | --- |
| Home, Save Lab, Media, Asset Library, Lore, Windowed & Mods, Settings, About tabs | None | Navigates to a cached page and moves focus according to navigation origin | Stale queued focus work is invalidated; inactive pages do not own status | Labels are clear; eight peer destinations overstate the normal-user relevance of Asset Library and research-heavy Mods |
| Review Setup | None | Opens Settings and targets setup | Does not modify the install | Clear, but it remains visible after a valid install and competes with normal tasks |
| Bottom status and game summary | Page activity | Shows current page state and redacted game identity | Full paths stay out of the shell summary | Useful trust cue |

### Home

| Control | Reaction and next state | Prerequisites/failure | Assessment |
| --- | --- | --- | --- |
| Choose game folder / Review Settings | Opens Settings | Setup action changes with unset, invalid, or ready game-folder state; manual Save Lab remains available without setup | Strong first-run behavior |
| Open Save Lab | Opens Save Lab | None | High value |
| Game Options | Opens Save Lab at Game Options | None | Useful deep link |
| Open Media | Opens Media | Valid install required for discovered content | High player value once configured |
| Open Lore | Opens Lore | Packaged or repo Lore source must load | High preservation value |
| Open Windowed & Mods | Opens copied-game workflow | Valid install required to create a playable copy | High value, but destination is too dense |
| Open Asset Library | Opens generated-catalog browser | Requires an externally generated catalog | Equal Home prominence is not justified for a first-time user |
| Open About | Opens product boundaries/version | None | Low-frequency but harmless |

### Save Lab

The page duplicates a three-step task guide and a three-tab strip. The guide is
helpful on first entry but repeats navigation thereafter.

| Area/control | Reaction | Prerequisite and success state | Failure/safety behavior |
| --- | --- | --- | --- |
| Analyze a save / Open save editor / Open Game Options | Selects the matching Save Lab tab | None | Navigation only |
| Save Analyzer: detected-file list, Refresh, input path, Browse, Analyze/Reload | Selects or opens a `.bes`/`.bea`, decodes it, and populates summary/report | Valid retail-shaped input | Read-only; invalid/unreadable files report status |
| Verbose output / Advanced byte details | Re-renders the current analysis with more detail | Loaded analysis | No write |
| Compare path, Browse, Compare files | Produces a byte/field comparison | Two compatible readable files | No write; incompatible inputs fail visibly |
| Summary tree, Copy report, Clear | Navigates result, copies text, or resets analyzer state | Analysis for copy | Copy affects clipboard only |
| Save Editor detected saves/Refresh/input/output/Browse | Chooses source and separate output | `.bes` input and safe output path | Default output is app-owned; in-place, alias, install-tree, device/network, ADS, reparse, and unsafe destinations are rejected |
| Patch preset, mission rank baseline, Mark goodies as NEW, patch missions/links/goodies/kills, kills-only | Changes the in-memory patch plan and visible summary | Valid input for a complete plan | Unknown bytes, file size, kill metadata, and unselected regions remain preserved |
| Per-mission rank overrides and per-category kill Write controls | Adds granular overrides | Corresponding section enabled | No file write until final action |
| Write patched save copy | Atomically writes and verifies the separate `.bes` output | Valid source, plan, and safe destination | Staged/committed identity and byte verification; installed source remains unchanged |
| Copy output | Copies the output path/text | Successful write | Does not move game files |
| Game Options detected files/Refresh/input/output/Browse | Chooses a `defaultoptions.bea`-shaped source and separate output | Valid 10,004-byte options buffer | Same guarded writer boundary as Save Editor |
| Sound/music override toggles and values | Enables and sets copied output audio values | Valid input | No write until final action |
| Invert walker/flight, vibration, controller config P1/P2 | Changes planned copied options fields | Valid selections/ranges | No runtime control-feel claim |
| Copy source, copy options entries/tail, load input/source keybinds, clear | Plans exact block/keybind transfer from another valid buffer | Compatible source | Preserves nonselected bytes and rejects incompatible shape |
| Per-binding P1/P2 overrides | Changes planned binding rows | Loaded binding table | Range/shape validation before write |
| Write options copy / Copy output | Atomically writes verified separate `.bea` output / copies result path | Valid source and plan | Installed/default source remains read-only |

### Media

| Control | Reaction | Prerequisite/failure | Assessment |
| --- | --- | --- | --- |
| Audio Library / Video Player | Switches tab; video runtime initializes only on demand | Valid install for content | Good preservation UX; avoids unnecessary VLC startup |
| Search and content tree | Filters/selects music, voices, videos, cutscenes, or briefings | Loaded catalog | Empty/loading/errors stay visible |
| Play, Pause, Stop, seek, volume | Controls selected inline media | Readable selected item and player availability | Player errors surface; source remains read-only |
| Show in Explorer | Reveals selected video | Selected readable file | Shell action only; label is clear |
| Browse Game Directory / Reload Library | Changes configured source or rescans | User-picked install | Duplicated across tabs; invalid folder is reported |
| Source folder / Path details | Reveals location details | Loaded source | Details are appropriately secondary |

### Asset Library

| Control | Reaction | Prerequisite/failure | Assessment |
| --- | --- | --- | --- |
| Change catalog, path input, Browse export folder, Load catalog | Loads a guarded generated `asset_catalog/catalog.json` | User must first run an external extraction/catalog workflow | Honest failure state, but no actionable in-app route to create the required catalog |
| Textures, Meshes, Embedded, Goodies tabs; search; Goodies filters | Filters the loaded catalog | Valid generated catalog | Valuable to preservationists, opaque to normal users |
| Copied `.bes` Goodies state Browse/Load/Clear | Adds display state to Goodies rows | Valid copied save | Read-only state load |
| Asset list and Front/Side/Top/Iso views | Selects and changes preview orientation | Previewable catalog row | No retail write |
| Neutral/Light/Dark texture background | Changes preview background | Texture selected | Presentation only |
| Open export, Open in Media, Copy path, View linked texture | Opens/copies the generated export or cross-links to supported content | Selected row with corresponding target | Clear local actions |
| Write local package, Open package, Copy package path | Materializes or exposes an app-owned material package | Valid model/catalog and guarded output | Contributor/rebuild tooling; disproportionate complexity for a default player page |

### Lore

| Control | Reaction | Prerequisite/failure | Assessment |
| --- | --- | --- | --- |
| Search documents | Filters included titles and content | Loaded library | Clear |
| Refresh | Reloads library source | Packaged/repo source available | Reports unavailable/loading state |
| Document tree | Opens included chapter in reader | Selected included document | Included content remains in app |
| Back / Forward / Home | Navigates reader history or curated entry point | History availability | Disabled appropriately |
| Hide/Show Library | Toggles left navigation | None | Useful reading mode |
| Open in browser | Opens only source/external target | Selected external-capable link | Browser action is explicitly labeled |

### Windowed & Mods

The first viewport gives a good four-step player model, but the full page
contains more than fifty interactive controls/settings. Required compatibility
rows are shown as ordinary checked boxes even though safe-copy creation adds the
pair regardless. That is a mental-model mismatch.

| Area/control | Reaction | Prerequisite/success | Failure/safety behavior |
| --- | --- | --- | --- |
| Use configured folder / Browse source | Selects read-only game source | Valid supported Steam specimen or clean backup path | Installed source remains read-only; mismatch is reported |
| Compatibility Copy, Windowed + Graphics Defaults, Enhanced Profile Preview, Graphics flag rows only, Debug Camera Preview, Clear optional mods | Replaces visible row selection and some copied-options defaults | Loaded valid catalogs | Names imply unequal evidence; Enhanced and Debug are not coherent player outcomes |
| Preset details and limits | Shows modules, evidence summary, restore strategy, and nonclaims | Selected profile | Good technical trust surface |
| Red/green/black/clear margins | Chooses one mutually exclusive frontend clear color | Custom/copy selection | UI proactively clears conflicts; cosmetic value is low |
| Add/Clear PATCHED marker | Adds/removes pointer row and hidden cave dependency | Supported specimen | One bounded title/menu proof; not every gameplay overlay path |
| Add/Clear Goodies preview | Adds/removes the copied-executable display-flag override | Supported specimen | Does not edit or permanently award the save; the effect persists in that safe copy until restored/recreated |
| Twenty dynamic patch checkboxes and Details expanders | Selects a row and shows bounded proof/limits | Catalog row visible and conflict-valid | Eleven visible experiments and eight Q-remap variants overwhelm normal users; hidden companions correctly expand |
| Copy savegames into safe copy | Includes source save folder in copied profile | Valid source | Source remains read-only; explicit opt-in |
| Music swap during creation | Stages one named copied-track swap | Available source tracks | Writes copied files only; audible runtime proof remains unaccepted |
| Create safe copy | Copies game, applies required compatibility and selected rows, verifies bytes, writes manifest/receipt | Valid source, selection, destination, and copied-options/music plan | App-owned root; fail-closed validation; installed game untouched |
| Safe copy receipt / launch plan preview | Discloses selected rows, dependencies, launch modifiers, copied files, restore/nonclaims | Prepared copy | Paths are redacted from primary summary |
| Launch safe game copy / Stop copied game | Revalidates and launches the registered copy / stops only the managed process | Prepared valid manifest and process state | Stop confirmation before force-close; no installed-game process mutation |
| Quiet capture / High detail test / Clear launch options | Sets/clears named argument combinations | Prepared or planned copy | Does not prove gameplay benefit |
| Skip intro, mute music, mute sound, high detail, no static shadows, no rumble, debug trace | Adds allowlisted launch arguments | Valid combination | Invalid or blocked flags never enter launch plan |
| Level ID / Admin Level / Local split-screen test | Sets bounded `-level`; preset selects known IDs; local test selects level 850 and split configuration | Numeric validation | Not a level browser, unlock, online, or gameplay-outcome proof |
| Online technical details / summary loaders | Reveals passive readiness claims and loads redacted topology/readiness/controller artifacts | Explicit technical toggles and valid sanitized files | Cannot enable Host/Join; belongs in research Lab |
| Controller configuration, persistence, sensitivity, invert settings, five control presets, texture RAM | Plans launch or copied-options changes | Valid ranges and available copied options | Read-back is not improved control-feel proof; public evidence says controller help matters, but these experiments do not solve it reliably |
| Three named copied-track swaps, arbitrary target/replacement, stage/restore | Writes or restores a copied music file | Prepared safe copy and valid OGG/source | Audible in-game playback remains unproven; names are not discoverable player metadata |
| Advanced BEA.exe-only source/copy, Create, Verify, Apply, Restore, operation log | Creates and mutates only a technical executable copy | Explicit advanced disclosure and safe app-owned target | Not a playable folder; should not compete with player workflow |

### Settings and About

| Control | Reaction | Prerequisite/failure | Assessment |
| --- | --- | --- | --- |
| Browse / Auto-Detect game directory | Sets the read-only source and updates all dependent pages | Full install shape | Clear valid/needs-review states; path details remain secondary |
| Path details | Reveals configured path | Configured path | Appropriate disclosure |
| Background audio/video and prevent overlap toggles | Save media behavior immediately | None | Plain and useful |
| Reload Saved Settings | Reloads persisted config | Existing config | Ambiguous after “changes save immediately”; sounds like undo |
| Settings file details | Reveals local config path/details | None | Technical but secondary |
| About | Shows capabilities, project boundaries, retail-authority notes, and version | None | Truthful, but repeats safety copy found elsewhere |

## Full patch and mod usefulness audit

Catalog accounting: 29 rows; 20 visible options; 9 hidden companions; 9 stable
visible rows; 11 experimental visible rows.

| Row(s) | Audience/value | Strongest proof | Risk and dependency | Recommendation |
| --- | --- | --- | --- | --- |
| `resolution_gate` + `force_windowed` | High; first-time and returning players | Exact bytes, static semantics, bounded copied-launch pair | Must be used as one compatibility base; no FOV/aspect or all-machine guarantee | Keep as locked, explicit safe-copy base; stop presenting as optional peer checkboxes |
| `extra_graphics_default_on` + `ignore_cardid_tweak_overrides` | Low-medium; legacy GPU troubleshooting | Exact bytes and copied launch | No proven visible graphics improvement/correctness | Combine and move to Advanced as “legacy GPU-rule bypass trial”; remove recommended/enhanced implication |
| `version_overlay_use_patched_format_pointer` + hidden `version_overlay_patched_format_cave_string` | Medium; mod-copy identity and trust | One copied title/menu `V1.00 - PATCHED` observation | Hidden cave required; not every overlay/gameplay path | Keep as an optional identity marker, with exact semantics and restore behavior visible |
| `frontend_clear_screen_dark_red`, `_dark_green`, `_black` | Low; cosmetic novelty and screenshot users | Exact bytes, title-screen proof, one navigated Goodies-menu color-family proof | Mutually exclusive; no whole-menu/HUD/gameplay theme | Keep as one compact Advanced cosmetic selector; remove arbitrary red from Enhanced |
| `goodies_gallery_display_unlock` | Medium for completionists/preservationists; low casual value | Two wall-state comparisons and one Tatiana presentation page | Copied-executable display state only; no save award, FMV/model, or every-entry proof | Keep as “Goodies wall preview (does not unlock your save)” in Mods/Lab; do not call it a 100% save |
| `skip_auto_toggle` | Low, niche fallback | Exact bytes/static startup-path interpretation | Runtime benefit varies; windowed pair required | Reveal only under windowed-startup troubleshooting after normal compatibility fails |
| `pause_o_scan_initializer_experiment` | Low current product readiness | Exact-PID CDB ordered O/pause evidence; one level-100 menu-open/Enter-resume observation | No broad pause/menu, second-O, collision, feel, or long-session proof | Research-only until normal gameplay usability and escape behavior are proven |
| `free_camera_aurore_gate_bypass` | Medium researcher/screenshot potential; low casual readiness | Exact bytes and bounded F toggle/camera-pointer proof | Requires reachable debug input; no coherent controls or safety proof | Keep as Lab gate, not a standalone player mod |
| `free_camera_keyboard_forward_q_hook` + hidden `_forward_q_cave` | Low as a product; research-only | Q reaches hook/cave and produces bounded position deltas | Depends on gate; conflicts with all seven variants; repurposes one Q-bound action | Keep as named legacy/research recipe; do not render as peer normal row |
| `free_camera_keyboard_backward_q_hook` + hidden `_backward_q_cave` | Same | Bounded backward position deltas | Same mutual-exclusion/control-scheme limits | Research-only |
| `free_camera_keyboard_strafe_left_q_hook` + hidden `_strafe_left_q_cave` | Same | Bounded left position deltas | Same | Research-only |
| `free_camera_keyboard_strafe_right_q_hook` + hidden `_strafe_right_q_cave` | Same | Bounded right position deltas | Same | Research-only |
| `free_camera_keyboard_yaw_left_q_hook` + hidden `_yaw_left_q_cave` | Same | Bounded left orientation deltas | Same | Research-only |
| `free_camera_keyboard_yaw_right_q_hook` + hidden `_yaw_right_q_cave` | Same | Bounded right orientation deltas | Same | Research-only |
| `free_camera_keyboard_pitch_up_q_hook` + hidden `_pitch_up_q_cave` | Same | Bounded up orientation deltas | Same | Research-only |
| `free_camera_keyboard_pitch_down_q_hook` + hidden `_pitch_down_q_cave` | Same | Bounded down orientation deltas | Same | Research-only |

### Safe-copy profile audit

| Profile | Value/proof judgment | Recommendation |
| --- | --- | --- |
| Compatibility Copy | Best value/risk ratio and truthful scope | Keep as the normal default; define the exact pair as versioned base behavior |
| Windowed + Graphics Defaults | Compatibility is useful; “Graphics Defaults” implies benefit not visually proven | Rename and move legacy GPU flags to Advanced troubleshooting |
| Enhanced Profile Preview | Arbitrary showcase presented as enhancement; unproven graphics/control benefit | Stop presenting as a normal outcome; retain temporarily as a labeled legacy Lab recipe so existing users can find it |
| Debug Camera Preview | Only a toggle plus Q-forward; not a usable free-camera scheme | Retain as a labeled legacy research recipe; do not present as player-ready preview |
| Custom | Valuable to technical modders | Advanced/Lab only |
| Music swaps and arbitrary OGG staging | High fan-value hypothesis, but no accepted audible-output proof and poor track-name discovery | Advanced experiment until track metadata/audition and in-game audible proof exist |
| Local split-screen preset | Real current action with bounded launch-plan truth | Keep near the normal safe-copy flow; continue to state it is not online play |

## Top pain points and misleading surfaces

1. **Enhanced Profile Preview overpromises.** It is not an enhanced edition or
   evidence-backed improvement bundle.
2. **Windowed & Mods is one page with several products inside it.** Normal play,
   patch research, controller experiments, music staging, online research, and
   executable diagnostics share one scroll.
3. **Required compatibility looks optional.** Users can see ordinary checked
   boxes even though creation injects the pair.
4. **Visible experiment count exceeds useful outcome count.** Eight one-key
   camera remaps are research evidence, not eight useful mods.
5. **Controller demand is observed, but the product does not solve it.** Copied
   defaults and one-byte/Q experiments are not a trusted modern-controller
   onboarding flow.
6. **Asset Library first-run is a dead end.** It says to generate a catalog
   outside the app but provides no direct, actionable creation route.
7. **Save Lab navigation is duplicated.** Task cards and tabs repeat the same
   three destinations; the current tab persists even when a user expects a
   fresh starting point.
8. **Safety wording is repeated so often that hierarchy weakens.** The boundary
   is important, but repetition pushes the actual task below the fold.
9. **Music swap labels expose filenames, not player meaning.** There is no
   audition/context layer and no accepted audible in-game output proof.
10. **Lore/package breadth can be confused with editorial completion.** The
    visible curated book is good; the 949-document package number must remain a
    packaging fact, not an editorial-quality claim.

## Ranked top 10 opportunities

Scores use 1 (low) to 5 (high). For effort and risk, lower is better.

| Rank | Opportunity | Value | Evidence | Effort | Risk | Dependency | Why now |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Split normal safe-copy workflow from a proof-stratified Lab; keep Compatibility exact and visible | 5 | 5 | 3 | 2 | 2 | Reduces the largest comprehension/trust defect without changing bytes |
| 2 | Demote/recompose Enhanced and Debug Camera; preserve them as labeled legacy Lab recipes | 5 | 5 | 2 | 2 | 1 | Removes direct overclaim while avoiding a silent recipe disappearance |
| 3 | Add player-facing controller setup guidance grounded in the Steam developer workaround; do not imply current experiments fix right-stick behavior | 5 | 4 | 2 | 1 | 1 | Addresses an observed recurring friction with low implementation risk |
| 4 | Make required compatibility a locked base module and continuously validate optional selection before Create | 5 | 5 | 3 | 3 | 2 | Aligns UI with actual plan-builder behavior and prevents selection surprise |
| 5 | Add an actionable Asset Library first-run route (“how to create a catalog” or an app-owned generator when legally/technically ready) | 4 | 5 | 2 for guidance / 5 for generator | 2 / 4 | 2 / 5 | Current first run has no usable next action |
| 6 | Add a guided common save journey: source → copied output → one edit → write → where to use it | 5 | 4 | 4 | 3 | 2 | Converts a powerful editor into a first-time task |
| 7 | Add completion-oriented Goodies cross-links among copied save state, gallery preview, media, and Lore | 4 | 3 | 4 | 3 | 3 | Public discussion shows some persistent completion interest |
| 8 | Prove and present modern display outcomes beyond enumeration/window preference (FOV/aspect/UI A/B) before stronger widescreen language | 5 | 4 | 5 | 4 | 5 | Widescreen demand is observed; current proof is narrower than player expectation |
| 9 | Replace raw music filenames with track metadata/audition and obtain accepted copied-runtime audible proof | 3 | 2 | 4 | 3 | 4 | Potential fan value, currently technical and unproven |
| 10 | Strengthen distribution trust/onboarding for the unsigned portable ZIP without making a release in this lane | 4 | 5 | 4 | 3 | 4 | First-time users face an unsigned archive and manual extraction/launch |

## Recommended bounded implementation slices

### Slice 1 — truthful profile curation (recommended first)

- Stop presenting Enhanced Profile Preview and Debug Camera Preview as normal
  peer outcomes.
- Keep both discoverable as explicitly labeled legacy/research Lab recipes; do
  not silently delete existing catalog IDs.
- Rename/de-emphasize the graphics pair as legacy GPU-rule troubleshooting.
- Remove Enhanced's automatic copied controller/sensitivity defaults, or make
  the recipe name/status explicitly say that it changes copied controls without
  proven feel improvement.
- Do not change executable bytes.

Acceptance: failing catalog/profile and WinUI copy tests first; focused AppCore
profile/catalog parity; patch safety; native UIA selected-state checks; native
visual inspection at normal and narrow widths.

### Slice 2 — normal versus Lab information architecture

- Normal: exact Compatibility base, game source, create/receipt/launch/stop,
  local split-screen preset, and explicit backup/restore/copy boundary.
- Player Mods: PATCHED identity marker and clearly non-save-awarding Goodies wall
  preview may be offered as optional mods, but not preselected and not described
  as the compatibility base.
- Lab: legacy graphics flags, colors, fullscreen fallback, pause, camera rows,
  music experiments, Custom, online research loaders, and BEA.exe-only tooling.
- Lab must be grouped by proof class and outcome; it must not be the current flat
  page moved behind one click.
- Preserve recipe discoverability and make old names/statuses explain where they
  moved.

Acceptance: native UIA proves normal cannot reach experimental music/online/
custom/diagnostic controls until Lab is explicitly opened; every former control
is either reachable in its new group or deliberately retired with a reason.

### Slice 3 — controller onboarding, not controller overclaim

- Add an in-app controller help surface based on the official Steam developer
  guidance: Steam Input mouse-aim workaround, in-game binding, sensitivity, and
  P1/P2 distinction.
- Link out clearly when opening Steam/community guidance.
- Keep copied configuration experiments separate and explicitly unproven for
  right-stick compatibility or feel.

Acceptance: copy/link tests, native keyboard/UIA navigation, and no claim that
the Toolkit patches or fixes every controller.

## Product-direction question requiring user taste

How narrow should the default normal-player mod surface be?

1. **Compatibility and recovery only (safest):** PATCHED marker and Goodies wall
   preview remain in Lab/Mods.
2. **Compatibility plus two proven optional mods (recommended balance):** keep
   the marker and explicitly non-save-awarding Goodies preview visible but
   unselected; all experiments remain in Lab.

This choice affects product personality: option 1 feels like a compatibility
utility; option 2 feels like a small preservation/mod toolkit. It does not
change patch bytes or the installed-game boundary.

## Exact nonclaims and evidence gaps

- No popularity, market-size, retention, or conversion claim is supported.
- No widescreen FOV, aspect-ratio, HUD, or all-machine windowing parity is
  proven.
- No visible graphics improvement or broad GPU/driver compatibility is proven
  for the graphics-default rows.
- No complete free-camera control scheme, control feel, joystick/analog
  coverage, pause/menu safety, gameplay safety, or long-session safety is
  proven.
- No Toolkit patch currently fixes the publicly documented modern-controller
  right-stick problem.
- No accepted audible in-game output proof exists for staged music replacement.
- Goodies display preview does not edit a save, permanently award Goodies, prove
  every entry, or provide a 100% save.
- The PATCHED marker is proven only in one bounded title/menu path; it is not a
  universal gameplay overlay or proof that every possible modification is
  active.
- Local split-screen is not Host/Join, distinct-endpoint online play, public
  matchmaking, or native BEA netcode.
- Lore pack breadth does not prove narrative completeness, editorial review,
  freshness, rights/provenance review, or uniform public safety.
- Asset Library does not generate retail catalogs in the app and does not grant
  redistribution rights for extracted assets.
- The current release remains an unsigned portable ZIP; installer-grade trust
  is unproven.
- No release, installed-game mutation, live runtime/Ghidra action, or new binary
  patch was performed for this audit.

## Baseline and review record

- `dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj
  --nologo`: passed, 0 warnings, 0 errors.
- `npm test`: stopped before product build/tests because the untouched baseline
  has pre-existing docsync drift in
  `reverse-engineering/binary-analysis/battleengine-morph-runtime-observer-design-2026-07-12.md`.
  This lane did not modify the primary-owned morph-canary document or mirror.
- Native inspection covered Home, Save Lab, Media loaded state, Asset Library
  empty/generated-catalog state, Lore loaded Start Here state, Windowed & Mods
  first and mid-scroll states, Settings, and About. The inspection app was
  closed afterward.
- Codex normal review: complete; recommended profile curation and a player/Lab
  split.
- Codex adversarial review: complete; found Enhanced overclaim, optional-looking
  required compatibility, profile-state mismatch risk, and flat-Lab risk.
- Cursor/Grok normal (`cursor-grok-4.5-high-fast`): complete; approved the
  direction with controller and widescreen clarity prioritized.
- Cursor/Grok adversarial (`cursor-grok-4.5-high-fast`): complete; required
  exact base/marker semantics, retained legacy recipe discoverability, and a
  proof-stratified Lab. Its objection to calling Goodies “nonpersistent” is
  resolved by using the precise claim: the row changes only the copied
  executable display path, does not edit or permanently award the save, and
  remains active in that safe copy until restore/recreation.

## State disposition

This coordinated worker did not edit `goal.md`, `developer_agent_state.json`,
or `documentation_agent_state.json`. Integration should update the canonical
state with: player-value audit complete; strongest opportunity is normal/Lab
curation; Enhanced/Debug should be demoted without deleting IDs; controller
guidance is the strongest low-risk observed-demand follow-up; baseline `npm
test` remains blocked by primary-owned morph-observer docsync drift.

## First implementation slice disposition

Primary selected option 2 on 2026-07-13. The first bounded slice now implements
that decision without changing the profile catalog, patch keys, or executable
bytes:

- Normal Windowed & Mods states the exact two-row compatibility base, recovery
  by recreating the safe copy, and two initially unselected player mods.
- PATCHED identity marker and Goodies wall preview remain opt-in and expose an
  exact live selected-state summary. Goodies copy retains the save, persistence,
  every-entry, and model/FMV nonclaims.
- A collapsed Lab separates retained legacy/research recipes, visual and
  executable experiments, and launch/control diagnostics. Existing recipe IDs
  and automation IDs remain discoverable.
- Normal/adversarial review findings were absorbed: semantic Lab headings,
  truthful assistive labels, complete two-by-two recipe/action grids, native
  collapsed/expanded state proof, and evidence-bounded “required lowest-change
  base” wording.

Fresh acceptance evidence: the full WinUI primary lane passed (1,319 AppCore
tests; 142 UI tests passed and two private-input visual tests skipped), the
focused native UIA smoke passed, and the copied-profile preflight passed. The
patch-engine safety command passed its .NET and legacy-script stages but its
accounting stage cannot run in this worktree because the intentionally
uninitialized `references/Onslaught` submodule omits `DXFrontend.cpp`; no
catalog or submodule change belongs to this slice.
