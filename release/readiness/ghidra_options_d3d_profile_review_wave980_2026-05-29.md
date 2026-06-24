# Ghidra Wave980 options D3D profile review (2026-05-29)

Status: read-only static review
Date: 2026-05-29
Branch: `main`
Tag: `options-d3d-profile-review-wave980`

## Scope

Wave980 re-reviewed the options-tail display/profile bridge around the remaining D3D device profile Wave911 candidates.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00420b10` | `OptionsTail_Write` | Reviewed; no mutation |
| `0x00420cd0` | `D3DDeviceProfileTable__GetAdapterRecord` | Reviewed; no mutation |
| `0x00420d10` | `D3DDeviceProfile__PackDeviceIndexKey` | Reviewed; no mutation |
| `0x00420d70` | `OptionsTail_Read` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave980-options-d3d-profile-review/metadata.tsv
subagents/ghidra-static-reaudit/wave980-options-d3d-profile-review/tags.tsv
subagents/ghidra-static-reaudit/wave980-options-d3d-profile-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave980-options-d3d-profile-review/instructions.tsv
subagents/ghidra-static-reaudit/wave980-options-d3d-profile-review/decompile/
```

Read-back result:

```text
metadata: 4/4 OK
tags: 4/4 OK
xrefs: 6 rows
instructions: 512 rows
decompile: 4/4 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. `OptionsTail_Write` writes the persisted display/profile key through `D3DDeviceProfileTable__GetAdapterRecord` and `D3DDeviceProfile__PackDeviceIndexKey`; `OptionsTail_Read` reuses `D3DDeviceProfile__PackDeviceIndexKey` while restoring display/audio/control/language settings and fallback rendering state.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260529-145018_post_wave980_options_d3d_profile_review_verified
files=19
bytes=173804423
MissingCount=0
ExtraCount=0
HashDiffCount=0
```

## Truth Boundary

This review confirms static Ghidra coherence for selected options-tail and D3D profile helpers. It does not prove exact options-tail layout names, runtime display/profile persistence, Direct3D device-selection behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave981 from the next Wave911 focused candidate.
