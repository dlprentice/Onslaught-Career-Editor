# Ghidra CEngine Viewpoint Signature Tranche - 2026-05-13

Status: GREEN public-safe static Ghidra signature evidence.

This wave corrected and hardened a compact CEngine resource/viewpoint/landscape-damage neighborhood after source comparison, serialized dry/apply/read-back, and a verified live Ghidra project backup. The saved labels are behavior-bounded static retail Ghidra evidence; they are not runtime engine behavior proof.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00449820` | `CEngine__ctor` | Constructor-style body installs the engine vtable, initializes camera/view/clipping/resource fields, and clears resource pointers. |
| `0x00449890` | `CEngine__Shutdown` | Shutdown path releases screen effects, shadows, trees, gamut, landscape, camera/water/map/HUD resources, and trims VB/IB pool context. |
| `0x004499d0` | `CEngine__Init` | Init path wires cvars and resource systems, initializes gamut/map/water/landscape/HUD/light/screen-effect/shadow/tree context, and returns success/failure. |
| `0x00449d50` | `CEngine__InitResources` | Loads zoom, blob-shadow, hilight, hit-effect, cloak, cloud-shadow, and tree-shadow texture/resource context. |
| `0x00449dc0` | `CEngine__LoadAllNamedMeshes` | Corrected from the older `CWorld__LoadNamedMeshCacheFromBuffer` label; `RET 0x4`, named-mesh loading text, mesh lookup/reuse/create context, and `dataFile` argument evidence. |
| `0x00449ef0` | `CEngine__GetViewMatrixFromCamera` | Corrected from the older `CFrontEnd__BuildCameraBasisFromYaw` label; `RET 0x8`, pitch basis, camera orientation vfunc, and matrix multiply/copy context. |
| `0x0044a020` | `CEngine__SetViewpoint` | Viewpoint wrapper with `RET 0x10`, viewport/player/camera context, and a saved four-stack-argument signature. |
| `0x0044a0d0` | `CEngine__SelectViewpoint` | Current-viewpoint setter with `RET 0x4`, engine field `+0x4ac`, and D3DDevice viewport context. |
| `0x0044a110` | `CEngine__ResetPos` | Corrected from the older `CCutscene__ResetLandscape` label; `RET 0x8`, engine landscape pointer at `+0x10`, and X/Y reset helper context. |
| `0x0044a130` | `CEngine__InitDamageSystem` | Corrected from the older `CGame__RebuildLandscapeDamageStamps` label; damage table/tree-entry setup, damage stamps, current-damage tracking, and landscape reset context. |

Evidence:

- `tools/ApplyEngineViewpointSignatureTranche.java` dry/apply passed with dry `targets=10 updated=0 skipped=10 failed=0` and apply `targets=10 updated=10 skipped=0 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `10` metadata rows, `10` decompile exports, `10` xref rows, `10` tag rows, `180` focused instruction rows, `10` focused xref evidence hits, and `10` focused instruction evidence hits.
- Focused validation passed: `py -3 tools\ghidra_engine_viewpoint_signature_probe_test.py`, `py -3 -m py_compile tools\ghidra_engine_viewpoint_signature_probe.py tools\ghidra_engine_viewpoint_signature_probe_test.py`, and `cmd.exe /c npm run test:ghidra-engine-viewpoint-signature`.
- The focused probe reports `0` stale target-name hits, `0` stale target-signature hits, and `0` overclaim hits.
- The refreshed all-functions baseline reports `6008` total functions, `0` legacy weak names, `1948` undefined signatures, and `2025` `param_N` signatures.
- The refreshed quality queue reports `6008` functions, `1232` commented functions, `4776` commentless functions, `1948` undefined signatures, and `2025` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1232/6008 = 20.51%`, strict clean-signature `1170/6008 = 19.47%`. The `20%` value is not a milestone or acceptance gate; the objective remains as close to `100%` evidence-grade static RE as possible.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_030711_post_wave360_engine_viewpoint_verified` with `19` files, `153095047` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/engine-viewpoint-wave360/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects and hardens ten CEngine resource/viewpoint/landscape-damage targets, but it does not prove exact Stuart-source method identities, concrete CEngine/landscape/resource layouts, local/type recovery, runtime engine/render/viewpoint behavior, BEA launch, game patching, or rebuild parity.
