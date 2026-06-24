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

public class ApplySafeSideShutdownWave542 extends GhidraScript {
    private static final String ADDRESS = "0x004de1d0";
    private static final String NEW_NAME = "CSafeSide__ShutdownAndUnlinkFactionAnchor";
    private static final String OLD_NAME = "CSafeSide__VFunc_02_004de1d0";
    private static final String CALLING_CONVENTION = "__fastcall";
    private static final String COMMENT =
        "Wave542 SafeSide signature/comment correction: vtable slot data at 0x005dcce4 points here, " +
        "and the register-only body removes this object from global list DAT_00855160 through " +
        "CSPtrSet__Remove before forwarding to CComplexThing__Shutdown. DAT_00855160 is also scanned " +
        "by CUnit__FindNearestFactionAnchor, so the list role is bounded as faction-anchor context. " +
        "Static retail evidence only; exact CSafeSide source identity, concrete list/object layout, " +
        "runtime faction-anchor behavior, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "safeside-wave542",
        "retail-binary-evidence",
        "signature-corrected",
        "comment-hardened",
        "owner-retained",
        "renamed"
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

    private boolean signatureMatches(Function fn, ParameterImpl thisParam) {
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
        return actual.getName().equals(thisParam.getName()) &&
            sameDataType(actual.getDataType(), thisParam.getDataType());
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

    private boolean nameAllowed(String actual) {
        return actual.equals(NEW_NAME) || actual.equals(OLD_NAME);
    }

    private boolean needsUpdate(Function fn, ParameterImpl thisParam) {
        if (!fn.getName().equals(NEW_NAME)) {
            return true;
        }
        if (!signatureMatches(fn, thisParam)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(COMMENT)) {
            return true;
        }
        return !hasAllTags(fn);
    }

    private String expectedSignature(ParameterImpl thisParam) {
        return "void " + CALLING_CONVENTION + " " + NEW_NAME + "(" +
            thisParam.getDataType().getDisplayName() + " " + thisParam.getName() + ")";
    }

    private void verifyReadBack(ParameterImpl thisParam) throws Exception {
        Function fn = targetFunction();
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NEW_NAME)) {
            throw new IllegalStateException("Readback name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn, thisParam)) {
            throw new IllegalStateException("Readback signature mismatch: expected " +
                expectedSignature(thisParam) + " got " + fn.getSignature());
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
        ParameterImpl thisParam = new ParameterImpl("this", voidPtr, currentProgram);
        Stats stats = new Stats();

        Function fn = targetFunction();
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!nameAllowed(fn.getName())) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NEW_NAME);
            stats.bad++;
        } else {
            boolean needsRename = !fn.getName().equals(NEW_NAME);
            boolean update = needsUpdate(fn, thisParam);
            if (dryRun) {
                if (needsRename) {
                    println("DRYRENAME: " + ADDRESS + " " + fn.getName() + " -> " + expectedSignature(thisParam));
                    stats.wouldRename++;
                } else {
                    println((update ? "DRY: " : "SKIP: ") + ADDRESS + " " + expectedSignature(thisParam));
                }
                stats.skipped++;
            } else if (!update) {
                println("SKIP: " + ADDRESS + " already current");
                stats.skipped++;
            } else {
                if (needsRename) {
                    fn.setName(NEW_NAME, SourceType.USER_DEFINED);
                    stats.renamed++;
                }
                fn.setCallingConvention(CALLING_CONVENTION);
                fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    new ParameterImpl[] {thisParam}
                );
                fn.setComment(COMMENT);
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
                verifyReadBack(thisParam);
                println("OK: " + ADDRESS + " " + targetFunction().getSignature());
                stats.updated++;
                Thread.sleep(50);
            }
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave542 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
