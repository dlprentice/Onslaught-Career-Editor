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

public class ApplyTexelUnpackHeadWave672 extends GhidraScript {
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
            "texel-unpack-head-wave672",
            "wave672-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened",
            "texel-unpacker",
            "float4-output",
            "source-pointer-fields",
            "keycolor-zero-gate",
            "postprocess-gate"
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

    private ParameterImpl[] unpackParams(DataType uintType, DataType intType, DataType voidPtr, DataType floatPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("source_x", uintType),
            param("source_y", uintType),
            param("destination_vec4_array", floatPtr),
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
        ParameterImpl[] params = unpackParams(uintType, intType, voidPtr, floatPtr);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00584b5f",
                "CTexture__UnpackTexels_Bgr8ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: BGR8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y, uses +0x106c as the byte span, writes R/G/B from bytes 2/1/0 and alpha 1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "bgr8", "alpha-one", "byte-span-106c", "three-byte-source-stride")
            ),
            new Spec(
                "0x00584c04",
                "CTexture__UnpackTexels_Bgra8ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: BGRA8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes R/G/B/A from bytes 2/1/0/3 scaled by the observed 8-bit factor to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "bgra8", "eight-bit-scale", "four-byte-source-stride")
            ),
            new Spec(
                "0x00584cc3",
                "CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: current-name BGR8 alpha-one unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances through 4-byte source records in the retail decompile, writes R/G/B from bytes 2/1/0 and alpha 1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, current-name/stride rationale, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("ctexture", "bgr8", "alpha-one", "four-byte-source-stride", "current-name-retained")
            ),
            new Spec(
                "0x00584d78",
                "CFastVB__UnpackTexels_Bits565ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: RGB565 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands 5/6/5-bit lanes to RGB with alpha 1.0 in destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "rgb565", "bits565", "alpha-one", "sixteen-bit-source")
            ),
            new Spec(
                "0x00584e32",
                "CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 5-5-5 alpha-one unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands three 5-bit color lanes with alpha 1.0 in destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits555", "alpha-one", "sixteen-bit-source")
            ),
            new Spec(
                "0x00584ee9",
                "CFastVB__UnpackTexels_Bits1555ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 1-5-5-5 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands three 5-bit color lanes and the high-bit alpha lane to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits1555", "alpha-bit", "sixteen-bit-source")
            ),
            new Spec(
                "0x00584fae",
                "CFastVB__UnpackTexels_Bits4444ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 4-4-4-4 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands four 4-bit lanes to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits4444", "nibble-lanes", "sixteen-bit-source")
            ),
            new Spec(
                "0x00585072",
                "CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 2-10-10-10 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes R/G/B from low/mid/high 10-bit fields and A from the top 2 bits to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits2-10-10-10", "ten-bit-lanes", "two-bit-alpha", "dword-source")
            ),
            new Spec(
                "0x00585161",
                "CFastVB__UnpackTexels_Bits8888ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 8-8-8-8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes four byte lanes from the 32-bit source word to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits8888", "eight-bit-scale", "dword-source")
            ),
            new Spec(
                "0x00585220",
                "CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 8-8-8 alpha-one unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes three byte lanes and alpha 1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits888", "alpha-one", "eight-bit-scale", "dword-source")
            ),
            new Spec(
                "0x005852d5",
                "CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 16-16 RG unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes two 16-bit lanes followed by B=1.0 and A=1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits16-16-rg", "alpha-one", "blue-one", "dword-source")
            ),
            new Spec(
                "0x00585380",
                "CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: alternate 2-10-10-10 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes R/G/B from high/mid/low 10-bit fields and A from the top 2 bits to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, alternate lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "bits2-10-10-10", "alternate-lane-order", "ten-bit-lanes", "two-bit-alpha", "dword-source")
            ),
            new Spec(
                "0x0058546f",
                "CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: current-owner 16-16-16-16 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, reads two dwords per texel, expands four 16-bit lanes to destination_vec4_array, and shows a decompiler __aullshr helper for the third lane. It then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, current owner/layout identity, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cmeshcollisionvolume", "current-owner-retained", "bits16-16-16-16", "qword-source", "aullshr-observed")
            ),
            new Spec(
                "0x00585576",
                "CDXTexture__UnpackTexels_Bits332ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 3-3-2 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands 3/3/2-bit RGB lanes with alpha 1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "bits332", "alpha-one", "byte-source")
            ),
            new Spec(
                "0x0058562d",
                "CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: A8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, writes zero RGB and byte-scaled alpha to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "a8-zero-rgb", "alpha-byte", "byte-source", "zero-rgb")
            ),
            new Spec(
                "0x005856b8",
                "CDXTexture__UnpackTexels_Bits332A8ToFloat4",
                "__thiscall",
                voidType,
                params,
                "Wave672 static read-back: 3-3-2 plus A8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, expands the first byte as 3/3/2 RGB and the second byte as alpha to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "bits332-a8", "alpha-byte", "two-byte-source")
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
            throw new IllegalStateException("Wave672 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
