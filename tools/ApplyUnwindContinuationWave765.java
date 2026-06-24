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

public class ApplyUnwindContinuationWave765 extends GhidraScript {
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
            "unwind-continuation-wave765",
            "wave765-readback-verified",
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
            new Spec("0x005d4948", "Wave765 static read-back: compiler-generated SEH unwind particle-list cleanup callback adjacent to the prior ResourceAccumulator/Round scope-table boundary. Scope-table DATA xref 0x0061d1b4 points at this body; instruction/decompile evidence shows CParticleManager__RemoveFromGlobalList_Thunk on the stack/local list node at (*(EBP-0x10))+0xe0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "resource-accumulator-adjacent")),
            new Spec("0x005d4956", "Wave765 static read-back: compiler-generated SEH unwind active-reader cleanup callback adjacent to the prior ResourceAccumulator/Round scope-table boundary. Scope-table DATA xref 0x0061d1bc points at this body; instruction/decompile evidence shows CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0xe8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader", "resource-accumulator-adjacent")),
            new Spec("0x005d4970", "Wave765 static read-back: Round.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d1e4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x8c) with Round.cpp debug path 0x00631d38, line token 0x62, and allocation/type value 0x0d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "free-object")),
            new Spec("0x005d4989", "Wave765 static read-back: Round.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d1ec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x8c) with Round.cpp debug path 0x00631d38, line token 0x6c, and allocation/type value 0x0b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "free-object")),
            new Spec("0x005d49a2", "Wave765 static read-back: Round.cpp-adjacent compiler-generated SEH unwind collision-round cleanup callback. Scope-table DATA xref 0x0061d1f4 points at this body; instruction/decompile evidence jumps to CCollisionSeekingRound__Destructor on *(EBP-0x8c). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "collision-seeking-round", "destructor")),
            new Spec("0x005d49ad", "Wave765 static read-back: Round.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d1fc points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "line-subobject")),
            new Spec("0x005d49c0", "Wave765 static read-back: Round.cpp-adjacent compiler-generated SEH unwind collision-round cleanup callback. Scope-table DATA xref 0x0061d224 points at this body; instruction/decompile evidence jumps to CCollisionSeekingRound__Destructor on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "collision-seeking-round", "destructor")),
            new Spec("0x005d49e0", "Wave765 static read-back: Round.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d24c points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x78. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "line-subobject")),
            new Spec("0x005d49e8", "Wave765 static read-back: Round.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d254 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x7c) with Round.cpp debug path 0x00631d38, line token 0x213, and allocation/type value 0x0b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "free-object")),
            new Spec("0x005d4a10", "Wave765 static read-back: Round.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d27c points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("round", "line-subobject")),
            new Spec("0x005d4a30", "Wave765 static read-back: render-object compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061d2a4 points at this body; instruction/decompile evidence jumps to CRenderThing__dtor on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("render-thing", "destructor")),
            new Spec("0x005d4a50", "Wave765 static read-back: meshpose.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d2cc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x214) with meshpose.h debug path 0x00631ed8, line token 0x21, and allocation/type value 0x7d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("meshpose", "free-object")),
            new Spec("0x005d4a80", "Wave765 static read-back: render-object compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061d2f4 points at this body; instruction/decompile evidence jumps to CRenderThing__dtor on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("render-thing", "destructor")),
            new Spec("0x005d4aa0", "Wave765 static read-back: render-object compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061d31c points at this body; instruction/decompile evidence jumps to CRenderThing__dtor on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("render-thing", "destructor")),
            new Spec("0x005d4ac0", "Wave765 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d344 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d4ae0", "Wave765 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d36c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor subobject at (*(EBP-0x42c))+0x04. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d4aee", "Wave765 static read-back: compiler-generated SEH unwind resource-descriptor cleanup callback. Scope-table DATA xref 0x0061d374 points at this body; instruction/decompile evidence jumps to CResourceDescriptor__dtor on the stack-local descriptor at EBP-0x428. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("resource-descriptor", "destructor")),
            new Spec("0x005d4b10", "Wave765 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d39c points at this body; instruction/decompile evidence checks (*(EBP-0x10))-0x04 for null, selects a monitor pointer, and jumps to CMonitor__Shutdown. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d4b50", "Wave765 static read-back: Sentinel.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d3c4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x04) with Sentinel.cpp debug path 0x0063221c, line token 0x20, and allocation/type value 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sentinel", "free-object")),
            new Spec("0x005d4b66", "Wave765 static read-back: Sentinel.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d3cc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x04) with Sentinel.cpp debug path 0x0063221c, line token 0x21, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sentinel", "free-object")),
            new Spec("0x005d4b7c", "Wave765 static read-back: Sentinel.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d3d4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x04) with Sentinel.cpp debug path 0x0063221c, line token 0x22, and allocation/type value 0x16. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sentinel", "free-object")),
            new Spec("0x005d4ba0", "Wave765 static read-back: Sentinel.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d3fc points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sentinel", "monitor", "shutdown")),
            new Spec("0x005d4ba8", "Wave765 static read-back: Sentinel.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d404 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sentinel", "active-reader")),
            new Spec("0x005d4bb3", "Wave765 static read-back: Sentinel.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d40c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sentinel", "active-reader")),
            new Spec("0x005d4bd0", "Wave765 static read-back: compiler-generated SEH unwind resource-descriptor array cleanup callback. Scope-table DATA xref 0x0061d434 points at this body; instruction/decompile evidence jumps to CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("resource-descriptor", "destructor"))
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
            throw new IllegalStateException("Wave764 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
