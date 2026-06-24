//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyParticleSpriteRenderWave462 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "particle-sprite-render-wave462",
            "retail-binary-evidence"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(250);
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004c0940",
                "CPDSimpleSprite__SetUVFromTileIndex",
                "__thiscall",
                voidType,
                "Wave462 correction: Computes the CPDSimpleSprite atlas UV rectangle at +0xb8..+0xc4 from a packed tile index and tile-grid selector; falls back to full 0..1 UVs when texture/frame state is absent. Static retail-binary evidence only; runtime rendering behavior, exact descriptor layout, source identity, and rebuild parity remain unproven.",
                tags("uv-atlas", "sprite", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tile_index", intType),
                    param("tile_grid_selector", uintType),
                    param("unused_context", intType)
                }
            ),
            new Spec(
                "0x004c14f0",
                "CPDSimpleSprite__VFunc_10_004c14f0",
                "__thiscall",
                intType,
                "Wave462 correction: CPDSimpleSprite vtable slot 10 updates per-particle sprite state, including expression-driven particle +0x74, optional +0x50 adjustment, optional nested vtable dispatch from descriptor +0x80, and frame accumulator +0x78. Static retail-binary evidence only; runtime rendering behavior, exact descriptor/particle layout, source identity, and rebuild parity remain unproven.",
                tags("vtable-slot-10", "sprite-update", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("particle", voidPtr),
                    param("unused_context", intType)
                }
            ),
            new Spec(
                "0x004c35d0",
                "CEngine__ConfigureParticleBurstForDistance",
                "__thiscall",
                voidType,
                "Wave462 correction: Configures the particle resource count at particle +0x80, optionally derives it from distance against the parent particle transform, calls CParticleManager__SetParticleResource(count * 0x28), and initializes resource-slot records under particle +0x88. Static retail-binary evidence only; runtime burst behavior, exact ownership/layout, source identity, and rebuild parity remain unproven.",
                tags("particle-resource", "distance-lod", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("particle", voidPtr),
                    param("unused_context", intType)
                }
            ),
            new Spec(
                "0x004c5280",
                "CPDSimpleSprite__CopyTransformMatrix",
                "__thiscall",
                voidType,
                "Wave462 correction: Copies observed CPDSimpleSprite matrix/basis fields into a caller-provided output block; Ghidra still shows local decompiler artifacts for the fourth column/unused context. Static retail-binary evidence only; exact matrix layout, runtime rendering behavior, source identity, and rebuild parity remain unproven.",
                tags("transform-copy", "sprite", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_matrix", voidPtr),
                    param("unused_context", voidPtr)
                }
            ),
            new Spec(
                "0x004c5c50",
                "CPDSimpleSprite__BuildUvAtlasBuckets",
                "__fastcall",
                voidType,
                "Wave462 correction: Initializes the global DAT_00829e58 UV-atlas lookup table for five tile-grid buckets and sets DAT_0082b39c after the table is built. Static retail-binary evidence only; runtime rendering behavior, exact table ownership, source identity, and rebuild parity remain unproven.",
                tags("uv-atlas", "table-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("unused_seed", floatType)
                }
            ),
            new Spec(
                "0x004c5d50",
                "CPDSimpleSprite__ProcessAndRenderSpriteList",
                "__fastcall",
                voidType,
                "Wave462 correction: Processes the CPDSimpleSprite active particle list, initializes noise/UV helpers, gates particles by visibility/distance bits, evaluates colour/scale/orientation paths, and emits quad vertices plus six indices through CVBufTexture/DXParticleTexture helpers. Static retail-binary evidence only; runtime rendering behavior, exact descriptor/particle layout, source identity, and rebuild parity remain unproven.",
                tags("sprite-render", "vertex-emission", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("descriptor", voidPtr)
                }
            ),
            new Spec(
                "0x004c78b0",
                "CPDSimpleSprite__ScaleVec3InPlace",
                "__thiscall",
                voidType,
                "Wave462 correction: Compact helper that scales three consecutive float components in place by the supplied scalar; caller context shows this is used by the sprite render path. Static retail-binary evidence only; exact vector type, source identity, and rebuild parity remain unproven.",
                tags("vec3", "scale", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("scale", floatType),
                    param("unused_context", floatType)
                }
            ),
            new Spec(
                "0x004c78d0",
                "CPDSimpleSprite__ReciprocalVec3Magnitude",
                "__fastcall",
                doubleType,
                "Wave462 correction: Returns 1.0 / sqrt(x*x + y*y + z*z) for three float components at the supplied vector pointer; no zero-length guard is visible in the retail helper. Static retail-binary evidence only; exact vector type, source identity, and rebuild parity remain unproven.",
                tags("vec3", "reciprocal-magnitude", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("vec3", voidPtr)
                }
            ),
            new Spec(
                "0x004c7950",
                "CPDSimpleSprite__EvaluateCurveDrivenScale",
                "__thiscall",
                doubleType,
                "Wave462 correction: Evaluates an expression-driven scalar using CPDSimpleSprite expression nodes, with observed pow/exp/sin/cos/inv/log/rand operator cases and clamp/wrap-style output modes. Static retail-binary evidence only; exact curve structure, source identity, and rebuild parity remain unproven.",
                tags("curve-scale", "expression-eval", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x_value", voidPtr),
                    param("lifetime", floatType),
                    param("particle_context", floatType),
                    param("eval_flags", floatType)
                }
            ),
            new Spec(
                "0x004c8040",
                "CPDSimpleSprite__VFunc_23_004c8040",
                "__fastcall",
                voidType,
                "Wave462 correction: CPDSimpleSprite vtable slot 23 initializes the noise table and dispatches CPDSimpleSprite__ProcessAndRenderSpriteList only when descriptor +0x6c is nonzero. Static retail-binary evidence only; runtime rendering behavior, exact descriptor layout, source identity, and rebuild parity remain unproven.",
                tags("vtable-slot-23", "render-dispatch", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("descriptor", voidPtr)
                }
            ),
            new Spec(
                "0x004c8060",
                "CEngine__ComputeSpriteTintByDistance",
                "__thiscall",
                intType,
                "Wave462 correction: Computes a packed sprite tint/alpha value from expression colour curves plus distance or age fade logic, with output modes that pack RGB or alpha-first variants. Static retail-binary evidence only; runtime tint behavior, exact ownership/layout, source identity, and rebuild parity remain unproven.",
                tags("tint", "distance-fade", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("particle_index", intType),
                    param("alpha_scale", intType),
                    param("descriptor_context", floatType),
                    param("distance_context", floatType)
                }
            ),
            new Spec(
                "0x004cab30",
                "Color32__LerpArgb",
                "__cdecl",
                intType,
                "Wave462 correction: Linearly interpolates each ARGB byte from two packed 32-bit colours using t and (1.0 - t); no clamp is applied inside this helper. Static retail-binary evidence only; source identity and rebuild parity remain unproven.",
                tags("color", "lerp", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("from_argb", uintType),
                    param("to_argb", uintType),
                    param("t", floatType)
                }
            ),
            new Spec(
                "0x004cac40",
                "Math__InvLerpClamp01",
                "__cdecl",
                doubleType,
                "Wave462 correction: Computes inverse lerp (value - min) / (max - min), clamps the result to 0..1, and has no visible divide-by-zero guard in the retail helper. Static retail-binary evidence only; source identity and rebuild parity remain unproven.",
                tags("math", "clamp", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("value", floatType),
                    param("min_value", floatType),
                    param("max_value", floatType)
                }
            ),
            new Spec(
                "0x004cac80",
                "CPDSelector__ConvertNormalizedToScreenCoords",
                "__cdecl",
                voidType,
                "Wave462 correction: Scales a normalized pair by the observed screen/global scalar and rounds through CRT__RoundDoubleWithFpuChecks; the decompiler does not expose a stable return/output contract. Static retail-binary evidence only; exact output convention, source identity, and rebuild parity remain unproven.",
                tags("selector", "screen-coords", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("normalized_x", floatType),
                    param("normalized_y", floatType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
