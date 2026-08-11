# `CGame` level-lifecycle semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — pristine retail bodies, direct calls, state writes, strings,
and three normalized-identical demo twins plus one independently fixed demo
entry; SOURCE — pinned `game.cpp`, `game.h`, and `Platform.h`; UNKNOWN — exact
source-revision identity, two remaining demo entries, and runtime failure paths.
Verdict: the complete six-function level/restart lifecycle has recovered source
identities, ownership boundaries, return codes, and bounded released behavior.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

The six released bodies cover 4,570 bytes and 1,204 decoded instructions. Their
machine-readable crosswalk is
[`cgame-level-lifecycle-semantics-2026-08-11.tsv`](cgame-level-lifecycle-semantics-2026-08-11.tsv).
That 2,225-byte table has SHA-256
`307edbb0a49faae3e35f63ee0271a48ac007e544f64a98f1d3772d0b396208fd`.

The retained source functions begin at `references/Onslaught/game.cpp:246`,
`:292`, `:414`, `:530`, `:1260`, and `:1573`. That file is 103,727 bytes,
SHA-256 `7f6932e001f0c57938dd49aba07ab1cd05239e7a038096fb25310a34e9a4ef4e`.
`EQuitType` is fixed independently by `references/Onslaught/Platform.h:6`
(SHA-256 `3f0c45560e58a0758e21b4adad40c7d57bdea9b0d2da79b72d8e023747e8efd`):
`0` none, `1` frontend, `2` system, `3` load error, `4` restart, `5` timeout,
`6` user frontend, and `7` user title screen.

## Recovered ownership and order

`RunLevel` is the outer owner. It performs the one-off initialization and
resource load, then repeats the attempt-local pair until the result is no
longer `QT_RESTART_LEVEL`:

```text
RunLevel
  Init
  InitRestartLoop
  load one-off resources
  repeat
    load attempt UI resources
    RestartLoopRunLevel
    ShutdownRestartLoop
    if restart: InitRestartLoop
  Shutdown
  return the exact EQuitType
```

The released bodies make the division concrete:

- `Init` owns the console defaults, map, engine, imposters, render queue,
  static shadows, game interface, and HUD. Failure of the map, engine, or
  imposter initialization returns false to `RunLevel`.
- `InitRestartLoop` resets the attempt clock, score, cameras, controllers,
  objectives, quit/game state, event manager, particles, map membership,
  interface and script listeners. It allocates the two fear grids, message box,
  message log, pause menu, help display, briefing log, and the deterministic
  random stream seeded with `123456`, then queues the three-second pre-run event.
- `RestartLoopRunLevel` loads and post-processes one attempt, runs the optional
  demo controls screen and intro FMV, restores static shadows, executes
  `autoexec.con`, performs the pre-run update phase, starts unit loop noises,
  selects tutorial or in-game music, and calls `MainLoop` until `mQuit` is
  nonzero. It then kills samples, records end-level data, clears attempt-local
  visual resources, destroys players/cameras, and returns the quit code.
- `ShutdownRestartLoop` is the attempt-local inverse. Its released ordering
  matters: it first stops music and script execution, destroys controllers and
  restart UI objects, then tears down world-owned structures before trees,
  spatial membership, atmospherics, physics sets, particles, script events,
  and the event manager. The final PC-specific action shuts down mouse input.
- `Shutdown` owns the one-off resource inverse: HUD/interface, particle sets,
  shadows, dynamic objects, engine/map, mesh/texture resources, memory cleanup,
  the PC outro path, and console command/variable removal.

This is not a name inferred from adjacency. The retail call export contains
181 direct call sites to 126 unique callees across these six bodies, matching
the source-level partition. `Init`, `InitRestartLoop`, and `Shutdown` also have
independently linked demo bodies with zero normalized instruction differences.
Corresponding callers fix demo `RunLevel` at `0x0046E120`, although that later
demo body is deliberately retained as address-only rather than declared equal.

## Released PC differences and limits

The retained source is architectural authority, not assumed retail source
identity. The released PC `RunLevel` directly reloads the localized sample bank
and explicitly initializes engine, interface, HUD, message, and pause resources.
The released attempt runner also contains playable-demo controls-screen and
stress-test branches. Those shipped branches and their constants come from the
retail body, even where preprocessing or source-revision differences obscure a
one-to-one source statement.

The pristine decompiles are retained locally under
`local-lab/ghidra-fullpass-2026-07-23/exports/W004/decompile/`; the direct-call
owner is
`local-lab/console-callback-atomic14-post-campaign-20260803-v1/post-direct-calls.tsv`.
Two demo entries (`ShutdownRestartLoop` and `RestartLoopRunLevel`) remain
unrecovered, and `RunLevel` still needs an independently bounded demo CFG.
Actual disc/read failures, allocation failures, demo timeout behavior, and
platform-specific PS2/Xbox branches remain runtime or cross-platform questions.
