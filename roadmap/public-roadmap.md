# Public Roadmap

The north star is a recognizable portion of the retail Level 100 tutorial in
the replacement engine, using locally materialized user-supplied retail assets
and retail-faithful Aquila handling. Research and tooling should directly
advance that outcome or a concrete player-facing toolkit workflow.

## Near-term sequence

1. **Enhanced Copy closed:** copied Level 100 runs at an exact 1600x900
   windowed baseline with the 28-region aspect/FOV correction; the copy writes
   the retail 16:9 option and minimum mouse sensitivity, and WinUI owns guarded
   create, launch, stop, and restore boundaries without changing the install.
2. **Retail modding go/no-go closed:** AppCore now makes two narrow,
   backup-guarded Level 100 changes in an app-owned copy: one fixed-size English
   subtitle replacement and one exact compiled mission command that changes the
   initial flight gate from disabled to enabled. Controlled retail runs rendered
   the text marker and showed the clean/modified transform paths reject/accept
   the same input; the real WinUI path reproduced the accepted result. Direct
   language-table edits and this one exact archive rebuild are viable. Loose
   script loading, a general mission compiler/editor, textures, general AYA
   authoring, and mod packages remain unproven.
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
- Do not track or package retail game assets or converted copies. Keep exact
  materialized inputs, bulk exports, and raw lab evidence local; source owns the
  bounded recipe, provenance, and code that consume them.
- A parser, patch write, state hash, or render smoke proves only its own
  contract. Player-visible and retail-behavior claims require direct automated
  observation.
- Host/Join, public matchmaking, and new retail-binary netcode remain out of
  scope.
