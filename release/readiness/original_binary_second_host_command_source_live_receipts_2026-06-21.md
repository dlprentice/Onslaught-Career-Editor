# Original Binary Second-Host Command-Source Live Receipts

Status: checker/builder hardening; no live second-host proof accepted
Date: 2026-06-21

This slice tightens the second-host command-source proof gate before any real VM or physical second-host run is promoted. It does not launch BEA, attach CDB, send host-helper input, enable Host/Join controls, publish public endpoints, or prove player-ready netplay.

What changed:

| Area | Requirement |
| --- | --- |
| Listener lifecycle | Private non-loopback bind, no wildcard/loopback/public bind, one accepted client, listener close before bundle write, teardown observed, and post-close connect rejection. |
| Source safety | Live candidates must carry two-phase host/client source-safety samples instead of a single preflight assertion. |
| Client postflight | The client sends a signed source-safety postflight before close; the server records acceptance in the transcript. |
| Live validation | `--live` now requires live server/client transcript hardening, live listener receipt evidence, and local-preflight two-phase source safety. |
| JSONL boundary | Command-source JSONL is capped at `4096` bytes before parse. |
| Physical host-kind provenance | Live physical validation rejects `operator-supplied-runtime-host-kind` for both host and client identity evidence. |
| Accepted live summary | The checker summary now reports the live command-source proof field as affirmative only when `--live` validation is requested and passes with non-fixture identity evidence plus per-event monotonic `serverObservedAtUnix` transcript timestamps inside the invitation window; shape/fixture validation reports it as false. |
| Fixture/overclaim rejection | Live validation rejects fixture sentinel auth/identity/source hashes, fixture timestamps/addresses, and hidden Host/Join-style overclaims expressed as string or numeric truthy values. |
| Run-kit material validation | The live-run kit now rejects missing/invalid upstream private-LAN proof, missing/unhashable host copied/install roots, and repo/public invitation paths before ready status; accepted invitation paths must be `.json` files under OS temp and outside the repo. |

Non-claims:

- `acceptedLiveSecondHostCommandSourceProof=false`
- `acceptedLiveSecondHostRuntimeDeliveryProof=false`
- `acceptedLiveSecondHostRuntimeCausalityProof=false`
- shape-valid command-source bundles are not accepted live proof unless a private live candidate passes the env-gated `--live` validator
- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `newBeaLaunchCount=0`
- `cdbAttachCount=0`
- `hostHelperInputSent=false`
- `maxJsonLineBytes=4096`
- `livePhysicalRejectsOperatorSuppliedRuntimeHostKind=true`
- ready run kits require `privateLanProofValidated=true`
- ready run kits require `hostSourceSafetyComputedByPreflight=true`
- ready run kits require `invitationPathValidatedUnderOsTempOutsideRepo=true`
- `--live` validation rejects synthetic live-labeled fixtures without non-fixture identity evidence and server-observed transcript timestamps
- `--live` validation rejects fixture sentinel auth/identity/source hashes and fixture timestamps/addresses
- hidden Host/Join-style overclaims are rejected even as string/numeric truthy values

Focused gates:

```powershell
py -3 tools\winui_safe_copy_online_second_host_command_source_check_test.py
py -3 tools\build_winui_original_binary_second_host_command_source_bundle_test.py
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py --self-test
py -3 tools\build_winui_original_binary_second_host_command_source_bundle.py --self-test
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-command-source-builder
npm run test:winui-original-binary-second-host-live-run-kit
```
