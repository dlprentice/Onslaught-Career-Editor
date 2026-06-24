//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBComposeTransformTailWave898 extends GhidraScript {
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
            "cfastvb-compose-transform-tail-wave898",
            "wave898-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-cfastvb-math-infrastructure",
            "raw-commentless-tail",
            "compose-transform-tail"
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
                "0x005a9f44",
                "CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44",
                "int CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44(void)",
                "Wave898 static read-back: CFastVB compose-transform/project dispatch row referenced as DATA by CFastVB__InitDispatchOpsFromFeatureFlags at 0x005984ea. Static retail Ghidra evidence only: preserves the current name/signature while the body forms a 3-bit selector from nullable matrix inputs, uses jump table 0x005aa0ac, initializes identity or selects/multiplies matrices through CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78, then calls CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced and optionally remaps the projected output through the pointer at EBP+0x10 before RET 0x18. Exact dispatch slot schema, optional-input layout, projected-output remap meaning, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "matrix-compose", "projected-vec3-remap")
            ),
            new Spec(
                "0x005aa0cc",
                "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar",
                "int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar(void)",
                "Wave898 static read-back: scalar optional-input compose-transform row referenced as DATA by CFastVB__InitDispatchOpsFromFeatureFlags at 0x005984f1. Static retail Ghidra evidence only: preserves the current name/signature while the body forms a 3-bit selector from nullable matrix inputs, uses jump table 0x005aa2d2, composes matrices with CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78, inverts via CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637, optionally remaps the input vector through the pointer at EBP+0x10, then calls CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced before RET 0x18. Exact dispatch slot schema, optional-input layout, remap semantics, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "scalar-compose-transform", "matrix-inverse")
            ),
            new Spec(
                "0x005aa2f2",
                "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD",
                "int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD(void)",
                "Wave898 static read-back: SIMD optional-input compose-transform row referenced as DATA by CFastVB__InitDispatchOpsFromFeatureFlags at 0x00598684. Static retail Ghidra evidence only: preserves the current name/signature while the body forms a 3-bit selector from nullable matrix inputs, uses jump table 0x005aa424, initializes identity through CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf, composes via CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78, inverts through CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d, optionally remaps the input vector through the pointer at EBP+0x10, then calls CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced before RET 0x18. Exact dispatch slot schema, SIMD-vs-scalar selection policy, optional-input layout, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table-data-xref", "simd-compose-transform", "matrix-inverse")
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
