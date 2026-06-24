# Lane 10 - Modernization Feasibility Findings

## Scope
Modernization feasibility for four objectives:
- legacy -> modern call translation
- wrapper profile integration
- graphics feature unlock path
- stability boundaries

Evidence base: `reverse-engineering/binary-analysis/*`, `patches/*`, `reverse-engineering/save-file/save-format.md`, `reverse-engineering/game-assets/modding-reference.md`, and source parity docs under `references/Onslaught`.

## Executive Feasibility Matrix

| Objective | Feasibility | Rationale | Key Evidence |
|---|---|---|---|
| Legacy -> modern call translation | **Medium** (wrapper-first) / **Low-Medium** (internal rewrite) | The retail binary exposes stable render/platform wrapper surfaces, but it mixes D3D9 runtime with legacy D3DApp-era control flow and D3D8-era shader assembly behavior. External translation is practical; deep in-binary call rewiring is high-risk. | `reverse-engineering/binary-analysis/executable-analysis.md` (D3D9 import), `reverse-engineering/binary-analysis/functions/display-settings.md`, `reverse-engineering/binary-analysis/functions/vbuffer.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md`, `reverse-engineering/binary-analysis/functions/VertexShader.cpp/_index.md` |
| Wrapper profile integration | **High** | Runtime/profile knobs already exist in persisted options tail and config/CVar state; integration is mostly packaging, deterministic defaults, and drift control. | `reverse-engineering/save-file/save-format.md` (tail fields incl. `g_D3DDeviceIndex`, `g_ProfileMultisampleType`, `g_ForceVsync`), `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`, `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/_index.md`, `reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md` |
| Graphics feature unlock path | **High** (staged) | Multiple proven levers already exist: `cardid.txt` tweaks, widescreen CVar gate, optional display-flow patches, and known widescreen diff map. | `reverse-engineering/game-assets/modding-reference.md`, `reverse-engineering/binary-analysis/widescreen-patch-analysis.md`, `reverse-engineering/binary-analysis/windowed-mode-analysis.md`, `patches/patch_display_mode_flow.py` |
| Stability boundaries | **Medium-High confidence boundaries are defined** | Static RE gate is closed and critical display/reset functions are mapped, but behavior risk rises sharply when moving from wrapper/config to code-cave/internal patching. | `reverse-engineering/binary-analysis/deep-validation-status.md`, `reverse-engineering/binary-analysis/display-modernization-plan.md`, `reverse-engineering/binary-analysis/functions/display-settings.md`, `patches/README.md` |

## Objective Findings

### 1) Legacy -> Modern Call Translation

Current reality:
- Retail executable imports `d3d9.dll`, but still follows older DirectX sample-framework style control flow (`CD3DApplication::*`, menu command routing, fullscreen/windowed toggle flow).
- Render plumbing has identifiable wrapper seams:
  - platform wrappers (`PLATFORM__BeginScene`, `PLATFORM__EndScene`, `PLATFORM__ClearScreen`)
  - buffer wrappers (`CVBuffer`, `CIBuffer`)
  - device lifecycle hooks (`Initialize3DEnvironment`, `Resize3DEnvironment`, `ToggleFullscreen`, `ForceWindowed`, reset/device-lost handling)

Feasibility conclusion:
- **Feasible now** at translation-layer boundary (wrapper/runtime interception) without changing the game’s internal call graph.
- **Not yet cost-effective** to do broad internal call translation in binary (too much regression risk vs gain).

Important caveat:
- `display-modernization-plan.md` mentions a `d3d8to9` pilot, but this binary is already D3D9. That suggests either historical carryover or a generic placeholder track. Treat `d3d8to9` as **low-priority/likely non-applicable** for this retail hash unless revalidated.

### 2) Wrapper Profile Integration

Integration is strongly feasible because profile-relevant settings are already persisted and reloadable:
- Tail fields include adapter/device and quality controls (`g_D3DDeviceIndex`, `g_ProfileMultisampleType`, vsync/mipmap/texture controls, landscape quality controls).
- Boot/load paths around `defaultoptions.bea` are mapped and deterministic.

Required integration model:
1. Wrapper config profile (per-wrapper preset file)
2. Game-side options baseline (`defaultoptions.bea`)
3. Optional `cardid.txt` overlay for capability unlocks

Primary risk:
- Runtime writes can drift profiles because save/load/pause paths can rewrite `defaultoptions.bea` from active buffers. Integration must include drift detection or periodic baseline re-application.

