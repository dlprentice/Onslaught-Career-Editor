//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureDecodeUploadTailWave886 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;
        final String[] removeTags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this(address, name, signature, comment, tags, new String[0]);
        }

        Spec(String address, String name, String signature, String comment, String[] tags, String[] removeTags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
            this.removeTags = removeTags;
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
            "texture-decode-upload-tail-wave886",
            "wave886-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "stack-locked-abi",
            "hidden-register-context",
            "important-render-infrastructure",
            "texture-decode-upload-tail",
            "raw-commentless-head"
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

    private boolean hasAnyTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (existing.contains(tag)) {
                return true;
            }
        }
        return false;
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
        return !hasAllTags(fn, spec.tags) || hasAnyTags(fn, spec.removeTags);
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
        if (hasAnyTags(readBack, spec.removeTags)) {
            throw new IllegalStateException("Read-back stale tag mismatch at " + spec.address);
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
            for (String tag : spec.removeTags) {
                fn.removeTag(tag);
            }
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
            new Spec(
                "0x00573d80",
                "CTexture__InsertNodeIntoTree",
                "int CTexture__InsertNodeIntoTree(void)",
                "Wave886 static read-back: RB-tree insert helper reached from CFastVB__InsertNodeIntoRBTreeWithHint_00573340 at 0x00573530. The body allocates a 0x14-byte node through OID__AllocObject_DefaultTag_00662b2c, stores the parent/payload/key-like fields, increments the tree header count at ECX+0xc, links against the DAT_009d0c44 sentinel, then performs red-black insert fixup rotations/recolors and writes the inserted node through the output slot. Existing CTexture owner name is retained from the Wave654 tree family even though the caller is adjacent CFastVB tree code. Static retail Ghidra evidence only; exact owner/template identity, concrete node layout, runtime texture/tree behavior, BEA patching, and rebuild parity remain unproven.",
                tags("rb-tree-insert", "sentinel-tree", "dat-009d0c44", "oid-alloc-0x14", "cfastvb-tree-caller", "ret-0x10")
            ),
            new Spec(
                "0x00574492",
                "CDXTexture__UploadDecodedBufferToSurface",
                "int CDXTexture__UploadDecodedBufferToSurface(void)",
                "Wave886 static read-back: decoded-buffer upload helper called from CDXTexture__DecodeMemoryAndUploadWithRect, CDXTexture__DecodeMemoryToTextureObject, and CDXTexture__CopyOrUploadSurfaceRegionWithFallback. The body validates destination/source/descriptor inputs, defaults -1 flags to 0x80004, calls CDXTexture__UploadSurfaceRegionWithFallback, builds local copy/conversion descriptors from the supplied rectangle/format state, invokes CFastVB__InitDualTexelConversionPipeline, then finalizes temporary upload state and releases the surface pair. Ghidra reports locked/hidden parameter storage, so Wave886 preserves the existing signature display. Static retail evidence only; exact surface/rectangle/profile layout, runtime D3D upload behavior, BEA patching, and rebuild parity remain unproven.",
                tags("decoded-buffer-upload", "surface-region-upload", "dual-texel-conversion", "ret-0x28")
            ),
            new Spec(
                "0x00574662",
                "CDXTexture__ConvertSurfaceWithActiveProfile",
                "int CDXTexture__ConvertSurfaceWithActiveProfile(void)",
                "Wave886 static read-back: active-profile surface conversion helper called from CDXTexture__DecodeMemoryToTextureObject and CDXTexture__ConvertSurfaceRegionWithActiveProfile. The body initializes mapped-file/surface-pair state, validates source/destination/descriptor inputs, defaults -1 flags to 0x80004, builds a texel codec profile with CDXTexture__CreateTexelCodecProfileFromSurfaceDesc, copies the six-dword descriptor into local conversion descriptors, invokes CFastVB__InitDualTexelConversionPipeline, shuts down the active profile, and releases the surface pair. Static retail evidence only; exact codec-profile layout, hidden register ABI, runtime conversion behavior, BEA patching, and rebuild parity remain unproven.",
                tags("surface-conversion", "active-profile", "texel-codec-profile", "dual-texel-conversion", "ret-0x2c")
            ),
            new Spec(
                "0x0057473b",
                "CDXTexture__NormalizeTextureConversionParams",
                "int CDXTexture__NormalizeTextureConversionParams(void)",
                "Wave886 static read-back: texture conversion parameter normalizer called from CDXTexture__DecodeMemoryToTextureObject at 0x00575516. The body rejects invalid device/usage/resource-type inputs with 0x8876086c-style errors, resolves requested format descriptors through CDXTexture__FindFormatDescriptorById and CFastVB__SelectBestFormatHandler, normalizes width/height/depth/mip-count pointers, queries device caps through the vtable slot at +0x1c, clamps texture/cube/volume dimensions, enforces power-of-two restrictions when required, aligns DXT1-DXT5 dimensions to 4-pixel blocks, and writes the normalized values back to the caller-provided slots. Static retail evidence only; exact Direct3D caps structure, hidden EDX/device ABI, runtime compatibility behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texture-param-normalizer", "format-selection", "dxt-block-align", "device-caps-query", "ret-0x20")
            ),
            new Spec(
                "0x00574ae5",
                "CDXTexture__DecodeMemoryAndUploadWithRect",
                "int CDXTexture__DecodeMemoryAndUploadWithRect(void)",
                "Wave886 static read-back: memory decode plus rectangle upload helper called by Platform__OpenDecodeUploadMappedTexture at 0x00575156. The body initializes a decoded surface-node tree, validates memory/buffer dimensions, decodes through CDXTexture__DecodeFromMemory_WithFallbackCodecs, derives a full-image rectangle or validates a caller rectangle against decoded width/height bounds, calls CDXTexture__UploadDecodedBufferToSurface, then frees the decoded surface-node tree. Static retail evidence only; exact rectangle ABI, codec fallback order, runtime image upload behavior, BEA patching, and rebuild parity remain unproven.",
                tags("memory-decode-upload", "fallback-codecs", "rect-validation", "surface-node-tree", "ret-0x24"),
                new String[] {"ret-0x18"}
            ),
            new Spec(
                "0x00574b9d",
                "CDXTexture__CopyOrUploadSurfaceRegionWithFallback",
                "int CDXTexture__CopyOrUploadSurfaceRegionWithFallback(void)",
                "Wave886 static read-back: surface-region copy helper reached from CDXTexture__GenerateMipChainBySurfaceCopy at 0x0057501f. The body gathers source/destination surface descriptors through vtable slot +0x30, prefers direct D3D copy/update paths when palettes, rectangles, and dimensions are compatible, temporarily mutes D3D9 debug output around vtable slots +0x88/+0x78, and falls back to CDXTexture__UploadSurfaceRegionWithFallback plus CDXTexture__UploadDecodedBufferToSurface when direct copy is unsuitable or fails. It finalizes temporary upload state before returning. Static retail evidence only; exact surface descriptor layout, Direct3D interface identity, runtime copy/upload behavior, BEA patching, and rebuild parity remain unproven.",
                tags("surface-copy-fallback", "d3d-copy-path", "d3d-debug-mute", "mip-chain-caller", "ret-0x20")
            ),
            new Spec(
                "0x00574da5",
                "CDXTexture__ConvertSurfaceRegionWithActiveProfile",
                "int CDXTexture__ConvertSurfaceRegionWithActiveProfile(void)",
                "Wave886 static read-back: compact surface-region conversion wrapper reached from CDXTexture__GenerateMipChainBySurfaceCopy at 0x00575073. The body resets conversion status, validates source/destination inputs, creates a texel codec profile through CDXTexture__CreateTexelCodecProfileFromSurfaceDesc, delegates the actual conversion to CDXTexture__ConvertSurfaceWithActiveProfile, then shuts down the active profile. Static retail evidence only; exact conversion-status layout, runtime mip-chain conversion behavior, BEA patching, and rebuild parity remain unproven.",
                tags("surface-region-conversion", "active-profile-wrapper", "mip-chain-caller", "ret-0x20"),
                new String[] {"ret-0x1c"}
            ),
            new Spec(
                "0x0057511b",
                "Platform__OpenDecodeUploadMappedTexture",
                "int Platform__OpenDecodeUploadMappedTexture(void)",
                "Wave886 static read-back: platform mapped-file decode/upload bridge called by Platform__ProcessPendingScreenDump at 0x00441d4a. The body initializes a mapped-file context, opens the supplied path read-only through CDXTexture__OpenMappedFileReadOnly, delegates decode/upload to CDXTexture__DecodeMemoryAndUploadWithRect on success, and closes the mapped handle before returning. Static retail evidence only; exact platform screenshot/upload caller intent, hidden ESI/path ABI, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mapped-file-decode-upload", "platform-bridge", "read-only-open", "screen-dump-caller", "ret-0x20"),
                new String[] {"ret-0x24"}
            ),
            new Spec(
                "0x0057516c",
                "CDXTexture__DecodeMemoryToTextureObject",
                "int CDXTexture__DecodeMemoryToTextureObject(void)",
                "Wave886 static read-back: central memory-to-texture-object decode helper called by CDXTexture__DecodeMappedMemoryEntry at 0x0057591a. The body validates memory/device/output slots, decodes through CDXTexture__DecodeFromMemory_WithFallbackCodecs, counts surface-chain and cube/volume slices, chooses requested or decoded dimensions, builds or copies a 256-entry palette, maps source format through CDXTexture__MapFormatTokenToInternalCode, normalizes creation parameters through CDXTexture__NormalizeTextureConversionParams, creates 2D/volume/cube texture objects through device vtable slots +0x5c/+0x60/+0x64, uploads or converts each mip/slice through CDXTexture__UploadDecodedBufferToSurface or CDXTexture__ConvertSurfaceWithActiveProfile, may generate a mip chain through CDXTexture__GenerateMipChainBySurfaceCopy, writes the created texture to the caller output slot, and releases all temporary surfaces on exit. Static retail evidence only; exact texture object ABI, palette/format semantics, runtime codec fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("memory-to-texture-object", "fallback-codecs", "palette-copy", "format-map", "texture-create-vtable", "mip-chain-generation", "ret-0x44")
            ),
            new Spec(
                "0x005758e6",
                "CDXTexture__DecodeMappedMemoryEntry",
                "void CDXTexture__DecodeMappedMemoryEntry(void)",
                "Wave886 static read-back: mapped-memory decode entry thunk called from CDXTexture__LoadTextureFromFile at 0x005578d3 and CDXTexture__DecodeMappedFileToTexture at 0x00575970. The body forwards the visible stack argument block, inserts constants 1 and 3 for decode/create mode slots, calls CDXTexture__DecodeMemoryToTextureObject, then returns with RET 0x3c. Static retail evidence only; exact forwarded argument meanings, runtime mapped-file decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mapped-memory-entry", "decode-thunk", "forwarded-stack-block", "ret-0x3c")
            )
        };

        Stats stats = new Stats();
        println("Wave886 texture decode/upload tail mode=" + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave886 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
