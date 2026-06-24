//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyUnwindContinuationWave748 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String comment, String[] tags) {
            this.address = address;
            this.name = "Unwind@" + address.substring(2);
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unwind-continuation-wave748",
            "wave748-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "compiler-unwind",
            "scope-table"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn) {
        if (!"__cdecl".equals(fn.getCallingConventionName())) {
            return false;
        }
        DataType actualReturn = fn.getReturnType();
        if (actualReturn == null || !actualReturn.isEquivalent(VoidDataType.dataType)) {
            return false;
        }
        return fn.getParameterCount() == 0;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }

            boolean signatureNeedsUpdate = !signatureMatches(fn);
            boolean changed = needsUpdate(fn, spec);
            if (!changed) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: would update " + spec.address + " " + spec.name + " signature=void __cdecl " + spec.name + "(void)");
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                stats.skipped++;
                return;
            }

            fn.setCallingConvention("__cdecl");
            fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " signature=void __cdecl " + spec.name + "(void)");
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.updated++;
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec("0x005d1fc8", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a Cutscene.cpp scope-table run. Scope-table DATA xref 0x0061ae64 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded reader at (*(EBP-0x10))+0x854. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cutscene", "active-reader", "destructor")),
            new Spec("0x005d1fd6", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a Cutscene.cpp scope-table run. Scope-table DATA xref 0x0061ae6c points at this body; decompile/instruction evidence shows it calls CResourceDescriptor__dtor on the resource descriptor at (*(EBP-0x10))+0x958. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime resource-descriptor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cutscene", "resource-descriptor", "destructor")),
            new Spec("0x005d1ff0", "Wave748 static read-back: Cutscene.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ae94 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x111c with Cutscene.cpp debug path 0x0062811c, line 0xcb, and allocation/type value 0x1c. Static retail Ghidra metadata/decompile/xref evidence only; runtime cutscene allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("cutscene", "free-object")),
            new Spec("0x005d2020", "Wave748 static read-back: Cutscene.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061aebc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x114 with Cutscene.cpp debug path 0x0062811c, line 0x225, and allocation/type value 0x1d. Static retail Ghidra metadata/decompile/xref evidence only; runtime cutscene allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("cutscene", "free-object")),
            new Spec("0x005d2050", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in the post-Cutscene scope-table run. Scope-table DATA xref 0x0061aee4 points at this body; decompile/instruction evidence shows it calls CTGALoader__Destructor on the stack-local loader at EBP-0x128. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime TGA-loader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tga-loader", "destructor")),
            new Spec("0x005d2070", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in the post-Cutscene landscape/resource scope-table run. Scope-table DATA xref 0x0061af0c points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime landscape resource cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "resource-descriptor-array", "destructor")),
            new Spec("0x005d2090", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a monitor/safe-pointer scope-table run. Scope-table DATA xref 0x0061af34 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d2098", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a monitor/safe-pointer scope-table run. Scope-table DATA xref 0x0061af3c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear", "embedded-set")),
            new Spec("0x005d20b0", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a monitor/safe-pointer scope-table run. Scope-table DATA xref 0x0061af64 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d20b8", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a monitor/safe-pointer scope-table run. Scope-table DATA xref 0x0061af6c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear", "embedded-set")),
            new Spec("0x005d20d0", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a local pointer-set scope-table run. Scope-table DATA xref 0x0061af94 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local pointer set at EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear", "stack-local")),
            new Spec("0x005d20f0", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a particle-manager scope-table run. Scope-table DATA xref 0x0061afbc points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on the stack-local manager/list node at EBP-0x90. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "global-list", "remove")),
            new Spec("0x005d2110", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a monitor/safe-pointer scope-table run. Scope-table DATA xref 0x0061afe4 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d2118", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a monitor/safe-pointer scope-table run. Scope-table DATA xref 0x0061afec points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear", "embedded-set")),
            new Spec("0x005d2130", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a particle-manager scope-table run. Scope-table DATA xref 0x0061b014 points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on the stack-local manager/list node at EBP-0x74. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "global-list", "remove")),
            new Spec("0x005d2150", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a local pointer-set scope-table run. Scope-table DATA xref 0x0061b03c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local pointer set at EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear", "stack-local")),
            new Spec("0x005d2170", "Wave748 static read-back: DestructableSegmentsController.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b064 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x14 with DestructableSegmentsController.cpp debug path 0x006287b4, line 0x1a8, and allocation/type value 0x55. Static retail Ghidra metadata/decompile/xref evidence only; runtime destructable-segment cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "free-object")),
            new Spec("0x005d2189", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a DestructableSegmentsController.cpp scope-table run. Scope-table DATA xref 0x0061b06c points at this body; decompile/instruction evidence shows it calls CDestroyableSegment__dtor_base on the pointer at EBP-0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime destroyable-segment cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "destroyable-segment", "destructor")),
            new Spec("0x005d2191", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a DestructableSegmentsController.cpp scope-table run. Scope-table DATA xref 0x0061b074 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the pointer at EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "active-reader", "destructor")),
            new Spec("0x005d2199", "Wave748 static read-back: monitor.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b07c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with monitor.h debug path 0x0062551c, line 0x5e, and allocation/type value 0x18. Static retail Ghidra metadata/decompile/xref evidence only; runtime monitor allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("monitor", "monitor-h", "free-object")),
            new Spec("0x005d21c0", "Wave748 static read-back: compiler-generated SEH unwind cleanup callback in a DestructableSegmentsController.cpp scope-table run. Scope-table DATA xref 0x0061b0a4 points at this body; decompile/instruction evidence shows it calls CDestroyableSegment__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime destroyable-segment cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "destroyable-segment", "destructor")),
            new Spec("0x005d21e0", "Wave748 static read-back: DestructableSegmentsController.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b0cc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with DestructableSegmentsController.cpp debug path 0x006287b4, line 0x1e3, and allocation/type value 0x55. Static retail Ghidra metadata/decompile/xref evidence only; runtime destructable-segment factory cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "free-object", "create-segment")),
            new Spec("0x005d21f9", "Wave748 static read-back: DestructableSegmentsController.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b0d4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with DestructableSegmentsController.cpp debug path 0x006287b4, line 0x1e8, and allocation/type value 0x55. Static retail Ghidra metadata/decompile/xref evidence only; runtime destructable-segment factory cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "free-object", "create-segment")),
            new Spec("0x005d2212", "Wave748 static read-back: DestructableSegmentsController.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b0dc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with DestructableSegmentsController.cpp debug path 0x006287b4, line 0x1ed, and allocation/type value 0x55. Static retail Ghidra metadata/decompile/xref evidence only; runtime destructable-segment factory cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "free-object", "create-segment")),
            new Spec("0x005d222b", "Wave748 static read-back: DestructableSegmentsController.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b0e4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with DestructableSegmentsController.cpp debug path 0x006287b4, line 0x1f2, and allocation/type value 0x55. Static retail Ghidra metadata/decompile/xref evidence only; runtime destructable-segment factory cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("destructable-segments-controller", "free-object", "create-segment"))
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave748 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
