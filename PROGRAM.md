# Execution Program

Status: durable backlog; Linux development phase active; internal preparation complete
Last updated: 2026-10-01 (decompilation continuation integrated; all game rows emit candidates; broader audit unfinished; rebuild and companion paused)
Summary: remaining work, acceptance gates, and completed program items without the execution diary.

The [standing goal](GOAL.md) keeps retail RE, the Godot rebuild, and the Godot
toolkit companion coequal. On September 6 David accepted the baseline and explicitly
resumed the rebuild-led phase below. The historical storage hold no longer blocks its
normal implementation. Save/evidence protections remain; no Windows VM activation,
external archive cleanup, production work or repository split is included.

Use `developer_state.json` → `current_re_authority` as the sole live campaign
selector. Capability claims belong in [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md),
validation in [VALIDATION.md](VALIDATION.md), and database state in
[Ghidra's guide](reverse-engineering/ghidra/README.md). Dated receipts and prior
queue revisions remain in Git and existing evidence owners; do not recreate a diary here.

## Open work

### Byte-matching decompilation — started September 28

David's September 28 goal makes a byte-matching decompilation of the game code the RE
lane's main loop. The source, build scripts and score live in the private repository
`github.com/dlprentice/bea-decomp` (checkout `~/Projects/game-dev/bea-decomp`); its README
owns the score and the matched-function list, and this file keeps only the plan.

- **Toolchain.** Visual C++ 6.0 SP5 under isolated headless Wine prefixes: CL 12.00.8804,
  C1 12.00.8867, C1XX 12.00.8964, C2 12.00.8966 and LINK 6.00.8447, pinned by
  `bea-decomp/config/toolchain.sha256`, with provenance in
  `local-lab/third-party/msvc6-sp5-toolchain/SOURCE.txt`. C2 build 8966 matches the retail
  Rich-header record; the initial SP6 setup is superseded. Flags `/O2 /Ob2 /GX /MT /QIfist`;
  the retail build folder
  `C:\dev\ONSLAUGHT2\` is mapped onto the source folder so `__FILE__` matches; file names keep
  the case retail's strings spell (`Unit.cpp`, `mapwho.cpp`), and a header's string follows the
  spelling of the `#include` that opened it.
- **Judge.** A function counts only when its whole compiled section equals the pristine
  bytes and every relocation lands where the evidence says (own section, annotated callees,
  pooled strings and constants by content, import slots by name, one consistent address
  for everything else).
- **Structure.** Objects are linked alphabetically by file name; unreferenced functions are
  removed and identical ones folded (every empty function is the `RET` at `0040c640`).
  Nearly every object ends with the maths header's constant initializers (288 found), which
  mark object boundaries (`bea-decomp/config/objects.tsv`).
- **Order.** Startup, settings, saves, menus and Level 100 first, then by object file and
  subsystem, dormant code included. Stuart's GPL source seeds the 26 files it shares with
  the retail build; each divergence is recorded in the decomp README with its evidence.
- **Promotion.** Names and prototypes a match proves go to Ghidra in batches through the
  promotion gate. New source matches do not automatically change the live database.
- **Name evidence.** A match proves a body, not its name, and most of the game's files were
  never released, so their names are the reconstruction's labels. A name goes to Ghidra only
  when Stuart's released source ties it to the body: the same-named released file defines
  it; a matched function compiled from a released file calls it by that name, so the
  relocation check puts the call on this address; or a released header declares it as a
  virtual whose slot the matched vtable fills with this body. The method name must be
  written in his text. Where it does not name the class (a global object, a macro, an
  unreleased header), the comment says the class qualifier is the reconstruction's; a
  caller that exists only in retail or in reconstructed code backs nothing. A body shared through
  identical-code folding keeps a shared name. A reconstruction label may go in as a
  comment that says it is one, never as the function's name.

Current state (October 1 continuation). Codex reproduced the five-peer handover baseline, then integrated
the spawner update, its name-to-unit lookup, the Sentinel firing update, Mine update and Unit preparation
with complete section/relocation matches. The Euler-angle constructor was already emitted exactly but lacked
its annotation; that coverage omission is corrected. The confirmation-menu event handler and central Unit
movement update now match too. A shared float-angle wrapper closes the camera update and infantry
initialization, with the complete score retaining every earlier matched symbol.
The tentacle spline, Wingman startup and normal-squad member-transfer routine now also match their
complete sections and relocations. The last creates a squad and transfers an existing unit; its inherited
"SpawnMembers" label did not establish new-unit spawning. These interfaces are reconstructed, not recovered
original source text or runtime acceptance.
Closest-edge selection, desired weapon pitch, and both remaining third-person camera queries now pass
fresh complete-section/relocation checks. The geometry correction preserves addition association; the
camera corrections preserve returned temporary lifetimes. A separate
[contact-normal experiment](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__Hit.md)
first exposed decision differences caused by the candidate's float arithmetic at the slope threshold;
the complete-body correction and native readback below now close that reconstruction defect. These
are authored numerical boundaries, not observed gameplay contacts.
Cached mesh-pose composition and triangle-prism admission now also pass complete section/relocation checks.
The former corrects the order of two orientations. Separate original-code comparisons corrected the
mesh/sphere caller's lost accumulated-hit flag and segment-hit numerator order; those full bodies remain
unmatched. The mesh producer can return count two with the third normal untouched or already replaced by
a blocking third contact. Actual triangle generation and callback reachability remain open.
The [weapon contract](reverse-engineering/game-mechanics/battle-engine-weapon-stores.md#aim-transform--october-1-recheck)
now records relative aiming limits based on barrel velocity and the observed retained-height fallback when
no pitch is selected. The source corrections preserve existing exact matches, without claiming complete
candidate equivalence or observed gameplay.
Walker mouse scaling, dive-bomber firing and initial storage-device selection now also match their complete
sections and relocations. Air/Carver guidance and virtual-keyboard layout initialization subsequently close
three more complete bodies. A separate [projectile-distance recheck](reverse-engineering/contracts/round/CRound__SpawnConfiguredProjectile__004db150.md#squared-distance-comparison--october-1-recheck)
corrects arithmetic order and reproduces a native x87 branch difference at explicitly selected 24-bit
precision; that full function remains unmatched and live precision/reachability are unmeasured.
The [control-binding contract](reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md#reconstructed-key-capture-comparison--october-1)
now also records 482 agreeing key-capture cases and ten failure controls, using actual helpers with explicit
disabled-sound/C-locale fixtures. The full key-capture function remains unmatched; physical input and
serialized settings compatibility are not established by those cases.
The [Unit contact handler](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__Hit.md#exact-reconstruction-correction--october-1)
now matches its entire section and all relocations; its earlier 13,839 native threshold cases have no
corrected decision differences. The [startup precision recheck](reverse-engineering/contracts/render-platform/CD3DApplication__Initialize3DEnvironment__0052af00.md#precision-setup--october-1-instruction-recheck)
confirms that retail omits the Direct3D preservation flag. PC24/nearest after creation is justified by
the API contract, while live control words and reset behavior remain unmeasured. The [sphere-response recheck](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#sphere-response-arithmetic--october-1)
then corrects squared-distance association, removing all 148 observed PC24 movement differences in
4,512 native cases. That full body remains unmatched; the previously discrepant sphere line body is
now exact, and all earlier matches are preserved.
The [cylinder-response recheck](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#cylinder-response-arithmetic--october-1)
corrects radial rounding: 462 native cases improve from 84 differences to eight, with no new
discrepancies. Initial-Z precision at translated origins remains a demonstrated open defect.
The cylinder line body is already exact. The Goodies requirement-text builder now also matches
its whole section and every relocation through the existing direct PC text lookup; menu rendering
acceptance is separate.
The [options-list recheck](reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md#options-list-title-return--october-1)
corrects the callback snapshot and now closes the entire renderer's section/relocation match
through natural local lifetimes. Bounded null-title and text-measurement cases retain explicit
reachability, rounding and device limits. The radio-message constructor also matches exactly;
portrait rendering and audio remain separate acceptance work.
The [imposter quad](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#imposter-quad-coordinates-and-precision--october-1)
now matches its entire section and all relocations after correcting reversed V coordinates
and premature rounding. Its enclosing renderer now also corrects matrix operand order and
centre-offset association, with bounded native witnesses. The font glyph stream and demonstrated
V-inset rounding defect are corrected within the limits of the [font contract](reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md#font-glyph-stream-and-v-inset-rounding--october-1).
Full rendering and live visual acceptance remain separate.
The [retained debug-arrow recheck](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#retained-debug-arrow-arithmetic-and-indices--october-1)
corrects a component-rounding boundary and records an unwritten retail index without guessing its visual effect.
The [particle-parser recheck](reverse-engineering/binary-analysis/tokenarchive-semantics-2026-08-11.md#allocation-and-scan-format-recheck--october-1)
corrects a reference-allocation request and the old integer-format description. The
[buffered-read comparison](reverse-engineering/binary-analysis/functions/DXMemBuffer.cpp.md#buffered-read-comparison--october-1)
finds agreement only within its explicit memory/refill provider model; real Windows I/O remains untested.
The [ballistic caller experiment](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#weapon-b-ballistic-height-and-prediction--october-1)
now binds prediction to horizontal range while height uses current Unit positions, and confirms the
ballistic return skips the world query. These are 84 original-code calls with explicit providers;
full candidate equivalence and live firing acceptance remain open.
The cockpit composition-order correction has bounded original-code evidence but leaves its two bodies
unmatched. A damage-report index is now snapshotted before a virtual query, as retail does; the affected
subblock is ordinarily unreachable under stable memory, and only an explicit isolated intervention exposes
the former difference. The existing damage contract records that limit. All integrations preserve earlier
exact matches. The private README owns the current counts.
`bea-decomp` main's README owns the score, matched list, findings and failed alternatives; per-function notes
sit above each near miss in the source.
- **What remains.** Every game-function row now has an emitted candidate; the remaining bodies compile but
  differ. The README's "Open near-misses" opens with where the work stands:
  - the remaining near misses by class: inline decisions, same-call size differences, instruction order or layout,
    and zero normalized shape distance (which can still hide different branch targets);
  - what to try first in each class;
  - each lane's leads, with measured states.

  The peers' full notes, patches and inline tables are in `bea-decomp/local-data/handover-20260930-lead/`.
  The README's "Findings" start with VC6's inline decision, which Peer A decoded from c2.dll and validated against
  the compiler's own log:
  - each function has a `max(1000, 2 × size)` budget;
  - callees of size 40 or less are free;
  - nested sites split what is left;
  - each source edit has a measured size cost.

  They then cover retail's maths header bracketing each product in its sums, which settled the term-order cluster
  on September 30. The linker's 32 import thunks at
  `0055d5e0` are library code: jump stubs into the game's DLLs (DirectSound, AVIFile, zlib, Ogg Vorbis,
  version.dll), verified against the import table and counted apart from the game functions.
- **Next lever.** Follow the compiler's actual dependency and lifetime differences on the remaining reorder
  rows. A bounded scheduler decode now reproduces the 81-IR-node region limit, unsigned ready-list ordering
  and default priority formula; lead controls retain every emitted function section and relocation in the
  inspected objects. This led to a concrete shared-header result: VC6's float `atan2f` wrapper in Azimuth
  moves the camera's final matrix multiply into the copy-setup scheduling region, reproducing retail's
  instruction order. Infantry initialization also matches, with no prior exact symbol lost. The earlier
  Reset/sprite cases remain unresolved. This is not a complete scheduler model or a recovered retail
  dependency graph; the private README owns the evidence and limits. The full graph builder and register
  allocator remain open. A bounded Mine trace now locates its pointer/reference register difference before
  scheduling: the reference carrier receives EAX earlier, while the pointer carrier receives EDX later;
  all scheduling-region orders remain the same. The lead reproduced the frozen compiler observations,
  without inferring a general allocation rule. In parallel:
  - run `tools/permuter/readbatch.py` and `tools/scans/readform.py --noreads --inplace` over the rows;
  - run the `tools/inline` searches over the call-list rows.

  An edit counts only when the original plausibly had it; budget-only padding stays forbidden.
- **Judge and tools.** A compiled section shorter than retail's body cannot match, vtable identities
  join the relocation-conflict check, and the DirectX and VC6 include trees are pinned.
  `tools/equiv.py` is a bounded differential falsifier: both bodies run at the retail address in
  separate emulators, and faults, unresolved dependencies, unsupported ABIs and incomplete coverage are
  inconclusive; randomized agreement never closes a body. The inline tools, the permuter
  and readform families, the near-miss scanners and the fleet scripts that merged five lanes
  (`tools/fleet/README.md`) are in `tools/`, listed in bea-decomp's `AGENTS.md`. The inline tools' logging copy
  of C2.DLL is rebuilt from the pinned toolchain into ignored `local-data`. The harness compiles and compares
  objects; it does not link a replacement executable, and the original project, PCH and link settings remain
  unknown.
- **Behaviour the matching corrected in the reconstruction.** Retail's bytes overruled the draft source in five
  places:
  - at top speed, `CDropship::Move` flies along its heading at its current speed;
  - CMCMech ProcessMovement tests `force`;
  - `CHud::RenderTargetIndicator` uses `stricmp` on the Thunderhead mesh, which takes the imposter while every
    other target lights and turns;
  - CMechGuide Unknown3 replans only when its destination moves;
  - SMechShared's constructor clears its five tables.

  bea-decomp's README ("A near miss can be a wrong reconstruction") and commits `50f5a0b`, `9747e43` and
  `deb9d71` hold the evidence. Whether the rebuild's contracts carry any of the draft behaviour has not been
  checked.
- **Contracts the decompilation corrected (September 30).** Static reads and bounded original-code
  cases; none establishes live presentation or player acceptance:
  - input and settings: [mouse recentering constant](reverse-engineering/source-code/frontend/controller-system.md#september-30-mouse-recentering-byte-match),
    [options reader](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#september-30-reconstructed-options-reader-comparison);
  - weapons and aiming: [current-mode lookup](reverse-engineering/game-mechanics/battle-engine-weapon-stores.md#current-mode-lookup--september-30-recheck),
    [call binding](reverse-engineering/game-mechanics/battle-engine-aiming.md#september-30-call-binding-recheck),
    [cockpit composition order](reverse-engineering/game-mechanics/battle-engine-aiming.md#cockpit-composition-order--september-30-recheck);
  - meshes, rendering and collision: [named-mesh interface](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#named-mesh-render-interface--september-30),
    [segment-contact precision](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#segment-contact-precision--september-30),
    [segment approach](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#segment-facing-and-approach--september-30),
    [bone payload dimensions](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#serialized-bone-payload-dimensions--september-30),
    [render-method setters](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#render-method-setters-have-different-acceptance-effects--september-30),
    [emitter and effect parts](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#emitter-and-effect-part-pointers--september-30),
    [trail points](reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md#trail-point-count-and-arithmetic-order--september-30),
    [device startup](reverse-engineering/contracts/render-platform/CD3DApplication__Initialize3DEnvironment__0052af00.md#device-boundaries-and-cleanup--september-30);
  - gameplay and interface: [unit damage](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__ApplyDamage.md),
    [free camera](reverse-engineering/binary-analysis/functions/game.cpp/CGame__ToggleFreeCameraOn.md),
    [relaxed-squad centroid](reverse-engineering/game-mechanics/spawner-squad-cycle.md#relaxed-squad-centroid--september-30-recheck),
    [scale-menu rendering](reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md#generic-scale-menu-rendering--september-30),
    [Goodies fractional text positioning](reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md#goodies-text-preserves-fractional-y--september-30).
- **Ghidra.** Name promotions `decomp-names`, `decomp-names-2` and `decomp-names-3` (evidence in
  `local-lab/…/re-audit-20260926/decomp-names*/`; the batch-3 folder holds the caller-witness and
  shared-body screens to reuse). A fourth batch waits: only about eight new names have a released
  caller under the rule above, and a wider batch needs another naming rule first. Open flow defect:
  Ghidra treats `0042c750` as non-returning, so `004b7d90`'s body omits the `ret` at `004b7e0a`.
- The six lane worktrees (`bea-decomp/.worktrees/{frontend,world,units,engine,peere,lead}`) are clean and merged.
  The 110 scratch trees were removed after their diffs were saved (deletion queue, September 30). Codex's helper
  worktrees (`bea-decomp/.worktrees/codex-*`) retain frozen, ignored experiments; do not replay their commits or
  delete their evidence.
The recorded live authority remains selected by `developer_state.json`. Do not replay the old
prepared-cohort queue or mistake isolated original-code probes for full game acceptance.

### Dedicated RE lane — current continuation

David resumed this dedicated RE task on September 22 from the preserved pause.
The interrupted language-cleanup control had watched the wrong input-state
address. Original instructions resolve that arithmetic error; the corrected
experiment now passes 26 cases while retaining the old address as an unchanged
control. Failed runs remain in the existing private owner. No retail body was
changed to make the checks pass.

Separate tasks own rebuild and companion implementation. The working branch is
`codex/retail-re-20260919`. Current database and recovery identities remain in
`developer_state.json` → `current_re_authority.latestLiveGhidraState`; use those
pointers rather than selecting a project by date or database number.

The resumed investigation confirmed CLIParams ownership of the initializer at
`004239f0`; its former Unit AI name is corrected through the
[one-row preservation/readback workflow](reverse-engineering/ghidra/README.md#cli-initializer-ownership--september-19).
Four isolated original-code cases establish its bounded defaults and preserved
memory. The complete [parser contract](reverse-engineering/binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md)
now records all 25 comparisons, sequential argument consumption, the initial
zero windowed guard, and directory/logger-filename side effects. Retail startup
acceptance remains separate from the isolated parser execution below.

The follow-up passed 47 isolated cases through the unchanged parser and native
CRT conversion code, with OS/printf boundaries intercepted. It identified ten
absolute reads of the developer selector, corrected its old frontend-state
identity, and separated autoconfig/cheat-query admission and the frontend
startup override from `-level`. No active consumer of either trace-request
field or later deliberate developer-selector writer was identified. That is
bounded static evidence, not proof against computed or external writes.

David's current priority is to recheck save files, settings and startup as one
compatibility chain. Existing notes, prior agent work and this lane's earlier
conclusions are fallible leads. Reproduce consequential claims against selected
pristine bytes and controlled execution before carrying them forward. Keep the
full-retail mandate and separate implementation owners.

The [save/startup contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md)
now separates the startup reader, normal menu load and writer, active settings,
serializer, and campaign reset. Original-code controls establish read/write
filename differences, menu forwarding into the next boot, binding/preset effects,
active-language ownership and volume application. Six preserved language files
also pass bounded original parsing and lookup. File/heap/device boundaries
remain explicit; these results do not establish complete retail startup.

The audio reset/bank controls resolve caller ordering, init-return admission,
shutdown versus Stop, Level 100 music restoration and early path caching that
can suppress a same-path retry after a failed or skipped bank load. Actual
platform services, lifetime effects and playback remain open; the direct sample
decode/quality path now has the bounded original-code evidence below.

Fifteen native Load/Save/reinitialize/Load/Save cases now include direct handoff
of the first serializer buffer. Both gold controls preserve all 10,004 bytes;
private derivatives distinguish progress-flag writes, counter normalization,
preset restoration and preservation-mode volumes. Linux generated-copy readback
is checked; retail file publication and full process restart are not. The
intervening career static initializer must not be confused with Blank.

Seventeen extended startup cases now execute Blank's original Goodie
recomputation with descriptor initialization. The final canonical reset has nine
instruction-state Goodies, no unlocked entries, preserved settings and unused
record storage. This closes the former Goodie hook for the reset route, not the
complete unlock table or its UI. Exact commands, artifacts and limits belong in
[VALIDATION.md](VALIDATION.md#original-load-save-and-reload-controls--september-20).

Nonnull language cleanup now executes the original outer/nested menu teardown,
list recycling, resource decrements and monitored-pointer clearing. Composed
SetLanguage calls retain old text throughout teardown, clear the outer owner,
then replace the active buffer; repeat selection copies again. Heap operations
and optional child destruction remain explicit boundaries. The
[cleanup contract](reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__SetLanguage.md#nonnull-cleanup-before-text-replacement)
and [saved controls](VALIDATION.md#original-nonnull-language-cleanup--september-22)
record exactly what this establishes.

Direct sample controls now execute the original cached reader, buffer factory,
ADPCM decoder and quality converter with two real English-bank records. They
expose different rounding in requested versus written sizes, and distinguish
returning a sample object from successfully decoding it. The current materializer's
pure decoder matches both complete high-quality PCM outputs. This does not
establish all-bank loading, real device outcomes or playback; see the
[sample contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-sample-decoding-and-saved-quality).

The outer caller now has original-code reuse/list/name-copy controls, including
insertion despite a supplied device-create failure. Its filename-route stub and
working buffer loader contradict inherited semantic labels; the
[caller contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#outer-sample-admission-and-registration)
records the evidence; the [four-function Ghidra correction](reverse-engineering/ghidra/README.md#sample-loading-metadata--september-22)
now preserves it in the working database with unchanged types and storage.
Original destruction now has 23 standalone controls and 11 composed failed-load
controls. A zero payload read removes a reused sample; old storage and sample
buffers are released once, while failed fresh creation preserves existing samples
and events. Heap reclamation, device lifetime and mutating callbacks remain
intercepted. Original bank loading, file Open/refill/Close and decoding now pass
11 cases: all 164 English samples, reload identity/duplication, quality changes,
tag/trailer admission and supplied device failures. The materializer's pure
decoder matches every complete high-quality output. The
[bank contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#complete-original-bank-loading-and-reloads)
separates parser, publication and device success. Nine subsequent original
Load/Save/reload controls expose a routing distinction: changing language and an
audio word together preserves the cached old bank path, while language-only
refresh replaces it. The same serialized result fixes the path on the next Load.
Device Init and the final bank entry remain explicit boundaries in this paired
control. Separate original Init controls now establish device-index normalization,
capability-derived state, enumeration and failure cleanup under supplied API
responses. Ten original outer-manager controls now establish pool/registration
setup, timer sampling and the caller-owned initialized byte: failed device Init
clears that byte without undoing setup. SFX parsing remains a boundary. Eight
composed Load/reset/Init/Save controls now prove that device-index normalization
can persist even when subsequent device creation fails; zero admitted devices
instead preserves the saved index. Failed reset retains the initialized flag,
allowing the second Load to request a language-bank refresh with null device
pointers. Separate original-bank controls now reproduce a null-device dereference
before the sample factory's COM error check; a valid zero-count bank avoids it.
Next connect this bank dependency to the composed route without replacing the
failed manager state, and retain the full startup/save compatibility objective.
Actual device/playback and cold-start acceptance remain open. The
[coupled contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#coupled-language-and-audio-settings-routing)
and [device/save contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-device-effects-during-load-and-save)
record the exact prior state and limits.
Keep original-code evidence distinct from decoder self-tests,
retail file durability and player acceptance. The retained AppCore sensitivity
clamp and display-mode naming discrepancy are implementation-consumer findings;
this RE task does not own those production changes.

The rebuild's cold full-combat route follows the
[final-wave contract](reverse-engineering/game-mechanics/level100-final-drone-wave.md)
and has won since September 26: the old abort was a designed retail branch, and retail adds friendly turrets after
Help Player and the jet Missile Pod. An original-code control shows activated
turrets can select the script-spawned enemy drones. The turret aim, Missile Pod
lock, crosshair and auto-aim refresh, seeking-round, round-lifetime and per-round
draw laws are static contracts there.

The [Level 100](reverse-engineering/game-mechanics/level100-construction-order.md)
and [World 110](reverse-engineering/game-mechanics/world-110-construction-order.md)
construction-order contracts give:
- the load order;
- every construction draw and queued event;
- what the first event flush delivers and draws;
- World 110's transition from a Level 100 win, and its player start.

[Waypoint paths](reverse-engineering/game-mechanics/waypoint-paths.md) and the
dropship [flight](reverse-engineering/game-mechanics/dropship-flight.md) and
[landing](reverse-engineering/game-mechanics/dropship-landing.md) contracts cover the
U-17's route and retreat and the World 110 landing craft: flight, `Land()`, unloading
(25 Light Gun Tanks and 20 Muspell Grunts per full craft), take-off and removal.

Every Level 100 and World 110 question the rebuild lane has sent is answered there,
or recorded as an open question with its cheapest falsifier. Still open:
- a copied-runtime log of shared draws and queued events, to confirm the static
  order from load through the first frames of both levels;
- which arm World 110's units take at their first think;
- composed runtime controls of the final-wave laws;
- a copied-runtime log of a landing craft's speed, descent and unload counts.

Preserve the aircraft/weapon continuation: pool initialization precedes logger
resets after parsing; arbitrary warning state, enabled-logger callbacks and
complete-shot RNG remain unresolved.

The RE record audit corrected ten wrong saved labels in the working project on
2026-09-26 (cohort `label-audit-20260926`, db.18658; see the
[Ghidra README](reverse-engineering/ghidra/README.md#re-audit-label-corrections--september-26)):
`0042efd0` `CWorldPhysicsManager__InitUnitRecordDefaults`, `00509c80`
`CWeapon__GetActualMaxRange`, `004f8140` `Mat34__SetFromEulerUnits4096`,
`0040c2e0` `CBattleEngine__WeaponFired`, `0040c340` `CBattleEngine__RecoilWeapon`,
`00407940` `CBattleEngine__AddShockShake`, `00407a50` `CBattleEngine__UpdateRotation`,
`004f99b0` `CUnit__StartPlayingInitNoise`, `00459810` `CFEPDevSelect__SetCurrentCard`
and `00465f10` `CFrontEnd__ctor`. `00407310` `CBattleEngine__DisplayLock` was
queued but is the source name (`BattleEngine.cpp:980-993`). The tracked
2026-08-31 name table is older than the working project; check the live export
before calling a label wrong.

The second label cohort (`label-audit-2-20260926`, applied live on 2026-09-26; see the
[Ghidra README](reverse-engineering/ghidra/README.md#re-audit-label-corrections-second-cohort--september-26))
corrected eighteen more labels from the bytes, among them `CCockpit__AddShockShake`,
`CPlayer__SetIsGod`, `IScript__FireArrivedEvent`, `IScript__UpdateWaypointFollowing`,
`CBattleEngine__GetImportance`, `CBattleEngine__CanBeLocked`, `CInfantryUnit__Damage`,
`CExplosion__Hit`, `CMonitor__dtor_base`, `CComponent__RefreshCachedTransform`,
`PCLTShell__D3D_SetTexture` and `CRenderMethod__ctor`. The notes that cited the old
names were updated, and three notes named after disproved labels were renamed.

The third game-label cohort (`label-audit-3-20260926`) is now live, with its
independent POST recovery restored and reopened successfully. The
[Ghidra record](reverse-engineering/ghidra/README.md#re-audit-label-corrections-third-cohort--september-26)
contains the exact scope and recovery identity. It corrects `CVBufTexture__ClearOut`,
`SYSTEM__Init`/`Run`/`Shutdown`, `CMonitor__dtor_thunk`,
`CComplexThing__SetThingType`, and `CActor__IsOnGround`/`IsOnObject`.
The missing SYSTEM header does not establish a class name; the destructor thunk
does not prove linker folding; the contact predicates return x87 C0, including
masked unordered comparisons. Zero buffer counts retain a zero capacity target.
Two BattleEngine contracts now resolve their contact callees and the
`GetImportance` return values; this is static evidence, not player acceptance.
The first sealed rehearsal was retained after review found ambiguous Init branch
wording. Fresh PRE, corrected seal, repeated rehearsal/controls and live recovery
passed; no prototype or body changed.

The library pass (audit step 2) named the statically linked library code in two cohorts, both live
([Ghidra README](reverse-engineering/ghidra/README.md#re-audit-c-runtime-library-names--september-26)).
`tools/re_lib_match.py` compares every function of pinned static libraries with the pristine bytes,
relocation fields masked, pools what each relocation implies, and checks import slots against the PE
import table; an independent `llvm-readobj`/`objdump` checker re-derives every match, count and member
claim. `library-d3dx-20260926` named 1,139 functions (the D3DX code in `0x00574270`-`0x005be622`, 1,112 of
its 1,114 decided, with 26 runtime functions and the global `operator_new`/`operator_delete` it calls).
`library-crt-20260926` named 370 more: 351 VC6 `LIBCMT` runtime functions and 15 fragments that saved
boundaries split off them, DxErr9's `_DXGetErrorString9A`, two D3DX corrections and `WinMain`. Of the 462
functions in the runtime's ranges (`0x0055d6a0`-`0x0056eb50`, `0x005be622`-`0x005d0f10`), 367 are named by
it, 85 already carried a proven name (listed as verified, not renamed), and 10 stay open: three bodies
that several library functions share identically (`0x0055dbe8`, `0x0055dcb0`, `0x0055e3ea`), five with no
SP6 match because the game links an older runtime build (the `asin`/`acos`/`pow` cores, `0x0055fc35`,
`0x0056c78a`), and the import thunks `Direct3DCreate9` and `DirectInput8Create`.

Of the 391 `CFastVB__` labels: 326 were D3DX code (named); 6 are the game's `FastVB.cpp` code
(`0x0051a270`-`0x0051a6a0`) and 2 their unwind funclets (step 3); 57 are NVIDIA's NvTriStrip with its STL
containers, now corrected as part of the 72-function cohort below.

The [NvTriStrip cohort](reverse-engineering/ghidra/README.md#re-audit-nvtristrip-library-identities--september-26)
is live, with independent POST recovery restored and reopened. Its 72 structural
identities distinguish the linked library and VC6 STL from game classes. These
are not byte-identical compiled-library matches. Pristine instructions establish
four-argument GenerateStrips and CreateStrips interfaces, two-byte retail index
storage and 24-byte faces; the later reference has different interfaces and a
fake-face field. The former triangle-equivalence predicate instead returns an
unmatched vertex index or -1; the supposed degenerate-output flag is cache size,
initially 16. Fifteen living contracts and the PrimitiveGroup constructor note
now state the re-derived behavior and limits. Prototypes, bodies, instructions,
types and all non-target function rows are preserved.

The first sealed rehearsal remains in `library-nvtristrip/rejected-v1/` because
FindOtherFace's comment omitted the possibility of a null selected face pointer.
The corrected seal repeated PRE, rehearsal, refusal controls and review before
live application. Its source graph has 69 compatible edges and two exact
return-size exceptions; the 37 absent/transitive-call notes are comparison
limitations, not 37 proven behavioral differences. This is no runtime/rendering
acceptance claim.

The three prepared cohorts are now promoted. Their receipts remain under
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/`; each reads its
predecessor's POST through `cohort_chain.py`.
The [library-comment cohort](reverse-engineering/ghidra/README.md#re-audit-verified-library-comments--september-26)
corrected 191 evidence comments and tag sets without changing any names,
prototypes or code bodies. It re-grounded 60 previously unaudited comments,
refreshed 129 changed library proofs and documented two further import thunks;
1,376 already matching comments were left alone. Independent LLVM/GNU checks
covered 1,542 admitted code comparisons, 118 data sections, 14 layout assertions,
15 complete folded-alias comparisons and three import thunks. All nine live
exports equal the separately reopened rehearsal; all 8,140 non-target function
rows and six protected exports are unchanged. Fresh PRE recovery, five no-write
refusal controls, independent review and independent Archive A POST restoration
passed. These are static identity/evidence checks, not ABI or runtime acceptance.

The matcher fixes behind this cohort have 31 passing focused tests. Ownership
now checks both available section/offset bounds and excludes ambiguous/folded
anchors. Alias evidence distinguishes compatible complete bodies, typed names
at one COFF entry and reference-only leads; later evidence can withdraw aliases.
The first 190-row seal was rejected before live application because it falsely
described `_wcsdup` as byte-identical to `_strdup`. Root reproduced their different
lengths and character-width arithmetic. That seal and rehearsal remain in
`library-verified/rejected-v1/`; the replacement repeated the full gate.

The [keyboard recheck](reverse-engineering/binary-analysis/cpccontroller-vtable-semantics-2026-08-11.md#september-26-keyboard-recheck)
corrects four saved prototypes/comments/tag sets through the full gate. The
three virtual key wrappers have an ECX receiver, one explicit key and an integer
EAX result; the raw release helper returns an unsigned byte in AL. The old
held-state description of the release table was wrong. Twenty-seven isolated
original-code cases (135 operations) distinguish remembered presses, duplicate
cache entries, full-cache behavior, array clears and message-pump reset paths.
Clearing arrays does not clear the remembered-key list, and the pump can return
without resetting it. Source's extra pad argument does not belong in these retail
interfaces. All names/bodies and 8,327 non-target rows are preserved; the live
readback matches rehearsal and independently restored Archive A POST recovery.
Real Windows events, physical input and complete runtime acceptance remain open.

The [startup identity cohort](reverse-engineering/ghidra/README.md#re-audit-startup-identities--september-26)
now corrects four names/comments/tag sets: the command-line string parser,
derived CPCController constructor, font initializer and sound-device initializer.
Their existing interfaces and bodies are preserved. The font filename is
`font22.512.tga`; the debug font has its own RTTI identity, and retail clears the
Xbox slots. Sound setup uses 64 slots and quality-dependent PCM settings; its
signed index check handles only indices at or above the count. The numeric
source-line overlap with PlaySound was a false lead. The LoadLevel consumer
note also corrects the three constructor arguments and its `0.5f` field value.
Fresh PRE, rehearsal, five no-write controls, independent review, exact live
readback and independent POST recovery passed. No new retail startup, rendering,
physical-device or audible acceptance is claimed.

The [Damage/shake comment correction](reverse-engineering/ghidra/README.md#re-audit-damage-and-shake-comments--september-26)
is live and independently restore-proven. Damage's name is correct; its old
augmentation/life/time offsets were transcription errors, while the retained
Level 521 observations already contained the correct map. Zero/negative input
skips the positive block, not the common tail. Forty-one isolated original-code
cases now bound damage/repair, late invulnerability restoration, ordered shield
comparisons, shake replacement and the distinct game/CRT RNG streams. Death and
thread-data provision remain explicit substitutes; no full-game acceptance is
claimed. The cockpit's integer parameter is now corrected to a float through a
separate one-function ABI cohort, with its original storage and locals preserved.
The mechanized virtual-method batch below now advances the name audit;
retain the grade-return finding below for a consumer-focused ABI cohort.

Step 3 uses `re_source_graph.py map-names` to build an explicit spelling-only
candidate map, then `check` and `re_name_evidence.py audit`. The fresh pass
maps 472 unambiguous candidates, checks 650 call edges and retains 18 graph
contradiction leads. It withholds ambiguous overloads and saved names; a
compatible graph alone no longer verifies an identity. The whole game-name
heuristic output is 78 support leads labelled `verified`, 53 contradicted,
931 existing structural placeholders and 3,556 unsupported. These are
instrument outputs, **not promoted audit dispositions** or completion counts.
The earlier 148/65/931/3,474 result used weaker logic and is historical.

The corrected model matches each RTTI holder's slot and composed fixed
subobject offset. A folded no-op can belong to new derived slots as well as
inherited ones; virtual-base offsets are withheld. Source candidates retain
same-arity overload ambiguity rather than selecting the last definition.
Identical const/nonconst bodies remain ambiguous, and inherited-slot pruning
cannot contradict a derived holder whose override may have folded. Graph
inputs pin source files, live export and producer tools; rows for a different
source identity or an unselected overload cannot contradict the saved name. Scalar
`WCHAR` and declared enums do not acquire invented result pointers; unknown
aggregate return ABIs remain unresolved. Consequently the previous grade and
`CGame__RunLevel` stack-pop objections were tool errors. The grade's separate
AX/receiver metadata error is independently established below.
The accepted tool pass and stale-producer refusal are retained in
`local-data/test-runs/re-audit-20260926/step3-shake-post/` (`*-v4` outputs).

The [Thing-family virtual-identity cohort](reverse-engineering/ghidra/README.md#re-audit-thing-family-virtual-identities--september-26)
now promotes **205 names, comments and tag sets** through the preservation gate.
Twenty-nine independently reviewed anchors from source declarations, pristine
instructions and script/virtual call sites propagate across 1,677 RTTI table
uses and 298 distinct function targets. Saved names are not alignment inputs.
The promotion changes no prototypes, storage, locals, types, instructions or
bodies; all 8,126 non-target function rows remain equal. All nine live exports
equal the separately reopened rehearsal, and independent Archive A POST
restoration passed. The tracked checkpoint is unchanged.

The admission rules are executable, not a request for 205 separate manual
investigations: a reviewed anchor pins the source interface and retail slot;
every mapped use must agree with fixed RTTI inheritance and subobject offsets;
all aliases and naming owners must be accounted for; and the complete saved
body must pass decoding, branch, return-cleanup and supported tail-stack checks.
Contradictory slots, unmapped aliases, ambiguous owners or unresolved stack
behavior are withheld. Independent review checked the method, every flagged
case, all anchors and representative overrides; root reproduced the witnesses
and all mapped table words. These checks prove the admitted interface identity
within their limits, not full ABI or behavioral correctness.

The [65 kept-name dispositions](reverse-engineering/ghidra/README.md#re-audit-verified-thing-family-identities--september-26)
are now promoted as comments/tags only. Fresh alignment and independent review
cover 727 table uses and all 7,962 target instruction rows. Five stale claims
are corrected or qualified: Carver's already recovered Init boundary, two
misidentified table starts, ComplexThing's nonzero-mode branch, and an unproven
inference about repeated Thing initialization. All names and prototypes remain
unchanged. Live/rehearsal equality, five no-write refusals and independently
restored Archive A POST passed. The 65 targets add 63 unique kept-name
dispositions; two were already counted as corrected by the third label cohort.
The 28 unresolved targets remain outside the completed counts.
The separate complete-header route requires exact slot counts and unambiguous
single inheritance. Its 26-class / 64-target candidate report yielded the
selected InitThing/Engine interfaces below; candidates outside the declared
cohort remain unpromoted. Missing macro/base definitions, conditional declarations
and overload ordering remain exclusions; CThing's missing interface headers
are bridged only by individually established slot anchors. Controller layouts
with 15 source slots versus 18 retail slots remain unresolved.

The tools now have 57 passing focused tests, including adverse decoding,
backward tail-branch, argument-width and unsupported-ABI cases; the cohort
framework has 93 passing tests.
The accepted report is `local-data/test-runs/re-audit-20260926/step3-shake-post/vtables-v6.json`;
the full gate is under `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/thing-virtual-identities/`.
Twenty-one existing notes had current identity assertions refreshed; their
remaining semantics and saved prototypes are not thereby audited. This refresh
also corrected Sentinel's misidentified table starts and shifted slot numbers.

The [header-interface cohort](reverse-engineering/ghidra/README.md#re-audit-header-interface-identities--september-26)
now promotes **16 names/comments/tag sets**: 15 initializer Copy/Load identities
and case-distinct `CDXEngine::ShutDown`. Seven source/byte anchors, all 27 known
RTTI uses and complete target instruction bodies were reviewed. Five kept
Engine names and the shared Sphere/Unit Copy body were not changed. Four draft
comment errors were caught, preserved under `rejected-v1/`, corrected and
resealed before live application. Exact live/rehearsal equality, five no-write
refusals and independently restored Archive A POST passed. All 8,331 projected
names match the live readback; the tracked checkpoint remains unchanged.

The [initializer contract](reverse-engineering/game-mechanics/world-initializer-copy-load.md)
is backed by 64 isolated original Copy cases and 1,288 original-loader cases
(1,072 distinct loader inputs) using an authored full-read interceptor. It
separates selective copies, Squad overloads, versioned reads, untouched fields
and signed-byte string wrap. Spawner loading remains static; original-reader
short/zero reads, constructor defaults and full-game loading remain untested.
The private copy/load receipts are under
`local-data/test-runs/re-audit-20260926/initializer-copy/` and `initializer-load/`.

The [Controller/Engine review](reverse-engineering/ghidra/README.md#re-audit-verified-controller-and-engine-identities--september-27)
retains **14 more verified names** and updates their comments/tags. Twelve
explicit anchors cover all 15 RTTI uses and 643 instruction rows. The
[Controller contract](reverse-engineering/binary-analysis/cpccontroller-vtable-semantics-2026-08-11.md#september-27-joystick-and-recording-recheck)
distinguishes 18 retail slots from 15 source slots, signed upper-only pad guards,
RightY flag ordering, exact stored scale bits and three-DWORD recording. The
[Engine recheck](reverse-engineering/source-code/core/engine-system.md#september-27-retail-initialization-recheck)
corrects two slot tags, direct-versus-virtual calls, KempyCube/HUD confusion,
the particle descriptor and local source omissions. Five refusal controls,
exact live/rehearsal equality and independently restored Archive A POST passed.
All names, prototypes, bodies and 8,317 non-target rows remain unchanged; all
8,331 projected names match the live readback. These are static findings, not
new joystick, recording-file or rendering acceptance.

ABI admission now withholds unknown source widths and destructor entry kinds;
a purecall seed's `RET` is no longer an inferred interface convention. The older
Thing-family `SetAnimMode` and `GoToPoint` identities retain independent manual
call-site evidence: `0x004f450b` through `0x004f4511` forwards three DWORDs;
`0x00534f00` through `0x00534f1c` supplies a 16-byte vector plus a BOOL to
slot 61. The stricter automated route awaits pinned parameter-width witnesses
for those unknown source types. It does not establish a new prototype audit.

The compiler-destructor recognizer is implemented; its 33 name normalizations
and the separate [80 kept-name comments](reverse-engineering/ghidra/README.md#re-audit-verified-compiler-deleting-entries--september-27)
are promoted with independently restored recovery. The 33 name changes are
predominantly spelling normalizations of plausible deleting-destructor labels,
now backed by exact byte/RTTI/normal-flow proofs; they are not 33 new gameplay
bugs. The method admitted 113 of 120 fixed CMonitor-family entries. Root
freshly checked 724 recognized RTTI tables, 165 slot uses and 5,590 instructions
across 227 admitted wrapper/cleanup bodies. A review found an implicit-register
provenance defect; the tool now refuses unsupported instructions and 69 focused
tests pass. The initial cohort seal's stale added date tags were corrected
before live application; the rejected rehearsal remains preserved.

The 80-name cohort changed only comments/tags, preserved every name and
prototype, and excluded the preceding 33 entries. All nine live exports equal
rehearsal; 8,251 other function rows remain exact. Six excluded entries
have multiple incomparable RTTI holders; the seventh is CUnit's separate
entry, whose desired spelling is occupied by one shared wrapper. Re-derive
those shared entries without treating a common base as an exclusive owner.
The CUnit table selects `0x004f84c0`, while the shared derived-class entry at
`0x0050ee90` reaches the same teardown through a separate tail. Source-symbol
ownership remains unresolved. Keep the extra same-template families outside
CMonitor open until their family evidence is bound. Camera candidates still
need aggregate-return and folded-alias handling. Follow the loader contract
with original-reader short/zero reads and the inlined Spawner.
Re-derive unresolved cases where the evidence can support a whole family, and
neutralize nothing merely for missing tool support. Next examine the frontend
page family: the surviving Goodies declarations and common-page calls may
establish menu/loading/saving interface slots despite the missing base header.
This is a research lead, not yet a promoted disposition. Remaining name leads include
`BattleEngineConfigurations__Load` (source class `UBattleEngineConfigurations`). Constructor, parser, font
and sound identities are resolved above. Damage's name and corrected behavioral
annotations are recorded above. The `CPCController` key-query
argument/result discrepancy is also resolved. These resolutions demonstrate why
numeric allocation coordinates alone must not decide an identity.

Follow-ups:
- NvTriStrip also exposes an absent function candidate at `0x00572e20`, passed
  as an array-constructor callback at `0x00572658`. Check actual boundaries and
  instructions in a later structural cohort; do not widen the names-only cohort.
- Ghidra does not treat `_exit` as no-return, so `D3DX__error_exit`'s saved body swallows
  `output_message` (`0x00592b20`); 13 call targets in matched code have no Ghidra function.
- `operator_new`/`operator_delete` lost their descriptive comments to the D3DX cohort's proof text; restore
  verified descriptions.
- PowerShell is retired machine-wide. The RE lane's 31 `.ps1`/`.psm1` files cannot run; several are
  pinned by hash in evidence verifiers (`Invoke-TtdCallContext.ps1`, `Invoke-TtdCallContextV2.ps1`,
  `Record-ApitraceD3D9.ps1` and the pinned `ttd_pipeline_contract_tests.py`, which names seven of them), so
  retire only the unpinned ones and keep the pinned ones as provenance.

### RE record audit — requested September 25

David requested a comprehensive correction pass over the existing RE record;
earlier analyses and this audit's own drafts are fallible. The
current readback has 8,332 internal functions; the earlier document inventory
counted about 1,980 RE documents
(354 contracts, 807 function notes). Items found while answering lane questions
on September 25 include:
- wrong saved labels (the table above);
- a factory contract that called the burst spawner a one-argument fastcall;
- a save-field name and the kill-counter reset rule;
- the base-thing bitmap's meaning;
- World 110's turret fire-control statement.

**Running coverage after the allocator records (September 28).**
These are conservative dispositions supported by this date's sealed cohorts
and final library-match proofs, not a percentage of game understanding:

| Audit dimension | Current count and limit |
| --- | --- |
| Names corrected | 2,163 unique functions; 2,164 rename rows include one repeated correction. The latest nine correct six Jet weapon helpers and three main dispatchers; the preceding 14 Jet and 25 Walker verified names stay retained. |
| Names verified and kept | 484 additional functions: 62 library/import identities, Damage, 63 Thing-family, 14 Controller/Engine, 80 compiler deleting-entry, 74 frontend, six reader, seventeen switch-method, 43 cleanup-body, nine console-menu, eight shared-music, 41 shared/PC-sound, 25 walker, 14 jet and 27 allocator identities. This excludes functions already counted as corrected. |
| Names neutralized by this audit | 0; existing structural placeholders are not newly completed dispositions. |
| Names still outside that accounted set | 5,685 of 8,332. This is an audit queue, not a claim that all those names are wrong or unsupported. |
| Prototype records corrected | 131 functions: the prior 118, nine Jet/main signature records, ChargeWeapon receiver normalization and three allocator interfaces (two bool returns, one automatic receiver) matched by compiled source. Three explicit-ECX members become automatic thiscall; two main name inputs become char pointers; four arguments acquire source names. Two records change only the function name. Physical input locations, return widths and cleanup stay unchanged. Receiver normalization in earlier cohorts does not imply demonstrated runtime transport breakage. Three unresolved frontend returns, ten custom-storage floating rows and GetSampleLength's float/double question remain outside these corrections; a corrected parameter list is not complete ABI validation. |
| Comments corrected | 2,660 unique function comments updated across the promoted cohorts. Retained historical leads are not automatically verified semantics. |
| Function boundaries | One additional window callback admitted over existing code, subsequently identified as WndProc. |
| Living documents | Whole-corpus verified/corrected/open totals remain unmeasured; dated samples below are not complete coverage. |

Count sources: promoted September 26 manifests, `controller-engine-verified-20260927` and
`compiler-destructor-identities-20260927` / `compiler-destructor-verified-20260927`,
`frontend-page-identities-20260927` / `frontend-page-verified-20260927`,
`frontend-callback-abi-20260927`, `class-name-identities-20260927` and
`membuffer-identities-20260927`, `listener-identities-20260927` and
`membuffer-abi-20260927`, `resource-reader-identities-20260927`, `reader-abi-20260927` and
`switch-identities-20260927` / `switch-verified-20260927`, `camera-position-20260927` / `camera-copy-abi-20260927`, `device-lifecycle-20260927`, `startup-shell-20260927`, `getbpp-abi-20260927`, `window-callback-boundary-20260927`, `frontend-argument-abi-20260927`, `window-callback-abi-20260927`, `cleanup-body-verified-20260927`, `postevent-cleanup-20260927`, `console-menu-identities-20260927` / `console-menu-verified-20260927`, `vertex-menu-abi-20260927`, `music-identities-20260927` / `music-verified-20260927`, `thing-gameplay-identities-20260927` / `thing-gameplay-abi-20260927`, `sptrset-forwarder-20260927`, `sptrset-identities-20260927` and `sptrset-abi-20260927`, `sound-verified-20260927`, `sound-abi-20260927` and `sound-source-identities-20260927`, `walker-verified-20260927`, `walker-helper-identities-20260927` and `weapon-icon-identities-20260927`, `jet-verified-20260927`, `jet-helper-identities-20260927`, `jet-charge-abi-20260927`, `memory-verified-20260927`, `memory-abi-20260928`, the final
`library-verified/prepare-plan/match/lib-verified.tsv`, its three-thunk comment
cohort, the Damage identity recheck and the 65 plus 14 plus 80 plus 74 plus six plus seventeen plus 43 plus nine plus eight plus 41 plus 25 plus 14 plus 27 kept-name targets, deduplicated
against every renamed address. Private paths are under the existing
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/` owner. Name sets
are deduplicated by entry address and checked against the current live export;
the old 1,196 already-matching library rows overlap previous rename cohorts and
must not be added to the corrected total. Prototype/comment counts are separate
dimensions. No newly completed whole-game runtime acceptance is claimed.

The [25-row walker verification](reverse-engineering/ghidra/README.md#re-audit-verified-walker-records--september-27)
retains the proven identities and corrects their notes/tags after complete
pristine body, caller and source review. It preserves every name, interface and
code byte. The reviewed replacement passed fresh PRE, rehearsal/readbacks,
five byte-stable refusals, live readback and independently restored Archive A
POST; the first imprecise seal/rehearsal remains retained. All 8,332 projected
names equal the full live table. Exact successful control/POST-open twins were
retired by fresh hash comparison after recovery, with queue records.

The [movement contract](reverse-engineering/game-mechanics/walker-dash.md#september-27-complete-body-recheck)
now preserves the asymmetric slow-movement scaling and distinguishes runtime
precision assumptions from static instructions. Rotate and Pitch both use the
selected player's yaw-right mouse-binding category for their extra multiplier;
this is not a weapon classification. The
[weapon-store recheck](reverse-engineering/game-mechanics/battle-engine-weapon-stores.md#september-27-walker-recheck)
and two refreshed function notes explain mutable selection, separate firing
readiness and the heat gate's unordered-comparison distinction. No new player,
Godot or retail runtime acceptance follows. The independently reviewed
11-row helper correction is now live with exact rehearsal/readback/recovery.
It corrects the false icon-pointer labels, float rotation inputs, charge clearing,
weapon enable/disable/count and the shared walker/jet firing predicate. The
[two actual icon getters](reverse-engineering/ghidra/README.md#re-audit-weapon-icon-identities--september-27)
are now corrected live, with exact readback and independently restored recovery.
Their complete bodies return profile +0x04; the string-consuming ChangeWeapon
caller distinguishes them from integer attachment +0x38. The main icon dispatch is
inlined inside ChangeWeapon; the bounded byte/caller search supports no extra
standalone wrapper label.
The [fourteen kept Jet identities](reverse-engineering/ghidra/README.md#re-audit-verified-jet-records--september-27)
now have corrected comments/tags with exact live readback and independently
restored recovery. The first seal was rejected for three wording errors; a
second disposable rehearsal was interrupted before a receipt. Both are retained;
the replacement passed all gates. Only comments/tags changed. All 8,332 projected
names match live; the successful exact control/POST-open twins were retired by
fresh hash comparison with the retained recovery copies.

The [Jet recheck](reverse-engineering/game-mechanics/battle-engine-weapon-stores.md#september-27-jet-recheck)
distinguishes store eligibility from active firing/charging, four chargeable tiers
from five total tiers, selected-charge clearing and ambient x87 rounding. Its
separate native selection/store probe passed 90 cases and four altered-copy
controls. The paused rebuild's inactive-weapon comment and old attachment/icon
citation need correction. Its AdvanceCharge time-only helper also needs comparison
with ReadyToCharge's null-mode branch; the existing helper models that branch,
so reachability is an integration question, not a demonstrated gameplay failure.
No rebuild code changed and no player/runtime acceptance follows.

The [nine Jet/main identities and interfaces](reverse-engineering/ghidra/README.md#re-audit-jet-weapon-identities-and-interfaces--september-27)
are now corrected live, with exact readback and independently restored recovery.
The 769 code bytes and all 8,323 non-target records are unchanged. Six living
function notes/contracts now replace obsolete identity restrictions with the
complete-byte/source/caller findings; three other notes reconcile caller names.

The [ChargeWeapon member interface](reverse-engineering/ghidra/README.md#re-audit-jet-charge-member-interface--september-27)
now uses automatic thiscall. Complete body and actual dispatcher transport prove
the ECX receiver; seven returns have no stack cleanup. Its physical transport,
name and code are unchanged. Full live readback, independent POST restoration,
seven refusal controls and all 8,332 projected names pass.

The [27 allocator records](reverse-engineering/ghidra/README.md#re-audit-verified-allocator-records--september-28)
now carry verified notes and tags; names, interfaces and code are unchanged. Complete
bodies, callers and the pinned source expose the retail differences: Win32 mutex
handles replace the BTS spinlock (Cleanup passes the handle's address), allocation
failures report localized per-heap errors, ReAlloc frees the original even when the
new allocation fails, and DumpMemory's first-buffer failure exits past its flag
reset. The first seal was rejected for three wording errors and is retained under
`memory-verified/rejected-v1/`; the replacement passed every gate.

The [allocator interfaces](reverse-engineering/ghidra/README.md#re-audit-allocator-interfaces--september-28)
now match the byte-matching compiled source and their callers: FreeTiny and ReallocTiny
return bool in AL (the bytes rule out an int return; bool follows the pinned declaration)
and Shutdown is an automatic-this member. Cleanup's bool parameter is deferred: the
applier admits a sub-word final stack parameter only for renames, so it waits for a
tested rule that checks the unchanged stack purge. Two rejected seals are kept in
`memory-abi/rejected-v1/` and `rejected-v2/`.

The completed native tiny-helper probe executes 197 unchanged retail bytes in
93 authored cases; four altered-copy controls fail as intended. It verifies that
false may leave nonzero upper EAX while AL is zero, in-range interior pointers
are accepted without alignment checks, and ReallocTiny links the old storage
into the free list before the intercepted allocation. It returns true for
recognition even when that allocation supplies null. Alloc and memcpy are
authored interceptors for ReallocTiny; FreeTiny has no calls. Full authored
memory, stack balance and preserved registers were checked. This does not
validate the real allocator, locks, exceptions or game runtime. Results:
`local-data/test-runs/re-audit-20260926/memory/tiny-helpers-4vuzyaxo/result.json`.
The first run is retained: its second adverse control refused a wrong expected
XOR opcode; the corrected run passed the complete set. No new Ghidra claim
was promoted from that failed run.

A subsequent console-registration alignment design is preserved as a research
lead: reuse the existing evidence tools and argument-transport checker; do not
use nearest strings or saved names as proof. Root checked the registrar body,
but the broader callback candidate set/tool extension remains unimplemented.
Private inputs and probes: `local-data/test-runs/re-audit-20260926/jet/` and
`memory/`. Scoped scripts remain in the existing ignored audit owner.

A new native original-code probe executes four unmodified selection/store bodies
on authored acyclic lists: 90 cases and four altered-copy controls passed. It
checks full EAX, cursor/index writes, all authored memory, preserved registers,
stack balance and two explicit masked x87 modes. The [weapon contract](reverse-engineering/game-mechanics/battle-engine-weapon-stores.md#isolated-selection-and-admission--september-27)
records the distinction from actual input cadence, current settings and gameplay.

The [resource-reader correction](reverse-engineering/ghidra/README.md#re-audit-resource-reader-identities--september-27)
re-derives five identities and keeps the exact live/rehearsal/recovery chain.
The existing name-evidence tool now checks literal-selected calls without
reusing saved names: twelve consumer transports, nine unconditional source
clauses, three conditional clauses withheld. Review added refusal coverage for
enclosing source conditions and internal calls bypassing the tag producer.
The [reader/dispatcher contract](reverse-engineering/source-code/io/chunker-system.md)
corrects invented validation/API claims and tag expansions. Forty-nine isolated
original-code reader cases plus two counterfactual controls distinguish partial
header updates, wrapped requested counts, pre-call consumed-count updates and
Close result translation. Buffer calls are intercepted; no real asset or game
was loaded. Goodies image loading uses one texture and derived height, unlike
the source image loop. The subsequent [reader-interface correction](reverse-engineering/ghidra/README.md#re-audit-chunk-reader-interfaces--september-27)
normalizes five existing ECX receivers to member conventions and corrects Read's
return from AL/bool to EAX/int. Constructor EAX=this and destructor void are
retained; size/count signedness remains open. All nine exports match rehearsal
and independently restored recovery. Six names are verified and kept; no
instruction, local or other function changed. The tag-call proof was rerun
after the five-name promotion: all twelve results and limits stayed identical.
The existing ABI admission tool now handles bounded switch tables in frontend
and listener methods. Its [six-name correction](reverse-engineering/ghidra/README.md#re-audit-switch-backed-method-identities--september-27)
is live, with exact rehearsal/readback and independently restored recovery.
The separate [17 kept-name cohort](reverse-engineering/ghidra/README.md#re-audit-verified-switch-backed-methods--september-27)
is also live, with exact readback and independent recovery. All 27,072 body bytes
and 7,455 instruction rows remain unchanged; the new comments preserve old notes
and expose three second-argument ABI questions rather than endorsing their types.
The tool pins each table and byte-remap span, checks unsigned guards and possible
bypassing entries, and retains cleanup/owner exclusions. Two additional names
remain withheld because raw instruction/string bytes resemble guard-interior
pointers; those occurrences do not prove actual incoming branches. Independent
review caught guard-interior and incomplete pointer-census defects in the tool,
and an overconfident removal of CRound's source-ownership uncertainty tag in the
first cohort seal. Root reproduced and corrected each before promotion. The 98
focused tool tests pass. Proofs and rejected drafts remain under
`local-data/test-runs/re-audit-20260926/switch-admission/`.

The [options callback recheck](reverse-engineering/binary-analysis/functions/display-settings.md#september-27-options-processing-recheck)
adds 21 original-code cases and two counterfactual controls. Local normalization
precedes the page-state test even on inactive pages; only a full-DWORD zero state
reaches the context-directed transition or persistence call. The helper returns
constant 2, unlike the source's controller enumeration. The two callees are
intercepted: this establishes no actual transition, save write or device behavior.
The Unit AI contract's stale scalar event argument is corrected to match its
already saved event-record pointer; its provisional return meaning stays open.
Consumer comments and concrete owner types remain open; do not infer an owner
solely from a factory's result.

The [camera position cohort](reverse-engineering/ghidra/README.md#re-audit-camera-position-identities--september-27)
promotes nine names through exact revised rehearsal/readback and independently
restored recovery. The tracked projection equals all 8,331 live names. Its
explicit aggregate result-buffer witness supports position slots 0/2 without
assuming a global aggregate ABI. All eleven selected RTTI holder uses agree;
five other existing position names are candidates for comment verification.
Full header alignment's seven classes / 71 slots / 39 targets remain candidate
counts, not completed semantic dispositions. The checker passed 113 focused
tests after root reproduced review findings about extra reads, wrapped offsets,
partial register writes, argument overwrite and bypassing entries. The first
cohort seal's imprecise destination/ownership wording was rejected and retained;
the replacement preserves all earlier notes and uncertainty tags.

The [camera evidence note](reverse-engineering/binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md#september-27-position-identities-and-result-transport)
records six unchanged original copy leaves, 193 bytes, 30 isolated cases and two
discriminating mutants. Sixteen-byte position and 48-byte orientation results
travel through a pointer supplied at entry `[ESP+0x4]`; the routines preserve
that destination in EAX. Overlap follows forward-copy order, not a before-image
guarantee. The original callers, complete frame lifetimes, camera geometry and
retail presentation were not executed. The viewpoint position getter can update
its previous-position cache; the rebuild must preserve sampling order.

The [six camera copy-return corrections](reverse-engineering/ghidra/README.md#re-audit-camera-copy-return-interfaces--september-27)
now retain the destination pointer in EAX in the saved physical signatures.
Every parameter annotation, automatic receiver, stack/type definition and name
is preserved; no source aggregate layout or orientation identity is invented.
All preservation/rehearsal/readback/refusal/review/recovery gates passed.

The [device lifecycle cohort](reverse-engineering/ghidra/README.md#re-audit-device-lifecycle-identities--september-27)
promotes 31 names/comments across 40 RTTI holder uses, preserving every prototype,
body and prior note/tag. Exact live/rehearsal equality, independently restored
Archive A recovery and all 8,331 projected names passed. The typed-list checker
binds real source declarations and calls to retail ECX/vptr/slot transport;
144 evidence/source-graph tests cover the admitted grammar and refusal cases.
No missing DeviceObject header was invented. Retail has two lists and restores
during initialization, unlike the source route. The existing
[platform note](reverse-engineering/source-code/core/platform-system.md#retail-device-lifecycle--september-27-correction)
and seven affected function notes now distinguish these identities from older
unverified semantics. Two shared stubs remain excluded; a texture initializer
is withheld by the checker's conservative WORD-store switch grammar, not a
proved retail defect. The rejected first seal had an off-by-one source citation
in eight comments; it was preserved, corrected and rehearsed afresh before live.
Private inputs: `local-data/test-runs/re-audit-20260926/device-lifecycle/`;
completed gate: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/device-lifecycle-v2/`.

The [startup shell cohort](reverse-engineering/ghidra/README.md#re-audit-startup-shell-identities--september-27)
corrects seven virtual-method identities and AddDeviceObject. Independent
source/caller/body witnesses establish each correspondence despite different
source/retail slot counts and order. All prototypes, 1,538 body bytes and 8,323
other function rows are unchanged; exact readback and independently restored
recovery passed. Review corrected an excluded Create witness that had claimed
ShowWindow/UpdateWindow calls; its actual visible-window creation uses
CreateWindowExA. The sealed eight-row payload was unaffected.

The [input contract](reverse-engineering/binary-analysis/cpccontroller-vtable-semantics-2026-08-11.md#september-27-window-message-producer-experiment)
now records 73 isolated original-code cases and two discriminating mutants:
68 synthetic messages exercise direct and WndProc dispatch, and five exercise
the constant texture-depth helper. The experiment confirms distinct trapped
keydown/keyup writes, console versus trap key arguments, full-DWORD suppression,
temporary character state and unsigned mouse-coordinate halves. Callees are
authored normal-return hooks; no Windows dispatch, real device or player
acceptance is claimed. Private evidence:
`local-data/test-runs/re-audit-20260926/startup-shell/`; completed cohort:
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/startup-shell/`.

The [GetBPP correction](reverse-engineering/ghidra/README.md#re-audit-getbpp-identity-and-interface--september-27)
replaces the wrong engine owner and no-argument cdecl declaration with a
source/caller-correlated shell member and one four-byte format argument.
The unused ECX receiver and unresolved enum type remain explicit. Int/EAX
return storage, stack purge, eight code bytes and 8,330 non-target rows are
unchanged. All preservation, rehearsal, nine refusal, independent review,
live readback and independent POST restoration checks passed. The prior five
original-code helper cases were reused, not rerun. Private receipts:
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/getbpp-abi/`.

The [window-callback boundary](reverse-engineering/ghidra/README.md#re-audit-window-callback-boundary--september-27)
is now promoted over the twelve existing decoded instructions at `0x00529070`:
34 bytes, no disassembly or retail-byte change. All 8,331 prior function rows
and 32,708 variables remain identical. Fresh preservation, rehearsal, five
byte-stable refusal controls, independent review, live readback and independently
restored POST passed. The complete projection matches all 8,332 live names.
The new default name and interface are intentionally unresolved; the separate
source-correlated WndProc metadata cohort comes next. Private receipts:
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/window-callback-boundary/`.
The [frontend argument cohort](reverse-engineering/ghidra/README.md#re-audit-frontend-argument-interfaces--september-27)
now corrects all 22 selected interfaces: six invented EDX formals, four render
stack interpretations, one button mapping and eleven omitted member receivers.
The existing evidence tool checks ordered PUSH values, source/header bindings,
fresh/cached dispatch agreement and all 32 known holder words. It rejects
review-reproduced stale-dispatch, assignment-expression and outgoing-stack
reload counterexamples. The timed SetPage caller puts the page on stack while
EDX holds a vptr, disproving an inference from the other caller's coincidence.
All names, return rows, locals, stack purge and 8,059 body bytes remain unchanged;
8,310 non-target function records are exact. The 141 evidence-tool tests,
94 framework tests, seven actual refusal controls, independent review, live
readback and independently restored POST passed. No new runtime run is claimed.
The [SetPage contract](reverse-engineering/contracts/frontend/CFrontEnd__SetPage__00466ae0.md#september-27-complete-dispatch-body-recheck)
replaces an unqualified source-parity statement with freshly decoded ordering:
active-page rereads after callbacks, plus a float duration in the timed path.
Its duplicate function note now links to that existing evidence owner.
Receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-argument-abi/`;
proof/tests: `local-data/test-runs/re-audit-20260926/frontend-options/`.

The [WndProc cohort](reverse-engineering/ghidra/README.md#re-audit-window-callback-identity-and-interface--september-27)
now names the registered callback and records four opaque stack DWORDs, full
EAX result and callee cleanup, with no incoming receiver. It preserves code,
locals and the saved unknown stack-purge field. All nine live/rehearsal exports,
independent POST restoration and nine refusal controls passed. SDK typedefs,
receiver lifetime and real Windows dispatch remain open. Its receipts are in
`window-callback-abi/` under the existing cohort owner.

The [43 cleanup-body identities](reverse-engineering/ghidra/README.md#re-audit-verified-cleanup-bodies--september-27)
are now verified live, with only comments and tags changed. All 6,586 body bytes,
1,973 instructions, names, interfaces and 8,289 non-target records are unchanged.
The existing evidence tool's
`cleanup-bodies` command checks first primary-vptr ownership, fresh complete
wrapper/recursive-body decoding, fresh RTTI and every matching wrapper shape.
Review-reproduced first-store and overlapping-ownership defects are fixed;
152 tests pass. The packet admits 44 cleanup identities: 43 existing spellings
and one proposed CPostEventData name, with 69 cases withheld. This includes
CUnit through a mechanically admitted wrapper whose prior name proposal had
collided; it does not imply 114 previously promoted wrapper names. The 43
retained identities are now live kept-name dispositions. The separate [CPostEventData cleanup cohort](reverse-engineering/ghidra/README.md#re-audit-cposteventdata-cleanup-identity--september-27)
now replaces the old neutral label, preserving all 105 body bytes, 29 instructions
and its existing interface. Legacy subsystem/wave tags are historical groupings,
not class proof. Both cohorts have five
refusal controls, exact independent review, live readback and independently
restored POST. The [console-menu identity cohort](reverse-engineering/ghidra/README.md#re-audit-console-menu-identities--september-27)
now promotes twelve inherited callback names from complete source/body witnesses,
seven table-specific RTTI chains and two same-object base/derived constructions.
All 734 body bytes / 276 instructions and saved interfaces remain unchanged;
exact live readback and independent POST restoration passed. The first comment
seal was rejected for two misleading phrases and preserved before live writes.
The [nine existing-name comment dispositions](reverse-engineering/ghidra/README.md#re-audit-verified-console-menu-names--september-27) are now live after the same preservation,
rehearsal, refusal, review, readback and independently restored recovery gates.
Their 758 body bytes / 257 instructions, all names and interfaces are unchanged;
5,027 historical comment bytes remain fallible leads. Shared/conflicting stubs remain
withheld. The evidence tool passes 164 tests, including reproduced review failures.
Separately, 23 isolated original-code cases and two altered-copy controls establish
VertexShader GetEntry argument/stack transport through the real stack probe. Its
[parameter-only signature correction](reverse-engineering/ghidra/README.md#re-audit-vertex-menu-argument-interface--september-27) is now live after seven refusal controls,
exact independent review/readback and independently restored recovery. Its
undefined/unassigned return is preserved; incidental formatter EAX is not a proven result API. Formatting/shader-text callees were hooks;
no real menu, Windows stack growth or rendered acceptance is claimed. Evidence:
`local-data/test-runs/re-audit-20260926/console-menu/`, latest experiment
`vertex-t4bw7ii_/receipt.json`.
The [music identity cohort](reverse-engineering/ghidra/README.md#re-audit-music-identities--september-27)
now corrects ten shared/device names, preserving 543 code bytes, 184 instructions,
all saved interfaces and two direct-tail thunk links. Five refusal controls,
exact live readback and independent POST restoration passed. Fresh decoding of
all eighteen shared/device bodies confirms previously documented OGG-only
admission, linear configured volume and the source assignment on random selection;
it does not rerun the older demo or isolated-code experiments. The source-graph tool now
uses complete entry-seeded bodies (21 focused tests), fixing cached switch-data
spill at SetVolume without claiming a Ghidra boundary defect.
The [Thing gameplay identity cohort](reverse-engineering/ghidra/README.md#re-audit-thing-gameplay-identities--september-27)
now corrects sixty names across eleven movement, activation and combat interfaces.
The packet covers 62 fixed-primary holders: eight kept names and eighteen
ambiguous/unresolved targets remain outside the mutation. All 7,714 body bytes,
2,386 instructions and saved interfaces are unchanged. Independent review,
five refusal controls, exact live readback and independently restored POST passed.
Two superseded rehearsal seals remain preserved; their prose/tag issues were
corrected before live. The full 8,332-row current name projection matches live.
The tree Damage note now withdraws the old elapsed-time/cooldown interpretation:
the incoming float is damage amount. This is a static interface/body correction,
not observed retail tree behavior. The subsequent [32-row physical-interface
cohort](reverse-engineering/ghidra/README.md#re-audit-thing-gameplay-interfaces--september-27)
corrects six scalar queries, sixteen activation methods and ten Hit/Damage rows,
including the Tree parameter-name-only correction. Twenty-two receivers become
automatic thiscall parameters; full-EAX predicates, source float with retained
ST0:10 storage, void results and opaque argument types follow complete native
callers and target bodies. All 29 locals, frames, argument positions, names and
code are preserved. Seven refusal controls, independent review, exact live
readback and independently restored POST passed. The comparator's default
parameter-name provenance rule was corrected from installed Ghidra source,
without changing the sealed mutation. Ten custom-storage floating
rows remain deferred because the current gate cannot represent source float
in ST0:10 without a separately reviewed storage-policy extension.
Evidence remains in `local-data/test-runs/re-audit-20260926/thing-gameplay/`;
cohorts are under `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/`.
The subsequent [eight shared-music records](reverse-engineering/ghidra/README.md#re-audit-verified-music-records--september-27)
retain already-correct names and correct comments/tags after full-body/source
review, five refusal controls, exact live readback and independently restored
POST recovery. Every name, interface, variable, stack and body stays unchanged;
all 8,332 projected names match live. The [shared-music note](reverse-engineering/binary-analysis/cmusic-shared-semantics-2026-08-11.md)
now separates source agreement on null-song assignment from genuine divergences,
bounds deferred selection writes and stop branches, and withdraws unsupported
high-level names for override guards. No audible or new runtime acceptance is claimed.
The GenericSPtrSet source
recheck exposed and corrected a parser defect: constructor initializer lists
were included in formal arguments. Balanced, literal-aware extents now separate
parameters, initializers and bodies; initializer calls reach the graph, and
assignment operators are indexed explicitly. Unsupported defaults withhold the
whole overload family. All 1,054 prior pinned .cpp definitions and their body
spans remain; eleven constructor argument lists are corrected and the missing
GenericSPtrSet assignment is admitted. These are source-index corrections, not
new retail dispositions. Both evidence-tool suites pass 197 tests; the next
14 container identities are now [promoted](reverse-engineering/ghidra/README.md#re-audit-genericsptrset-identities--september-27)
with exact live readback and independently restored recovery. Their first
rehearsal caught an undeclared automatic thunk rename and was retained without
any live application. The separate [forwarding-entry correction](reverse-engineering/ghidra/README.md#re-audit-genericsptrset-forwarding-entry--september-27)
preceded the successful second rehearsal; its complete record stayed unchanged.
All 1,065 target bytes, 363 instructions, saved interfaces and non-target rows
remain unchanged. The subsequent [interface cohort](reverse-engineering/ghidra/README.md#re-audit-genericsptrset-interfaces--september-27)
now corrects seven direct records and the dependent thunk: automatic receivers,
full EAX results and source-correlated static pool-method conventions. Complete
body/caller evidence, eight no-write refusal controls, exact live readback and
independently restored POST recovery passed. Its 339 bytes / 121 instructions,
frames, names and non-target records are unchanged. The constructor's EAX result
does not assert a C++ pointer return or an external consumer; zero-argument RET
alone cannot identify a calling convention. The current projection matches all
8,332 live names. The [list experiment](VALIDATION.md#original-pointer-list-operations--september-27)
passed 42 original-code cases and two altered-copy controls. The existing career
child/parent-link and ReCalcLinks notes now record null-item truncation and
the hidden result copy, separately from unexecuted complete career/save paths.
The monitor map also corrects its false only-writer claim: Shutdown clears the
pool-base pointer. Current consumer identities and W4 compatibility guidance
are updated; frozen packet and campaign receipts remain historical.
Keep the CUnitAI/CMechAI collision separate; never
move an excluded label simply to free a spelling. Evidence and failed/passing
controls: `local-data/test-runs/re-audit-20260926/frontend-options/cleanup-*`.
The five kept position names' comments and remaining camera slots remain open. Orientation constructor
witnesses remain withheld on raw pointer-like words, not proven incoming edges;
the first-call engine view-matrix consumer at `0x00449ef0` is an independent lead.
Shared Generic/Interpolated getters cannot receive an exclusive owner. Purecall,
ubiquitous stubs, unproved indirect tails and uncovered aliases stay withheld.
Remaining memory-buffer/listener comments and ABI questions remain in scope.
Private proof/experiment owner: `local-data/test-runs/re-audit-20260926/camera-interface/`;
completed gate: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/camera-position-v2/`.

The shared sound/backend review began with 42 candidates beyond the already
promoted DeviceInit: 13,186 bytes / 4,311 decoded instructions including that
anchor. The inventory alone established no dispositions; the completed subset
is recorded below. The [event-queue correction](reverse-engineering/binary-analysis/csoundmanager-shared-semantics-2026-08-11.md#september-27-event-queue-correction)
already resolves an inherited head-insertion error with 60 original-code cases
and two consequential altered-copy controls. Nonempty queues retain their head;
the flag selects insertion after the head or after the first negative-channel
node/tail. Device and audible behavior remain untested by this experiment.
Complete body/source/caller review produced 42 identity records. The
[41 kept-name sound cohort](reverse-engineering/ghidra/README.md#re-audit-verified-sound-records--september-27)
is now promoted with exact live readback and independently restored recovery.
The subsequent [two sound source-name corrections](reverse-engineering/ghidra/README.md#re-audit-sound-source-names-and-arguments--september-27)
are also promoted. The [shared note](reverse-engineering/binary-analysis/csoundmanager-shared-semantics-2026-08-11.md#september-27-sound-family-identity-and-documentation-recheck)
corrects asymmetric pitch-RNG, main-list versus chain lookup, pause/frozen scope
and source-version claims. The [backend note](reverse-engineering/binary-analysis/cpcsoundmanager-backend-semantics-2026-08-11.md#backend-identity-and-wording-recheck--september-27)
also repairs stale sample-route and volume-field wording. The first seal was
rejected before live use: five stop sequences were inlined rather than calls,
and KillAllSamples forwards block zero. The corrected 41-row seal passed a fresh
rehearsal, refusals and independent review. Keep interface changes separate,
particularly source-member versus saved stack-only annotations. The lookup
at `004e0a00` is now GetSample, with an extra retail reload argument and a second
argument named music. GetSoundEvent's flag is now insert_after_head; both
corrections preserve physical types/storage. This work does not claim successful loading
through the retail filename-loader stub.
The [ten sound interface corrections](reverse-engineering/ghidra/README.md#re-audit-sound-interfaces--september-27)
are now promoted: nine receiver-annotation changes and the full-width
IsEffectPlaying return. Exact live/rehearsal equality and independently restored
recovery passed. GetSampleLength's return type remains unresolved.
The [original sample-lookup experiment](reverse-engineering/binary-analysis/csoundmanager-shared-semantics-2026-08-11.md#september-27-sample-lookup-correction)
passes 76 cases and two altered-copy controls in each of two bounded harness
variants. It measures full-width music, low-byte reload and low-byte-only
reuse normalization; comparison/creation are intercepted. Actual loading and
audio remain outside it. Five freshly decoded GetSampleLength call sites,
including the cutscene consumer, support member-call annotation but do not
settle float versus double return precision; the [backend note](reverse-engineering/binary-analysis/cpcsoundmanager-backend-semantics-2026-08-11.md#getsamplelength-caller-and-precision-boundary--september-27)
records that boundary and a numerical falsifier. Next is the coherent walker
movement/weapon family: 26 complete bodies (7,143 bytes / 2,232 instructions)
have been decoded, but source-spelling candidates alone are not dispositions.
Remaining sound and camera interfaces stay in scope.
Private owner: `local-data/test-runs/re-audit-20260926/sound/`.

The existing source-graph tool now checks selected direct-call witnesses against
complete caller/target byte pins, an exact active source statement, ECX receiver,
ordered DWORD arguments and target stack cleanup. Eight shared-to-PC sound calls
pass; seven altered witness inputs are refused. Caller identity, register meaning
and explicit source-branch selection remain independently reviewed premises.
This reusable check reduces repeated transport analysis without certifying whole
functions or silently accepting missing macro/include context. Its affected
suites pass 211 tests; [validation and limits](VALIDATION.md#direct-source-call-evidence--september-27)
are recorded separately from the original-code queue experiment.

David's renewed scope keeps all saved names, prototypes, comments and living
documents in the audit. Prefer validated library/template matches, header
vtable/RTTI alignment, allocation anchors with measured line drift, and
call-site/graph/file-order alignment in the existing evidence tools. No tool
match is not proof of a bad name. Strengthen those instruments before assigning
neutral names; preserve displaced names as explicitly fallible comment leads.
Use reviewable cohorts and the existing preservation gate. Update these counts
after each promotion, keeping unique functions and repeat corrections distinct.
The prepared three-cohort queue is complete; it must not be restarted.

**Scratch retention (September 27).** David authorized retiring proven duplicate
audit copies. Fresh hashes supported removal of 100 completed probe project pairs
on B (12,301,973,840 bytes), with their 100 manifests, original receipts and all
exports retained. Archive A history stays intact; 89 changed/rejected/incomplete
pairs remain. Working and checkpoint inventories still match their recorded
identities. The [closeout retention rule](reverse-engineering/ghidra/README.md#scratch-retention-after-completed-promotions)
now uses the existing backup tool's exact-pair retirement helper after all gates;
its publication-failure controls preserve evidence. The completed `sptrset-abi`
closeout used `cohort_ops.retire_completed_probes()` after independent POST
restoration, retiring two additional exact twins (251,139,816 bytes) while
preserving both manifests and original receipts. The sound kept-name closeout
uses the same rule for its two successful exact twins; its rejected first seal
and byte-different rehearsal remain preserved. Keep PRE through all consumers and
do not retire changed rehearsals by semantic-export equality. This bounded
cleanup does not settle historical lab recovery or authorize cold-history pruning.

**Slot-save result boundary (September 27).** Five original-code adapter cases
and one separate counterfactual show that a complete CRT item write followed
by close error still returns zero; non-one item results return one without
closing. The read-only real fixture, exact calls/transport and all outputs
were independently checked. Static explicit-save composition takes the zero
success branch; main/pause callers ignore the slot result. None establishes
actual Windows persistence or a complete menu/dialog run. This retail path
uses CRT streams, distinct from CDXMemBuffer and the source's older PC writer.
Evidence remains in `local-data/test-runs/save-startup-20260919/`; the existing
[save contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#september-27-slot-save-failure-boundary)
and backend/function notes own the correction. No Ghidra disposition count
changes. The resource/chunk-reader follow-up above now separates promoted
identities/interfaces from still-unproved consumer owners and payload schemas.

**Memory-buffer ABI (September 27).** Eight interfaces are corrected live with
independently restored POST recovery: six members and two byte-proven direct
thunks. Five returns now use full EAX instead of AL; the destructor and its
thunk gain their implicit ECX receivers; three existing ECX transports receive
member-convention metadata; Write's size becomes signed without moving it.
Names, locals, all 2,002 code bytes / 678 instructions and 8,323 other function
rows are unchanged. All nine live exports equal rehearsal, and the complete
name projection remains exact. Eleven real refusal controls and 94 framework
tests passed. Exact typedef spelling, full class layouts and actual Windows
I/O are not certified.

The original six-row rehearsal exposed two automatically changed thunk
interfaces and was rejected before live. The revised framework requires every
such dependent explicitly, verifies its entire direct jump and matching
interface, and refuses omitted dependents before writing. A further review
caught a stale receiver-count sentence; that seal was preserved and the final
text repeated the gates. Records: existing `membuffer-abi/` cohort owner.
The [buffer contract](reverse-engineering/binary-analysis/functions/DXMemBuffer.cpp.md)
also records the remaining constructor-comment overstatement and bounded
Read/Skip/check-byte findings; four kept comments await promotion.

**Event-listener identities (September 27).** The existing vtable tool now
binds both guarded EventManager queue calls to the surviving `CThing::HandleEvent`
declaration through raw fixed RTTI and the actual event receiver. All 169 uses
were checked without using saved names as evidence. Sixteen source-identity
renames are live with unchanged bodies/prototypes, exact readback and an
independently restored POST. The complete name projection matches all 8,331
live entries. Five additional kept names need a separate comments/tags cohort;
previously counted names are excluded from new coverage. Eleven targets remain
withheld for shared bodies, ambiguous owners, purecall, bounded-switch proof
or two whole-image disassembly-cache gaps. Entry-seeded decoding resolves the
latter bytes; they are not demonstrated Ghidra boundary defects.

Private proof and rejected draft: `local-data/test-runs/re-audit-20260926/listener/`;
promotion: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/listener-identities/`.
Review corrected reversed event-branch wording and tightened three adverse
matcher cases; the evidence-tool module passed **75**, not the 90 mistakenly
quoted in the first tool commit. Per-handler semantics and saved types remain
separate work. In particular the influence handler consumes a pointer, despite
its saved float parameter. The memory-buffer ABI correction is now promoted.
Real Windows I/O and player runtime acceptance remain open.

**Frontend interface evidence (September 27).** The existing
name-evidence tool now binds seven surviving `CFEPGoodies` virtual declarations
to the common page callers and the constructor's receiver/table installation;
it does not invent the absent base header's declaration order. Fresh pristine
decoding reproduced 97 proposed identities (23 renames, 74 retained names),
while 35 candidates remain withheld. Both cohorts are promoted: 23 corrected
names and 74 retained names with bounded interface evidence comments. The 77 focused evidence-tool cases passed, including rejection of
template aggregates mistaken for pointer parameters/returns. Independent
reviews were re-derived against the specimen and source.

The 23-name PRE check stopped before sealing: Options render at `0x0051f700`
contains an incorrect saved instruction layout at `[0x0051f7be,0x0051f7c6)`.
Fresh pristine decoding and a read-only Ghidra inspection show one eight-byte
instruction where the listing has two unrelated instructions and four
undefined bytes. Its two incoming branches target the proper start; no saved
interior reference, comment or non-dynamic symbol was found. The exact span is now
repaired through the promotion gate, with independently restored POST recovery.
The subsequent 23-name cohort also passed fresh PRE, rehearsal, five byte-stable
refusals, independent review/root reproduction, live readback and independently
restored POST. All 8,331 projected names match live; 2,573 target instruction rows
and 8,308 non-target functions remain exact. The saved frontend
prototype defects and retail/source transition-timer difference were separate
findings, not certified by name matching; their follow-up is recorded below. Evidence and the rejected
pre-seal attempt are in `re-audit-20260926/frontend-page-identities/` under the
private owner above. The [render note](reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Render.md)
now records the opposite-endpoint argument and retail Credits/Screen Position
identity. Eighty-five native original-tail cases verify the Options factor
thresholds and exceptional float inputs; no rendering or player acceptance
is claimed. The structural repair and bounded execution add no name/prototype
dispositions. The separate 74-name comment cohort preserves every name/prototype,
all 8,184 target instruction rows and 8,257 non-target functions. Its shared
slot-4 entry has nine supported holders; the existing Language Test prefix is
explicitly nonexclusive. Review corrected stale Intro Process category tags
before live; the affected rehearsal and refusal controls were repeated. Independent
POST restoration passed. Receipts: `re-audit-20260926/frontend-page-verified/`.

The [Process timer note](reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Process.md)
now records 166 original-code cases: retail filters elapsed time and advances a
floating counter, unlike the source's integer increment. A stored counter can
round to the duration while the higher-precision comparison still skips
completion. Every case has retained input/output bytes; the earlier run with
colliding display labels is preserved and superseded. This proves the isolated
arithmetic/branch boundary, not the real clock, page callbacks or visual timing.
The separate [three-interface ABI correction](reverse-engineering/ghidra/README.md#re-audit-frontend-callback-abi--september-27)
now records the implicit receiver and missing stack argument for frontend Render
and Intro TransitionNotification, and the correct float/page argument order for
Options Render. Complete pristine bodies, direct/common callers and receiver
tables agree; all 990 bytes / 278 instruction rows remain unchanged. All nine
live exports equal rehearsal, seven refusal controls left project bytes unchanged,
and independently restored POST recovery passed. Names are unchanged. The initial
empty-tag draft and the comparator's omitted derived frame-size changes are
preserved with their corrections. Retail Render accepts but ignores the source's
forcerender argument and lacks its function-local 60 Hz throttle; global frame
pacing remains unproved. Private receipts: `re-audit-20260926/frontend-callback-abi/`.

The [62 class-name getters](reverse-engineering/ghidra/README.md#re-audit-class-name-getter-identities--september-27)
are now corrected live with independent POST recovery. A source-call anchor in
`CGame::FillOutEndLevelData`, its complete retail dispatch/copy window and raw
RTTI slot 7 bind each exact six-byte getter to `_GetClassName`. The tool never
uses saved names as identity evidence. It replaces 47 structural placeholders
and 15 descriptive aliases; all prior notes remain fallible leads. Each initial
class string lies in writable `.data`; missing declaration qualifiers, possible
inlined forwarding and runtime immutability remain unproved. No prototype is
certified by this cohort. Two draft matcher gaps were reproduced and fixed:
incomplete copy-tail verification and an ambiguous repeated-base check. All
85 focused tool cases passed, including adversarial re-pinned inputs. All nine
live exports equal rehearsal, five actual refusals preserve project bytes, and
the current 8,331-name projection equals live. Receipts:
`re-audit-20260926/class-name-identities/` under the private owner above.

The [CDXMemBuffer contract](reverse-engineering/binary-analysis/functions/DXMemBuffer.cpp.md)
now rechecks all twelve bodies and separates source identities from retail
buffer-size, file-flag, compressed-data and sidecar differences. Five corrected
names/comments/tags are live with independently restored POST recovery. All
1,262 code bytes / 423 instruction rows and 8,326 non-target functions remain
unchanged; all nine live exports match rehearsal and the full current name
projection matches live. Five actual refusal controls preserved project bytes.
A source-line citation and hexadecimal-offset notation were corrected before
resealing; the first rehearsal remains preserved.

The complete original ReadString body ran in 67 bounded authored-buffer cases,
and Write/Close ran in 71. These reproduce CR/non-LF truncation, stale-byte
consumption after an empty refill, and failed/short-write continuation. Close's
success result alone does not establish persistence. Neither experiment used
real Windows file APIs, compressed decoding or original saves. The saved ABI corrections have since been promoted as eight explicit rows,
including two direct thunk dependents, as recorded above. Remaining
retained-name comment corrections are follow-up, not new completed counts. Receipts: `re-audit-20260926/membuffer-identities/` and
`local-data/test-runs/re-audit-20260926/membuffer/`.

Next listener work: five newly reviewed kept names need comments/tags; the
sixteen renames are complete as recorded above. The entry-seeded decoder now
closes the two cached coverage gaps with exact bytes, ownership and ABI checks;
82 focused cases and independent review pass. The new InfantryGuide/MechGuide
name candidates remain unpromoted. Five switch bodies still need a bounded
dispatch-table proof; other shared/ambiguous entries remain withheld.
The buffer ABI rehearsal exposed two direct thunks whose inherited prototype
changes needed declaration with their targets. The rejected attempts remain
preserved; explicit follower checks and the eight-row live correction are
complete. Continue consumer-priority ABI findings alongside this family.

Next bounded ABI evidence: [CCareer__GetGradeFromRanking](reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__GetGradeFromRanking.md)
returns AX, not a full integer, and all 14 direct callers supply the career
receiver in ECX.
Nineteen private original-code cases execute the complete grade/conversion
bodies and finite-floor path: negative ranking returns E, masked NaN returns S,
values above one are not clamped, and EAX retains the scratch pointer's high
bits. The scratch ring is modified; this is not globally pure. This finding is
not yet promoted. Private evidence: `local-data/test-runs/re-audit-20260926/career-grade/run-gmqyky4j/grade.json`.

Order: answer the rebuild and companion lanes' blocking questions first, then
audit by consumer:
1. The RE documents the rebuild tree cites. Done on 2026-09-26 for 32
   documents, by six read-only reviewers whose findings were re-derived before
   any edit; errors were corrected in place and the rebuild and companion lanes
   were told what touched their code.
2. The save-file documents the companion reads. Done: the god flags at
   `0x2496`/`0x249A`, displayable Goodies, the attempts field and others.
3. The queued Ghidra labels. Done: `label-audit-20260926` (above).
4. A sample of the factory-drafted contracts, re-derived from pristine bytes,
   to measure their error rate before any wider pass. Done on 2026-09-26:
   - **Mechanical claims.** A script re-derived the checkable claims of all 344 factory
     drafts from the pristine bytes and the live export: body range, byte count, body
     hash, instruction count, callee sites, callers and the `ret` size against the
     prototype. These claims hold, with these exceptions:
     - one wrong prototype (`CFrontEnd__Render` is `BOOL Render(BOOL)`);
     - 20 titles older than the live label;
     - 5 drafts that say "no callers" but have direct callers;
     - 2 drafts whose titles were corrected on 2026-09-08 without renaming their files
       (`contract_factory_validate.py`).
     The records are in `local-data/test-runs/contract-audit-20260926/`.
   - **Semantic claims.** Three read-only reviewers checked a sample of 12 drafts; the RE
     lane re-derived every claim they marked wrong.
     - 27 of 220 checkable claims are wrong (12%) and one is unsupported.
     - 11 of the 12 drafts carry at least one wrong claim.
     - 5 name the wrong function or owner, and one is filed in the wrong subsystem.
     - The errors come from inherited labels and packet comments (owner prefixes, callee
       names, parameter meanings, "exact" source claims), not from the byte-level fields.
     - Each sampled draft now has its verified corrections at the top.
   - **What the sample means.** Use the drafts' identity blocks. Treat their names, owners,
     parameter meanings and source-exactness as leads.
   - **Next.** A wider pass should start with the verified label table above as a label
     cohort. It should then take the `CFastVB__` family, and then the drafts the rebuild
     or companion cite.
   - **Found on the way.** The retail walker dash window differs from the source and from
     the rebuild ([walker dash](reverse-engineering/game-mechanics/walker-dash.md)).

Correct each document in place from the bytes, the pinned source or an
original-code run; treat existing names, comments and reports as leads, not
evidence.

### Remote checkpoint integrated on Linux — September 12

The complete remote difference from `135775772a126af48b9930a8fcfd4140000a4af9`
to `f6ad243f45e115ddc906a0d9dd79490d34d97171` was fetched and reviewed in
an isolated repo-local worktree. All six code/tool corrections are retained,
including the independently duplicated actor-script restore fix. The newer
Windows-staging retirement and local aircraft follow-up were preserved.
No main merge, release, desktop control or CI run was involved.

The incoming C# changes now compile and their owning tests pass. The final
focused Core selection passed 150/150; Client passed 907 with two existing
capture-dependent skips. All 52 added admission/guard cases ran. Negative
controls against the previous implementations failed as expected. Python
launcher/exporter checks passed, and the updated Java packet exporter compiled
and produced 14 verified packets from a read-only Ghidra copy. Exact commands,
limits and private logs are in [VALIDATION.md](VALIDATION.md#remote-source-review--2026-09-09-execution-pending).

The unpublished smoke suggestion was reproduced independently: closing a
smoke run could return zero before the completion report existed. The Linux
launcher now requires that completed lifecycle report and retains timeout
diagnostics. This bounded check does not replace gameplay, visual or audio
acceptance. The forty-step hash difference was isolated to the new arithmetic
mode byte; the separate older Headless fingerprint now checks its current
bounded Walker state. Full-combat and Save Lab UI acceptance remain open.

**The executable-backed Ghidra audit is active.** Initial read-only exports covered
8,330 internal-function rows, 32,688 return/parameter/local rows, 410 types, 2,300
bookmarks, actual body ranges, direct calls and saved analysis options.
They establish an inventory of existing analysis, not complete semantic review.
The first exact correction restores the Plane controller's incoming event
argument, with full readback and independently restored recovery. Its old
missing-boundary question was stale documentation: both call sites already
belong to the saved function. The decompiler's remaining stack-expression
artifact is explicit in the [controller evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).

Continue structural and semantic RE through the existing owners. The
[script callback audit](reverse-engineering/binary-analysis/functions/IScript.cpp.md#native-callback-transport--september-12-static-audit)
corrected two missing callback prototypes and distinguishes the native argument
count from script arguments. The remaining default signatures need per-body
review; shared cleanup is not permission to assign one prototype wholesale. Aircraft integration must preserve separate Unit
AI/controller state and the scheduled selected-provider/common-AI chain;
retiming the current per-Move target refresh alone would omit real behavior.
The bounded weapon selector now matches isolated original-code cases and has
focused Core coverage. Original-code Unit preparation/fire phase experiments
also passed, and five misleading provider/helper names were corrected in Ghidra.
The recovered provider contracts are not yet wired to actor firing. Core now
executes the separate aircraft exit listener, retains its owner/selector/deadline,
and submits script Ready at the scheduled handoff. New bursts wait for normal
control; pending bursts retain their continuation. Exit completion clears the
collision-ignore pointer and preserves guide state. Spawner loss marks the
Plane dying without declaring immediate shutdown. These are bounded source
and in-process checks, not full aircraft or tutorial acceptance.
The reduced-fixture returning driver again clears all 22 targets without
abort. The cold shipping-manifest route still aborts after one final-wave kill;
its client and direct-Core inputs agree. Preserve that failed completion gate
while replacing the remaining approximate combat owners.
The shared initializer attribution and both dispatcher/exit event-pointer
parameters are now corrected in the working Ghidra project with full readback
and independent recovery. The exit comment now identifies GetVulnerable,
the distinct CST collision-ignore pointer and TRUE GoTo override, with the
same preservation gate. A composed original-code experiment passes 21 cases:
slot-4 refresh precedes readiness, preparation can select twice, and an already
ready weapon can fire despite newly failed feasibility. Pending preparation
retains its earlier aim point. These contracts still need production integration.
The selected GunA/GunB selector1 model transforms and ordered Unit weapon uses
now reach Core as immutable inputs. An unchanged-code attachment experiment
passes 27 cases / 33 calls, distinguishing current/interpolated pose and
same-frame direct-cache reuse. Carry those measured paths into runtime cache
ownership. Native population now passes 11 cases / 17 calls over the full
12-part training mesh; its frame-zero poses match stored CPOS/CORI under both
tested precision modes. The cache stamp counts renders, not gameplay updates:
MainLoop permits multiple renders per update and pre-run updates without
rendering. Resolve ordered render context and camera-latch lifetime, and complete B feasibility's
real line query alongside retained aim,
preparation/readiness and scheduled bursts,
including terminal callbacks and next-frame round movement, before replacing
the old all-slots loop. Details remain in the controller evidence owner above.
Keep conditional random draws, ordered avoidance candidates and monitored
reference lifetime. The remaining controls-remap boundary is a candidate for
its own instruction-bounded correction. No broad cleanup, unreviewed bulk
prototype assignment or new campaign is needed to pursue these findings.

### Active phase — Linux playable slices and first Save Lab workflow

David retains desktop control until he explicitly releases it. Prioritize
RE and rebuild source/headless work meanwhile; live retail/rebuild playthroughs
and the Save Lab UI workflow remain pending.

David delegated project and companion direction on September 8. Prioritize a
faithful Godot game that the community can play and inspect, with Windows as the
primary audience and native Linux support. Keep a later enhanced version separate
from retail defaults. Native execution of selected original routines supports RE;
building a second complete port is not an additional active deliverable.
The first actual Godot development video is recorded in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#reconstruction), with its
revision, input route and known limitations. An isolated display may render footage
without controlling David's desktop; a synthetic demonstration is not a player
acceptance run. Keep the existing capture/launcher owners rather than creating a
separate presentation or test framework.
The same isolation now supports a copied-retail WineD3D observation, including
measured Plane control words and Euler transitions. Its development `-level`
entry does not close the player route; use these observations to replace the
remaining approximate aircraft transaction, with limits recorded in the existing
[Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).

David's September 7 priority is startup, menus and complete Level 100 parity.
Audit the actual Ghidra database in bounded cohorts against pristine bytes and
pinned source, correct misleading names/comments/signatures or boundaries when
proved, and carry recovered contracts into production code. Existing pipelines,
tests and agent reports are fallible inputs. Further World 110 expansion is
paused until this first route is established; its completed source stays useful.

1. Establish native Linux Godot build, launch, real input, audio, pause/focus,
   capture and live tape recording/replay using the installed pinned tools.
2. Complete the cold first-career Level 100 tutorial through player input and
   player-observable information, including completion/debrief/return and retry/
   failure. Compare presentation, audio, timing, controls and world behavior with
   retail; neither the synthetic smoke route nor a single Won establishes parity.
3. Resolve blocking systems with targeted, specimen-bound RE and implemented
   contracts. Keep the independent full-retail mandate and existing evidence owners.
4. Deliver a separate Godot Save Lab: open a real save, edit one supported field
   to a new copy, reopen and verify the original and every unselected byte.
5. Construct real World 110 from its own admitted inputs, then demonstrate the
   100→110 transition, useful play, retry and return without substituting World 100.

Refactor responsibilities where these steps expose a concrete problem. Reuse useful
Core/Client/AppCore code and retain WinUI migration material. Validate focused changes,
commit/push coherent milestones, update the existing capability/validation documents,
and stop with a phase report when these deliverables are complete. This phase does not
complete the full retail RE, game-parity or companion mandate.

### P6 — Campaign bookkeeping relief — OPEN; NOT IMPLEMENTED

Close already-triaged-out questions with their existing terminal verdicts and
decouple campaign generations from purely structural Ghidra promotions, re-grounding
when semantic grades require it. This is proposed policy, not today's authority.
Acceptance: a verified generation cut closes the intended rows with zero semantic
movement and the policy is recorded in campaign owner documents. This bookkeeping
proposal is not a prerequisite for the active playable slices.

### P7 — World-110 generalization — PARTIAL; NOT PLAYABLE

Since 2026-09-26 `Simulation` constructs World 110 from its materialized static
world, in the retail load order, through its start state, and a Level 100 win
carries its surviving base world into it through the career (VALIDATION.md,
"World 110 construction and start state" and "World 110's base-world carry-over
from Level 100"). The earlier, separate World 110 stage (its admissions,
player-start owners and construction prefix) was retired the same day in favour
of that one owner. Still open: the landing craft's flight, landing and cargo,
squad formation, and World 110's presentation in the Godot host.

The complete static Actor/base and Unit initialization order is now recorded in
the existing [Actor owner](reverse-engineering/binary-analysis/functions/Actor.cpp.md)
and [Unit owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__Init.md).
Implementing that order still requires actual render/mesh state, collision and
publication effects, and recursive child initialization; static body closure
does not complete those runtime objects.

The four landing-craft Component inputs now use their actual mesh attachment,
parent float pose and matrix-to-Euler conversion. Native x87 arithmetic and
focused Core checks agree on their meaningful output words. This closes an
incoming-argument dependency; child allocation, Init and event/world publication
remain unfinished.

The construction owner retains both explicit-tree tables and can now construct
the 1,481 base-world pines with real MapWho entries, live neighbor traversal and
owned collision-readiness events. The prefix requires an explicit incoming RNG
seed and uses a stated nearest/53-bit arithmetic assumption. It shares object/
reader identity allocation with subsequent detached player shells. Actual retail
FP/seed state, final tree orientation, complete collision response and ordinary
actor initialization remain open. The first lander/child collision exclusions
and separate Unit/animation/AI listeners are recorded in the
[World-110 owner](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md),
along with the first three Buildings' render/animation route and the Feature
contract. PostLoad spatial sorting is implemented separately and awaits the
complete load sequence. Startup RE narrows the seed/FP witnesses without claiming
those runtime values were measured.
The first three Buildings now use those shared owners, the existing Actor state,
64 real destructible segments and distinct AI readers/listeners. The factory
prepares its attached Sabre template; the repair pad constructs its actual
weapon using shared charge/selection state and effect-list nodes. No tank is
spawned and no repair shot is fired by this Init prefix. The same shared
Actor/Unit transaction continues through the inactive SAT turret and six iceberg
Features, including their actual weapon/animation state, current-versus-old
poses and type-dependent collision centres. The remaining ordinary objects and
renderer/resource caches still need integration before world event delivery,
reset and play. Keep the same spatial/event/RNG ownership when extending the
remaining authored objects; this prefix is not a playable world.
The old test-only Simulation route that ran Level100 Setup under a World110
stamp is explicitly rejected; direct World110 mission and hash tests remain.

Remaining: complete start/actor/player/Battle Engine construction, real ownership
and reader identities, physics/coordinate enrichment, squad/spawner expansion and
publication order, policy effects, player initialization, registry/state hashing,
real headless/interactive session, Godot lifecycle, and campaign 100→110 play.
The host still constructs only world 100. Acceptance: evidence-backed contracts
and focused production-path tests recorded in [PARITY.md](rebuild/PARITY.md),
working second-world lifecycle and campaign transition, and the current-truth
section of [rebuild/README.md](rebuild/README.md) updated without widening partial claims.
The serialized-seed ceiling is in
[world-110-initial-constructor-seeds.md](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md).

### P8 — Player-input replay tapes — IN PROGRESS

Record an actual play session as a `CommandTape`, then replay it twice under
`--expect` with identical results. Acceptance: both runs pass and the recording
procedure is documented under `rebuild/tools/`. Native Linux input capture is now
in scope. Expected hashes must be measured during live play; a synthetic tape or
expectations generated by replaying the same tape do not meet this gate.
The September 6 mostly idle native session passed both expected hashes across
two replays. Recording now works; a substantial player-input tutorial recording
and its workflow acceptance remain open.

### P10 — Godot toolkit companion — PLAYER APP BUILT ON LINUX; PAUSED

The companion is a C# application built in code on Godot 4.8 dev6 .NET and organised
around players: careers with a campaign map, Goodies, career editing, cheats, game
settings, automatic backups that can be put back, music and voices, and lore (see its
[README](companion/OnslaughtToolkit.Godot/README.md)). Every write into the game is a
choice made after a verified backup, never while the game runs. Its suite and renders of
every screen at two sizes pass on Linux, and both exports build; the Linux package runs.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore)
records what is proven. David closed its goal on September 26 and paused the lane; it
resumes on its branch when he sets new requirements.

Still open: a human click-through, listening to the music and voices, and running the
Windows package. The portable write path has run only on Linux, and Windows
cross-export/package checks do not establish Windows execution.

Later, only at David's direction: patching the installed `BEA.exe` with a preview, a
verified backup and restore; showing the Goodies' own contents; media replacement; a
public release. No unrelated launcher, store or community features are planned. Keep MIT
application, GPL rebuild and private retail data separate. WinUI/AppCore remain reference
material, and the legacy [Windows release procedure](README.RELEASE.md) is historical, not
a release task. The companion lane does not own retail RE/Ghidra contracts or the faithful
rebuild's Godot migration.

### P11 — CLI parity — OPEN

The documented remaining gaps are cheat-named save-copy creation, trainer hotkeys,
and music playback. `media list`, `lore search/show`, and advanced `saves patch`
options already exist; `trainer music --out` renders audio but does not play it.
Standalone asset-library parity remains unverified and in scope until the implemented
command surface and per-verb Windows tests establish it.
Acceptance: close the remaining gaps with per-verb Windows tests, keep
[CLI.md](CLI.md) aligned with the implemented command surface, and keep public
copy free of internal process language. Source inspection is not Windows acceptance.

### P12 — Repository preparation — INTERNAL BASELINE COMPLETE; EXTERNAL AUDIT OPEN

The complete checkout now lives at `/srv/archive-b/Onslaught-Career-Editor`,
with a bind/automount at `/home/xsniper80/Projects/game-dev/Onslaught-Career-Editor`.
`local-lab/` and `local-data/` remain real ignored children of that one checkout.
The old ProjectData route stays absent. Current mount and recovery rules belong
in [AGENTS.md](AGENTS.md) and the existing local data guides.

David's September 6 repository-internal preparation and independent follow-up audit
are complete. He subsequently authorized the active development phase above.
Completed preparation scope:

- [x] Align current guides, implementation maps, platform boundaries and timing prose;
  retain all three goals, evidence grades, save/provenance rules and development holds.
- [x] Repair the packet exporter's Linux launcher, dry-run/refusal behavior,
  verified incremental reuse and recoverable publication; repair canonical probe-ledger
  routing and the case-sensitive authoring fixture. Correct host-attestor diagnostics
  without changing any frozen campaign selector, pin, grade or receipt.
- [x] Group the four recovery packages under `local-data/recovered/`, preserving
  all 120 files / 28,217,115 bytes and recorded metadata. Retain both unselected
  seed stages under `local-data/recovered/seed-staging/` and fourteen historical
  validation files under `local-data/test-runs/retained-lab-records/`: another
  126 files / 68,827,682 bytes, with unchanged hashes and recorded metadata.
  The existing migration queue and local-data owner map record exact paths.
- [x] Close the bounded lab-root and tool reviews, retaining failed attempts,
  distinct staging trees and all frozen contents. Review findings and their
  reproduced resolutions live under `local-lab/reviews/preparation-20260906/`.
- [x] Close the independent follow-up findings: refuse unregistered packet replacement
  and output inside a bind-aliased project; explicitly report the four Windows-only
  tools suites as skipped on Linux. Retire three superseded tracked roadmap/signoff
  documents, remove obsolete execution and approval diaries from active state, and
  correct the current write-safety, native Lore and natural-Damage summaries.
  Retire seven unused fixed-model review helpers and condense review guidance to
  its evidence/preservation rules; preserve the generated historical review trees.
- [x] Retain four more historical validation logs and one obsolete instruction patch
  under their operational owners: 5 files / 29,048 bytes, every hash and recorded
  metadata field unchanged. Recheck the earlier 246-file grouping successfully.
- [x] Correct the three Linux test assertions that expected Windows namespace
  messages. The affected class passes 22/22 without skips or production behavior
  changes; no new broad Core or Windows runtime result is claimed.
- [x] Pass the affected existing tool suites and documentation/public-payload
  gates. [VALIDATION.md](VALIDATION.md) records the focused results and limits.

KEEP in place: the reviewed and writable Ghidra homes, frozen campaign inputs
and receipt graphs, explicitly retained historical/rehearsal projects,
`local-data/_recovered-worktrees/` and `local-data/windows-profile-2026-08-28/`.
Ignored status and a historical name do not establish redundancy. Existing dated
logs, manifests and citations remain evidence, not a new execution queue.

The storage owner's later September 6 closeout retired both B-side lab/cold
mirrors and moved remaining non-project B collections to A. It also retired a
few proven Archive A duplicates. The current checkout/lab/data stay on B, with
independent Ghidra cold recovery on A; this is not a whole-lab backup. Other
graveyard material and historical ignored non-lab recovery remain unresolved.
The migration queue owns those receipts; this development phase does not reopen
external cleanup or backup work. David separately retired the never-built Windows VM
staging on September 12; no Windows validation host is provisioned. Native Linux Godot now
runs, while complete runtime acceptance and the P7/P8/P10/P11 gaps remain open.

## Completed items

| Item | Completed scope and owner |
| --- | --- |
| P0 — Integration spine | Source/doc integration and branch consolidation landed. Later causal round-ID evidence superseded the geometric Blaster observer; measured tests belong in VALIDATION.md. |
| P1 — Sealed static-receipt reseat | The campaign cut completed. Select current state through `current_re_authority`; historical receipts do not select a parent. |
| P2 — Ghidra promotion/integration | The named cohort ceremonies and corrected offline integration completed. Read the Ghidra owner before any further promotion. |
| P3 — Simplify developer state | Retired 554 superseded top-level fields and unconsumed nested diaries from active loading. `_history` gives exact Git recovery; required compatibility values, current authority, hold, evidence limits and explicit KEEP controls survive. Archived follow-ups are not declared closed. |
| P4 — Function-triage packets | The exporter produced complete packets in one read-only headless run and served an RE question. Tool usage and focused tests are in tools/README.md. |
| P5 — Coverage index/query | The receipt-based index and preregistered cross-trace query completed. Raw TTD recordings were subsequently retired; this milestone does not promise raw replay or intact historical paths. |
| P9 — Ferry sweep split | The expensive sweep is separate from the default Core suite; the explicit command remains in VALIDATION.md. |

Completion requires the named acceptance evidence, not effort or an unrelated green
suite. Preserve fail-closed checks and use the smallest relevant existing validation.
Completed bookkeeping, document cleanup, or a partial World-110 owner does not close
the full RE, reconstruction, or toolkit goal.
