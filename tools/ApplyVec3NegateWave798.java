//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyVec3NegateWave798 extends GhidraScript {
    private static final String ADDRESS = "0x004404f0";
    private static final String OLD_NAME = "CThing__NegateVec3ToOut";
    private static final String NEW_NAME = "Vec3__NegateToOut";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave798 static read-back: owner-neutral Vec3 negate-to-output helper. Instruction evidence reads ECX as the source Vec3, loads X/Y/Z through [ECX], [ECX+4], and [ECX+8], applies FCHS to each component, writes the negated vector to the single stack output pointer at [ESP+4], and returns with RET 0x4. Broad xrefs from CDXEngine__BuildDirectionalSampleRing, CThing__RenderDebugVolumeOverlay, CMCMech__UpdateBone, CMCBuggy__UpdateWheel, CCylinder__ResolveCollisionVFunc02, and CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore make the older CThing-specific owner label too narrow. Static retail Ghidra evidence only; concrete Vec3 type/layout recovery, exact source identity, runtime math/collision/render behavior, BEA patching, and rebuild parity remain unproven.";
    private static final String[] TAGS = {
        "static-reaudit",
        "vec3-negate-wave798",
        "wave798-readback-verified",
        "retail-binary-evidence",
        "name-corrected",
        "signature-corrected",
        "comment-hardened",
        "vector-math",
        "owner-neutral"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private String expectedSignature(ParameterImpl[] params) {
        StringBuilder sb = new StringBuilder();
        sb.append("void ").append(CALLING_CONVENTION).append(" ").append(NEW_NAME).append("(");
        for (int i = 0; i < params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(params[i].getDataType().getDisplayName()).append(" ").append(params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean signatureMatches(Function fn, ParameterImpl[] params) {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), VoidDataType.dataType)) {
            return false;
        }
        if (fn.getParameterCount() != params.length) {
            return false;
        }
        for (int i = 0; i < params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = params[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> actual = tagNames(fn);
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void verifyReadBack(ParameterImpl[] params) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!fn.getName().equals(NEW_NAME)) {
            throw new IllegalStateException("Read-back name mismatch at " + ADDRESS + ": " + fn.getName());
        }
        if (!signatureMatches(fn, params)) {
            throw new IllegalStateException("Read-back signature mismatch at " + ADDRESS + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(COMMENT)) {
            throw new IllegalStateException("Read-back comment mismatch at " + ADDRESS);
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back tag mismatch at " + ADDRESS);
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyVec3NegateWave798 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        ParameterImpl[] expectedParams = new ParameterImpl[] {
            param("this", voidPtr),
            param("outVec", voidPtr)
        };

        Stats stats = new Stats();
        try {
            Function fn = functionAtEntry(ADDRESS);
            if (fn == null) {
                println("MISSING: " + ADDRESS);
                stats.missing++;
            } else if (!fn.getName().equals(OLD_NAME) && !fn.getName().equals(NEW_NAME)) {
                println("BADNAME: " + ADDRESS + " expected=" + OLD_NAME + " or " + NEW_NAME + " actual=" + fn.getName());
                stats.bad++;
            } else {
                boolean renameNeeded = !fn.getName().equals(NEW_NAME);
                boolean signatureNeedsUpdate = !signatureMatches(fn, expectedParams);
                boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(COMMENT);
                boolean tagsNeedUpdate = !hasAllTags(fn);

                if (!renameNeeded && !signatureNeedsUpdate && !commentNeedsUpdate && !tagsNeedUpdate) {
                    println("SKIP: " + ADDRESS + " " + NEW_NAME);
                    stats.skipped++;
                } else if (dryRun) {
                    println("DRY: " + ADDRESS + " " + fn.getName() + " -> " + NEW_NAME + " :: " + expectedSignature(expectedParams));
                    stats.skipped++;
                    if (renameNeeded) {
                        stats.wouldRename++;
                    }
                    if (signatureNeedsUpdate) {
                        stats.signatureUpdated++;
                    } else if (commentNeedsUpdate || tagsNeedUpdate) {
                        stats.commentOnlyUpdated++;
                    }
                } else {
                    if (renameNeeded) {
                        fn.setName(NEW_NAME, SourceType.USER_DEFINED);
                        stats.renamed++;
                    }
                    if (signatureNeedsUpdate) {
                        fn.setCallingConvention(CALLING_CONVENTION);
                        fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
                        fn.replaceParameters(
                            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                            true,
                            SourceType.USER_DEFINED,
                            expectedParams
                        );
                        stats.signatureUpdated++;
                    }
                    fn.setComment(COMMENT);
                    for (String tag : TAGS) {
                        fn.addTag(tag);
                    }
                    if (!signatureNeedsUpdate) {
                        stats.commentOnlyUpdated++;
                    }
                    verifyReadBack(expectedParams);
                    println("OK: " + ADDRESS + " " + NEW_NAME + " :: " + expectedSignature(expectedParams));
                    stats.updated++;
                    Thread.sleep(50L);
                }
            }
        } catch (Exception ex) {
            println("FAIL: " + ADDRESS + " " + ex.getMessage());
            stats.bad++;
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave798 apply encountered missing/bad rows");
        }
    }
}
