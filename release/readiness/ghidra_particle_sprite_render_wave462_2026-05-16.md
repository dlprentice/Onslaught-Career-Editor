# Ghidra Particle Sprite / Render Helper Wave462 Evidence

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004c8060` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-16

## Scope

Wave462 saved Ghidra signature/comment/tag corrections for `14` particle sprite/render helper targets:

`0x004c0940`, `0x004c14f0`, `0x004c35d0`, `0x004c5280`, `0x004c5c50`, `0x004c5d50`, `0x004c78b0`, `0x004c78d0`, `0x004c7950`, `0x004c8040`, `0x004c8060`, `0x004cab30`, `0x004cac40`, and `0x004cac80`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave462-particle-sprite-render-current/`
- Apply script: `tools/ApplyParticleSpriteRenderWave462.java`
- Probe: `tools/ghidra_particle_sprite_render_wave462_probe.py`
- Test alias: `npm run test:ghidra-particle-sprite-render-wave462`
- Dry summary: `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply summary: `updated=14 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `14` metadata rows, `14` tag rows, `18` xref rows, `14` decompile exports plus `index.tsv`, and `798` focused instruction rows.
- Hardened UV atlas selection, sprite state/update dispatch, particle resource burst setup, transform/vector helpers, expression-driven scale/tint helpers, packed ARGB interpolation, inverse-lerp clamping, and selector normalized-coordinate conversion.
- Queue after refresh: `6057` functions, `2073` commented, `3984` commentless, `1725` undefined signatures, `1603` `param_N` signatures.
- Current telemetry proxies: comment-backed `2073/6057 = 34.23%`; strict comment-plus-clean-signature `2009/6057 = 33.17%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-182636_post_wave462_particle_sprite_render_verified` (`19` files, `156928903` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime particle rendering/sprite behavior, exact descriptor and particle layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
