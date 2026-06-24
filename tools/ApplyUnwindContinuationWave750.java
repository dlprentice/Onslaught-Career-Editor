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

public class ApplyUnwindContinuationWave750 extends GhidraScript {
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
            "unwind-continuation-wave750",
            "wave750-readback-verified",
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
            new Spec("0x005d24e0", "Wave750 static read-back: eventmanager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b334 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with eventmanager.cpp debug path 0x00628d3c, line 0x43, and allocation/type value 0x34. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime event-manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "free-object")),
            new Spec("0x005d24f6", "Wave750 static read-back: eventmanager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b33c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with eventmanager.cpp debug path 0x00628d3c, line 0x43, and allocation/type value 0x37. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime event-manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "free-object")),
            new Spec("0x005d2520", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the eventmanager.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b364 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader pointer at *(EBP-0x24). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "active-reader", "destructor")),
            new Spec("0x005d2528", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the eventmanager.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b36c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader pointer at *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "active-reader", "destructor")),
            new Spec("0x005d2540", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the eventmanager.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b39c points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on the stack-local manager/list node at EBP-0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "particle-manager", "global-list", "remove")),
            new Spec("0x005d2560", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the eventmanager.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b3c4 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown with the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "monitor", "shutdown")),
            new Spec("0x005d2580", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the eventmanager.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b3ec points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape descriptor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("eventmanager", "landscape", "resource-descriptor-array", "destructor")),
            new Spec("0x005d25a0", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FEPBEConfig-adjacent scope-table run. Scope-table DATA xref 0x0061b414 points at this body; decompile/instruction evidence shows it calls CDXMemBuffer__dtor_base on the stack-local memory buffer at EBP-0x208. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime memory-buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("fepbeconfig", "cdxmembuffer", "destructor")),
            new Spec("0x005d25c0", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FEPBEConfig-adjacent scope-table run. Scope-table DATA xref 0x0061b43c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the set/list at (*(EBP-0x10))+0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("fepbeconfig", "sptrset", "clear")),
            new Spec("0x005d25e0", "Wave750 static read-back: FEPBEConfig.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b464 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x20) with FEPBEConfig.cpp debug path 0x00628fac, line 0x80, and allocation/type value 0x18f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime FEPBEConfig cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("fepbeconfig", "free-object")),
            new Spec("0x005d2610", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FEPBEConfig-adjacent scope-table run. Scope-table DATA xref 0x0061b48c points at this body; decompile/instruction evidence shows it jumps to CMenuItem__RestoreCompactVTable with the menu item pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime menu-item cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("fepbeconfig", "menuitem", "vtable-reset")),
            new Spec("0x005d2630", "Wave750 static read-back: FEPDebriefing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b4b4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with FEPDebriefing.cpp debug path 0x0062913c, line 0x80, and allocation/type value 0x30. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime debriefing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("fepdebriefing", "free-object")),
            new Spec("0x005d2660", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FEPDebriefing/FrontEnd-adjacent scope-table run. Scope-table DATA xref 0x0061b4dc points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local set at EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("fepdebriefing", "frontend", "sptrset", "clear")),
            new Spec("0x005d2680", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b504 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk with the object pointer at *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "monitor", "shutdown", "thunk")),
            new Spec("0x005d2688", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b50c points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the subobject at (*(EBP-0x14))+0x8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "camera", "destructor")),
            new Spec("0x005d2693", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b514 points at this body; instruction evidence shows it dispatches DeviceObject__ctor_like_00512d50 with ECX derived from (*(EBP-0x14))+0x1c4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, constructor/unwind direction, runtime device-object behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "device-object")),
            new Spec("0x005d26a1", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b51c points at this body; decompile/instruction evidence shows it calls CFEPMultiplayerStart__ClearJoinedPlayerSet on the subobject at (*(EBP-0x14))+0x2bc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, concrete CFEPMultiplayerStart field layout, runtime multiplayer-start cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "fepmultiplayerstart", "sptrset", "clear")),
            new Spec("0x005d26af", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b524 points at this body; decompile/instruction evidence shows it calls CFEPMultiplayerStart__ClearSecondaryPlayerSet on the subobject at (*(EBP-0x14))+0x2ec. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, concrete CFEPMultiplayerStart field layout, runtime multiplayer-start cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "fepmultiplayerstart", "sptrset", "clear")),
            new Spec("0x005d26bd", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b52c points at this body; instruction evidence shows it dispatches CWaitingThread__ctor_like_00528bf0 with ECX derived from (*(EBP-0x10))+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, constructor/unwind direction, runtime waiting-thread behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "waiting-thread")),
            new Spec("0x005d26c8", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b534 points at this body; instruction evidence shows it dispatches CFEPMultiplayerStart__InitWaitingThreadSubsystem with ECX derived from (*(EBP-0x14))+0x37dc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, constructor/unwind direction, runtime frontend waiting-thread behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "fepmultiplayerstart", "waiting-thread")),
            new Spec("0x005d26e0", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b55c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk with the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "monitor", "shutdown", "thunk")),
            new Spec("0x005d26e8", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b564 points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the subobject at (*(EBP-0x10))+0x8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "camera", "destructor")),
            new Spec("0x005d26f3", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b56c points at this body; instruction evidence shows it dispatches DeviceObject__ctor_like_00512d50 with ECX derived from (*(EBP-0x10))+0x1c4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, constructor/unwind direction, runtime device-object behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "device-object")),
            new Spec("0x005d2701", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b574 points at this body; decompile/instruction evidence shows it calls CFEPMultiplayerStart__ClearJoinedPlayerSet on the subobject at (*(EBP-0x10))+0x2bc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, concrete CFEPMultiplayerStart field layout, runtime multiplayer-start cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "fepmultiplayerstart", "sptrset", "clear")),
            new Spec("0x005d270f", "Wave750 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b57c points at this body; decompile/instruction evidence shows it calls CFEPMultiplayerStart__ClearSecondaryPlayerSet on the subobject at (*(EBP-0x10))+0x2ec. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, concrete CFEPMultiplayerStart field layout, runtime multiplayer-start cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "fepmultiplayerstart", "sptrset", "clear"))
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
            throw new IllegalStateException("Wave750 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
