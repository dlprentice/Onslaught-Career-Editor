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

public class ApplyTexelCallbackRawPackersWave671 extends GhidraScript {
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
            "texel-callback-raw-packers-wave671",
            "wave671-readback-verified",
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

    private ParameterImpl[] vec4PackerParams(DataType uintType, DataType intType, DataType floatPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", new PointerDataType(VoidDataType.dataType)),
            param("output_x", uintType),
            param("output_y", uintType),
            param("source_vec4_array", floatPtr),
            param("unused_context", intType)
        };
    }

    private ParameterImpl[] rawPackerParams(DataType uintType, DataType intType, DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", new PointerDataType(VoidDataType.dataType)),
            param("output_x", uintType),
            param("output_y", uintType),
            param("source_texel_records", voidPtr),
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
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00584724",
                "CDXTexture__PackTexels_CallbackPerTexel_RepeatA",
                "__thiscall",
                voidType,
                vec4PackerParams(uintType, intType, floatPtr),
                "Wave671 static read-back: repeat-A callback wrapper optionally normalizes source vec4 records, computes the output pointer from +0x1058/+0x105c/+0x20 and count +0x1060, then loops through texels calling observed indirect helper 0x005759c3 with mode selector 1, source stride +0x10, and output stride +4. Static metadata only; exact callback ABI, selector contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "callback-dispatch", "repeat-a", "indirect-helper", "mode-1")
            ),
            new Spec(
                "0x00584786",
                "CDXTexture__PackTexels_CallbackPerTexel_RepeatB",
                "__thiscall",
                voidType,
                vec4PackerParams(uintType, intType, floatPtr),
                "Wave671 static read-back: repeat-B callback wrapper optionally normalizes source vec4 records, computes the output pointer from +0x1058/+0x105c/+0x20 and count +0x1060, then loops through texels calling observed indirect helper 0x005759c3 with mode selector 2, source stride +0x10, and output stride +4. Static metadata only; exact callback ABI, selector contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "callback-dispatch", "repeat-b", "indirect-helper", "mode-2")
            ),
            new Spec(
                "0x005847e9",
                "CDXTexture__PackTexels_CallbackPerTexel_Once",
                "__thiscall",
                voidType,
                vec4PackerParams(uintType, intType, floatPtr),
                "Wave671 static read-back: single-call callback wrapper optionally normalizes source vec4 records, computes the output pointer from +0x1058/+0x105c/+0x20 and count +0x1060, then pushes byte count count*4, source pointer, output pointer, and calls observed indirect helper 0x005759c3 once. Static metadata only; exact callback ABI, byte-count contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "callback-dispatch", "single-call", "indirect-helper", "byte-count")
            ),
            new Spec(
                "0x00584831",
                "CDXTexture__PackTexels_CopyRaw32",
                "__thiscall",
                voidType,
                rawPackerParams(uintType, intType, voidPtr),
                "Wave671 static read-back: raw 32-bit copy packer optionally normalizes source records, computes the output pointer from +0x1058/+0x105c/+0x20 and count +0x1060, then copies the first 4 bytes from each 16-byte source record while advancing output by +4 and source by +0x10. Static metadata only; exact source-record contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "raw-copy", "copy-raw32", "dword-output")
            ),
            new Spec(
                "0x00584886",
                "CDXTexture__PackTexels_CopyRaw64",
                "__thiscall",
                voidType,
                rawPackerParams(uintType, intType, voidPtr),
                "Wave671 static read-back: raw 64-bit copy packer optionally normalizes source records, computes the output pointer from +0x1058/+0x105c/+0x20 and count +0x1060, then copies the first 8 bytes from each 16-byte source record while advancing output by +8 and source by +0x10. Static metadata only; exact source-record contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "raw-copy", "copy-raw64", "qword-output")
            ),
            new Spec(
                "0x005848e3",
                "CDXTexture__PackTexels_CopyRaw128",
                "__thiscall",
                voidType,
                rawPackerParams(uintType, intType, voidPtr),
                "Wave671 static read-back: raw 128-bit copy packer optionally normalizes source records, computes the output pointer from +0x1058/+0x105c/+0x20 and count +0x1060, then copies count*16 bytes from the source record stream to the output with MOVSD.REP/tail-byte copy. Static metadata only; exact source-record contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "raw-copy", "copy-raw128", "vec4-output")
            ),
            new Spec(
                "0x00584936",
                "CDXTexture__PackTexels_NoDither_A16L16",
                "__thiscall",
                voidType,
                vec4PackerParams(uintType, intType, floatPtr),
                "Wave671 static read-back: currently named no-dither A16L16 packer optionally runs domain conversion and normalization, reads the shared +0x34 dither-table term in the current decompile, then writes a 32-bit A16L16-style texel with high 16 bits from source +0xc and low 16 bits from weighted RGB luminance constants. Static metadata only; exact no-dither naming rationale, luminance/alpha contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "texel-packer", "no-dither-named", "dither-term-observed", "a16l16", "dword-output", "luminance")
            ),
            new Spec(
                "0x00584a4c",
                "CTexture__PackTexels_NoDither_Bits16_16_16",
                "__thiscall",
                voidType,
                vec4PackerParams(uintType, intType, floatPtr),
                "Wave671 static read-back: currently named no-dither 16-16-16 packer optionally runs domain conversion and normalization, reads the shared +0x34 dither-table term in the current decompile, then writes three 16-bit words per texel from observed source lanes +8, +4, and +0. Static metadata only; exact no-dither naming rationale, lane-order contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "texel-packer", "no-dither-named", "dither-term-observed", "bits16-16-16", "three-word-output")
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
            throw new IllegalStateException("Wave671 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
