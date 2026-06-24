# Ghidra Wave900+ Through Wave1034 Recheck

Status: validation passed; later static closeout supersession verified by Wave1220
Date: 2026-06-01
Scope: `wave900-plus-through-wave1034-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1034. It validates the Wave1034 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1033 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1034-recheck
```

Expected coverage:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1034 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1034 --check`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1034 readiness/evidence anchor: `mapwho-spatial-query-review-wave1034`, `0x00491900 CMapWhoEntry__Init`, `0x00491d80 CMapWho__SetIteratorFromSectorHead`, `0x00491ea0 CMapWho__GetFirstEntryWithinRadius`, `0x00492110 CMapWho__GetFirstEntryWithinLine`, `0x00492670 CMapWho__WorldToSector`, `0x00492860 CMapWho__DebugDrawSector`, `0x00492ba0 CMapWhoEntry__SetPosition`, `0x00492c90 CMapWhoEntry__GetOwner`, `660/1408 = 46.88%`, `889/1493 = 59.54%`, `500/500 = 100.00%`, `G:\GhidraBackups\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified`, no mutation.

Boundary:

This is structural static evidence validation. It does not prove runtime spatial queries, runtime collision/render/tree/AI targeting behavior, exact source-body identity, concrete MapWho layouts beyond observed offsets, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1034; wave900-plus-through-wave1034-recheck; mapwho-spatial-query-review-wave1034; 0x00491ea0 CMapWho__GetFirstEntryWithinRadius; 0x00492110 CMapWho__GetFirstEntryWithinLine; 0x00492670 CMapWho__WorldToSector; 660/1408 = 46.88%; 889/1493 = 59.54%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified.
