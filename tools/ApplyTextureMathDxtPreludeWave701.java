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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureMathDxtPreludeWave701 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texture-math-dxt-prelude-wave701",
            "wave701-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
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
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
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
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
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
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType doubleType = DoubleDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType floatPtr = new PointerDataType(floatType);

        return new Spec[] {
            new Spec(
                "0x005960c1",
                "CDXTexture__FastReciprocalSqrtScalar",
                "__stdcall",
                doubleType,
                new ParameterImpl[] { param("float_bits", uintType) },
                "Wave701 static read-back: computes a table-assisted reciprocal square-root approximation from raw IEEE-style float_bits using the mantissa lookup tables at DAT_00658c98/DAT_00658c9c and an exponent adjustment mask before returning the scalar as double. Static metadata only; exact lookup-table provenance, numeric error bounds, input domain, CPU-dispatch ABI, and runtime math correctness remain unproven.",
                signatureTags("texture-math", "reciprocal-sqrt", "lookup-table", "tranche-head")
            ),
            new Spec(
                "0x00596106",
                "CDXTexture__NormalizeVec3Fast",
                "__stdcall",
                floatPtr,
                new ParameterImpl[] {
                    param("normalized_vec3_out", floatPtr),
                    param("input_vec3", floatPtr)
                },
                "Wave701 static read-back: measures the three-float input_vec3 length squared, zeroes normalized_vec3_out for zero length, copies already-near-unit vectors when the observed tolerance check passes, otherwise scales xyz by the same table-assisted reciprocal square-root approximation used by CDXTexture__FastReciprocalSqrtScalar. Static metadata only; exact vec3 layout contract, tolerance policy, aliasing contract, numeric error bounds, and runtime math correctness remain unproven.",
                signatureTags("texture-math", "vec3-normalize", "reciprocal-sqrt", "dispatch-slot")
            ),
            new Spec(
                "0x005961d0",
                "CDXTexture__MultiplyMatrix4x4_InPlaceSafe",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("matrix4x4_out", floatPtr),
                    param("left_matrix4x4", floatPtr),
                    param("right_matrix4x4", floatPtr)
                },
                "Wave701 static read-back: multiplies two observed 4x4 float matrices into matrix4x4_out, handles the right-matrix alias case in-place, and copies the right matrix through a 16-dword scratch buffer when both inputs alias the destination. Static metadata only; exact row/column convention, transform handedness, full aliasing contract, dispatch-table ABI, and runtime math correctness remain unproven.",
                signatureTags("texture-math", "matrix4x4", "alias-safe", "dispatch-slot")
            ),
            new Spec(
                "0x005962b3",
                "CDXTexture__MultiplyMatrix4x4_Safe",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("matrix4x4_out", floatPtr),
                    param("left_matrix4x4", floatPtr),
                    param("right_matrix4x4", floatPtr)
                },
                "Wave701 static read-back: multiplies two observed 4x4 float matrices, routes the destination through a 16-dword scratch buffer when matrix4x4_out aliases either input, and copies the scratch result back after the four-row multiply. Static metadata only; exact row/column convention, transform handedness, full aliasing contract, dispatch-table ABI, and runtime math correctness remain unproven.",
                signatureTags("texture-math", "matrix4x4", "alias-safe", "dispatch-slot")
            ),
            new Spec(
                "0x00596341",
                "CFastVB__InitMathDispatchTable",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] { param("math_dispatch_table", voidPtr) },
                "Wave701 static read-back: seeds the observed math dispatch table with fixed helper labels and function pointers, including CDXTexture__MultiplyMatrix4x4_InPlaceSafe at +0x0c, CDXTexture__MultiplyMatrix4x4_Safe at +0x10, and CDXTexture__NormalizeVec3Fast at +0x1c, while mirroring the LAB_00596028 pointer at +0x88. Static metadata only; exact table schema, CPU feature replacement behavior, non-exported slot identities, and runtime dispatch behavior remain unproven.",
                signatureTags("texture-math", "dispatch-table", "matrix4x4", "vec3-normalize")
            ),
            new Spec(
                "0x00596386",
                "CDXTexture__UnpackRgb565ToRgbaFloat",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] { param("rgb565_word", uintType) },
                "Wave701 static read-back: expands the visible rgb565_word into normalized float RGBA lanes using 5-bit red/blue and 6-bit green scale constants, writes alpha 1.0, and stores the output through a hidden EAX float4 pointer that is not represented in the saved signature. Static metadata only; exact hidden-register ABI, output ownership, color-space convention, and runtime texel fidelity remain unproven.",
                signatureTags("texture-codec", "rgb565", "float4", "hidden-eax-output")
            ),
            new Spec(
                "0x005963d2",
                "CDXTexture__NormalizeColorBlockByAlpha",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("rgba_float_block16", voidPtr) },
                "Wave701 static read-back: walks sixteen float4 RGBA entries, zeroes RGB when alpha is 0.0, divides RGB by alpha when alpha is below 1.0, clamps each normalized RGB lane to 1.0 when the original lane is at least alpha, and returns 0. Static metadata only; exact block ownership, color-space convention, alpha policy, caller contract, and runtime texture fidelity remain unproven.",
                signatureTags("texture-codec", "rgba-float-block", "alpha-normalize", "dxt-prep")
            ),
            new Spec(
                "0x00596450",
                "CTexture__PremultiplyAlphaBlock16",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("premultiplied_rgba_out", voidPtr) },
                "Wave701 static read-back: copies sixteen hidden-EAX source float4 RGBA entries into premultiplied_rgba_out, multiplies RGB lanes by source alpha, preserves alpha, and returns 0. The source block pointer is hidden in EAX and is not represented in the saved signature. Static metadata only; exact hidden-register ABI, source/destination ownership, color-space convention, and runtime texture fidelity remain unproven.",
                signatureTags("texture-codec", "rgba-float-block", "premultiply-alpha", "hidden-eax-input", "dxt-prep")
            ),
            new Spec(
                "0x00596480",
                "CFastVB__PackClampedRgbToR5G6B5",
                "__fastcall",
                uintType,
                new ParameterImpl[] { param("rgb_float_triplet", voidPtr) },
                "Wave701 static read-back: clamps the first three float channels at rgb_float_triplet into 0.0..1.0, rounds red/blue through the 5-bit scale constant and green through the 6-bit scale constant, and packs the result into an RGB565 word. Static metadata only; exact rounding-mode control-word side effect, color-space convention, input stride, and runtime texel fidelity remain unproven.",
                signatureTags("texture-codec", "rgb565", "pack", "dxt-endpoint")
            ),
            new Spec(
                "0x00596589",
                "CFastVB__SolveScalarEndpointPairFromSamples",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("endpoint_min_out", floatPtr),
                    param("endpoint_max_out", floatPtr),
                    param("scalar_samples16", floatPtr)
                },
                "Wave701 static read-back: scans sixteen scalar_samples16 values, chooses min/max candidates with special handling for the observed six-endpoint mode, builds interpolation weights from tables at DAT_005eefe4/DAT_005ef01c, iteratively refines endpoint_min_out and endpoint_max_out for up to eight passes, clamps both endpoints to 0.0..1.0, and uses hidden EBX as the endpoint-count/mode input. Static metadata only; exact hidden-register ABI, interpolation table identity, error metric, scalar source semantics, and runtime compression quality remain unproven.",
                signatureTags("texture-codec", "endpoint-solver", "scalar-block", "hidden-ebx-mode")
            ),
            new Spec(
                "0x005968a4",
                "CFastVB__SolveVectorEndpointPairFromSamples",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("endpoint_min_rgb_out", floatPtr),
                    param("endpoint_max_rgb_out", floatPtr),
                    param("rgba_samples16", floatPtr),
                    param("endpoint_count", intType)
                },
                "Wave701 static read-back: scans sixteen four-float sample rows, selects an RGB bounding axis, chooses endpoint ordering from variance buckets, optionally refines RGB endpoints with interpolation tables for endpoint_count 3 or 4, and writes the resulting RGB endpoint pair. Static metadata only; exact sample stride/layout, DXT mode identity, vector error metric, interpolation table provenance, and runtime compression quality remain unproven.",
                signatureTags("texture-codec", "endpoint-solver", "rgb-vector-block", "dxt-endpoint")
            ),
            new Spec(
                "0x00596e23",
                "CFastVB__QuantizeScalarBlockIndices",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("dxt_color_block_out", voidPtr),
                    param("alpha_mode_weight", floatType)
                },
                "Wave701 static read-back: quantizes a hidden-EAX sixteen-pixel float RGBA block into dxt_color_block_out, chooses the observed three- or four-color mode from alpha_mode_weight and alpha-lane checks, distributes quantization residuals across the 4x4 block, calls CFastVB__SolveVectorEndpointPairFromSamples, packs RGB565 endpoints, unpacks the chosen endpoints for selector fitting, and writes the 32-bit selector mask before returning 0. Static metadata only; exact hidden-EAX input ABI, output DXT block schema, alpha-mode semantics, residual diffusion policy, and runtime compression quality remain unproven.",
                signatureTags("texture-codec", "dxt-quantize", "rgb565", "selector-indices", "hidden-eax-input", "tranche-tail")
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

        println("ApplyTextureMathDxtPreludeWave701 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
