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

public class ApplyUnwindContinuationWave756 extends GhidraScript {
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
            "unwind-continuation-wave756",
            "wave756-readback-verified",
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
            new Spec("0x005d3392", "Wave756 static read-back: MCTentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c0ac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x174) with MCTentacle.cpp debug path 0x0062e06c, line token 0x1b, and allocation/type value 0x6d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCTentacle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mctentacle", "free-object")),
            new Spec("0x005d33c0", "Wave756 static read-back: Mech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c0d4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Mech.cpp debug path 0x0062e0e0, line token 0x1b, and allocation/type value 0x3d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime Mech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mech", "free-object")),
            new Spec("0x005d33e0", "Wave756 static read-back: Mech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c0fc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Mech.cpp debug path 0x0062e0e0, line token 0x16, and allocation/type value 0x48. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime Mech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mech", "free-object")),
            new Spec("0x005d3400", "Wave756 static read-back: Mech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c124 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Mech.cpp debug path 0x0062e0e0, line token 0x17, and allocation/type value 0x4e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime Mech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mech", "free-object")),
            new Spec("0x005d3420", "Wave756 static read-back: Mech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c14c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Mech.cpp debug path 0x0062e0e0, line token 0x5c, and allocation/type value 0x57. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime Mech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mech", "free-object")),
            new Spec("0x005d3440", "Wave756 static read-back: compiler-generated SEH unwind particle-manager list cleanup callback. Scope-table DATA xref 0x0061c174 points at this body; decompile/instruction evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on the stack-local node at EBP-0x8c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "list-cleanup")),
            new Spec("0x005d3460", "Wave756 static read-back: compiler-generated SEH unwind UnitAI destructor callback. Scope-table DATA xref 0x0061c19c points at this body; decompile/instruction evidence jumps to CUnitAI__dtor_body_00415080 with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime UnitAI cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unitai", "destructor")),
            new Spec("0x005d3480", "Wave756 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c1c4 points at this body; decompile/instruction evidence jumps to CMonitor__Shutdown with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d3488", "Wave756 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c1cc points at this body; decompile/instruction evidence calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d3493", "Wave756 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c1d4 points at this body; decompile/instruction evidence calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d34b0", "Wave756 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c1fc points at this body; decompile/instruction evidence jumps to CMonitor__Shutdown_Thunk with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d34b8", "Wave756 static read-back: compiler-generated SEH unwind landscape free-object callback. Scope-table DATA xref 0x0061c204 points at this body; decompile/instruction evidence calls CDXLandscape__FreeObjectCallback on (*(EBP+0x4))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d34c3", "Wave756 static read-back: compiler-generated SEH unwind UnitAI owned-object cleanup callback. Scope-table DATA xref 0x0061c20c points at this body; decompile/instruction evidence calls CUnitAI__FreeOwnedObjects_10_18 on (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime UnitAI cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unitai", "owned-object-cleanup")),
            new Spec("0x005d34ce", "Wave756 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061c214 points at this body; decompile/instruction evidence calls CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "monitor")),
            new Spec("0x005d34f0", "Wave756 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061c23c points at this body; decompile/instruction evidence jumps to CMonitor__Shutdown_Thunk with ECX loaded from *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d34f8", "Wave756 static read-back: compiler-generated SEH unwind UnitAI owned-object cleanup callback. Scope-table DATA xref 0x0061c244 points at this body; decompile/instruction evidence calls CUnitAI__FreeOwnedObjects_10_18 on (*(EBP-0x14))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime UnitAI cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unitai", "owned-object-cleanup")),
            new Spec("0x005d3503", "Wave756 static read-back: compiler-generated SEH unwind landscape free-object callback. Scope-table DATA xref 0x0061c24c points at this body; decompile/instruction evidence calls CDXLandscape__FreeObjectCallback on (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("landscape", "free-object")),
            new Spec("0x005d3520", "Wave756 static read-back: compiler-generated SEH unwind profiling-scope cleanup callback. Scope-table DATA xref 0x0061c274 points at this body; decompile/instruction evidence jumps to CMCBuggy__ProfileEnd on the stack-local profile scope at EBP-0x34. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime profiler behavior, BEA patching, and rebuild parity remain unproven.", tags("profile", "mcbuggy")),
            new Spec("0x005d3540", "Wave756 static read-back: MemoryManager.cpp-adjacent compiler-generated SEH unwind mutex cleanup callback. Scope-table DATA xref 0x0061c29c points at this body; decompile/instruction evidence jumps to CMemoryHeap__ReleaseMutexUnwindCleanup for the mutex handle pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mutex cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("memory-manager", "mutex-cleanup")),
            new Spec("0x005d3560", "Wave756 static read-back: MemoryManager.cpp-adjacent compiler-generated SEH unwind mutex cleanup callback. Scope-table DATA xref 0x0061c2c4 points at this body; decompile/instruction evidence jumps to CMemoryHeap__ReleaseMutexUnwindCleanup for the mutex handle pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mutex cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("memory-manager", "mutex-cleanup")),
            new Spec("0x005d3580", "Wave756 static read-back: compiler-generated SEH unwind memory-buffer destructor callback. Scope-table DATA xref 0x0061c2ec points at this body; decompile/instruction evidence jumps to CDXMemBuffer__dtor_base for the large stack-local buffer at EBP-0x6844. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime memory-buffer cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("memory-manager", "mem-buffer", "destructor")),
            new Spec("0x005d35a0", "Wave756 static read-back: MemoryManager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c314 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x2210) with MemoryManager.cpp debug path 0x0062f590, line token 0x64, and allocation/type value 0x708. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime memory-manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("memory-manager", "free-object")),
            new Spec("0x005d35bc", "Wave756 static read-back: MemoryManager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c31c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x2210) with MemoryManager.cpp debug path 0x0062f590, line token 0x64, and allocation/type value 0x77a. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime memory-manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("memory-manager", "free-object")),
            new Spec("0x005d35f0", "Wave756 static read-back: MenuItem.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c344 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with MenuItem.cpp debug path 0x0062f7d8, line token 0x80, and allocation/type value 0xad. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime menu-item cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("menuitem", "free-object")),
            new Spec("0x005d360c", "Wave756 static read-back: MenuItem.cpp-adjacent compiler-generated SEH unwind compact menu-item vtable cleanup callback. Scope-table DATA xref 0x0061c34c points at this body; decompile/instruction evidence jumps to CMenuItem__RestoreCompactVTable with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime menu-item cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("menuitem", "vtable-restore"))
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
            throw new IllegalStateException("Wave756 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
