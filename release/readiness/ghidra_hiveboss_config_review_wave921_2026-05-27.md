# Ghidra Wave921 HiveBoss config review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `hiveboss-config-review-wave921`

## Scope

Wave921 reviewed HiveBoss config, init, and adjacent motion-controller helpers from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x0047fe30` | `CHiveBoss__Init` | Reviewed; no mutation |
| `0x004804c0` | `CHiveBoss__SetVar` | Reviewed; no mutation |
| `0x00497090` | `CMCHiveBoss__Constructor` | Reviewed; no mutation |
| `0x00497110` | `CMCHiveBoss__ScalarDeletingDestructor` | Reviewed; no mutation |
| `0x004976d0` | `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave921-hiveboss-config-review/metadata.tsv
subagents/ghidra-static-reaudit/wave921-hiveboss-config-review/tags.tsv
subagents/ghidra-static-reaudit/wave921-hiveboss-config-review/instructions.tsv
subagents/ghidra-static-reaudit/wave921-hiveboss-config-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave921-hiveboss-config-review/decompile/
```

Read-back result:

```text
metadata: 5/5 OK
tags: 5/5 OK
xrefs: 5 rows
instructions: 1045 rows
decompile: 5/5 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. `CHiveBoss__SetVar` remains the Wave911 focused risk row, but fresh instruction read-back confirms the `RET 0x8` two-argument config handler shape, repeated `hb_*` string comparisons, guide-field writes through `this+0x208`, HiveBoss float writes around `this+0x284..0x2a0`, and fallback to `CComplexThing__SetVar`.

The adjacent init and motion-controller helpers also remain coherent with the existing Wave397/Wave432 saved corrections: `CHiveBoss__Init` allocates the destructable-segment controller, constructs `CMCHiveBoss`, calls `CUnit__Init`, resolves `core2`, creates the guide object, and seeds HiveBoss fields; the `CMCHiveBoss` helpers remain tied to vtable `0x005dc388` and cylinder-transform behavior.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260527-172645_post_wave921_hiveboss_config_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected HiveBoss config/init/motion helpers. It does not prove runtime HiveBoss behavior, concrete `CHiveBoss` or `CMCHiveBoss` layouts, source-body identity, BEA patch behavior, or rebuild parity.

## Next

Continue Wave922 with another focused cluster from Wave911, preferably frontend text/layout helpers or another source-evidenced family where stale-owner/source-parity evidence may provide correction opportunities.
