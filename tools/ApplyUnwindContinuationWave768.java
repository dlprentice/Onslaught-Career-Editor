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

public class ApplyUnwindContinuationWave768 extends GhidraScript {
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
            "unwind-continuation-wave768",
            "wave768-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "compiler-unwind",
            "scope-table"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
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
            Thread.sleep(50L);
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyUnwindContinuationWave768 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec("0x005d5050", "Wave768 static read-back: Tentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d8cc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Tentacle.cpp debug path 0x00632ccc, line token 0x2f, and allocation/type value 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "free-object")),
            new Spec("0x005d5070", "Wave768 static read-back: Tentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d8f4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Tentacle.cpp debug path 0x00632ccc, line token 0x35, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "free-object")),
            new Spec("0x005d5090", "Wave768 static read-back: Tentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d91c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Tentacle.cpp debug path 0x00632ccc, line token 0x3c, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "free-object")),
            new Spec("0x005d50b0", "Wave768 static read-back: Tentacle.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d944 points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "monitor", "shutdown")),
            new Spec("0x005d50b8", "Wave768 static read-back: Tentacle.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d94c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "active-reader")),
            new Spec("0x005d50c3", "Wave768 static read-back: Tentacle.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d954 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "active-reader")),
            new Spec("0x005d50e0", "Wave768 static read-back: Tentacle.cpp-adjacent compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061d97c points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on the stack-local node at EBP-0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tentacle", "particle-manager")),
            new Spec("0x005d5100", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind CDXMemBuffer cleanup callback. Scope-table DATA xref 0x0061d9a4 points at this body; instruction/decompile evidence jumps to CDXMemBuffer__dtor_base on the stack-local buffer at EBP-0x240. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "mem-buffer")),
            new Spec("0x005d5150", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind CDXMemBuffer cleanup callback. Scope-table DATA xref 0x0061d9f4 points at this body; instruction/decompile evidence jumps to CDXMemBuffer__dtor_base on the stack-local buffer at EBP-0x140. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "mem-buffer")),
            new Spec("0x005d5170", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061da1c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "monitor", "shutdown")),
            new Spec("0x005d5190", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061da44 points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "monitor", "shutdown")),
            new Spec("0x005d5198", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind mapwho-entry cleanup callback. Scope-table DATA xref 0x0061da4c points at this body; instruction/decompile evidence jumps to CMapWhoEntry__RemoveFromMap on the entry subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "mapwho-entry")),
            new Spec("0x005d51b0", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind collision-seeking cleanup callback. Scope-table DATA xref 0x0061da74 points at this body; instruction/decompile evidence jumps to CCollisionSeekingRound__Destructor on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "collision-seeking-round")),
            new Spec("0x005d51d0", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061da9c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "monitor", "shutdown")),
            new Spec("0x005d51f0", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind CThing destructor cleanup callback. Scope-table DATA xref 0x0061dac4 points at this body; instruction/decompile evidence jumps to CThing__dtor_base on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "thing", "destructor")),
            new Spec("0x005d51f8", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061dacc points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "monitor", "shutdown")),
            new Spec("0x005d5200", "Wave768 static read-back: texture.cpp-adjacent compiler-generated SEH unwind mapwho-entry cleanup callback. Scope-table DATA xref 0x0061dad4 points at this body; instruction/decompile evidence jumps to CMapWhoEntry__RemoveFromMap on the entry subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "mapwho-entry")),
            new Spec("0x005d5220", "Wave768 static read-back: thing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061dafc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with thing.cpp debug path 0x006331c0, line token 0x299, and allocation/type value 0x18. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thing", "free-object")),
            new Spec("0x005d5250", "Wave768 static read-back: thing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061db24 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with thing.cpp debug path 0x006331c0, line token 0x2ff, and allocation/type value 0x05. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thing", "free-object")),
            new Spec("0x005d5280", "Wave768 static read-back: ThunderHead.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061db4c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with ThunderHead.cpp debug path 0x00633240, line token 0x20, and allocation/type value 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thunderhead", "free-object")),
            new Spec("0x005d52a0", "Wave768 static read-back: ThunderHead.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061db74 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with ThunderHead.cpp debug path 0x00633240, line token 0x2b, and allocation/type value 0x16. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thunderhead", "free-object")),
            new Spec("0x005d52c0", "Wave768 static read-back: ThunderHead.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061db9c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with ThunderHead.cpp debug path 0x00633240, line token 0x31, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thunderhead", "free-object")),
            new Spec("0x005d52e0", "Wave768 static read-back: ThunderHead.cpp-adjacent compiler-generated SEH unwind landscape resource-descriptor cleanup callback. Scope-table DATA xref 0x0061dbc4 points at this body; instruction/decompile evidence jumps to CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x534. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thunderhead", "landscape-resource")),
            new Spec("0x005d5300", "Wave768 static read-back: ThunderHead.cpp-adjacent compiler-generated SEH unwind CThing destructor cleanup callback. Scope-table DATA xref 0x0061dbec points at this body; instruction/decompile evidence jumps to CThing__dtor_base on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thunderhead", "thing", "destructor")),
            new Spec("0x005d5320", "Wave768 static read-back: tree.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061dc14 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with tree.cpp debug path 0x00633a84, line token 0x8f, and allocation/type value 0x5c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tree", "free-object"))
        };

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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave768 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
