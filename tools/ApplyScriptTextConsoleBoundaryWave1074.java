//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
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

public class ApplyScriptTextConsoleBoundaryWave1074 extends GhidraScript {
    private static final String ADDRESS = "0x00537c40";
    private static final String END_RET = "0x00537c69";
    private static final String NEXT_RAW = "0x00537c70";
    private static final String NAME = "IScript__PrintText";
    private static final String CALLING_CONVENTION = "__stdcall";
    private static final String COMMENT =
        "Wave1074 boundary recovery: ScriptCommandRegistry__InitBuiltins descriptor 0x0064d220 " +
        "stores s_PrintText_0064f984 and handler field 0x0064d250 DATA-xrefs to this previously " +
        "missing function at 0x00537c40. Fresh pre-state listed the address as " +
        "INSTRUCTION_NO_FUNCTION; the prior raw command returns at 0x00537c25 RET 0xc, this body " +
        "returns at 0x00537c69 RET 0xc, and the next raw command begins at 0x00537c70. The body " +
        "reads script_args[0] through the script datatype integer getter vtable slot +0x30, calls " +
        "CText__GetStringById on the global text table at 0x0083d960, then forwards the resolved " +
        "localized text to CConsole__Printf with format string 0x0064fda4 \"%w\" and console " +
        "pointer 0x0066f580. Static retail Ghidra metadata/decompile/xref/instruction evidence " +
        "only; exact source-body identity, command descriptor schema, runtime MissionScript " +
        "dispatch/console behavior, BEA patching, gameplay outcomes, and rebuild parity remain " +
        "separate proof.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "script-text-console-boundary-wave1074",
        "wave1074-readback-verified",
        "retail-binary-evidence",
        "function-boundary-recovered",
        "mission-script",
        "script-command",
        "print-text",
        "text-lookup",
        "console-output",
        "signature-hardened",
        "comment-hardened"
    };

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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private ParameterImpl param(String name) throws Exception {
        return new ParameterImpl(name, voidPtr(), currentProgram);
    }

    private ParameterImpl[] params() throws Exception {
        return new ParameterImpl[] {
            param("script_args"),
            param("unused_state"),
            param("out_result")
        };
    }

    private Function functionAtEntry(Address address) {
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn) throws Exception {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), VoidDataType.dataType)) {
            return false;
        }
        ParameterImpl[] expectedParams = params();
        if (fn.getParameterCount() != expectedParams.length) {
            return false;
        }
        for (int i = 0; i < expectedParams.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = expectedParams[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private String expectedSignature() throws Exception {
        ParameterImpl[] expectedParams = params();
        StringBuilder sb = new StringBuilder();
        sb.append("void ").append(CALLING_CONVENTION).append(" ").append(NAME).append("(");
        for (int i = 0; i < expectedParams.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(expectedParams[i].getDataType().getDisplayName()).append(" ").append(expectedParams[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
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

    private void applySignature(Function fn) throws Exception {
        fn.setCallingConvention(CALLING_CONVENTION);
        fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, params());
    }

    private Function getOrCreate(boolean dryRun, Stats stats) throws Exception {
        Address address = addr(ADDRESS);
        Function fn = functionAtEntry(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + ADDRESS + " -> " + expectedSignature());
            return null;
        }

        if (getInstructionAt(address) == null && (getDataAt(address) != null || currentProgram.getListing().getDefinedDataContaining(address) != null)) {
            currentProgram.getListing().clearCodeUnits(address, address.add(15), false);
        }
        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, NAME);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + ADDRESS + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void verifyReadBack() throws Exception {
        Function fn = functionAtEntry(addr(ADDRESS));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Read-back name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn)) {
            throw new IllegalStateException("Read-back signature mismatch: " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(COMMENT)) {
            throw new IllegalStateException("Read-back comment mismatch");
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back tag mismatch");
        }
        AddressSetView body = fn.getBody();
        if (!body.contains(addr(END_RET))) {
            throw new IllegalStateException("Read-back body does not include expected RET at " + END_RET);
        }
        if (body.contains(addr(NEXT_RAW))) {
            throw new IllegalStateException("Read-back body unexpectedly absorbed next raw command at " + NEXT_RAW);
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyScriptTextConsoleBoundaryWave1074 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        try {
            Function fn = getOrCreate(dryRun, stats);
            if (fn == null) {
                stats.signatureUpdated++;
                stats.commentOnlyUpdated++;
                stats.updated++;
                println(summary(stats));
                return;
            }

            boolean renameNeeded = !fn.getName().equals(NAME);
            boolean signatureNeedsUpdate = !signatureMatches(fn);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(COMMENT)
                || !hasAllTags(fn);

            if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
                println("SKIP: " + ADDRESS + " " + NAME);
                stats.skipped++;
                println(summary(stats));
                return;
            }
            if (dryRun) {
                println("DRY: " + ADDRESS + " " + fn.getName() + " -> " + expectedSignature());
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else if (commentOrTagsNeedUpdate) {
                    stats.commentOnlyUpdated++;
                }
                println(summary(stats));
                return;
            }

            if (renameNeeded) {
                fn.setName(NAME, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                applySignature(fn);
                stats.signatureUpdated++;
            }
            fn.setComment(COMMENT);
            Set<String> existingTags = tagNames(fn);
            for (String tag : TAGS) {
                if (!existingTags.contains(tag)) {
                    fn.addTag(tag);
                }
            }
            if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            verifyReadBack();
            println("OK: " + ADDRESS + " " + NAME + " -> " + expectedSignature());
            stats.updated++;
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + ADDRESS + " " + NAME + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }

        println(summary(stats));
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1074 script text console boundary apply encountered missing/bad rows");
        }
    }

    private String summary(Stats stats) {
        return "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad;
    }
}
