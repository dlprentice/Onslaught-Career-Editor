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

public class ApplyTexelCodecContinuationWave675 extends GhidraScript {
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
            "texel-codec-continuation-wave675",
            "wave675-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
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

    private ParameterImpl[] blockReadParams(DataType uintType, DataType intType, DataType voidPtr, DataType floatPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("block_x", uintType),
            param("block_y", uintType),
            param("destination_vec4_array", floatPtr),
            param("unused_context", intType)
        };
    }

    private ParameterImpl[] blockWriteParams(DataType uintType, DataType intType, DataType voidPtr, DataType floatPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("block_x", uintType),
            param("block_y", uintType),
            param("source_vec4_array", floatPtr),
            param("unused_context", intType)
        };
    }

    private ParameterImpl[] decodeParams(DataType uintType, DataType intType, DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("row_index", intType),
            param("column_index", uintType),
            param("decode_if_needed", uintType)
        };
    }

    private ParameterImpl[] flushParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("profile", voidPtr)
        };
    }

    private ParameterImpl[] dtorParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr)
        };
    }

    private Spec spec(String address, String name, String callingConvention, DataType returnType,
            ParameterImpl[] params, String comment, String... tags) {
        return new Spec(address, name, callingConvention, returnType, params, comment, baseTags(tags));
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);

        ParameterImpl[] ctorParams = ctorParams(voidPtr);
        ParameterImpl[] unpackParams = unpackParams(uintType, intType, voidPtr, floatPtr);
        ParameterImpl[] blockReadParams = blockReadParams(uintType, intType, voidPtr, floatPtr);
        ParameterImpl[] blockWriteParams = blockWriteParams(uintType, intType, voidPtr, floatPtr);
        ParameterImpl[] decodeParams = decodeParams(uintType, intType, voidPtr);
        ParameterImpl[] flushParams = flushParams(voidPtr);
        ParameterImpl[] dtorParams = dtorParams(voidPtr);

        Spec[] specs = new Spec[] {
            spec(
                "0x005869b0",
                "CTexture__UnpackTexels_Bits16_16_16_ToFloat4",
                "__thiscall",
                voidType,
                unpackParams,
                "Wave675 static read-back: CTexture-labelled 16-16-16 unpacker expands three 16-bit source lanes into RGB float4 output and writes alpha 1.0 before the observed key-color/post-process gates. Static metadata only; exact lane enum contract, runtime texture output, and rebuild parity remain unproven.",
                "texel-unpacker", "ctexture", "bits16-16-16", "float4-output", "keycolor-zero-gate", "postprocess-gate"
            ),
            spec(
                "0x00586a55",
                "CFastVB__TexelUnpackProfile_005ea128__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea128. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea128"
            ),
            spec(
                "0x00586a71",
                "CFastVB__TexelUnpackProfileRegistry_005ea138__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: registry constructor initializes the shared unpack profile, allocates the scratch vec4 row window, records even-aligned bounds, and selects component shifts for YUY2/RGBG/GBGR/UYVY-style FourCC cases. Static metadata only; exact descriptor ABI and runtime format contract remain unproven.",
                "texel-unpack-profile-registry", "format-factory-case", "scratch-row-window", "fourcc-component-shifts", "vtable-005ea138"
            ),
            spec(
                "0x00586b63",
                "CFastVB__TexelUnpackProfile_005ea148__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea148. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea148"
            ),
            spec(
                "0x00586b7f",
                "CFastVB__TexelUnpackProfile_005ea158__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea158. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea158"
            ),
            spec(
                "0x00586b9b",
                "CFastVB__TexelUnpackProfile_005ea168__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea168. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea168"
            ),
            spec(
                "0x00586bb7",
                "CFastVB__FlushPendingConvertedRows16",
                "__fastcall",
                intType,
                flushParams,
                "Wave675 static read-back: flush helper writes pending two-pixel scratch rows back to the 16-bit source surface, handling direct component-shift RGBG/GBGR-like cases and YUV-to-RGB conversion/clamp cases before clearing the dirty flag. Static metadata only; exact FourCC semantics and runtime codec behavior remain unproven.",
                "texel-codec-flush", "scratch-row-window", "yuv-rgb-conversion", "component-shift-pack", "dirty-flag-clear"
            ),
            spec(
                "0x00586ec7",
                "CFastVB__InitTexelUnpackVTable_005ea198",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea198. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea198"
            ),
            spec(
                "0x00586ee3",
                "CFastVB__TexelUnpackProfile_005ea1a8__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea1a8. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea1a8"
            ),
            spec(
                "0x00586eff",
                "CFastVB__TexelUnpackProfile_005ea1b8__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea1b8. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea1b8"
            ),
            spec(
                "0x00586f1b",
                "CFastVB__TexelUnpackProfile_005ea1c8__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea1c8. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea1c8"
            ),
            spec(
                "0x00586f37",
                "CFastVB__DecodeRowWindowToScratchPairs",
                "__thiscall",
                intType,
                decodeParams,
                "Wave675 static read-back: row-window decoder flushes stale dirty rows, selects the requested two-pixel row/column window, and expands packed 16-bit RGBG/GBGR/YUY2/UYVY-style data into scratch float4 pairs. Static metadata only; exact FourCC naming, color-space contract, and runtime output remain unproven.",
                "texel-codec-decode", "scratch-row-window", "two-pixel-pairs", "yuv-rgb-conversion", "component-shift-unpack"
            ),
            spec(
                "0x00587303",
                "CFastVB__TexelUnpackProfile_005ea1f4__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea1f4. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea1f4"
            ),
            spec(
                "0x00587322",
                "CFastVB__TexelUnpackProfile_005ea204__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea204. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea204"
            ),
            spec(
                "0x0058733e",
                "CFastVB__TexelUnpackProfile_005ea214__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: profile constructor forwards the format descriptor to the shared texel-unpack profile initializer, then binds vtable 0x005ea214. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile", "format-factory-case", "vtable-binding", "vtable-005ea214"
            ),
            spec(
                "0x0058735a",
                "CFastVB__StoreDecodedBlockToScratch",
                "__thiscall",
                voidType,
                blockWriteParams,
                "Wave675 static read-back: store helper optionally converts/normalizes an input vec4 block, decodes the backing row window, copies the block into scratch storage, and marks the scratch row dirty for a later flush. Static metadata only; exact block ABI and runtime codec behavior remain unproven.",
                "texel-codec-store", "scratch-row-window", "vec4-block-copy", "dirty-flag-set", "domain-conversion"
            ),
            spec(
                "0x005873f8",
                "CFastVB__LoadDecodedBlockFromScratch",
                "__thiscall",
                voidType,
                blockReadParams,
                "Wave675 static read-back: load helper decodes the backing row window into scratch storage, copies scratch vec4 rows to the destination block, then applies the observed key-color/post-process gates. Static metadata only; exact block ABI and runtime codec behavior remain unproven.",
                "texel-codec-load", "scratch-row-window", "vec4-block-copy", "keycolor-zero-gate", "postprocess-gate"
            ),
            spec(
                "0x00587477",
                "CFastVB__TexelCodecProfile__ctorFromFourCC",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: codec profile constructor chains through the unpack profile initializer, dispatches DXT1-DXT5 FourCC cases to decode/encode callbacks, copies descriptor bounds, aligns block windows, and initializes quad-cache slots. Static metadata only; exact format-table contract and runtime DXT behavior remain unproven.",
                "texel-codec-profile", "fourcc-dispatch", "dxt-codec", "quad-cache", "aligned-block-window"
            ),
            spec(
                "0x00587663",
                "CFastVB__TexelCodecProfile_005ea224__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: codec-profile constructor forwards the descriptor to the FourCC codec profile initializer, then binds vtable 0x005ea224. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-codec-profile", "format-factory-case", "dxt-codec", "vtable-binding", "vtable-005ea224"
            ),
            spec(
                "0x0058767b",
                "CFastVB__TexelCodecProfile_005ea234__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: codec-profile constructor forwards the descriptor to the FourCC codec profile initializer, then binds vtable 0x005ea234. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-codec-profile", "format-factory-case", "dxt-codec", "vtable-binding", "vtable-005ea234"
            ),
            spec(
                "0x00587693",
                "CFastVB__TexelCodecProfile_005ea244__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: codec-profile constructor forwards the descriptor to the FourCC codec profile initializer, then binds vtable 0x005ea244. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-codec-profile", "format-factory-case", "dxt-codec", "vtable-binding", "vtable-005ea244"
            ),
            spec(
                "0x005876ab",
                "CTexture__WriteTexelBlockWithQuadCache",
                "__thiscall",
                voidType,
                blockWriteParams,
                "Wave675 static read-back: write helper maintains a 4x4 quad cache, lazily decodes needed source blocks, stores caller vec4 data into cache rows, and invokes the configured encode callback when a quad becomes complete. Static metadata only; exact DXT block ABI and runtime texture output remain unproven.",
                "texel-codec-write", "ctexture", "quad-cache", "dxt-codec", "encode-callback", "vec4-block-copy"
            ),
            spec(
                "0x00587af0",
                "CTexture__ReadTexelBlockWithQuadCache",
                "__thiscall",
                voidType,
                blockReadParams,
                "Wave675 static read-back: read helper lazily fills a cached 4x4 decoded block via the configured decode callback, copies requested vec4 rows to the destination, then applies key-color zeroing and post-process gates. Static metadata only; exact DXT block ABI and runtime texture output remain unproven.",
                "texel-codec-read", "ctexture", "quad-cache", "dxt-codec", "decode-callback", "keycolor-zero-gate", "postprocess-gate"
            ),
            spec(
                "0x00587daf",
                "CFastVB__TexelPackProfile_scalar_deleting_dtor",
                "__fastcall",
                voidType,
                dtorParams,
                "Wave675 static read-back: destructor-like helper restores the registry vtable, flushes pending converted 16-bit rows, frees the scratch row window, then tail-calls the base texel-unpack profile destructor. Static metadata only; exact class ownership and scalar-delete wrapper semantics remain unproven.",
                "texel-codec-dtor", "scratch-buffer-free", "flush-before-dtor", "destructor-like"
            ),
            spec(
                "0x00587dd6",
                "CFastVB__TexelUnpackProfileRegistry_005ea254__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave675 static read-back: registry constructor forwards the descriptor to the 0x005ea138 registry initializer, then binds vtable 0x005ea254. Static metadata only; exact descriptor ABI and factory contract remain unproven.",
                "texel-unpack-profile-registry", "format-factory-case", "scratch-row-window", "vtable-binding", "vtable-005ea254"
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
            throw new IllegalStateException("Wave675 apply encountered missing/bad rows");
        }
    }
}
