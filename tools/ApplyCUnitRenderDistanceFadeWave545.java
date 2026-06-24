//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCUnitRenderDistanceFadeWave545 extends GhidraScript {
    private static final String ADDRESS = "0x004f6fd0";
    private static final String NAME = "CUnit__RenderWithDistanceFade";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave545 CUnit render-fade signature/comment hardening: OID__RenderWithState1BOverride " +
        "calls this only after the unit render-context pointer at this+0x48 is non-null and treats " +
        "the low-byte return as handled/not-handled. RET 0x4 and the body read one stack " +
        "render_flags argument after ECX this; the stale third decompiler argument came from the " +
        "old signature. The body reads *(this+0x48)+0xbc, compares it against zero/default float " +
        "constant 0x005d856c, computes a clamped time delta using DAT_00672fd0 plus constants " +
        "0x005d85d8/0x005d8c68/0x005d8c70, writes the rounded value to global 0x0063012c for the " +
        "nested CThing__Render call, restores 0x0063012c to 0xff, and returns handled=true; the " +
        "nonpositive/NaN path returns false. Static retail evidence only; exact fade field meaning, " +
        "global render-state meaning, runtime rendering behavior, source identity, and rebuild " +
        "parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "unit-render-distance-fade-wave545",
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

    private boolean signatureMatches(Function fn, ParameterImpl thisParam, ParameterImpl renderFlagsParam, DataType returnType) {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), returnType)) {
            return false;
        }
        if (fn.getParameterCount() != 2) {
            return false;
        }
        Parameter actualThis = fn.getParameter(0);
        Parameter actualRenderFlags = fn.getParameter(1);
        return actualThis.getName().equals(thisParam.getName()) &&
            sameDataType(actualThis.getDataType(), thisParam.getDataType()) &&
            actualRenderFlags.getName().equals(renderFlagsParam.getName()) &&
            sameDataType(actualRenderFlags.getDataType(), renderFlagsParam.getDataType());
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

    private boolean needsUpdate(Function fn, ParameterImpl thisParam, ParameterImpl renderFlagsParam, DataType returnType) {
        if (!fn.getName().equals(NAME)) {
            return true;
        }
        if (!signatureMatches(fn, thisParam, renderFlagsParam, returnType)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(COMMENT)) {
            return true;
        }
        return !hasAllTags(fn);
    }

    private String expectedSignature(ParameterImpl thisParam, ParameterImpl renderFlagsParam, DataType returnType) {
        return returnType.getDisplayName() + " " + CALLING_CONVENTION + " " + NAME + "(" +
            thisParam.getDataType().getDisplayName() + " " + thisParam.getName() + ", " +
            renderFlagsParam.getDataType().getDisplayName() + " " + renderFlagsParam.getName() + ")";
    }

    private void verifyReadBack(ParameterImpl thisParam, ParameterImpl renderFlagsParam, DataType returnType) throws Exception {
        Function fn = targetFunction();
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Readback name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn, thisParam, renderFlagsParam, returnType)) {
            throw new IllegalStateException("Readback signature mismatch: expected " +
                expectedSignature(thisParam, renderFlagsParam, returnType) + " got " + fn.getSignature());
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        ParameterImpl thisParam = new ParameterImpl("this", voidPtr, currentProgram);
        ParameterImpl renderFlagsParam = new ParameterImpl("render_flags", uintType, currentProgram);
        Stats stats = new Stats();

        Function fn = targetFunction();
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME);
            stats.bad++;
        } else {
            boolean update = needsUpdate(fn, thisParam, renderFlagsParam, boolType);
            if (dryRun) {
                println((update ? "DRY: " : "SKIP: ") + ADDRESS + " " +
                    expectedSignature(thisParam, renderFlagsParam, boolType));
                stats.skipped++;
            } else if (!update) {
                println("SKIP: " + ADDRESS + " already current");
                stats.skipped++;
            } else {
                fn.setCallingConvention(CALLING_CONVENTION);
                fn.setReturnType(boolType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    thisParam,
                    renderFlagsParam
                );
                fn.setComment(COMMENT);
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
                verifyReadBack(thisParam, renderFlagsParam, boolType);
                println("OK: " + ADDRESS + " " +
                    expectedSignature(thisParam, renderFlagsParam, boolType));
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
