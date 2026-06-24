//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBSimdTransformTailWave897 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cfastvb-simd-transform-tail-wave897",
            "wave897-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-cfastvb-math-infrastructure",
            "raw-commentless-tail",
            "simd-transform-tail"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("MISSING_READBACK: " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("BADNAME_READBACK: " + spec.address + " got " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("BADSIG_READBACK: " + spec.address + " got " + fn.getSignature());
        }
        String comment = fn.getComment();
        if (comment == null || !comment.equals(spec.comment)) {
            throw new IllegalStateException("BADCOMMENT_READBACK: " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("BADTAGS_READBACK: " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    return;
                }
                stats.renamed++;
                println("RENAME_BLOCKED_BY_POLICY: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getSignature().toString().equals(spec.signature)) {
                println("BADSIG: " + spec.address + " got " + fn.getSignature() + " expected " + spec.signature);
                stats.bad++;
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x005a09f8",
                "CFastVB__ConvertHalfToFloat8_SIMDKernel",
                "void CFastVB__ConvertHalfToFloat8_SIMDKernel(void)",
                "Wave897 static read-back: hidden-register SSE/MMX half-float conversion kernel called by CFastVB__ConvertHalfToFloatArray_SSE at 0x005a0b53. Static retail Ghidra evidence only: preserves the current name/signature while instruction evidence shows packed compare masks, exponent/sign lane shuffling, MULPS scaling, and RET; the decompiler collapses the body because the XMM/MMX ABI is locked/hidden. Exact half-float lane layout, NaN/Inf/subnormal policy, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("half-float-conversion", "hidden-register-abi", "sse-kernel")
            ),
            new Spec(
                "0x005a1c55",
                "CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55",
                "int CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55(void)",
                "Wave897 static read-back: alternate Vec4 batch transform row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x00598365. Static retail Ghidra evidence only: preserves the current name/signature while the body broadcasts a matrix through CFastVB__BroadcastMatrix4x4ToSIMDLanes, runs four-wide SHUFPS/MULPS/ADDPS transform batches, then falls back through CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200 for tail elements before RET 0x18. Exact dispatch-table slot schema, vector/matrix layout, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "vec4-transform-batch", "scalar-tail-fallback")
            ),
            new Spec(
                "0x005a1e5b",
                "CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b",
                "int CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b(void)",
                "Wave897 static read-back: alternate Vec4W batch transform row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x00598347. Static retail Ghidra evidence only: preserves the current name/signature while the body broadcasts the matrix, runs four-wide transform batches, and uses CFastVB__DispatchIndirect_00656f30 for tail dispatch before RET 0x18. Exact dispatch-table slot schema, W-lane contract, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "vec4w-transform-batch", "dispatch-tail-fallback")
            ),
            new Spec(
                "0x005a1fe9",
                "CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9",
                "int CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9(void)",
                "Wave897 static read-back: alternate projected Vec4 batch row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x00598351. Static retail Ghidra evidence only: preserves the current name/signature while instruction/decompile evidence shows matrix broadcast, four-wide projected transform math, RCPPS reciprocal refinement for projected W, and CFastVB__DispatchIndirect_00656f54 tail dispatch before RET 0x18. Exact projection ABI, dispatch-table slot schema, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "projected-vec4-batch", "rcpps-projection")
            ),
            new Spec(
                "0x005a214f",
                "CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f",
                "int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f(void)",
                "Wave897 static read-back: alternate no-offset Vec4 batch transform row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x0059835b. Static retail Ghidra evidence only: preserves the current name/signature while the body runs matrix-broadcast SIMD transform batches without the full offset/translation path and uses CFastVB__DispatchIndirect_00656f44 for tail dispatch before RET 0x18. Exact no-offset contract, dispatch-table slot schema, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "no-offset-vec4-batch", "dispatch-tail-fallback")
            ),
            new Spec(
                "0x005a225f",
                "CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f",
                "int CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f(void)",
                "Wave897 static read-back: alternate perspective Vec4 batch transform row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x0059823e, 0x00598383, and 0x00598389. Static retail Ghidra evidence only: preserves the current name/signature while the body broadcasts matrix lanes, performs four-wide perspective/transform arithmetic, and falls back through CFastVB__DispatchOp_TransformVec2ByMatrix4 for tail elements before RET 0x18. Exact perspective/offset ABI, dispatch-table slot schema, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "perspective-vec4-batch", "scalar-tail-fallback")
            ),
            new Spec(
                "0x005a249d",
                "CFastVB__DispatchOp_TransformVec3WBatch_Alt_005a249d",
                "int CFastVB__DispatchOp_TransformVec3WBatch_Alt_005a249d(void)",
                "Wave897 static read-back: alternate Vec3W batch transform row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x00598379. Static retail Ghidra evidence only: preserves the current name/signature while the body broadcasts matrix lanes, performs four-wide Vec3/W transform batches, and falls back through CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1 before RET 0x18. Exact Vec3W lane contract, dispatch-table slot schema, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "vec3w-transform-batch", "scalar-tail-fallback")
            ),
            new Spec(
                "0x005a266d",
                "CFastVB__TransformProjectVec3ByMatrix4_Batch4",
                "int CFastVB__TransformProjectVec3ByMatrix4_Batch4(void)",
                "Wave897 static read-back: four-at-a-time projected Vec3-by-matrix4 batch row referenced as DATA by CFastVB__InitDispatchTableVariant_0059822c at 0x0059836f. Static retail Ghidra evidence only: preserves the current name/signature while the body broadcasts the matrix, processes four Vec3 inputs per loop, refines RCPPS reciprocals for projected W, writes projected xyz outputs, and falls back through CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786 before RET 0x18. Exact stride ABI, projection math equivalence, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "projected-vec3-batch4", "rcpps-projection")
            ),
            new Spec(
                "0x005a289e",
                "CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD",
                "void CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD(void)",
                "Wave897 static read-back: hidden-register SIMD half-float special-case screen called by CFastVB__ConvertHalfToFloatArray_SIMD at 0x005a29c0. Static retail Ghidra evidence only: preserves the current name/signature while the decompile/instruction evidence checks eight half-float lanes against masks rooted at 0x0065e750 before returning; exact branch meaning, NaN/Inf/subnormal handling, lane layout, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("half-float-conversion", "hidden-register-abi", "special-case-screen")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
    }
}
