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

public class ApplyUnitDefaultTuningWave543 extends GhidraScript {
    private static final String ADDRESS = "0x004eb9a0";
    private static final String NAME = "CUnit__InitDefaultTuningBlock";
    private static final String CALLING_CONVENTION = "__fastcall";
    private static final String COMMENT =
        "Wave543 CUnit default tuning-block signature/comment hardening: register-only helper " +
        "initializes the tuning block passed in ECX with fixed dword defaults across offsets " +
        "+0x00..+0x84. Observed constants include 1.0 at +0x00/+0x04/+0x08/+0x0c/+0x1c/+0x50/+0x60, " +
        "0.1 at +0x40, 0.8 at +0x54/+0x58/+0x5c, and zero elsewhere. A raw thunk at 0x004eb1d0 " +
        "loads ECX with 0x0083d248 and jumps here, indicating at least one global-default instance. " +
        "Static retail evidence only; exact struct field names, source identity, runtime tuning " +
        "behavior, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "unit-default-tuning-wave543",
        "retail-binary-evidence",
        "signature-corrected",
        "comment-hardened"
    };

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

    private Address targetAddress() {
        Address result = toAddr(ADDRESS);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + ADDRESS);
        }
        return result;
    }

    private Function targetFunction() {
        Address address = targetAddress();
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, ParameterImpl tuningBlockParam) {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), VoidDataType.dataType)) {
            return false;
        }
        if (fn.getParameterCount() != 1) {
            return false;
        }
        Parameter actual = fn.getParameter(0);
        return actual.getName().equals(tuningBlockParam.getName()) &&
            sameDataType(actual.getDataType(), tuningBlockParam.getDataType());
    }

    private boolean hasAllTags(Function fn) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : TAGS) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, ParameterImpl tuningBlockParam) {
        if (!fn.getName().equals(NAME)) {
            return true;
        }
        if (!signatureMatches(fn, tuningBlockParam)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(COMMENT)) {
            return true;
        }
        return !hasAllTags(fn);
    }

    private String expectedSignature(ParameterImpl tuningBlockParam) {
        return "void " + CALLING_CONVENTION + " " + NAME + "(" +
            tuningBlockParam.getDataType().getDisplayName() + " " + tuningBlockParam.getName() + ")";
    }

    private void verifyReadBack(ParameterImpl tuningBlockParam) throws Exception {
        Function fn = targetFunction();
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Readback name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn, tuningBlockParam)) {
            throw new IllegalStateException("Readback signature mismatch: expected " +
                expectedSignature(tuningBlockParam) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(COMMENT)) {
            throw new IllegalStateException("Readback comment mismatch");
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Readback missing tags");
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        ParameterImpl tuningBlockParam = new ParameterImpl("tuning_block", voidPtr, currentProgram);
        Stats stats = new Stats();

        Function fn = targetFunction();
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME);
            stats.bad++;
        } else {
            boolean update = needsUpdate(fn, tuningBlockParam);
            if (dryRun) {
                println((update ? "DRY: " : "SKIP: ") + ADDRESS + " " + expectedSignature(tuningBlockParam));
                stats.skipped++;
            } else if (!update) {
                println("SKIP: " + ADDRESS + " already current");
                stats.skipped++;
            } else {
                fn.setCallingConvention(CALLING_CONVENTION);
                fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    tuningBlockParam
                );
                fn.setComment(COMMENT);
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
                verifyReadBack(tuningBlockParam);
                println("OK: " + ADDRESS + " " + expectedSignature(tuningBlockParam));
                stats.updated++;
            }
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
