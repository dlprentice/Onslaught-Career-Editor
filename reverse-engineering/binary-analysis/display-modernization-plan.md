# Display Modernization Plan

> Post-validation planning artifact (no implementation).
> Last updated: 2026-03-01

## Goal

Plan a low-regression path to modern display/windowing stability after static RE validation gates are closed.

## Candidate Tracks

### Track A: Internal Patch Track

Patch retail `BEA.exe` startup/message-loop/display code paths directly.

### Track B: Wrapper/Translation Track

Use compatibility wrappers (`dgVoodoo2`, DXVK-like path) without patching core binary behavior first.
`d3d8to9` references are historical from earlier investigation and must be revalidated against the current retail D3D9 hash before being treated as active guidance.

## Decision Matrix

| Dimension | Track A: Internal Patch | Track B: Wrapper/Translation |
|---|---|---|
| Risk | High (binary behavior changes) | Medium (external runtime layer) |
| Effort | High (RE + patch + QA matrix) | Medium (config + compatibility validation) |
| Compatibility Breadth | Medium (depends on patch quality) | High (multiple GPUs/drivers via mature wrappers) |
| Debuggability | High internal observability; harder rollback | Easier rollback/toggle; less internal visibility |
| Reversibility | Medium (must keep clean patch chain) | High (remove wrapper to revert) |
| CI/Release impact | Higher (new binary artifact governance) | Lower (runtime packaging + docs) |

## Call-Translation Feasibility (2026-03-05)

Question evaluated: "port all calls to modern versions" for long-term preservation.

### Evidence Snapshot

- Retail `BEA.exe` imports confirm this build is already D3D9-era, not D3D8-era:
  - `d3d9.dll` (`Direct3DCreate9`)
  - `DINPUT8.dll` (`DirectInput8Create`)
  - `DSOUND.dll` (ordinal imports)
- Render/platform subsystem surface is large even before full binary-only callsite tracing:
  - 23 render/platform-adjacent source-file domains in the mapped corpus
  - 166 functions across those domains (`functions/_index.md` table sums)
- Internal source snapshot contains very high DirectX API density (`~949` API-symbol hits across `.cpp/.h`), which is not retail-identical but is a strong scale indicator.

### Practical Meaning

"Port all calls" is not a small byte-patch task. It implies one of:

1. Full renderer/input/audio rewrite path (binary surgery/injection + extensive compatibility QA), or
2. A robust compatibility translation layer strategy (wrapper-first), with optional targeted internal patches.

For this repo's current constraints (no full retail source tree/project files, patch-first delivery model), option 1 is a large multi-phase engineering program, not an incremental patch set.

### Effort/Risk Estimate

- **Full in-binary call modernization (all major render/input/audio call families):**
  - Effort: **very high**
  - Risk: **very high** (device-reset, state-cache, timing/input regressions)
  - Rollback complexity: **high**
- **Wrapper/translation-first modernization with targeted binary patches:**
  - Effort: **moderate**
  - Risk: **medium**
  - Rollback complexity: **low-to-medium**

### Recommendation

Keep wrapper/translation as the primary modernization lane, and reserve direct call-port rewrites for narrowly scoped defects that wrappers cannot solve. This remains aligned with Track B-first policy above.

## Recommended Rollout Path

1. Baseline first: keep unpatched retail hash as canonical control.
2. Pilot Track B first (`dgVoodoo2` then DXVK-style path) with deterministic config packs and runbook steps.
3. Gate Track A behind explicit defects that wrappers cannot resolve.
4. If Track A is needed: isolate to minimal patch set (window/message-loop/device-reset only), maintain byte-level diff manifest, and preserve rollback binary.
5. Add post-load drift detection for `defaultoptions.bea` and define a baseline reapply policy when load/save flows rewrite global options snapshots.

## Test Matrix

| Category | Cases |
|---|---|
| Startup | default launch, `-forcewindowed`, startup with missing/invalid config values |
| Mode transitions | windowed <-> fullscreen toggles, alt-tab cycles, minimize/restore |
| Device resilience | lost-device simulation, adapter switch, resolution changes |
| Render correctness | HUD/UI scaling, FOV consistency, widescreen behavior parity |
| Input interaction | mouse capture/release in windowed mode, controller focus recovery |
| Persistence | settings save/load across restarts (`defaultoptions.bea` and `.bes` load path effects) |

### GPU/Driver Matrix (Minimum)

| Vendor | Adapter Class | Driver Era A | Driver Era B |
|---|---|---|---|
| NVIDIA | GTX 10xx / RTX 20xx+ | legacy stable branch | current branch |
| AMD | RX 5xxx/6xxx/7xxx | legacy stable branch | current branch |
| Intel | UHD/Xe | legacy stable branch | current branch |

## Exit Criteria (Planning -> Implementation)

1. Static deep-validation gate marked closed in `deep-validation-status.md`.
2. Approved target track (A/B) with owner and rollback plan.
3. Reproducible test harness and pass/fail checklist recorded in repo.
