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

public class ApplyUnwindContinuationWave758 extends GhidraScript {
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
            "unwind-continuation-wave758",
            "wave758-readback-verified",
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
            new Spec("0x005d38bc", "Wave758 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c55c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x34c) with mesh.cpp debug path 0x0062f8e8, line token 0x80, and allocation/type value 0x9cc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d38db", "Wave758 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c564 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x350) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0x9fc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d38f7", "Wave758 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c56c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x34c) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0xa05. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3913", "Wave758 static read-back: mesh.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c574 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x34c) with mesh.cpp debug path 0x0062f8e8, line token 0x01, and allocation/type value 0xa58. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh", "free-object")),
            new Spec("0x005d3940", "Wave758 static read-back: compiler-generated SEH unwind CLine vtable-restore callback. Scope-table DATA xref 0x0061c59c points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 for the stack-local object at EBP-0x28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line", "vtable-restore")),
            new Spec("0x005d3960", "Wave758 static read-back: compiler-generated SEH unwind CLine vtable-restore callback. Scope-table DATA xref 0x0061c5c4 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CLine__SetBaseVtable_00426360. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line", "vtable-restore")),
            new Spec("0x005d3980", "CMeshCollisionVolume__SetPartBounds_Unwind", "Wave758 static read-back: MeshCollisionVolume.cpp compiler-generated SEH unwind allocation-cleanup callback for the existing CMeshCollisionVolume__SetPartBounds_Unwind row. Scope-table DATA xref 0x0061c5ec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with MeshCollisionVolume.cpp debug path 0x0062fe40 and raw pushed immediate tokens 0x229 and 0x6c. The existing name is preserved; no rename was performed. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact allocator callback argument semantics for those two immediates, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mesh-collision-volume", "free-object")),
            new Spec("0x005d39b0", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c614 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with MeshPart.cpp debug path 0x0062fe70, line token 0x46, and allocation/type value 0xe9. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d39e0", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c63c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with MeshPart.cpp debug path 0x0062fe70, line token 0x01, and allocation/type value 0x15f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d3a10", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c664 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x154) with MeshPart.cpp debug path 0x0062fe70, line token 0x74, and allocation/type value 0x717. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d3a40", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c68c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x8) with MeshPart.cpp debug path 0x0062fe70, line token 0x01, and allocation/type value 0xa2a. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d3a59", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c694 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x8) with MeshPart.cpp debug path 0x0062fe70, line token 0x74, and allocation/type value 0xab6. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d3a80", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c6bc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with MeshPart.cpp debug path 0x0062fe70, line token 0x01, and allocation/type value 0xc28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d3a99", "Wave758 static read-back: MeshPart.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c6c4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with MeshPart.cpp debug path 0x0062fe70, line token 0x01, and allocation/type value 0xc58. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpart", "free-object")),
            new Spec("0x005d3ac0", "Wave758 static read-back: MeshRenderer.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c6ec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x14) with MeshRenderer.cpp debug path 0x00630178, line token 0x10, and allocation/type value 0x207. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshrenderer", "free-object")),
            new Spec("0x005d3af0", "Wave758 static read-back: compiler-generated SEH unwind waiting-thread helper callback. Scope-table DATA xref 0x0061c714 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10), subtracts 0x20, and jumps to CWaitingThread__ctor_like_00528bf0. Static retail Ghidra metadata/decompile/xref evidence only; exact helper semantics, parent source-body identity, runtime waiting-thread cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("waiting-thread")),
            new Spec("0x005d3b10", "Wave758 static read-back: compiler-generated SEH unwind waiting-thread helper callback. Scope-table DATA xref 0x0061c73c points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CWaitingThread__ctor_like_00528bf0. Static retail Ghidra metadata/decompile/xref evidence only; exact helper semantics, parent source-body identity, runtime waiting-thread cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("waiting-thread")),
            new Spec("0x005d3b30", "Wave758 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c764 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x14) and jumps to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d3b38", "Wave758 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c76c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x14))+0x30. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d3b50", "Wave758 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c794 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CMonitor__Shutdown_Thunk. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d3b70", "Wave758 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c7bc points at this body; instruction/decompile evidence loads ECX from *(EBP-0x18) and jumps to CMonitor__Shutdown. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d3b78", "Wave758 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c7c4 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x18))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear")),
            new Spec("0x005d3b90", "Wave758 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c7ec points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CMonitor__Shutdown. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d3b98", "Wave758 static read-back: compiler-generated SEH unwind smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c7f4 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear")),
            new Spec("0x005d3bb0", "Wave758 static read-back: compiler-generated SEH unwind stack-local smart-pointer set cleanup callback. Scope-table DATA xref 0x0061c81c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the stack-local set at EBP-0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset", "clear"))
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
            throw new IllegalStateException("Wave758 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
