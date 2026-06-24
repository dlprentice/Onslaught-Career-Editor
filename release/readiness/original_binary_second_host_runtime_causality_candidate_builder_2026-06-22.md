# Original Binary Second-Host Runtime-Causality Candidate Builder Readiness Note

Status: preflight/materializer gate added
Date: 2026-06-22
Scope: `second-host-runtime-causality-candidate-builder`

This slice adds `tools/build_winui_original_binary_second_host_runtime_causality_candidate.py` and package script `test:winui-original-binary-second-host-runtime-causality-builder`.

What is proven:

| Evidence | Result |
| --- | --- |
| File-backed self-test candidate | The builder can write a candidate under the private runtime proof root that the strict runtime-causality checker accepts only with explicit fixture mode. |
| Current executor rejection | The builder rejects the current host-authority-derived compatibility runtime executor without writing a candidate. |
| Truthy edit rejection | The builder also rejects compatibility executor artifacts whose second-host runtime/delivery booleans are edited to look live. |
| Public command wiring | `test:winui-original-binary-second-host-runtime-causality-builder` runs the builder unit tests and builder self-test. |

Non-claims:

- No BEA launch is added by this slice.
- No CDB attach is added by this slice.
- No live source-bound second-host runtime causality is accepted.
- No Host/Join control is enabled.
- No public endpoint, public matchmaking, or native BEA netcode is implemented.
- No player-ready netplay or active P3/P4 original-binary runtime gameplay is proven.

Next proof boundary:

A future accepted live candidate must consume a real distinct-host or explicitly VM-labeled command-source proof and bind its accepted payload plus invitation lifecycle hashes through scheduler, bridge, runtime input-window, exact-PID CDB, mapped P2 sequence, host-helper delivery, copied-runtime artifact, copied executable hash, and process identity raw material in one same-run private proof chain.
