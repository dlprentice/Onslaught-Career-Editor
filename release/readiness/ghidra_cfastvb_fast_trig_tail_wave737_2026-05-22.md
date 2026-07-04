# Ghidra CFastVB Fast Trig Tail Wave737 Readiness Note

Status: passed
Date: 2026-05-22

Wave737 CFastVB fast trig tail saved comments/tags/signatures for six adjacent fast trigonometric helper rows with the `cfastvb-fast-trig-tail-wave737` and `wave737-readback-verified` tags. The pass hardened two visible vec4 sine/cosine signatures, left four locked packed-MMX helper signatures comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005b81d0 CFastVB__SinCosApproxVec4_Paired` | `void __stdcall CFastVB__SinCosApproxVec4_Paired(float * angle_vec4, float * out_sin_vec4, float * out_cos_vec4)` | RET `0xc` helper called by `CFastVB__DispatchOp_EulerToQuaternion_0059f4f1`; reads four angle lanes and writes sine-like and cosine-like vec4 outputs. |
| `0x005b83b9 CFastVB__SinCosVec4Approx` | `void __stdcall CFastVB__SinCosVec4Approx(float * angle_vec4, float * out_sin_vec4, float * out_cos_vec4)` | RET `0xc` helper called by `CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf`; reads four angle lanes and writes sine-like and cosine-like vec4 outputs. |
| `0x005b85c0 Math__Atan2ApproxPacked` | `int Math__Atan2ApproxPacked(void)` | Comment/tag-only packed atan2-style helper called by quaternion pair interpolation; Ghidra still reports locked hidden `MM0`/`MM1` inputs and a stale EAX-style return. |
| `0x005b86c0 CFastVB__FastAcosApprox_Scalar` | `int CFastVB__FastAcosApprox_Scalar(void)` | Comment/tag-only fast acos-style helper called by axis-angle extraction, quaternion normalization fallback, and spline blending paths; hidden `MM0` ABI remains deferred. |
| `0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar` | `uint CFastVB__FastTrigPairApprox_Scalar(void)` | Comment/tag-only fast trig-pair helper used by axis-angle quaternion, spline, and rotation-matrix dispatch paths; packed register return and neighboring no-function xref boundaries remain deferred. |
| `0x005b8da0 CFastVB__FastSinApprox_Scalar_005b8da0` | `uint CFastVB__FastSinApprox_Scalar_005b8da0(void)` | Comment/tag-only fast sine-style helper used by quaternion interpolation, quaternion normalization fallback, and spline blending paths; packed register ABI remains deferred. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`, then final dry `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `6` metadata rows, `6` tag rows, `30` xref rows, `1686` instruction rows, and `6` decompile rows; read-only caller/xref-site context exports verified `9` caller decompile rows and `1110` xref-site instruction rows.
- Queue refresh passed with `6098` total functions, `4339` commented, `1759` commentless, `1216` exact-undefined signatures, `43` `param_N` signatures, comment-backed proxy `4339/6098 = 71.15%`, and strict clean-signature proxy `4281/6098 = 70.20%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-123343_post_wave737_cfastvb_fast_trig_tail_verified`, `19` files, `166955911` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact polynomial identity, packed register ABI, packed lane layout, floating-point accuracy, runtime math behavior, no-function caller boundaries, source identity, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave737 CFastVB fast trig tail`, `cfastvb-fast-trig-tail-wave737`, `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`, `0x005b83b9 CFastVB__SinCosVec4Approx`, `0x005b85c0 Math__Atan2ApproxPacked`, `0x005b86c0 CFastVB__FastAcosApprox_Scalar`, `0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar`, `0x005b8da0 CFastVB__FastSinApprox_Scalar_005b8da0`, `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-123343_post_wave737_cfastvb_fast_trig_tail_verified`.
