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

public class ApplyUnwindContinuationWave763 extends GhidraScript {
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
            "unwind-continuation-wave763",
            "wave763-readback-verified",
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
            new Spec("0x005d4477", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cde4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x59c, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4493", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5a8, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d44af", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdf4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x14) with PauseMenu.cpp debug path 0x006314dc, line token 0x5aa, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d44cb", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cdfc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x14) with PauseMenu.cpp debug path 0x006314dc, line token 0x5ab, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d44e7", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce04 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5ac, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4503", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce0c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5ad, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d451f", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce14 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5ae, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d453b", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce1c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5b1, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4557", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce24 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5b3, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4573", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce2c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x5b5, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d45a0", "Wave763 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061ce54 points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "monitor", "shutdown")),
            new Spec("0x005d45a8", "Wave763 static read-back: compiler-generated SEH unwind pointer-set clear callback. Scope-table DATA xref 0x0061ce5c points at this body; instruction/decompile evidence shows CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x10))+0x14. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "pointer-set")),
            new Spec("0x005d45c0", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ce84 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x661, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d45dc", "Wave763 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061ce8c points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP+0x4). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "monitor", "shutdown")),
            new Spec("0x005d45e4", "Wave763 static read-back: compiler-generated SEH unwind menu-range variant destructor callback. Scope-table DATA xref 0x0061ce94 points at this body; instruction/decompile evidence shows CMenuItemRangeVariant__Destructor on the subobject at (*(EBP+0x4))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "menu-item-range", "destructor")),
            new Spec("0x005d45ef", "Wave763 static read-back: compiler-generated SEH unwind pointer-set clear callback. Scope-table DATA xref 0x0061ce9c points at this body; instruction/decompile evidence shows CSPtrSet__Clear on the embedded pointer set at (*(EBP+0x4))+0x3c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "pointer-set")),
            new Spec("0x005d45fa", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cea4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x8f2, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4616", "Wave763 static read-back: PauseMenu.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ceac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with PauseMenu.cpp debug path 0x006314dc, line token 0x8f2, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "free-object")),
            new Spec("0x005d4640", "Wave763 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061ced4 points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "monitor", "shutdown")),
            new Spec("0x005d4648", "Wave763 static read-back: compiler-generated SEH unwind menu-range variant destructor callback. Scope-table DATA xref 0x0061cedc points at this body; instruction/decompile evidence shows CMenuItemRangeVariant__Destructor on the subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "menu-item-range", "destructor")),
            new Spec("0x005d4653", "Wave763 static read-back: compiler-generated SEH unwind pointer-set clear callback. Scope-table DATA xref 0x0061cee4 points at this body; instruction/decompile evidence shows CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x10))+0x3c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("pause-menu", "pointer-set")),
            new Spec("0x005d4670", "Wave763 static read-back: Plane.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cf0c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Plane.cpp debug path 0x00631630, line token 0x13, and allocation/type value 0x17. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("plane", "free-object")),
            new Spec("0x005d4686", "Wave763 static read-back: Plane.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cf14 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Plane.cpp debug path 0x00631630, line token 0x14, and allocation/type value 0x16. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("plane", "free-object")),
            new Spec("0x005d469c", "Wave763 static read-back: Plane.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cf1c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with Plane.cpp debug path 0x00631630, line token 0x2a, and allocation/type value 0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("plane", "free-object")),
            new Spec("0x005d46c0", "Wave763 static read-back: compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061cf44 points at this body; instruction/decompile evidence shows CMonitor__Shutdown on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("plane", "monitor", "shutdown"))
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
            throw new IllegalStateException("Wave763 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
