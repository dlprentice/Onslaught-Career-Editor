//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyUnwindContinuationWave757 extends GhidraScript {
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
            "unwind-continuation-wave757",
            "wave757-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "compiler-unwind",
            "scope-table"
        };
        String[] out = new String[common.length + extras.length];
        System.arraycopy(common, 0, out, 0, common.length);
        System.arraycopy(extras, 0, out, common.length, extras.length);
        return out;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String expectedSignature(Spec spec) {
        return "void __cdecl " + spec.name + "(void)";
    }

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!signature.equals(expectedSignature(spec))) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + signature);
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
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

            String signature = fn.getSignature().toString();
            boolean signatureNeedsUpdate = !signature.equals(expectedSignature(spec));
            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            Set<String> actualTags = tagNames(fn);
            boolean tagsNeedUpdate = false;
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    tagsNeedUpdate = true;
                    break;
                }
            }

            if (!signatureNeedsUpdate && !commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " signature=" + signature + " -> " + expectedSignature(spec));
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
            new Spec("0x005d3614", "Wave757 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c354 points at this body; decompile/instruction evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x34. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d3630", "Wave757 static read-back: compiler-generated SEH unwind compact menu-item vtable cleanup callback. Scope-table DATA xref 0x0061c37c points at this body; decompile/instruction evidence jumps to CMenuItem__RestoreCompactVTable with ECX loaded from *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime menu-item cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("menuitem", "vtable-restore")),
            new Spec("0x005d3638", "Wave757 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c384 points at this body; decompile/instruction evidence jumps to CGenericActiveReader__dtor with ECX loaded from *(EBP+0x18). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d3640", "Wave757 static read-back: Monitor.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c38c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x8) with Monitor.h debug path 0x00622b80, line token 0x5e, and allocation/type value 0x18. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "free-object")),
            new Spec("0x005d3660", "Wave757 static read-back: compiler-generated SEH unwind compact menu-item vtable cleanup callback. Scope-table DATA xref 0x0061c3b4 points at this body; decompile/instruction evidence jumps to CMenuItem__RestoreCompactVTable with ECX loaded from *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime menu-item cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("menuitem", "vtable-restore")),
            new Spec("0x005d3668", "Wave757 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c3bc points at this body; decompile/instruction evidence jumps to CGenericActiveReader__dtor with ECX loaded from *(EBP+0x18). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d3670", "Wave757 static read-back: Monitor.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c3c4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x8) with Monitor.h debug path 0x00622b80, line token 0x5e, and allocation/type value 0x18. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "free-object")),
            new Spec("0x005d3690", "Wave757 static read-back: compiler-generated SEH unwind compact menu-item vtable cleanup callback. Scope-table DATA xref 0x0061c3ec points at this body; decompile/instruction evidence jumps to CMenuItem__RestoreCompactVTable with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime menu-item cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("menuitem", "vtable-restore")),
            new Spec("0x005d3698", "Wave757 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c3f4 points at this body; decompile/instruction evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x34. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d36b0", "Wave757 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c41c points at this body; decompile/instruction evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear")),
            new Spec("0x005d36d0", "Wave757 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c444 points at this body; decompile/instruction evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear")),
            new Spec("0x005d36f0", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c46c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with mesh.cpp debug path 0x0062f8e8, line token 0x24, and allocation/type value 0x91. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3720", "Wave757 static read-back: compiler-generated SEH unwind memory-buffer destructor callback. Scope-table DATA xref 0x0061c494 points at this body; decompile/instruction evidence jumps to CDXMemBuffer__dtor_base for the stack-local buffer at EBP-0x340. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime memory-buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "mem-buffer", "destructor")),
            new Spec("0x005d3740", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4dc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x82c) with mesh.cpp debug path 0x0062f8e8, line token 0x24, and allocation/type value 0x349. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d375c", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4e4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x82c) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x3a2. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3778", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4f4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x81c) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x4ad. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3794", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4ec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x79c) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x3ec. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d37b0", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4fc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x794) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x584. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d37cc", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c504 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x794) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x5fe. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d37e8", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4bc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x794) with mesh.cpp debug path 0x0062f8e8, line token 0x24, and allocation/type value 0x235. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3804", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4c4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x794) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x251. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3820", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4cc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x810) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x28d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d383c", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c4d4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x794) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x2d5. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3870", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c52c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x755. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d38a0", "Wave757 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c554 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x34c) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x982. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mesh cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object"))
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
            throw new IllegalStateException("Wave757 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
