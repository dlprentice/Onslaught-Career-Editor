//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFmvPlayWave404 extends GhidraScript {
    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void runSpec(boolean dryRun, Stats stats) throws Exception {
        String address = "0x004655d0";
        String expectedName = "con_fmv_play";
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        ParameterImpl[] params = new ParameterImpl[] {
            param("command_line", charPtr)
        };
        String expectedSignature = "void __cdecl con_fmv_play(char * command_line)";
        String comment =
            "Console command handler for fmv_play <filename>: validates that the command line is longer than the 9-byte prefix, " +
            "mirrors DAT_006630cc into DAT_0089d69c, enters controller non-interactive mode, invokes the frontend video object " +
            "at 0x0089d690 through vtable slot +0x2c with command_line+9 and flags 0,0,0,0,1, then leaves non-interactive mode. " +
            "On short input it prints the syntax string through CConsole__AddString. Static retail evidence only; exact frontend " +
            "video object type/layout, runtime playback behavior, and rebuild parity remain unproven.";
        String[] tags = new String[] {
            "static-reaudit",
            "fmv-play-wave404",
            "console-command",
            "frontend-video",
            "fmv",
            "signature-corrected",
            "comment-hardened",
            "retail-binary-evidence"
        };

        Function fn = functionAtEntry(address);
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + address + " Function not found");
            return;
        }
        if (!fn.getName().equals(expectedName)) {
            throw new IllegalStateException("Unexpected function name at " + address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + address + " " + fn.getSignature() + " -> " + expectedSignature);
            stats.skipped++;
            return;
        }

        fn.setCallingConvention("__cdecl");
        fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            params
        );
        fn.setComment(comment);
        for (String tag : tags) {
            fn.addTag(tag);
        }

        Function readBack = functionAtEntry(address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + address);
        }
        if (!readBack.getName().equals(expectedName)) {
            throw new IllegalStateException("Read-back name mismatch at " + address + ": " + readBack.getName());
        }
        if (!readBack.getSignature().toString().equals(expectedSignature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.contains("Console command handler for fmv_play <filename>")) {
            throw new IllegalStateException("Read-back comment mismatch at " + address);
        }
        Set<String> readTags = tagNames(readBack);
        for (String tag : tags) {
            if (!readTags.contains(tag)) {
                throw new IllegalStateException("Missing read-back tag at " + address + ": " + tag);
            }
        }

        stats.updated++;
        println("UPDATED: " + address + " " + readBack.getSignature());
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = true;
        String[] args = getScriptArgs();
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        runSpec(dryRun, stats);
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave404 had missing/bad targets");
        }
    }
}
