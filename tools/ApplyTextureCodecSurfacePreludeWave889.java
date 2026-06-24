//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureCodecSurfacePreludeWave889 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "texture-codec-surface-prelude-wave889",
            "wave889-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "texture-codec-surface-prelude",
            "important-render-infrastructure",
            "raw-commentless-tail"
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
        if (!fn.getSignature().toString().equals(spec.signature)) {
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
        String actualSignature = readBack.getSignature().toString();
        if (!actualSignature.equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature);
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
            if (!fn.getSignature().toString().equals(spec.signature)) {
                stats.bad++;
                println("BADSIG: " + spec.address + " actual=" + fn.getSignature() + " expected=" + spec.signature);
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec("0x00579a9a", "CVertexShader__CompileScriptWithDirectiveParser", "int CVertexShader__CompileScriptWithDirectiveParser(void)", "Wave889 static read-back: stack-locked vertex-shader script compile wrapper. The body initializes a directive parser context, initializes preprocessor state from a memory span, dispatches script loading by version, rejects leftover tokens, optionally emits concatenated text to the caller buffer, and destroys parser context. Static retail Ghidra evidence only; exact script grammar, hidden ABI, runtime shader compile behavior, BEA patching, and rebuild parity remain unproven.", tags("vertex-shader-script", "directive-parser", "stack-locked-abi")),
            new Spec("0x00579b39", "CDXTexture__LookupNamedFormatDescriptor", "int __stdcall CDXTexture__LookupNamedFormatDescriptor(void * format_name, uint required_flags, void * out_descriptor_or_null)", "Wave889 static read-back: named texture-format descriptor lookup. The body binary-searches the 0x005e9340 descriptor table, requires the requested flag mask at row +8, optionally copies the three-dword row, and returns D3D-style success/failure codes. Static retail Ghidra evidence only; exact descriptor schema, full table identity, runtime format behavior, BEA patching, and rebuild parity remain unproven.", tags("format-descriptor", "table-005e9340", "binary-search")),
            new Spec("0x00579bd5", "CDXTexture__SetD3D9DebugMute", "void __stdcall CDXTexture__SetD3D9DebugMute(int mute_enabled)", "Wave889 static read-back: D3D9 debug mute bridge. The body resolves DebugSetMute from d3d9.dll and d3d9d.dll on demand, checks cached registry/config flag D3DXDoNotMute through CDXTexture__RegistryValueEqualsDword, and forwards the requested mute value when allowed. Static retail Ghidra evidence only; exact registry path, runtime D3D debug behavior, BEA patching, and rebuild parity remain unproven.", tags("d3d9-debug", "debugsetmute", "registry-gated")),
            new Spec("0x00579ca5", "CDXTexture__InitSurfaceNodeZeroed", "void __fastcall CDXTexture__InitSurfaceNodeZeroed(void * surface_node)", "Wave889 static read-back: zero-initializes the observed surface-node record fields before decode/build paths populate descriptor, buffer, extent, pitch, depth, and child-link state. Static retail Ghidra evidence only; exact surface-node layout, lifetime contract, runtime texture behavior, BEA patching, and rebuild parity remain unproven.", tags("surface-node", "zero-init")),
            new Spec("0x00579cbe", "CDXTexture__FreeSurfaceNodeTree", "void __fastcall CDXTexture__FreeSurfaceNodeTree(void * surface_node)", "Wave889 static read-back: recursive surface-node tree cleanup. The body frees owned primary/secondary buffers when ownership flags are set, then recursively frees child links at +0x4c and +0x50 through OID__FreeObject_Callback. Static retail Ghidra evidence only; exact ownership/layout contract, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("surface-node", "recursive-cleanup", "ownership-flags")),
            new Spec("0x00579d17", "CDXTexture__SurfaceNode_scalar_deleting_dtor", "void * __thiscall CDXTexture__SurfaceNode_scalar_deleting_dtor(void * this, uint delete_flags, int unused_arg1)", "Wave889 static read-back: scalar deleting destructor for the surface-node record. It calls CDXTexture__FreeSurfaceNodeTree on the object and conditionally releases the object allocation based on delete_flags. Static retail Ghidra evidence only; exact allocator ownership, destructor ABI, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("surface-node", "scalar-deleting-dtor")),
            new Spec("0x00579d33", "CDXTexture__InitSurfaceFormatInfoFromDescriptor", "int __thiscall CDXTexture__InitSurfaceFormatInfoFromDescriptor(void * this, void * descriptor_row, void * unused_context)", "Wave889 static read-back: initializes surface-node format/extent fields from a descriptor row. The body releases prior owned buffers, copies descriptor identity and six extent/stride fields, masks DXT/YUV/RGB-like bounds, recomputes width/height/depth extents, and returns success. Static retail Ghidra evidence only; exact descriptor and surface-node layouts, runtime texture behavior, BEA patching, and rebuild parity remain unproven.", tags("surface-node", "format-descriptor", "extent-fields")),
            new Spec("0x00579e08", "CDXTexture__DecodeBmpDibFromMemory", "int __thiscall CDXTexture__DecodeBmpDibFromMemory(void * this, void * dib_bytes, uint byte_count, void * unused_context)", "Wave889 static read-back: BMP DIB decoder body. The export shows a large parser/converter that validates in-memory DIB bytes, handles header/format branches, populates the texture surface-node state, and returns D3D-style status codes. Static retail Ghidra evidence only; exact BMP/DIB variant coverage, palette/bitfield rules, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("bmp-dib-decode", "image-codec", "large-parser")),
            new Spec("0x0057a934", "CDXTexture__WriteSurfaceAsBmpToHandle", "int __thiscall CDXTexture__WriteSurfaceAsBmpToHandle(void * this, void * file_handle, int write_enabled, int unused_arg2)", "Wave889 static read-back: BMP writer for a decoded surface chain. The body selects format-specific packing paths, writes BMP/DIB header and surface bytes through the handle callback, and respects the write_enabled flag. Static retail Ghidra evidence only; exact BMP output contract, row order, runtime I/O behavior, BEA patching, and rebuild parity remain unproven.", tags("bmp-write", "image-codec", "surface-writer")),
            new Spec("0x0057af0a", "CDXTexture__DecodeJpegFromMemory", "int __stdcall CDXTexture__DecodeJpegFromMemory(void * encoded_bytes, int byte_count)", "Wave889 static read-back: JPEG memory decode bridge. The body initializes JPEG/decode context helpers, routes through the internal JPEG parser/decoder pipeline, and returns status from the decoded texture path. Static retail Ghidra evidence only; exact context layout, runtime JPEG behavior, BEA patching, and rebuild parity remain unproven.", tags("jpeg-decode", "image-codec", "decode-bridge")),
            new Spec("0x0057b182", "CDXTexture__DecodeTgaFromMemory", "int __thiscall CDXTexture__DecodeTgaFromMemory(void * this, void * encoded_bytes, uint byte_count, uint unused_context)", "Wave889 static read-back: TGA memory decoder body. The export shows header validation, pixel-format/depth branches, output allocation/copy paths, and D3D-style status returns into the shared texture surface state. Static retail Ghidra evidence only; exact TGA variant coverage, origin/alpha handling, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("tga-decode", "image-codec")),
            new Spec("0x0057b6fa", "CDXTexture__DecodePpmFromMemory", "uint __thiscall CDXTexture__DecodePpmFromMemory(void * this, void * encoded_bytes, uint byte_count, uint unused_context)", "Wave889 static read-back: PPM memory decoder body. The body parses numeric/text tokens, validates dimensions and component ranges, copies decoded RGB data into the shared surface-node path, and returns status. Static retail Ghidra evidence only; exact PPM dialect coverage, whitespace/comment rules, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("ppm-decode", "image-codec", "text-parser")),
            new Spec("0x0057b9ce", "CDXTexture__DecodePngFromMemory", "int __stdcall CDXTexture__DecodePngFromMemory(void * encoded_bytes, int byte_count)", "Wave889 static read-back: PNG memory decode bridge. The body initializes PNG/decode helpers, drives the internal libpng-like read path, applies option/row transform helpers, and returns status into the shared texture surface state. Static retail Ghidra evidence only; exact PNG option state, transform coverage, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("png-decode", "image-codec", "decode-bridge")),
            new Spec("0x0057bf1f", "CDXTexture__BuildDdsSurfaceNodeTree", "int __thiscall CDXTexture__BuildDdsSurfaceNodeTree(void * this, void * dds_bytes, uint byte_count, void * unused_context)", "Wave889 static read-back: DDS parser/surface-node tree builder. The body validates DDS headers, initializes surface-node records, handles mip/depth child links, copies descriptor/extent state, and returns D3D-style status codes. Static retail Ghidra evidence only; exact DDS header/format coverage, mip-chain ownership, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("dds-decode", "surface-node-tree", "image-codec")),
            new Spec("0x0057c28b", "CDXTexture__WriteDdsSurfaceChainToHandle", "int __thiscall CDXTexture__WriteDdsSurfaceChainToHandle(void * this, void * file_handle, int write_enabled)", "Wave889 static read-back: DDS writer for a surface-node chain. The body emits DDS header/format metadata and walks surface-chain data through handle writes. Static retail Ghidra evidence only; exact DDS output schema, mip/depth traversal, runtime I/O behavior, BEA patching, and rebuild parity remain unproven.", tags("dds-write", "surface-node-chain", "image-codec")),
            new Spec("0x0057c57d", "CDXTexture__FlushStreamWriteBufferChunk", "int __stdcall CDXTexture__FlushStreamWriteBufferChunk(void * stream_context)", "Wave889 static read-back: stream write-buffer chunk callback. The body writes buffered bytes through the file/stream callback at 0x005d8108 and updates the stream context status. Static retail Ghidra evidence only; exact stream-context layout, I/O error semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("stream-write-buffer", "callback")),
            new Spec("0x0057c5b2", "CDXTexture__FlushStreamWriteBufferTail", "void __stdcall CDXTexture__FlushStreamWriteBufferTail(void * stream_context)", "Wave889 static read-back: stream write-buffer tail flush callback. The body emits any remaining buffered bytes through the same file/stream callback slot used by the chunk flusher. Static retail Ghidra evidence only; exact stream-context layout, tail semantics, runtime I/O behavior, BEA patching, and rebuild parity remain unproven.", tags("stream-write-buffer", "tail-flush")),
            new Spec("0x0057c5dc", "CDXTexture__EncodeRgbBufferToJpegStream", "int __thiscall CDXTexture__EncodeRgbBufferToJpegStream(void * this, void * file_handle, int unused_arg1)", "Wave889 static read-back: JPEG encoder bridge for an RGB surface buffer. The body initializes JPEG write context, installs stream flush callbacks, configures encode parameters, and writes encoded output to the supplied file handle. Static retail Ghidra evidence only; exact JPEG encoder options, stream context layout, runtime encode behavior, BEA patching, and rebuild parity remain unproven.", tags("jpeg-encode", "image-codec", "stream-writer")),
            new Spec("0x0057c7a4", "CMeshCollisionVolume__LoadMappedTextureResourcesByMode", "int __thiscall CMeshCollisionVolume__LoadMappedTextureResourcesByMode(void * this, void * mapped_resource_name_or_path, int output_mode, int open_mode_flags, int unused_arg3)", "Wave889 static read-back: mapped texture export/load path by output mode. The body selects a format descriptor list by output_mode, converts the surface-node chain when the selected descriptor differs, opens a mapped output context, and dispatches BMP/JPEG/DDS-style writers for observed modes 0/1/4/6. Static retail Ghidra evidence only; exact mode enum, mapped-file context, runtime texture export behavior, BEA patching, and rebuild parity remain unproven.", tags("mapped-texture-resource", "mode-dispatch", "surface-conversion")),
            new Spec("0x0057ca3a", "CDXTexture__DecodeBmpFromMemory", "int __thiscall CDXTexture__DecodeBmpFromMemory(void * this, void * bmp_bytes, uint byte_count, uint unused_context)", "Wave889 static read-back: BMP decode wrapper. The body forwards the decoded texture object, byte span, and context to CDXTexture__DecodeBmpDibFromMemory and normalizes the return path. Static retail Ghidra evidence only; exact BMP wrapper ABI, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("bmp-decode", "image-codec", "wrapper")),
            new Spec("0x0057ca6a", "CDXTexture__DecodeFromMemory_WithFallbackCodecs", "int CDXTexture__DecodeFromMemory_WithFallbackCodecs(void)", "Wave889 static read-back: stack-locked multi-codec decode dispatcher. The decompile tries codec modes in order BMP, PPM, DDS, JPEG, PNG, TGA, and DIB, cleans failed partial surface allocations, fills optional output descriptor fields, and normalizes surface-node dimensions after success. Static retail Ghidra evidence only; exact hidden ABI, codec priority policy, runtime decode behavior, BEA patching, and rebuild parity remain unproven.", tags("multi-codec-dispatch", "image-codec", "stack-locked-abi")),
            new Spec("0x0057cc53", "CDXTexture__InitMappedFileContext", "void __fastcall CDXTexture__InitMappedFileContext(void * surface_pair)", "Wave889 static read-back: mapped-file/context initializer. The body clears the observed two-slot surface/file context before mapped texture load/export paths open or attach resources. Static retail Ghidra evidence only; exact context layout, runtime file behavior, BEA patching, and rebuild parity remain unproven.", tags("mapped-file-context", "zero-init")),
            new Spec("0x0057cc5d", "CDXTexture__ReleaseSurfacePairIfPresent", "void __fastcall CDXTexture__ReleaseSurfacePairIfPresent(void * surface_pair)", "Wave889 static read-back: mapped-file/surface-pair release helper. The body checks the two context slots and invokes their virtual/release callbacks when present. Static retail Ghidra evidence only; exact context layout, ownership policy, runtime release behavior, BEA patching, and rebuild parity remain unproven.", tags("mapped-file-context", "release-helper")),
            new Spec("0x0057cc7b", "Math__FloorFloatToDouble", "double __stdcall Math__FloorFloatToDouble(float value)", "Wave889 static read-back: small floor/float conversion helper used by resample-kernel construction. The body calls the shared floating-point conversion helper at 0x0055dfe7 and returns the converted double-like result to callers. Static retail Ghidra evidence only; exact CRT/math helper identity, rounding edge behavior, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("math-helper", "floor-float", "resample-kernel")),
            new Spec("0x0057cc8e", "CFastVB__ClearTripleDword", "void __fastcall CFastVB__ClearTripleDword(void * triple_dword)", "Wave889 static read-back: clears a three-dword scratch/descriptor record. DATA xrefs from dual-profile conversion setup point at this helper as a compact zeroing callback. Static retail Ghidra evidence only; exact scratch-record identity, caller contract, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("scratch-clear", "triple-dword", "callback")),
            new Spec("0x0057cca4", "CFastVB__BuildResampleKernelBuckets", "int * __stdcall CFastVB__BuildResampleKernelBuckets(uint output_count, int source_count, int clamp_edges)", "Wave889 static read-back: variable-length one-dimensional resample-kernel bucket builder. The body allocates a bucket table, uses Math__FloorFloatToDouble to locate source intervals, accumulates per-source weights, and records per-output offsets for dual-profile conversion callers. Static retail Ghidra evidence only; exact kernel-table layout, numeric edge behavior, runtime resampling quality, BEA patching, and rebuild parity remain unproven.", tags("resample-kernel", "bucket-table", "dual-profile-conversion")),
            new Spec("0x0057cf60", "CDXTexture__CopyDxtBlockRegion", "int __fastcall CDXTexture__CopyDxtBlockRegion(void * copy_context)", "Wave889 static read-back: DXT block-region copy helper. The body validates 4x4 block alignment, selects DXT1 8-byte blocks or DXT2-5 16-byte blocks, computes source/destination row/depth offsets, and copies the requested block rectangle. Static retail Ghidra evidence only; exact copy-context layout, runtime texture conversion behavior, BEA patching, and rebuild parity remain unproven.", tags("dxt-copy", "block-aligned", "surface-conversion"))
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        println("TARGETS: " + specs.length);
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave889 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
