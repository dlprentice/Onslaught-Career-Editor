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

public class ApplyUnwindContinuationWave766 extends GhidraScript {
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
            "unwind-continuation-wave766",
            "wave766-readback-verified",
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
            new Spec("0x005d4bf0", "Wave766 static read-back: SoundManager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d45c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with SoundManager.cpp debug path 0x00632428, line token 0x5a, and allocation/type value 0x4a. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("soundmanager", "free-object")),
            new Spec("0x005d4c10", "Wave766 static read-back: SoundManager.cpp-adjacent compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d484 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x98) in the same scope-table neighborhood as the SoundManager.cpp debug-path cleanup row. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("soundmanager", "free-object")),
            new Spec("0x005d4c30", "Wave766 static read-back: SoundManager.cpp-adjacent compiler-generated SEH unwind CDXMemBuffer stack cleanup callback. Scope-table DATA xref 0x0061d4ac points at this body; instruction/decompile evidence jumps to CDXMemBuffer__dtor_base on the stack-local buffer at EBP-0x140. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("soundmanager", "dx-mem-buffer")),
            new Spec("0x005d4c50", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d4d4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "active-reader")),
            new Spec("0x005d4c70", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d4fc points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "monitor", "shutdown")),
            new Spec("0x005d4c78", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d504 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "active-reader")),
            new Spec("0x005d4c90", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d52c points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "monitor", "shutdown")),
            new Spec("0x005d4c98", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d534 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x10))+0x08. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "active-reader")),
            new Spec("0x005d4cb0", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061d55c points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on the stack-local node at EBP-0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "particle-manager")),
            new Spec("0x005d4cd0", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind line-subobject cleanup callback. Scope-table DATA xref 0x0061d584 points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local line object at EBP-0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "line-subobject")),
            new Spec("0x005d4cf0", "Wave766 static read-back: SphereTrigger.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d5ac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x8) with SphereTrigger.cpp debug path 0x0063270c, line token 0x53, and allocation/type value 0x5b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "free-object")),
            new Spec("0x005d4d06", "Wave766 static read-back: SphereTrigger.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d5b4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader pointer at *(EBP+0x8). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("spheretrigger", "active-reader")),
            new Spec("0x005d4d0e", "Wave766 static read-back: monitor.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d5bc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with monitor.h debug path 0x0062551c, line token 0x18, and allocation/type value 0x5e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "free-object")),
            new Spec("0x005d4d30", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind complex-thing cleanup callback. Scope-table DATA xref 0x0061d5e4 points at this body; instruction/decompile evidence jumps to CComplexThing__dtor_base_Thunk_004bff30 on *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "complex-thing", "destructor")),
            new Spec("0x005d4d38", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061d5ec points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the member set at (*(EBP-0x14))+0xa4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "sptrset")),
            new Spec("0x005d4d46", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d5f4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x14))+0xc4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "active-reader")),
            new Spec("0x005d4d54", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d5fc points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x14))+0xc8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "active-reader")),
            new Spec("0x005d4d62", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind landscape object-vector cleanup callback. Scope-table DATA xref 0x0061d604 points at this body; instruction/decompile evidence jumps to CDXLandscape__FreeObjectCallback on the object record at (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "dx-landscape")),
            new Spec("0x005d4d80", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind complex-thing cleanup callback. Scope-table DATA xref 0x0061d62c points at this body; instruction/decompile evidence jumps to CComplexThing__dtor_base_Thunk_004bff30 on *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "complex-thing", "destructor")),
            new Spec("0x005d4d88", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061d634 points at this body; instruction/decompile evidence jumps to CSPtrSet__Clear on the member set at (*(EBP-0x14))+0xa4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "sptrset")),
            new Spec("0x005d4d96", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d63c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x14))+0xc4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "active-reader")),
            new Spec("0x005d4da4", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d644 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the embedded active-reader subobject at (*(EBP-0x14))+0xc8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "active-reader")),
            new Spec("0x005d4db2", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind landscape object-vector cleanup callback. Scope-table DATA xref 0x0061d64c points at this body; instruction/decompile evidence jumps to CDXLandscape__FreeObjectCallback on the object record at (*(EBP-0x10))+0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "dx-landscape")),
            new Spec("0x005d4dd0", "Wave766 static read-back: SquadNormal.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d674 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with SquadNormal.cpp debug path 0x0063283c, line token 0x81, and allocation/type value 0x0a. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "free-object")),
            new Spec("0x005d4de9", "Wave766 static read-back: SquadNormal.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d67c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader pointer at *(EBP+0xc). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("squadnormal", "active-reader"))
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
            throw new IllegalStateException("Wave766 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
