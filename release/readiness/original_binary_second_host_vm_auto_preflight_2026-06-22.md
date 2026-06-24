# Original Binary Second-Host VM Auto Preflight

Status: complete tooling/readiness follow-up, no live command-source proof
Date: 2026-06-22
Scope: `second-host-vm-auto-preflight-not-command-source-proof`

This slice removes a proof-ladder blocker in the original-binary online multiplayer lane. A VM-labeled run kit already required a client `runtimeHostKind=vm-guest`, but manual `--client-runtime-host-kind vm-guest` remained operator-supplied and therefore attempt-only. The client preflight can now auto-classify real VM guests from platform-owned evidence while preserving the proof boundary.

What changed:

| Area | Result |
| --- | --- |
| Runtime host-kind detector | `tools/build_winui_original_binary_second_host_command_source_bundle.py` can now auto-return `vm-guest` when bounded platform evidence contains VM markers such as Hyper-V, VMware, VirtualBox, KVM/QEMU, Xen, Parallels, bhyve, or common cloud VM labels. |
| Precedence | Container and WSL detection still win before VM markers; `wsl-on-host`, `container-on-host`, and `unknown-host` remain non-promotional. |
| Privacy boundary | Raw vendor/model/DMI/CIM strings are only used locally for classification and are not serialized into client preflight output or public docs. |
| Manual override boundary | Manual runtime-kind overrides remain `operator-supplied-runtime-host-kind` and are attempt-only diagnostics, not live validation evidence. |
| Client guidance | The client preflight summary and redacted run-kit templates now say to omit manual runtime-kind overrides for live proof. |
| Run-kit readiness | A VM-labeled live run kit can become `readyToRunLiveCommandSource=true` only when client runtime kind is auto-preflight `vm-guest` and the other private live-candidate inputs are present. |
| Builder output hygiene | Command-source bundles are now written through a same-directory temporary candidate that is validated before atomic replacement, so rejected source-safety drift cannot leave a fresh private proof JSON behind. |

Focused validation passed:

```powershell
py -3 tools\build_winui_original_binary_second_host_command_source_bundle_test.py
py -3 tools\winui_original_binary_second_host_command_source_client_test.py
py -3 tools\winui_original_binary_second_host_live_readiness_test.py
py -3 tools\winui_original_binary_second_host_live_run_kit_test.py
npm run test:winui-original-binary-second-host-command-source-builder
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-live-readiness
npm run test:winui-original-binary-second-host-live-run-kit
```

Non-claims:

- No BEA process was launched.
- No listener was opened.
- No invitation was created.
- No command-source proof was created.
- No CDB attach occurred.
- No Ghidra mutation occurred.
- No installed Steam game or original `BEA.exe` mutation occurred.
- This is not accepted live second-host command-source proof.
- This is not accepted live second-host runtime-delivery proof.
- This is not Host/Join enablement, public matchmaking, native BEA netcode, or player-ready online multiplayer.

Next proof boundary:

Run the live-run kit from a real distinct physical private-LAN host or from a real VM whose client preflight auto-detects `vm-guest`, then create and validate the private command-source bundle with `--live`. Only after that accepted command source exists should the lane move to source-bound copied-runtime causality, separate rendered-session proof, or any Host/Join promotion work.
