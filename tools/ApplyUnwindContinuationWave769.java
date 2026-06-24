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

public class ApplyUnwindContinuationWave769 extends GhidraScript {
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
            "unwind-continuation-wave769",
            "wave769-readback-verified",
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
        println("ApplyUnwindContinuationWave769 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec("0x005d5350", "Wave769 static read-back: tree.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061dc3c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x40) with tree.cpp debug path 0x00633a84, line token 0xf0, and allocation/type value 0x07. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tree", "free-object")),
            new Spec("0x005d5380", "Wave769 static read-back: tree.cpp-adjacent compiler-generated SEH unwind stack-local CLine cleanup callback. Scope-table DATA xref 0x0061dc64 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0x50. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tree", "line-helper")),
            new Spec("0x005d5388", "Wave769 static read-back: tree.cpp-adjacent compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061dc6c points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on the stack-local node at EBP-0x90. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle behavior, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tree", "particle-manager")),
            new Spec("0x005d53a0", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind device-object helper callback. Scope-table DATA xref 0x0061dc94 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Exact helper semantics remain unproven. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("device-object", "helper-semantics-unproven")),
            new Spec("0x005d53c0", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind device-object helper callback. Scope-table DATA xref 0x0061dcbc points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Exact helper semantics remain unproven. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("device-object", "helper-semantics-unproven")),
            new Spec("0x005d53e0", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind actor destructor-base cleanup callback. Scope-table DATA xref 0x0061dce4 points at this body; instruction/decompile evidence jumps to CActor__dtor_base on the object pointer at *(EBP-0x50). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d53e8", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061dcec points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x50))+0x144. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d53f6", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061dcf4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x50))+0x148. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d5404", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dcfc points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x50))+0x17c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d5412", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd04 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x50))+0x18c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d5420", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd0c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x50))+0x19c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d542e", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd14 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x50))+0x1b4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d543c", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd1c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x50))+0x1c4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d544a", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd24 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x50))+0x1d4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d5470", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind actor destructor-base cleanup callback. Scope-table DATA xref 0x0061dd4c points at this body; instruction/decompile evidence jumps to CActor__dtor_base on the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d5478", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061dd54 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x144. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d5486", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061dd5c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x148. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d5494", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd64 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x17c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d54a2", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd6c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x18c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d54b0", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd74 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x19c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d54be", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd7c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x1b4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d54cc", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd84 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x1c4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d54da", "Wave769 static read-back: tree/Unit-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061dd8c points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the embedded set at (*(EBP-0x10))+0x1d4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d5500", "Wave769 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ddb4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x70) with Unit.cpp debug path 0x00633b6c, line token 0xc0, and allocation/type value 0x61. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object")),
            new Spec("0x005d5519", "Wave769 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ddbc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x6c) with Unit.cpp debug path 0x00633b6c, line token 0x139, and allocation/type value 0x61. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object"))
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
            throw new IllegalStateException("Wave769 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
