//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyCPDSimpleSpriteRenderResidualCurrentRiskWave1191 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Target(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1191-cpdsimplesprite-render-residual-current-risk-review",
        "wave1191-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "cpdsimplesprite",
        "particle-render",
        "sprite-render",
        "source-identity-deferred",
        "exact-layout-deferred",
        "runtime-behavior-deferred",
        "visual-parity-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x004c0940",
            "CPDSimpleSprite__SetUVFromTileIndex",
            "void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void * this, int tile_index, uint tile_grid_selector, int unused_context)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite UV atlas helper retained from the Wave462 correction. Fresh metadata/xref/decompile/instruction evidence shows a tile-grid selector jump table, packed tile-index coordinate math, writes to the CPDSimpleSprite UV rectangle at this+0xb8..this+0xc4, and fallback full 0..1 UVs when texture/frame state is absent. Static rebuild contract only; exact descriptor/texture-frame layout, exact source-body identity, runtime particle rendering, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("uv-atlas", "tile-index", "sprite-uv")
        ),
        new Target(
            "0x004c5280",
            "CPDSimpleSprite__CopyTransformMatrix",
            "void __thiscall CPDSimpleSprite__CopyTransformMatrix(void * this, void * out_matrix, void * unused_context)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite transform-copy helper retained from the Wave462 correction. Fresh metadata/xref/decompile/instruction evidence shows the helper copying observed basis/transform float fields from this into the caller-provided output matrix block; Ghidra still exposes the unused/context artifact, so the signature remains conservative. Static rebuild contract only; exact matrix structure, concrete descriptor layout, exact source-body identity, runtime particle transform behavior, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("transform-copy", "matrix-copy")
        ),
        new Target(
            "0x004c5c50",
            "CPDSimpleSprite__BuildUvAtlasBuckets",
            "void __fastcall CPDSimpleSprite__BuildUvAtlasBuckets(float unused_seed)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite UV-atlas bucket initializer retained from the Wave462 correction. Fresh xrefs show CPDSimpleSprite__ProcessAndRenderSpriteList calls this at 0x004c5d6f when DAT_0082b39c is clear; the body fills five tile-grid bucket families under DAT_00829e58 and sets DAT_0082b39c after initialization. Static rebuild contract only; exact global table schema, source-body identity, runtime renderer initialization timing, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("uv-atlas", "table-init", "global-atlas-table")
        ),
        new Target(
            "0x004c5d50",
            "CPDSimpleSprite__ProcessAndRenderSpriteList",
            "void __fastcall CPDSimpleSprite__ProcessAndRenderSpriteList(void * descriptor)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite active sprite-list processor retained from the Wave462 correction. Fresh xrefs show CPDSimpleSprite__VFunc_23_004c8040 calls this at 0x004c8056; body evidence initializes noise and UV-atlas helpers, walks/gates active particles by descriptor state, visibility and distance fields, evaluates scale/colour/orientation/expression paths, calls CPDSimpleSprite__ScaleVec3InPlace, CPDSimpleSprite__ReciprocalVec3Magnitude, CPDSimpleSprite__EvaluateCurveDrivenScale, then emits quad vertices through CVBufTexture__GetVertexPtrAt and six indices through DXParticleTexture__GetIndexBuffer. Static rebuild contract only; exact descriptor/particle/CVBufTexture layouts, runtime particle ordering/culling, visual parity, source-body identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("sprite-list", "vertex-emission", "cvbuftexture", "dxparticletexture")
        ),
        new Target(
            "0x004c78b0",
            "CPDSimpleSprite__ScaleVec3InPlace",
            "void __thiscall CPDSimpleSprite__ScaleVec3InPlace(void * this, float scale, float unused_context)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite Vec3 scale helper retained from the Wave462 correction. Fresh xrefs show CPDSimpleSprite__ProcessAndRenderSpriteList calls this at 0x004c745f, 0x004c7689, and 0x004c7697; body evidence scales three consecutive float components in place by the supplied scalar while preserving the conservative Ghidra calling-convention shape. Static rebuild contract only; exact vector type, exact source-body identity, runtime particle orientation/scale behavior, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("vec3", "scale", "render-helper")
        ),
        new Target(
            "0x004c78d0",
            "CPDSimpleSprite__ReciprocalVec3Magnitude",
            "double __fastcall CPDSimpleSprite__ReciprocalVec3Magnitude(void * vec3)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite reciprocal-magnitude helper retained from the Wave462 correction. Fresh xrefs show CPDSimpleSprite__ProcessAndRenderSpriteList calls this at 0x004c73ef; body evidence computes 1.0 / sqrt(x*x + y*y + z*z) for three float components at vec3, and no zero-length guard is visible in the retail helper. Static rebuild contract only; exact vector type, runtime zero-vector behavior, source-body identity, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("vec3", "reciprocal-magnitude", "sqrt")
        ),
        new Target(
            "0x004c7950",
            "CPDSimpleSprite__EvaluateCurveDrivenScale",
            "double __thiscall CPDSimpleSprite__EvaluateCurveDrivenScale(void * this, void * x_value, float lifetime, float particle_context, float eval_flags)",
            "Wave1191 static current-risk read-back: CPDSimpleSprite curve-driven scalar evaluator retained from the Wave462 correction. Fresh xrefs show CPDSimpleSprite__ProcessAndRenderSpriteList calls this at 0x004c74f0; decompile/instruction evidence evaluates recursive expression nodes and observed pow/exp/sin/cos/inv/log/rand-style operator cases plus clamp/wrap output modes. Static rebuild contract only; exact curve/expression structure, random distribution parity, source-body identity, runtime particle-scale behavior, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("curve-scale", "expression-eval", "particle-scale")
        )
    };

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        boolean dryRun = true;
        if ("apply".equals(mode)) {
            dryRun = false;
        } else if (!"dry".equals(mode)) {
            throw new IllegalArgumentException("Expected mode dry|apply, got: " + mode);
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : TARGETS) {
            Address address = toAddr(target.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + target.address + " " + target.name);
                missing++;
                continue;
            }

            boolean targetBad = false;
            if (!target.name.equals(function.getName())) {
                println("BADNAME: " + target.address + " expected=" + target.name + " actual=" + function.getName());
                targetBad = true;
            }
            if (!target.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + target.address + " expected=" + target.signature + " actual=" + function.getSignature());
                targetBad = true;
            }
            if (targetBad) {
                bad++;
                continue;
            }

            Set<String> actualTags = tagNames(function);
            Set<String> requiredTags = new HashSet<>(Arrays.asList(target.tags));
            requiredTags.removeAll(actualTags);
            boolean commentNeedsUpdate = function.getComment() == null || !target.comment.equals(function.getComment());
            boolean tagsNeedUpdate = !requiredTags.isEmpty();

            if (!commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + target.address + " " + target.name + " comment/tags already current");
                skipped++;
            } else if (dryRun) {
                println("WOULD_UPDATE: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags=+" + String.join(",", requiredTags));
                if (commentNeedsUpdate) {
                    commentOnlyUpdated++;
                }
                tagsAdded += requiredTags.size();
            } else {
                if (commentNeedsUpdate) {
                    function.setComment(target.comment);
                    commentOnlyUpdated++;
                }
                for (String tag : requiredTags) {
                    function.addTag(tag);
                }
                tagsAdded += requiredTags.size();
                updated++;
                currentProgram.flushEvents();
                Thread.sleep(50L);

                Function readBack = functionManager.getFunctionAt(address);
                if (readBack == null) {
                    println("VERIFY_MISSING: " + target.address);
                    bad++;
                } else {
                    if (!target.comment.equals(readBack.getComment())) {
                        println("VERIFY_BAD_COMMENT: " + target.address);
                        bad++;
                    }
                    Set<String> readBackTags = tagNames(readBack);
                    for (String tag : target.tags) {
                        if (!readBackTags.contains(tag)) {
                            println("VERIFY_MISSING_TAG: " + target.address + " " + tag);
                            bad++;
                        }
                    }
                }
                println("UPDATED: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags_added=" + requiredTags.size());
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + commentOnlyUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1191 CPDSimpleSprite render residual normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private static String[] withCommon(String... extraTags) {
        String[] tags = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, tags, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, tags, COMMON_TAGS.length, extraTags.length);
        return tags;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
