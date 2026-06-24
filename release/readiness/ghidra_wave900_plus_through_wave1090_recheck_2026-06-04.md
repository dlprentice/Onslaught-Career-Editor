# Ghidra Wave900+ Through Wave1090 Recheck Note

Status: validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1090-recheck`

This note extends the post-Wave900 recheck chain through Wave1090 and records the passed local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1090-recheck
```

Wave1090 (`cdebris-lifecycle-render-review-wave1090`) re-read the seven saved `CDebris` lifecycle, metadata, render, and imposter-render rows with no mutation. The focused readiness note is [`ghidra_cdebris_lifecycle_render_review_wave1090_2026-06-04.md`](ghidra_cdebris_lifecycle_render_review_wave1090_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1534/1560 = 98.33%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- CDebris vtable `0x005daf14` exports `48` OK slots; key slots include `CDebris__Init`, `CDebris__dtor_base`, `CDebris__Render`, and `CDebris__RenderImposter`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-135715_post_wave1090_cdebris_lifecycle_render_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime debris rendering, concrete `CDebris` layout, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- Readiness notes: `193`.
- Covered waves: `191`.
- Package probe scripts: `189`.
- Evidence bases: `189`.
- Backup references: `191`.
- Apply scripts: `69`.
- Wave982-Wave1090 direct probes: `109` results, `1` direct pass, `108` expected stale-state/rolled-doc/historical-live-queue failures, `0` disallowed evidence/unclassified failures.
- Current queue: `6410` functions, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1090; cdebris-lifecycle-render-review-wave1090; 0x004411a0 CDebris__Init; 0x00441320 CDebris__dtor_base; 0x004413a0 CDebris__Render; 0x00441420 CDebris__RenderImposter; 0x005daf14; grs_tuft1.MSH; DAT_0066eb78; DAT_0063012c; 1534/1560 = 98.33%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-135715_post_wave1090_cdebris_lifecycle_render_review_verified; no mutation.
