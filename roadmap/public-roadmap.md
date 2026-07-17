# Public Roadmap

The north star is a recognizable portion of the retail Level 100 tutorial in
the replacement engine, using authorized original assets and retail-faithful
Aquila handling. Research and tooling should directly advance that outcome or a
concrete player-facing toolkit workflow.

## Near-term sequence

1. Close one **Enhanced Copy** milestone for the retail game: aspect-correct
   widescreen gameplay, one reproduced modern-input defect, and a stable
   apply/launch/restore profile. Automation must launch only a verified copy,
   observe the exact changed behavior, stop its owned process, and leave the
   installed game untouched.
2. Run one **retail modding go/no-go**: make a visible, reversible change to
   mission text, script behavior, texture, or another bounded original asset and
   automatically confirm the copied game loaded it. If retail requires an
   unavailable authoring pipeline, classify that lane as executable patches
   only instead of building a speculative mod-package framework.
3. Turn the rebuild's **Aquila Handling Lab** into a source-derived,
   retail-compared slice: walker movement/turning, camera, morph, jet handling,
   landing, aim, and one weapon. Remove synthetic behavior as each real contract
   replaces it.
4. Implement the opening/firing-range portion of **Level 100** with objective
   progression and combat behavior from the real mission data. Procedural
   presentation may remain only where asset/renderer work is not yet ready.
5. Treat the owned replacement engine—not the closed x86 executable—as the
   eventual modding and networking platform. Defer online multiplayer until one
   real mission replays deterministically.

## Product ownership

- WinUI is the polished toolkit, copied-game manager, and eventual rebuild
  launcher.
- AppCore owns save-byte preservation, parsers, patch plans, guarded writes,
  and installed-game/copy safety.
- The C# CLI remains an unshipped maintainer adapter, not an automation product.
- Rebuild Core owns deterministic simulation; Godot adapts it for presentation.
- Ghidra, the retail executable, Stuart's GPL source, original game data, and
  controlled copied-runtime observations are implementation evidence—not
  parallel deliverables.

## Boundaries

- Never mutate an installed game or synthesize a save.
- Preserve unknown bytes, expected-byte patching, backup/restore, licenses,
  credits, provenance, and third-party terms.
- The project has full permission to use, modify, and distribute original game
  assets. Add only the curated assets a live product/rebuild slice consumes;
  bulk exports and raw lab evidence are not source.
- A parser, patch write, state hash, or render smoke proves only its own
  contract. Player-visible and retail-behavior claims require direct automated
  observation.
- Host/Join, public matchmaking, and new retail-binary netcode remain out of
  scope.
