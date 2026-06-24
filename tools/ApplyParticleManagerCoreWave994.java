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

public class ApplyParticleManagerCoreWave994 extends GhidraScript {
    private static final String ADDRESS = "0x004cb920";
    private static final String NAME = "CParticleManager__UpdateParticleAndRecycleIfDead";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave994 signature correction: RET 0x4 and the entry-frame read at 0x004cb924 prove one stack "
        + "argument (particle) after ECX carries the particle manager receiver; this removes the stale "
        + "unused_context parameter from the Wave463 signature. The body updates one particle's lifetime "
        + "and position, refreshes attached handle activity/backlink fields, applies the observed death-flag "
        + "logic, dispatches particle-set vfunc +0x28, and recycles dead particles to the manager free list. "
        + "Static retail-binary evidence only; runtime particle behavior, exact manager/particle/handle "
        + "layouts, source identity, BEA patching, and rebuild parity remain separate proof.";
    private static final String[] TAGS = {
        "static-reaudit",
        "particle-manager-core-review-wave994",
        "wave994-readback-verified",
        "retail-binary-evidence",
        "signature-corrected",
        "comment-hardened",
        "phantom-param-corrected",
        "particle-manager-wave463",
        "particle-update",
        "particle-recycle"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
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
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
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
        sb.append("void ").append(CALLING_CONVENTION).append(" ").append(NAME).append("(");
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

    private int missingTagCount(Function fn) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private boolean hasAllTags(Function fn) {
        return missingTagCount(fn) == 0;
    }

    private void verifyReadBack(ParameterImpl[] params) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
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
        println("ApplyParticleManagerCoreWave994 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        ParameterImpl[] expectedParams = new ParameterImpl[] {
            param("this", voidPtr),
            param("particle", voidPtr)
        };

        Stats stats = new Stats();
        try {
            Function fn = functionAtEntry(ADDRESS);
            if (fn == null) {
                println("MISSING: " + ADDRESS);
                stats.missing++;
            } else if (!fn.getName().equals(NAME)) {
                println("BADNAME: " + ADDRESS + " expected=" + NAME + " actual=" + fn.getName());
                stats.bad++;
            } else {
                boolean signatureNeedsUpdate = !signatureMatches(fn, expectedParams);
                boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(COMMENT);
                int tagsToAdd = missingTagCount(fn);

                if (!signatureNeedsUpdate && !commentNeedsUpdate && tagsToAdd == 0) {
                    println("SKIP: " + ADDRESS + " " + NAME);
                    stats.skipped++;
                } else if (dryRun) {
                    println("DRY: " + ADDRESS + " " + NAME + " :: " + expectedSignature(expectedParams)
                        + " signatureNeedsUpdate=" + signatureNeedsUpdate
                        + " commentNeedsUpdate=" + commentNeedsUpdate
                        + " tagsToAdd=" + tagsToAdd);
                    stats.skipped++;
                    if (signatureNeedsUpdate) {
                        stats.signatureUpdated++;
                    } else {
                        stats.commentOnlyUpdated++;
                    }
                    stats.tagsAdded += tagsToAdd;
                } else {
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
                    } else {
                        stats.commentOnlyUpdated++;
                    }
                    fn.setComment(COMMENT);
                    for (String tag : TAGS) {
                        if (!tagNames(fn).contains(tag)) {
                            fn.addTag(tag);
                            stats.tagsAdded++;
                        }
                    }
                    verifyReadBack(expectedParams);
                    println("OK: " + ADDRESS + " " + NAME + " :: " + expectedSignature(expectedParams));
                    stats.updated++;
                    currentProgram.flushEvents();
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
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave994 apply encountered missing/bad rows");
        }
    }
}
