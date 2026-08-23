# W1 rebuild delta — save, session, input, and frontend

Status: candidate mapping receipt; current-code inspection at base `784367bd43f9ec13125521b00fe0c8352670ffdd`
Date: 2026-08-22
Summary: current reconstruction already carries several Career, frontend, input, and generic event-scheduler laws from this W1 family, but it still has no save persistence, generic storage backend, generic monitor-lifetime owner, or complete CGame/CPlayer shell.
Evidence: SOURCE — current rebuild owners/tests and pinned source contracts; MEASURED — exact repository path/symbol inspection at the named base; INFERRED — ranked implementation slices; UNKNOWN — unimplemented retail/runtime behavior explicitly left open below.

## Inspection boundary

This report compares the 180 source definitions in [`definitions.tsv`](definitions.tsv) with the current `rebuild/` tree. It does not edit the rebuild and does not infer implementation from similarly named files. The code owners below were read directly with their tests, and [`rebuild/PROVENANCE.md`](../../../../rebuild/PROVENANCE.md) remains the authority for source/retail precedence.

Per-row dispositions use three terms:

- `PORTED_SOURCE_SHAPE`: the specific source law is represented by a current deterministic owner with its boundary documented.
- `PARTIAL_OWNER_PRESENT`: a coherent current owner exists, but this exact C++ interface/body or its complete state is not carried.
- `NO_DIRECT_PORT`: no generic reconstruction owner for this definition exists.

## Already carried laws

### Career

`RetailCareerGrades.cs` carries both `CGrade` constructors, signed `operator>=`, source-only equality, the exact `CCareer::GetNode` offset/negative-index law, and the source `GetLink` guard/stride projection. `RetailCareerUpdateGoodieStates.cs` carries direct goodie-state get/set over the 300-dword store. `RetailCareerProgress.cs` carries the 32-word slot store. Those exact W1 rows are marked `PORTED_SOURCE_SHAPE`.

The surrounding Career subsystem is materially present rather than absent: `RetailCareerNodes.cs`, `RetailCareerReCalcLinks.cs`, `RetailCareerProgress.cs`, `RetailCareerKillCounters.cs`, `RetailCareerUpdateGoodieStates.cs`, `RetailWorldCatalog.cs`, and `Level100WonCareerHandoff.cs` carry the released 43-node graph, root/child selection law, level-100 progression handoff, grade, slot, kill, and bounded goodie behavior. The remaining W1 Career accessors are marked partial because there is no current persistent career-record/session object that exposes all settings and save state exactly.

### Frontend

`OnslaughtRebuild.Client/RetailFrontendSession.cs` owns the presentation-only frontend state machine, and `OnslaughtRebuild.Godot/RetailFrontendFlow.cs` adapts input and presentation. The current enum and tests cover click-to-start, Main Menu, Quit, DevSelect, Options, Level Select, Mission Briefing, Select Configuration, Loading, and Gameplay handoff. This disproves an older broad gap claim that the reconstruction was still only a click/main-menu/Level-100 selector shell.

The W1 `CFrontEnd` accessors are still only `PARTIAL_OWNER_PRESENT`: the current session is an intentional reconstruction owner, not a byte-layout port of `CFrontEnd`; save mode, autosave persistence, memory-card selection, full page inventory, and text/controller arrays remain incomplete or absent.

### Input and game session

`OnslaughtRebuild.Client/InteractiveSession.cs` and `InteractiveSessionTests.cs` carry fixed-step input latches, one-step edge consumption, measured mouse sensitivity, and selected movement/fire/zoom actions. Those owners overlap the five exact PC button/key forwarding laws, but they do not recreate `CController`'s target stack, three-word button store, configuration bank, record/playback buffer, reconnect presence, or vibration dispatch. The W1 input rows therefore remain `PARTIAL_OWNER_PRESENT` rather than being promoted merely because both systems process input.

`OnslaughtRebuild.Core/Simulation.cs`, `Level100ActorRegistry.cs`, and mission/session owners carry selected player, objective, level, state, camera-handoff, and deterministic-random laws. They do not carry the complete `CGame` shell, arbitrary player array, pause/message owners, score/options store, render timing facade, or complete `CPlayer` statistics/view API. The W1 Game/Player rows are partial for that reason.

