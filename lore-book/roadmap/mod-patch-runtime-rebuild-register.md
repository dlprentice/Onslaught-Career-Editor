# Mod, Patch, Runtime, And Rebuild Register

Status: public-safe summary
Last updated: 2026-06-23

This public register summarizes the current player-facing and contributor-facing
state. The private maintainer tree contains deeper runtime ledgers, debugger
logs, screenshots, copied-game artifacts, and proof helper scripts that are
intentionally excluded from public candidates.

## Safe-Copy Patch Surface

- WinUI Windowed & Mods prepares app-owned safe copies and patches copied files
  only. The installed Steam folder and original `BEA.exe` remain read-only.
- Current patch catalog accounting: 29 total rows; 20 visible options
  (9 stable, 11 experimental); 9 hidden companions.
- Public-safe patch catalog accounting:

| Track | Current value | Public meaning |
| --- | --- | --- |
| Visible executable patch options | `20 visible options: 9 stable, 11 experimental` | User-facing patch choices in the public WinUI lane. |
| Patch-row proof clarity | `20/20 visible rows with proof drawer fields` | Visible rows carry bounded proof and non-claim copy for contributor review. |
| Catalog rows with target specimen identity | `29/29 rows` | Every catalog row declares the supported clean Steam retail specimen identity. |
| Catalog rows with policy metadata | `29/29 rows` | Every catalog row carries machine-readable dependency, conflict, proof, selectability, preset, and windowed-pair policy metadata. |

- The stable player-oriented path is the copied-game windowed compatibility and
  graphics-defaults family.
- Experimental rows include frontend color presets, Goodies display overrides,
  debug/free-camera rows, a pause-key initializer experiment, and diagnostics
  intended for copied executables only.
- Patch rows are byte-verified and specimen-specific. They are not general
  claims for other executable builds.

## Runtime And Multiplayer Posture

- Local copied-game proof exists for safe-copy launch, patch byte verification,
  bounded frame capture, managed stop, selected control/input observations, and
  local split-screen proof slices.
- Online multiplayer is not a released capability. Host/Join controls must stay
  hidden or disabled until distinct-endpoint command-source proof and
  source-bound copied-runtime causality proof are both accepted.
- Public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay,
  4+ original-binary runtime players, deterministic sync, rollback, anti-cheat,
  and player-ready separate-screen netplay remain unproven.

## Asset, Audio, And Rebuild Posture

- Public docs describe the asset/resource formats and the supported extraction
  direction, but public candidates do not include proprietary game assets or
  private extraction outputs.
- Safe-copy music staging and copied-track presets exist in the product lane.
  Audible-output parity remains a separate proof class and is not claimed here.
- Static Ghidra closure and current-risk re-audit are summarized publicly as
  bounded static-contract evidence. Static closure is not runtime parity,
  rebuild parity, exact layout proof, or no-noticeable-difference proof.

## Public Contributor Boundaries

- Use the patch catalog, AppCore tests, and public validation commands as the
  contributor-facing contract.
- `patches/catalog/patches.v2.json` carries policy metadata for all 29 rows.
- Do not add copied executables, saves, screenshots, frame captures, private
  proof bundles, raw debugger logs, or local artifact paths to public PRs.
- When a feature depends on runtime behavior, phrase it as a bounded proof or a
  planned proof until the public-safe acceptance contract says otherwise.
