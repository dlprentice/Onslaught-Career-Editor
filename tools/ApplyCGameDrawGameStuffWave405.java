//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCGameDrawGameStuffWave405 extends GhidraScript {
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

    private boolean allowedExistingName(String name) {
        return name.equals("CGame__DrawGameStuff") || name.equals("FrontendUpdate_CheatChecks");
    }

    private void runSpec(boolean dryRun, Stats stats) throws Exception {
        String address = "0x004714c0";
        String expectedName = "CGame__DrawGameStuff";
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        ParameterImpl[] params = new ParameterImpl[] {
            param("this", voidPtr)
        };
        String expectedSignature = "void __thiscall CGame__DrawGameStuff(void * this)";
        String comment =
            "Name/signature correction: source-parity CGame::DrawGameStuff pass called by CDXEngine__PostRender after " +
            "CGame__DrawDebugStuff with ECX=&DAT_008a9a98. Retail body handles the PC screenshot/selection key branch, " +
            "periodic FPS trace/status-buffer text, developer/game status overlays, encoded frontend cheat text rendering " +
            "through Frontend__XorWideTextBlock100BytesToScratch, console status-history rendering, and game-over/objective " +
            "overlays. Static retail/source-alignment evidence only; exact CGame layout, input-key semantics, runtime overlay " +
            "behavior, and rebuild parity remain unproven.";
        String[] tags = new String[] {
            "static-reaudit",
            "cgame-draw-game-stuff-wave405",
            "game",
            "debug-overlay",
            "status-overlay",
            "game-over",
            "source-parity",
            "name-corrected",
            "signature-hardened",
            "comment-hardened",
            "retail-binary-evidence"
        };

        Function fn = functionAtEntry(address);
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + address + " Function not found");
            return;
        }
        if (!allowedExistingName(fn.getName())) {
            throw new IllegalStateException("Unexpected function name at " + address + ": " + fn.getName());
        }

        if (dryRun) {
            if (!fn.getName().equals(expectedName)) {
                stats.wouldRename++;
            }
            println("DRY: " + address + " " + fn.getName() + " " + fn.getSignature() + " -> " + expectedSignature);
            stats.skipped++;
            return;
        }

        if (!fn.getName().equals(expectedName)) {
            fn.setName(expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention("__thiscall");
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
        if (readComment == null || !readComment.contains("source-parity CGame::DrawGameStuff")) {
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
        try {
            runSpec(dryRun, stats);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + ex.getMessage());
        }
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave405 had missing/bad targets");
        }
    }
}
