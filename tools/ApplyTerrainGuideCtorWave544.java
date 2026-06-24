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

public class ApplyTerrainGuideCtorWave544 extends GhidraScript {
    private static final String ADDRESS = "0x004f1ec0";
    private static final String OLD_NAME = "CTerrainGuide__ctor_like_004f1ec0";
    private static final String NAME = "CTerrainGuide__ctor";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave544 TerrainGuide constructor signature/comment hardening: compact constructor wrapper " +
        "for a 0x20-byte guide object. RET 0x4 proves one owner/guideOwner stack argument after " +
        "ECX this. The body forwards guideOwner to CGuide__ctor_base, installs vtable 0x005df4ec, " +
        "returns this, and is reached from GillM, WarspiteDome, Cannon, and Sentinel init paths " +
        "that allocate pool-0x17 helper objects and store the returned pointer at owner+0x208. " +
        "Static retail evidence only; exact source class identity, guide layout, runtime terrain " +
        "behavior, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "terrain-guide-wave544",
        "retail-binary-evidence",
        "name-corrected",
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

    private boolean signatureMatches(Function fn, ParameterImpl thisParam, ParameterImpl ownerParam, DataType returnType) {
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
        Parameter actualOwner = fn.getParameter(1);
        return actualThis.getName().equals(thisParam.getName()) &&
            sameDataType(actualThis.getDataType(), thisParam.getDataType()) &&
            actualOwner.getName().equals(ownerParam.getName()) &&
            sameDataType(actualOwner.getDataType(), ownerParam.getDataType());
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

    private boolean allowedCurrentName(String name) {
        return name.equals(NAME) || name.equals(OLD_NAME);
    }

    private boolean needsUpdate(Function fn, ParameterImpl thisParam, ParameterImpl ownerParam, DataType returnType) {
        if (!fn.getName().equals(NAME)) {
            return true;
        }
        if (!signatureMatches(fn, thisParam, ownerParam, returnType)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(COMMENT)) {
            return true;
        }
        return !hasAllTags(fn);
    }

    private String expectedSignature(ParameterImpl thisParam, ParameterImpl ownerParam, DataType returnType) {
        return returnType.getDisplayName() + " " + CALLING_CONVENTION + " " + NAME + "(" +
            thisParam.getDataType().getDisplayName() + " " + thisParam.getName() + ", " +
            ownerParam.getDataType().getDisplayName() + " " + ownerParam.getName() + ")";
    }

    private void verifyReadBack(ParameterImpl thisParam, ParameterImpl ownerParam, DataType returnType) throws Exception {
        Function fn = targetFunction();
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Readback name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn, thisParam, ownerParam, returnType)) {
            throw new IllegalStateException("Readback signature mismatch: expected " +
                expectedSignature(thisParam, ownerParam, returnType) + " got " + fn.getSignature());
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
        ParameterImpl ownerParam = new ParameterImpl("guideOwner", voidPtr, currentProgram);
        Stats stats = new Stats();

        Function fn = targetFunction();
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!allowedCurrentName(fn.getName())) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME + " or " + OLD_NAME);
            stats.bad++;
        } else {
            boolean update = needsUpdate(fn, thisParam, ownerParam, voidPtr);
            boolean needsRename = !fn.getName().equals(NAME);
            if (dryRun) {
                println((update ? "DRY: " : "SKIP: ") + ADDRESS + " " + fn.getName() + " -> " +
                    expectedSignature(thisParam, ownerParam, voidPtr));
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
            } else if (!update) {
                println("SKIP: " + ADDRESS + " already current");
                stats.skipped++;
            } else {
                if (needsRename) {
                    fn.setName(NAME, SourceType.USER_DEFINED);
                    stats.renamed++;
                }
                fn.setCallingConvention(CALLING_CONVENTION);
                fn.setReturnType(voidPtr, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    thisParam,
                    ownerParam
                );
                fn.setComment(COMMENT);
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
                verifyReadBack(thisParam, ownerParam, voidPtr);
                println("OK: " + ADDRESS + " " + expectedSignature(thisParam, ownerParam, voidPtr));
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
