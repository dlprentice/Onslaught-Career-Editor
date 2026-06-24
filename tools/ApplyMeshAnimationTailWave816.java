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

public class ApplyMeshAnimationTailWave816 extends GhidraScript {
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
            "mesh-animation-tail-wave816",
            "wave816-readback-verified",
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
        println("ApplyMeshAnimationTailWave816 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004b0cd0",
                "CMesh__SelectModeSpecificPtr",
                new String[] {},
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave816 static read-back: selects the CMesh part pointer used by loaders/collision/shadow/random-vertex paths from mode field +0x8c. Mode 1 or 3 returns this, mode 6 returns the alternate pointer at +0x124, and other modes return null. Evidence includes the current decompile plus 15 call xrefs from CMesh__Load, CDestructableSegmentsController__ProcessNode, CMeshCollisionVolume vfuncs, CStaticShadows__BuildShadowMaps, and CMesh__GetRandomVertexWeightedByPartArea. Static retail Ghidra evidence only; exact mode enum, concrete mesh layout, runtime render/collision behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmesh", "mode-selector", "meshpart-selector")
            ),
            new Spec(
                "0x004b0d00",
                "CMeshPart__InterpolateSegmentTransform",
                new String[] {},
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("frame_a", intType),
                    param("frame_b", intType),
                    param("frame_lerp", floatType),
                    param("out_transform_3x4", voidPtr),
                    param("out_anchor_vec4", floatPtr)
                },
                "Wave816 static read-back/signature hardening: interpolates CMeshPart per-frame anchor/transform data. The only direct callsite is 0x004b17fc in CMCMech__BuildInterpolatedPoseAndAnchor, which pushes five stack arguments, sets ECX to the part, and the callee returns with RET 0x14. The body clamps frame_a/frame_b against count +0xb8, maps them through byte table +0xc4, reads anchor vec4 records at +0xc8 and transform rows at +0x10c, blends row/anchor deltas by frame_lerp, then writes a 12-dword transform and 4-float anchor output. Static retail Ghidra evidence only; exact CMeshPart field names, frame-table schema, matrix convention, source-body identity, runtime animation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "animation", "interpolation", "ret-0x14", "abi-corrected")
            ),
            new Spec(
                "0x004b0fb0",
                "CMCMech__BuildInterpolatedPoseAndAnchor",
                new String[] {},
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("frame_a", intType),
                    param("frame_b", intType),
                    param("blend_step_or_flag", intType),
                    param("optional_pose_controller", voidPtr),
                    param("out_transform_3x4", voidPtr),
                    param("out_anchor_vec4", floatPtr),
                    param("cache_slot", intType),
                    param("notify_callbacks", intType),
                    param("force_recursive_path", intType)
                },
                "Wave816 static read-back/signature hardening: builds interpolated pose transform and anchor output for CMeshPart/CMCMech-style animation users. Representative callsites from CMesh__Load, CMeshPart__CacheFrameData, CMeshPart__EvaluateAnimatedTransformCore, CMeshRenderer__RenderMeshCore, CMCMech__UpdateBone, CMCBuggy__UpdateWheel, CMCTentacle__UpdateSpline, and CRTCutscene__BuildCurrentFrameOutputs push nine stack dwords and the body returns with RET 0x24. The body reuses two global pose-cache slots at DAT_00704cf0/DAT_00704d20 with anchors at DAT_00704cd0/DAT_00704ce0, follows parent part +0x98, local cache counts/pointers at +0x118/+0x11c/+0x120/+0x104/+0x108, calls CMeshPart__InterpolateSegmentTransform, and optionally calls pose-controller vtable slots +0x70/+0x4/+0xc/+0x10 while filling output transform/anchor buffers. Static retail Ghidra evidence only; exact CMCMech/CMeshPart/controller types, argument semantics beyond observed frame/output/cache/callback roles, global cache lifetime, runtime animation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "animation", "pose-cache", "ret-0x24", "abi-corrected")
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
            throw new RuntimeException("Wave816 apply encountered missing/bad rows");
        }
    }
}
