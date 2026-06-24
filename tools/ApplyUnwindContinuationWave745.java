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

public class ApplyUnwindContinuationWave745 extends GhidraScript {
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
            "unwind-continuation-wave745",
            "wave745-readback-verified",
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
            new Spec("0x005d1840", "Wave745 static read-back: Carrier.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a6ac points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Carrier.cpp debug path 0x006243bc, line 0x1a, and memtype 0x17. Static retail Ghidra metadata/decompile/xref evidence only; runtime carrier allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("carrier", "carrier-cpp", "free-object")),
            new Spec("0x005d1856", "Wave745 static read-back: Carrier.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a6b4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Carrier.cpp debug path 0x006243bc, line 0x1b, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime carrier allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("carrier", "carrier-cpp", "free-object")),
            new Spec("0x005d1880", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carrier-region scope-table run. Scope-table data xref 0x0061a6dc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("carrier", "monitor", "shutdown")),
            new Spec("0x005d1888", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carrier-region scope-table run. Scope-table data xref 0x0061a6e4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("carrier", "active-reader", "embedded-reader")),
            new Spec("0x005d1893", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carrier-region scope-table run. Scope-table data xref 0x0061a6ec points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("carrier", "active-reader", "embedded-reader")),
            new Spec("0x005d18b0", "Wave745 static read-back: Carver.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a714 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Carver.cpp debug path 0x00624400, line 0x16, and memtype 0x17. Static retail Ghidra metadata/decompile/xref evidence only; runtime carver allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("carver", "carver-cpp", "free-object")),
            new Spec("0x005d18c6", "Wave745 static read-back: Carver.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a71c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Carver.cpp debug path 0x00624400, line 0x17, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime carver allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("carver", "carver-cpp", "free-object")),
            new Spec("0x005d18f0", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carver-region scope-table run. Scope-table data xref 0x0061a744 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("carver", "monitor", "shutdown")),
            new Spec("0x005d18f8", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carver-region scope-table run. Scope-table data xref 0x0061a74c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("carver", "active-reader", "embedded-reader")),
            new Spec("0x005d1903", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carver-region scope-table run. Scope-table data xref 0x0061a754 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("carver", "active-reader", "embedded-reader")),
            new Spec("0x005d1920", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Carver-region scope-table run. Scope-table data xref 0x0061a77c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("carver", "monitor", "shutdown", "thunk")),
            new Spec("0x005d1940", "Wave745 static read-back: chunker.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a7a4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with chunker.cpp debug path 0x00624464, line 0x62, and memtype 0x11. Static retail Ghidra metadata/decompile/xref evidence only; runtime chunk-reader/resource allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("chunker", "chunker-cpp", "free-object")),
            new Spec("0x005d1960", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the chunker/resource scope-table run. Scope-table data xref 0x0061a7cc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the large stack-local pointer at EBP-0x468. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("chunker", "monitor", "shutdown", "stack-local")),
            new Spec("0x005d196b", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the chunker/resource scope-table run. Scope-table data xref 0x0061a7d4 points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on stack local EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime resource-descriptor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("chunker", "cdxlandscape", "resource-descriptor", "stack-local")),
            new Spec("0x005d1980", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the chunker/resource scope-table run. Scope-table data xref 0x0061a7fc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("chunker", "monitor", "shutdown")),
            new Spec("0x005d19a0", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the chunker/resource scope-table run. Scope-table data xref 0x0061a824 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("chunker", "monitor", "shutdown")),
            new Spec("0x005d19c0", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the chunker/resource scope-table run. Scope-table data xref 0x0061a84c points at this body; decompile/instruction evidence shows it calls CLine__SetBaseVtable_00426360 on stack local EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("chunker", "line-helper", "stack-local")),
            new Spec("0x005d19e0", "Wave745 static read-back: Component.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a874 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Component.cpp debug path 0x006247f8, line 0x4d, and memtype 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; runtime component allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("component", "component-cpp", "free-object")),
            new Spec("0x005d1a00", "Wave745 static read-back: Component.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a89c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Component.cpp debug path 0x006247f8, line 0x53, and memtype 0x17. Static retail Ghidra metadata/decompile/xref evidence only; runtime component allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("component", "component-cpp", "free-object")),
            new Spec("0x005d1a20", "Wave745 static read-back: Component.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a8c4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Component.cpp debug path 0x006247f8, line 0x5c, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime component allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("component", "component-cpp", "free-object")),
            new Spec("0x005d1a36", "Wave745 static read-back: Component.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a8cc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Component.cpp debug path 0x006247f8, line 0x5e, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime component allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("component", "component-cpp", "free-object")),
            new Spec("0x005d1a4c", "Wave745 static read-back: Component.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a8d4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Component.cpp debug path 0x006247f8, line 0x60, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime component allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("component", "component-cpp", "free-object")),
            new Spec("0x005d1a62", "Wave745 static read-back: Component.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a8dc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Component.cpp debug path 0x006247f8, line 0x63, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime component allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("component", "component-cpp", "free-object")),
            new Spec("0x005d1a90", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Component.cpp scope-table run. Scope-table data xref 0x0061a904 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("component", "monitor", "shutdown")),
            new Spec("0x005d1a98", "Wave745 static read-back: compiler-generated SEH unwind cleanup callback in the Component.cpp scope-table run. Scope-table data xref 0x0061a90c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field *(EBP-0x10)+0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("component", "active-reader", "embedded-reader"))
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
            throw new IllegalStateException("Wave745 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
