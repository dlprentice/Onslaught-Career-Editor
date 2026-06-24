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

public class ApplyUnwindContinuationWave770 extends GhidraScript {
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
            "unwind-continuation-wave770",
            "wave770-readback-verified",
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
        println("ApplyUnwindContinuationWave770 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec("0x005d5532", "Wave770 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ddc4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Unit.cpp debug path 0x00633b6c, line token 0x15b, and allocation/type value 0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object")),
            new Spec("0x005d554b", "Wave770 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ddcc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Unit.cpp debug path 0x00633b6c, line token 0x164, and allocation/type value 0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object")),
            new Spec("0x005d5564", "Wave770 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ddd4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Unit.cpp debug path 0x00633b6c, line token 0x16f, and allocation/type value 0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object")),
            new Spec("0x005d5590", "Wave770 static read-back: Unit.cpp-adjacent compiler-generated SEH unwind stack-local CLine cleanup callback. Scope-table DATA xref 0x0061ddfc points at this body; instruction/decompile evidence jumps to CLine__SetBaseVtable_00426360 on the stack-local object at EBP-0x70. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, exact helper subtype, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "line-helper")),
            new Spec("0x005d5598", "Wave770 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061de04 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x98) with Unit.cpp debug path 0x00633b6c, line token 0x44d, and allocation/type value 0x06. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object")),
            new Spec("0x005d55c0", "Wave770 static read-back: Unit.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061de2c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Unit.cpp debug path 0x00633b6c, line token 0xc1b, and allocation/type value 0x06. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "free-object")),
            new Spec("0x005d55f0", "Wave770 static read-back: Unit.cpp-adjacent compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061de54 points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor object at *(EBP-0x74). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "monitor")),
            new Spec("0x005d55f8", "Wave770 static read-back: Unit.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061de5c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x74))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d5603", "Wave770 static read-back: Unit.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061de64 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x74))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d560e", "Wave770 static read-back: Unit.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061de6c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x74))+0x28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("unit", "active-reader")),
            new Spec("0x005d5630", "Wave770 static read-back: Unit/vbuftexture-adjacent compiler-generated SEH unwind device-object helper callback. Scope-table DATA xref 0x0061de94 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Exact helper semantics remain unproven. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("device-object", "helper-semantics-unproven")),
            new Spec("0x005d5650", "Wave770 static read-back: Unit/vbuftexture-adjacent compiler-generated SEH unwind device-object helper callback. Scope-table DATA xref 0x0061debc points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Exact helper semantics remain unproven. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("device-object", "helper-semantics-unproven")),
            new Spec("0x005d5670", "Wave770 static read-back: vbuftexture.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061dee4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with vbuftexture.cpp debug path 0x00633d5c, line token 0xb6, and allocation/type value 0x2c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("vbuftexture", "free-object")),
            new Spec("0x005d56a0", "Wave770 static read-back: vbuftexture.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061df0c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with vbuftexture.cpp debug path 0x00633d5c, line token 0xfb, and allocation/type value 0x2f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("vbuftexture", "free-object")),
            new Spec("0x005d56d0", "Wave770 static read-back: vbuftexture/VertexShader-adjacent compiler-generated SEH unwind device-object helper callback. Scope-table DATA xref 0x0061df34 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Exact helper semantics remain unproven. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("device-object", "helper-semantics-unproven")),
            new Spec("0x005d56f0", "Wave770 static read-back: vbuftexture/VertexShader-adjacent compiler-generated SEH unwind device-object helper callback. Scope-table DATA xref 0x0061df5c points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to DeviceObject__ctor_like_00512d50. Exact helper semantics remain unproven. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("device-object", "helper-semantics-unproven")),
            new Spec("0x005d5710", "Wave770 static read-back: VertexShader.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061df84 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x14) with VertexShader.cpp debug path 0x0063cf78, line token 0x2bd, and allocation/type value 0x50. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("vertex-shader", "free-object")),
            new Spec("0x005d5740", "Wave770 static read-back: VertexShader.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061dfac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0xd8) with VertexShader.cpp debug path 0x0063cf78, line token 0x99a, and allocation/type value 0x50. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("vertex-shader", "free-object")),
            new Spec("0x005d5770", "Wave770 static read-back: Warspite.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061dfd4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Warspite.cpp debug path 0x0063d12c, line token 0x0a, and allocation/type value 0x16. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite", "free-object")),
            new Spec("0x005d5790", "Wave770 static read-back: Warspite.cpp-adjacent compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061dffc points at this body; instruction/decompile evidence jumps to CMonitor__Shutdown on the monitor object at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite", "monitor")),
            new Spec("0x005d5798", "Wave770 static read-back: Warspite.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061e004 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite", "active-reader")),
            new Spec("0x005d57a3", "Wave770 static read-back: Warspite.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061e00c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite", "active-reader")),
            new Spec("0x005d57c0", "Wave770 static read-back: WarspiteDome.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061e034 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with WarspiteDome.cpp debug path 0x0063d170, line token 0x19, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite-dome", "free-object")),
            new Spec("0x005d57d6", "Wave770 static read-back: WarspiteDome.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061e03c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with WarspiteDome.cpp debug path 0x0063d170, line token 0x1a, and allocation/type value 0x16. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite-dome", "free-object")),
            new Spec("0x005d57ec", "Wave770 static read-back: WarspiteDome.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061e044 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with WarspiteDome.cpp debug path 0x0063d170, line token 0x1d, and allocation/type value 0x1b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("warspite-dome", "free-object"))
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
            throw new IllegalStateException("Wave770 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
