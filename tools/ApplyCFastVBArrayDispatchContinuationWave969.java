//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBArrayDispatchContinuationWave969 extends GhidraScript {
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
        String common = "Static retail Ghidra evidence only; exact dispatch-table slot schema, vector/matrix layout, packed lane order, hidden SSE/register ABI, source identity, runtime math/render behavior, BEA patching, and rebuild parity remain unproven.";
        String[] baseTags = new String[] {
            "static-reaudit",
            "cfastvb-array-dispatch-continuation-wave969",
            "wave969-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "dispatch-table-target",
            "cfastvb",
            "array-transform",
            "packed-sse",
            "stack-locked",
            "comment-hardened",
            "signature-hardened"
        };

        return new Spec[] {
            new Spec(
                "0x005a3a40",
                "CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40",
                "Wave969 CFastVB array-dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0xec at 0x005986cf. The block starts after 0x005a3980 RET 0x18, falls back through scalar helper 0x005aa73b for small/tail counts, broadcasts matrix rows into XMM lanes, processes strided Vec2 inputs in batches, applies translation terms, writes transformed Vec4-style output lanes, and returns with RET 0x18 at 0x005a3c9c before 0x005a3ca0. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a3ca0",
                "CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0",
                "Wave969 CFastVB array-dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0xf0 at 0x005986d9. The block starts after 0x005a3c9c RET 0x18, falls back through scalar helper 0x005aa7c9 for small/tail counts, applies matrix rows plus translation terms to strided Vec2 inputs, refines projected W with RCPPS/SUBPS/MULPS, writes projected Vec2 output lanes, and returns with RET 0x18 at 0x005a3ee2 before 0x005a3f00. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a3f00",
                "CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00",
                "Wave969 CFastVB array-dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0xf4 at 0x005986e3. The block starts after 0x005a3ee2 RET 0x18, falls back through scalar helper 0x005aa790 for small/tail counts, batches strided Vec2 inputs across matrix row lanes without translation terms, writes transformed Vec2 output lanes, and returns with RET 0x18 at 0x005a40b3 before 0x005a40c0 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a4160",
                "CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160",
                "Wave969 CFastVB array-dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0xfc at 0x005986bb. The block starts after 0x005a40c0 RET 0x18, falls back through scalar helper 0x005a9f3f for small/tail counts, applies matrix rows plus translation terms to strided Vec3 inputs, refines projected W with RCPPS/SUBPS/MULPS, writes projected Vec3-style output lanes, and returns with RET 0x18 at 0x005a447a before 0x005a4480. Signature is intentionally stack-locked as int(void). " + common,
                baseTags
            ),
            new Spec(
                "0x005a4480",
                "CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480",
                "Wave969 CFastVB array-dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x100 at 0x005986c5. The block starts after 0x005a447a RET 0x18, falls back through scalar helper 0x005a99f8 for small/tail counts, batches strided Vec3 inputs across matrix row lanes without translation terms, writes transformed Vec3-style output lanes, and returns with RET 0x18 at 0x005a46f9 before adjacent target 0x005a46fc. Signature is intentionally stack-locked as int(void). " + common,
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
            throw new IllegalStateException("Wave969 CFastVB array dispatch continuation apply encountered missing/bad rows");
        }
    }
}
