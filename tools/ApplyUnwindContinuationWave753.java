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

public class ApplyUnwindContinuationWave753 extends GhidraScript {
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
            "unwind-continuation-wave753",
            "wave753-readback-verified",
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
            new Spec("0x005d2c48", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the post-GroundVehicle scope-table run. Scope-table DATA xref 0x0061ba14 points at this body; decompile/instruction evidence shows it calls CDXLandscape__FreeObjectCallback on (*(EBP+0x4))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d2c53", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the post-GroundVehicle scope-table run. Scope-table DATA xref 0x0061ba1c points at this body; decompile/instruction evidence shows it calls CUnitAI__FreeOwnedObjects_10_18 on (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime UnitAI-owned-object cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit-ai", "free-owned-objects")),
            new Spec("0x005d2c70", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the post-GroundVehicle scope-table run. Scope-table DATA xref 0x0061ba44 points at this body; decompile/instruction evidence shows it calls CDXLandscape__FreeObjectCallback on (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d2c90", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the post-GroundVehicle scope-table run. Scope-table DATA xref 0x0061ba6c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d2c98", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the post-GroundVehicle scope-table run. Scope-table DATA xref 0x0061ba74 points at this body; decompile/instruction evidence shows it calls CDXLandscape__FreeObjectCallback on (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d2cb0", "Wave753 static read-back: HiveBoss.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ba9c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with HiveBoss.cpp debug path 0x0062cc98, line 0x55, and allocation/type value 0x21. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HiveBoss cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hiveboss", "free-object")),
            new Spec("0x005d2cc6", "Wave753 static read-back: HiveBoss.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061baa4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with HiveBoss.cpp debug path 0x0062cc98, line 0x1b, and allocation/type value 0x22. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HiveBoss cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hiveboss", "free-object")),
            new Spec("0x005d2cdc", "Wave753 static read-back: HiveBoss.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061baac points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with HiveBoss.cpp debug path 0x0062cc98, line 0x17, and allocation/type value 0x28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HiveBoss cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hiveboss", "free-object")),
            new Spec("0x005d2d00", "Wave753 static read-back: Hud.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bad4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with Hud.cpp debug path 0x0062ce78, line 0x38, and allocation/type value 0x5d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "free-object")),
            new Spec("0x005d2d16", "Wave753 static read-back: Hud.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061badc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with Hud.cpp debug path 0x0062ce78, line 0x38, and allocation/type value 0x5f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "free-object")),
            new Spec("0x005d2d40", "Wave753 static read-back: Hud.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bb04 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x8) with Hud.cpp debug path 0x0062ce78, line 0x38, and allocation/type value 0x137. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "free-object")),
            new Spec("0x005d2d59", "Wave753 static read-back: Hud.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bb0c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x8) with Hud.cpp debug path 0x0062ce78, line 0x38, and allocation/type value 0x13b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "free-object")),
            new Spec("0x005d2d80", "Wave753 static read-back: Hud.cpp-adjacent compiler-generated SEH unwind local-set cleanup callback. Scope-table DATA xref 0x0061bb34 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local set at EBP-0x4c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "sptrset", "clear")),
            new Spec("0x005d2d88", "Wave753 static read-back: Hud.cpp-adjacent compiler-generated SEH unwind local-set cleanup callback. Scope-table DATA xref 0x0061bb3c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local set at EBP-0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "sptrset", "clear")),
            new Spec("0x005d2d90", "Wave753 static read-back: Hud.cpp-adjacent compiler-generated SEH unwind local-set cleanup callback. Scope-table DATA xref 0x0061bb44 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local set at EBP-0x3c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "sptrset", "clear")),
            new Spec("0x005d2d98", "Wave753 static read-back: Hud.cpp-adjacent compiler-generated SEH unwind local-set cleanup callback. Scope-table DATA xref 0x0061bb4c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the stack-local set at EBP-0x5c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime HUD set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "sptrset", "clear")),
            new Spec("0x005d2db0", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the Hud.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061bb74 points at this body; decompile/instruction evidence shows it loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper semantics, runtime device-object cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "device-object")),
            new Spec("0x005d2dd0", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the Hud.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061bb9c points at this body; decompile/instruction evidence shows it loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper semantics, runtime device-object cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("hud", "device-object")),
            new Spec("0x005d2df0", "Wave753 static read-back: imposter.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bbc4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x1c) with imposter.cpp debug path 0x0062d3f0, line 0x39, and allocation/type value 0x29. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime imposter cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("imposter", "free-object")),
            new Spec("0x005d2e10", "Wave753 static read-back: Infantry.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bbec points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with Infantry.cpp debug path 0x0062d4a8, line 0x0b, and allocation/type value 0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime infantry cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("infantry", "free-object")),
            new Spec("0x005d2e26", "Wave753 static read-back: Infantry.cpp-adjacent compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bbf4 points at this body; decompile/instruction evidence shows it calls CCollisionSeekingRound__Destructor on the object pointer at *(EBP+0x4). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime seeking-round cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("infantry", "collision-seeking-round", "destructor")),
            new Spec("0x005d2e2e", "Wave753 static read-back: Infantry.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bbfc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with Infantry.cpp debug path 0x0062d4a8, line 0x17, and allocation/type value 0x46. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime infantry cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("infantry", "free-object")),
            new Spec("0x005d2e44", "Wave753 static read-back: Infantry.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bc04 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with Infantry.cpp debug path 0x0062d4a8, line 0x16, and allocation/type value 0x47. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime infantry cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("infantry", "free-object")),
            new Spec("0x005d2e70", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the Infantry.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061bc2c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime infantry monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("infantry", "monitor", "shutdown")),
            new Spec("0x005d2e78", "Wave753 static read-back: compiler-generated SEH unwind cleanup callback in the Infantry.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061bc34 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime infantry active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("infantry", "active-reader", "destructor"))
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
            throw new IllegalStateException("Wave753 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
