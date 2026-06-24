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

public class ApplyUnwindContinuationWave759 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String comment, String[] tags) {
            this(address, "Unwind@" + address.substring(2), comment, tags);
        }

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
            "unwind-continuation-wave759",
            "wave759-readback-verified",
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
            new Spec("0x005d3bd0", "Wave759 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c844 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d3bf0", "Wave759 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c86c points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d3bf8", "Wave759 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c874 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x18. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear")),
            new Spec("0x005d3c10", "Wave759 static read-back: Mine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c89c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x68) with Mine.cpp debug path 0x006309a4, line token 0x1b, and allocation/type value 0x1f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mine", "free-object")),
            new Spec("0x005d3c30", "Wave759 static read-back: Mine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c8c4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x50) with Mine.cpp debug path 0x006309a4, line token 0x10, and allocation/type value 0x58. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mine", "free-object")),
            new Spec("0x005d3c50", "Wave759 static read-back: Missile.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c8ec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Missile.cpp debug path 0x006309c0, line token 0x61, and allocation/type value 0x0b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("missile", "free-object")),
            new Spec("0x005d3c70", "Wave759 static read-back: compiler-generated SEH unwind CLine vtable-restore callback. Scope-table DATA xref 0x0061c914 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 for the stack-local object at EBP-0x144. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line", "vtable-restore")),
            new Spec("0x005d3c7b", "Wave759 static read-back: compiler-generated SEH unwind CLine vtable-restore callback. Scope-table DATA xref 0x0061c91c points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 for the stack-local object at EBP-0x110. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line", "vtable-restore")),
            new Spec("0x005d3c90", "Wave759 static read-back: compiler-generated SEH unwind CLine vtable-restore callback. Scope-table DATA xref 0x0061c944 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 for the stack-local object at EBP-0x144. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line", "vtable-restore")),
            new Spec("0x005d3c9b", "Wave759 static read-back: compiler-generated SEH unwind CLine vtable-restore callback. Scope-table DATA xref 0x0061c94c points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 for the stack-local object at EBP-0x110. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line", "vtable-restore")),
            new Spec("0x005d3cb0", "Wave759 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c974 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3cc6", "Wave759 static read-back: compiler-generated SEH unwind unit destructor-base callback. Scope-table DATA xref 0x0061c97c points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CUnit__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime unit cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "destructor")),
            new Spec("0x005d3cce", "Wave759 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c984 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on object field (*(EBP+0x4))+0x250. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "sptrset", "clear")),
            new Spec("0x005d3cdc", "Wave759 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c98c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x264. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d3cea", "Wave759 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c994 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on object field (*(EBP+0x4))+0x284. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "sptrset", "clear")),
            new Spec("0x005d3cf8", "Wave759 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c99c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on object field (*(EBP+0x4))+0x294. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "sptrset", "clear")),
            new Spec("0x005d3d06", "Wave759 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c9a4 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on object field (*(EBP+0x4))+0x2a4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "sptrset", "clear")),
            new Spec("0x005d3d14", "Wave759 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c9ac points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x4c8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d3d22", "Wave759 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c9b4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x4cc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d3d30", "Wave759 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c9bc points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x4e0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d3d3e", "Wave759 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c9c4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x574. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d3d4c", "Wave759 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c9cc points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x5e8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d3d5a", "Wave759 static read-back: compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061c9d4 points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on object field (*(EBP+0x4))+0x5f8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle/list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "particle-list")),
            new Spec("0x005d3d68", "Wave759 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c9dc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x07, and allocation/type value 0x2b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3d7e", "Wave759 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c9e4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x2d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object"))
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
            throw new IllegalStateException("Wave759 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
