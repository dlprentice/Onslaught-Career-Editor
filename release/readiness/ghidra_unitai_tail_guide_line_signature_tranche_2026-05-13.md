# Ghidra UnitAI Tail / Guide-Line Signature Tranche - 2026-05-13

Status: GREEN public-safe static Ghidra signature evidence.

This wave followed the external stale-reference debt from the UnitAI / DiveBomber / Dropship tranche and corrected the adjacent UnitAI tail, guide constructor, and dropship ground-trace helper labels. It preserved the narrow claim boundary after serialized dry/apply/read-back and a verified live Ghidra project backup.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00447b10` | `CUnitAI__PlayWingUnfoldedAnimationAndSetState5` | Resolves `wingunfolded`, dispatches animation vfunc `+0xf0`, sets state `+0x27c` to `5`, and removes the unit from the occupancy grid. |
| `0x00447b60` | `CUnitAI__HasReachedCachedAnchorPoint` | Checks cached-anchor flag `+0x290` and compares current X/Y to cached `+0x280/+0x284`. |
| `0x00447bb0` | `CUnitAI__GetOrGenerateCachedAnchorPoint` | Corrected to one stack argument, `RET 0x4`; seeds/regenerates cached anchor fields `+0x280..+0x28c`, calls `CUnitAI__IsCachedAnchorPointValid`, and copies the cached anchor to `outAnchorPoint`. |
| `0x00447d50` | `CUnitAI__IsCachedAnchorPointValid` | Validates cached anchors through CMapWho, collision/height context, and occupancy bitmask checks. |
| `0x00447fa0` | `CUnitAI__AdvanceDoorWingAnimationState` | Recognizes `dooropening`, `doorclosing`, `wingfolded`, and `wingunfolded`, dispatches animation, and updates state `+0x27c`. |
| `0x00448110` | `CUnitAI__SetDoorWingState6` | Narrow state helper writing `+0x27c = 6`. |
| `0x00448120` | `CUnitAI__SetDoorWingState7AndMirrorYawOffset` | Writes `+0x27c = 7` and mirrors yaw/offset field `+0x2a4` around the `1.0`-style constant. |
| `0x00448170` | `CDropship__TraceGroundAndSpawnThrusterDust` | Corrected from misleading `CLine__ctor_like_00448170`; stdcall `RET 0x8`, stack-local `CLine`, static heightfield trace, and dropship thruster-dust effect context. |
| `0x0047e290` | `CGuide__ctor_base` | Corrected from constructor-like placeholder wording; one stack argument `guideOwner`, `RET 0x4`, installs the base vtable, stores owner, copies owner fields, clears `+0x1c`, and returns `this`. |
| `0x00415d70` | `CBoatGuide__ctor` | Calls `CGuide__ctor_base(this, guideOwner)`, writes vtable `0x005d8d5c`, and returns `this`. |

Evidence:

- `tools/ApplyUnitAiTailGuideLineSignatureTranche.java` dry/apply passed with dry `targets=10 updated=0 skipped=10 failed=0` and apply `targets=10 updated=10 skipped=0 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `10` metadata rows, `10` decompile exports, `25` xref rows, `10` tag rows, `18050` instruction rows, `11` focused xref evidence hits, and `10` focused instruction evidence hits.
- Focused validation passed: `py -3 tools\ghidra_unitai_tail_guide_line_signature_probe_test.py`, `py -3 -m py_compile tools\ghidra_unitai_tail_guide_line_signature_probe.py tools\ghidra_unitai_tail_guide_line_signature_probe_test.py`, and `cmd.exe /c npm run test:ghidra-unitai-tail-guide-line-signature`.
- The focused probe reports `0` stale target-name hits, `0` stale target-signature hits, and `0` overclaim hits. It allows the intentional old `CLine__ctor_like_00448170` mention only inside the saved correction comment that explains the prior bad label.
- The refreshed all-functions baseline reports `6008` total functions, `0` legacy weak names, `1949` undefined signatures, and `2031` `param_N` signatures.
- The refreshed quality queue reports `6008` functions, `1223` commented functions, `4785` commentless functions, `1949` undefined signatures, and `2031` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1223/6008 = 20.36%`, strict clean-signature `1161/6008 = 19.32%`. The `20%` value is not a milestone or acceptance gate; the objective remains as close to `100%` evidence-grade static RE as possible.
- The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_022050_post_wave359_unitai_tail_guide_line_verified` with `19` files, `153095047` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/unitai-tail-guide-line-wave359/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects and hardens ten UnitAI tail / guide-line targets, but it does not prove exact Stuart-source method identities, concrete UnitAI/Dropship/Guide layouts, local/type recovery, runtime UnitAI/Dropship/Guide behavior, BEA launch, game patching, or rebuild parity.
