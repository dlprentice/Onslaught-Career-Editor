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

public class ApplyUnwindContinuationWave762 extends GhidraScript {
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
            "unwind-continuation-wave762",
            "wave762-readback-verified",
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
            new Spec("0x005d41e4", "Wave762 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ccdc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x69. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d41fa", "Wave762 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cce4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x6a. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d4210", "Wave762 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ccec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x6b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d4230", "Wave762 static read-back: compiler-generated SEH unwind stack memory-buffer destructor callback. Scope-table DATA xref 0x0061cd14 points at this body; instruction/decompile evidence shows CDXMemBuffer__dtor_base on the stack-local buffer at EBP-0x140. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mem-buffer", "destructor")),
            new Spec("0x005d4250", "Wave762 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061cd3c points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x18). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown")),
            new Spec("0x005d4258", "Wave762 static read-back: compiler-generated SEH unwind pointer-set clear callback. Scope-table DATA xref 0x0061cd44 points at this body; instruction/decompile evidence shows CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x18))+0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pointer-set")),
            new Spec("0x005d4263", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd4c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x14) with PauseMenu.cpp debug path 0x006314dc, line token 0x539, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d427f", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd54 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x558, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d429b", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd5c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x55d, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d42b7", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd64 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x562, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d42d3", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd6c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x570, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d42ef", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd74 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x57d, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d430b", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd7c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x580, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4327", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd84 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x583, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4343", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd8c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x587, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d435f", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd94 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x588, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d437b", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cd9c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x589, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4397", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cda4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x58a, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d43b3", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x58d, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d43cf", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdb4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x593, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d43eb", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdbc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x596, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4407", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdc4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x597, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4423", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdcc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x598, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d443f", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdd4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x599, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d445b", "Wave762 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cddc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x59a, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object"))
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
            throw new IllegalStateException("Wave762 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
