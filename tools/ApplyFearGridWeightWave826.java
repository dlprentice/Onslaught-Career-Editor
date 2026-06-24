//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFearGridWeightWave826 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "feargrid-weight-wave826",
            "wave826-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "feargrid",
            "occupancy-grid"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() throws Exception {
        return new Spec[] {
            new Spec(
                "0x004daff0",
                "FearGridTrackedObject__LookupFearWeightByArchetype",
                "double __thiscall FearGridTrackedObject__LookupFearWeightByArchetype(void * this)",
                "__thiscall",
                DoubleDataType.dataType,
                new ParameterImpl[] {},
                "Wave826 static read-back/name correction: CFearGrid__RebuildOccupancyAndScheduleTick calls this helper with the tracked object being marked, not the CFearGrid grid object. The helper reads the tracked object's config/archetype name pointer at tracked_object+0xf0+0x08, scans DAT_008553f8 entries with an inline string compare against entry+0x30, returns the matched float at entry+0x34 through x87, and falls back to _DAT_005d856c when no name/list match exists. The caller filters tracked objects by object+0x11c matching grid+0x8008, scales this result by _DAT_005d8c4c, and marks the grid occupancy plane at grid+0x08. Static retail Ghidra evidence only; exact tracked-object class, DAT_008553f8 entry schema, scalar semantics, runtime AI/fear behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "tracked-object", "archetype-weight", "preset-list")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!fn.getSignature().toString().equals(spec.expectedSignature)) {
            return false;
        }
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }

        if (!fn.getName().equals(spec.expectedName)) {
            if (dryRun) {
                println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName);
                stats.wouldRename++;
            } else {
                fn.setName(spec.expectedName, SourceType.USER_DEFINED);
                println("RENAMED: " + spec.address + " " + spec.expectedName);
                stats.renamed++;
            }
        }

        boolean signatureOk = sameSignature(fn, spec);
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasTags(fn, spec.tags);
        if (signatureOk && commentOk && tagsOk) {
            println("SKIP: " + spec.address + " " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY_UPDATE: " + spec.address + " " + spec.expectedName
                + " signature_ok=" + signatureOk + " comment_ok=" + commentOk + " tags_ok=" + tagsOk);
            if (!signatureOk) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.skipped++;
            return;
        }

        if (!signatureOk) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else {
            stats.commentOnlyUpdated++;
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        boolean readbackOk = true;
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
            stats.bad++;
            readbackOk = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            stats.bad++;
            readbackOk = false;
        }
        if (!hasTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            stats.bad++;
            readbackOk = false;
        }
        if (readbackOk) {
            println("READBACK_OK: " + spec.address + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0] : "dry";
        boolean dryRun = isDryRun(mode);
        println("ApplyFearGridWeightWave826 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave826 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
