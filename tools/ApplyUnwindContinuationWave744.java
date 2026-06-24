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

public class ApplyUnwindContinuationWave744 extends GhidraScript {
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
            "unwind-continuation-wave744",
            "wave744-readback-verified",
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
            new Spec("0x005d1610", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a47c points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera")),
            new Spec("0x005d1618", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a484 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "embedded-reader")),
            new Spec("0x005d1630", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a4ac points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera")),
            new Spec("0x005d1638", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a4b4 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on embedded object field EBP-0x24 plus 0x4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "embedded-monitor")),
            new Spec("0x005d1643", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a4bc points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the pointer at EBP-0x20. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d164b", "Wave744 static read-back: Monitor.h compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a4c4 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Monitor.h debug path 0x00622b80, line 0x18, and memtype 0x5e. Static retail Ghidra metadata/decompile/xref evidence only; runtime monitor allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("monitor", "monitor-h", "free-object")),
            new Spec("0x005d1661", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a4cc points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x24 plus 0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "embedded-reader")),
            new Spec("0x005d1680", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a4f4 points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera")),
            new Spec("0x005d1688", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a4fc points at this body; decompile/instruction evidence shows it conditionally derives EBP-0x14 from pointer EBP-0x10 plus 0x4 when non-null, then calls CMonitor__Shutdown on the derived pointer. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "conditional-cleanup")),
            new Spec("0x005d16af", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a504 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "embedded-reader")),
            new Spec("0x005d16d0", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a52c points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera")),
            new Spec("0x005d16d8", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a534 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the pointer at EBP-0x20. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d16e0", "Wave744 static read-back: Monitor.h compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a53c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Monitor.h debug path 0x00622b80, line 0x18, and memtype 0x5e. Static retail Ghidra metadata/decompile/xref evidence only; runtime monitor allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("monitor", "monitor-h", "free-object")),
            new Spec("0x005d1700", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a564 points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera")),
            new Spec("0x005d1720", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a58c points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera")),
            new Spec("0x005d1740", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a5b4 points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the large stack-local pointer at EBP-0x1a0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("camera", "generic-camera", "stack-local")),
            new Spec("0x005d1760", "Wave744 static read-back: Cannon.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a5dc points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Cannon.cpp debug path 0x00623dd4, line 0x22, and memtype 0x17. Static retail Ghidra metadata/decompile/xref evidence only; runtime cannon allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("cannon", "cannon-cpp", "free-object")),
            new Spec("0x005d1776", "Wave744 static read-back: Cannon.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a5e4 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Cannon.cpp debug path 0x00623dd4, line 0x23, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime cannon allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("cannon", "cannon-cpp", "free-object")),
            new Spec("0x005d178c", "Wave744 static read-back: Cannon.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a5ec points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Cannon.cpp debug path 0x00623dd4, line 0x26, and memtype 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; runtime cannon allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("cannon", "cannon-cpp", "free-object")),
            new Spec("0x005d17b0", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a61c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on stack local EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "stack-local")),
            new Spec("0x005d17b8", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a614 points at this body; decompile/instruction evidence shows it tests flag word EBP-0x20 bit 0 and conditionally calls CSPtrSet__Clear on the pointer at EBP+4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "conditional-cleanup")),
            new Spec("0x005d17e0", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a64c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on stack local EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "stack-local")),
            new Spec("0x005d17e8", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a654 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on stack local EBP-0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "stack-local")),
            new Spec("0x005d17f0", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a644 points at this body; decompile/instruction evidence shows it tests flag word EBP-0x30 bit 0 and conditionally calls CSPtrSet__Clear on the pointer at EBP+4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "conditional-cleanup")),
            new Spec("0x005d1820", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a67c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on stack local EBP-0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "stack-local")),
            new Spec("0x005d1828", "Wave744 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741-Wave743 unwind table. Scope-table data xref 0x0061a684 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on stack local EBP-0x1c, closing the local set-clear pair immediately before the next Carrier.cpp allocation-cleanup cluster. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "stack-local"))
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
            throw new IllegalStateException("Wave744 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
