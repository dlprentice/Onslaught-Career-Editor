# Shield Live Measurement Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a receipt-bound, input-free walker shield measurement mode with paired energy/shield correlation checks and a focused deterministic contract gate.

**Architecture:** The existing walker runtime runner retains ownership of receipt identity, sampling, deadlines, cleanup, and two-attempt lifecycle. A strengthened pure-Python shield scaffold analyzes paired fields, while the runner dispatches `--measure shield` to an idle observation branch that never creates Q-input markers or calls motion acceptance. Catalog/reporting and package scripts expose the new readiness without claiming a live result or changing Core.

**Tech Stack:** Python 3 standard library and `unittest`, existing C#/AppCore-generated runtime harness consumed read-only, npm script routing, Markdown documentation.

## Global Constraints

- Never read from, write to, patch, launch, or mutate the installed Steam game or original `BEA.exe` during offline readiness work.
- Do not launch BEA, attach CDB, send input, read live memory, or create runtime proof without a complete explicit live lease under `goal.policy.md`.
- Keep shield acceptance independent of motion, velocity, steady-speed, and Q-input acceptance.
- Require walker vehicle mode and correlated positive energy/shield update edges.
- Keep the shield envelope `v0-scaffold`; do not publish a v1 retail contract or change deterministic Core without two accepted live attempts.
- Add the orchestrator to a focused walker-specific gate; do not expand `test:runtime-tooling-safety`.
- Preserve the unrelated untracked `terminals/` directory.

---

### Task 1: Paired Shield Analysis Harness

**Files:**
- Modify: `tools/battleengine_shield_scaffold.py`
- Modify: `tools/battleengine_shield_scaffold_test.py`

**Interfaces:**
- Consumes: `ShieldSample(tick: int, shield: float, energy: float)` sequences and QPC frequency.
- Produces: `ShieldRateMetrics` with shield rate, energy rate, paired-edge fraction, relative rate delta, sample count, and `materialize_shield_pair_envelope(...)`.

- [ ] **Step 1: Write failing paired-correlation tests**

  Extend `battleengine_shield_scaffold_test.py` so the valid synthetic series supplies matching energy and shield rates. Add tests that reject static energy, negative energy while shield rises, a shield/energy steady-rate relative delta above `0.25`, non-finite samples, non-monotonic ticks, and unstable two-attempt shield or energy rates. Require the provisional envelope to expose `steadyShieldRatePerSec`, `steadyEnergyRatePerSec`, `pairedActiveEdgeFraction`, and `rateRelativeDelta`.

- [ ] **Step 2: Run RED**

  Run:

  ```powershell
  py -3 tools\battleengine_shield_scaffold_test.py
  ```

  Expected: FAIL because `ShieldSample` and `ShieldRateMetrics` do not yet carry energy correlation and the envelope lacks the new fields.

- [ ] **Step 3: Implement the minimum paired analysis**

  Change the public scaffold types to this shape:

  ```python
  @dataclass(frozen=True)
  class ShieldSample:
      tick: int
      shield: float
      energy: float

  @dataclass(frozen=True)
  class ShieldRateMetrics:
      attempt: int
      accepted: bool
      steady_rate_per_sec: float
      steady_energy_rate_per_sec: float
      paired_active_edge_fraction: float
      relative_rate_delta: float
      sample_count: int
  ```

  Validate finite values before calculating adjacent rates. Treat shield edges above `1e-6` as active, require at least five, require at least `0.80` of active shield edges to have positive energy movement, and require the paired steady-rate relative delta to be no greater than `0.25`. Extend `synthetic_shield_series` with optional `energy_start` and `energy_rate_per_sec`, defaulting to the shield start/rate. Build exact two-attempt bands for both rates and conservative correlation bounds without promoting them beyond `v0-scaffold`.

- [ ] **Step 4: Run GREEN**

  Run the shield scaffold test again and require all tests to pass with no warnings.

### Task 2: Input-Free Receipt-Bound Shield Mode

**Files:**
- Modify: `tools/battleengine_walker_trajectory_sampler.py`
- Modify: `tools/run_battleengine_walker_trajectory_measurement.py`
- Modify: `tools/run_battleengine_walker_trajectory_measurement_test.py`
- Modify: `tools/battleengine_walker_trajectory_sampler_test.py`

