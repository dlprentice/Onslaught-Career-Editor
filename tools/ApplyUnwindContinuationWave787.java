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

public class ApplyUnwindContinuationWave787 extends GhidraScript {
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
            "unwind-continuation-wave787",
            "wave787-readback-verified",
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
        return cleanupNamed(address, "Unwind@" + address.substring(2), xref, helper, targetText, extraTags);
    }

    private Spec cleanupNamed(String address, String name, String xref, String helper, String targetText, String... extraTags) {
        String comment = "Wave787 static read-back: compiler-generated SEH unwind cleanup callback. Scope-table DATA xref "
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
        println("ApplyUnwindContinuationWave787 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            cleanup("0x005d7d30", "0x0062007c", "CDXSurf__UnlinkNodeFromGlobalList", "(*(EBP-0x10))+0x8", "dxsurf-unlink"),
            cleanup("0x005d7d3b", "0x00620084", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7d50", "0x006200ac", "CDXSurf__UnlinkNodeFromGlobalList", "conditional CDXSurf node pointer derived from (*(EBP-0x110))+0x8 or null at EBP-0x114", "dxsurf-unlink"),
            cleanup("0x005d7d86", "0x006200b4", "DeviceObject__ctor_like_00512d50", "*(EBP-0x110)", "deviceobject-helper"),
            cleanup("0x005d7da0", "0x006200dc", "CDXMemBuffer__dtor_base", "EBP-0x244", "dx-mem-buffer-dtor"),
            cleanupNamed("0x005d7dc0", "CDXTexture__Deserialize_Unwind", "0x00620104", "OID__FreeObject_Callback", "*(EBP-0x168) with DXTexture.cpp debug path 0x0065269c, line token 0xc25, and allocation/type value 0x2", "oid-free", "dxtexture-deserialize"),
            cleanup("0x005d7df0", "0x0062012c", "OID__FreeObject_Callback", "*(EBP-0xc8) with DXTrees.cpp debug path 0x006529b0, line token 0x5e, and allocation/type value 0x1f", "oid-free", "dxtrees-cleanup"),
            cleanup("0x005d7e09", "0x00620134", "OID__FreeObject_Callback", "*(EBP-0xc8) with DXTrees.cpp debug path 0x006529b0, line token 0x6a, and allocation/type value 0x1f", "oid-free", "dxtrees-cleanup"),
            cleanup("0x005d7e30", "0x0062015c", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7e50", "0x00620184", "DeviceObject__ctor_like_00512d50", "*(EBP-0x10)", "deviceobject-helper"),
            cleanup("0x005d7e70", "0x0062018c", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x3c", "fastvb-span-release"),
            cleanup("0x005d7e78", "0x00620194", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x5c", "fastvb-span-release"),
            cleanup("0x005d7e80", "0x0062019c", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x6c", "fastvb-span-release"),
            cleanup("0x005d7e88", "0x006201a4", "CFastVB__ReleaseBufferAndResetTriplet_0056f520", "EBP-0x2c", "fastvb-span-release"),
            cleanup("0x005d7e90", "0x006201ac", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x4c", "fastvb-span-release"),
            cleanup("0x005d7e98", "0x006201b4", "OID__FreeObject_Callback", "*(EBP+0x10)", "oid-free"),
            cleanup("0x005d7ea3", "0x006201bc", "OID__FreeObject_Callback", "*(EBP+0x4)", "oid-free"),
            cleanup("0x005d7ec0", "0x006201e0", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x4c", "fastvb-span-release"),
            cleanup("0x005d7ec8", "0x006201e8", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x3c", "fastvb-span-release"),
            cleanup("0x005d7ed0", "0x006201f0", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x1c", "fastvb-span-release"),
            cleanup("0x005d7ed8", "0x006201f8", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x2c", "fastvb-span-release"),
            cleanup("0x005d7ef0", "0x0062021c", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x1c", "fastvb-span-release"),
            cleanup("0x005d7ef8", "0x00620224", "OID__FreeObject_Callback", "*(EBP+0x8)", "oid-free"),
            cleanup("0x005d7f10", "0x00620248", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x1c", "fastvb-span-release"),
            cleanup("0x005d7f18", "0x00620250", "CFastVB__ReleaseBufferAndResetTriplet_0056f260", "EBP-0x3c", "fastvb-span-release"),
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
            throw new IllegalStateException("Wave787 apply encountered missing/bad rows");
        }
    }
}
