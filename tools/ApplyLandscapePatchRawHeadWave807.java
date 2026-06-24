//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyLandscapePatchRawHeadWave807 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        String actual = fn.getSignature().toString();
        if (!actual.equals(expectedSignature(spec))) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        Parameter[] params = fn.getParameters();
        if (params.length != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < params.length; i++) {
            if (!params[i].getName().equals(spec.parameters[i].getName())) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        return !fn.getName().equals(spec.name)
            || !signatureMatches(fn, spec)
            || fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address
                + ": " + fn.getSignature() + " != " + expectedSignature(spec));
        }
        if (!spec.comment.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName()
                    + " expected=" + spec.previousName + " or " + spec.name);
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(spec.comment)
                || !hasAllTags(fn, spec.tags);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                else if (commentOrTagsNeedUpdate || renameNeeded) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            if (!signatureNeedsUpdate) {
                stats.commentOnlyUpdated++;
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "landscape-patch-raw-head-wave807",
            "wave807-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();

        return new Spec[] {
            new Spec(
                "0x0048f2f0",
                "CDXPatch__SetGridOriginStepAndRebuild",
                "CDXLandscape__SetUpdateBoundsAndRebuildVB",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("grid_origin_x", intType),
                    param("grid_origin_z", intType),
                    param("grid_step", intType),
                    param("tile_metadata", intType)
                },
                "Wave807 static read-back correction: RET 0x10 proves four stack arguments after ECX=this. CDXLandscape__UpdateLOD callsite 0x00546fe6 calls this immediately after CDXPatchManager__AllocatePatchSlot returns a patch pointer in EAX, then passes two tile coordinates scaled by 8, grid_step derived as 4 >> lod_slot, and a tile-record metadata value from [ESI+0x0b]. Body stores the args into CDXPatch fields +0x2c, +0x30, +0x34, and +0x4c, then calls CDXPatch__RebuildHeightGridVertexBuffer(this). Static retail evidence only; exact CDXPatch field names, tile-record layout, runtime terrain rendering/GPU behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cdxpatch", "dx-landscape", "terrain-lod", "height-grid", "renamed", "tranche-head")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyLandscapePatchRawHeadWave807 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave807 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
