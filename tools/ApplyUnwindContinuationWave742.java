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

public class ApplyUnwindContinuationWave742 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
            "unwind-continuation-wave742",
            "wave742-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "compiler-unwind"
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
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED
            );
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
            new Spec(
                "0x005d1170",
                "Unwind@005d1170",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619fcc points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field EBP-0x10 plus 0x2a4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d117e",
                "Unwind@005d117e",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619fd4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x4c8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "active-reader", "scope-table")
            ),
            new Spec(
                "0x005d118c",
                "Unwind@005d118c",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619fdc points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x4cc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "active-reader", "scope-table")
            ),
            new Spec(
                "0x005d119a",
                "Unwind@005d119a",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619fe4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x4e0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "active-reader", "scope-table")
            ),
            new Spec(
                "0x005d11a8",
                "Unwind@005d11a8",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619fec points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x574. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "active-reader", "scope-table")
            ),
            new Spec(
                "0x005d11b6",
                "Unwind@005d11b6",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619ff4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x5e8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "active-reader", "scope-table")
            ),
            new Spec(
                "0x005d11c4",
                "Unwind@005d11c4",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x00619ffc points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on object field EBP-0x10 plus 0x5f8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "particle-manager", "scope-table")
            ),
            new Spec(
                "0x005d11d2",
                "Unwind@005d11d2",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741 Unit/BattleEngine-adjacent unwind table. Scope-table data xref 0x0061a004 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field EBP-0x10 plus 0x620. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d11f0",
                "Unwind@005d11f0",
                "Wave742 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a02c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with BattleEngine.cpp debug path 0x006230bc, line 0x1f5, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "battleengine-cpp", "free-object", "scope-table")
            ),
            new Spec(
                "0x005d1220",
                "Unwind@005d1220",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a054 points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on stack local EBP-0x180. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("line-vtable", "stack-local", "scope-table")
            ),
            new Spec(
                "0x005d1240",
                "Unwind@005d1240",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a07c points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on stack local EBP-0xb0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("line-vtable", "stack-local", "scope-table")
            ),
            new Spec(
                "0x005d1260",
                "Unwind@005d1260",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a0a4 points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on stack local EBP-0x70. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("line-vtable", "stack-local", "scope-table")
            ),
            new Spec(
                "0x005d1280",
                "Unwind@005d1280",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a0cc points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on stack local EBP-0x134. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("line-vtable", "stack-local", "scope-table")
            ),
            new Spec(
                "0x005d128b",
                "Unwind@005d128b",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a0d4 points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on stack local EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("line-vtable", "stack-local", "scope-table")
            ),
            new Spec(
                "0x005d12a0",
                "Unwind@005d12a0",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a0fc points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on stack local EBP-0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("particle-manager", "stack-local", "scope-table")
            ),
            new Spec(
                "0x005d12c0",
                "Unwind@005d12c0",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a124 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field EBP-0x10 plus 0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d12e0",
                "Unwind@005d12e0",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a14c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d1300",
                "Unwind@005d1300",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a174 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d1320",
                "Unwind@005d1320",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a19c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d1340",
                "Unwind@005d1340",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a1c4 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d1360",
                "Unwind@005d1360",
                "Wave742 static read-back: Boat.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a1ec points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Boat.cpp debug path 0x00623990, line 0x1e, and memtype 0x17. Static retail Ghidra metadata/decompile/xref evidence only; runtime boat allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("boat", "boat-cpp", "free-object", "scope-table")
            ),
            new Spec(
                "0x005d1376",
                "Unwind@005d1376",
                "Wave742 static read-back: Boat.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a1f4 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Boat.cpp debug path 0x00623990, line 0x1f, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime boat allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("boat", "boat-cpp", "free-object", "scope-table")
            ),
            new Spec(
                "0x005d13a0",
                "Unwind@005d13a0",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a21c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown", "scope-table")
            ),
            new Spec(
                "0x005d13a8",
                "Unwind@005d13a8",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a224 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader", "scope-table")
            ),
            new Spec(
                "0x005d13b3",
                "Unwind@005d13b3",
                "Wave742 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a22c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader", "scope-table")
            )
        };

        println("ApplyUnwindContinuationWave742 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave742 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
