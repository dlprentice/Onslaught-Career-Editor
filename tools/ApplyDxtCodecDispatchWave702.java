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

public class ApplyDxtCodecDispatchWave702 extends GhidraScript {
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

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "dxt-codec-dispatch-wave702",
            "wave702-readback-verified",
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
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);
        println("ApplyDxtCodecDispatchWave702 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0059764a",
                "CDXTexture__DecodeDxt1ColorBlockToRgba",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("rgba_float_block16_out", floatPtr),
                    param("dxt1_color_block", voidPtr)
                },
                "Wave702 static read-back: decodes a DXT1 color block into sixteen RGBA float4 rows by unpacking two RGB565 endpoints through the hidden-EAX output helper, interpolating four-color or three-color/transparent palettes, and consuming the 32-bit two-bit selector mask. Static metadata only; exact DXT1 alpha policy, float layout contract, runtime texture fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt1", "rgb565", "decode", "tranche-head")
            ),
            new Spec(
                "0x0059778a",
                "CTexture__DecodeDxt3BlockToFloatRgba",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("rgba_float_block16_out", floatPtr),
                    param("dxt3_block", voidPtr)
                },
                "Wave702 static read-back: decodes the color half through CDXTexture__DecodeDxt1ColorBlockToRgba at block+8, then expands the two explicit 32-bit 4-bit-alpha rows into the alpha lane of sixteen RGBA float4 entries. Static metadata only; exact alpha scale constant, block ABI, runtime texture fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt3", "explicit-alpha", "decode")
            ),
            new Spec(
                "0x0059780d",
                "CTexture__DecodeDxt5BlockToFloatRgba",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("rgba_float_block16_out", floatPtr),
                    param("dxt5_block", voidPtr)
                },
                "Wave702 static read-back: decodes the color half through CDXTexture__DecodeDxt1ColorBlockToRgba at block+8, builds the six- or eight-entry alpha ladder from the first two endpoint bytes, and applies the two 24-bit three-bit-selector groups to the alpha lane. Static metadata only; exact selector ordering, alpha ladder semantics, runtime texture fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt5", "interpolated-alpha", "decode")
            ),
            new Spec(
                "0x00597949",
                "CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("dxt_color_block_out", voidPtr),
                    param("rgba_float_block16", floatPtr)
                },
                "Wave702 static read-back: copies sixteen RGBA float4 samples while error-diffusing the alpha lane across a 4x4 block, rounds corrected alpha samples, then calls CFastVB__QuantizeScalarBlockIndices with the observed tiny alpha-mode marker. Static metadata only; exact diffusion policy, hidden FPU-control side effects, output block ABI, runtime compression quality, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt5", "encode", "error-diffusion", "alpha-indices")
            ),
            new Spec(
                "0x00597a61",
                "CFastVB__PackScalarBlock_4BitEndpoints",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("dxt3_block_out", voidPtr),
                    param("rgba_float_block16", floatPtr)
                },
                "Wave702 static read-back: initializes an 8-byte explicit-alpha output field, error-diffuses sixteen source alpha samples into 4-bit packed nibbles, and then quantizes the color selector block at output+8. Static metadata only; exact DXT3 block ABI, diffusion policy, color/alpha coupling, runtime compression quality, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt3", "encode", "explicit-alpha", "selector-indices")
            ),
            new Spec(
                "0x00597b87",
                "CFastVB__PackScalarBlock_InterpolatedEndpoints",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("dxt5_block_out", voidPtr),
                    param("rgba_float_block16", floatPtr)
                },
                "Wave702 static read-back: quantizes alpha samples to byte-scaled values, detects all-opaque/all-transparent edge cases, solves scalar endpoints, writes DXT5 alpha endpoint bytes, builds six- or eight-entry selector remap tables, error-diffuses residuals, and packs two three-byte selector groups. Static metadata only; exact endpoint ordering, residual diffusion policy, runtime compression quality, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt5", "encode", "interpolated-alpha", "selector-indices")
            ),
            new Spec(
                "0x00598056",
                "CTexture__EncodeDxt3AlphaBlock",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("dxt3_block_out", voidPtr)
                },
                "Wave702 static read-back: prepares a stack RGBA float4 block through CTexture__PremultiplyAlphaBlock16 and, on non-negative status, forwards it to CFastVB__PackScalarBlock_4BitEndpoints for DXT3 alpha/color packing. Static metadata only; hidden source-block ABI, runtime compression quality, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt3", "encode", "premultiply-alpha")
            ),
            new Spec(
                "0x0059808a",
                "CTexture__EncodeDxt5AlphaBlock",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("dxt5_block_out", voidPtr)
                },
                "Wave702 static read-back: prepares a stack RGBA float4 block through CTexture__PremultiplyAlphaBlock16 and, on non-negative status, forwards it to CFastVB__PackScalarBlock_InterpolatedEndpoints for DXT5 alpha/color packing. Static metadata only; hidden source-block ABI, runtime compression quality, BEA patching, and rebuild parity remain unproven.",
                tags("dxt-codec", "dxt5", "encode", "premultiply-alpha")
            ),
            new Spec(
                "0x005980be",
                "CFastVB__InitDispatchTableVariant_005980be",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("math_dispatch_table", voidPtr)
                },
                "Wave702 static read-back: seeds a math dispatch-table variant with the scalar/base transform, normalize, matrix, cubic, quaternion, half-float, and batch helper pointers observed in the retail binary. Static metadata only; exact CPU mode identity, slot schema, runtime feature replacement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table", "math-dispatch", "cpu-feature", "variant-005980be")
            ),
            new Spec(
                "0x0059822c",
                "CFastVB__InitDispatchTableVariant_0059822c",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("math_dispatch_table", voidPtr)
                },
                "Wave702 static read-back: seeds an alternate math dispatch-table variant with alternate matrix/quaternion/batch helpers, packed-B adjugate support, and SIMD half-float conversion slots observed in the retail binary. Static metadata only; exact CPU mode identity, slot schema, runtime feature replacement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table", "math-dispatch", "cpu-feature", "variant-0059822c")
            ),
            new Spec(
                "0x00598474",
                "CFastVB__InitDispatchOpsFromFeatureFlags",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("math_dispatch_table", voidPtr)
                },
                "Wave702 static read-back: queries CFastVB__DetectCpuFeatureMask, conditionally replaces math dispatch-table slots for observed feature-mask bits 0x20/0x80/0x100/0x200/0x40, and installs packed/SIMD transform, quaternion, matrix, and batch helpers. Static metadata only; exact feature-bit names, slot schema, runtime CPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-table", "math-dispatch", "cpu-feature", "feature-mask", "tranche-tail")
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
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave702 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
