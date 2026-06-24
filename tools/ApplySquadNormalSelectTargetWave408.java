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

public class ApplySquadNormalSelectTargetWave408 extends GhidraScript {
    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int wouldUpdate = 0;
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> current = tagNames(fn);
        for (String tag : tags) {
            if (!current.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void runSpec(boolean dryRun, Stats stats) throws Exception {
        String address = "0x00477cb0";
        String expectedName = "CSquadNormal__SelectBestEngagementTarget";
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        ParameterImpl[] params = new ParameterImpl[] {
            param("squad", voidPtr)
        };
        String expectedSignature = "void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad)";
        String comment =
            "Signature/comment hardening: CSquadNormal target-selection/scoring helper. Fresh retail read-back shows " +
            "one stack argument (RET 0x4), no ECX thiscall setup, squad state at +0x7c selecting global candidate " +
            "lists DAT_00855090/DAT_008550b0/DAT_008550c0, virtual position/support-object reads at vtable " +
            "+0x120/+0x124, per-candidate flag/range/faction/support checks, scoring against config weights at " +
            "squad+0xa0 offsets 0x158/0x164/0x168/0x16c/0x170/0x174/0x178/0x17c, support/escort helpers, and " +
            "fallback through candidate+0x148. Static retail evidence only; exact CSquadNormal/source identity, " +
            "candidate struct layout, global list semantics, runtime AI behavior, and rebuild parity remain unproven.";
        String[] tags = new String[] {
            "static-reaudit",
            "squadnormal-select-target-wave408",
            "squad-normal",
            "ai-target-selection",
            "name-confirmed",
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
        if (!fn.getName().equals(expectedName)) {
            throw new IllegalStateException("Unexpected function name at " + address + ": " + fn.getName());
        }

        boolean needsUpdate = !fn.getSignature().toString().equals(expectedSignature)
            || fn.getComment() == null
            || !fn.getComment().contains("CSquadNormal target-selection/scoring helper")
            || !hasAllTags(fn, tags);

        if (dryRun) {
            if (needsUpdate) {
                stats.wouldUpdate++;
            }
            println("DRY: " + address + " " + fn.getSignature() + " -> " + expectedSignature);
            stats.skipped++;
            return;
        }

        fn.setCallingConvention("__stdcall");
        fn.setReturnType(voidPtr, SourceType.USER_DEFINED);
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
        if (readComment == null || !readComment.contains("CSquadNormal target-selection/scoring helper")) {
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
            " would_update=" + stats.wouldUpdate +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave408 had missing/bad targets");
        }
    }
}
