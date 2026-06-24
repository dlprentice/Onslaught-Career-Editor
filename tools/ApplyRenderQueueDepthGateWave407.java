//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyRenderQueueDepthGateWave407 extends GhidraScript {
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
        return name.equals("CRenderQueue__InsertIfDepthBelowIndexedLimit")
            || name.equals("CVBufTexture__QueueRenderIfDepthInRange");
    }

    private void runSpec(boolean dryRun, Stats stats) throws Exception {
        String address = "0x00477b70";
        String expectedName = "CRenderQueue__InsertIfDepthBelowIndexedLimit";
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        ParameterImpl[] params = new ParameterImpl[] {
            param("this", voidPtr),
            param("item", voidPtr),
            param("depth", FloatDataType.dataType)
        };
        String expectedSignature = "void __thiscall CRenderQueue__InsertIfDepthBelowIndexedLimit(void * this, void * item, float depth)";
        String comment =
            "Name/signature correction: render-queue depth-gated insert helper reached from CVBufTexture__RenderDynamicUnitPass. " +
            "The caller sets ECX to global render queue &DAT_009c7550, pushes item and computed depth, and the target returns " +
            "with RET 0x8. Body skips when DAT_0089d680 is set, compares depth against an indexed CRenderQueue limit at " +
            "this+0x5bc*8+0x8, then calls CRenderQueue__InsertSortedByDepth(this,item,depth). Static retail evidence only; " +
            "exact CRenderQueue layout, DAT_0089d680 semantics, runtime LOD/render behavior, and rebuild parity remain unproven.";
        String[] tags = new String[] {
            "static-reaudit",
            "renderqueue-depth-gate-wave407",
            "render-queue",
            "dynamic-unit-render",
            "owner-corrected",
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
        if (readComment == null || !readComment.contains("render-queue depth-gated insert helper")) {
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
            throw new IllegalStateException("Wave407 had missing/bad targets");
        }
    }
}
