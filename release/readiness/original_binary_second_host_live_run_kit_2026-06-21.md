# Original Binary Second-Host Live Run Kit Readiness Note

Status: complete public-safe run-kit preflight
Date: 2026-06-21
Scope: `second-host-live-run-kit-not-command-source-proof`

This slice adds a checked live-run kit for the next original-binary second-host command-source attempt. It does not create a private proof bundle. It packages the current host live-readiness result, a future computed client identity/source-safety preflight, required private live-run inputs, and redacted host/client command templates.

Evidence:

| Item | Result |
| --- | --- |
| Schema | `winui-original-binary-second-host-live-run-kit.v1` |
| Focused tool | `tools/winui_original_binary_second_host_live_run_kit.py` |
| Focused tests | `tools/winui_original_binary_second_host_live_run_kit_test.py` |
| Package script | `test:winui-original-binary-second-host-live-run-kit` |
| Current workstation result | `readyToAttemptHarness=false`; `readyForLiveValidationCandidate=false`; `readyToRunLiveCommandSource=false`; `serverCommandInputsComplete=false`; `clientPreflightProvided=false`; `candidatePrivateBindAddressCount=1`; `wslOnHostInterfaceCount=1` |
| Bind-host hardening | `serverCommandInputsComplete=true` now requires an eligible selected private non-WSL bind host when `--bind-host` is supplied |
| Run material hardening | Ready status requires `privateLanProofValidated=true`, `hostSourceSafetyComputedByPreflight=true`, and `invitationPathValidatedUnderOsTempOutsideRepo=true`; paired `--live` command-source validation rejects synthetic live-labeled fixtures without non-fixture identity evidence and server-observed transcript timestamps. |
| Runtime-kind/private-LAN compatibility hardening | The run kit now separates `readyToAttemptHarness` from `readyForLiveValidationCandidate`/`readyToRunLiveCommandSource`. Fixture private-LAN proof such as TEST-NET/documentation `192.0.2.0/24` or fixture sentinel auth/server identity can be attempt-shaped but cannot mark the kit live-ready. VM-labeled readiness requires client `runtimeHostKind=vm-guest` from auto platform preflight; operator-supplied `vm-guest` remains manual attempt evidence only. Physical second-host live readiness requires `runtimeHostKindSource=auto-platform-preflight` and rejects `vm-guest`. |

Focused validation passed:

```powershell
py -3 -m py_compile tools\winui_original_binary_second_host_live_readiness.py tools\winui_original_binary_second_host_live_readiness_test.py tools\winui_original_binary_second_host_live_run_kit.py tools\winui_original_binary_second_host_live_run_kit_test.py
npm run test:winui-original-binary-second-host-live-readiness
npm run test:winui-original-binary-second-host-live-run-kit
```

Non-claims:

- No listener was opened.
- No invitation was created.
- No BEA process was launched.
- No CDB attach occurred.
- No game input was sent.
- No command-source proof was created.
- No Host/Join control may be enabled from this evidence alone.
- No live second-host LAN, public matchmaking, native BEA netcode, runtime delivery, runtime causality, or player-ready netplay is proven.

Next proof boundary:

Use the live-run kit with a distinct private host or explicitly VM-labeled endpoint: produce a computed client preflight, run the redacted host/client command-source flow, validate the private live bundle with `--live`, then bind that accepted command source through scheduler, bridge, copied-runtime input-window, exact-PID CDB, mapped P2 sequence, and host-helper delivery receipts. `--live` requires `machineFingerprintSource=local-hostname-platform-preflight`, `runtimeHostKindSource=auto-platform-preflight`, per-event monotonic `serverObservedAtUnix` timestamps inside the invitation window, and non-fixture auth/identity/source hash values. Private paths, raw invitations, proof bundles, copied game roots, and secrets remain release-excluded.
