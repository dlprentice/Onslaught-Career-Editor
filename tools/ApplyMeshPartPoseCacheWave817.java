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

public class ApplyMeshPartPoseCacheWave817 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String[] allowedExistingNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String[] allowedExistingNames,
                String callingConvention, DataType returnType, ParameterImpl[] parameters,
                String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.allowedExistingNames = allowedExistingNames;
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

    private boolean allowedName(Function fn, Spec spec) {
        String actual = fn.getName();
        if (actual.equals(spec.expectedName)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "meshpart-pose-cache-wave817",
            "wave817-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType a, DataType b) {
        if (a == null || b == null) {
            return a == b;
        }
        return a.getName().equals(b.getName()) || a.isEquivalent(b);
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        Parameter[] actualParams = fn.getParameters();
        if (actualParams.length != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < actualParams.length; i++) {
            Parameter actual = actualParams[i];
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

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        if (!allowedName(fn, spec)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.expectedName);
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);

        if (needsRename) {
            if (dryRun) {
                stats.wouldRename++;
            } else {
                stats.renamed++;
            }
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsRename && !needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
        }
        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            println("READBACK_MISSING: " + spec.address);
            stats.bad++;
            return;
        }
        if (readBackMatches(readBack, spec, stats)) {
            println("OK: " + spec.address + " " + readBack.getName() + " " + readBack.getSignature());
            stats.updated++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }
        println("ApplyMeshPartPoseCacheWave817 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004b4ba0",
                "CMeshPart__PopulatePoseCacheRecursive",
                new String[] {},
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("anchor_x", floatType),
                    param("anchor_y", floatType),
                    param("anchor_z", floatType),
                    param("anchor_w", floatType),
                    param("transform_dword00", intType),
                    param("transform_dword01", intType),
                    param("transform_dword02", intType),
                    param("transform_dword03", intType),
                    param("transform_dword04", intType),
                    param("transform_dword05", intType),
                    param("transform_dword06", intType),
                    param("transform_dword07", intType),
                    param("transform_dword08", intType),
                    param("transform_dword09", intType),
                    param("transform_dword10", intType),
                    param("transform_dword11", intType),
                    param("mesh_part", voidPtr),
                    param("frame_arg0", intType),
                    param("frame_arg1", intType),
                    param("cache_value", intType)
                },
                "Wave817 static read-back/signature hardening: recursive MeshPart pose-cache population helper. The signature scalarizes the observed RET 0x50 aggregate-stack payload rather than claiming exact source aggregate types. The body sets up CMeshPart__EvaluateAnimatedTransformCore, copies a 12-dword transform block into cache slot this[0] indexed by mesh_part+0x88, copies the anchor vec4 into this[1], writes frame/cache scalars through this[2]/this[3], and recurses over children from mesh_part+0x90/+0x94; direct xrefs are the self-recursive call at 0x004b4ca1 and CMeshPart__RefreshCachedPoseIfStale at 0x004b4dbc. Static retail Ghidra evidence only; exact aggregate C signature, concrete cache/CMeshPart/controller layouts, source-body identity, runtime animation/render behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "pose-cache", "recursive", "ret-0x50", "scalarized-aggregate", "abi-corrected")
            ),
            new Spec(
                "0x004b4cd0",
                "CMeshPart__RefreshCachedPoseIfStale",
                new String[] {},
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_context", voidPtr),
                    param("pose_controller", voidPtr),
                    param("unused_stack_arg2", intType),
                    param("force_refresh", intType)
                },
                "Wave817 static read-back/signature hardening: refreshes a pose-cache object when DAT_008a9aac has advanced past the cached timestamp at this+0x14 or force_refresh is nonzero. Callers push four stack dwords and the callee exits with RET 0x10; CSphere__RenderAnimatedRecursive calls it at 0x004b6296 and CMeshPart__EvaluatePoseTransformForFrame calls it at 0x004b4e81. The body uses pose-controller vtable callbacks +0x70/+0x1c/+0x18/+0x20, marks this+0x14 with 0xffffd8f1 during rebuild, seeds the root matrix from DAT_00704db8 and the first parent part through mesh_context+0x160, calls CMeshPart__PopulatePoseCacheRecursive at 0x004b4dbc, then restores this+0x14 and writes this+0x18. Static retail Ghidra evidence only; exact cache/controller/mesh layouts, the unused stack slot meaning, source-body identity, runtime animation/render behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "pose-cache", "stale-refresh", "ret-0x10", "abi-corrected")
            ),
            new Spec(
                "0x004b4de0",
                "CMeshPart__EvaluatePoseTransformForFrame",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("animation_context", voidPtr),
                    param("pose_controller", voidPtr),
                    param("mesh_part", voidPtr),
                    param("out_anchor_vec4", floatPtr),
                    param("out_transform_3x4", floatPtr),
                    param("skip_controller_transform", intType),
                    param("unused_stack_arg6", intType)
                },
                "Wave817 static read-back/signature hardening: evaluates a MeshPart pose transform for a caller-supplied frame/context and writes default DAT_00704de8 anchor plus DAT_00704db8 transform outputs before taking either the cached-pose or interpolation path. Four observed callsites, CDiveBomber__SelectTarget 0x00445130, CMeshCollisionVolume__SetPartBounds 0x004ad70a, raw site 0x004dd1cf, and raw site 0x004dede9, push seven dwords and clean with ADD ESP, 0x1c, so the signature records a seven-argument cdecl ABI while preserving one unused stack slot. The body can call CMeshPart__RefreshCachedPoseIfStale at 0x004b4e81, copy cached anchor/matrix entries by mesh_part+0x88, or call CMeshPart__ResolveWrappedFrameIndexAndLerp and CMCMech__BuildInterpolatedPoseAndAnchor, then optionally applies pose-controller transform callbacks through Vec3__SetXYZ and Mat34__SetRows when skip_controller_transform is zero. Static retail Ghidra evidence only; exact source aggregate types, raw-site owner identity, concrete controller/cache layouts, runtime animation/collision/render behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "pose-cache", "cdecl-seven-args", "default-anchor-transform", "abi-corrected")
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
            throw new RuntimeException("Wave817 apply encountered missing/bad rows");
        }
    }
}
