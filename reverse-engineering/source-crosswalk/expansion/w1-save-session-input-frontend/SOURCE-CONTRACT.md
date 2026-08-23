# W1 source contract — save, session, input, and frontend

Status: candidate expansion receipt; exact source-first contract, retail claims bounded separately
Date: 2026-08-22
Summary: the 180 omitted definitions in the reviewed W1 19-file set are now expressed as line/signature-stable source contracts with explicit target branches, retail evidence ceilings, falsifiers, and rebuild dispositions.
Evidence: SOURCE — pinned GPL source bodies and target guards; MEASURED — reviewed function notes, semantic tables, name/closure joins, and Generation-32 register/closure joins; UNKNOWN — unresolved retail bodies and compiler selection where each row says so.
Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; this wave reads tracked projections only and does not open or write the specimen.

## Authority and scope

The implementation authority is the pinned GPL source at `references/Onslaught@5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. The released-PC authority is the pristine `BEA.exe.original.backup` specimen with SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, but this wave reads only tracked function notes, promoted semantic tables, the current 8,329-row name table, and the dated 8,136-row static closure. It neither opens nor writes the specimen.

[`definitions.tsv`](definitions.tsv) is the row authority. Every row preserves `(source_file, source_line, function, signature)`, the selected preprocessor branch, a normalized source-body digest, algorithm, fields, constants, side effects, retail class/VA/evidence/falsifier, and current rebuild disposition. The receipt does not edit canonical `crosswalk.tsv` or its `REPORT.md`.

The exact 19-file set is `activereader.h`, `Career.h`, `Controller.h`, `DXGame.h`, `event.h`, `eventmanager.h`, `FEPGoodies.h`, `FrontEnd.cpp`, `Frontend.h`, `game.cpp`, `game.h`, `MemoryCard.h`, `PCController.cpp`, `PCController.h`, `PCGame.h`, `PCMemoryCard.h`, `Player.cpp`, `Player.h`, and `scheduledevent.h`. Its reviewed set hash is `72fb22a1716dcb87059f9af9b93e9c9c9d8415a85b64399828003ea2b36e5381`.

## Corpus hygiene and reuse preflight

Before finalizing the tracked receipt, this wave read `local-lab/INDEX.md`,
`local-lab/CORPUS-HYGIENE-2026-08-22.md`, and the current
`source-first-expansion/EXECUTION.md`. It searched tracked owners and
`local-lab/INDEX-CATALOG-2026-08-17.md` by subsystem, all eleven populated VAs,
representative W1 stable keys, the plan/auditor hashes, and the crosswalk/parser
tool names. The historical catalog routes earlier frontend/controller/TTD work
but contains none of the exact W1 stable keys or plan hashes; tracked notes,
semantic TSVs, source-system syntheses, the current contract coverage, and the
Generation-32 register/closure do contain the populated retail identities.

No generic inventory or retail probe was rerun. `selection.tsv` is the exact W1
subset of the reviewed 634-row `partition.tsv` (`bc367919…301fde`). The shared
`PLAN.md`, `sample.tsv`, and `manifest.json` remain predecessors, and the
predecessor tree-sitter auditor is named by its reviewed hash in
`RECEIPT.json`. The eleven populated rows also join the current Generation-32
tracked register (`4862fc61…85b4`) and `campaign-functions.tsv`
(`a63f42e3…1c63`) under READY `08ed8964…e73f` and reducer
`4c465010…4db3`.

Reuse accounting is exclusive on the load-bearing retail-evidence axis: 11
definitions are `REUSED`, 169 are `EXTENDED` with source/rebuild fields, and 0
are `NEW_MEASUREMENT`. Artifact accounting is 1 `REUSED` (`selection.tsv`), 7
`EXTENDED`, and 0 `NEW_MEASUREMENT`; exact paths, hashes, and meanings are in
`RECEIPT.json`. W1 opens no PS2 question and does not reuse or extend the closed
generic PS2 chain `520e9bfa` → `cbafa266` → `51ffe3d6`.

## Source architecture and laws

### Monitored references

`CGenericActiveReader` owns a deletion-aware `CMonitor*`. Its destructor unregisters itself when the target is live, while `ToReadDied` clears the pointer (`activereader.h:11-24`). `CActiveReader<T>` adds typed construction, copy registration, reassignment through the generic owner, identity comparisons, and pointer access (`activereader.h:29-41`). This is an observer-lifetime contract, not ownership of the monitored object: constructors and reassignment register a deletion event, the destructor unregisters it, and a target-death callback nulls the pointer.

The exact source side effects are row-level in `definitions.tsv`; no retail inlining or template-folding claim follows from the source. Only the generic destructor has a bounded named retail analog in this wave.

### Career record, options, and progression state

The source record is a fixed-capacity graph and settings store: 100 nodes, 200 links, 300 goodies, 32 slot words, two player option lanes, and 43 authored level-structure rows (`Career.h:13-24`, `Career.h:102-108`, `Career.h:193-207`). `CGrade` stores one signed source `char`; `operator>=` gives `S` priority and otherwise reverses ordinary letter order (`Career.h:28-38`). `CGoodie` starts `GS_UNKNOWN`, and `CCareerNodeLink` starts incomplete with destination `-1` (`Career.h:40-73`).

The omitted inline interface exposes direct node/link access, goodie state, progress, slots, god mode, sound/music volume, controller configuration, invert-Y, and vibration (`Career.h:138-179`). These are field laws with no hidden I/O. Negative node/link indices return null; positive indices have no upper guard. The exact fields and assignment/read side effects remain explicit per row.

Build membership matters. Under `TARGET != PC`, the source declares external-buffer Load/Save and a real size function. Under the PC branch, `Load(char*, bool)` returns false, `Save(char*)` is empty, and `SizeOfSaveGame()` returns zero while separate no-argument PC methods are declared (`Career.h:121-134`). Those PC stubs are not the released PC serializer: promoted retail evidence proves a versioned career/options loader and serializer at other source anchors. The W1 rows therefore keep the PC stub identities separate and unresolved rather than borrowing the retail `CCareer__Load` name.

### Controller and PC input interface

`CController` is both an input-state owner and a stack of monitored `IController` targets. It carries configuration, reverse-Y, pad number, vibration dispatch, three current and three old button words, analogue axes, repeat state, and record/playback state (`Controller.h:172-209`, `Controller.h:211-258`, `Controller.h:293-343`). The five omitted shared-header accessors are direct configuration/reverse/presence/pad laws; `IsPresent` is an unconditional source `TRUE` and is not a physical-device probe (`Controller.h:194-202`, `Controller.h:258`).

`CPCController` forwards three joystick transition queries to `LT`, two key queries to `PLATFORM`, and implements vibration as an empty body (`PCController.h:14-36`). The constructor only delegates to the base with target, pad, configuration, and reverse-Y arguments (`PCController.cpp:143-146`). Promoted PC-controller semantics prove the five query wrappers in this wave as source-inline bodies; the constructor remains unresolved because the released base ABI diverges from the retained source signature.

### Event scheduling

The source scheduler uses a 20,000-record pool, 200 frame buckets, three priorities, and one sorted overflow owner (`eventmanager.h:14-25`, `eventmanager.h:43-88`). At the 20 Hz game rate, the ring covers ten seconds. `Update` advances time and then flushes; relative, absolute, and owned-event insertion paths converge on the same pool (`eventmanager.h:49-68`). The omitted accessors expose event count, processed count, time, monotonically assigned process number, frame count, and validity without mutating the scheduler.

`CEvent` stores a 16-bit event number and a monitored destination (`event.h:13-26`). `CScheduledEvent` adds a monitored data pointer, reuse flag, static live count, and a union that is either scheduled time or free-list link (`scheduledevent.h:13-46`). Construction initializes data null and increments the static count. The omitted getters/setters are direct views of those fields. Generic event-pool behavior is not inferred from the rebuild's mission-specific event stream.

### Frontend session state

`CFrontEnd` constructs with no autosave, first-run true, selected level `-1`, all-levels cheat false, an empty save filename, and controller port `-1` (`FrontEnd.cpp:32-41`). Initialization starts the event manager, updates career state, initializes the selected platform frontend resources, initializes memory-card state, and builds page owners (`FrontEnd.cpp:49-100`).

The omitted inline interface is a state facade over control type, counter/quit, active and transition pages, common-page address, save/autosave state, memory-card number, success page/time, all-levels cheat, controller/text-set arrays, and first-run state (`Frontend.h:100-173`, `Frontend.h:254-290`). The source declares two or four controller ports depending on target (`Frontend.h:103-107`). These laws describe source ownership and mutation order; they do not prove the released page set, object offsets, input timing, persistence, or pixels.

`CGoodieData` is an authored requirement tuple. The two omitted accessors return `Number` and `Number2` without evaluation or mutation (`FEPGoodies.h:20-46`).

### Game and player facades

`CGame` exposes the source session's control mode, quit transition, deterministic random stream, player/camera arrays, level/game/pause state, objective arrays, pan/prerun timing, score thresholds, auto-aim, slots, level start, render timing, and frontend settings (`game.h:108-228`, `game.h:257-309`). The omitted rows are mostly one-line getters/setters. They are contracts over one source-owned field or array element, not evidence that the full released shell is reconstructed.

The two omitted `CWaitForStart` methods always permit paused control and identify as mech control (`game.cpp:1238-1256`). The credits control helper initializes and resets a quit flag, reads it, accepts paused control, and identifies as frontend control (`game.cpp:4086-4105`). These local classes remain line/signature-distinct from other methods with the same leaf names.

`CPlayer` is an `IController` facade over a monitored Battle Engine, player number, god/view state, five kill counters, seven statistics, and timeout (`Player.h:12-38`, `Player.h:58-108`). Construction records the number, clears the monitored Battle Engine and statistics, selects first-person view, clears kill counts, and reads god mode from career (`Player.cpp:24-34`). The omitted header bodies are direct getters, indexed stat updates, and one kill-counter increment. The constructor has only a bounded retail analog because its function note does not establish full source-body equality.

### Platform timing and storage stubs

`CDXGame` and `CPCGame` expose direct base-time and frame-time stores (`DXGame.h:9-19`, `PCGame.h:9-21`). They are platform shell setters, not independent time sources.

`CMemoryCard` defines the error vocabulary and abstract storage transaction surface. Its omitted `TooManySavesHere` source body unconditionally returns false (`MemoryCard.h:8-25`, `MemoryCard.h:27-60`). The PC owner in the retained source is mostly a no-device stub: `IsHDDAvailable` is false, `GetNumCards` writes zero and returns success, and `Update` returns false (`PCMemoryCard.h:8-17`, `PCMemoryCard.h:95-98`). Released PC semantics diverge at `GetNumCards`: the named adapter writes one device and returns success. This is the one explicit SOURCE_DIVERGES row in the wave.

## Retail classification boundary

The wave admits eight `SOURCE_EXACT` rows: three Career inline laws and five PC input forwarding/edge bodies. It admits three `SOURCE_ANALOG` rows: the generic ActiveReader destructor, the released PC memory-card device-count adapter, and the Player constructor. The other 169 rows remain `NO_MATCH_FOUND`, which means only that the bounded tracked search did not prove a retail body. It never means absent, optimized away, or unshipped.

[`RETAIL-DELTA.tsv`](RETAIL-DELTA.tsv) separates source agreement, source divergence, source-only bounded negatives, and unresolved identities. Every populated VA resolves in both current tracked static authorities and in its precise evidence target. Name similarity alone never promotes a row.

## Falsifiers and limits

- A source-anchor or normalized-body digest mismatch invalidates the row before any retail decision is considered.
- A pristine body/ABI mismatch at an exact VA refutes `SOURCE_EXACT`.
- A different proven owner or incompatible ABI refutes a bounded analog.
- A promoted same-owner alias/body with compatible semantics falsifies a source-only negative search.
- Compiler target membership, overload identity, or static/runtime proof can resolve every ambiguous/external row; until then, the row stays unresolved.
- This contract does not mutate Ghidra, the pristine or installed executable, user saves, the rebuild, canonical crosswalk files, or tracked retail assets.
