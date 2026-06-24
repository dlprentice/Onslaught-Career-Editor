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

public class ApplyUnwindContinuationWave746 extends GhidraScript {
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
            "unwind-continuation-wave746",
            "wave746-readback-verified",
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
            new Spec("0x005d1aa3", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in the post-Component active-reader scope-table run. Scope-table DATA xref 0x0061a914 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "embedded-reader", "component-adjacent")),
            new Spec("0x005d1ac0", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in an adjacent monitor/active-reader scope-table run. Scope-table DATA xref 0x0061a93c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d1ac8", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in an adjacent monitor/active-reader scope-table run. Scope-table DATA xref 0x0061a944 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "embedded-reader")),
            new Spec("0x005d1ad3", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in an adjacent monitor/active-reader scope-table run. Scope-table DATA xref 0x0061a94c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "embedded-reader")),
            new Spec("0x005d1af0", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in an adjacent DX memory-buffer scope-table run. Scope-table DATA xref 0x0061a974 points at this body; decompile/instruction evidence shows it calls CDXMemBuffer__dtor_base on stack local EBP-0x240. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dxmembuffer", "stack-local")),
            new Spec("0x005d1b10", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in the Controller.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061a99c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x18)+0x4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("controller", "sptrset", "clear")),
            new Spec("0x005d1b1b", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in the Controller.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061a9a4 points at this body; decompile/instruction evidence shows it calls CDXMemBuffer__dtor_base on object field *(EBP-0x18)+0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime DX memory-buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("controller", "dxmembuffer")),
            new Spec("0x005d1b26", "Wave746 static read-back: Controller.cpp compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061a9ac points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x14 with Controller.cpp debug path 0x00625538, line 0x27, and memtype 0x3c7. Static retail Ghidra metadata/decompile/xref evidence only; runtime controller allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("controller", "controller-cpp", "free-object")),
            new Spec("0x005d1b3f", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in the Controller.cpp-adjacent active-reader scope-table run. Scope-table DATA xref 0x0061a9b4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the pointer at EBP-0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("controller", "active-reader")),
            new Spec("0x005d1b47", "Wave746 static read-back: monitor.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061a9bc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with monitor.h debug path 0x0062551c, line 0x5e, and memtype 0x18. Static retail Ghidra metadata/decompile/xref evidence only; runtime monitor allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("monitor", "monitor-h", "free-object")),
            new Spec("0x005d1b70", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a Controller/monitor-adjacent scope-table run. Scope-table DATA xref 0x0061a9e4 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear")),
            new Spec("0x005d1b7b", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a Controller/monitor-adjacent scope-table run. Scope-table DATA xref 0x0061a9ec points at this body; decompile/instruction evidence shows it calls CDXMemBuffer__dtor_base on object field *(EBP-0x10)+0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime DX memory-buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("dxmembuffer")),
            new Spec("0x005d1b90", "Wave746 static read-back: Controller.cpp compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061aa14 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Controller.cpp debug path 0x00625538, line 0x27, and memtype 0x3c7. Static retail Ghidra metadata/decompile/xref evidence only; runtime controller allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("controller", "controller-cpp", "free-object")),
            new Spec("0x005d1ba9", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a Controller/monitor-adjacent active-reader scope-table run. Scope-table DATA xref 0x0061aa1c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d1bb1", "Wave746 static read-back: monitor.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061aa24 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with monitor.h debug path 0x0062551c, line 0x5e, and memtype 0x18. Static retail Ghidra metadata/decompile/xref evidence only; runtime monitor allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("monitor", "monitor-h", "free-object")),
            new Spec("0x005d1be0", "Wave746 static read-back: CPhysicsScript.cpp compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061aa4c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with CPhysicsScript.cpp debug path 0x0062568c, line 0x18, and memtype 0x10. Static retail Ghidra metadata/decompile/xref evidence only; runtime physics-script allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "cphysicsscript-cpp", "free-object")),
            new Spec("0x005d1c00", "Wave746 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061aa74 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0xf, and memtype 0x971. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1c19", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set run. Scope-table DATA xref 0x0061aa7c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x3c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1c24", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set run. Scope-table DATA xref 0x0061aa84 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x4c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1c2f", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set run. Scope-table DATA xref 0x0061aa8c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x5c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1c3a", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set run. Scope-table DATA xref 0x0061aa94 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x6c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1c50", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in the CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061aabc points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1c70", "Wave746 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061aae4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x3d, and memtype 0x95c. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1ca0", "Wave746 static read-back: compiler-generated SEH unwind cleanup callback in the CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061ab0c points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1cc0", "Wave746 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061ab34 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x3c, and memtype 0x955. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object"))
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
            throw new IllegalStateException("Wave746 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
