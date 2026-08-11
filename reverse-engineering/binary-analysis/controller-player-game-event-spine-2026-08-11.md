# Controller-to-player/game event spine

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless bodies,
calls, constants, and branch structure; SOURCE — pinned `Controller.cpp`,
`Player.cpp`, `game.cpp`, and their declarations.
Verdict: all ten uniquely owned virtual targets across `CController`,
`CPlayer`, and `CGame` have exact source/ABI identities and zero normalized
demo/retail differences.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

The paired vtables are:

| Class | Retail | Demo | Structural key |
| --- | --- | --- | --- |
| `CController` | `0x005D977C` | `0x005DA77C` | `084db0e09b00e95b51eb39b92d1715a84b015b46fc21223fae97782317c3437e` |
| `CPlayer` | `0x005DE770` | `0x005DF770` | `083bc2df86d7dc1c2a07f91c26914ce278457ef46ba65f503f204b3dc1de6b5e` |
| `CGame` | `0x005DBBB4` | `0x005DCBB4` | `6e86ddcaad97b3cdbc3221b909e09036927f93cb07c5698fe48916e9f1040ec5` |

Their ten unique targets contain 4,407 retail body bytes and 1,346 decoded
instructions. Two hundred two instructions differ in 367 raw bytes between
builds; every pair has zero normalized differences.

The machine-readable result is
[`controller-player-game-event-spine-2026-08-11.tsv`](controller-player-game-event-spine-2026-08-11.tsv).
That 2,417-byte table has SHA-256
`f9942d3806cd33f473eed24d9775deab0e4410feba8cd4f95e0d04700030af51`.
The broader independent comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered dispatch chain

The released chain is now explicit at each virtual boundary:

1. `CController::Flush` preserves prior digital words, clears current words,
   and invokes the platform-specific mapping pass.
2. `CController::DoMappings` samples four analogue axes, applies the `0.36f`
   dead zones, handles playback/repeat/configuration, evaluates every mapping
   mode, and emits normalized actions to the current `IController`.
3. `CPlayer::ReceiveButtonAction` enforces game-state and powered-up gates,
   handles pause/panning, applies reverse-Y and the released tangent response
   curve, then dispatches morph, zoom, configuration, weapon, cloak, and
   walker/jet movement actions to `CBattleEngine` and its two parts.
4. `CGame::ReceiveButtonAction` owns game/debug commands: god mode, free camera,
   frame advance, cutscene skip, console navigation, debug-unit/squad cycling,
   forced win/loss, and objective completion.
5. `CPlayer::HandleEvent` returns from the pan camera to the control view.
   `CGame::HandleEvent` owns prerun/panning transitions, respawn, pause, and the
   recurring `0.003f` game-sound master-volume fade.

The constant `CanBeControlledWhenInPause` and `GetControlType` bodies are
compiler-folded with other classes, so they are present in the complete
vtables but not repeated in the unique-owner table. Destructors and game
shutdown complete the ownership/lifetime boundary without inventing another
input subsystem.