**Interfaces:**
- Consumes: sampler `RawSample.energy` / `.shields` at BE+0xFC / +0x100.
- Produces: `MEASURE_SHIELD = "shield"`, CLI `--measure shield --vehicle walker`, idle trace collection, and `battleengine-shield-rate-private-metrics.v1`.

- [ ] **Step 1: Write failing mode and dispatch tests**

  Add tests requiring:

  ```python
  self.assertIn(self.m.sampler.MEASURE_SHIELD, self.m.sampler.MEASURE_MODES)
  self.m.validate_measure_vehicle(self.m.sampler.MEASURE_SHIELD, self.m.sampler.VEHICLE_WALKER)
  ```

  Require shield+jet validation to fail, parser choices to accept `shield`, correlated synthetic trace rows to produce accepted shield metrics, the private payload to name `none-idle-observation`, and `sampler.analyze_attempt` not to be called for shield. Add a collection test that replaces `ExternalHarnessQInput` and `execute_deadlined_q_batches` with fail-on-call sentinels while patched guarded phase sampling returns baseline/hold/release rows.

- [ ] **Step 2: Run RED**

  Run:

  ```powershell
  py -3 tools\battleengine_walker_trajectory_sampler_test.py
  py -3 tools\run_battleengine_walker_trajectory_measurement_test.py
  ```

  Expected: the new shield-mode tests fail because `MEASURE_SHIELD`, runner dispatch, private metrics, and the no-input branch do not exist.

- [ ] **Step 3: Implement minimal runner wiring**

  Add `MEASURE_SHIELD` after `MEASURE_ENERGY` in the sampler catalog. Import the shield scaffold in the runner and extend metric unions. In `collect_trace`, complete readiness and guarded baseline sampling, then for shield collect hold and release through `_sample_batches` with fresh QPC origins and return without constructing `ExternalHarnessQInput` or calling `execute_deadlined_q_batches`. Set readiness and raw payload input protocol to `none-idle-observation`.

  Analyze all three ordered phases as:

  ```python
  samples = [
      shield_scaffold.ShieldSample(
          tick=row.tick,
          shield=float(row.shields),
          energy=float(row.energy),
      )
      for phase in ("baseline", "hold", "release")
      for row in provisional.samples[phase]
  ]
  ```

  Require walker vehicle mode, emit the bounded private metrics schema, update CLI help, and preserve every other mode's existing Q/morph/motion path.

- [ ] **Step 4: Run GREEN and refactor only while green**

  Re-run sampler and orchestrator tests. If the no-input branch duplicates trace construction, extract one private helper without changing behavior and re-run both suites.

### Task 3: Catalog, Reporter, And Focused Command Gate

**Files:**
- Modify: `tools/battleengine_measure_mode_catalog.py`
- Modify: `tools/battleengine_measure_mode_catalog_test.py`
- Modify: `tools/battleengine_campaign_scalar_status.py`
- Modify: `tools/battleengine_campaign_scalar_status_test.py`
- Modify: `reverse-engineering/game-mechanics/campaign-scalar-status.md`
- Modify: `reverse-engineering/game-mechanics/shield-rate-scalar-measurement-plan.md`
- Modify: `package.json`
- Modify: `CONTRIBUTING.md`
- Modify: `VALIDATION.md`

**Interfaces:**
- Consumes: sampler `MEASURE_MODES` and the runner/scaffold tests.
- Produces: live shield catalog row, machine-readable live/offline status, `test:battleengine-walker-trajectory-measurement`, and `test:battleengine-walker-measurement-contract`.

- [ ] **Step 1: Write failing catalog/report tests**

  Require six live modes including `shield`, four remaining offline harnesses, no collision between sets, and campaign status output containing the shield live mode while retaining scalar status `scaffold+offset; live pending`.

- [ ] **Step 2: Run RED**

  Run:

  ```powershell
  py -3 tools\battleengine_measure_mode_catalog_test.py
  py -3 tools\battleengine_campaign_scalar_status_test.py
  ```

  Expected: FAIL because shield remains offline-only and the report omits live measure modes.

