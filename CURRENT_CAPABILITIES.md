# Current Capabilities

Status: active — what is demonstrated today, and what is not
Last updated: 2026-10-22 (Onslaught CE's install behaviour described; the decompilation cited as onslaught-decomp; the related repositories are linked; rebuild gate wording; the companion moved to Godot 4.8 beta1 and .NET 10.0.13, Windows backups default to an unsynced local folder; AppCore removed, its test facts now in the companion's tests; careers in old WinUI safe copies listed on Home; companion review fixes: CE running check seen on Linux, backups from another game folder after confirmation; the companion is Onslaught Companion and works with the original game only; AppCore patching and safe launch retired; relicensing: code GPL-3.0-only, docs and lore CC BY-SA 4.0)
Summary: the demonstrated capability of each part of the project with the measured gap stated beside it. Every
figure here is the value at the commit that wrote it; re-measure before relying on one. Superseded narratives remain
in Git and the private RE archive; they are not current operating instructions.

The companion, Onslaught Companion, is the player app for the original game and the future Onslaught CE launcher; its
development is paused until new requirements.
The byte-matching decompilation is complete and is the reverse-engineering authority (public export:
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp)); its native port is published separately as [Onslaught CE](https://github.com/dlprentice/onslaught-ce), and this
document does not measure it. The Godot rebuild, a scoped proof of concept (level 100, startup to exit), is developed
in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), which records its measured parity; `rebuild/` here is a frozen copy. Executable patching and copied-install
safe launch are retired and not planned; their code (the AppCore library and the `patches/` catalog) was removed on
2026-10-22, and Git keeps it.

## Retail behaviour findings — save, settings and startup

The [current compatibility recheck](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md)
executes selected unchanged retail bodies with preserved inputs and explicit
OS/heap/device boundaries. It establishes startup read versus write filenames,
campaign reset after settings load, menu-load forwarding to the next startup,
binding/preset serialization effects and the active language field written by the serializer.

The September 20 language extension passes 19 parser/cached-read/copy cases,
then 17 lookup-composition cases. All 2,571 IDs in each of six preserved language
files resolve through original text/audio-name/adjacent lookup code; pool bounds,
termination and offline decoding pass. Actual file Open and allocation remain
intercepted, and lookup imports captured state explicitly. These results do not
establish full startup, audio playback, localized rendering, durable save round
trips or reconstruction acceptance. The subsequent audio-volume recheck adds
25 focused scenarios at two x87 precisions and 16 composed loader/setter/save
cases, retaining original sound-event updates with explicit device boundaries.
The next 26 reset/restoration and 22 language-bank controls resolve caller
ordering and a cached-path retry limitation: a failed Open or skipped load can
suppress the next identical request. Actual devices, lifetime services and bank
file opening remain intercepted.

