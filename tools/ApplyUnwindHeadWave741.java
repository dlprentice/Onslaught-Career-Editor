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

public class ApplyUnwindHeadWave741 extends GhidraScript {
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
            "unwind-head-wave741",
            "wave741-readback-verified",
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
                "0x005d0f10",
                "Unwind@005d0f10",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619e04 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Monitor.h debug path 0x00622b80, line 0x18, and memtype 0x5e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "free-object", "scope-table", "monitor-h")
            ),
            new Spec(
                "0x005d0f30",
                "Unwind@005d0f30",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619e2c points at this body; decompile/instruction evidence shows it forwards the pointer at EBP-0x10 to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown-thunk", "scope-table")
            ),
            new Spec(
                "0x005d0f38",
                "Unwind@005d0f38",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619e34 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded reader at EBP-0x10 plus 0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader", "scope-table")
            ),
            new Spec(
                "0x005d0f50",
                "Unwind@005d0f50",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619e5c points at this body; decompile/instruction evidence shows it forwards the pointer at EBP-0x10 to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown-thunk", "scope-table")
            ),
            new Spec(
                "0x005d0f70",
                "Unwind@005d0f70",
                "Wave741 static read-back: AirUnit.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619e84 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x80 with AirUnit.cpp debug path 0x00622cf4, line 0x2a, and memtype 0x10. Static retail Ghidra metadata/decompile/xref evidence only; runtime aircraft effect cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("airunit", "free-object", "scope-table", "airunit-cpp")
            ),
            new Spec(
                "0x005d0f86",
                "Unwind@005d0f86",
                "Wave741 static read-back: AirUnit.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619e8c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x80 with AirUnit.cpp debug path 0x00622cf4, line 0x36, and memtype 0x10. Static retail Ghidra metadata/decompile/xref evidence only; runtime aircraft effect cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("airunit", "free-object", "scope-table", "airunit-cpp")
            ),
            new Spec(
                "0x005d0fb0",
                "Unwind@005d0fb0",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619eb4 points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime resource cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("resource-descriptor", "dxlandscape-cleanup", "scope-table")
            ),
            new Spec(
                "0x005d0fd0",
                "Unwind@005d0fd0",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619edc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown", "scope-table")
            ),
            new Spec(
                "0x005d0ff0",
                "Unwind@005d0ff0",
                "Wave741 static read-back: Atmospherics.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f04 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Atmospherics.cpp debug path 0x00622ec4, line 0x70, and memtype 0x65. Static retail Ghidra metadata/decompile/xref evidence only; runtime weather cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("atmospherics", "free-object", "scope-table", "atmospherics-cpp")
            ),
            new Spec(
                "0x005d1006",
                "Unwind@005d1006",
                "Wave741 static read-back: Atmospherics.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f0c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Atmospherics.cpp debug path 0x00622ec4, line 0x73, and memtype 0x65. Static retail Ghidra metadata/decompile/xref evidence only; runtime weather cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("atmospherics", "free-object", "scope-table", "atmospherics-cpp")
            ),
            new Spec(
                "0x005d1030",
                "Unwind@005d1030",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f34 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x490 with BattleEngine.cpp debug path 0x006230bc, line 0x63, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d1049",
                "Unwind@005d1049",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f3c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x490 with BattleEngine.cpp debug path 0x006230bc, line 0x64, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d1062",
                "Unwind@005d1062",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f44 points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime resource cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("resource-descriptor", "dxlandscape-cleanup", "scope-table")
            ),
            new Spec(
                "0x005d106d",
                "Unwind@005d106d",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f4c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x490 with BattleEngine.cpp debug path 0x006230bc, line 0xb1, and memtype 0x10. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d1089",
                "Unwind@005d1089",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f54 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x490 with BattleEngine.cpp debug path 0x006230bc, line 0xbd, and memtype 0x10. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d10a5",
                "Unwind@005d10a5",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f5c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x490 with BattleEngine.cpp debug path 0x006230bc, line 0xc8, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d10c1",
                "Unwind@005d10c1",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f64 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x47c with BattleEngine.cpp debug path 0x006230bc, line 0x1f5, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d10dd",
                "Unwind@005d10dd",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f6c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x47c with BattleEngine.cpp debug path 0x006230bc, line 0x108, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d10f9",
                "Unwind@005d10f9",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f74 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x47c with BattleEngine.cpp debug path 0x006230bc, line 0x124, and memtype 0x15. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine construction cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "free-object", "scope-table", "battleengine-cpp")
            ),
            new Spec(
                "0x005d1115",
                "Unwind@005d1115",
                "Wave741 static read-back: BattleEngine.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619f7c points at this body; decompile/instruction evidence shows it forwards the pointer at EBP-0x47c to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; runtime BattleEngine cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("battleengine", "monitor", "shutdown-thunk", "scope-table")
            ),
            new Spec(
                "0x005d1130",
                "Unwind@005d1130",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619fa4 points at this body; decompile/instruction evidence shows it calls CUnit__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime unit cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "destructor", "scope-table")
            ),
            new Spec(
                "0x005d1138",
                "Unwind@005d1138",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619fac points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field EBP-0x10 plus 0x250. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d1146",
                "Unwind@005d1146",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619fb4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x264. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "active-reader", "scope-table")
            ),
            new Spec(
                "0x005d1154",
                "Unwind@005d1154",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619fbc points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field EBP-0x10 plus 0x284. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "sptrset-clear", "scope-table")
            ),
            new Spec(
                "0x005d1162",
                "Unwind@005d1162",
                "Wave741 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x00619fc4 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field EBP-0x10 plus 0x294. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit", "sptrset-clear", "scope-table")
            )
        };

        println("ApplyUnwindHeadWave741 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave741 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
