//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyCDXTextureImageCodecWave662 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
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
            "cdxtexture-image-codec-wave662",
            "wave662-readback-verified",
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00579b39",
                "CDXTexture__LookupNamedFormatDescriptor",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("format_name", voidPtr), param("required_flags", uintType), param("out_descriptor_or_null", voidPtr) },
                "Wave662 static read-back: binary-searches the 0x005e9340 named format descriptor table, requires the requested flag mask, optionally copies the three-dword descriptor row, and returns D3D-style success/failure codes. Static metadata only; exact descriptor schema and runtime format behavior remain unproven.",
                new String[] {},
                tags("format-descriptor", "binary-search")
            ),
            new Spec(
                "0x00579bd5",
                "CDXTexture__SetD3D9DebugMute",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("mute_enabled", intType) },
                "Wave662 static read-back: resolves DebugSetMute from d3d9.dll/d3d9d.dll on demand, gates calls through a cached registry/config flag, and forwards the mute value when debug muting is allowed. Static metadata only; exact registry key naming and runtime D3D behavior remain unproven.",
                new String[] {},
                tags("d3d-debug", "debugsetmute")
            ),
            new Spec(
                "0x00579ca5",
                "CDXTexture__InitSurfaceNodeZeroed",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("surface_node", voidPtr) },
                "Wave662 static read-back: clears the observed surface-node root pointers, ownership flags, and child links at offsets 0x00/0x04/0x08/0x38/0x3c/0x4c/0x50 before decode/tree population. Static metadata only; exact surface-node layout remains unproven.",
                new String[] {},
                tags("surface-node", "initializer")
            ),
            new Spec(
                "0x00579cbe",
                "CDXTexture__FreeSurfaceNodeTree",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("surface_node", voidPtr) },
                "Wave662 static read-back: releases owned primary/secondary buffers when ownership flags are set, then recursively frees child surface-node links at 0x4c and 0x50. Static metadata only; exact ownership/layout contract remains unproven.",
                new String[] {},
                tags("surface-node", "recursive-free")
            ),
            new Spec(
                "0x00579d17",
                "CDXTexture__SurfaceNode_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", uintType), param("unused_arg1", intType) },
                "Wave662 static read-back: scalar-deleting destructor wrapper that frees the surface-node tree and conditionally frees this when bit 0 of delete_flags is set; second recovered argument is unused in the current decompile. Static metadata only; exact compiler-generated destructor ABI remains unproven.",
                new String[] {},
                tags("surface-node", "scalar-deleting-dtor")
            ),
            new Spec(
                "0x00579d33",
                "CDXTexture__InitSurfaceFormatInfoFromDescriptor",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("descriptor_row", voidPtr), param("unused_context", voidPtr) },
                "Wave662 static read-back: releases prior owned buffers, copies descriptor identity and six extent/stride fields into the surface node, masks DXT/YUV/RGB-like bounds, recomputes width/height/depth extents, and returns success. Static metadata only; exact descriptor/layout identity remains unproven.",
                new String[] {},
                tags("surface-node", "format-descriptor")
            ),
            new Spec(
                "0x00579e08",
                "CDXTexture__DecodeBmpDibFromMemory",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("dib_bytes", voidPtr), param("byte_count", uintType), param("unused_context", voidPtr) },
                "Wave662 static read-back: validates BMP DIB header sizes, masks, palette data, and row bounds, then populates the surface-node format/extent fields plus decoded pixel/palette buffers. Static metadata only; exact BMP variant coverage and runtime image fidelity remain unproven.",
                new String[] {},
                tags("bmp", "dib-decode", "surface-node")
            ),
            new Spec(
                "0x0057a934",
                "CDXTexture__WriteSurfaceAsBmpToHandle",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("file_handle", voidPtr), param("write_enabled", intType), param("unused_arg2", intType) },
                "Wave662 static read-back: builds BMP file/DIB headers for observed surface formats, emits optional palette/header/pixel rows through WriteFile when enabled, and returns D3D-style status codes. Static metadata only; exact file-handle ownership and BMP output fidelity remain unproven.",
                new String[] {},
                tags("bmp", "writefile", "surface-export")
            ),
            new Spec(
                "0x0057af0a",
                "CDXTexture__DecodeJpegFromMemory",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("encoded_bytes", voidPtr), param("byte_count", intType) },
                "Wave662 static read-back: initializes the JPEG decode pipeline, binds memory input callbacks, gates MMX conversion, decodes scanlines into the active surface-node buffer, and releases decoder state. Static metadata only; exact JPEG library ABI and runtime output fidelity remain unproven.",
                new String[] {},
                tags("jpeg", "memory-decode")
            ),
            new Spec(
                "0x0057b182",
                "CDXTexture__DecodeTgaFromMemory",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("encoded_bytes", voidPtr), param("byte_count", uintType), param("unused_context", uintType) },
                "Wave662 static read-back: validates TGA header/type/depth fields, handles palette and direct-color cases, applies origin/orientation bits, allocates decoded buffers, and populates surface-node dimensions/format. Static metadata only; exact TGA variant coverage and runtime image fidelity remain unproven.",
                new String[] {},
                tags("tga", "memory-decode", "surface-node")
            ),
            new Spec(
                "0x0057b6fa",
                "CDXTexture__DecodePpmFromMemory",
                "__thiscall",
                uintType,
                new ParameterImpl[] { param("this", voidPtr), param("encoded_bytes", voidPtr), param("byte_count", uintType), param("unused_context", uintType) },
                "Wave662 static read-back: parses P3/P6 PPM headers with comments/whitespace, allocates a 32-bit output buffer, scales samples by the declared max value, and writes RGB rows with opaque alpha. Static metadata only; exact PPM compatibility and runtime image fidelity remain unproven.",
                new String[] {},
                tags("ppm", "memory-decode", "surface-node")
            ),
            new Spec(
                "0x0057b9ce",
                "CDXTexture__DecodePngFromMemory",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("encoded_bytes", voidPtr), param("byte_count", intType) },
                "Wave662 static read-back: checks the PNG signature, creates PNG/inflate decode contexts, applies bit-depth/palette/gamma/alpha transforms, decodes rows into the active surface-node buffer, and releases decode handles. Static metadata only; exact PNG library ABI and runtime output fidelity remain unproven.",
                new String[] {},
                tags("png", "memory-decode")
            ),
            new Spec(
                "0x0057bf1f",
                "CDXTexture__BuildDdsSurfaceNodeTree",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("dds_bytes", voidPtr), param("byte_count", uintType), param("unused_context", voidPtr) },
                "Wave662 static read-back: validates DDS magic/header fields, resolves the format descriptor, derives cube/volume/mip counts, and builds a linked surface-node tree over payload spans. Static metadata only; exact DDS layout, cube/volume semantics, and runtime upload behavior remain unproven.",
                new String[] {},
                tags("dds", "surface-node", "mip-chain")
            ),
            new Spec(
                "0x0057c28b",
                "CDXTexture__WriteDdsSurfaceChainToHandle",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("file_handle", voidPtr), param("write_enabled", intType) },
                "Wave662 static read-back: counts surface-node chain levels/faces, writes DDS magic/header and optional palette data, then streams each surface row/block through WriteFile. Static metadata only; exact DDS header flags and runtime export fidelity remain unproven.",
                new String[] {},
                tags("dds", "writefile", "surface-export")
            ),
            new Spec(
                "0x0057c57d",
                "CDXTexture__FlushStreamWriteBufferChunk",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("stream_context", voidPtr) },
                "Wave662 static read-back: flushes a full 0x1000-byte stream buffer through WriteFile, resets the current pointer and remaining-byte fields, and returns a nonzero callback status. Static metadata only; exact stream-writer ABI remains unproven.",
                new String[] {},
                tags("jpeg", "stream-write", "writefile")
            ),
            new Spec(
                "0x0057c5b2",
                "CDXTexture__FlushStreamWriteBufferTail",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("stream_context", voidPtr) },
                "Wave662 static read-back: writes the pending tail bytes from the stream buffer when the buffer is partially filled. Static metadata only; exact stream-writer ABI remains unproven.",
                new String[] {},
                tags("jpeg", "stream-write", "writefile")
            ),
            new Spec(
                "0x0057c5dc",
                "CDXTexture__EncodeRgbBufferToJpegStream",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("file_handle", voidPtr), param("unused_arg1", intType) },
                "Wave662 static read-back: configures JPEG encoder callbacks around a WriteFile-backed stream, converts surface rows to RGB triples, feeds scanlines into the encoder pipeline, and releases temporary buffers. Static metadata only; exact encoder quality/config and runtime output fidelity remain unproven.",
                new String[] {},
                tags("jpeg", "stream-encode", "writefile")
            ),
            new Spec(
                "0x0057ca3a",
                "CDXTexture__DecodeBmpFromMemory",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("bmp_bytes", voidPtr), param("byte_count", uintType), param("unused_context", uintType) },
                "Wave662 static read-back: validates the BMP file header and payload length, then forwards the DIB body to CDXTexture__DecodeBmpDibFromMemory. Static metadata only; exact BMP variant coverage and runtime image fidelity remain unproven.",
                new String[] {},
                tags("bmp", "memory-decode")
            ),
            new Spec(
                "0x0057cc53",
                "CDXTexture__InitMappedFileContext",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("surface_pair", voidPtr) },
                "Wave662 static read-back: initializes an observed two-pointer surface-pair/mapped-file context by clearing both interface slots. Static metadata only; exact object identity remains unproven.",
                new String[] {},
                tags("surface-pair", "initializer")
            ),
            new Spec(
                "0x0057cc5d",
                "CDXTexture__ReleaseSurfacePairIfPresent",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("surface_pair", voidPtr) },
                "Wave662 static read-back: releases the two observed interface slots in a surface-pair context by invoking vtable slot 0 with argument 1 when each pointer is present. Static metadata only; exact COM/interface identity remains unproven.",
                new String[] {},
                tags("surface-pair", "release")
            ),
            new Spec(
                "0x0057cf60",
                "CDXTexture__CopyDxtBlockRegion",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("copy_context", voidPtr) },
                "Wave662 static read-back: validates source/destination DXT block alignment, selects DXT1 8-byte or DXT2-5 16-byte blocks, and copies the requested block rectangle across row/depth strides. Static metadata only; exact copy-context layout and runtime texture conversion behavior remain unproven.",
                new String[] {},
                tags("dxt", "block-copy")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave662 had missing/bad rows");
        }
    }
}
