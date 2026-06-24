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

public class ApplyUnwindContinuationWave749 extends GhidraScript {
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
            "unwind-continuation-wave749",
            "wave749-readback-verified",
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
            new Spec("0x005d2250", "Wave749 static read-back: DiveBomber.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b10c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with DiveBomber.cpp debug path 0x006289c0, line 0x16, and allocation/type value 0x12. Static retail Ghidra metadata/decompile/xref evidence only; runtime dive-bomber allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("divebomber", "free-object")),
            new Spec("0x005d2266", "Wave749 static read-back: DiveBomber.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b114 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with DiveBomber.cpp debug path 0x006289c0, line 0x17, and allocation/type value 0x13. Static retail Ghidra metadata/decompile/xref evidence only; runtime dive-bomber allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("divebomber", "free-object")),
            new Spec("0x005d2290", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the DiveBomber/Dropship-adjacent scope-table run. Scope-table DATA xref 0x0061b13c points at this body; decompile/instruction evidence shows it jumps to CMonitor__Shutdown with the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d2298", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the DiveBomber/Dropship-adjacent scope-table run. Scope-table DATA xref 0x0061b144 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded active reader at (*(EBP-0x10))+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "destructor")),
            new Spec("0x005d22a3", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the DiveBomber/Dropship-adjacent scope-table run. Scope-table DATA xref 0x0061b14c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded active reader at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "destructor")),
            new Spec("0x005d22c0", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the DiveBomber/Dropship-adjacent scope-table run. Scope-table DATA xref 0x0061b174 points at this body; decompile/instruction evidence shows it jumps to CMonitor__Shutdown_Thunk with the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d22e0", "Wave749 static read-back: Dropship.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b19c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Dropship.cpp debug path 0x00628a54, line 0x1b, and allocation/type value 0x2c. Static retail Ghidra metadata/decompile/xref evidence only; runtime dropship allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("dropship", "free-object")),
            new Spec("0x005d22f6", "Wave749 static read-back: Dropship.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b1a4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Dropship.cpp debug path 0x00628a54, line 0x17, and allocation/type value 0x2d. Static retail Ghidra metadata/decompile/xref evidence only; runtime dropship allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("dropship", "free-object")),
            new Spec("0x005d230c", "Wave749 static read-back: Dropship.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b1ac points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Dropship.cpp debug path 0x00628a54, line 0x16, and allocation/type value 0x2e. Static retail Ghidra metadata/decompile/xref evidence only; runtime dropship allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("dropship", "free-object")),
            new Spec("0x005d2322", "Wave749 static read-back: Dropship.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b1b4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Dropship.cpp debug path 0x00628a54, line 0x10, and allocation/type value 0x37. Static retail Ghidra metadata/decompile/xref evidence only; runtime dropship allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("dropship", "free-object")),
            new Spec("0x005d2350", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the Dropship.cpp scope-table run. Scope-table DATA xref 0x0061b1dc points at this body; decompile/instruction evidence shows it jumps to CMonitor__Shutdown with the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dropship", "monitor", "shutdown")),
            new Spec("0x005d2358", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the Dropship.cpp scope-table run. Scope-table DATA xref 0x0061b1e4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded active reader at (*(EBP-0x10))+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dropship", "active-reader", "destructor")),
            new Spec("0x005d2363", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the Dropship.cpp scope-table run. Scope-table DATA xref 0x0061b1ec points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded active reader at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dropship", "active-reader", "destructor")),
            new Spec("0x005d2380", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the Dropship.cpp scope-table run. Scope-table DATA xref 0x0061b214 points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on the stack-local manager/list node at EBP-0x68. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dropship", "particle-manager", "global-list", "remove")),
            new Spec("0x005d2388", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the Dropship.cpp scope-table run. Scope-table DATA xref 0x0061b21c points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on the stack-local CLine-like object at EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line/local-object cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dropship", "line", "vtable-reset")),
            new Spec("0x005d23a0", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b244 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with engine.cpp debug path 0x00628b40, line 0x36, and allocation/type value 0x87. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d23b9", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b24c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with engine.cpp debug path 0x00628b40, line 0x30, and allocation/type value 0x8b. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d23d2", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b254 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with engine.cpp debug path 0x00628b40, line 0x33, and allocation/type value 0x8f. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d23eb", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b25c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with engine.cpp debug path 0x00628b40, line 0x35, and allocation/type value 0x93. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d2404", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b264 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with engine.cpp debug path 0x00628b40, line 0x31, and allocation/type value 0xa5. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d241d", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b26c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with engine.cpp debug path 0x00628b40, line 0x34, and allocation/type value 0xab. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d2440", "Wave749 static read-back: engine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b294 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with engine.cpp debug path 0x00628b40, line 0x26, and allocation/type value 0x136. Static retail Ghidra metadata/decompile/xref evidence only; runtime engine allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("engine", "free-object")),
            new Spec("0x005d2470", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the engine/event-manager-adjacent scope-table run. Scope-table DATA xref 0x0061b2bc points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime landscape resource cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("engine", "landscape", "resource-descriptor-array", "destructor")),
            new Spec("0x005d2490", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the engine/event-manager-adjacent scope-table run. Scope-table DATA xref 0x0061b2e4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active reader pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "destructor")),
            new Spec("0x005d24b0", "Wave749 static read-back: compiler-generated SEH unwind cleanup callback in the eventmanager.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b30c points at this body; decompile/instruction evidence shows it calls CRT__EhVectorDestructorIterator_WithUnwind over the array at (*(EBP-0x10))+0x30 with element size 0x10, count 0x258, and CSPtrSet__Clear as the element destructor. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime event-manager bucket cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "sptrset", "vector-destructor"))
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
            throw new IllegalStateException("Wave749 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
