# Modern Controller Setup Guidance Design

**Status:** Approved by the primary task on 2026-07-13 (option A)

## Goal

Help a first-time or returning player work around Battle Engine Aquila's known
modern-controller friction without implying that Onslaught Toolkit detects,
configures, or repairs controller behavior.

## Evidence Boundary

- Ziggurat's public developer guidance reports that one or both right-stick
  axes may not be read correctly on modern XInput controllers. It recommends
  the Steam Input layout named **Aquila - Gamepad with Mouse Aiming**, followed
  by manual in-game button and left-stick binding and minimum mouse
  sensitivity.
- PCGamingWiki independently records the right-stick binding limitation, lack
  of controller-only pause/cutscene controls, and lack of controller menu
  navigation. This is corroboration, not product authority.
- The Toolkit's existing Game Options workflow edits a separate copied
  `defaultoptions.bea`-shaped file. No accepted evidence shows that its raw
  controller configuration values are named modern-controller profiles or
  that changing them improves control feel.

## Player-Facing Contract

Save Lab's Game Options tab gains one compact, always-visible **Modern
controller setup** card before file selection. It gives exactly three ordered
steps:

1. In Steam Input, select **Aquila - Gamepad with Mouse Aiming**.
2. In the game's Controller Options, bind the buttons and map left-stick up to
   Movement: Forward so the movement directions are assigned.
3. Lower the game's mouse sensitivity to minimum, then adjust inversion in the
   game's walking and flying controls if needed.

The card includes an action labeled **Open Ziggurat's Steam setup guide in
browser**. The app opens only the fixed public Steam discussion URL through the
Windows URI launcher after a user click. Automated UI smoke finds the action
but never invokes it.

The card states that the Toolkit can edit a copied options file, but does not
configure Steam Input, detect the connected controller, or prove improved
control feel. The existing raw P1/P2 controller-configuration fields gain a
nearby caveat explaining that they are numeric values preserved or written in
the copied options data, not named modern-gamepad profiles.

## Interaction And Accessibility

- Add stable automation IDs for the card, heading, three-step text, nonclaim,
  external action, and raw-field caveat.
- Mark the heading as accessibility heading level 2.
- Keep all existing Game Options automation IDs and write behavior unchanged.
- Do not place the guidance on Home or add a wizard/completion state.
- Do not open the external URL during automated smoke.

## Verification

- A focused source contract test is written first and fails because the new
  controls and handler are absent.
- The focused test proves the exact evidence-bounded steps, browser label,
  fixed HTTPS target, launcher use, nonclaims, field caveat, and stable IDs.
- Native UIA proves the card content and external action are exposed in Game
  Options without invoking the action.
- A native screenshot at the existing compact test window is inspected for
  wrapping, clipping, and whether file selection remains clearly reachable.

## Nonclaims

This slice does not configure Steam Input, detect controller type or state,
repair right-stick input, bind controls in the running game, prove improved
control feel, alter options-file semantics, change AppCore/catalog/patch bytes,
launch the game, perform runtime or Ghidra work, edit canonical goal/state, or
make a release.
