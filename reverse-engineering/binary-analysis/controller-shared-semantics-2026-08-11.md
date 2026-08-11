# `CController` shared mapping and dispatch semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — complete pristine retail bodies, table accesses, constants,
virtual calls, and seventeen normalized-identical PC demo twins; SOURCE — pinned
`Controller.cpp` and `Controller.h`; UNKNOWN — physical-device timing, live input
feel, and PS2/Xbox instruction parity.
Verdict: the shared controller object, mapping engine, repeat/deadzone laws,
control-stack routing, record/playback boundary, inactivity timeout, and vibration
policy are recovered. The released PC mapper is materially richer than the
retained source.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

These seventeen functions cover 3,815 retail bytes and 1,177 decoded
instructions. Every body has an independently linked demo twin with zero
normalized instruction differences; 298 raw bytes differ only in encoded
address or displacement spans. The machine-readable result is
[`controller-shared-semantics-2026-08-11.tsv`](controller-shared-semantics-2026-08-11.tsv).
That 5,529-byte table has SHA-256
`5ec124db16c51e302fa76d2a57dbe495470013da155ab51c617358a6a2eec51f`.

The retained implementation is
[`references/Onslaught/Controller.cpp`](../../references/Onslaught/Controller.cpp),
13,847 bytes, SHA-256
`342f96c53205fc47b2ce1c0776db56cd8acc9e5bb7f539c2bc7aedf41f286d58`.
Its interface is
[`references/Onslaught/Controller.h`](../../references/Onslaught/Controller.h),
9,257 bytes, SHA-256
`74fd5ad844b36fa9ccf470c591014e94b6306e80046a314a00215b6cc65f679f`.
Released decompiles are retained under
`local-lab/ghidra-fullpass-2026-07-23/exports/W002/decompile/`. The concrete PC
device half is separately recovered in
[`cpccontroller-vtable-semantics-2026-08-11.md`](cpccontroller-vtable-semantics-2026-08-11.md),
and the downstream action route is in
[`controller-player-game-event-spine-2026-08-11.md`](controller-player-game-event-spine-2026-08-11.md).

## Object, lifetime, and control ownership

The released constructor takes exactly three stack arguments after `this`:
initial target, input/binding-bank index, and configuration. It constructs the
monitored target stack and memory buffer, installs the shared vtable, pushes the
initial target, then initializes six virtual-button words, repeat state,
record/playback flags, pause state, bank `+0x16C`, and configuration `+0x174`.
There is no retained fourth `reverse_look_y_axis` constructor argument or field;
the retained source itself says look inversion moved into `CPlayer`.

`SetToControl` allocates an active-reader cell, registers it with the target's
deletion monitor, and pushes it at the stack head. `RelinquishControl` performs
the inverse operation and diagnoses both an initially empty stack and a pop
that leaves no owner. Destruction closes an active controller stream, drains
all registered readers, and destroys the buffer. The compiler-generated
`0x004F00D0` entry is a one-instruction direct transfer to that destructor.

`Flush` is the tick boundary: copy current button words to old, clear current,
then invoke virtual `DoMappings`. This preserves the source's edge/repeat model
while allowing the platform adapter to provide the physical state.

## Released mapping engine

`DoMappings @ 0x0042DB40` lazily counts 47 action rows. Each released row is 32
bytes: action ID at `+0x04`, then two 12-byte binding slots beginning at `+0x08`
and `+0x14`; input code `-1` disables a slot. The record base is
`0x008892D8` (the action-word view begins at `0x008892DC`). The current bank at
`this+0x16C` selects the first pass; in non-multiplayer play bank 0 also scans
bank 1. Ordinary live mapping is skipped while developer mode is enabled.

Released push types `0..9` reproduce the retained enum: held, once, release,
repeat, positive/negative analogue, positive/negative analogue-as-repeat, key
once, and key held. The PC build extends the switch through `17`:

- type `10` calls a third platform key-state query;
- types `11..14` form signed mouse axes from cursor displacement about the
  window centre, with positive/negative sign gating and two bank-gated forms;
- type `15` reads the three mouse-button held states;
- types `16..17` consume the three mouse transition-state families plus
  positive/negative wheel delta.

Those numeric cases and operations are exact; historical enum names for the
added cases are not present and are not invented here. The mouse magnitude is
`clamp(g_MouseSensitivity * centred_pixels * 0.004333333, -1, 1)`. A transient
flag prevents a zero-valued recenter event from refreshing the inactivity
timer. Both Shift scan codes (`0x2A` and `0x36`) held together emit action
`0x2D`, `BUTTON_FRONTEND_CHEAT`.

The shared repeat state accepts a new press immediately, arms 0.50 seconds,
then repeats only after strict elapsed `>` delay and switches subsequent delay
to 0.12 seconds. Only one shared repeat timer exists, matching the retained
source warning that one repeat button is accepted at a time.

## Analogue and record/playback laws

`GetMappedInputValue @ 0x0042E3D0` supports six negative input codes: four
stick axes and two POV axes. Its released deadzone is inclusive
`[-0.15, +0.15]`. Outside it, the remaining `0.85` range is linearly remapped
to full scale with constant `1.1764706`; nonnegative inputs become digital
`1.0` or `0.0`. Analogue-as-button cases use strict thresholds `> +0.9` and
`< -0.9`. The retained source's cached four-axis path and `0.36` deadzone were
not shipped in these two PC executables.

Playback invokes the platform reader before mapping, dispatches each recorded
virtual action at most once per flush, then clears its bit. Recording invokes
the platform writer last. The platform bodies prove that the released stream
is exactly three 32-bit virtual-button words per tick, not the retained
28-byte four-float-plus-three-word structure. `StartRecording` also uses the
released buffer write API with mode `0x11`, whereas the retained source calls
`InitFromMem`.

## Dispatch, inactivity, and vibration

`SendButtonAction` always sets the appropriate virtual-button word first. With
a valid target it refreshes inactivity except for the mouse-zero suppression
case. Actions below 16 route to a frontend target or the global game receiver;
ordinary actions route to the current target only after reconnect-interface
and pause-controllability gates. An empty target stack is diagnosed rather than
silently inventing a recipient.

Inactivity quit is enabled by playable-demo mode or the released `-e3` flag,
disabled during a non-interactive section or with a nonpositive timeout, and
fires only when elapsed milliseconds are strictly greater than the timeout.
Unlike the retained source, `ResetInactivityTimer` stores zero while the
non-interactive flag is active. `SetNonInteractiveSection` preserves elapsed
time across ordinary FMV/noninteractive spans but lets attract-mode time
continue.

Vibration accepts a nonzero request only in `GAME_STATE_PLAYING`; a zero stop
request is still allowed outside it. The selected career option either passes
the requested amplitude to the platform device or forces zero.

## Boundary

This closes the released shared mapping/dispatch policy and its exact PC demo
recurrence. It does not establish USB/DirectInput polling cadence, operating
system event ordering, runtime controller latency, the intended names of PC
push types 10..17, PS2/Xbox table layouts, force-feedback feel, or rebuild
parity. No executable or Ghidra mutation is part of this report.
