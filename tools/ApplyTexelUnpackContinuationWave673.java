//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyTexelUnpackContinuationWave673 extends GhidraScript {
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] baseTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texel-unpack-continuation-wave673",
            "wave673-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
        }, extras);
    }

    private String[] profileTags(String... extras) {
        return concat(baseTags(
            "texel-unpack-profile",
            "format-factory-case",
            "vtable-binding"
        ), extras);
    }

    private String[] unpackTags(String... extras) {
        return concat(baseTags(
            "texel-unpacker",
            "float4-output",
            "source-pointer-fields",
            "keycolor-zero-gate",
            "postprocess-gate"
        ), extras);
    }

    private String[] dtorTags(String... extras) {
        return concat(baseTags(
            "texel-unpack-profile",
            "scalar-deleting-dtor",
            "optional-free"
        ), extras);
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

    private ParameterImpl[] ctorParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("format_descriptor", voidPtr)
        };
    }

    private ParameterImpl[] dtorParams(DataType voidPtr, DataType byteType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("flags", byteType)
        };
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

    private Spec profileSpec(String address, String name, DataType returnType, ParameterImpl[] params,
            String formatCase, String vtableAddress, String[] tags) {
        return new Spec(
            address,
            name,
            "__thiscall",
            returnType,
            params,
            "Wave673 static read-back: texel-unpack profile constructor thunk reached from CFastVB__CreateTexelUnpackProfileByFormat case " + formatCase +
                " after a 0x1074 allocation; it calls CFastVB__TexelUnpackProfile__ctorFromDescriptor(format_descriptor), binds vtable " + vtableAddress +
                ", and returns this with RET 0x4. Static metadata only; exact profile ABI, descriptor layout, callback-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
            tags
        );
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        ParameterImpl[] ctorParams = ctorParams(voidPtr);
        ParameterImpl[] unpackParams = unpackParams(uintType, intType, voidPtr, floatPtr);

        Spec[] specs = new Spec[] {
            profileSpec(
                "0x0058577f",
                "CFastVB__TexelUnpackProfile_005e9f3c__ctor",
                voidPtr,
                ctorParams,
                "0x14",
                "0x005e9f3c",
                profileTags("case-0x14", "vtable-005e9f3c")
            ),
            new Spec(
                "0x0058579b",
                "CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: 4-4-4 alpha-one unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two bytes per texel, writes R from byte1 low nibble, G from byte0 high nibble, B from byte0 low nibble, and A=1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, format-table contract, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("ctexture", "bits444", "alpha-one", "nibble-lanes", "two-byte-source")
            ),
            profileSpec(
                "0x0058584f",
                "CFastVB__TexelUnpackProfile_005e9f4c__ctor",
                voidPtr,
                ctorParams,
                "0x15",
                "0x005e9f4c",
                profileTags("case-0x15", "vtable-005e9f4c")
            ),
            new Spec(
                "0x0058586b",
                "CTexture__UnpackTexels_PaletteIndexA8ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: palette-index plus A8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two bytes per texel, copies a vec4 palette entry from this+0x38 indexed by byte0, then overwrites alpha from byte1 using the observed 8-bit scale. It then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, palette layout, format-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("ctexture", "palette-index", "alpha-byte", "two-byte-source", "palette-this-38")
            ),
            profileSpec(
                "0x00585908",
                "CFastVB__InitTexelUnpackVTable_005e9f5c",
                voidPtr,
                ctorParams,
                "0x16",
                "0x005e9f5c",
                profileTags("case-0x16", "vtable-005e9f5c", "current-name-retained")
            ),
            profileSpec(
                "0x00585924",
                "CFastVB__InitTexelUnpackVTable_005e9f6c",
                voidPtr,
                ctorParams,
                "0x17",
                "0x005e9f6c",
                profileTags("case-0x17", "vtable-005e9f6c", "current-name-retained")
            ),
            profileSpec(
                "0x005859bc",
                "CFastVB__InitTexelUnpackVTable_005e9f7c",
                voidPtr,
                ctorParams,
                "0x18",
                "0x005e9f7c",
                profileTags("case-0x18", "vtable-005e9f7c", "current-name-retained")
            ),
            new Spec(
                "0x005859d8",
                "CFastVB__UnpackTexels_L8ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: L8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one byte per texel, copies byte-scaled luminance into RGB, and writes A=1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, luminance contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cfastvb", "l8", "luminance", "alpha-one", "byte-source")
            ),
            profileSpec(
                "0x00585a5f",
                "CFastVB__TexelUnpackProfile_005e9f8c__ctor",
                voidPtr,
                ctorParams,
                "0x19",
                "0x005e9f8c",
                profileTags("case-0x19", "vtable-005e9f8c")
            ),
            new Spec(
                "0x00585a7b",
                "CFastVB__UnpackTexels_L8A8ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: L8A8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two bytes per texel, copies byte0-scaled luminance into RGB and byte1-scaled alpha into A, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, luminance/alpha contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cfastvb", "l8a8", "luminance", "alpha-byte", "two-byte-source")
            ),
            profileSpec(
                "0x00585b19",
                "CFastVB__TexelUnpackProfile_005e9f9c__ctor",
                voidPtr,
                ctorParams,
                "0x1a",
                "0x005e9f9c",
                profileTags("case-0x1a", "vtable-005e9f9c")
            ),
            new Spec(
                "0x00585b35",
                "CFastVB__UnpackTexels_A4L4ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: A4L4 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one byte per texel, copies the low nibble as luminance into RGB and the high nibble as alpha into A, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, nibble lane contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cfastvb", "a4l4", "luminance", "alpha-nibble", "byte-source", "nibble-lanes")
            ),
            new Spec(
                "0x00585bd3",
                "CFastVB__TexelUnpackProfile_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                dtorParams(voidPtr, byteType),
                "Wave673 static read-back: texel-unpack profile scalar-deleting destructor wrapper calls CFastVB__TexelUnpackProfile__dtor(this), frees this through OID__FreeObject_Callback when flags bit 0 is set, and returns this. Data xrefs show this wrapper shared by many adjacent texel-unpack profile vtables/descriptors. Static metadata only; exact allocator ownership, full vtable coverage, runtime lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                dtorTags("shared-profile-dtor", "flags-bit0")
            ),
            profileSpec(
                "0x00585bef",
                "CFastVB__InitTexelUnpackVTable_005e9fac",
                voidPtr,
                ctorParams,
                "0x1b",
                "0x005e9fac",
                profileTags("case-0x1b", "vtable-005e9fac", "current-name-retained")
            ),
            new Spec(
                "0x00585c0b",
                "CFastVB__UnpackTexels_L16ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: L16 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one 16-bit word per texel, copies 16-bit-scaled luminance into RGB, and writes A=1.0 to destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact profile ABI, luminance contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cfastvb", "l16", "luminance", "alpha-one", "sixteen-bit-source")
            ),
            profileSpec(
                "0x00585c94",
                "CFastVB__InitTexelUnpackVTable_005e9fbc",
                voidPtr,
                ctorParams,
                "0x1c",
                "0x005e9fbc",
                profileTags("case-0x1c", "vtable-005e9fbc", "current-name-retained")
            ),
            new Spec(
                "0x00585cb0",
                "CTexture__UnpackTexels_Signed8_8_ToFloat4_RG",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: signed 8-8 RG unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two bytes per texel, sign-scales byte0/byte1 into R/G with the observed -128 adjustment, fills Z=1.0 and A=1.0, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact signed-normal format contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("ctexture", "signed8-8", "rg", "signed-normal", "za-one", "two-byte-source")
            ),
            profileSpec(
                "0x00585d6b",
                "CFastVB__TexelUnpackProfile_005e9fd0__ctor",
                voidPtr,
                ctorParams,
                "0x1d",
                "0x005e9fd0",
                profileTags("case-0x1d", "vtable-005e9fd0")
            ),
            profileSpec(
                "0x00585d87",
                "CFastVB__TexelUnpackProfile_005e9fe0__ctor",
                voidPtr,
                ctorParams,
                "0x1e",
                "0x005e9fe0",
                profileTags("case-0x1e", "vtable-005e9fe0")
            ),
            new Spec(
                "0x00585da3",
                "CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: signed 5-5 plus A6 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one 16-bit word per texel, sign-extends/scales the low and next 5-bit lanes into R/G with the observed -16 adjustment, fills Z=1.0, and scales the high 6 bits into alpha, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact signed-normal/alpha contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cdxtexture", "signed5-5-a6", "signed-normal", "alpha-six-bit", "sixteen-bit-source", "z-one")
            ),
            profileSpec(
                "0x00585e83",
                "CFastVB__TexelUnpackProfile_005e9ff0__ctor",
                voidPtr,
                ctorParams,
                "0x1f",
                "0x005e9ff0",
                profileTags("case-0x1f", "vtable-005e9ff0")
            ),
            new Spec(
                "0x00585e9f",
                "CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: signed 8-8 plus A8 RG unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances four bytes per texel, sign-scales byte0/byte1 into R/G with the observed -128 adjustment, fills Z=1.0, and scales byte2 into alpha; byte3 remains unused in the current decompile. It then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact source-record contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cdxtexture", "signed8-8-a8", "rg", "signed-normal", "alpha-byte", "four-byte-source")
            ),
            profileSpec(
                "0x00585f6b",
                "CFastVB__TexelUnpackProfile_005ea000__ctor",
                voidPtr,
                ctorParams,
                "0x20",
                "0x005ea000",
                profileTags("case-0x20", "vtable-005ea000")
            ),
            profileSpec(
                "0x00585f87",
                "CFastVB__TexelUnpackProfile_005ea010__ctor",
                voidPtr,
                ctorParams,
                "0x21",
                "0x005ea010",
                profileTags("case-0x21", "vtable-005ea010")
            ),
            new Spec(
                "0x00585fa3",
                "CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave673 static read-back: signed 8-8-8-8 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one dword per texel, sign-scales four byte lanes into RGBA with the observed -128 adjustment, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10). Static metadata only; exact signed-normal format contract, lane-order enum contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                unpackTags("cfastvb", "signed8-8-8-8", "signed-normal", "four-byte-source", "rgba")
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
            throw new IllegalStateException("Wave673 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
