# Audio and music reconstruction delta

Status: bounded source-first reconstruction assessment
Last updated: 2026-08-22
Evidence: SOURCE — pinned audio/music headers and implementation shape; MEASURED — promoted pristine-PC audio/music semantic tables and current reconstruction code/tests; INFERRED — ranked implementation slices; UNKNOWN — audible parity and unselected accessor bodies.
Specimen: pristine PC retail `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; never the patched installed executable.
Verdict: the current Level 100 adapter already carries bounded lifecycle and cue laws, but its shared tangent option conversion is contradicted by promoted retail bodies and is the first coherent correction slice.
Scope: current reconstruction ownership and coherent next slices implied by the 23-definition audio/music header receipt.

## Current implementation owner

The current playback owner is intentionally path-specific: `rebuild/OnslaughtRebuild.Godot/Level100Audio.cs:9-12` says it is a Level 100 adapter rather than a reusable audio engine. It owns exact stream selection, queue/mix/pause presentation behavior, pitch/volume, and stream lifetime while mission, frontend, flight, actor, destruction, HUD, and pause owners provide canonical events.

Already carried laws include:

- one music player, so frontend and tutorial selection cannot overlap (`Level100Audio.cs:56-63`);
- fixed frontend/tutorial recipes, selected tracks 8 and 3, and stream-level looping for selection replay (`Level100Audio.cs:253-291`, `Level100AudioCatalog.cs:222-254`);
- exact Level 100 cue records, radio/HUD constants, queueing, actor-attached 3D playback, pause/resume, and kill/exit boundaries (`Level100Audio.cs`, `Level100AudioCatalog.cs`, and `rebuild/PROVENANCE.md:947-1014`);
- signed 0.02 flight-loop fade steps evaluated at the released 20 Hz cadence (`Level100AudioCatalog.cs:575-606`);
- separate path-specific player/cache collections rather than a falsely named retail `CSoundManager` linked list or 256-event pool.

Those are real carried behaviors. They do not implement the complete shared `CMusic` state machine, the generic `CEffect -> CSample -> CSoundEvent` policy, DirectSound channel arbitration, or the 23 exact source function identities.

## Stale or contradicted claims found

The current option-volume path is pinned to retained-source behavior that the promoted retail semantics now contradict:

- `Level100AudioCatalog.ToRetailOptionMix` applies `1 - tan((1-v)*1.38)/tan(1.38)` (`Level100AudioCatalog.cs:509-523`).
- `Level100Audio` applies that curve to both sound and music options (`Level100Audio.cs:109-128,757-768`).
- `Level100AudioCatalogTests.cs:589-669` calls the curve released behavior and hard-pins the curved cold-start mixes.
- `rebuild/PROVENANCE.md:968-970` likewise says the PC `SetMasterVolume` tangent curve is the adapter input.

Promoted retail/demo twins say otherwise. `CSoundManager::SetMasterVolume @ 0x004E04C0` stores the supplied float directly; the retained PC tangent conversion was not shipped (`csoundmanager-shared-semantics-2026-08-11.md:98-108`). `CMusic::SetVolume @ 0x004BBA10` computes `round(volume * 127)`, stores that integer, logs it, and persists the original float; the retained tangent curve was not shipped (`cmusic-shared-semantics-2026-08-11.md:84-86`). The current code, tests, and provenance therefore encode a stale source-equals-retail assumption. This receipt does not edit rebuild files, but a direct implementation lane should correct the code, tests, and prose together.

A second boundary is not a code defect but must stay explicit: retained `pcsoundmanager.h` says 32 buffers, while released initialization owns 64 physical slots and a capability-derived active voice count. A future generic channel owner must use the released contract rather than the source constant.

## Ranked coherent implementation slices

### 1. Correct released PC option-volume conversion

Replace the one shared tangent helper with two explicit presentation laws: sound master uses the released direct float, while music quantizes through `round(option * 127)` and derives device volume from that integer. Update the cold-start and option-change tests plus the stale `PROVENANCE.md` statement in the same reviewed slice. Keep the authored option defaults 0.8/0.9; only their conversion changes. This is the highest-value slice because the current player-visible mix is actively contradicted by promoted retail semantics.

Evidence gate: `csoundmanager-shared-semantics-2026-08-11.tsv` row `0x004E04C0`; `cmusic-shared-semantics-2026-08-11.tsv` row `0x004BBA10`; focused Level100 audio tests. Audible equivalence remains ungraded without a loopback/runtime audio gate.

### 2. Generalize the single-channel CMusic policy above Godot streams

Extract a presentation-only music policy that retains the current singular player but owns configured/current/target integer volume, queued replacement, five-point fade steps, and selection replay. Preserve measured retail exceptions: Ogg playlist extension, assignment-to-random null path, released track indices, and direct integer volume law. Do not add empty virtual methods solely to mimic C++ shape; adapt the source state machine to the existing Godot stream boundary.

Evidence gate: `Music.h:48-106`, promoted `cmusic-shared-semantics-2026-08-11.*`, `cpcmusic-vtable-semantics-2026-08-11.*`, and focused deterministic policy tests outside Core. Filesystem enumeration and async decoder timing remain presentation/platform concerns.

### 3. Introduce a shared logical sound-event policy only when a second world needs it

Lift cue lifetime, category mix, pause/kill, fade/pitch, and channel-budget policy out of the Level 100 adapter into a reusable client/Godot owner, preserving the source `CEffect -> CSample -> CSoundEvent -> CSoundManager` boundary without importing pointer/list implementation. Use the released 256 logical-event pool and 64-slot/capability-derived PC backend evidence; do not copy `GetAvailableChannels() == 32`. Keep Godot objects and real-time APIs outside deterministic Core.

Evidence gate: promoted `csoundmanager-shared-semantics-2026-08-11.*` and `cpcsoundmanager-backend-semantics-2026-08-11.*`, current Level100 audio catalog tests, and a focused second-world consumer proving the extraction is not speculative architecture work.

## Remaining boundary

No automated audio-output parity gate exists (`rebuild/PARITY.md:450-453`). These slices can prove state, selection, quantization, and lifecycle contracts, but not DirectSound/Godot loudness, driver timing, decoder buffering, or audible parity. `GetMenuSoundsMasterVolume` remains unadjudicated and must not be copied as either a bug or a fix until a retail body/caller proves its field read.
