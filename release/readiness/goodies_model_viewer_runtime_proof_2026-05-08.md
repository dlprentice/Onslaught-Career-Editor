# Goodies Model-Viewer Runtime Proof - 2026-05-08

Status: public-safe runtime evidence summary
Date: 2026-05-08
Branch: `wip/sandbox`

## Purpose

This pass executed the copied-profile Goodies model-viewer proof planned in `release/readiness/goodies_model_viewer_runtime_proof_plan_2026-05-08.md`.

The proof used the local Steam install as read-only source material, created a copied runtime profile under ignored `subagents/`, verified the copied executable's `force_windowed` state, copied a valid existing save into a copied slot, launched only the copied profile, captured the in-game Goodies wall, opened a representative model Goodie, sent bounded viewer input, and stopped the managed runtime.

No installed game file, original `BEA.exe`, original save, or Ghidra project was mutated. No CDB attach was needed for this visual runtime proof.

## Preflight

Required gates passed before launch:

```powershell
npm run test:goodies-model-viewer-runtime-preflight
npm run test:goodies-model-viewer-alignment
npm run test:goodies-model-viewer-readback
npm run test:mesh-renderer-readback
npm run test:goodies-selection-observer-log
py -3 tools\start_game_profile_test.py
py -3 tools\send_game_window_input_test.py
```

Important output summary:

```text
Goodies model-viewer runtime proof preflight is ready.
Goodies model alignment: source 45, installed GDAT 45, catalog 45.
Goodies model-viewer read-back probe: pass, files 7/7.
MeshRenderer read-back probe: pass, files 4/4.
Goodies selection observer log probe tests: 7/7.
Copied-profile launch helper tests: 4/4.
Scoped input helper tests: 3/3.
```

## Runtime Result

Result: PASS.

Sanitized runtime summary:

- Prepared a fresh copied profile under ignored `subagents/`.
- Verified/applied `force_windowed` only against the copied executable; the copied executable was already patched, so no bytes were written in this pass.
- Copied a valid existing 10,004-byte save into the copied profile as `BEA 1.bes`; copied save analysis reported version `0x4BD1`, `CareerInProgress=YES`, and `232/233` displayable Goodies unlocked.
- Launched the copied profile with `-skipfmv`.
- Loaded the copied save through the retail UI.
- Reached the Goodies wall and selected `BE:A Unit-01 'Pulsar'`.
- Opened the in-game model viewer for the selected model Goodie.
- Captured the rendered model-viewer screen before and after bounded keyboard input.
- Stopped the copied `BEA.exe` process and verified that no `BEA`, `cdb`, `ghidra`, or `analyzeHeadless` process remained.

Private captures and JSON remain ignored under:

```text
subagents/goodies-model-viewer-runtime-proof-2026-05-08/
```

The private capture sequence includes:

```text
02-goodies-wall.png
03-pulsar-selected.png
04-model-viewer-open.png
05-after-bounded-input.png
```

The visual inspection of those private captures shows:

- `03-pulsar-selected.png`: Goodies wall selection text `Unlocked! BE:A Unit-01 'Pulsar'`.
- `04-model-viewer-open.png`: in-game model-viewer screen with the rendered BE:A model visible.
- `05-after-bounded-input.png`: rendered model remains visible after bounded input, with a changed view/text state.

One earlier private branch in the same copied-profile root intentionally remains as negative navigation evidence: pressing RIGHT eight times from `Hawk Winter` follows the known top-row wall mapping to `Race Challenge 1`, which opens a level-loading path rather than the model viewer. That negative branch reinforces the documented wall mapping and is not counted as the positive model-viewer proof.

## What This Proves

- A copied, windowed runtime profile can open a representative in-game Goodies model viewer.
- The source/resource/catalog model-Goodie alignment has live runtime support for at least the selected representative model Goodie.
- Bounded input can be sent to the managed copied BEA window while the model viewer is open, without uncontrolled automation.
- The proof harness can stop the copied runtime and leave no managed game/debugger/Ghidra process behind.

## What This Does Not Prove

- Exhaustive model-viewer playback for all 45 model Goodies.
- Native WinUI textured/material/animated model rendering.
- Camera, lighting, skeleton, animation, or material parity between WinUI and the retail model viewer.
- Continuous streaming or open-ended runtime autonomy.
- Public redistribution rights for private extracted game assets.

## Privacy / Release Safety

This summary is public-safe. It does not include private screenshots, raw frame captures, copied executables, copied saves, private full paths, CDB logs, Ghidra project data, or proof JSON.

Raw evidence remains under ignored `subagents/` and must not be committed.
