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

public class ApplyUnwindContinuationWave743 extends GhidraScript {
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
            "unwind-continuation-wave743",
            "wave743-readback-verified",
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
                "0x005d13d0",
                "Unwind@005d13d0",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a254 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown")
            ),
            new Spec(
                "0x005d13d8",
                "Unwind@005d13d8",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a25c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d13e3",
                "Unwind@005d13e3",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a264 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d1400",
                "Unwind@005d1400",
                "Wave743 static read-back: Bomber.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a28c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Bomber.cpp debug path 0x00623a78, line 0x11, and memtype 0x17. Static retail Ghidra metadata/decompile/xref evidence only; runtime bomber allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("bomber", "bomber-cpp", "free-object")
            ),
            new Spec(
                "0x005d1416",
                "Unwind@005d1416",
                "Wave743 static read-back: Bomber.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a294 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Bomber.cpp debug path 0x00623a78, line 0x12, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime bomber allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("bomber", "bomber-cpp", "free-object")
            ),
            new Spec(
                "0x005d1440",
                "Unwind@005d1440",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a2bc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown")
            ),
            new Spec(
                "0x005d1448",
                "Unwind@005d1448",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a2c4 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d1453",
                "Unwind@005d1453",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a2cc points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d1470",
                "Unwind@005d1470",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a2f4 points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown-thunk")
            ),
            new Spec(
                "0x005d1490",
                "Unwind@005d1490",
                "Wave743 static read-back: Building.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a31c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Building.cpp debug path 0x00623af4, line 0x32, and memtype 0x80. Static retail Ghidra metadata/decompile/xref evidence only; runtime building allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("building", "building-cpp", "free-object")
            ),
            new Spec(
                "0x005d14a9",
                "Unwind@005d14a9",
                "Wave743 static read-back: Building.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a324 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Building.cpp debug path 0x00623af4, line 0x33, and memtype 0x80. Static retail Ghidra metadata/decompile/xref evidence only; runtime building allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("building", "building-cpp", "free-object")
            ),
            new Spec(
                "0x005d14d0",
                "Unwind@005d14d0",
                "Wave743 static read-back: Building.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a34c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Building.cpp debug path 0x00623af4, line 0x64, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime building allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("building", "building-cpp", "free-object")
            ),
            new Spec(
                "0x005d14e6",
                "Unwind@005d14e6",
                "Wave743 static read-back: Building.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a354 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with Building.cpp debug path 0x00623af4, line 0x68, and memtype 0x16. Static retail Ghidra metadata/decompile/xref evidence only; runtime building allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("building", "building-cpp", "free-object")
            ),
            new Spec(
                "0x005d1510",
                "Unwind@005d1510",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a37c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime monitor shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("monitor", "shutdown")
            ),
            new Spec(
                "0x005d1518",
                "Unwind@005d1518",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a384 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0xc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d1523",
                "Unwind@005d1523",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a38c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on embedded object field EBP-0x10 plus 0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d1540",
                "Unwind@005d1540",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a3b4 points at this body; decompile/instruction evidence shows it calls CResourceDescriptor__dtor on stack local EBP-0x5b8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime resource-descriptor cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("resource-descriptor", "stack-local")
            ),
            new Spec(
                "0x005d1560",
                "Unwind@005d1560",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a3dc points at this body; decompile/instruction evidence shows it calls CParticleManager__RemoveFromGlobalList_Thunk on stack local EBP-0x404. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("particle-manager", "stack-local")
            ),
            new Spec(
                "0x005d1580",
                "Unwind@005d1580",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a404 points at this body; decompile/instruction evidence shows it calls CDXMemBuffer__dtor_base on stack local EBP-0x140. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime DX memory-buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dx-membuffer", "stack-local")
            ),
            new Spec(
                "0x005d158b",
                "Unwind@005d158b",
                "Wave743 static read-back: bytesprite.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a40c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x164 with bytesprite.cpp debug path 0x00623c18, line 0x1d, and memtype 0x61. Static retail Ghidra metadata/decompile/xref evidence only; runtime byte-sprite allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("bytesprite", "bytesprite-cpp", "free-object")
            ),
            new Spec(
                "0x005d15b0",
                "Unwind@005d15b0",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a434 points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the pointer at EBP-0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime generic-camera cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("camera", "generic-camera")
            ),
            new Spec(
                "0x005d15b8",
                "Unwind@005d15b8",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a43c points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader")
            ),
            new Spec(
                "0x005d15c0",
                "Unwind@005d15c0",
                "Wave743 static read-back: compiler-generated SEH unwind cleanup callback continuing the Wave741/Wave742 unwind table. Scope-table data xref 0x0061a444 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on object field EBP-0x14 plus 0x4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("active-reader", "embedded-reader")
            ),
            new Spec(
                "0x005d15cb",
                "Unwind@005d15cb",
                "Wave743 static read-back: Camera.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a44c points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Camera.cpp debug path 0x00623c90, line 0x9e, and memtype 0x28. Static retail Ghidra metadata/decompile/xref evidence only; runtime camera allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("camera", "camera-cpp", "free-object")
            ),
            new Spec(
                "0x005d15e4",
                "Unwind@005d15e4",
                "Wave743 static read-back: Camera.cpp compiler-generated SEH unwind cleanup callback. Scope-table data xref 0x0061a454 points at this body; decompile/instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP+4 with Camera.cpp debug path 0x00623c90, line 0xa9, and memtype 0x26. Static retail Ghidra metadata/decompile/xref evidence only; runtime camera allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.",
                tags("camera", "camera-cpp", "free-object")
            )
        };

        println("ApplyUnwindContinuationWave743 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave743 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