### 3) Graphics Feature Unlock Path

A practical unlock ladder already exists, from least risky to most invasive:
1. `cardid.txt` modern GPU entries + high-feature tweak flags
2. `ALLOW_WIDESCREEN_MODES` enablement and validated `-res` path
3. Wrapper-forced windowed/fullscreen behavior (`DxWnd`/`dgVoodoo2` style path)
4. Minimal display-flow patching (`patch_display_mode_flow.py`)
5. Full widescreen code-cave binary variant only when required

Feasibility is high because each step has existing evidence and tooling, and each can be rolled back independently.

### 4) Stability Boundaries

Boundaries are clear:
- **Stable boundary (preferred):** external wrapper + config/profile changes; no binary mutation.
- **Controlled-risk boundary:** byte-verified minimal display-flow patches with backup/restore.
- **High-risk boundary:** code-cave widescreen behavior patches and deeper render-path rewrites.
- **Unknown/avoid-by-default boundary:** broad internal translation of render and message-loop internals beyond mapped functions.

The project is in a good position for staged rollout because static RE validation is marked closed and key display/lifecycle functions are documented.

## Recommended Staged Implementation Order

### Stage 0 - Baseline and Rollback Guardrails
- Pin canonical binary hash and capture a clean control run.
- Ensure rollback artifacts are present (`.original.backup`, documented restore command).
- Lock a deterministic test checklist (startup, alt-tab, mode switches, reset/lost-device, HUD scaling, input focus).

### Stage 1 - Wrapper-Only Pilot (No Binary Patch)
- Pilot one wrapper profile at a time (start with `dgVoodoo2`/DxWnd path used in docs).
- Validate windowed/fullscreen transitions, alt-tab resilience, and input capture recovery.
- Keep all changes external and reversible.

### Stage 2 - Wrapper Profile Integration
- Package reproducible profile bundles:
  - wrapper config preset
  - recommended game options baseline (`defaultoptions.bea` handling)
  - optional `cardid.txt` modern GPU entries
- Add drift checks for `defaultoptions.bea` rewrites after load/pause flows.

### Stage 3 - Graphics Feature Unlock Configuration
- Enable graphics options via `cardid.txt` + widescreen CVar path first.
- Use resolution and screen-shape settings already present in options/tail.
- Verify visual parity and performance before any in-binary mutation.

### Stage 4 - Minimal Internal Display Patches (Only if Stage 1-3 Insufficient)
- Apply `patch_display_mode_flow.py` in split mode (`--resolution-only`, `--windowed-only`) for A/B isolation.
- Keep optional fullscreen-toggle skip patch disabled unless explicitly needed.
- Re-run full stability checklist after each isolated mutation.

### Stage 5 - Advanced/Internal Translation Work (Explicit Exception Path)
- Enter only for defects wrappers/config cannot solve.
- Restrict scope to mapped display lifecycle functions.
- Require per-change byte diff manifest + runtime validation matrix before promotion.

## Blocker List

| Blocker | Impact | Severity | Mitigation |
|---|---|---|---|
| Missing full source parity for display/render internals (known source gaps, legacy build mismatch) | Limits confidence for deep in-binary translation design | High | Keep wrapper-first strategy; use binary-observed behavior as authority |
| Binary variant drift (`-forcewindowed` guard/state differences by baseline) | Can invalidate one-size-fits-all patch/profile assumptions | High | Gate by hash/version checks before applying profiles/patches |
| D3D8-vs-D3D9 ambiguity in historical modernization notes | Wrong wrapper/translation selection risk | Medium | Treat D3D9 retail path as authoritative; revalidate any D3D8-specific recommendation |
| `defaultoptions.bea` rewrite side effects from load/pause/save flows | Wrapper/profile settings can silently drift between sessions | High | Add post-load drift detection and baseline reapply policy |
| No broad automated GPU/driver compatibility matrix in-repo | Hidden regressions across hardware classes | High | Establish a small fixed matrix first (NVIDIA/AMD/Intel + 2 driver eras) before wider rollout |
| Code-cave widescreen patch complexity (28 regions, behavior-coupled) | High regression blast radius if used as first-line modernization | Medium-High | Keep as late-stage fallback after wrapper/config path fails |

## Practical Recommendation
Proceed with **wrapper-profile integration + graphics unlock via config/cardid first**, then escalate to minimal internal display patching only for unresolved defects. Deep legacy->modern internal call translation is currently feasible only as a constrained exception track, not as the default modernization strategy.
