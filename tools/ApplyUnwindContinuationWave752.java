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

public class ApplyUnwindContinuationWave752 extends GhidraScript {
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
            "unwind-continuation-wave752",
            "wave752-readback-verified",
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
            new Spec("0x005d29f1", "Wave752 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b7cc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x1c) with game.cpp debug path 0x0062bba4, line 0x27, and allocation/type value 0x11bf. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2a20", "Wave752 static read-back: GillM.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b7f4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with GillM.cpp debug path 0x0062c9e8, line 0x1b, and allocation/type value 0x2d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillM cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm", "free-object")),
            new Spec("0x005d2a40", "Wave752 static read-back: GillM.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b81c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with GillM.cpp debug path 0x0062c9e8, line 0x16, and allocation/type value 0x38. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillM cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm", "free-object")),
            new Spec("0x005d2a60", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GillM.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b844 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillM monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm", "monitor", "shutdown")),
            new Spec("0x005d2a68", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GillM.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b84c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillM active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm", "active-reader", "destructor")),
            new Spec("0x005d2a73", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GillM.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b854 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillM active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm", "active-reader", "destructor")),
            new Spec("0x005d2a90", "Wave752 static read-back: GillM.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b87c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with GillM.cpp debug path 0x0062c9e8, line 0x17, and allocation/type value 0x3e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillM cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm", "free-object")),
            new Spec("0x005d2ab0", "Wave752 static read-back: GillMHead.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b8a4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with GillMHead.cpp debug path 0x0062ca6c, line 0x16, and allocation/type value 0x13. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillMHead cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm-head", "free-object")),
            new Spec("0x005d2ad0", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GillMHead.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b8cc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillMHead monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm-head", "monitor", "shutdown")),
            new Spec("0x005d2ad8", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GillMHead.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b8d4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillMHead active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm-head", "active-reader", "destructor")),
            new Spec("0x005d2ae3", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GillMHead.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b8dc points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime GillMHead active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("gillm-head", "active-reader", "destructor")),
            new Spec("0x005d2b00", "Wave752 static read-back: GroundAttackAircraft.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b904 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundAttackAircraft.cpp debug path 0x0062cadc, line 0x1b, and allocation/type value 0x13. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "free-object")),
            new Spec("0x005d2b16", "Wave752 static read-back: GroundAttackAircraft.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b90c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundAttackAircraft.cpp debug path 0x0062cadc, line 0x16, and allocation/type value 0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "free-object")),
            new Spec("0x005d2b2c", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GroundAttackAircraft.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b914 points at this body; decompile/instruction evidence shows it calls CUnitAI__dtor_body_00415080 on the object pointer at *(EBP+0x4). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft AI cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "unit-ai", "destructor")),
            new Spec("0x005d2b34", "Wave752 static read-back: GroundAttackAircraft.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b91c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundAttackAircraft.cpp debug path 0x0062cadc, line 0x17, and allocation/type value 0x15. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "free-object")),
            new Spec("0x005d2b60", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GroundAttackAircraft.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b944 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "monitor", "shutdown")),
            new Spec("0x005d2b68", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GroundAttackAircraft.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b94c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "active-reader", "destructor")),
            new Spec("0x005d2b73", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GroundAttackAircraft.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b954 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "active-reader", "destructor")),
            new Spec("0x005d2b90", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GroundAttackAircraft.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b97c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-attack aircraft monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-attack-aircraft", "monitor", "shutdown", "thunk")),
            new Spec("0x005d2bb0", "Wave752 static read-back: GroundUnit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b9a4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundUnit.cpp debug path 0x0062cb0c, line 0x10, and allocation/type value 0x23. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-unit cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-unit", "free-object")),
            new Spec("0x005d2bd0", "Wave752 static read-back: GroundVehicle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b9cc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundVehicle.cpp debug path 0x0062cb30, line 0x1b, and allocation/type value 0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-vehicle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-vehicle", "free-object")),
            new Spec("0x005d2be6", "Wave752 static read-back: GroundVehicle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b9d4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundVehicle.cpp debug path 0x0062cb30, line 0x1b, and allocation/type value 0x21. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-vehicle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-vehicle", "free-object")),
            new Spec("0x005d2bfc", "Wave752 static read-back: GroundVehicle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b9dc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundVehicle.cpp debug path 0x0062cb30, line 0x17, and allocation/type value 0x23. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-vehicle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-vehicle", "free-object")),
            new Spec("0x005d2c12", "Wave752 static read-back: GroundVehicle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b9e4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with GroundVehicle.cpp debug path 0x0062cb30, line 0x16, and allocation/type value 0x25. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-vehicle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-vehicle", "free-object")),
            new Spec("0x005d2c40", "Wave752 static read-back: compiler-generated SEH unwind cleanup callback in the GroundVehicle.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061ba0c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ground-vehicle monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("ground-vehicle", "monitor", "shutdown", "thunk"))
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
            throw new IllegalStateException("Wave752 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
