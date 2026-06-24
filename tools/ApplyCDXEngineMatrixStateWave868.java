//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCDXEngineMatrixStateWave868 extends GhidraScript {
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
            "cdxengine-matrix-state-wave868",
            "wave868-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-reviewed",
            "important-connective-infrastructure",
            "cdxengine",
            "renderer-state",
            "matrix-state",
            "transform-cache"
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
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005508a0",
                "CDXEngine__ClearMatrixBlock",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("dest", voidPtr)},
                "Wave868 CDXEngine matrix-state static read-back: this helper clears most dwords in an 0x58-byte matrix/cache block while leaving the +0x10 and +0x20 slots untouched. The nearby caller at 0x00550870 iterates eight 0x5c-byte records from global 0x009c65c0 before reinitializing the global CDXEngine transform caches at 0x0055088e. This is high-importance, low local-evidence-density renderer infrastructure, not low-value glue. Static retail Ghidra metadata/decompile/xref evidence only; exact block layout, global table ownership, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("matrix-block-clear", "global-render-state")
            ),
            new Spec(
                "0x005508e0",
                "CDXEngine__InitTransformCaches",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave868 CDXEngine matrix-state static read-back: initializes the CDXEngine transform caches to identity matrices at this+0x354, this+0x394, this+0x3d4, and this+0x414, fills the larger matrix-state table beginning at this+0x454, marks dirty/state bytes at this+0xe28 through this+0xe2e, and resets adjacent render-state fields such as 0xfff00fff, 0xffff0000, 0x41200000, and 1.0 defaults. Xrefs include CDXFrontEnd__RenderStart and global render setup code that calls this after clearing matrix blocks. This is high-importance, low local-evidence-density renderer infrastructure. Static retail Ghidra evidence only; exact CDXEngine field names, table count semantics, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("transform-cache-init", "identity-matrix", "global-render-state")
            ),
            new Spec(
                "0x00550b10",
                "CDXEngine__SetProjectionMatrix",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("near_z", floatType),
                    param("far_z", floatType),
                    param("viewport_w", floatType),
                    param("viewport_h", floatType)
                },
                "Wave868 CDXEngine matrix-state static read-back: RET 0x10 and the existing clean signature show four float inputs after ECX. The body marks projection dirty byte this+0xe2a, builds a projection/depth matrix using near_z/viewport_w, near_z/viewport_h, far_z/(far_z-near_z), and -(near_z*far_z)/(far_z-near_z), then copies 16 floats to this+0x3d4. Xrefs span CDXEngine__Render, CHud__RenderTargetIndicatorOverlay, CDXCompass__RenderWorldSpaceOverlay, CFrontEnd__RenderStart, and CFEPBEConfig projection setup. This is high-importance, low local-evidence-density renderer infrastructure. Static retail Ghidra evidence only; exact camera/projection convention, viewport semantic naming, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("projection-matrix", "depth-matrix", "render-overlay")
            ),
            new Spec(
                "0x00550be0",
                "CDXEngine__SetViewAndProjection",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("view_matrix", floatPtr),
                    param("proj_matrix", floatPtr)
                },
                "Wave868 CDXEngine matrix-state static read-back: RET 0x8 and the existing clean signature show two matrix-pointer arguments after ECX. The body stages view/projection matrix values, dispatches through the shared matrix helper call visible in decompile as CVertexShader__DispatchTableCall_656f78, marks view/projection dirty byte this+0xe29, and copies 16 floats to this+0x394. Xrefs include CDXEngine__Render, CHud__RenderTargetIndicatorOverlay, CDXCompass__RenderWorldSpaceOverlay, CFrontEnd__RenderStart, CRenderQueue__RenderAll, and CFrontEnd__UpdateCamera. This is high-importance, low local-evidence-density renderer infrastructure. Static retail Ghidra evidence only; exact helper identity, row/column convention, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("view-projection-matrix", "render-queue", "camera-render-state")
            ),
            new Spec(
                "0x00550ca0",
                "CDXEngine__SetWorldMatrixElements",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("m00", floatType),
                    param("m01", floatType),
                    param("m02", floatType),
                    param("m03", floatType),
                    param("m10", floatType),
                    param("m11", floatType),
                    param("m12", floatType),
                    param("m13", floatType),
                    param("m20", floatType),
                    param("m21", floatType),
                    param("m22", floatType),
                    param("m23", floatType),
                    param("m30", floatType),
                    param("m31", floatType),
                    param("m32", floatType),
                    param("m33", floatType)
                },
                "Wave868 CDXEngine matrix-state static read-back: RET 0x40 and the existing clean signature show sixteen float inputs after ECX. The body marks world-matrix dirty byte this+0xe28, reorders selected matrix elements into a 4x4 world transform with zeroed slots and a 1.0 terminal element, then copies 16 floats to this+0x354. Xrefs make this a major renderer transform hub: CDXEngine__Render, CMeshRenderer__RenderMesh, CRenderQueue__BeginFrame, CRenderQueueBucket__RenderAndRecycle, CDXLandscape__Render, CDXTrees__Render, CWaterRenderSystem passes, CDXImposter__RenderAll, HUD/compass overlays, debug draw, and unit shadow probes all call it. This is high-importance, low local-evidence-density renderer infrastructure. Static retail Ghidra evidence only; exact matrix convention, full CDXEngine field layout, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("world-matrix", "render-transform-hub", "mesh-renderer", "water-render", "landscape-render")
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
            throw new RuntimeException("Wave868 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