The subsequent 15 native reload cases feed original Save output directly into
original Load. Both gold controls preserve all 10,004 bytes, including unknown
fields; named derivatives distinguish flag writes, normalization and preserved
live settings. Private generated-copy fsync/readback succeeds on Linux. A further
17 startup cases execute original Blank and its full reset-time Goodie call:
exactly nine entries finish in instruction state, with no unlocked Goodies.
These results do not establish retail writer durability, complete process startup,
every unlock rule or player parity. Direct sample decoding is bounded separately below.
See [executed checks](VALIDATION.md#original-load-save-and-reload-controls--september-20).

The September 22 extension passes 26 original nonnull-cleanup and language-change
controls. Existing menu destruction, list recycling, resource counts and monitored
references are checked before the active text changes. A conditional input-state
write is verified at its corrected address. Heap operations and optional child
destruction are intercepted; authored objects do not establish complete menu
construction, input-device effects or visible localization. See the
[bounded cleanup contract](reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__SetLanguage.md#nonnull-cleanup-before-text-replacement).

The subsequent **44 sample controls** execute original cached reading, buffer
creation, decoding and quality conversion with intercepted heap/device services.
Two real English-bank records decode at all three normal quality values. One
reproduces a one-byte excess at quality 1 and a one-byte unwritten tail at quality
2 relative to the requested sizes. The current materializer's pure decoder matches
both complete quality-0 outputs. These are controlled-memory results, not real
device overflow, audible behavior, whole-bank loading or full startup acceptance.
See the [sample contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-sample-decoding-and-saved-quality)
and [executed checks](VALIDATION.md#original-sample-decode-and-quality-conversion--september-22).

A further 25 original caller controls resolve sample reuse, list insertion,
name truncation and suffix selection. They distinguish a filename-route stub
from the working buffer loader, correcting the meaning implied by inherited
names. The four-function metadata correction (private RE archive: `reverse-engineering/ghidra/README.md`)
is now saved, independently read back and protected by restored Archive A recovery;
all types, storage and unrelated functions are unchanged. A sample
can be inserted after a supplied device-creation failure, so list presence alone
does not establish playable audio. See the
[outer sample contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#outer-sample-admission-and-registration).

Original sample destruction now passes **23 standalone cases** and **11 cases
composed with the caller and loader**. A zero payload read removes a reused
sample from the canonical list, detaches matching events, conditionally stops
their channels and requests each old resource release once. Failed fresh creation
preserves existing samples and events. An initially null primary channel leaves
its secondary slot untouched.
These are guarded ownership observations with heap/COM/callback boundaries;
they do not establish real reclamation, playback or complete startup. See the
[destruction contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-sample-destruction-and-failed-loads)
and [executed checks](VALIDATION.md#original-sample-destruction-and-failed-loads--september-22).

Complete original bank/Open/refill/Close/sample decoding now passes **11 cases /
184 sample attempts**. All 164 English-bank high-quality PCM outputs also match
the current materializer's pure decoder: **21,537,072 bytes** compared. Reuse
preserves sample identities and list positions; disabling it prepends duplicates.
Supplied Create/Lock failures leave a published sample without playable PCM while
later records continue. Changed tags and a parser-unconsumed trailer are admitted;
zero/negative counts skip samples. These are original-code observations with
supplied filesystem/heap/COM boundaries, not real playback or complete startup.
See the [bank contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#complete-original-bank-loading-and-reloads)
and [executed checks](VALIDATION.md#original-complete-bank-loading-and-reloads--september-22).

Nine paired settings controls now connect original Load, reset/language refresh,
Save and direct-buffer reload. With a cached French path, applying English plus
an audio-word change presents that old path to the bank loader, although both
serialized outputs exactly match the English gold fixture. The second Load
corrects the path. Device Init and bank loading remain intercepted in this
composition; these results do not demonstrate audible wrong-language playback
or a cold-start defect. See the
[coupled routing contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#coupled-language-and-audio-settings-routing).

Separate original device Init/enumeration controls now pass **29 cases**. They
establish conditional index normalization, exact primary formats, capability-derived
method/count values and failure cleanup. An oversized device index becomes zero;
a negative index survives. Failed GetCaps can still lead to successful Init, with
different retained/defaulted state. These are isolated instruction observations
with supplied device responses, not actual audio-device or Load/Save integration
acceptance. See the
[device contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-audio-device-initialization).

Ten further controls execute original outer sound-manager setup and device Init
together. They verify all 256 pool objects, menu/console registration, timer
sampling and the initialized-byte distinction. Device failure clears that byte
but retains the preceding setup; matching console names reuse their entries.
SFX parsing and platform effects remain supplied boundaries. This does not
execute the full startup chain. See the
[outer initialization contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-outer-sound-manager-initialization).

Eight subsequent controls compose original device Init into Load/reset/Save and
reload. An out-of-range saved device index becomes zero when devices are admitted,
even if main-device creation later fails; no admitted devices leaves the saved
index unchanged. Both serializers preserve every other byte of the declared
fixture/derivatives. Failed reset keeps the initialized flag set, so a subsequent
load can request a language-bank refresh despite null device pointers. The bank
entry remains intercepted; this does not establish recovery or audible playback.
See the [device/save contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-device-effects-during-load-and-save).

Separate controls of the original bank code reproduce a null-device dereference
in the first sample's factory before its COM error check. A supplied valid device
completes the same records; a zero-count bank bypasses sample creation. This is
isolated original-code evidence, not an observed installed-game/Proton crash or
a single executed failed-Load-to-bank chain. See the
[missing-device contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#bank-loading-with-a-missing-device).

## Godot companion — careers, settings, backups, music and lore

The GPL-3.0-only [companion](companion/OnslaughtToolkit.Godot/README.md) is a C# application
built entirely in code on **Godot 4.8.beta1.mono.official.4d10419ca** and .NET 10 (`net10.0`,
runtime 10.0.13, SDK 10.0.402). Its one scene only
attaches the root script; the build refuses GDScript, saved resources and multi-node
scenes. David approved its feature set and Flight-deck look on 2026-09-25; on 2026-09-26
he asked for it to be built around players: easy to find your way, easy on the eyes, and
safe for their game and saves.

**Which game it works with:** today only the original game, the Steam or retail install that holds `BEA.exe`. It reads
and writes that install's `savegames/*.bes` and `defaultoptions.bea`, and Play starts it through Steam. It does not read
Onslaught CE's own career folder or launch CE, and its backups cover only the original game; it does refuse to write
into the game folder while CE runs and to save a copy into CE's folder. Its sidebar:

- **Home** finds the game through Steam (native, Flatpak or Snap on Linux; the registry
  on Windows) or a chosen folder, checks `BEA.exe` against the Steam release by SHA-256,
  shows the banner art from the player's own manual, offers Play through Steam, lists the
  careers with their progress and opens the most recent one read-only.
- **Your career**: a Summary with a map of the career's path through the campaign (each
  mission's rank, the routes taken and those the game recorded as not taken, read from the
  links the career stores), then missions, Goodies and kills; the 230 Goodies the game's
  gallery shows, row by row as on its wall, with titles from the player's text, unlock
  rules and how each rule is known (071–073 are stored but never shown); Edit career for
  kill counts and Goodies; Cheats for a byte-identical copy named to switch on the three
  cheats seen working in the Steam game.
- **Your game**: Game settings (the defaults the game reads at start, or the copy each career
  stores, which the game does not apply when that career loads: sound, invert, vibration,
  controller layout, mouse sensitivity, screen shape and keys captured from a key press, in
  the two binding slots each action has)
  and Backups (automatic backups when the companion opens and after the game closes, only
  when something changed; Back up now; every set, with Put back for each file).
- **Extras**: Music & voices plays the soundtrack and voice lines from the install with
  the game's transcripts (Bink cutscenes are listed only); Lore reads the repository's lore
  offline with search, the map of Allium from the player's manual and the manual itself;
  Art & sound lists the install's models, textures and bank sound effects, previews them and
  saves copies (models as glTF, textures as PNG, sounds as WAV).
- **Advanced**, folded away: Career bytes (the open career's stored values, or the bytes that
  differ from another career).

A change reaches the game only through one dialog that offers a new career, replacing the
one that was opened, or a copy elsewhere. Before anything in the game changes, every career
and the settings file are copied to a verified backup set; nothing is written while it finds
`BEA.exe` or Onslaught CE running, checked before the backup and again just before the swap (on
Linux, the `BEA.exe` rule was seen on 2026-09-26 to find the Steam game's own process under
Proton and nothing else; the CE rule was seen on 2026-10-22 to find a running Onslaught CE 0.1
on Linux, recorded in the ignored `local-data/companion/evidence/ce-running-check-2026-10-22.log`,
and is untested on Windows); a
file the game saved since it was opened is not replaced; the new file is swapped in (on Linux
an atomic exchange that swaps back if the displaced file is not the one backed up; elsewhere
`File.Replace` with the same comparison) and verified. A file is put back from Backups only if it
still matches the SHA-256 its backup recorded; a backup from another game folder goes back only
after a confirmation naming both folders. Switching careers or closing with unsaved changes asks first. When the game closes, or the player
comes back to the companion, it reads what the game saved and shows the latest, keeping any
unsaved changes; while changes are unsaved, a bar under the page keeps Save in reach. Every label style outside the banner measures at least 4.5:1 against the
surfaces it sits on.

The in-process [ProtectedSaveFiles](companion/OnslaughtToolkit.Godot/Files/ProtectedSaveFiles.cs)
adapter uses the companion's own `SaveLabFileTransaction` and `FileMutationSafety` (moved from the retired
AppCore library and since cut down to what the companion uses; see the companion's
[PROVENANCE](companion/OnslaughtToolkit.Godot/PROVENANCE.md)). Linux publication retains
no-follow handles, physical identities, unnamed staging and no-clobber linking.
Malformed or changed inputs and conflicting outputs are refused; uncertain publication
never becomes a success receipt or an automatic deletion. There is no helper process or
unchecked write fallback, and normal Godot .NET exports bundle their runtime.

A replacement in the game is refused on a drive without an atomic exchange (renameat2 RENAME_EXCHANGE); a failure
after a file is in place is reported as a possible change and the file is left as it is. Both are checked by fault
injection in the tests, not on a real drive lacking the exchange. Backups cover the careers and settings file the
companion can read; other files are skipped and counted.

**Evidence:** the lane's commit messages from 2026-09-26 record each check: `npm test`
(one C# contract suite inside headless Godot, including the portable write path run on
Linux, and the development runner's own cases), renders of every screen at 1280×800 and 1920×1080
reviewed first-hand, the problems that review found fixed, covered by tests, re-rendered and
reviewed again, and Linux and Windows packages exported, with the Linux package started and
quit cleanly under an isolated home. The earlier approved-workflow receipts are
in [their validation section](VALIDATION.md#companion-approved-workflows--september-26) and
the migration's in [its section](VALIDATION.md#companion-c-migration--september-25).
Art & sound and the Goodies page's "What it shows" are covered by the contract suite on
synthetic models, textures, a sound bank and Goodie archives; no dated receipt for them is
recorded here. **Windows execution (the portable write path has run only on Linux), a human
click-through and listening to the audio remain pending.** The companion does not patch
`BEA.exe` and that is not planned; mission, rank and link edits are not offered; no legacy
feature parity or retail gameplay acceptance is implied.

## Retired WinUI toolkit

The Windows-only WinUI 3 shell, its UI tests, the maintainer CLI and the portable ZIP
packaging were removed on 2026-10-15; the Godot companion replaced them. Their source,
demonstrated features and receipts remain in Git history.

The WinUI app's core library, AppCore (executable patch plans, guarded application, copied-install
"safe launch" profiles and their save and options services), and the `patches/` catalog it read
were removed on 2026-10-22; Git keeps them. Executable patching and safe launch are not planned
for the companion: Onslaught CE replaces them; it reads the install and keeps its own files in its own folder. AppCore's save-layout
and file-safety test facts were carried into the companion's own tests first. On Windows, Home
lists every `.bes` left in the old toolkit's safe copies
(`%APPDATA%\OnslaughtCareerEditor\GameProfiles\*`, in each copy's `savegames`, `saves` and `Save`
folders and its top folder, as AppCore's rescue searched) and saves each career-sized one as a
protected copy elsewhere; a file of another size is listed as one that cannot be copied. That listing
and copy are tested on a scratch folder on Linux (the button and save picker driven by the interface
test) and have not run on Windows; nobody has looked at the panel on screen.

## Reconstruction

**Active: the parity-core proof of concept.** David reactivated the rebuild on 2026-10-15 as a scoped proof of
concept: startup to exit 1:1 with retail, level 100 playable to completion. `OnslaughtRebuild.Parity` (a float-exact
C# port of the decompilation's simulation) owns the simulation and `OnslaughtRebuild.Host` the presentation, with an
experimental live mode. What it demonstrates, measured Present by Present against retail and native-port recordings,
and what remains open are recorded in [rebuild/PARITY.md](rebuild/PARITY.md) rather than repeated here; the Parity
suite's setup is in [rebuild/README.md](rebuild/README.md#working-lane). Test success there does not establish
audible audio, visual equality, physical input or a completed tutorial.

**History: the earlier fixed-point rebuild.** On 2026-10-15 David first parked this fixed-point rebuild in favour of a
native source port, then restarted the lane around the parity core above. What follows is the fixed-point rebuild's
demonstrated state at the old tag archive/godot-rebuild-20260926 (now in the private RE archive); it is reference,
not active work.

[`rebuild/`](rebuild/README.md) is a GPL-3.0-only (as a whole), source- and RE-informed
reconstruction lane. `OnslaughtRebuild.Core` owns fixed-step simulation,
snapshots, state hashing, and command-tape replay without presentation,
filesystem, clock, process, network, or GPU dependencies.

**September 26: Level 100 won, World 110 built, final capture.** The RE lane's
contracts for Level 100 are carried in C#, each with a focused test: the
Battle Engine's crosshair and auto-aim refresh, weapon stores and recoil shake,
the jet Missile Pod with locks and seeking rounds, every round's launch basis
and its own MOVE and life events, the cockpit Gun emitters, the retail load
order with every unit's callbacks, the influence map and warm-up draws, the
three-second pre-run, scripts starting on their INIT_SCRIPT events, waypoint
walks, the U-17's flight and the planes' move orders and retreat. The cold-start
route plays Level 100 through the player-input surface and wins it, and its
recorded tape replays deterministically to the same win
(`Level100ColdStartTests`; its gate replays it twice). World 110
is built in Core from retail data through its start state, and a Level 100 win
carries its surviving base world into World 110's load through the one Won
career update; the Client session launches World 110 with that carry-over
(`World110ConstructionTests`, `World110CarryOverTests`,
`Level100WonCareerHandoffTests`, `RetailCampaignFlowTests`). The Godot host
still plays only world 100, and World 110's landing craft do not fly yet. A
final offscreen capture of `main` matched the September 25 baseline except
differences traced to evidence
([VALIDATION.md](VALIDATION.md#return-to-all-code-c--september-25)): the
baseline's missing pines, the terrain's stage-3 detail matrix and the September
26 simulation contracts. The rebuild's Windows PowerShell launchers were retired
the same day; the Linux launcher carries their smoke and capture checks. Not done
when parked: World 110 in the host, the friendly turrets and parts of auto-aim,
physical input and audible audio, a side-by-side comparison with a retail run,
and Windows.

**September 25 return to all-code C#.** The rebuild is C# only and built in
code again (David's direction), on the exact `4.8.dev6.mono.official.8898c2b3d`
engine and `Godot.NET.Sdk/4.8.0-dev.6` with `net8.0`. Its code is the last
all-code C# rebuild (`b0b9c5e7`, September 19) with the pause menu's tree built
in code and the later evidenced fixes: strict AYA texture admission, refusals
of two impossible inputs and the smoke-validator pin. The September 19–25
GDScript and editor-scene work is retired; Git keeps it. The restored build
records the identical smoke tape (`89ca7b4b…`), the C# headless replayer
reproduces its trace and final state (`a4e6673b…`, `53c1cc64…`) and the first
flight fingerprint, and an offscreen Movie Maker capture of startup, menus and
Level 100 matches the September 25 baseline's audio byte for byte and its frames
except the evidenced differences in [VALIDATION.md](VALIDATION.md). Level 100 and
World 110 moved on September 26 (above). No desktop input or desktop capture was used.

**September 6 native Linux evidence.** Godot 4.7.2 .NET built and ran through
the native synthetic First Flight smoke with no Godot error. A separate normal
startup reached menus, new career, briefing/configuration, the Level 100 intro
and gameplay through operating-system input. The intro produced nonzero captured
audio. Its mostly idle gameplay tape recorded **9,367 ticks** and replayed twice
with both the live trace and final-state hashes verified. Expected hashes were
accumulated from live snapshots, not generated by replay. The tape and captures
are in `local-data/first-flight/player-20260906-b/`; replay and build output are
in `local-data/test-runs/linux-route-20260906-af1sa_l9/`.

This establishes a native execution and recording route. It does **not** establish
training completion, pause/retry/failure through live input, full audio mixing,
controls parity or World 110 play. Logo/montage soundtracks were subsequently
decoded into the startup cache and passed format/length checks; their native
playback still awaits the next desktop session. David reported successful retail
Steam/Proton launch; the agent inspected that installation and executable identity
but has not reproduced the retail playthrough.

**September 8 isolated rendering.** The corrected living-aircraft build completed
the native synthetic smoke at 2,148 ticks with the same final hash as the Client
check. A private authenticated Xvfb server and software renderer produced actual
Godot menu frames and a 107.9-second movie at 20 frames/s, matching the smoke's
one 20 Hz simulation tick per frame. No desktop input or desktop capture was used.
The smoke exercised movement, four fire inputs, retry and return; its mission
was still Running. It is development footage, not a completed player tutorial,
retail comparison or performance benchmark. Logs and raw recordings are in
`local-data/first-flight/progress-video-20260908-a/`. The recording predates the
audio-exit correction below. The labelled 50-second preview is
`onslaught-progress-2026-09-08-final.mp4` in that
directory; `first-flight-full-20hz.mp4` retains the full smoke recording. Both
show the production source at `5fc65256`; the preview uses edited excerpts.

**Audio shutdown.** The Godot host now stops producers and streams before quitting,
then lets the mixer release outstanding playback objects. One shared weak-reference
observer covers music, samples, radio and FMV tracks, including recently replaced
tracks; menu, window, capture and smoke exits use the same shutdown owner. The
private full smoke went from four/eight leaked Ogg objects in the two diagnostic
runs to none, preserving its 2,148-tick simulation hash and retry/return results.
The private window-close event and main-menu capture also exited without leaked
objects; **174/174** focused audio/frontend checks passed. These are lifecycle
checks with the Dummy audio driver, not audible mixing or Windows acceptance.
Exact logs and remaining boundaries are in [VALIDATION.md](VALIDATION.md).

**September 8 copied-retail observation.** A pristine-identity retail copy also
reached and rendered Level 100 through installed Proton Experimental Wine and
WineD3D on the private display. Its `-level 100` entry bypassed the frontend;
audio was disabled. Hardware breakpoints captured twenty-five Plane/guide calls
with live PC24/RN arithmetic. The existing native routine probe reproduced
eleven consecutive observed Euler/basis transitions. Core now carries the
matrix operation order as well as angle smoothing, with **50/50** focused tests
passing. A subsequent 128-sample run captured 32 consecutive Moves; compiled
Core arithmetic matched 352 grouped comparisons with the observed guide inputs.
The production mover now retains raw creation/pose/Euler/drive/velocity state,
translates before smoothing, preserves bank, and schedules its clearance cache.
Spawned aircraft use the seated Airfield and distinct raw emitters. Snapshot,
restore and schema 47 include the guide and ordered aircraft callbacks.
Managed trig remains provisional outside the finite comparisons. Native
controller approach/retreat and weapon-support callbacks, the complete avoidance
candidate stream, contacts, effects and dying flight remain unfinished; the
current target bridge still pursues during Move. Private
inputs, scripts and receipts are in `local-data/retail-runtime/aircraft-20260908-a/`;
the [Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md)
records the exact route and limits. This does not reproduce a player tutorial,
the normal Steam/DXVK launch path or Windows behavior.

**September 7 source and RE progress.** The
[Actor/base contract](reverse-engineering/binary-analysis/functions/Actor.cpp.md)
and [Unit construction order](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md)
now resolve the static ordering of script binding, publication, shared random
draws, weapons, attached spawners and movement requests. World 110 still lacks
the complete execution of those dependencies. The
[scheduler implementation](rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs)
now captures the overflow visit count before overflow callbacks, matching retail;
the regression failed before repair and all 32 affected tests passed. This is
source/static progress, not a new live playthrough or parity result.

September 12 reviewed and executed the complete incoming remote checkpoint:
focused Core passed 150/150 and Client passed 907 with two existing capture
skips. Full-combat and Save Lab UI acceptance remain open. The resumed Ghidra
audit corrected one missing Plane-controller event argument, with isolated and
live readback and verified off-drive recovery. Two script callback prototypes were then
corrected through the same gate, preserving unknown return and purge metadata.
Five further names/comments/tag sets now identify the Unit provider selector
and its Weapon readiness, mask and burst helpers correctly, with all bodies,
ABI and non-target metadata preserved and independently restored recovery.
The audit also refuted a stale
missing-boundary note. The internal-function inventory is available, but the
wider semantic audit is incomplete; the controller's decompiler stack artifact and
named-but-untyped script callbacks remain explicit next work. See the
[execution receipts](VALIDATION.md#linux-execution-of-the-remote-checkpoint--september-12)
and Ghidra owner (private RE archive: `reverse-engineering/ghidra/README.md`).

The bounded nonballistic Unit weapon selector now has original-code execution
evidence and passing Core cases, including a distance example that detects
incorrect widened arithmetic. Selection preserves burst locks, first-wins
ties and retail's unusual out-of-range scoring. It is not yet connected to
actor firing: retained aim, preparation phases and burst-event ownership must
be integrated together. [Validation](VALIDATION.md#bounded-unit-weapon-selector--september-12)
records the exact stubs, exclusions and negative controls.
An additional unchanged-code phase experiment covers preparation, readiness,
fire and post-fire state across 26 synthetic cases. It establishes bounded
state transitions and the ignored Weapon Fire return, not projectile creation
or combat acceptance; the actor firing loop still needs their integration.

The Airfield's two exit waypoint inputs now reach Core with their exact CEMT
selectors, model positions and inherited orientations. The bounded lookup
matches independent calculated world-pose words and preserves definition/hash
ownership. Core now runs the earlier 3002 exit phase, including both altitude
clamps, strict arrival/deadline checks, event reuse and delayed targeted Ready.
Restore retains the exit and pending handoff without repeating Init or Ready.
Completion clears collision-ignore state while preserving the guide; loss of
the spawner marks the Plane dying without declaring immediate shutdown.
New bursts wait for normal control, while a pending burst can continue and its
new round first moves on the following tick. An unchanged-code exit/GoTo/guide
experiment passed 26 synthetic cases; these and the Core checks are recorded in
[validation](VALIDATION.md#aircraft-exit-lifecycle-integration--september-12).
Normal control still hands back to the existing approximate target/weapon loop.
Selected-provider firing, dying flight, contacts, avoidance and complete world
event/RNG order remain open; no full-combat or player-route acceptance is claimed.
The working Ghidra initializer now has its RTTI-backed CUnitAI attribution, and
the dispatcher/exit prototypes carry the actual incoming event pointer. These
metadata corrections preserve the unestablished return types and are backed by
separate full readbacks and restored independent recovery.
The exit comment now distinguishes vulnerability, CST collision-ignore and
the GoTo override. A subsequent original-code common-controller/Unit-phase
composition passed 21 cases across 27 calls: provider refresh precedes readiness,
preparation can select twice, pending preparation retains aim, and already-ready
fire does not recheck the newly computed feasibility flag. Scene queries,
selection, target aim, Weapon Fire and acquisition are controlled stubs.
The existing firing loop still omits the selected weapon mounts and the
non-seeking round's B-feasibility line query. Neither this experiment nor the
metadata correction advances full-combat or player acceptance.
Ordered aircraft weapon uses and exact GunA/GunB selector1 model poses now
reach Core through the materializer and Client decoder. Immutable ownership
and definition identity retain the raw flags, order and twelve pose words;
the earlier GunA/2 binding cannot be selected accidentally. This adds required
firing input without changing simulation behavior. An eight-case unchanged
MainLoop-fragment experiment also shows that its supplied model-time fraction
need not equal one under PC24 arithmetic. The follow-up unchanged attachment
composition passes 27 cases / 33 calls through native Unit/mesh/getter/math
bodies with synthetic receivers and warm caches. It distinguishes current from
interpolated pose, arithmetic order and direct-cache reuse within a frame.
The next unchanged-code experiment passes 11 cases / 17 calls with a fresh
renderer cache and all 12 actual mesh parts. Native frame-zero population
matches stored CPOS/CORI under both tested precision controls. Static loop
readback identifies the cache stamp as the separate render-frame number;
gameplay updates and render calls need not advance together. The firing loop's
use of these paths, ordered render context and camera-latch lifetime remain
open; this adds no player-route acceptance. See the
[focused evidence](VALIDATION.md#aircraft-renderer-cache-population--september-12).

The first-training review corrected five misleading Ghidra names/comments in
the working database, followed by the missing physical-keyboard function boundary
and a bounding-box reader mislabeled as a material loader. Two follow-up
comments now record its caller correctly and the shipped AABB-distance quirk,
with separate full readback and verified PRE/POST recovery. Four further
labels/comments/tag sets now assign segment-controller helpers and their motion
bridges to the correct owner, removing the disproved UnitAI classification;
the checkpoint/working owner (private RE archive: `reverse-engineering/ghidra/README.md`) records the
exact scope. The rebuild's New Career field now carries the measured fresh-text,
cursor, character, width and unique-name rules. Its software keyboard and caret
geometry remain incomplete. Held Vulcan input now reaches Fire; Pulse release
clears charge before refusal, and per-weapon float readiness replaces integer
countdowns as the gate. The charged mode uses its 0.5-second reload. Focused
checks passed (43 frontend, 68 Core and five input/weapon Client tests).
September 8 connected the shared retail event-clock calculation to weapon
readiness, including level reset and gameplay pause. Large now uses its authored
speed 20, nominal lifetime 7 seconds, contact radius 0.20 and direct damage 8;
its zero aim spread preserves the two retail scatter random draws.
Contact inputs preserve the original serialized BBOX/render-radius float words
and per-part hierarchy/cache/NMIC records, retaining absent caches explicitly.
The Warehouse bounds-report builder preserves original part identity, reference
geometry, cached-transpose arithmetic and the first-six contact order. It still
requires supplied poses and break-latch eligibility; it is not yet connected to
the production explosion path. Geometry operations follow the measured device
setup's PC24/RN intent; the later copied-retail sample above confirms that mode
for its Plane/guide calls, not the entire explosion path or other backends.
Direct Morph/Charge/Fire/ChangeWeapon/Zoom now precede actor and mission
callbacks, using the retained launch pose. Full axis/event ordering, spatial
blasts, Large effects and precise float motion/expiry remain open. Tank/Truck
death now retires the script immediately while retaining collision/render
activation until the retail half-second shutdown bucket. Further accepted damage
still lowers life; death callbacks and the timer remain one-shot. Pending
shutdown order/timing survive restore and canonical hashing. Pending ground
motion now preserves the four-update cadence: retained velocity on intervening
updates, then the full-update stop, with distinct old-position/old-orientation
rules and conditional terrain support. Native float velocity, surface contact
times, terrain tilt/bob and the Drone's different shutdown/motion conditions
remain incomplete. These changes have not had a live desktop playthrough;
focused results are in [VALIDATION.md](VALIDATION.md).

World 110 is constructed by `Simulation` from its materialized static world, in
the retail load order, through its start state, with Level 100's surviving base
world carried in through the career (VALIDATION.md, "World 110 construction and
start state" and "World 110's base-world carry-over from Level 100"). The
earlier, separate World 110 construction stage (the turret-input, tree,
Building, SAT and Feature prefix and its admissions) was retired on 2026-09-26
because it duplicated that construction without ever running in the product;
its retail contracts stay in the
[World110 evidence owner](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md).
The Godot host still starts only Level 100.

**2026-08-19 operator click-through (not training Won).** Godot 4.7.1
mono on `main` showed night fortress → Aquila title art → main menu
(New Game highlighted) → CHOOSE GAME NAME / BEA 1. `RetailFrontendScenePath`
now also drives Loading → Gameplay. Scene-path tests 19/19 after that
merge. L100 Core owners on `main` include EnableFlightMode, SetObjective
OR 0x20, TargetZone InJetMode/Pause wait-stop. WinUI GUI was not
re-launched this pass.

**2026-08-19 evening — cold start to Level 100, in engine (still not
training Won).**
`Capture-Frontend.ps1 -Plan gameplay -Purpose production
-RetailOffsetManifest …/level100-gameplay/manifest.json` drove the whole
scripted traversal on `75ecbd2e` with a clean Godot source tree: click-to-start
→ FEP_MAIN New Game → CHOOSE GAME NAME → level select → mission briefing →
select configuration → Loading → Gameplay, then held Level 100 for 42 s.
**92** shots at retail's realised level offsets, **0** screen mismatches, **0**
missing, **0** wrong-size, `capturePurpose` `production`. In-level frames carry
the released first-person cockpit, HUD reticle, scanner, portrait, and the
tutorial subtitle line. `Level100WaterEnvelopeTests.CapturedWaterStaysInsideTheRetailEnvelope`
**scored that capture and passed** — it was not skipped, so the retail water
envelope was measured against rendered pixels, not asserted. The frontend
parity scorer still reports UNSCORED for this plan because its reference set is
the frontend page corpus, which holds no in-level page; that is a scope
boundary, not a pass.

The Aquila walker texture bind **is** wired in
`FirstFlightWorldView.BuildPlayer`. `m_f_be1.msh.aya` uses TEXR indices
{0, 1, 3} and the dictionary supplies all three (cockpit, BE_texB, BE_texA),
leaving `unboundUsedIndices` empty in the asset-lab bind census;
`RetailAquilaWalkerAsset` throws on an unmapped used index, so the walker
rendering through all 92 production frames is the runtime witness. What is
still not wired is the TEXB-name→file lookup, the decoded-PNG path, table rows
2/4–7 (`Chrome3`, unused on this actor), and bones/skinning.

The Godot Level 100 Opening Slice now uses all 513×513 unit-lattice positions
decoded from the released tiled Level 100 HFLD, plus the Federation walker/jet,
all 33 visible static objects in the
released Level 100 base-world records, all 1,481 Steam-instantiated pines, the
released active-path water grid and authored shoreline, three training tanks,
and target Warehouse
geometry. Core starts at the released
player-one heading and owns the authored player ground elevation plus the
machine-observed objective and player gates through the first Firing Range
exercise. The prior synthetic arena boundary, flat plane, and
placeholder structures are gone. Terrain, retained meshes, facilities, sky,
light, camera, and Core-relative positions now share the released
`(X, Y, Z-down)` → Godot `(X, -Z, -Y)` mapping. The opening view follows the
released four-point Level 100 pan around the exterior Aquila, switches to the
retained first-person cockpit and HUD after 5.95 seconds, and reaches the retail
playing-camera state after six seconds. Level 100's script keeps the player
deactivated beyond that camera handoff: Core enables movement/look only when the
mission script and message schedule enable power. The historical tick-1000
observation in `rebuild/PROVENANCE.md` uses 30 Hz Core sample coordinates;
current scheduling belongs to `Level100MissionTiming`. The Firing
Range later deactivates the player, then re-enables it with only the Pulse
Cannon; flight remains disabled. Two fresh
uninterrupted safe-copy runs repeated the same camera endpoints, six-second
length, handoff, and playing-state boundary. A clean Level 100 control and two
fresh repeated safe-copy runs also establish the walker's acceleration,
equal forward/strafe cap, frictional
coast, and inertial body turning. The client renders Core's continuous yaw
rather than an eight-direction visual snap. Two further repeated runs establish
BattleEngine-owned vertical aim at the authored start: exact first input and
`0.8` coast response, stable pitch endpoints `+0.532123` and about `-1.0912`,
and a Pulse Cannon direction matching the crosshair-derived yaw/pitch vector
within `0.00119` per component. Godot now pitches the retained retail cockpit
and camera and renders the resulting three-dimensional Core projectile path.
It also follows the released input ownership: `WASD` and arrow keys move the
Battle Engine, while mouse or trackpad motion owns look and aim. At retail's
compiled default sensitivity `7.0`, the Godot adapter preserves pointer
magnitude, applies
the released centered-offset mapping and recentering rate, and feeds Core's
released walker yaw/pitch response. Other sensitivity settings,
inversion, and jet mouse response are not yet claimed.

The compiled default and selectable sensitivity law are specimen-bound in
[rebuild/PROVENANCE.md](rebuild/PROVENANCE.md).

Core uses the source-declared 10-tick walker-to-jet transition at 20 Hz, but the
mission script controls when flight becomes available. The walker, jet, and first-person cockpit now load
directly from their exact released AYA files as 63-, 54-, and 21-part
hierarchies with 54, 58, and 10 material surfaces. The external jet and cockpit
advance through their separately timed authored `walktofly` frames after the
released transition-entry mesh swap, then select looping `fly` frame 0. The
exact takeoff effect and in-flight loop begin at that same boundary. The
walker's twenty leg-chain parts consume four
deterministic Core foot contacts. Core reproduces the released diagonal step
scheduling, 400-phase-unit-per-second swing, 0.4-unit lift, and exact Level 100
heightfield contact; Godot selects each leg's `LegMotion` frame by required
root-to-foot extension rather than replaying one synthetic gait cycle. The 24
non-tree static-world mesh types, four `pinesnow` variants, and two target types
remain bounded static conversions. The 1,481 pine placements use exact released
meshes inside retail's **authored 30-unit** horizontal mesh-quality boundary —
the image's own static initialiser, which is the Geometry detail = Medium arm —
and exact six-view atlas geometry beyond it. There is no third fast-tree path:
no always-on camera-facing standing card and no camera-height-gated horizontal
card is drawn — the reconstruction's only pine representations are the gated
close meshes and the six-view far imposters
(`rebuild/OnslaughtRebuild.Client.Tests/Level100PineRepresentationTests.cs`
forbids any third batch, `AddFastPineImposters`, and `camera_facing`). Retail's
own separate fast-tree static path remains an unresolved retail finding,
explicitly not drawn here. The standing-view manifest pins a phase-0 ordinal
cycle only as a
deterministic reconstruction; all 1,481 assignments and their four counts are
checked. Steam's exact owner allocation/view sequence and address-selector
phase remain unresolved. The
converted static-world and target OBJ front faces are adapted to
Godot's clockwise winding instead of exposing
interior/back faces. Aquila and exterior meshes render from exact locally
materialized AYA-wrapped textures. Static object
shading uses the released PC ambient plus opposing sun/anti-sun lights and
stage-zero `MODULATE2X`, not invented Godot metallic/roughness values. One no-input control and two
fixed-yaw retail repetitions per facility establish circular walker contact only
for the Control Tower and Tank Factory: inward motion is removed, while tangent
motion slides around the tower. Core consumes those two observed envelopes; it
does not claim general mesh collision.

The 30-unit Medium boundary comes from the retail static initializers;
persisted options can select a different distance. The measured distinction is
owned by [rebuild/PROVENANCE.md](rebuild/PROVENANCE.md).

Twenty-nine exact released HUD textures — **the count the client loads and
composes**, not the count the asset materializer retains, which is larger and is
stated in `rebuild/PROVENANCE.md` — including Font13PS and the three v3
crosshair layers, replace the prototype overlay for the bounded threat circle,
lower-left scanner/weapon instrument, lower-right battleline/portrait,
active-objective markers, and conditional message panel. All fifty-one
English tutorial messages now use
exact released strings, shipped Ogg/Vorbis voices, proportional font metrics,
the native 120-pixel message composition, and four released
Tatiana/technician portrait poses. Repeated retail runs matched every retained opening boundary
within 50 ms, then repeated Target Zone 1's 5.4-unit overlap, delayed objective
swap, and `TUTORIAL_02` dispatch. One control and three accepted Firing Range
runs then repeated the same five-message sequence, current-weapon highlight,
four objective pointers, temporary player deactivation, and Pulse Cannon-only
activation. A no-fire control and fresh isolated copied-runtime runs then
established the same bounded lifecycle for each of the three training tanks:
first active charge bucket `10`, round speed `35`, movement `1.75` per released
20 Hz update, starting life `6`, direct-contact total damage `1.8`, and
destruction/objective removal on shot four; one separate glancing hit removed
`1.0`. These are observations of those shots, not a universal same-target
damage rule. Core still applies a fixed Medium explosion stage. The September 8
correction gives charged Large its own movement/contact scalars and direct
damage, without inventing a fixed Large blast. The [round/explosion contract](reverse-engineering/binary-analysis/cround-hit-damage-path-2026-08-10.md)
requires a spatial neighbor scan and distance falloff, including eligible dying
receivers. That production gap remains open.
Two further isolated repetitions then removed the Warehouse objective
after exactly twelve normal hits along one fixed center-aim attack line and
repeated the released player-off,
Vulcan-message, Pulse-off/Vulcan-on handoff. That observation remains a bounded
runtime comparison. Core has extent-weighted 28-segment health and now disables
the main core's 20 direct Extra children in the native list order when that core
breaks. The six queued chimney breaks, pending-collapse state and debris effects
remain unfinished. Godot
removes each completed objective and radar marker,
uses the measured cockpit `Gun` emitter, and consumes exact released round,
impact, tank-destruction, sound, text, and voice assets for the bounded
presentation. The exact initial root terrain now includes the released macro
blend, structure shadows, and pine-shadow rules over all 1,481 placements. Its repeating Level
100 detail texture, cube-25 sky, fixed-function
ambient/sun/anti-sun lighting, exponential fog, and renderer-correct final color
transfer replace their earlier placeholders. Copied-runtime state confirms the
released Level 100 terrain path; static analysis fixes its stage order to plain
macro/detail modulation followed by `MODULATE2X` cloud/rotated-detail stages. The
one Level 100 base texture whose released `CTexture` record selects
texture-alpha blending now preserves its lit exterior under transparent texels
instead of exposing the facility interior. Water now uses the
released camera-following 25×25 grid, exact Level 100 height and color, two
animated caustic stages, authored `reflection00` imagery, sun-reflection stages,
and both exact `SURF` shoreline bands. Its active reflection stage uses the
released absolute-world `1/256` transform rather than the inactive advanced
path's animated half-scale transform. Steam disables the wave stage before the
main grid draw; the client applies its measured animation only to the authored
shoreline passes, alongside the camera-height-scaled alpha-tested sun patch, the
bounded sun-glint subpass, the released pass order, and measured animation
rates. There is no additive water pass
(`rebuild/OnslaughtRebuild.Client.Tests/Level100WaterEnvelopeTests.cs` rejects
any `blend_add` draw in the water source). This reconstructs
the bounded active fixed-function path observed on the supported Steam specimen;
it does not claim the inactive advanced path, dynamic scene reflection/refraction,
or general renderer pixel identity. The detail texture uses the released
identity and rotated quarter-scale transforms and observed modulation modes; the exact
moving cloud-shadow texture now uses the released scale, scroll, and modulation.
Core's projectile path now consumes canonical-registry actor identity,
hash-verified mesh binding, active state, full three-dimensional pose/basis and
velocity. The released medium-pulse swept sphere uses BBOX only for broadphase
and deterministically millimetre-quantized projected mesh
topology for contact. Target Tanks retain their four-hit direct
path; Warehouse contacts drive extent-weighted 28-segment
health, the `5.0` core multiplier, core-child/strict-30% terminal tests, and
`Hit`/dying/died facts consumed by the released mission scripts. Segment and
typed effect state is deterministic and hashed. Godot consumes the ordered
Pulse-impact and terminal effect events, including their existing audio and
target-destruction presentation. Tank/Truck meshes remain until their scheduled
physical shutdown. Warehouse and Drone still use whole-target terminal removal;
completed-break versus pending-collapse state and delayed child events
remain incomplete. Detached Warehouse parts, rubble, and retail-random secondary debris
are not yet presented.
Walker acceleration now follows Core's
continuous body yaw; the bounded projectile path shares its yaw and vertical
pitch while jet
translation retains the older eight-way approximation. The slice does not
yet reproduce Steam's dynamic 1/2/4-step terrain patch topology, steep-slope or
wire the available actor contact path into walker movement beyond those two
observed facility envelopes, exact toe-normal alignment or CMC body sway,
resolved Warehouse rubble trajectories,
mesh-part damage variation, retail-random secondary particles/debris, AI, the
remaining weapon roster, facility destruction,
the inactive optional advanced-water path and dynamic scene reflection/refraction,
jet-to-walker presentation, Steam's dynamic
HUD ring and full multi-stage mask/influence-map implementation, general
contacts, other portraits/video, and exact portrait RNG phase,
later mission audio, campaign,
networking, or the rest of the transform model. The camera slice does not yet
reproduce terrain-relative pitch limits, terrain occlusion, camera shake, or later
scripted cameras. The old seeded synthetic targets are gone; Core and Godot
share the four observed retail targets. HUD markers use the shipped radar asset,
not world-space synthetic beacons.
Core embeds the exact Level 100 HFLD, applies Steam's released fixed-point
height sampler, and hashes the resulting walker ground elevation. Godot adapts
that value for the player; static-world objects and projectile effects remain
presentation-grounded. The observed route did not exercise a steep-slope flag,
body tilt, or nonzero vertical velocity, so those behaviors remain outside the
demonstrated slice.

**Visual parity remains unproven.** The current configured frontend measurements
belong to `rebuild/tools/frontend-parity-plan.json`, whose provenance names July 31
and commit `fc07fef6`; reading that configuration is not a fresh runtime comparison.
The earlier July 27 gameplay/frontend scores and correction history remain in Git
and their dated capture records. They must not be presented as today's measured gap.

`tools/score_frontend_capture.py` derives each regression ceiling as
`min(measured + marginPp, 100)` and evaluates the worst sample. The selected plan's
margin is two percentage points. A ceiling is a regression guard, not parity
acceptance, and a run with no scorable evidence reports `UNSCORED`.

The selected plan explicitly leaves six pages unscored. Options lacks matching
reconstruction burst frames; developer and level selection have unstable retail
comparisons; briefing, configuration selection and loading lack a second retail
burst for a noise floor. The current reasons stay with the plan. Options ink-mask
comparison measures text placement only. The main menu's recovered 50-frame
transition does not settle these gaps.

**September 8 deterministic tutorial results.** The cold-start client/Core
harness visits startup, logo, montage, splash, click-to-start, main menu, New
Game, level select, briefing, configuration, loading and gameplay. Its corrected
controller phase fires before actor movement and mission callbacks. The test
driver now aims from that retained launch pose instead of compensating for the
former reversed phase order.

The cold-start harness and its direct-Core control now load the full 44-actor
shipping manifest through the production hash-checked decoder. Its earlier
22-target completion preceded the living-aircraft turn-rate correction below;
that result is no longer the current full-combat outcome.
The direct-Core control uses the same pointer-quantized commands and matches the
complete state hash and pose trace. These are the two comparable inputs in
[the cold-start tests](rebuild/OnslaughtRebuild.Core.Tests/Level100ColdStartTests.cs).
The September 8 signed-basis correction is separately covered by exact tilted-offset/renderer
tests, real materialization and focused Client checks; it does not establish
native flight or visual parity. The authored Flyby and spawned AirTrainer now
start with their physics profile's 3000 milli-life, including restore and render
projection checks. Aircraft vulnerability and complete damage/death behavior
remain open.

Living Planes now retain their full initialized air turn rate. Retail reduces
it to one third only while dying; the former mover applied that reduction to
living aircraft too. The replacement raw free-flight mover retains that rate,
old/current pose, drive, velocity and the ordered guide callbacks. Restored
actor scripts keep the spawn-registration and clock hooks; the pending Hangar
spawn regression first failed without those hooks, then passed with them.
Aircraft event arithmetic and its mode are retained in schema 47.

Cold combat wins. The cold-start route clears the firing range, flies and
lands all three flight legs, destroys the Target Trucks, Moving Targets and the
first airborne wave with the weapons in the order the script hands them over,
and ends the final wave on one of its two released branches, six kills or the
sub-40 % abort. The six-kill assertion that failed from September 12 was a
driver expectation, not a retail invariant (the RE lane's final-wave contract).
The returning-career chain autopilot, on reduced fixture definitions, also
reaches `Won` by input alone. Current ticks, hull and kill counts are pinned in
[`Level100ColdStartTests`](rebuild/OnslaughtRebuild.Core.Tests/Level100ColdStartTests.cs)
and the [full-chain tests](rebuild/OnslaughtRebuild.Core.Tests/Level100FullChainTests.cs),
which also retain the independent naive and trigger-disabled controls; they
are not copied here.

These are synthetic in-process regressions. The driver reads exact health,
poses and terrain visibility; its commands cross the player-input surface but
its perception is omniscient. They do not establish human/native-Godot
playability or retail equality. The complete desktop route remains pending.

The retained [ferry oracle](rebuild/OnslaughtRebuild.Core.Tests/Level100FerryLandingTests.cs)
checks hand-off altitude and the released water threshold; its older sweep
results in [VALIDATION.md](VALIDATION.md) are dated evidence, not a new sweep
following these controller changes. Exact bot endpoint values are sensitive to
input and mechanics. Current claims come from their owning focused tests, not
from old trajectories copied into this page.

The current source tree and release packages do not include retail game assets
or their conversions, other than two registered screenshots used for the app's
own Home and About surfaces — pictures of the game running rather than files
copied out of it. They are listed in
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md)
and the allowance is stated in [`AGENTS.md`](AGENTS.md).
The rebuild materializes the exact currently consumed slice
from a user-provided supported retail installation into ignored local paths.
The remaining asset gap is technical integration and format fidelity.
Read [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) before changing this lane.

## Reverse engineering

The byte-matching decompilation, published as [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), matches all 5,482 retail functions and is
the reverse-engineering authority; its README holds the score, the matched list and the remaining divergences.
Findings reach this repository as prose and specs in [`reverse-engineering/`](reverse-engineering/RE-INDEX.md),
citing functions rather than quoting code.

The Ghidra-era campaign (generations, contract grades, promotion cohorts, the tracked Ghidra checkpoint and
`developer_state.json`) ended with that work. Its records moved on 2026-10-15 to the private repository
`dlprentice/onslaught-re-archive`, byte-exact at their old paths; its figures are history, not current capability.

## Evidence boundary

[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) is the front door to the game documentation.
The decompilation and the retail executable own static released-binary facts; controlled copied-runtime
observations own measured behaviour. Stuart's GPL source owns architecture and implementation evidence; retail
static and runtime differences decide where the Steam release diverged.

## Distribution

The companion has no published release yet; `npm run export:companion-godot -- --platform both` builds Linux and
Windows packages that bundle their .NET runtime. The retired WinUI app's last release, the unsigned portable
Windows ZIP `v1.0.11` (tag `winui-v1.0.11`), is still on the Releases page and is no longer maintained; its
executable patching and safe launch are not in the current companion and are replaced by Onslaught CE. No package includes the retail
executable, the original assets, saves, a Ghidra database or the rebuild client. Repository licenses do not cover
retail game data; future releases keep that user-supplied boundary.

Use `npm run` for the current command surface: `npm test` checks the companion.
