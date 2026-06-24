# Original Binary Second-Host Runtime Causality Gate

Status: validator/contract ready; no accepted live second-host runtime causality proof
Date: 2026-06-21
Scope: `second-host-runtime-causality-proof-gate-not-host-join-enable`

This slice adds the public-safe proof gate for the missing rung between a future accepted second-host command-source proof and copied-original-BEA runtime evidence. It does not run BEA, attach CDB, mutate Ghidra, patch an executable, enable Host/Join, publish a public endpoint, or claim player-ready online multiplayer.

New tracked gate:

- `roadmap/original-binary-online-second-host-runtime-causality.v1.json`
- `tools/winui_safe_copy_online_second_host_runtime_causality_check.py`
- `tools/winui_safe_copy_online_second_host_runtime_causality_check_test.py`
- `test:winui-original-binary-second-host-runtime-causality`

The gate requires a future live candidate to stay under the private runtime proof root, use candidate-bundle-relative file references, recompute raw artifact receipts from disk, and bind one same-run chain across:

- accepted second-host command-source proof
- scheduler proof
- bridge proof
- runtime input-window artifact
- exact-PID CDB log
- mapped P2 sequence receipt bound to the runtime input-window artifact
- host-helper delivery receipt bound to the exact-PID CDB artifact
- copied-runtime artifact
- copied-runtime executable hash
- process identity hash

Every raw artifact file must carry a `winui-original-binary-second-host-runtime-causality-artifact-receipt.v1` semantic receipt envelope and a `winui-original-binary-second-host-runtime-causality-raw-evidence.v1` role-specific raw-evidence body with the expected artifact role, hash key, run id, accepted second-host command request payload hash, second-host invitation lifecycle hash, `sourceBound=true`, `sameRunArtifact=true`, `fixtureOrPosthocBinding=false`, and `selfTestOnly=false`. Live validation now also requires concrete raw-evidence body fields for command-source transcript hardening, scheduler relay-plan evidence, bridge mapping, mapped P2 sequence, host-helper delivery, runtime input-window rows, exact-PID CDB log rows, copied-runtime artifact rows, copied-executable byte hash, and process identity. Each role body must name a role-specific raw-evidence material kind and unit count, point to a candidate-bundle-relative private-root-contained raw-material file, and recompute `rawEvidenceSha256` from that file. Receipt-only, envelope-only or hash-only synthetic files, JSON-only forged artifacts, fixture/posthoc, swapped-run, stale-CDB, PID-mismatched, host-authority-derived, mapped-P2/host-helper alias drift, operator-source-safety, unknown source-hash-mode, missing-boundary-key, outside-private-root, private-path-leaking artifacts, hidden truthy Host/Join/direct-input overclaims, and Host/Join-overclaim candidates are rejected. Self-test fixtures require explicit fixture mode and cannot return live-delivery proof booleans.

Current truth remains:

- `acceptedLiveSecondHostRuntimeCausalityProof=false`
- `acceptedLiveSecondHostRuntimeDeliveryProof=false`
- `runtimeInputDerivedFromSecondHostCommandSource=false`
- `runtimeDrivenBySecondHostCommandSource=false`
- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `multiHostLanPlayProof=false`
- `publicMatchmakingProof=false`
- `nativeBeaNetcodeProof=false`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `moreThanTwoOriginalBinaryRuntimePlayersProof=false`

Focused validation:

```powershell
py -3 tools\winui_safe_copy_online_second_host_runtime_causality_check_test.py
py -3 tools\winui_safe_copy_online_second_host_runtime_causality_check.py --self-test
py -3 tools\winui_safe_copy_online_second_host_runtime_causality_check.py --check
npm run test:winui-original-binary-second-host-runtime-causality
py -3 tools\winui_safe_copy_online_host_join_enablement_check_test.py
npm run test:winui-original-binary-host-join-enablement
```

Consults: Codex read-only and adversarial reviewers were used for the proof boundary. The main corrections from adversarial review were that the promotion guard must remain shape-preflight only, that mapped P2 and host-helper receipt aliases must be file-backed rather than shape-only, and that hash-matching file-backed artifacts could still be synthetic without semantic receipt, role-specific raw-evidence checks, material descriptors, hidden-overclaim scanning, and raw-material file hash recomputation. This gate now requires private-root-contained raw-artifact causality receipts before any Host/Join path can treat a second-host command as runtime-delivered.

Next proof boundary: run a real distinct-host or VM-labeled private command-source artifact through scheduler, bridge, runtime input-window, and exact-PID CDB receipts, then validate it through this gate. Until that exists, Host/Join stays blocked.
