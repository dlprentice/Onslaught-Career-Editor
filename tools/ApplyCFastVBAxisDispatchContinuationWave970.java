//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBAxisDispatchContinuationWave970 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean hasAllTags(Function fn, String[] expectedTags) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expectedTags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn) {
        DataType intType = IntegerDataType.dataType;
        return fn.getReturnType() != null
            && (fn.getReturnType().isEquivalent(intType) || fn.getReturnType().getDisplayName().equals(intType.getDisplayName()))
            && fn.getParameterCount() == 0;
    }

    private void applySignature(Function fn) throws Exception {
        fn.setReturnType(IntegerDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            new ParameterImpl[] {}
        );
    }

    private Spec[] specs() {
        String common = "Static retail Ghidra evidence only; exact dispatch-table slot schema, vector/quaternion/matrix layout, packed lane order, hidden MMX/register ABI, source identity, runtime math/render behavior, BEA patching, and rebuild parity remain unproven.";
        String[] baseTags = new String[] {
            "static-reaudit",
            "cfastvb-axis-dispatch-continuation-wave970",
            "wave970-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "dispatch-table-target",
            "cfastvb",
            "quaternion",
            "packed-mmx",
            "stack-locked",
            "comment-hardened",
            "signature-hardened"
        };

        return new Spec[] {
            new Spec(
                "0x005a46fc",
                "CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc",
                "Wave970 CFastVB axis/quaternion dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x4c at 0x0059850d. The block starts after 0x005a46f9 RET 0x18, consumes two packed qword quaternion-like inputs from stack arguments, uses packed multiply/add/subtract lanes with sign masks at 0x005ef118, writes two qword output lanes through the first stack argument, runs FEMMS, and returns with RET 0x0c at 0x005a4792 before 0x005a4795. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a4795",
                "CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795",
                "Wave970 CFastVB axis/quaternion dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x50 at 0x00598514. The block starts after 0x005a4792 RET 0x0c, computes a packed four-float/qword length from the input lanes, gates against threshold constant 0x005ef170, refines reciprocal square root with PFRSQRT/PFRSQIT1/PFRCPIT2, writes normalized qword output lanes, runs FEMMS, and returns with RET 0x08 at 0x005a47ef before 0x005a47f2. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a4836",
                "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836",
                "Wave970 CFastVB axis/quaternion dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this default body into dispatch-table slot +0x60 at 0x00598530. The block starts after 0x005a4833 RET 0x0c, reads matrix-like diagonal/off-diagonal lanes from the input record, selects largest-diagonal/trace-style branches through internal target 0x005a4980, normalizes with packed reciprocal-square-root refinement and constant 0x005ef168, writes quaternion-like qword output lanes, and returns through RET 0x08 terminals at 0x005a4904/0x005a497d/0x005a49f1/0x005a4a4f before feature-override target 0x005a4a52. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a4a52",
                "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52",
                "Wave970 CFastVB axis/quaternion dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this feature-override body into dispatch-table slot +0x60 at 0x005986a6 when feature bits 0x100 and 0x200 are both present. The block starts after 0x005a4a4f RET 0x08, mirrors the packed matrix3x3-to-quaternion branch shape with PMOVMSKB/PFCMPGE mask selection, reciprocal-square-root refinement, constant 0x005ef168 scaling, and qword output writes, then returns with RET 0x08 at 0x005a4c64 before 0x005a4c67. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();

        for (Spec spec : specs()) {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                if (dryRun) {
                    println("WOULD_CREATE: " + spec.address + " " + spec.name);
                    stats.wouldCreate++;
                    continue;
                }
                boolean disassembled = disassemble(address);
                fn = createFunction(address, spec.name);
                if (fn == null) {
                    println("BAD: could not create function at " + spec.address + " disassembled=" + disassembled);
                    stats.bad++;
                    continue;
                }
                stats.created++;
            }

            boolean changed = false;
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    stats.wouldRename++;
                } else {
                    fn.setName(spec.name, SourceType.USER_DEFINED);
                    stats.renamed++;
                    changed = true;
                }
            }

            if (!signatureMatches(fn)) {
                if (dryRun) {
                    println("WOULD_SIGNATURE: " + spec.address + " int " + spec.name + "(void)");
                    stats.signatureUpdated++;
                } else {
                    applySignature(fn);
                    stats.signatureUpdated++;
                    changed = true;
                }
            }

            String comment = fn.getComment();
            if (comment == null || !comment.equals(spec.comment)) {
                if (dryRun) {
                    println("WOULD_COMMENT: " + spec.address);
                    stats.commentOnlyUpdated++;
                } else {
                    fn.setComment(spec.comment);
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (!hasAllTags(fn, spec.tags)) {
                if (dryRun) {
                    println("WOULD_TAGS: " + spec.address);
                    stats.commentOnlyUpdated++;
                } else {
                    for (String tag : spec.tags) {
                        fn.addTag(tag);
                    }
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (changed) {
                stats.updated++;
            } else if (!dryRun) {
                stats.skipped++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave970 CFastVB axis dispatch continuation apply encountered missing/bad rows");
        }
    }
}
