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

public class ApplyMissionScriptObjectCodeWave546 extends GhidraScript {
    private static final String ADDRESS = "0x004f7440";
    private static final String NAME = "CMissionScriptObjectCode__FreeObjectIfPresent";
    private static final String CALLING_CONVENTION = "__fastcall";
    private static final String COMMENT =
        "Wave546 MissionScript object-code cleanup signature/comment hardening: register-only helper " +
        "takes the object_code record in ECX and frees the two owned pointers at +0x00 and +0x04 " +
        "through global memory manager 0x009c3df0. The only observed xref is " +
        "CMissionScriptObjectCode__ClearFields, which checks its object-code pointer for non-null, " +
        "calls this helper, frees the enclosing object-code allocation, and clears the owner field. " +
        "Static retail evidence only; exact object-code record layout, allocation ownership, source " +
        "identity, runtime mission-script behavior, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "mission-script-object-code-wave546",
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

    private boolean signatureMatches(Function fn, ParameterImpl objectCodeParam) {
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
        return actual.getName().equals(objectCodeParam.getName()) &&
            sameDataType(actual.getDataType(), objectCodeParam.getDataType());
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

    private boolean needsUpdate(Function fn, ParameterImpl objectCodeParam) {
        if (!fn.getName().equals(NAME)) {
            return true;
        }
        if (!signatureMatches(fn, objectCodeParam)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(COMMENT)) {
            return true;
        }
        return !hasAllTags(fn);
    }

    private String expectedSignature(ParameterImpl objectCodeParam) {
        return "void " + CALLING_CONVENTION + " " + NAME + "(" +
            objectCodeParam.getDataType().getDisplayName() + " " + objectCodeParam.getName() + ")";
    }

    private void verifyReadBack(ParameterImpl objectCodeParam) throws Exception {
        Function fn = targetFunction();
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Readback name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn, objectCodeParam)) {
            throw new IllegalStateException("Readback signature mismatch: expected " +
                expectedSignature(objectCodeParam) + " got " + fn.getSignature());
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
        ParameterImpl objectCodeParam = new ParameterImpl("object_code", voidPtr, currentProgram);
        Stats stats = new Stats();

        Function fn = targetFunction();
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME);
            stats.bad++;
        } else {
            boolean update = needsUpdate(fn, objectCodeParam);
            if (dryRun) {
                println((update ? "DRY: " : "SKIP: ") + ADDRESS + " " + expectedSignature(objectCodeParam));
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
                    objectCodeParam
                );
                fn.setComment(COMMENT);
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
                verifyReadBack(objectCodeParam);
                println("OK: " + ADDRESS + " " + expectedSignature(objectCodeParam));
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
