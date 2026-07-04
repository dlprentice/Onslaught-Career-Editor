# Ghidra CEngine Render / Resource Signature Tranche - 2026-05-13

Status: GREEN static Ghidra signature evidence

This note records a public-safe saved-signature tranche for four adjacent CEngine render/resource helper targets. It is static retail Ghidra evidence only. It does not prove exact Stuart-source method identity, concrete class layouts, local variables, recovered types, runtime render/resource behavior, BEA launch behavior, game patching, or rebuild parity.

## Targets

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0044a1c0` | `CEngine__UpdatePos` | `RET 0x4`, landscape/render-position context, and CEngine field references around current viewpoint/update-position behavior. |
| `0x0044a1f0` | `CEngine__LoadMixers` | Corrected from stale `CResourceAccumulator__LoadAndCopyMixerTextureSet`; `RET 0x4`, `CMapTex` mixer-load context, set argument, and copied mixer level context. |
| `0x0044a2a0` | `CEngine__SetKempyCube` | Corrected from stale `CResourceAccumulator__InitKempyCubeResources`; CEngine singleton caller evidence and KempyCube resource-selection context. |
| `0x0044a2c0` | `CEngine__SetWater` | Corrected from stale `CResourceAccumulator__ReloadWaterRenderTextures`; CEngine singleton caller evidence and water texture/reload resource-selection context. |

## Evidence

- `ApplyEngineRenderResourceSignatureTranche.java` dry/apply passed serially. Dry reported `targets=4 updated=0 skipped=4 failed=0`; apply reported `targets=4 updated=4 skipped=0 failed=0` and `REPORT: Save succeeded`.
- Post-apply read-back verified `4` metadata rows, `4` decompile exports, `4` xref rows, `4` tag rows, and `324` focused instruction rows.
- The focused probe reported `Status: PASS`, `4` xref evidence hits, `4` instruction evidence hits, `0` stale target-name hits, `0` stale target-signature hits, and `0` overclaim hits.
- Focused validation passed: `py -3 tools\ghidra_engine_render_resource_signature_probe_test.py`, `py -3 -m py_compile tools\ghidra_engine_render_resource_signature_probe.py tools\ghidra_engine_render_resource_signature_probe_test.py`, and `cmd.exe /c npm run test:ghidra-engine-render-resource-signature`.
- The refreshed all-functions baseline reports `6008` total function objects, `0` weak functions, `1948` undefined signatures, and `2022` `param_N` signatures.
- The refreshed quality queue reports `1235` commented functions and `4773` commentless functions.
- Current confirmation proxies are telemetry only: comment-backed `1235/6008 = 20.56%`; strict clean-signature `1173/6008 = 19.52%`. The `20%` value is not a milestone.
- The actual live Ghidra project backup is verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_035100_post_wave361_engine_render_resource_verified` with `19` files, `153095047` bytes, and `HashDiffCount=0`.

Raw Ghidra exports, logs, and probe JSON are intentionally kept under ignored `subagents/ghidra-static-reaudit/engine-render-resource-wave361/current/`.
