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

public class ApplyUnwindContinuationWave754 extends GhidraScript {
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
            "unwind-continuation-wave754",
            "wave754-readback-verified",
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
            new Spec("0x005d2e83", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback immediately after the Infantry.cpp run. Scope-table DATA xref 0x0061bc3c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "destructor")),
            new Spec("0x005d2ea0", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bc64 points at this body; decompile/instruction evidence shows it calls CCollisionSeekingRound__Destructor on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime seeking-round cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("collision-seeking-round", "destructor")),
            new Spec("0x005d2ec0", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bc8c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d2ec8", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bc94 points at this body; decompile/instruction evidence shows it calls CDXLandscape__FreeObjectCallback on (*(EBP+0x4))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d2ed3", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bc9c points at this body; decompile/instruction evidence shows it calls CUnitAI__FreeOwnedObjects_10_18 on (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime UnitAI-owned-object cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit-ai", "free-owned-objects")),
            new Spec("0x005d2ede", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bca4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on (*(EBP-0x10))+0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "destructor")),
            new Spec("0x005d2f00", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bccc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d2f08", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bcd4 points at this body; decompile/instruction evidence shows it calls CUnitAI__FreeOwnedObjects_10_18 on (*(EBP-0x14))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime UnitAI-owned-object cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit-ai", "free-owned-objects")),
            new Spec("0x005d2f13", "Wave754 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061bcdc points at this body; decompile/instruction evidence shows it calls CDXLandscape__FreeObjectCallback on (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d2f30", "Wave754 static read-back: InfluenceMap.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bd1c points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP-0x3d0) with InfluenceMap.cpp debug path 0x0062d61c, line token 0x20, and allocation/type value 0x74. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "free-object")),
            new Spec("0x005d2f49", "Wave754 static read-back: InfluenceMap.cpp-adjacent compiler-generated SEH unwind destructor callback. Scope-table DATA xref 0x0061bd24 points at this body; decompile/instruction evidence shows it calls CComplexThing__dtor_base on *(EBP-0x3d0). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap/ComplexThing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "complexthing", "destructor")),
            new Spec("0x005d2f54", "Wave754 static read-back: InfluenceMap.cpp-adjacent compiler-generated SEH unwind set-cleanup callback. Scope-table DATA xref 0x0061bd2c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on (*(EBP-0x3d0))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "sptrset", "clear")),
            new Spec("0x005d2f62", "Wave754 static read-back: InfluenceMap.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bd04 points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP-0x3d0) with InfluenceMap.cpp debug path 0x0062d61c, line token 0x20, and allocation/type value 0x46. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "free-object")),
            new Spec("0x005d2f7b", "Wave754 static read-back: InfluenceMap.cpp-adjacent compiler-generated SEH unwind destructor callback. Scope-table DATA xref 0x0061bd0c points at this body; decompile/instruction evidence shows it calls CComplexThing__dtor_base on *(EBP-0x3d0). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap/ComplexThing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "complexthing", "destructor")),
            new Spec("0x005d2f86", "Wave754 static read-back: InfluenceMap.cpp-adjacent compiler-generated SEH unwind set-cleanup callback. Scope-table DATA xref 0x0061bd14 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on (*(EBP-0x3d0))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "sptrset", "clear")),
            new Spec("0x005d2fa0", "Wave754 static read-back: InfluenceMap.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bd54 points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP-0x10) with InfluenceMap.cpp debug path 0x0062d61c, line token 0x20, and allocation/type value 0x1a6. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime InfluenceMap cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("influencemap", "free-object")),
            new Spec("0x005d2fd0", "Wave754 static read-back: compiler-generated SEH unwind destructor callback in the InfluenceMap-to-InitThing transition run. Scope-table DATA xref 0x0061bd7c points at this body; decompile/instruction evidence shows it calls CComplexThing__dtor_base on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime ComplexThing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complexthing", "destructor")),
            new Spec("0x005d2ff0", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bda4 points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x0f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d3006", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bdac points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x13. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d301c", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bdb4 points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d3032", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bdbc points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d3048", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bdc4 points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x1f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d305e", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bdcc points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x23. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d3074", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bdd4 points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x27. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d308a", "Wave754 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback in the InitThing factory run. Scope-table DATA xref 0x0061bddc points at this body; instruction evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x2b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object"))
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
            throw new IllegalStateException("Wave754 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
