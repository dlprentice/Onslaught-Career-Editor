# Execution Program

Status: durable backlog under David's 2026-10-15 direction
Last updated: 2026-11-05 (the 0.2 hold and the standing 0.1.x authorization point to GOAL.md; every Companion capability named in the migration; the repository rename and a second history flatten held; status wording corrections)
Summary: the open work, its acceptance gates, and what was closed or paused, without an execution diary.

The [goal](GOAL.md) sets the direction. Toolkit capability claims belong in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) and its checks in [VALIDATION.md](VALIDATION.md); CE and the Godot
rebuild own their own release and parity evidence. The queue that
ran the Ghidra campaign, the decompilation plan and the rebuild's work items until 2026-10-15 is in the private
pre-flatten history (before the public root commit of 2026-10-15); the campaign's records are in the private historical
maintainer archive.

## Cross-project progress and priorities

This is the single cross-project chart. Multiplayer engineering status was updated **2026-11-04**; the public
contributor routes were rechecked **2026-11-02**. Older measurements retain their dates in the linked owners. Verify the owner and current release
before relying on a row.
A development branch is not a released feature. Update the affected row at a
material milestone rather than keeping a second live dashboard in a continuity note. The [goal](GOAL.md#how-progress-is-measured)
defines progress and what a completion claim requires.

| Area | Current state and remaining outcome | Detailed owner |
| --- | --- | --- |
| CE release and player experience | Latest public release: 0.1.13 (published 2026-10-31). Its release notes describe shipped changes, checks and limits; physical Windows retesting remains open. The unreleased 0.1.99 r1 and r2 checkpoints are preserved. r2 passed a Linux build, a Windows cross-target build (no Windows run) and package-content checks, a Linux main-menu render and local edited-project smoke, bounded Companion workflow checks and reviewed manual-launch routes. David has now tried CE and the museum construction test; his observations are recorded below. Development is resumed. This is not the 0.2 release; native Windows runtime and the online game path remain unaccepted. | [0.1.13 release notes](https://github.com/dlprentice/onslaught-ce/releases/tag/v0.1.13), [Manual feedback](#onslaught-ce-player-experience-and-online-play), [checkpoint order](#order-after-0113) |
| Reported Windows issues | One reproduced cause of double music is fixed in 0.1.12, with software-VM evidence, and Jeppi reports the audio fixed in 0.1.13 on their own Windows PC (a player's report; no log has been read). 0.1.13 adds changes aimed at the pause-menu mouse, the game clock after Alt-Tab and the system cursor in fullscreen; none of these three changes has yet been seen on a real Windows PC. The reporter's physical AMD/input retest, separate stutter and reported graphics artifacts remain open. | [CE releases](https://github.com/dlprentice/onslaught-ce/releases/latest) |
| Online multiplayer | On November 4, a bounded test with automated input and no movement or firing used two actual Linux CE processes on one machine through the authorized TURN relay: both entered a session, exchanged traffic and confirmed 1,000 simulation ticks; the guest closed and the host handled departure, returned to the frontend and quit normally. Independent raw-record review confirmed this result. It was not two physical players, moving and firing together, Windows, voice, a campaign win or a public service ([details](#multiplayer-engineering)). The test services were disabled afterwards. Player-ready host/join, native Windows, independent-machine networks and campaign progression remain acceptance gaps. The public CE README still lists Internet multiplayer as planned; public 0.1.13 is unchanged. | [Multiplayer engineering below](#multiplayer-engineering), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Campaign co-op and scale | Ordinary-campaign objectives, transitions, deaths, rejoin and safe progression are not established online. Opposing-team versus/skirmish maps, larger matches, team colours and compatible Battle Engine/unit customization remain goals. Players should be able to pilot Battle Engines or play eligible infantry, vehicles, guns and controllable structures. Temporary control needs identity/team/squad preservation, AI hand-back with current valid orders and controls/HUD appropriate to the type. The bounded opt-in solo tank prototype (movement, native firing, camera/control return and squad hand-back on one level; see [Multiplayer engineering](#multiplayer-engineering)) does not prove these full outcomes or network control. Local split-screen is not online co-op. | [Multiplayer engineering below](#multiplayer-engineering) |
| Controls, display and guidance | Improve understandable dodge/zoom and free-camera help, controllers, accessible menus, window/display choices and performance while preserving the game's look and feel. David's manual r2 report found photo mode fine, dodge difficult despite some successes, Commander janky and tank control jerky. Graphics reported Extra unavailable on an RTX 4060 with Geometry Medium and anti-aliasing None. These observations need focused reproduction; no cause or fix is established. Prefer supported high ordinary graphics separately from the requested optional maximum-distance/LOD/full-model mode. Floaty mouse and 4K HUD/UI remain in scope. Real devices and representative Windows graphics remain acceptance gaps. | [Player experience work below](#onslaught-ce-player-experience-and-online-play), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Level and mission tools | Required: usable 3D map and mission authoring inside native CE through its menus. Current integrated authoring runs in Companion, with JSON Save/Open, 3D placement and linked-map preview; it does not complete the in-game requirement. Unambiguous object definitions resolve to same-archive meshes, with inspected static, untextured level-221 models and unsupported references reported. In a controlled 2026-11-03 run (the page driven programmatically; no person at the Save as dialog), the page's Save as path produced projects that placed one existing level-221 boat at its authored X/Y in CE; the boat's own initialization replaced the stored height, and in one moved case later mission and AI reactions followed, so moving an object does not keep a mission unchanged. Both unreleased 0.1.99 Linux packages (r1 and r2) passed local edited-project smokes without a network session. No publicly released CE reads these projects. Reuse this working data/tooling while building native CE controls and workflow. Textures, animation, terrain editing, new playable levels, full mission authoring, human use, multiplayer loading and native Windows validation remain open; older installed-level candidates retain their separate scope. | [Mission project evidence](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore), [Mission project workflow and limits](companion/OnslaughtToolkit.Godot/README.md#mission-project), [Installed-level workflow](roadmap/companion-level-editor.md#2-what-exists-today), [Remaining candidates](roadmap/companion-level-editor.md#unreleased-editor-candidates) |
| Mods and content catalogue | Released mods override existing files and supply worlds on Linux; Windows remains disabled. CE development source includes the reviewed Windows loading contract, integrated November 3, with the normal-build switch OFF. Native filesystem acceptance remains open; integration does not enable Windows mods for players. The complete mod platform and verified catalogue remain open; catalogue path counts do not establish complete asset coverage. | [CE mods](https://github.com/dlprentice/onslaught-ce#mods-experimental), [Creation scope](#level-and-mission-tools), [Catalogue work](#content-catalogue), [Coverage limits](tools/README.md#catalogue-source-file-coverage) |
| Museum and custom levels | Required: an actual explorable 3D museum reached through CE's menus. The separate Goodies gallery retains bounded Linux visitor-access, return-navigation and saved-data acceptance for pictures/models; it does not unlock movies, cheats or bonus levels. The r2 checkpoint's construction test places three copies of one static prop on existing terrain; independent review and a repeated Linux run support movement and clean exit with inspected images and preserved careers, inputs and package files. Its museum-only profile stays separate from campaign play. Neither the gallery nor this test completes the museum or newly authored terrain/mission; native Windows, physical mouse input, audible audio and collision/damage remain unverified. | [Museum and authoring scope](#level-and-mission-tools), [Order after 0.1.13](#order-after-0113), [Level evidence](roadmap/companion-level-editor.md#3-what-the-measurements-say-2026-10-29-level-100-the-read-only-retail-view) |
| Commander | Required: continuous real-time 3D RTS Commander inside native CE, with usable camera, selection, orders and status UI. CE 0.1.13's opt-in map pauses the battle; development adds a live 3D strategic view. These partial controls do not complete the required mode. In a bounded Linux run, scripted Move, Advance and Fall back took one tank squad on one level to the ordered place and Hold stopped it; a longer Move stalled for an unknown reason. Aircraft, turrets, buildings and script-following squads take no orders, and artillery can only Hold ([CE README](https://github.com/dlprentice/onslaught-ce#commander-map-experimental)). David's manual r2 report is janky, so usability remains open. Buildings/production and eventual multiplayer remain goals; direct unit play is distinct. Preserve ordinary play while proving the full workflow, other units/scenarios and native Windows behavior. | [Goal](GOAL.md), [Mission-editor direction](roadmap/companion-mission-editor.md#optional-modes-and-ordinary-play), [CE commander map](https://github.com/dlprentice/onslaught-ce#commander-map-experimental) |
| Godot rebuild | Selected recorded level-100 comparisons exist; complete gameplay, audio and presentation parity and a finished playable replacement are not established. HD assets and expanded gameplay follow a faithful baseline. | [Godot parity record](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PARITY.md) |
| Decompilation and baseline | The private mapped-function check uses a disclosed one-byte compiled-object concession; without it one mapped function remains unmatched. Stand-ins and full linked/runtime equivalence remain separate work. The corrected public [overview](https://github.com/dlprentice/onslaught-decomp/blob/9169f28862ebda0b768cbcc7ec354734af013f5e/README.md#L14-L18) and [score-write documentation](https://github.com/dlprentice/onslaught-decomp/blob/9169f28862ebda0b768cbcc7ec354734af013f5e/tools/README.md#L7-L10) are exported. | [Public decompilation](https://github.com/dlprentice/onslaught-decomp) |
| Companion | Required end state: every Companion capability moves into native CE, and the separate app stays supported until each replacement is verified, then is phased out. Current standalone tools and evidence remain preserved. Automated Linux acceptance against released CE 0.1.13 covers the real launcher/career load, copied-career edits/backups/settings, running-game refusal and restoration. The 0.1.99 r1 Companion stage passed bounded copied-career/settings and inspected workflow/project checks. The r2 stage also passed actual version discovery, copied-career backup/edit/restore, settings writes and stale-write refusal; fresh workflow and installed-model images were inspected. David has not tried Companion in his November 4 playtest. These remain programmatic checks, not human use or an update hand-off. Broader Windows UI/device acceptance, listening and safe release remain. | [Companion README](companion/OnslaughtToolkit.Godot/README.md), [current evidence](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore), [dated 0.1.13 acceptance](VALIDATION.md#companion-with-real-onslaught-ce-0113--november-3) |
| Diagnostics and recording | Useful bounded logs and manual, informed reporting are available. Preserve faithful reference tapes and develop separate coverage for CE features and controller input; avoid telemetry or automatic uploads. | [CE reporting guidance](https://github.com/dlprentice/onslaught-ce#report-a-problem) |
| Special Thanks | Stuart Gillam, Jeppi and BermudaMaster are acknowledged in 0.1.12. Keep acknowledgements accurate as further contributors are identified. | [CE credits](https://github.com/dlprentice/onslaught-ce#credits-and-special-thanks) |
| Documentation, repositories and recovery | Public setup and contribution workflows are published. Owner reconciliation and indexing of retained evidence and continuity notes remain open. The verified restore covers one selected snapshot; restoration of the full corpus and recovery on a replacement machine remain unproven. | [Contributor workflow](CONTRIBUTING.md), [Recovery scope](#recovery-and-repository), [Project index](PROJECT-INDEX.md) |
| Showcase and website | Port footage is paused at David's direction (2026-10-29) and restarts only if David asks. The domain is owned; no website deployment is currently required. | Maintainer direction |

### Order after 0.1.13

Player experience and online co-op remain priorities. All lanes below remain requested outcomes. CE is the primary
place to play, create and experiment: continuous 3D RTS Commander, 3D map/mission authoring and an explorable 3D museum
must be usable inside native CE through its menus. A map/preview toggle, an external-editor launch button or the
Goodies gallery does not complete those respective requirements. Preserve ordinary campaign play and useful
quality-of-life improvements. Scenario eligibility, implementation and packaging can develop around these concrete
player workflows; the order below tracks dependencies, not dates.

The 0.2 release hold and the standing authorization for 0.1.x releases are worded once, in
[GOAL.md](GOAL.md#how-progress-is-measured): 0.2 is not released until David gives an explicit go-ahead after its whole
program is complete and tested internally, and internal playtest checkpoints do not lift that hold. Gated 0.1.x
maintenance releases remain under David's standing authorization of 2026-10-27; 0.1.99 is an internal checkpoint label
that is never published. Working multiplayer and the complete in-game workflows above are required alongside the other
agreed outcomes.

David has requested that **0.1.99 include the recent integrated work**. Two local checkpoints carry that label, and
this page names them only as **0.1.99 r1** (the earlier snapshot) and **0.1.99 r2** (the separate refreshed checkpoint,
which contains the reviewed work described below). "Package" and "stage" name components of a checkpoint (its CE
package, its Companion stage), never the checkpoint itself. r1, its accepted builds/packages, Companion stage,
launch setup/profile and copied user data remain preserved. The earlier Linux package smokes and bounded Companion
workflow/image checks remain evidence for r1; r2 has its own acceptance.

r2 has passed Linux and Windows cross-target builds (no Windows run) and package-content checks with networking, ICE
and text chat included. Native signaling is included on Linux; Windows relay startup still refuses its unvalidated path. The exact Linux package rendered its main menu/version and a local edited
project, and both runs exited cleanly. This does not establish navigation through the CE hub. The r2 Companion
passed actual version discovery, copied-career backup/edit/restore, settings writes and stale-write refusals; fresh
workflow and installed-model images were inspected. Its installed models remain static and untextured. Separate
manual launch routes passed independent review, focused helper checks and checks of the actual prepared files.
A separate museum construction test has bounded Linux acceptance as described below. Live services remain disabled,
and neither native Windows runtime nor the online game path is accepted for this checkpoint. Compiling those paths
does not establish a working online match.

**Development across the requested areas is resumed.** Preserve r1 and r2 artifacts and manual data while the
reported issues are reproduced in separate development/test outputs. They remain unreleased local checkpoints,
not the 0.2 release. The opposing-team, direct-unit, voice and other outcomes below remain in scope. Treat the
manual feedback below as observations within the tested scope, and retain each snapshot's source and evidence.

1. Online co-op for the initial two-player path: validate Windows hosting, the Windows guest rows and controls, message pages and a played win reaching the career writer. Windows hosting, a played win and Internet play remain unproven. Then more of it: opposing-team versus/skirmish maps, larger matches as the networking design permits, and play across the Internet without manual port forwarding. The initial pair is a validation step, not the final player limit.
2. The split-screen gamepad layer: a pad for each player in ordinary two-player split screen, with the menus and pause, and with faithful modes and recordings kept as retail. It comes first of the input lanes because the next lane uses it.
3. Complete continuous real-time 3D RTS Commander inside native CE with appropriate UI, then prove the uncovered controls/scenarios, native Windows behavior and a co-op commander seat. Commander design should explore a Battle Engine pilot who can issue battlefield orders and an optional dedicated commander role; these are future proposals, not implemented roles. The team commander role is optional: an eligible player may take a vacant team role and step down, and teammates, including the commander, may vote to remove them; a tie does not remove them. The proposed recall requires a majority of eligible team members, with eligibility, timeouts and disconnections to be defined. The commander role and its voting are proposed, not implemented. AI-controlled Battle Engines and expanded unit AI are planned; reuse of suitable existing unit behavior is to be explored, and no new AI behavior is claimed as implemented.
4. The remaining player-experience lanes: the CE Settings page as a table (pad navigation, a Windows run), a split-screen HUD scale per viewport (off in faithful modes), the fix for the crash on Retry in levels whose static shadows are bound to things that cannot hold one, the second phase of the sharper UI art, and launcher polish (a prompt that fits 1,280 pixels, a calmer line when a signature does not match). A unified CE entry must make Play, Create and Multiplayer discoverable. Create must provide usable 3D map/mission authoring inside CE; launching the separate Companion is not completion. Migrate Companion capabilities into the unified CE experience, retaining the current app and reusable data/contracts until their replacements are verified; check the contents and entry points of the delivered package.
5. The post-release review of every Onslaught repository: stale documents and how the products describe each other.
6. Mods toward the platform David describes: Windows support for the existing world-mod route first (without it, a custom level reaches only Linux players), then replacing any asset, then adding content and a scripting interface, each designed before it is built; the approved 3D map and mission editor work, with prototypes and independent work proceeding where their dependencies allow. The tools that replace walker meshes continue with chains, bounds, skeletal and camera parts and skinned meshes. Independent CE-native authoring may progress in parallel.
7. Done 2026-10-30, ahead of this order at David's request: CE ran editor changes in the bounded cases documented in the [level editor plan](roadmap/companion-level-editor.md). A comparison with the original is recorded privately and does not establish complete equivalence. Next, a writer that builds a level from scratch (terrain, world and mission), whose first targets are a two-unit test level that CE runs and the museum world, walked or flown around in the Battle Engine. Retail-compatible test levels are optional where useful.
8. The content catalogue to a complete inventory (every model, texture and image, used or not), alongside the museum's art boards, turntables, lighting, signs and a main-menu entry. The first CE exhibition can progress in parallel with catalogue work.
9. Level and mission authoring from scratch: usable 3D map and mission editors inside CE, including save/reopen and a connected playtest workflow, custom levels for players and small test levels CE can run. Reuse the existing tools and project contracts; retail-compatible export remains optional where useful.
10. Migrate every Companion capability into CE, with Windows acceptance for the resulting invocation, input, dialogs, rendering and workflows. The separate Companion stays supported, with its evidence, until each replacement is verified and usable; do not silently discard its remaining acceptance work.
11. Windows validation of every lane before release, the release path's own script, and the reported Windows issues retested on real hardware.
12. Source-only matching of the one function that needs the disclosed one-byte concession (see the chart's Decompilation and baseline row), and the Godot rebuild, continue alongside as separate products, not part of the CE package.

## Open work

### Godot rebuild

The rebuild's work queue, milestones and measured parity are kept in
[onslaught-godot](https://github.com/dlprentice/onslaught-godot), where it is developed; `rebuild/` here is a frozen
copy.

### Companion — CE integration

The companion is a C# application built in code on Godot 4.8 beta1 .NET and .NET 10, and organised around players: careers
with a campaign map, Goodies, career editing, cheats, game settings, automatic backups that can be put back, music
and voices, and lore (see its [README](companion/OnslaughtToolkit.Godot/README.md)). In this current standalone app,
every write into the game is a choice made after a verified backup, never while the game runs.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) records
what is proven. Players can choose the original game or CE, manage careers and backups, and use CE's two supported
launcher settings and the steps for updating CE (the companion contacts nothing). The CE launcher checks its own signed
feed and installs an update only when the player chooses Update.

The required end state is one native CE product, with the separate Companion phased out only after verified
replacement. Move every current Companion workflow and its subflows into CE (careers, saves and backups, settings,
lore, content exploration and the catalogue, the editors, installation management) alongside gameplay, content
authoring, mod selection and the in-game catalogue; the checklist below is the inventory. This replaces the earlier
plan to keep a separate offline-management product. Preserve and reuse the working Companion, tools, data/contracts
and evidence during the migration; the separate Companion stays supported until each replacement is verified. No
embedding of Godot, C# or another runtime is prescribed by this product decision.

Save editing inside CE needs an explicit coordination contract with loaded careers. Retain verified backups,
changed-source refusal, preservation of unknown data and read-back checks. Protect an in-use career, and arrange
the safe save/reload hand-off before enabling edits: a frontend screen may still have cached career state that could
overwrite a file edit. Simply removing the standalone app's running-process refusal would not provide that safety.
This integrated workflow remains required work, not a delivered capability.

#### Native CE migration checklist

This checklist inventories the production Companion pages and their subflows from the linked source. It is a
migration requirement, not a new runtime acceptance result. Each unchecked row needs an end-to-end native CE
workflow; existing CE features may already provide parts of it. CE can combine or rearrange the screens, but a
button that opens the standalone Companion does not complete a row. Preserve the working app and its evidence
until the replacements are verified; then it can be phased out or retained as redundant access to those capabilities.

| Workflow and current source owner | What exists in the Companion | Native CE completion check |
| --- | --- | --- |
| [ ] Home, game selection and launch — [HomePage](companion/OnslaughtToolkit.Godot/Ui/Pages/HomePage.cs), [CE home panel](companion/OnslaughtToolkit.Godot/Ui/CeHomePanel.cs) | Discover or choose an original-game install and CE launcher, check the selected inputs, browse recent careers, import a career or open one read-only, launch the selected game, open its manual and show update instructions. With CE selected, original-install careers remain read-only sources for new copies. Update instructions do not download or install CE; the CE launcher owns signed updating. | Provide coherent native access to game data, careers and update/settings information, preserving original-game compatibility and source identity. Consolidate with the existing CE launcher and menus; do not invent a second updater or revive retired executable patching/copied-install safe launch. |
| [ ] Older career recovery and location warnings — [HomePage](companion/OnslaughtToolkit.Godot/Ui/Pages/HomePage.cs) | Lists careers left in the old Windows toolkit's copied installs and saves checked copies elsewhere without changing the originals. Wrong-sized entries remain visible. Separately warns about Windows VirtualStore careers; that warning does not mean the app reads, backs up or restores them, and native Windows acceptance remains open. | Keep discoverability, checked copy-out and honest location warnings available within CE. Verify the Windows paths before claiming recovery there; keep unresolved locations visible rather than silently omitting a player's careers. |
| [ ] Summary — [SummaryPage](companion/OnslaughtToolkit.Godot/Ui/Pages/SummaryPage.cs) | Campaign route map, recorded taken/not-taken paths, mission names/status/ranks, kills and the career's Goodie strip. | Provide a native career overview tied to the selected save and installed text, with correct route/rank semantics. This is viewing stored progress, not an implemented arbitrary campaign-progress editor. |
| [ ] Goodies — [GoodiesPage](companion/OnslaughtToolkit.Godot/Ui/Pages/GoodiesPage.cs) | Browse categories and earned/new/viewed states, filter entries, inspect unlock rules and explicitly preview unearned items. Pictures display; model entries lead to Art & sound; videos and race entries identify their files/levels. Hidden stored slots remain preserved. | Retain the gallery, state explanations, optional previews and links into appropriate native content views and career editing. Gallery access does not complete the separate explorable 3D museum, and listed video/race entries are not proof that every item plays from this page. |
| [ ] Edit career — [EditCareerPage](companion/OnslaughtToolkit.Godot/Ui/Pages/EditCareerPage.cs) | Change kill counts and individual/all Goodie unlocks, review changes in words or exact bytes, undo/reset, save a new named career, replace an allowed career or save a copy elsewhere. Reserved and unknown data are preserved. | Supply the useful edits, previews and save choices through native CE, with the loaded-career coordination, backup, changed-source refusal and read-back rules above. Do not silently broaden this into unverified mission/progression editing. |
| [ ] Cheats — [CheatsPage](companion/OnslaughtToolkit.Godot/Ui/Pages/CheatsPage.cs) | Creates a byte-identical career copy with a cheat-activating name, either in the selected game or elsewhere; it does not run a developer console. | Preserve the usable cheat-copy workflow alongside CE's separately tracked console/cheat controls, explaining their effects and protecting the source career. Verify each native route rather than assuming that a copied name enables every proposed cheat. |
| [ ] Game settings — [SettingsPage](companion/OnslaughtToolkit.Godot/Ui/Pages/SettingsPage.cs), [CE settings panel](companion/OnslaughtToolkit.Godot/Ui/CeSettingsPanel.cs) | Edit original default options or a career's stored options: volumes, per-player flight/walking inversion, vibration/layout, mouse slider steps, screen shape and captured keyboard bindings in both slots; preserve other bindings and unknown fields. Open arbitrary options/career files read-only, undo changes and save a copy or allowed replacement. CE settings currently cover `update_check` and `record_sessions`, preserving unrelated configuration lines. A career's options are not applied by the game on load and may be overwritten later. | Consolidate native options with the established file semantics and safe save/reload behavior, including keyboard/controller/mouse bindings and CE launcher settings. Keep the distinction between effective defaults and stored career options visible; retain existing preferences and separate CE recording enhancements from faithful tapes. |
| [ ] Backups — [BackupsPage](companion/OnslaughtToolkit.Godot/Ui/Pages/BackupsPage.cs) | Automatic backups on app opening and after game exit when data changed, manual backup, chosen backup folder, dated sets/reasons and restoring an individual file. Scope is selected-game careers plus original default options; CE career sets include original careers in the combined list, while CE configuration has separate verified copies. | Offer native backup, inspection and restore with equivalent recovery and read-back guarantees. Coordinate with loaded saves instead of dropping the current process-based protection. Preserve backup scope and error messages; this feature is not an in-app cloud/off-site backup service. |
| [ ] Music & voices — [MusicPage](companion/OnslaughtToolkit.Godot/Ui/Pages/MusicPage.cs) | Browse installed soundtrack and voice lines by mission, search titles/transcripts, play/pause/stop, seek and adjust listening volume. Validate audio before decoding. Cutscenes are listed, not played by this page. | Provide the media browser, transcripts and playback controls natively, using the player's own files and verifying audible output. Keep this separate from planned multiplayer voice chat; future media replacement uses CE overrides, not installation-file swaps. |
| [ ] Lore — [LorePage](companion/OnslaughtToolkit.Godot/Ui/Pages/LorePage.cs) | Offline shelves/reading order, article outline, search, back/forward/home navigation and shortcuts, installed campaign names, the Allium map from the player's manual and opening that manual. | Make the lore library, search/navigation and installed manual/map content accessible from CE. Preserve attribution and local-data boundaries; retain an appropriate manual-opening route without treating a web link as the whole native lore experience. |
| [ ] Art & sound — [AssetsPage](companion/OnslaughtToolkit.Godot/Ui/Pages/AssetsPage.cs) | Search/browse installed models, textures and sound-bank samples; static model/texture previews and sound playback; export new GLB, PNG and WAV files. Model exports carry available textures, skeleton and animation data, but the preview is static, multi-mesh handling is limited to the first mesh and export interpolation/lighting can differ from the game. | Provide native discovery, previews, listening and deliberate exports with the same no-overwrite and protected-folder rules. Complete catalogue/animation coverage remains separate work in the [catalogue owner](#content-catalogue); existing export support is not proof of an animation player or a complete asset browser. |
| [ ] Level editor: maps and placed objects — [LevelEditorPage](companion/OnslaughtToolkit.Godot/Ui/Pages/LevelEditorPage.cs), [terrain viewport](companion/OnslaughtToolkit.Godot/Ui/Pages/LevelTerrainViewport.cs) | Select an installed level; inspect/filter placed objects; type coordinates, drag/nudge on a relief map, undo/redo/reset and copy an eligible unit. Paths and source-name links connect objects and scripts. A 3D terrain/marker view supports inspection and movement. Terrain sculpting is an unsaved preview: changed terrain disables Save and Play. Supported object/script edits can be staged as a new CE mod and tried through an isolated temporary profile without a career. | Migrate these workflows into the required [native 3D map/mission editor](#level-and-mission-tools), then complete persistent terrain authoring, safe source-preserving save/reopen and connected playtesting. Preserve object identity, targets, coordinate semantics and the player's real profile. Current bounded Linux edit runs do not establish native Windows or general new-level creation. |
| [ ] Level editor: mission scripts — [ScriptsPanel](companion/OnslaughtToolkit.Godot/Ui/ScriptsPanel.cs), [script compiler](companion/OnslaughtToolkit.Godot/Missions/ScriptCompiler.cs) | Inspect compiled handlers/calls, installed source, object uses and waypoint/name links; edit an eligible level script, compile/use it as an undoable change, see errors/warnings or restore the shipped script. Base-world and missing-source restrictions are visible. Drafts remain while switching scripts; the staged world contains compiled changes but does not retain edited source beside it. | Preserve inspection, navigation, diagnostics and undo in the native mission editor, and keep authored source through project save/reopen. Prove supported rules/objectives in CE with safe script execution and isolated playtests; compiling one script is not complete mission authoring. |
| [ ] Mission project — [CeMissionProjectPage](companion/OnslaughtToolkit.Godot/Ui/Pages/CeMissionProjectPage.cs) | New/Open/Save as `.ceproject`; authored object/source IDs and text, definitions, source attachments and entry-source selection; 3D marker placement, orbit/zoom/frame, typed coordinates, apply/undo/redo. Bind a placement to an installed object, load/reload/close a sampled-terrain and static untextured-model preview, reporting unsupported references. The game-folder path stays out of the project. The page has no terrain editing, source execution or new playable-level export. | Reuse the authored project contract in CE's native editor and complete the author → save/reopen → play → return loop. Preserve links, source text and safe file choices. Existing bounded linked-object X/Y loading is partial; object initialization may replace height, and full scene, mission, network and native Windows acceptance remain open. |
| [ ] Advanced Career bytes — [CareerBytesPage](companion/OnslaughtToolkit.Godot/Ui/Pages/CareerBytesPage.cs) | Read-only stored-value inspection, including god flags, and comparison against another career with byte differences grouped by region. | Keep advanced inspection and comparison available natively without turning this read-only tool into an unrestricted save writer or leaking career data into reports. |
| [ ] Shared navigation and write lifecycle — [CompanionApp](companion/OnslaughtToolkit.Godot/Ui/CompanionApp.cs) | Selected game/career context, open/save shortcuts, dirty-state and discard prompts, write progress, deferred closing during writes, game-running awareness and re-reading changed careers/settings after the game closes or focus returns without dropping drafts. | Integrate these protections with CE's own frontend, active match, loaded career and background work. Keep errors actionable, original/CE data ownership clear, drafts recoverable and ordinary gameplay unaffected. Verify real input, file dialogs and failure paths on Linux and Windows. |

The [Companion README](companion/OnslaughtToolkit.Godot/README.md#what-it-does) and
[capability record](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) retain the
evidence and platform limits. The [level/mission tool owner](#level-and-mission-tools) and
[catalogue owner](#content-catalogue) retain the broader authoring and content work; their command-line backends
are not additional demonstrated Companion screens. Reuse their validated contracts while supplying the required
native player access. A row is complete only after the intended interaction, result and applicable recovery/baseline
checks are observed on the claimed platforms, with source/evidence retained before standalone functionality is retired.

Public contributor setup is implemented. A fresh anonymous public clone installed verified official tools,
compiled the Companion and passed its authored runtime gate without maintainer files or game data on 2026-11-02.
The [setup guide](companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export) and
[validation record](VALIDATION.md#public-companion-setup--november-2) own the commands and measured scope.

Remaining acceptance and release work:

- Complete Windows UI acceptance. A [selected native Windows development workflow](VALIDATION.md#companion-native-windows-development-ui--october-25)
  exercised production-page actions and its screenshots were inspected; ordinary release invocation, physical input,
  file dialogs, hardware rendering and broader UI coverage remain open. The [November 3 Linux acceptance](VALIDATION.md#companion-with-real-onslaught-ce-0113--november-3)
  uses released CE 0.1.13's real launcher, protected edits, the game's own Load menu, running-game refusals and backup
  restoration. The November 4 0.1.99 r1 Companion stage adds the bounded copied-career/settings and inspected
  workflow/project images recorded in [current capabilities](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore).
  The r2 stage also passed the bounded copied-career/settings workflow and inspected installed-model views.
  These checks do not exercise the update hand-off or human input. Separate
  [native Windows checks](companion/OnslaughtToolkit.NativeChecks/README.md) cover production file/settings writes,
  real-process refusal, and CE loading the edited Unicode career. None is full campaign acceptance.
- Resolve the intermittent Windows launcher-version timeout: a reproduced failure waits in loader startup
  opening SDL3.dll, before the launcher's own version handling. The independently reproduced redirected-output
  defect is corrected in CE 0.1.5; it does not explain this separate startup wait.
- A human click-through and listening to the music and voices. See the companion README for the pinned source
  contract, backup scope and other limits. Public release remains at David's direction.

Any future media replacement would be a CE option (for example a CE user-data override folder), not a file swap
in an install.

Keep public application code and private retail data separate throughout migration, with the faithful baseline
independently testable. The current standalone Companion has no store, account or community features; CE's broader
multiplayer requirements are tracked separately below.

### Onslaught CE player experience and online play

Prioritize real player reports and a reliable corrective release while keeping the faithful reference path separate.
Fix reproduced retail bugs and improve performance while preserving the game's look and feel. The age of an API
is not a measured bottleneck: separate CPU simulation, draw submission, geometry/detail work, resource allocation,
GPU rendering and frame pacing before choosing an optimization. Keep inherited retail defects distinct from CE
regressions, and demonstrate the corrected behavior and its cost on each claimed platform. Investigate the report
of floaty mouse input in the original game; CE behavior is unknown. Reproduce the report and compare the original
and CE with matched input, frame timing and display conditions before choosing a correction; no mouse fix is claimed.
Check actual release packages on each claimed platform, and distinguish an authored fixture, Wine, a software-rendered
VM and representative physical hardware. Confirm that controls and features are accessible in-game and that errors
help players act. Make planned menu options discoverable with honest disabled or coming-soon states, and pursue live
display changes where feasible instead of silently requiring a restart. Verify the developer console, cheats, free
camera and tutorial guidance rather than inferring that all paths work. Keep faithful reference tape and replay behavior
while developing a separate way to record and
validate CE enhancements and controller input. More logging must remain bounded, non-admin and user-controlled; do
not add telemetry or automatic report uploads.

David's November 4 manual r2 feedback is a player report, separate from the earlier scripted checks. The supplied
log identifies CE 0.1.99 build `293eb81a8f7f` on an NVIDIA GeForce RTX 4060 Laptop GPU under Wayland, with three CE
launches and one museum launch, four normal game-close messages and zero reported summary errors. Those log counters
do not measure visual quality, control feel or correctness of every action.
The retained log has SHA-256 `81f2de49e62165489abf8356821f52d76148d55e547e805e42c4bd7b8a7e0dd7`.

| Area tried or discussed | Report and remaining work |
| --- | --- |
| Photo mode | David reported it working fine in this test. Keep the bounded positive report; it does not certify every level or platform. |
| Graphics | Extra graphics appeared unavailable despite the expected capability bypass; Geometry was Medium and anti-aliasing None. Reproduce the saved settings, capability decision and menu state before claiming a cause. The requested direction is high ordinary defaults and supported effects on capable hardware, with saved preferences preserved. Add terrain-detail/LOD, pop-in and extended draw-distance options, measuring image quality and frame timing. Maximum-distance/full-model rendering remains a separate optional mode, not the default yet. |
| Gallery and races | David found locked categories and no explorable museum there. The visitor currently opens pictures/models only; it does not unlock movies, cheats or bonus-level items. All five races were already reachable through retail Goodies unlocks; CE adds immediate access without campaign progression. See the [Bonus Levels description](https://github.com/dlprentice/onslaught-ce#in-the-game). The gallery and separate construction test remain distinct from the required explorable museum. |
| Commander | David described it as janky. Reproduce navigation, selection, camera and order feedback through ordinary input; successful scripted orders do not establish usability. |
| Tank control | David reported jerky control. Separate movement, steering, camera and frame timing in a reproduction; the ownership/firing checks do not establish smooth control feel. |
| Dodge | David managed some dodges but found them difficult. Preserve that distinction while checking timing, bindings and understandable guidance; the report does not establish a nonworking mechanic. |
| Museum construction test | David reported that it loaded. This is a human launch observation for the small separate test, not acceptance of the complete museum, collisions or all controls. |
| Companion | David has not tried it. Its workflow/editor evidence remains automated; no human Companion or editor acceptance is added by this CE playtest. |

**Deferred (David, November 4):** DLSS and ray-traced effects are ideas to evaluate later as optional future
enhancements, with supported-hardware checks, useful fallbacks and a way to retain the original look. David explicitly
placed both on the back burner, and neural texture compression is deferred with them: record the ideas, but do not
start implementation while the current work is being finished. No integration, hardware acceptance or performance
benefit is claimed. Neural texture compression is a possible future option, not an automatic benefit of updating
DirectX. The [Microsoft DirectX ML update](https://devblogs.microsoft.com/directx/evolving-directx-for-the-ml-era-on-windows/)
and [NVIDIA neural-rendering introduction](https://developer.nvidia.com/blog/get-started-with-neural-rendering-using-nvidia-rtx-kit/)
describe integration-dependent capabilities; their demonstrations do not establish memory or frame-rate gains for CE.

For the reported Windows issues, Jeppi identified the screenshot as the tutorial map; a separate log records a Blackout
session but does not establish the screenshot's level or cause. Training and Blackout are comparison cases. Verify whether
his reported fly mode was aircraft flight or the detached/free camera, then compare that view with retail and the port;
distinguish software rendering from physical hardware and do not claim the reporter's AMD symptoms fixed without evidence.

#### Multiplayer engineering

For multiplayer, progress in dependency order: two independent players with their own input, viewpoint, HUD and audio;
complete host/join and session failure handling; Linux and native Windows in both host roles across actual networks;
then tutorial/early-campaign co-op, save-safe progression and broader campaign coverage. Validate compatibility,
latency, loss, disconnects and rejoin. Versus and skirmish should support maps with opposing teams. Players may pilot
Battle Engines or directly control eligible other units under the match's rules, with team colours and compatible
customization. Spawning as a unit and temporarily taking control of one are both open design options; directly
playing it is distinct from a commander giving it orders. Infantry, vehicles (aircraft and boats included),
mounted/fixed guns and eligible controllable structures are in scope. This combined-arms direction needs coherent team/squad identity across direct
control, commander orders and the planned voice channels; it is not a currently implemented combination.
An opt-in solo tank prototype is integrated into CE development source and
0.1.99 r1. Its bounded independent Linux review demonstrated movement, native firing and
camera/control return on Aquila Prototype; the retained review receipt has SHA-256
`ba94fe981d4e95860e1b7112753596b9f070b4cebfda846c328c7c2d64dfa730`.
The parked Battle Engine remains vulnerable, not a required rule for future online roles. The initial prototype lacked
squad restoration. The refresh includes the reviewed hand-back correction: reciprocal membership is restored only
when the original squad is still live and compatible, the unit adopts that squad's current AI, and external ownership
changes are preserved. The retained independent review has SHA-256
`69886ea02b775c19a8c965d8005c9856e359e1645b6f1e4cd5b74079bb484d2b`.
Exact formation or waypoint restoration is not established. A unit HUD, native Windows runtime and physical-input
acceptance remain open. Network unit ownership/control and combinations with commander play remain unimplemented goals.
These optional match rules must not change the ordinary campaign. Larger player counts, custom maps and
Battle Engine/unit customization must not be claimed as available merely because a protocol or menu anticipates them.
Do not assume a transport, paid service, new recipient or cross-platform determinism without evidence and authorization.

For temporary control, preserve the same unit identity, team and squad membership rather than replacing the unit or
silently removing it from its group. Track valid new orders received while it is human-controlled. On release or
disconnect, restore AI using the latest valid orders, not just an entry-time snapshot. The design and checks must
cover a last surviving member, a squad that no longer exists, a destroyed target and an invalid destination, with an
explicit fallback appropriate to the unit. This hand-back contract is separate from how a match lets a player spawn
as a unit. Neither network possession nor complete AI/squad restoration is claimed for the current prototype.

The future controls and HUD must fit what is being played:

| Type | Required experience; not a current feature claim |
| --- | --- |
| Infantry | A viewpoint appropriate to the soldier, usable weapon selection, ammunition and reload feedback, with the unit's own movement and firing behavior. |
| Tanks and artillery | Native aiming/traverse limits, firing arcs and applicable trajectory feedback, ammunition and reload state. |
| Aircraft | A flight viewpoint and flight controls, weapon arcs, ammunition and reload state, a clear way to leave control, and only the actions the type supports. |
| Boats, ferries and other vehicles (wheeled, hover, walkers, drones) | The viewpoint, controls and feedback their type supports, with native movement and firing behavior. |
| Every other unit type | The catalogue's unit definitions list every type; each gets a defined viewpoint, controls and HUD, or an explicit written exclusion. |
| Mounted/fixed guns, turrets and controllable structures | Appropriate viewpoint, traverse/aim controls and a clear way to leave control; only actions the controlled type supports. |

Crosshairs, aim/trajectory indicators and firing feedback must agree with the native weapon's actual firing state and
obstructions. A displayed target or a fire input alone is not proof that a round was fired or that its path is clear.
These requirements stay in the broader unit-role work; they do not hold the isolated 0.1.99 checkpoint for infantry,
all-unit controls, full HUDs or online possession.

The intended menu is **Multiplayer → Local or Online**. Local should clearly distinguish split-screen from
local-network play. Online should offer a browser of available public lobbies and options to create or join public
and private lobbies, including a private invite/join path. Text chat is integrated in 0.1.99 r2 (source, unit tests
and package-content checks only; no in-game acceptance). Voice is planned and not implemented: it should offer
proximity/local, squad and team channels, speaking indicators above participating units, and mute controls, and its
backend, channel rules and indicator visibility still need design and validation. Optional LAN discovery plus an online directory and relay is one preliminary connection
design; the current two-player admission is an experiment, not a permanent cap. Cloudflare TURN and an experimental
Cloudflare Worker provide the authorized bounded relay and private-room signaling tests. Public lobby discovery and
production admission remain unfinished; their data handling and player workflows still need design and validation. These experiments do not establish
a shipped CE multiplayer service or player-ready automatic connections. Private lobby access controls must be
designed and validated: being unlisted alone does not establish private access.

The older [original-binary feasibility note](roadmap/original-binary-online-multiplayer-feasibility.md) concerns a
separate historical route, not a statement that CE already has online play.

The November 4 TURN test's retained summary has SHA-256
`48bca4f415db38b90ebef4cdb7820368c3e37d0cac6d4c333e6c8c09ea3f8c3f`; its independent raw-record review has SHA-256
`d78d6246061361a6ec38d66ba25ac3babeec300d5dd15e5f027f8f30e649991f`.
It proves the bounded Linux session lifecycle in the chart's Online multiplayer row (TURN relay), not active movement/fire, Windows, two physical machines,
voice, a campaign win or a publicly available service. The next active-input check must observe both player
movement and actual shot creation in both game processes, first with a direct test and then through TURN.

Multiplayer engineering results remain separate from public source and release acceptance. The
[published CE README](https://github.com/dlprentice/onslaught-ce/blob/bb4fa1f899db0d1826216b89a59c50781bb9cc9b/README.md#L721-L722)
lists Internet multiplayer as planned. Player-ready in-game host/join, native Windows hosting, two physical machines
across actual networks, a played campaign win and real-device controls still need acceptance; bandwidth requirements
still need measurement. The public release remains 0.1.13. The full 0.2 program remains in scope; the release hold is
worded in [GOAL.md](GOAL.md#how-progress-is-measured).

### Level and mission tools

The creation target is a modern CE-native project format and custom gameplay. Original-game export is useful where
practical but is not a prerequisite; the existing campaign's faithful baseline remains separate. The required player
workflow is a usable realtime 3D map and mission editor inside native CE, entered through its menus, with authoring,
save/reopen and connected playtesting. The existing Companion implementation and its formats are reusable working
tools; opening it from CE does not satisfy the in-game requirement. The integrated
[Mission project page](companion/OnslaughtToolkit.Godot/README.md#mission-project) creates an authored editor
document with placements, preserved source text and source links, saved and reopened as `.ceproject` JSON. Its 3D
view starts as a flat placement plane with markers, with orbit, zoom, drag and undo. A placement can be bound to one
named object of an installed level, and that level loaded as a read-only preview of sampled terrain and static,
untextured models. The Companion's Mission project page resolves unambiguous object definitions to meshes in the same resource archive;
fresh Linux level-221 captures were inspected. Missing, ambiguous and unsupported references are omitted and reported.
Base-world objects stay where the map puts them, and a name only the base world has, or that two objects of the level
share, is refused, following CE's project loader. The page edits no terrain and has no source
compilation or new playable-level export. CE development source now reads linked projects. In a controlled run on
2026-11-03 (the page driven programmatically; no person at the Save as dialog), projects saved through the production
page's Save as path placed one existing level-221 boat at its authored X/Y in default Linux CE; an independent review
reproduced the path. The boat initializes its own height, so stored Z is not a promise of runtime height, and in one
moved case later mission and AI reactions followed, so moving an object does not keep a mission unchanged. On
November 4, the network-enabled 0.1.99 r1 Linux package also passed a local smoke check of one of
those page-saved projects, with an inspected placement log entry and gameplay image and no active network session.
The 0.1.99 r2 Linux package also loaded that project, rendered gameplay and exited cleanly with no active peer. These
checks use programmatic page signals, not human dialog or drag input, and establish neither Windows nor multiplayer
project loading/replication, mission completion or general object support. No publicly released CE reads these
projects. The [capability record](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore)
owns the measured scope; the full format, authoring and runtime goals remain open.

David's mod-platform direction (2026-10-30) is recorded in [GOAL.md](GOAL.md): safe authoring and compatibility,
complete content coverage and HD successors remain open, and this page tracks the work.

The Companion's Level editor can inspect and move placed objects (typed, dragged on the map or nudged with the arrow keys), list only the moved ones, copy a unit (appended after every row so existing row, path and target indices do not shift; the copy retains its script and target), show a map and mission scripts, and edit a script's
source (compile it, make the level use it, undo it); it saves changed world files as new CE mods and starts CE at the open level with the changes in a temporary folder of its own (its Play button). The page is covered by
tests and offscreen captures on Linux; a script edit, a unit copy and two moved Target Tanks were staged by it and run in CE on Linux (section 16 of the mission
editor design and the level editor plan); nobody has used it by hand, and the mod does not preserve the edited source beside the world file. The [installed-level editor's candidates](roadmap/companion-level-editor.md#unreleased-editor-candidates), some on main and
some on branches, record their scope separately from the new authored-project workflow. Installed-level world/terrain project Save/Open,
script-draft restoration and the waypoint-check workflow remain outside that integration. The [level editor plan](roadmap/companion-level-editor.md)
and [mission editor design](roadmap/companion-mission-editor.md) own their remaining gates, including source-preserving
staging, hand use and gameplay acceptance. CE's released world-mod route remains Linux-only. The reviewed Windows
loading contract was integrated into CE development source on November 3. It constrains mod reads and keeps fallback
to installed data, but normal Windows builds retain the Windows mod-loading switch OFF (see the chart's Mods and content catalogue row). A special test build can exercise the loader;
that is not player availability. Native filesystem behavior, including links, spelling and files changed during a
run, still needs its Windows gate before enabling the route.

The integrated, unreleased Museum Preview currently reuses the Goodies pictures/models gallery. Its visitor access
does not unlock movies, cheats or bonus-level items. A wording correction naming the gallery read-only was integrated into CE development source on 2026-11-04, after the r2 build, so neither the r1 nor the r2 package carries it.
Its visitor Back route and saved-data checks passed independent Linux review; the retained review receipt has SHA-256
`9eb42f9130db4ea5d43728febc78bd8129e7f32644c09a6f1561930a47b5ceaf`. This is a gallery, not an explorable level;
native Windows behavior and the full museum remain open.

The 0.1.99 r2 checkpoint adds a separate **museum construction test**: three identical static props on
existing terrain, reached through its own prepared launch route and museum-only profile
(its authored room description is in [docs/ce-museum-project.md](docs/ce-museum-project.md)). The reviewed staging tool
and a repeated run of the exact Linux package demonstrated movement and clean exit; fresh frames were inspected,
inputs and package files read back unchanged, and no career files were created. The independent review has SHA-256
`ccb53107417183050541a5da3aa111f5dac1bf5500d35d8125529e9bb6d75b77`.
The repeated-run receipt has SHA-256 `25e70811254e85d256dc60d40969b155086f6c274604594e9381189ba13eff4b`.
The museum profile contains a base-world override that can affect other levels, so it is for this test only, not
campaign play. Offscreen relative-mouse acquisition was unsupported in these runs; physical mouse behavior,
collision/damage, audible audio and native Windows are unverified. The gallery preview remains separate, and this
sparse room does not complete the requested museum or a general new-level authoring system.

The museum and custom-level direction was approved on 2026-10-31 and clarified on November 4: the required experience
is an actual explorable 3D world inside native CE, reached through CE's menus. The gallery is separate and does not
complete it. The museum should be a self-guided world built from scratch, displaying every unit and model, inert,
for exploration on foot or in flight in the Battle Engine. It should show the game's art on boards, with turntables,
lighting and signs. The art comes from the player's own installation and is never shipped. A small CE-first exhibition can progress before
catalogue completion, suitable Windows support or original-game-compatible output. Full museum coverage still needs
a complete catalogue, level authoring, Windows support that passes its Windows gate (see the chart's Mods and content
catalogue row) and CE support for boards, turntables, lighting and signs. Protect the original campaign's expected behavior with regression tests while allowing documented bug fixes
and improvements. Small test levels runnable in both the original and CE remain optional where a direct comparison
is useful. Existing CE edit runs and the bounded comparison with the original do not establish complete equivalence;
the [level editor plan](roadmap/companion-level-editor.md) owns the CE runs' measured scope.

### Game documentation — ongoing

Write what the decompilation establishes as prose and specs in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation),
the one home of the game documentation, citing functions rather than quoting code;
[`reverse-engineering/`](reverse-engineering/RE-INDEX.md) here is a frozen copy. The companion's CE work (careers,
settings, launch) is the next consumer. Sections whose decompiler listings moved to the private archive on 2026-10-15 keep a pointer and,
where needed, a short summary; a fuller prose description is welcome wherever a reader needs one.

### Content catalogue

An evidence-based inventory of the game's content (textures, meshes, animations, sound, music, films, levels,
scripts, effects, interface art) with JSON metadata, as the basis for HD successors, modding, editors, multiplayer
compatibility and the rebuild. `tools/content_catalog.py` (schema `tools/content_catalog.schema.json`) surveys a
selected install and catalogues the families existing parsers read; every relationship names the loader function or
data that establishes it, and meshes and textures carry a usage summary for HD prioritisation. Its output is
retail-derived and stays in ignored `local-data/`. The `WRES` world bodies (every thing, waypoint path and compiled
mission script, with what the scripts' literal arguments name), the `ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB` and `DMKR`
payloads, the
`sprintf`-built sky, water, detail and HUD texture names and the registry of named things (`WORLD.mNamedThings`:
which things are predicted to join on load and in which order, so a script's thing name has a source-modelled lookup;
`tools/named_things.py`, with the retail gate `tools/content_catalog_gate.py`), the battle engine configurations (with
the weapons, explosion, cockpit and description each names, and the levels that offer each) and the `sounds.sfx`
effects (with their chains and the bank samples they play; `tools/game_tables_decode.py`) are decoded in their
loaders' order, and the physics script value by value with the rebuild's value classes, joined to the particle
effects, sound effects and HUD icons its values name (`tools/physics_values_decode.py`). `tools/content_inventory.py`,
with its retail gate `tools/content_inventory_gate.py`, accounts for every byte of a selected install as decoded,
framed by a record but unread, or unknown, and lists every model, texture, image, animation, sound, film and text
asset, used or not ([inventory entry point](tools/README.md#content-inventory)). Next: readers for what stays framed
(the font records, part of each imposter record and the HUD dial's later frames) once their loaders' layouts are
established, and the inventory of a second install. A catalogue is a foundation, not the mod system or an HD
conversion.

### Decompilation and native port

The maintainer's private byte-matching check matches every mapped game function with a guarded one-byte
correction to a compiled object; without the correction, one function remains unmatched. Its public export,
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), records its own coverage with that concession,
explains the DirectX sample files it leaves out, and documents its divergences.
The function matches do not by themselves establish complete behavioural equivalence or a byte-identical linked
executable. Its native source port (Windows and Linux) is published as
[Onslaught CE](https://github.com/dlprentice/onslaught-ce) (GPL-3.0-only source and binaries, no game files). Nothing
from either is copied into this repository.
Concession-free matching remains open: one mapped function still needs the guarded object-code correction.

### Recovery and repository

Keep an inventory of unique source, evidence, saves and necessary recovery material; verify selected off-site restores
and eventually rehearse recovery on a replacement machine. Reuse existing backups and deduplicate rather than repeatedly
uploading large unchanged collections. Keep private paths, credentials and signing keys out of tracked files. Selected
restores are not proof that the full corpus or current worktrees can be recovered.

On 2026-11-01, a selected review-evidence delta was restored with a fresh cache: the exact 77-file set,
8,466,420 bytes, matched every recorded file hash. The private verification receipt
`ROOT-RESTORE-VERIFIED.private.json` has SHA-256
`2499c8105365440c626a2b0d92d71e9c8ba9243039fc1d65ad02c0da994a3fa3` and records that the original inputs were unchanged.
This establishes only the selected snapshot; it does not cover work created afterward. Full-corpus and replacement-machine recovery remain open.

- The public history was flattened to a single new root (approved by David); the full earlier history is a
  verified bundle and `refs/old/*` in the private RE archive. The third-party fork and GitHub's pull-request refs
  still hold the old history; whether to ask GitHub Support to purge the PR refs is David's decision.
- The split: the Godot rebuild is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot) (the `rebuild/` copy here is frozen), and
  the game documentation is published as [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation). Held: bundling and re-flattening this repository's
  history, and renaming the repository. Public main histories stay unrewritten and the Companion is being moved into
  CE, so no rename is scheduled; any rename waits until the Companion's retirement is settled and is a separate,
  coordinated task.

## Paused

- **The earlier fixed-point rebuild's queue** (Core/Client/Godot, paused 2026-10-15 when the rebuild restarted around
  the parity core): World 110 generalization (former P7) and player-input replay tapes (former P8). Its final state is
  described in [rebuild/README.md](rebuild/README.md#the-earlier-rebuild-history). That historical queue was scoped to
  level 100; the current and longer-term rebuild goals are in [GOAL.md](GOAL.md).

## Closed

| Item | Outcome |
| --- | --- |
| Retail RE by Ghidra campaign (generations, contracts, promotion cohorts, record audit) | Superseded by the byte-matching decompilation; records in the private RE archive. |
| Private decompilation matching measurement (measurement closed; concession-free matching is open) | Every mapped function matches with the guarded one-byte correction; one remains unmatched without it. The published [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) records its own coverage, with that concession, and what it leaves out in its [score document](https://github.com/dlprentice/onslaught-decomp/blob/main/docs/SCORE.md). |
| WinUI toolkit, its UI tests and CLI (former P11) | Removed 2026-10-15; the companion replaced them. |
| Campaign bookkeeping relief (former P6) | Retired with the campaign. |
| Repository preparation (former P12) | The maintainer's checkout lives on a separate archive drive; `local-lab/` and `local-data/` are real ignored children. The 2026-10-15 cleanup moved the Ghidra checkpoint and RE machinery to the private archive and removed the WinUI surfaces. |
