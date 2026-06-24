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

public class ApplyTexelUnpackTailWave674 extends GhidraScript {
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
            "texel-unpack-tail-wave674",
            "wave674-readback-verified",
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
            String factoryContext, String vtableAddress, String[] tags) {
        return new Spec(
            address,
            name,
            "__thiscall",
            returnType,
            params,
            "Wave674 static read-back: texel-unpack profile constructor thunk reached from CFastVB__CreateTexelUnpackProfileByFormat " + factoryContext +
                " after a 0x1074 allocation; it calls CFastVB__TexelUnpackProfile__ctorFromDescriptor(format_descriptor), binds vtable " + vtableAddress +
                ", and returns this with RET 0x4. Static metadata only; exact profile ABI, descriptor layout, callback-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
            tags
        );
    }

    private Spec unpackSpec(String address, String name, DataType returnType, ParameterImpl[] params,
            String detail, String[] tags) {
        return new Spec(
            address,
            name,
            "__thiscall",
            returnType,
            params,
            "Wave674 static read-back: " + detail +
                " Static metadata only; exact profile ABI, format-table contract, callback-table contract, runtime texture output, BEA patching, and rebuild parity remain unproven.",
            tags
        );
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
        ParameterImpl[] ctorParams = ctorParams(voidPtr);
        ParameterImpl[] unpackParams = unpackParams(uintType, intType, voidPtr, floatPtr);

        Spec[] specs = new Spec[] {
            profileSpec(
                "0x0058609e",
                "CFastVB__TexelUnpackProfile_005ea020__ctor",
                voidPtr,
                ctorParams,
                "case 0x22 / call-site 0x00588098",
                "0x005ea020",
                profileTags("case-0x22", "callsite-00588098", "vtable-005ea020")
            ),
            unpackSpec(
                "0x005860ba",
                "CTexture__UnpackTexels_Signed16_16_ToFloat4_RG",
                voidType,
                unpackParams,
                "signed 16-16 RG unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two 16-bit words per texel, sign-scales R/G with the observed -0x8000 correction, fills Z=1.0 and A=1.0, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10).",
                unpackTags("ctexture", "signed16-16", "rg", "signed-normal", "za-one", "two-word-source")
            ),
            profileSpec(
                "0x0058617c",
                "CFastVB__InitTexelUnpackVTable_005ea034",
                voidPtr,
                ctorParams,
                "case 0x23 / call-site 0x005880b8",
                "0x005ea034",
                profileTags("case-0x23", "callsite-005880b8", "vtable-005ea034", "current-name-retained")
            ),
            profileSpec(
                "0x00586198",
                "CFastVB__TexelUnpackProfile_005ea044__ctor",
                voidPtr,
                ctorParams,
                "case 0x24 / call-site 0x005880d8",
                "0x005ea044",
                profileTags("case-0x24", "callsite-005880d8", "vtable-005ea044")
            ),
            unpackSpec(
                "0x005861b4",
                "CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4",
                voidType,
                unpackParams,
                "signed 2-10-10-10 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one dword per texel, sign-extends/scales three 10-bit lanes with the observed -0x200 correction, scales the top 2-bit lane into alpha, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10).",
                unpackTags("cdxtexture", "signed2-10-10-10", "signed-normal", "alpha-two-bit", "dword-source", "rgba")
            ),
            profileSpec(
                "0x005862cd",
                "CFastVB__TexelUnpackProfile_005ea058__ctor",
                voidPtr,
                ctorParams,
                "case 0x28 / call-site 0x005880f8",
                "0x005ea058",
                profileTags("case-0x28", "callsite-005880f8", "vtable-005ea058")
            ),
            profileSpec(
                "0x005862e9",
                "CFastVB__InitTexelUnpackVTable_005ea068",
                voidPtr,
                ctorParams,
                "case 0x29 / call-site 0x00588118",
                "0x005ea068",
                profileTags("case-0x29", "callsite-00588118", "vtable-005ea068", "current-name-retained")
            ),
            unpackSpec(
                "0x00586305",
                "CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4",
                voidType,
                unpackParams,
                "signed 16-16-16-16 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances four 16-bit words per texel, sign-scales RGBA with the observed -0x8000 correction, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10).",
                unpackTags("cdxtexture", "signed16-16-16-16", "signed-normal", "four-word-source", "rgba")
            ),
            profileSpec(
                "0x0058641c",
                "CFastVB__TexelUnpackProfile_005ea078__ctor",
                voidPtr,
                ctorParams,
                "call-site 0x00588138 in the adjacent post-0x29 factory block",
                "0x005ea078",
                profileTags("callsite-00588138", "vtable-005ea078", "factory-sequence-after-case-0x29")
            ),
            unpackSpec(
                "0x00586438",
                "CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ",
                voidType,
                unpackParams,
                "signed 8-8 normal-map unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two bytes per texel, sign-scales X/Y with the observed -0x80 correction, reconstructs Z with sqrt(max(0, 1 - x*x - y*y)), writes A=1.0, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10).",
                unpackTags("ctexture", "normalxy", "signed8-8", "reconstruct-z", "alpha-one", "two-byte-source")
            ),
            profileSpec(
                "0x00586519",
                "CFastVB__TexelUnpackProfile_005ea088__ctor",
                voidPtr,
                ctorParams,
                "case 0x33 / call-site 0x005881ea",
                "0x005ea088",
                profileTags("case-0x33", "callsite-005881ea", "vtable-005ea088")
            ),
            profileSpec(
                "0x00586535",
                "CFastVB__TexelUnpackProfile_005ea098__ctor",
                voidPtr,
                ctorParams,
                "case 0x34 / call-site 0x005881ca",
                "0x005ea098",
                profileTags("case-0x34", "callsite-005881ca", "vtable-005ea098")
            ),
            profileSpec(
                "0x00586551",
                "CFastVB__TexelUnpackProfile_005ea0a8__ctor",
                voidPtr,
                ctorParams,
                "case 0x51 / call-site 0x005882c0",
                "0x005ea0a8",
                profileTags("case-0x51", "callsite-005882c0", "vtable-005ea0a8")
            ),
            profileSpec(
                "0x005865ed",
                "CFastVB__TexelUnpackProfile_005ea0b8__ctor",
                voidPtr,
                ctorParams,
                "case 0x3c / call-site 0x005881aa",
                "0x005ea0b8",
                profileTags("case-0x3c", "callsite-005881aa", "vtable-005ea0b8")
            ),
            unpackSpec(
                "0x00586609",
                "CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne",
                voidType,
                unpackParams,
                "callback-per-texel stride-2 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances two source bytes per texel through CDXTexture__UnpackTexels_DispatchIndirect_00575a65, then forces G/B/A to 1.0 before the usual key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10) gates.",
                unpackTags("cdxtexture", "callback-dispatch", "stride2-source", "gba-one")
            ),
            profileSpec(
                "0x0058669a",
                "CFastVB__InitTexelUnpackVTable_005ea0c8",
                voidPtr,
                ctorParams,
                "case 0x3d / call-site 0x0058818a",
                "0x005ea0c8",
                profileTags("case-0x3d", "callsite-0058818a", "vtable-005ea0c8", "current-name-retained")
            ),
            profileSpec(
                "0x005866b6",
                "CFastVB__InitTexelUnpackVTable_005ea0d8",
                voidPtr,
                ctorParams,
                "case 0x3e / call-site 0x0058820a",
                "0x005ea0d8",
                profileTags("case-0x3e", "callsite-0058820a", "vtable-005ea0d8", "current-name-retained")
            ),
            unpackSpec(
                "0x005866d2",
                "CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne",
                voidType,
                unpackParams,
                "callback-per-texel stride-4 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one dword per texel through CDXTexture__UnpackTexels_DispatchIndirect_00575a65, then forces Z/A to 1.0 before the usual key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10) gates.",
                unpackTags("cfastvb", "callback-dispatch", "stride4-source", "za-one")
            ),
            profileSpec(
                "0x0058675f",
                "CFastVB__InitTexelUnpackVTable_005ea0e8",
                voidPtr,
                ctorParams,
                "case 0x3f / call-site 0x005882a0",
                "0x005ea0e8",
                profileTags("case-0x3f", "callsite-005882a0", "vtable-005ea0e8", "current-name-retained")
            ),
            unpackSpec(
                "0x0058677b",
                "CDXTexture__UnpackTexels_CallbackSingleTexel",
                voidType,
                unpackParams,
                "single-callback unpacker forwards one texel through CDXTexture__UnpackTexels_DispatchIndirect_00575a65, then applies the same key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10) gates to destination_vec4_array.",
                unpackTags("cdxtexture", "callback-dispatch", "single-texel")
            ),
            profileSpec(
                "0x005867d2",
                "CFastVB__TexelUnpackProfile_005ea0f8__ctor",
                voidPtr,
                ctorParams,
                "case 0x40 / call-site 0x00588280",
                "0x005ea0f8",
                profileTags("case-0x40", "callsite-00588280", "vtable-005ea0f8")
            ),
            unpackSpec(
                "0x0058686f",
                "CTexture__UnpackTexels_CopyRaw128",
                voidType,
                unpackParams,
                "raw 128-bit copy unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, copies 16 bytes per texel directly into destination_vec4_array, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10).",
                unpackTags("ctexture", "copy-raw128", "raw-copy", "sixteen-byte-source")
            ),
            unpackSpec(
                "0x005868d1",
                "CFastVB__UnpackTexels_L16A16_ToFloat4",
                voidType,
                unpackParams,
                "L16A16 unpacker computes the packed-source pointer from +0x1058/+0x105c/+0x20 using source_x/source_y and count +0x1060, advances one dword per texel, copies 16-bit luminance into RGB and 16-bit alpha into A, then conditionally runs key-color zeroing (+0x18) and post-process/gamma-or-square (+0x10).",
                unpackTags("cfastvb", "l16a16", "luminance", "alpha-sixteen-bit", "dword-source")
            ),
            profileSpec(
                "0x00586978",
                "CFastVB__TexelUnpackProfile_005ea108__ctor",
                voidPtr,
                ctorParams,
                "case 0x43 / call-site 0x00588260",
                "0x005ea108",
                profileTags("case-0x43", "callsite-00588260", "vtable-005ea108")
            ),
            profileSpec(
                "0x00586994",
                "CFastVB__InitTexelUnpackVTable_005ea118",
                voidPtr,
                ctorParams,
                "case 0x6e / call-site 0x00588343",
                "0x005ea118",
                profileTags("case-0x6e", "callsite-00588343", "vtable-005ea118", "current-name-retained")
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
            throw new IllegalStateException("Wave674 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
