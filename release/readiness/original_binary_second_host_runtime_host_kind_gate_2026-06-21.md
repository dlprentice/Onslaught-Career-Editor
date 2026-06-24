# Original Binary Second-Host Runtime-Host-Kind Gate

Status: proof-gate hardening, no new live runtime proof
Date: 2026-06-21
Scope: `original-binary-second-host-runtime-host-kind-gate`

This slice hardens the second-host command-source proof ladder before any Host/Join or runtime-delivery promotion. The command-source bundle contract and live run kit now require a redacted runtime-host-kind field in the host/client identity evidence. Accepted runtime kinds are bounded to `windows-host`, `linux-host`, `macos-host`, and explicitly labeled `vm-guest`; `wsl-on-host`, `container-on-host`, and `unknown-host` are rejected.

The gate keeps the proof classes separate:

| Proof shape | Required runtime-host-kind boundary |
| --- | --- |
| `distinct-vm-private-lan-labeled-vm-only` | Client must be `vm-guest`, and the proof remains VM-labeled / same-physical-machine only. |
| `distinct-physical-host-private-lan` | Client must not be `vm-guest`, and the proof must remain not-same-physical-machine. |
| WSL/container/unknown | Rejected for live second-host command-source promotion. |

2026-06-22 follow-up: the client preflight can now auto-classify real VM guests from bounded platform-owned evidence after container/WSL checks. Manual runtime-kind overrides remain `operator-supplied-runtime-host-kind` and are still attempt-only diagnostics.

Implementation anchors:

- `tools/build_winui_original_binary_second_host_command_source_bundle.py`
- `tools/winui_original_binary_second_host_command_source_client.py`
- `tools/winui_original_binary_second_host_live_readiness.py`
- `tools/winui_original_binary_second_host_live_run_kit.py`
- `tools/winui_safe_copy_online_second_host_command_source_check.py`
- `roadmap/original-binary-online-second-host-command-source.v1.json`

Validation run:

- `py -3 tools\winui_safe_copy_online_second_host_command_source_check_test.py`
- `py -3 tools\build_winui_original_binary_second_host_command_source_bundle_test.py`
- `py -3 tools\winui_original_binary_second_host_command_source_client_test.py`
- `py -3 tools\winui_original_binary_second_host_live_run_kit_test.py`
- `py -3 tools\winui_original_binary_second_host_live_run_kit.py --self-test`
- `py -3 tools\winui_original_binary_second_host_live_run_kit.py --check`
- `npm run test:winui-original-binary-second-host-command-source`
- `npm run test:winui-original-binary-second-host-command-source-builder`
- `npm run test:winui-original-binary-second-host-live-run-kit`
- `npm run test:winui-original-binary-second-host-live-readiness`

Non-claims:

- No BEA process was launched for this slice.
- No CDB attach occurred for this slice.
- No Ghidra mutation occurred.
- No installed Steam game or original `BEA.exe` mutation occurred.
- This is not accepted live second-host command-source proof.
- This is not accepted live second-host runtime-delivery proof.
- This is not Host/Join enablement, public matchmaking, native BEA netcode, or player-ready online multiplayer.

Deployment note: offline safe-copy patch families can eventually behave like "prepare a copied game folder, launch it, and keep the original install untouched." First-generation online multiplayer is different: until a deeper native patch or in-game netcode surface exists, the WinUI app or a packaged companion helper is expected to remain active during an online session to own matchmaking/session identity, invitations, relay/auth, host authority, process cleanup, and safety checks.
