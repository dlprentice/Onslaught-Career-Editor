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

public class ApplyTexelPackerContinuationWave670 extends GhidraScript {
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
            "texel-packer-continuation-wave670",
            "wave670-readback-verified",
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
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
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
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00583c8e",
                "CTexture__PackTexels_Dither_Bits8_8",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: dithered packer callback writes one 16-bit 8-8-style texel with two rounded 8-bit source lanes, using output pointer fields +0x1058/+0x105c/+0x20, count +0x1060, dither table +0x34, optional domain conversion +0x1050, and optional normalization +0x10. Static metadata only; exact lane contract, dither table provenance, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "dither-packer", "bits8-8", "word-output")
            ),
            new Spec(
                "0x00583d89",
                "CTexture__PackTexels_Dither_Bits5_5_5",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: dithered packer callback writes one 16-bit 5-5-5-style texel from three rounded source lanes, using the shared output pointer, count, conversion, normalization, and dither-table gates. Static metadata only; exact channel order, alpha policy, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "dither-packer", "bits5-5-5", "word-output")
            ),
            new Spec(
                "0x00583eb3",
                "CTexture__PackTexels_Dither_Bits8_8_8_Alt",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: alternate dithered 8-8-8-style packer callback writes one 32-bit store from three rounded source lanes, preserving the observed lane order and shared dither-table term. Static metadata only; exact channel-order enum contract, unused high byte policy, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "dither-packer", "bits8-8-8-alt", "dword-output")
            ),
            new Spec(
                "0x00583fe5",
                "CTexture__PackTexels_Dither_Bits8_8_8_8_Alt",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: alternate dithered 8-8-8-8-style packer callback writes one 32-bit texel from four rounded source lanes with the shared output pointer, count, conversion, normalization, and dither-table gates. Static metadata only; exact channel-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "dither-packer", "bits8-8-8-8-alt", "dword-output")
            ),
            new Spec(
                "0x00584144",
                "CFastVB__PackTexels_NoDither_Bits16_16",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: currently named no-dither 16-16 packer callback writes one 32-bit texel from two rounded 16-bit source lanes; the current decompile still reads the shared dither-table term at +0x34 before rounding. Static metadata only; exact no-dither naming rationale, channel contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "texel-packer", "no-dither-named", "dither-term-observed", "bits16-16", "dword-output")
            ),
            new Spec(
                "0x0058423f",
                "CFastVB__PackTexels_NoDither_Bits2_10_10_10",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: currently named no-dither 2-10-10-10 packer callback writes one 32-bit texel from four rounded source lanes; the current decompile still reads the shared dither-table term at +0x34 before rounding. Static metadata only; exact no-dither naming rationale, channel-order contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "texel-packer", "no-dither-named", "dither-term-observed", "bits2-10-10-10", "dword-output")
            ),
            new Spec(
                "0x0058439e",
                "CFastVB__PackTexels_NoDither_Bits16_16_16_16",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: currently named no-dither 16-16-16-16 packer callback writes two 32-bit words per texel from four rounded 16-bit source lanes; the current decompile still reads the shared dither-table term at +0x34 before rounding. Static metadata only; exact no-dither naming rationale, packed-lane contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "texel-packer", "no-dither-named", "dither-term-observed", "bits16-16-16-16", "qword-output")
            ),
            new Spec(
                "0x00584535",
                "CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: dithered 8-8-style packer callback calls the observed indirect helper 0x00575d99 to populate two local float lanes, then writes one 16-bit texel with the shared output pointer, count, conversion, and dither-table gates. Static metadata only; exact helper target, auxiliary lookup contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "dither-packer", "bits8-8-from-aux-lookup", "word-output", "indirect-helper")
            ),
            new Spec(
                "0x0058463a",
                "CTexture__PackTexels_Dither_L16_Alt",
                "__thiscall",
                voidType,
                texelPackerParams(uintType, intType, floatPtr),
                "Wave670 static read-back: alternate dithered luminance packer callback writes one 16-bit output from weighted RGB lanes using constants at 0x005e72dc/0x005e72e0/0x005e72e4, the observed 16-bit scale, and the shared dither table. Static metadata only; exact luminance contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "dither-packer", "l16-alt", "word-output", "luminance")
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
            throw new IllegalStateException("Wave670 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