### Generic event scheduler

`OnslaughtRebuild.Core/RetailEventScheduler.cs` already carries the source and
released `CEventManager` shape: the 200×3 ring, sorted overflow list, 20,000-row
pool/free list, frame-derived clock, relative/absolute/owned-event admission,
flush order, reuse, recycling, and all six W1 manager accessors. Its focused
`RetailEventSchedulerTests.cs` pins the retail routing, ordering, counters, and
boundary constants. The six `eventmanager.h` rows are therefore
`PORTED_SOURCE_SHAPE`, not a gap.

`CEvent` and `CScheduledEvent` state is represented inside the scheduler's
pooled records, including event number, listener, data, due time, reuse, and
free link, but not every standalone setter/getter or the static live-count API.
Those rows are `PARTIAL_OWNER_PRESENT`. `ClearListener` also carries the filed
event's ActiveReader target-death nulling law, while the generic monitor
registration/copy/reassignment/destructor-unlink owner remains absent.

## Confirmed current gaps

- No rebuild path serializes or loads a career/save payload. The frontend explicitly owns no save persistence, and the current selector career is in-memory only.
- No generic `CMemoryCard`/`CPCMemoryCard` storage adapter exists. Any future filesystem owner must stay outside deterministic Core and must not synthesize protected `.bes` files.
- No generic `CMonitor`/`CActiveReader` registration, copy, reassignment, and destructor-unlink system exists. The current scheduler does model listener death and pooled event state; only the remaining generic lifetime surface is a gap.
- No complete `CController` configuration/reverse-Y/vibration/record-playback owner exists.
- No byte-layout port of `CFrontEnd`, complete frontend page set, or source save/autosave transaction exists.
- No complete `CGame`/`CPlayer` shell exists; current Level-100 owners intentionally expose only bounded deterministic behavior.

## Stale gap claims found

Two dated generalizations are no longer safe inputs for future work:

1. “Campaign is absent” is too broad. The current Core carries the released 43-node graph, selectability law, Level-100 FillOut handoff, and world-110 selection/admission groundwork. What remains absent is persistent career save/load and broad campaign execution, not all campaign logic.
2. “Frontend is only click-to-start/main menu/Level-100 select/loading” is stale. The current client includes Quit, DevSelect, Options, Mission Briefing, Select Configuration, career-law selection, and explicit gameplay handoff. Save persistence, debrief composition, and later-world session construction remain open.

The receipt keeps those distinctions in every per-row rebuild disposition instead of turning the older summary into a new task list.

## Ranked coherent implementation slices

### 1. Career read/load and frontend persistence seam

Highest source coverage and user value. Build a pure deterministic career-record/codec owner from the already-carried Career layout and field laws, then adapt storage outside Core through the frontend/client boundary. Retail adjudication is unusually ready: `career-save-format-semantics-2026-08-11.tsv`, `frontend-save-load-semantics-2026-08-11.tsv`, exact Career notes, and the tracked save tooling bound the released PC divergences. Start from a real reviewed baseline; never synthesize `.bes`, change unknown bytes, or let filesystem concerns enter Core.

### 2. Controller options state through the existing input owner

Carry configuration number, invert-Y, vibration enable, and source defaults as one options-state slice feeding `InteractiveSession` and the existing Options page. Keep device discovery, recording/playback, and platform vibration output outside the deterministic state owner. Retail controller semantics and options-tail evidence can adjudicate the source/PC differences without inventing a new controller framework.

### 3. Complete monitored event-listener lifetime

Extend the existing `RetailEventScheduler` only where a real consumer needs the
remaining monitored-listener/data lifetime: generic registration, target-death
notification, reassignment, copy registration, and unlink on destruction.
Preserve the scheduler's already-tested ring/overflow/pool behavior rather than
rebuilding it. The pinned ActiveReader/Monitor source and tracked event-system
evidence bound this as one lifetime slice, not 21 accessor tasks.

## Non-goals

This report does not create implementation cards, prescribe a per-function port, claim save compatibility, or treat source analogy as released equality. Current code wins over dated prose; retail measurements win where they prove a source divergence; deterministic Core remains free of filesystem, clock, process, network, and GPU APIs.
