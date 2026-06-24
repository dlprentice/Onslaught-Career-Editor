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

public class ApplyUnwindContinuationWave767 extends GhidraScript {
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
            "unwind-continuation-wave767",
            "wave767-readback-verified",
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
            new Spec("0x005d4e00", "Wave767 static read-back: SquadNormal.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d6a4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with SquadNormal.cpp debug path 0x0063283c, line token 0x437, and allocation/type value 0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "free-object")),
            new Spec("0x005d4e30", "Wave767 static read-back: SquadNormal.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d6cc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x4e4) with SquadNormal.cpp debug path 0x0063283c, line token 0x48b, and allocation/type value 0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "free-object")),
            new Spec("0x005d4e60", "Wave767 static read-back: SquadRelaxed.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d6f4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with SquadRelaxed.cpp debug path 0x00632918, line token 0xa0, and allocation/type value 0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadrelaxed", "free-object")),
            new Spec("0x005d4e90", "Wave767 static read-back: SquadRelaxed.cpp-adjacent compiler-generated SEH unwind complex-thing cleanup callback. Scope-table DATA xref 0x0061d71c points at this body; instruction/decompile evidence jumps to CComplexThing__dtor_base on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadrelaxed", "complex-thing", "destructor")),
            new Spec("0x005d4e98", "Wave767 static read-back: SquadRelaxed.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d724 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadrelaxed", "active-reader")),
            new Spec("0x005d4eb0", "Wave767 static read-back: SquadRelaxed.cpp-adjacent compiler-generated SEH unwind complex-thing cleanup callback. Scope-table DATA xref 0x0061d74c points at this body; instruction/decompile evidence jumps to CComplexThing__dtor_base on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadrelaxed", "complex-thing", "destructor")),
            new Spec("0x005d4eb8", "Wave767 static read-back: SquadRelaxed.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d754 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadrelaxed", "active-reader")),
            new Spec("0x005d4ed0", "Wave767 static read-back: SquadRelaxed.cpp-adjacent compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061d77c points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on the stack-local node at EBP-0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadrelaxed", "particle-manager")),
            new Spec("0x005d4ef0", "Wave767 static read-back: StaticShadows.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d7a4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x614) with StaticShadows.cpp debug path 0x006329f8, line token 0x18a, and allocation/type value 0x70. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "free-object")),
            new Spec("0x005d4f0c", "Wave767 static read-back: StaticShadows.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d7ac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x684) with StaticShadows.cpp debug path 0x006329f8, line token 0x1a7, and allocation/type value 0x61. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "free-object")),
            new Spec("0x005d4f28", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7b4 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x31c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f33", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7bc points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x24c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f3e", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7c4 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x2b4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f49", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7cc points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x2e8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f54", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7d4 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x280. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f5f", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7dc points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x218. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f6a", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7e4 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x1b0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f75", "Wave767 static read-back: StaticShadows.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d7ec points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x1e4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "line-subobject")),
            new Spec("0x005d4f90", "Wave767 static read-back: StaticShadows.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d814 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with StaticShadows.cpp debug path 0x006329f8, line token 0x43d, and allocation/type value 0x70. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("staticshadows", "free-object")),
            new Spec("0x005d4fc0", "Wave767 static read-back: Submarine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d83c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Submarine.cpp debug path 0x00632abc, line token 0x1d, and allocation/type value 0x16. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("submarine", "free-object")),
            new Spec("0x005d4fd6", "Wave767 static read-back: Submarine.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d844 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Submarine.cpp debug path 0x00632abc, line token 0x1e, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("submarine", "free-object")),
            new Spec("0x005d5000", "Wave767 static read-back: Submarine.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d86c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("submarine", "monitor", "shutdown")),
            new Spec("0x005d5008", "Wave767 static read-back: Submarine.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d874 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("submarine", "active-reader")),
            new Spec("0x005d5013", "Wave767 static read-back: Submarine.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d87c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("submarine", "active-reader")),
            new Spec("0x005d5030", "Wave767 static read-back: Submarine.cpp-adjacent compiler-generated SEH unwind controller cleanup callback. Scope-table DATA xref 0x0061d8a4 points at this body; instruction/decompile evidence jumps to CController__dtor_Thunk on the stack-local controller at EBP-0x184. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("submarine", "controller", "destructor"))
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
            throw new IllegalStateException("Wave767 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
