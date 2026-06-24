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

public class ApplyUnwindContinuationWave773 extends GhidraScript {
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
            "unwind-continuation-wave773",
            "wave773-readback-verified",
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

    private Spec cleanup(String address, String xref, String helper, String targetText, String... extraTags) {
        String comment = "Wave773 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref "
            + xref
            + " points at this body; instruction/decompile evidence calls or jumps to "
            + helper
            + " on "
            + targetText
            + ". Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.";
        return new Spec(address, comment, tags(extraTags));
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyUnwindContinuationWave773 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            cleanup("0x005d5b45", "0x0061e344", "CSPtrSet__Clear", "the subobject at (*(EBP-0x10))+0x100", "sptrset", "sptrset-offset-100"),
            cleanup("0x005d5b53", "0x0061e34c", "CSPtrSet__Clear", "the subobject at (*(EBP-0x10))+0x110", "sptrset", "sptrset-offset-110"),
            cleanup("0x005d5b70", "0x0061e374", "OID__FreeObject_Callback", "*(EBP-0x1c)", "oid-free"),
            cleanup("0x005d5b89", "0x0061e37c", "OID__FreeObject_Callback", "*(EBP-0x1c)", "oid-free"),
            cleanup("0x005d5bb0", "0x0061e3a4", "CLine__SetBaseVtable_00426360", "the stack/object cell at EBP+0x4", "line-vtable-reset"),
            cleanup("0x005d5bd0", "0x0061e3cc", "CDXMemBuffer__dtor_base", "the stack-local buffer at EBP-0x308", "dxmem-buffer"),
            cleanup("0x005d5bf0", "0x0061e3f4", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d5c09", "0x0061e3fc", "CMonitor__Shutdown", "*(EBP+0x4)", "monitor-shutdown"),
            cleanup("0x005d5c11", "0x0061e404", "CSPtrSet__Clear", "the subobject at (*(EBP+0x4))+0x8", "sptrset", "sptrset-offset-8"),
            cleanup("0x005d5c30", "0x0061e42c", "CMonitor__Shutdown", "*(EBP-0x10)", "monitor-shutdown"),
            cleanup("0x005d5c38", "0x0061e434", "CSPtrSet__Clear", "the subobject at (*(EBP-0x10))+0x8", "sptrset", "sptrset-offset-8"),
            cleanup("0x005d5c43", "0x0061e43c", "CSPtrSet__Clear", "the subobject at (*(EBP-0x10))+0x18", "sptrset", "sptrset-offset-18"),
            cleanup("0x005d5c60", "0x0061e464", "OID__FreeObject_Callback", "*(EBP-0x38c4)", "oid-free"),
            cleanup("0x005d5c7c", "0x0061e46c", "CMonitor__Shutdown", "*(EBP-0x38c4)", "monitor-shutdown"),
            cleanup("0x005d5c87", "0x0061e474", "CSPtrSet__Clear", "the subobject at (*(EBP-0x38c4))+0x8", "sptrset", "sptrset-offset-8"),
            cleanup("0x005d5ca0", "0x0061e49c", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d5cb9", "0x0061e4a4", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d5cd2", "0x0061e4ac", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d5d00", "0x0061e4d4", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d5d20", "0x0061e4fc", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d5d36", "0x0061e504", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d5d4c", "0x0061e50c", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d5d62", "0x0061e514", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d5d78", "0x0061e51c", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d5d8e", "0x0061e524", "CUnit__dtor_base_Thunk_004bfe00", "*(EBP+0x4)", "unit-dtor-thunk"),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave773 apply encountered missing/bad rows");
        }
    }
}
