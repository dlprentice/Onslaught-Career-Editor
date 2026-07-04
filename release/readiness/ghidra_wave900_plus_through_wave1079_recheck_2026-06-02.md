# Ghidra Wave900+ Through Wave1079 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1079-recheck`

This note extends the post-Wave900 recheck chain through Wave1079 and records the Wave1079 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1079-recheck
```

Wave1079 (`texture-tga-table-review-wave1079`) recovered and saved one previously unresolved CTGALoader vtable slot-8 function boundary at `0x004f2cc0 CTGALoader__HasNonzeroStatusOut_004f2cc0`. The focused readiness note is [`ghidra_texture_tga_table_review_wave1079_2026-06-02.md`](ghidra_texture_tga_table_review_wave1079_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `182`
- Covered waves: `180`
- Package probe scripts: `178`
- Evidence bases: `178`
- Backup references: `180`
- Apply scripts: `59`
- Wave982-Wave1079 direct probes: `resultCount=98`, `passCount=1`, `failCount=97`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6262`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6262/6262 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1373/1560 = 88.01%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified`, `19` files, `174754695` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual name, exact status-output field semantics, runtime TGA/image-loading behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1079; texture-tga-table-review-wave1079; 0x004f2cc0 CTGALoader__HasNonzeroStatusOut_004f2cc0; 0x005df518; 0x005df538; 0x004f2ce0 CTGALoader__Load; 0x00616dd0; 812/1408 = 57.67%; 1373/1560 = 88.01%; 500/500 = 100.00%; 6262/6262 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified; boundary recovery.
