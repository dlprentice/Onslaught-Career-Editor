//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyDitherPackerHeadWave668 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] allowedExistingNames, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
            "dither-packer-head-wave668",
            "wave668-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
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
            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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
        }
        catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] texelPackerParams(DataType uintType, DataType intType, DataType floatPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", new PointerDataType(VoidDataType.dataType)),
            param("output_x", uintType),
            param("output_y", uintType),
            param("source_vec4_array", floatPtr),
            param("unused_context", intType)
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0058210e",
                "CTexture__PostProcessDecodedTexels_GammaOrSquare",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("texel_vec4_array", floatPtr),
                    param("unused_context", uintType)
                },
                "Wave668 static read-back: post-processes count-controlled decoded vec4 texels from texel_vec4_array using count +0x1060, mode +0x08, and gamma/square selector +0x14; modes 1/4 transform RGB lanes while other modes transform alpha only, either through CFastVB__LookupCurveFromSquaredInput or direct square. Static metadata only; exact gamma curve, profile ABI, runtime image-quality behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "texel-postprocess", "gamma-or-square", "vec4")
            ),
            new Spec(
                "0x00582244",
                "CFastVB__PackTexels_Dither_Bits8_8_8_BGR",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9f44 writes three bytes per output texel in B,G,R order using output pointer fields +0x1058/+0x105c/+0x20, count +0x1060, dither table +0x34, optional domain conversion +0x1050, and optional normalization +0x10. Static metadata only; exact format enum, color-space contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "bgr888", "byte-output")
            ),
            new Spec(
                "0x00582355",
                "CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9f54 writes one 32-bit ARGB8888-style texel from source vec4 lanes, with the same output stride/base, count, dither table, optional domain conversion, and optional normalization gates as the neighboring packers. Static metadata only; exact channel-order contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "argb8888", "dword-output")
            ),
            new Spec(
                "0x0058249e",
                "CFastVB__PackTexels_Dither_Bits8_8_8_RGB",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9f64 writes 24-bit RGB byte output by rounding source vec4 RGB lanes with the observed 8-bit scale constant and per-pixel dither term. Static metadata only; exact format enum, channel-order contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "rgb888", "byte-output")
            ),
            new Spec(
                "0x005825c3",
                "CFastVB__PackTexels_Dither_Bits5_6_5",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9f74 writes 16-bit RGB565 output by rounding RGB lanes with the observed 5/6/5 scale constants and packing them into one word. Static metadata only; exact format enum, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "rgb565", "word-output")
            ),
            new Spec(
                "0x005826e8",
                "CFastVB__PackTexels_Dither_Bits5_5_5",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9f84 writes 16-bit RGB555 output by rounding RGB lanes with the observed 5-bit scale constant and packing them into one word. Static metadata only; exact format enum, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "rgb555", "word-output")
            ),
            new Spec(
                "0x0058280d",
                "CFastVB__PackTexels_Dither_A1R5G5B5",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9f94 writes 16-bit A1R5G5B5-style output, deriving the one-bit alpha lane from the source alpha plus dither term and packing RGB with the observed 5-bit scale constant. Static metadata only; exact alpha threshold policy, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "a1r5g5b5", "word-output")
            ),
            new Spec(
                "0x00582950",
                "CFastVB__PackTexels_Dither_A4R4G4B4",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9fa4 writes 16-bit A4R4G4B4-style output by rounding alpha and RGB lanes with the observed 4-bit scale constant and packing four nibbles. Static metadata only; exact channel-order contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dither-packer", "a4r4g4b4", "word-output")
            ),
            new Spec(
                "0x00582a99",
                "CTexture__PackTexels_Dither_Bits332",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9fb4 writes one 8-bit 3-3-2 packed texel from RGB lanes using the observed 3-bit/2-bit scale constants plus dither table. Static metadata only; exact format enum, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "dither-packer", "bits332", "byte-output")
            ),
            new Spec(
                "0x00582bbe",
                "CTexture__PackTexels_Dither_Bits8",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9fc4 writes one 8-bit single-channel output from the observed source lane at +0x0c, using the shared output stride/base, count, dither table, optional domain conversion, and optional normalization gates. Static metadata only; exact channel meaning, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "dither-packer", "bits8", "byte-output")
            ),
            new Spec(
                "0x00582c8a",
                "CTexture__PackTexels_Dither_Bits565",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9fd8 writes 16-bit packed output with the observed 5/6/5-like scale mix and alpha/source-lane participation shown in decompile. Static metadata only; exact channel map, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "dither-packer", "bits565", "word-output")
            ),
            new Spec(
                "0x00582dd3",
                "CTexture__PackTexels_Dither_Bits444",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave668 static read-back: dithered packer callback at table slot 0x005e9fe8 writes 16-bit 4-4-4 packed output by rounding three source lanes with the observed 4-bit scale constant and packing nibbles. Static metadata only; exact format enum, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "dither-packer", "bits444", "word-output")
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
            throw new IllegalStateException("Wave668 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
