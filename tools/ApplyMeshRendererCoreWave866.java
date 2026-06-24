//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyMeshRendererCoreWave866 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String convention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String convention, DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.convention = convention;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "meshrenderer-core-wave866",
            "wave866-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened",
            "important-connective-infrastructure",
            "mesh-renderer",
            "render-core"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.convention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean alreadyApplied(Function fn, Spec spec) {
        return fn.getName().equals(spec.name)
            && signatureMatches(fn, spec)
            && spec.comment.equals(fn.getComment())
            && hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.convention).append(" ").append(spec.name).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                stats.bad++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }

            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsComment = !spec.comment.equals(fn.getComment());
            boolean needsTags = !hasAllTags(fn, spec.tags);

            if (!needsSignature && !needsComment && !needsTags) {
                println("SKIP_OK: " + spec.address + " " + spec.name + " already current");
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY_UPDATE: " + spec.address + " " + spec.name
                    + " -> " + expectedSignature(spec)
                    + " needsSignature=" + needsSignature
                    + " needsComment=" + needsComment
                    + " needsTags=" + needsTags);
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else if (needsComment || needsTags) {
                    stats.commentOnlyUpdated++;
                }
                return;
            }

            if (needsSignature) {
                fn.setCallingConvention(spec.convention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            if (needsComment) {
                fn.setComment(spec.comment);
            }
            for (String tag : spec.tags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                }
            }

            Function readback = functionAtEntry(spec.address);
            if (readback == null || !alreadyApplied(readback, spec)) {
                println("READBACK_BAD: " + spec.address);
                if (readback != null) {
                    println("READBACK_GOT: " + readback.getName() + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
                }
                stats.bad++;
                return;
            }
            println("READBACK_OK: " + spec.address + " " + spec.name + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00549570",
                "CMeshRenderer__RenderMeshCore",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("world_position_x", floatType),
                    param("world_position_y", floatType),
                    param("world_position_z", floatType),
                    param("world_position_w", floatType),
                    param("transform_matrix12", floatPtr),
                    param("mesh_part", voidPtr),
                    param("render_context", voidPtr),
                    param("effect_owner", voidPtr),
                    param("render_slot_or_mode", intType),
                    param("render_flags", intType),
                    param("reserved_zero", intType),
                    param("world_position_vec4", voidPtr)
                },
                "Wave866 mesh-renderer-core static read-back: CMeshRenderer__RenderMesh calls this caller-cleaned core draw body once at 0x004b6a82, after copying the four world-position dwords by value, then pushing transform_matrix12, mesh_part, render_context, effect_owner, render_slot_or_mode, render_flags, an observed zero slot, and the original world_position_vec4 pointer; the caller cleans 0x30 bytes. The body uses a 0x1e54-byte stack frame, reads mesh_part+0x8c for mesh-type dispatch, uses render-context vfuncs +0x70/+0x68 in the caller and +0x1c/+0x18/+0x14 frame-provider slots in the core, handles animated pose/interpolation evidence through CMCMech__BuildInterpolatedPoseAndAnchor, emits CVBufTexture vertices/indices/batch renders, and hands layer-pass rendering to CMeshRenderer__RenderMeshWithLayerPasses at 0x0054a4b6 and 0x0054b265. This is high-importance connective renderer infrastructure despite dense local evidence and weak source-body parity. Static retail Ghidra metadata/decompile/xref evidence only; exact renderer/mesh/pose layouts, exact source identity, visual rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("caller-cleaned-0x30", "large-stack-frame", "cvbuftexture", "mesh-layer-pass", "animated-pose")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
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
            throw new RuntimeException("Wave866 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