- [ ] **Step 3: Update catalog, report, docs, and package routing**

  Move `shield` into `MEASURE_MODE_CATALOG` with walker vehicle, shield scaffold module, and `sampler-wired; live dual-accept pending`. Emit both `liveMeasureModes` and `offlineHarnesses` in the campaign status report. Update the human status and shield plan to distinguish live wiring from live evidence.

  Add adjacent package scripts:

  ```json
  "test:battleengine-walker-trajectory-measurement": "py -3 tools\\run_battleengine_walker_trajectory_measurement_test.py",
  "test:battleengine-walker-measurement-contract": "npm run test:battleengine-walker-trajectory-sampler && npm run test:battleengine-walker-trajectory-measurement && npm run test:battleengine-shield-scaffold && npm run test:battleengine-measure-mode-catalog"
  ```

  Document this focused gate in the existing runtime-helper command guidance without adding it to `test:runtime-tooling-safety`.

- [ ] **Step 4: Run GREEN through the working npm shim**

  Run:

  ```powershell
  C:\Users\david\AppData\Roaming\npm\npm.cmd run test:battleengine-walker-measurement-contract
  C:\Users\david\AppData\Roaming\npm\npm.cmd run test:battleengine-campaign-scalar-status
  ```

  Expected: all focused suites pass and the status reporter exits zero.

### Task 4: Verification, Review Envelope, Authority Audit, And State

**Files:**
- Modify only files already listed plus `goal.md` and `goal.campaign.md` if verified state materially changes.

**Interfaces:**
- Consumes: complete diff, focused tests, runtime authority fields, and reviewer findings.
- Produces: accepted offline readiness advancement; either a fully authorized two-attempt live pair or a precise live blocker followed by the next safe slice.

- [ ] **Step 1: Run proportional offline verification**

  Run serially:

  ```powershell
  py -3 -m py_compile tools\battleengine_shield_scaffold.py tools\battleengine_walker_trajectory_sampler.py tools\run_battleengine_walker_trajectory_measurement.py tools\battleengine_measure_mode_catalog.py tools\battleengine_campaign_scalar_status.py
  C:\Users\david\AppData\Roaming\npm\npm.cmd run test:battleengine-walker-measurement-contract
  C:\Users\david\AppData\Roaming\npm\npm.cmd run test:battleengine-campaign-scalar-status
  C:\Users\david\AppData\Roaming\npm\npm.cmd run test:doc-commands
  git diff --check
  ```

  Do not run full `npm test`, native Godot, WinUI, or BEA for this nonvisual offline readiness change.

- [ ] **Step 2: Obtain the one required review envelope**

  Dispatch bounded read-only normal and adversarial Codex reviewers over the exact diff. Run sanitized normal and adversarial Cursor consults without local paths, credentials, proprietary payloads, raw runtime evidence, or action authority. Resolve every substantive finding and re-run affected gates.

- [ ] **Step 3: Audit live authority without broad-reading local payload roots**

  Confirm the baton names the runtime action family, exact allowed and forbidden commands, two-attempt lease, exact private proof-root policy, validation gates, cleanup/rollback, and expiration. If any field is absent, do not launch BEA: record one well-formed blocker with `code`, `evidence`, `prior_attempt`, `owner`, `next_action`, `retry_after`, and `duplicate_check`, then select the next safe independent campaign slice.

- [ ] **Step 4: If and only if authority is complete, execute the bounded pair**

  Use only the tracked runner, copied executable, ignored/app-owned roots, and exactly two attempts. A first-attempt failure prevents attempt two under the existing runner; either failed attempt forbids a public contract. Require full receipt identity, cleanup, distinct receipts, pair eligibility, compact evidence, and post-run zero relevant-process census.

- [ ] **Step 5: Land state and continue**

  Update the shield plan and baton with only verified truth. Publish a v1 contract/policy/Core mapping only if two accepted attempts justify it. Otherwise keep Core provisional, commit and push the reviewed offline advancement/blocker state, and immediately continue with the next highest-value authorized slice from `goal.campaign.md`.
