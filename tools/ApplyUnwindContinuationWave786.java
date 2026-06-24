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

public class ApplyUnwindContinuationWave786 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

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
            "unwind-continuation-wave786",
            "wave786-readback-verified",
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
        String name = "Unwind@" + address.substring(2);
        String comment = "Wave786 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref "
            + xref
            + " points at this body; instruction/decompile evidence calls "
            + helper
            + " on "
            + targetText
            + ". Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.";
        return new Spec(address, name, comment, tags(extraTags));
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyUnwindContinuationWave786 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            cleanup("0x005d7a96", "0x0061fdf4", "DebugTrace", "(*(EBP-0x10))+0xae0 via ECX before jumping to the retail stub", "debugtrace-stub"),
            cleanup("0x005d7aa4", "0x0061fdfc", "DebugTrace", "(*(EBP-0x10))+0x13ac via ECX before jumping to the retail stub", "debugtrace-stub"),
            cleanup("0x005d7ac0", "0x0061fe24", "CMemoryManager__DeleteTagList", "*(EBP-0x10)", "memory-tag-list-delete"),
            cleanup("0x005d7ac8", "0x0061fe2c", "DebugTrace", "(*(EBP-0x10))+0x214 via ECX before jumping to the retail stub", "debugtrace-stub"),
            cleanup("0x005d7ad6", "0x0061fe34", "DebugTrace", "(*(EBP-0x10))+0xae0 via ECX before jumping to the retail stub", "debugtrace-stub"),
            cleanup("0x005d7ae4", "0x0061fe3c", "DebugTrace", "(*(EBP-0x10))+0x13ac via ECX before jumping to the retail stub", "debugtrace-stub"),
            cleanup("0x005d7b00", "0x0061fe64", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7b20", "0x0061fe8c", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7b40", "0x0061feb4", "CDXMemBuffer__dtor_base", "EBP-0x140", "dx-mem-buffer-dtor"),
            cleanup("0x005d7b4b", "0x0061febc", "CChunkReader__dtor_base", "EBP-0x150", "chunk-reader-dtor"),
            cleanup("0x005d7b60", "0x0061fee4", "CFrontEndPage__DeActiveNotification", "the deactivating front-end page pointer", "frontend-deactive-notification"),
            cleanup("0x005d7b80", "0x0061ff0c", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d7b96", "0x0061ff14", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d7bac", "0x0061ff1c", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d7bc2", "0x0061ff24", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d7bf0", "0x0061ff4c", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7bf8", "0x0061ff54", "CRT__EhVectorDestructorIterator_WithUnwind", "the 0x20-element CGenericActiveReader array at (*(EBP-0x10))+0x0c", "eh-vector-dtor", "active-reader-dtor"),
            cleanup("0x005d7c20", "0x0061ff7c", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7c28", "0x0061ff84", "CRT__EhVectorDestructorIterator_WithUnwind", "the 0x20-element CGenericActiveReader array at (*(EBP-0x10))+0x0c", "eh-vector-dtor", "active-reader-dtor"),
            cleanup("0x005d7c50", "0x0061ffac", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d7c70", "0x0061ffd4", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d7ca0", "0x0061fffc", "OID__FreeObject_Callback", "*(EBP-0x6c)", "oid-free"),
            cleanup("0x005d7cd0", "0x00620024", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d7cf0", "0x0062004c", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
            cleanup("0x005d7d09", "0x00620054", "OID__FreeObject_Callback", "*(EBP-0x10)", "oid-free"),
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
            throw new IllegalStateException("Wave786 apply encountered missing/bad rows");
        }
    }
}
