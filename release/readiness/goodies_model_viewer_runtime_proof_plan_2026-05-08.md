# Goodies Model-Viewer Runtime Proof Plan - 2026-05-08

Status: public-safe proof plan, not runtime proof

## Objective

Design the next copied-profile runtime wave for representative in-game Goodies model-viewer playback.

The current evidence is strong but still bounded:

- `release/readiness/goodies_model_viewer_alignment_2026-05-08.md` proves the source `GT_MESH` Goodie set, installed `GDAT` kind-1 archive set, and generated catalog Model set agree on 45 model Goodies.
- `release/readiness/goodies_model_viewer_readback_2026-05-08.md` proves existing retail Ghidra decompile exports contain the Goodies mesh deserialization branch and mesh interaction/update branches.
- `release/readiness/mesh_renderer_readback_2026-05-08.md` proves existing retail decompile exports contain the main `CMeshRenderer__RenderMesh` dispatch path.
- `release/readiness/goodies_input_observer_runtime_proof_2026-05-08.md` proves copied-profile normal wall navigation reaches the `CFEPGoodies__ButtonPressed` input path and skips `71`, `72`, and `73` on the ordinary wall route.

What remains unproven is live in-game model-viewer playback from a copied profile: open a representative model Goodie, observe the mesh viewer, exercise bounded viewer input, capture before/after evidence, and stop cleanly.

## Non-Negotiable Safety

- Do not patch or mutate the installed/original Steam `BEA.exe`.
- Do not mutate the installed game or original BEA.exe.
- Do not synthesize `.bes` or `defaultoptions.bea` from scratch.
- Copy a valid profile/save/options baseline before writing.
- Use app-owned copied-profile and artifact roots only.
- Apply `force_windowed` only to the copied `BEA.exe` if a windowed runtime is needed.
- Keep raw screenshots, frame captures, CDB logs, copied profiles, copied saves, copied executables, command output with private paths, and proof JSON under ignored/private paths such as `subagents/`.
- Publish only sanitized summaries.
- Confirm no managed `BEA.exe`, `cdb.exe`, Ghidra, or headless Ghidra process remains at the end; the final cleanup check must show no BEA process remains.

## Preflight Gates

Run these before a live runtime attempt:

```powershell
npm run test:goodies-model-viewer-alignment
npm run test:goodies-model-viewer-readback
npm run test:mesh-renderer-readback
npm run test:goodies-selection-observer-log
py -3 tools\start_game_profile_test.py
py -3 tools\send_game_window_input_test.py
```

These gates prove the static model-viewer alignment, retail read-back guards, CDB observer parser/command-file contract, launch-helper argument allowlist, and scoped-input parser contract. They do not launch BEA.

## Runtime Matrix

| Step | Purpose | Expected private evidence | Public claim if green |
| --- | --- | --- | --- |
| Copied profile prep | Create an isolated runtime profile from the read-only install. | Private copied-profile manifest and copied executable hash. | Proof used a copied profile only. |
| Windowed patch on copy | Keep the game controllable for capture/input. | Byte-verified `force_windowed` patch result against copied executable only. | Runtime used a copied executable, not the installed executable. |
| Save/options setup | Use a copied valid save/options baseline that has representative model Goodies visible or safely unlockable. | Copied save path, before/after targeted patch summary if needed, fixed-size validation. | Save setup was copy-scoped and byte-preserving. |
| Launch and attach | Launch the copied profile, identify the managed BEA window, and attach CDB by exact PID only if debugger observation is needed. | Launch JSON, window list, exact-PID attach log-readiness output. | Runtime target identity was explicit and bounded. |
| Navigate to model Goodie | Reach a representative model Goodie already known in the 45-row model set. | Screenshot/capture sequence and, if used, observer log with selected Goodie id/path. | Representative model Goodie was selected through the copied runtime profile. |
| Open model viewer | Trigger the Goodie model viewer and wait for stable display. | Before/after captures showing transition into model viewer. | In-game Goodies model-viewer playback was observed. |
| Bounded viewer input | Exercise only documented viewer controls such as rotation/zoom/manual-control toggles if the current observer/read-back supports them. | Input JSON plus after-input capture/log summary. | The viewer accepted bounded input without uncontrolled automation. |
| Stop and cleanup | Stop managed process and verify no stale BEA/CDB/Ghidra processes remain. | Process-list proof and cleanup summary. | Runtime proof left no managed game/debugger process. |

## Observer Guidance

Use existing observers only if they answer a named question:

- `tools/runtime-probes/goodies-input-observer.cdb.txt` is appropriate for normal wall navigation and `CFEPGoodies__ButtonPressed` input-path confirmation.
- `tools/runtime-probes/goodies-selection-observer.cdb.txt` samples `get_goodie_number`, selected-load state, and `StartLoadingGoody`, but it can be noisy because the mapper is hot during render-loop sampling.

Do not attach CDB just to collect more logs. If the visual model-viewer proof can be captured without debugger evidence, prefer the lower-risk capture path and keep CDB for a separately scoped observer question.

## Acceptance Language

If the wave proves representative model-viewer playback:

```text
Copied-profile runtime proof opened a representative in-game Goodies model viewer from a copied, windowed runtime profile. Raw captures, logs, copied files, and command output remain private; public docs record only the bounded path, selected Goodie class, safety posture, and sanitized observations.
```

If the wave fails to reach model-viewer playback:

```text
Copied-profile runtime proof did not reach representative Goodies model-viewer playback. The failure is recorded as setup/navigation/observer/runtime-specific evidence and does not contradict the existing static source/resource/catalog/read-back model-viewer evidence.
```

## Not Claimed By This Plan

- This plan is not runtime proof.
- This plan does not launch BEA.
- This plan does not mutate the installed game, original `BEA.exe`, original saves, or Ghidra.
- This plan does not prove final native WinUI textured/material/animated rendering.
- This plan does not prove camera, lighting, skeleton, animation, material parity, or a scratch rebuild.
