# WinUI Original Binary Second-Host Live Candidate Gate

Status: contract/self-test gate added; no live proof claimed
Date: 2026-06-22
Scope: `winui-original-binary-second-host-live-candidate-gate`

This slice adds an explicit fail-closed wrapper for the next online multiplayer promotion step. The wrapper separates normal checker/self-test success from private live-candidate validation so a green aggregate cannot be misread as second-host netplay proof.

Accepted private candidate summaries carry scope `private-candidate-validation-not-host-join-enablement`. Online play is not available in this release, and Host/Join remains disabled unless a later separate product/release promotion gate is intentionally added and validated.

Tracked surface:

| Item | Purpose |
| --- | --- |
| `tools/winui_original_binary_second_host_live_candidate_gate.py` | Validates private command-source live candidates, private runtime-causality candidates, and their composite payload/invitation binding. |
| `tools/winui_original_binary_second_host_live_candidate_gate_test.py` | Regression tests for missing env vars, fixture rejection, self-test artifact rejection, hash mismatch rejection, and non-enabling composite success. |
| `test:winui-original-binary-second-host-live-candidate-gate` | Public-safe self-test for the fail-closed wrapper. |
| `test:winui-original-binary-second-host-command-source-live` | Env-gated private command-source candidate validation. |
| `test:winui-original-binary-second-host-runtime-causality-candidate` | Env-gated private runtime-causality candidate validation. |
| `test:winui-original-binary-host-join-candidate-gate` | Env-gated composite candidate validation. |

Boundary:

- No BEA launch.
- No CDB attach.
- No Ghidra mutation.
- No patch bytes applied.
- No accepted live second-host command-source proof.
- No accepted live second-host runtime-causality proof.
- No Host/Join enablement.
- No player-ready netplay, public matchmaking, or native BEA netcode.
- No private proof paths, raw invitation data, secrets, copied-game roots, or raw runtime evidence are recorded in this public-safe note.

Candidate validation requires operator-supplied private paths:

```powershell
$env:SECOND_HOST_COMMAND_SOURCE_BUNDLE = "<private-proof-root>\command-source-bundle.json"
$env:SECOND_HOST_RUNTIME_CAUSALITY_CANDIDATE = "<private-proof-root>\runtime-causality-candidate.json"
npm run test:winui-original-binary-host-join-candidate-gate
```

Even if the private candidate gate passes later, Host/Join remains disabled until a separate product/release promotion gate is intentionally added and validated.
