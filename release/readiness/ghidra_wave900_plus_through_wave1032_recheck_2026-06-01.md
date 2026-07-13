# Ghidra Wave900+ Through Wave1032 Recheck

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004530a0` → `CTweak__dtor_base_thunk_004530a0` (was `CTweak__dtor_unlink_from_static_list_004530a0`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: validation passed; later static closeout supersession verified by Wave1220
Date: 2026-06-01
Scope: `wave900-plus-through-wave1032-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1032. It validates the Wave1032 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1031 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1032-recheck
```

Coverage anchors:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1032 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1032 --check`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1032 readiness/evidence anchor: `tweak-reconnect-interface-review-wave1032`, `0x00527c90 CReconnectInterface__ctor`, `0x00527d00 CReconnectInterface__VFunc_07_00527d00`, `0x00528690 CTweak__ctor_base`, `0x005286b0 CTweak__dtor_base`, `0x00528b20 CTweakInt_SetNumViewpoints__ctor`, `0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl`, `0x004530a0 CTweak__dtor_base_thunk_004530a0`, `0x0054d4ac`, `631/1408 = 44.82%`, `860/1493 = 57.60%`, `500/500 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified`, no mutation.

Boundary:

- This recheck validates static evidence structure, backups, apply/read-only logs, focused probe classifications, and current queue closure.
- It does not prove runtime behavior, exact source-layout identity, gameplay outcomes, BEA patching, or rebuild parity.

Probe token anchor: Wave1032; wave900-plus-through-wave1032-recheck; tweak-reconnect-interface-review-wave1032; 0x00527c90 CReconnectInterface__ctor; 631/1408 = 44.82%; 860/1493 = 57.60%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified.
