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

public class ApplyUnwindContinuationWave771 extends GhidraScript {
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
            "unwind-continuation-wave771",
            "wave771-readback-verified",
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
        println("ApplyUnwindContinuationWave771 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec("0x005d5810", "Wave771 static read-back: compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061e06c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d5818", "Wave771 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061e074 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d5823", "Wave771 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061e07c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d5840", "Wave771 static read-back: compiler-generated SEH unwind wave-sound cleanup callback. Scope-table DATA xref 0x0061e0a4 points at this body; instruction/decompile evidence calls CWaveSoundRead__BaseConstructor on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact constructor/destructor role, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("wave-sound")),
            new Spec("0x005d5880", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e0f4 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d58a0", "Wave771 static read-back: compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061e11c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x50). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d58a8", "Wave771 static read-back: compiler-generated SEH unwind vector-cleanup callback. Scope-table DATA xref 0x0061e124 points at this body; instruction/decompile evidence calls CRT__EhVectorDestructorIterator_WithUnwind on (*(EBP-0x50))+0x14 with element size 8, count 2, and CParticleManager__RemoveFromGlobalList_Thunk as the element cleanup callback. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-list", "vector-cleanup")),
            new Spec("0x005d58be", "Wave771 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061e12c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x50))+0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d58e0", "Wave771 static read-back: compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061e154 points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown_Thunk on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor")),
            new Spec("0x005d58e8", "Wave771 static read-back: compiler-generated SEH unwind vector-cleanup callback. Scope-table DATA xref 0x0061e15c points at this body; instruction/decompile evidence calls CRT__EhVectorDestructorIterator_WithUnwind on (*(EBP-0x10))+0x14 with element size 8, count 2, and CParticleManager__RemoveFromGlobalList_Thunk as the element cleanup callback. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-list", "vector-cleanup")),
            new Spec("0x005d5910", "Wave771 static read-back: compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061e184 points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on the stack-local node at EBP-0xa54. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-list")),
            new Spec("0x005d5930", "Wave771 static read-back: compiler-generated SEH unwind CLine stack-local cleanup callback. Scope-table DATA xref 0x0061e1ac points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0x14c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line-helper")),
            new Spec("0x005d593b", "Wave771 static read-back: compiler-generated SEH unwind CLine stack-local cleanup callback. Scope-table DATA xref 0x0061e1b4 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0x70. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line-helper")),
            new Spec("0x005d5943", "Wave771 static read-back: compiler-generated SEH unwind CLine stack-local cleanup callback. Scope-table DATA xref 0x0061e1bc points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0xa4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line-helper")),
            new Spec("0x005d594e", "Wave771 static read-back: compiler-generated SEH unwind CLine stack-local cleanup callback. Scope-table DATA xref 0x0061e1c4 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0xd8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line-helper")),
            new Spec("0x005d5970", "Wave771 static read-back: compiler-generated SEH unwind CLine stack-local cleanup callback. Scope-table DATA xref 0x0061e1ec points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0xc0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line-helper")),
            new Spec("0x005d5990", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e214 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d5998", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e21c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59a3", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e224 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x20. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59ae", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e22c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x30. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59b9", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e234 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59c4", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e23c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x50. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59cf", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e244 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x60. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59da", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e24c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x70. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset")),
            new Spec("0x005d59e5", "Wave771 static read-back: compiler-generated SEH unwind smart-pointer-set cleanup callback. Scope-table DATA xref 0x0061e254 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the subobject at (*(EBP-0x10))+0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("sptrset"))
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
            throw new IllegalStateException("Wave771 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
