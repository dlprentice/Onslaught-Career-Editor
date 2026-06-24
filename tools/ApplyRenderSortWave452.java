//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyRenderSortWave452 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;
        final boolean updateSignature;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters,
                boolean updateSignature) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(Address address) {
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        if (!spec.updateSignature) {
            return "<comment-tags-only; signature deferred>";
        }
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
            "render-sort-wave452",
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
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }

            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (spec.updateSignature) {
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
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

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
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
        DataType byteType = ByteDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004b5250",
                "CDXEngine__NormalizeCycleScalar",
                "__cdecl",
                floatType,
                "Wave452 signature/comment hardening: normalizes an x87 scalar by wrapping against the retail float constants at 0x005d8568 and 0x005d856c. HUD render callsites push one float value and immediately consume ST0 with FSTP after the call, so the prior void return was stale. Static retail callsite/instruction evidence only; exact angle/time unit semantics, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("render-sort", "x87-return", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("cycle_scalar", floatType)
                },
                true
            ),
            new Spec(
                "0x004b52a0",
                "Math__AbsDoubleFromSignedFloat",
                "__cdecl",
                floatType,
                "Wave452 signature/comment hardening: returns the absolute-value x87 scalar for one caller-pushed float, using FCHS on the negative path and leaving ST0 live for the HUD caller. The body reads the 0.0f-style compare constant at 0x005d856c; the legacy double return label was wider than the observed caller use. Static retail callsite/instruction evidence only; exact source helper identity, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("math", "x87-return", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("value", floatType)
                },
                true
            ),
            new Spec(
                "0x004b52c0",
                "CDXEngine__PackVec3AndDepthToSortKey",
                "__cdecl",
                intType,
                "Wave452 signature/comment hardening: packs three vec3 lanes from position_vec3 and the depth_scalar into a 32-bit render sort key using the observed scale/bias constants 0x005dbc4c, 0x005d95b8, and 0x005d9644. Directional sample ring and mesh renderer core callsites push exactly a vector pointer plus float depth and clean 0x8 bytes after the call. Static retail callsite/decompile evidence only; exact bucket ordering semantics, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("render-sort", "sort-key", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("position_vec3", voidPtr),
                    param("depth_scalar", floatType)
                },
                true
            ),
            new Spec(
                "0x004b5330",
                "CMeshPart__EvaluateAnimatedTransformCore",
                null,
                null,
                "Wave452 comment/tag hardening only: evaluates mesh-part animation-frame interpolation, writes transform/current-part outputs, and reaches CMCMech__BuildInterpolatedPoseAndAnchor for mech-pose interpolation. One caller shows six cdecl stack arguments, but adjacent render-recursive callsites mix by-value matrix/vector stack material, so the signature is intentionally deferred. Static retail decompile/callsite evidence only; exact matrix/vector types, animation controller layout, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("meshpart", "animation", "transform", "signature-deferred", "comment-hardened"),
                new ParameterImpl[] {},
                false
            ),
            new Spec(
                "0x004b5ad0",
                "CMeshPart__RenderAnimatedRecursive",
                null,
                null,
                "Wave452 comment/tag hardening only: recursive mesh-part render wrapper that prepares optional orientation/controller transforms, calls CMeshPart__EvaluateAnimatedTransformCore, dispatches CMeshRenderer__RenderMesh, then recurses across child part lists at +0x90/+0x94. The callsites include by-value matrix/vector stack regions, so the signature is intentionally deferred. Static retail decompile/callsite evidence only; exact part tree layout, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("meshpart", "render", "recursive", "signature-deferred", "comment-hardened"),
                new ParameterImpl[] {},
                false
            ),
            new Spec(
                "0x004b5e80",
                "CSphere__RenderPartsWithOrientation",
                null,
                null,
                "Wave452 comment/tag hardening only: iterates the sphere mesh-part table, applies an orientation transform from the controller/vtable path, prepares local matrices, and dispatches visible parts through CMeshRenderer__RenderMesh. The caller builds by-value orientation/matrix material on the stack, so the signature is intentionally deferred. Static retail decompile/callsite evidence only; exact CSphere layout, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("sphere", "render", "orientation", "signature-deferred", "comment-hardened"),
                new ParameterImpl[] {},
                false
            ),
            new Spec(
                "0x004b6260",
                "CSphere__RenderAnimatedRecursive",
                null,
                null,
                "Wave452 comment/tag hardening only: chooses between cached-pose rendering, CSphere__RenderPartsWithOrientation, and CMeshPart__RenderAnimatedRecursive, then optionally follows linked/sibling parts through +0x8 when recursive rendering remains enabled. HUD target-indicator and internal callsites have mixed stack payloads, so the signature is intentionally deferred. Static retail decompile/callsite evidence only; exact CSphere/tree layout, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("sphere", "render", "recursive", "signature-deferred", "comment-hardened"),
                new ParameterImpl[] {},
                false
            ),
            new Spec(
                "0x004b6350",
                "CMeshRenderer__RenderMesh",
                "__cdecl",
                voidType,
                "Wave452 signature/comment hardening: top-level mesh render dispatcher with seven observed stack arguments: world position, transform matrix, mesh part, render context, effect owner, render slot/mode, and render flags. The body gates mesh-part modes/flags, handles particle/effect setup through CParticleManager__CreateEffect, writes world matrix state via CDXEngine__SetWorldMatrixElements, dispatches CMeshRenderer__RenderMeshCore, and can draw debug volume overlays. Static retail decompile/callsite evidence only; exact matrix/vector field names, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-renderer", "render", "particle-effects", "debug-overlay", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("world_position_vec4", voidPtr),
                    param("transform_matrix12", voidPtr),
                    param("mesh_part", voidPtr),
                    param("render_context", voidPtr),
                    param("effect_owner", voidPtr),
                    param("render_slot_or_mode", intType),
                    param("render_flags", byteType)
                },
                true
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new RuntimeException("ApplyRenderSortWave452 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
