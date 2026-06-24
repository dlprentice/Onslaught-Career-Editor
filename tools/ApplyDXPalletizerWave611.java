//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyDXPalletizerWave611 extends GhidraScript {
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
            "dxpalletizer-wave611",
            "retail-binary-evidence",
            "signature-corrected",
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
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType bytePtr = new PointerDataType(ByteDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType uintPtr = new PointerDataType(uintType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0054e500",
                "DXPalletizer__InsertColor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("channel0", byteType),
                    param("channel1", byteType),
                    param("channel2", byteType),
                    param("alpha_or_channel3", byteType),
                    param("bit_depth", byteType)
                },
                "Wave611 DXPalletizer octree hardening: callsite 0x0054eb41 sets ECX to the current octree node/root and pushes channel bytes plus depth 7. Body walks bit planes into a 16-child RGBA octree, allocates 0x54-byte nodes with debug path 0x00651d60 line 0x16, clears child slots at +0x14, stores leaf colors at depth <= 0, and increments pixel count +0x08. Static retail decompile/instruction/xref evidence only; exact source identity, exact octree-node layout names, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "insert-color", "callsite-verified", "debug-path-00651d60")
            ),
            new Spec(
                "0x0054e670",
                "DXPalletizer__BuildPalette",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("palette_words", uintPtr)
                },
                "Wave611 DXPalletizer palette-build hardening: callsites 0x0054ebc6 and recursive 0x0054e6aa pass ECX as an octree node and one stack palette pointer. Body writes node color dword +0x00 to palette[index] when node +0x04 is non-negative, then walks the 16 child slots at +0x14 recursively. Static retail decompile/instruction/xref evidence only; exact source identity, exact node field names, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "palette-build", "recursive-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054e6e0",
                "DXPalletizer__AssignPaletteIndices",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("palette_counter", intPtr),
                    param("minimum_pixel_count", uintType)
                },
                "Wave611 DXPalletizer index-assignment hardening: callsites 0x0054eb7a/0x0054eba3 and recursive 0x0054e756 pass ECX as an octree node, palette counter pointer, and threshold. Branch nodes recurse through 16 children; leaf nodes with +0x08 pixel_count >= threshold set active flag +0x10, store palette index at +0x04, increment the counter, return assigned pixel count, and clear +0x08. Static retail decompile/instruction/xref evidence only; exact source identity, exact node field names, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "palette-index", "recursive-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054e790",
                "DXPalletizer__CollapseOctreeNode",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave611 DXPalletizer collapse hardening: callsite 0x0054ebb8 and recursive 0x0054e929 pass ECX as an octree node. Body skips already-selected or leaf nodes, checks whether all populated children are leaves, merges leaf child pixel counts into parent +0x08, sets leaf/selected flags at +0x0c/+0x10 as appropriate, frees child nodes through DXPalletizer__FreeOctreeNode and CDXMemoryManager__Free, or recurses into branch children. Static retail decompile/instruction/xref evidence only; exact source identity, exact node field names, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "collapse-octree", "recursive-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054e950",
                "DXPalletizer__FreeOctreeNode",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("free_self", byteType)
                },
                "Wave611 DXPalletizer free-node hardening: callsites 0x0054e86b, 0x0054e97d, and 0x0054eefe pass ECX as node plus delete flag 1. Body recurses through 16 child slots at +0x14, clears each child pointer, frees descendants, conditionally frees the current node through CDXMemoryManager__Free when free_self & 1, and returns the node pointer for scalar-deleting style callers. Static retail decompile/instruction/xref evidence only; exact source identity, exact node field names, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "free-node", "recursive-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054e9d0",
                "DXPalletizer__Palletize",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_rgba", voidPtr),
                    param("width", intType),
                    param("height", intType),
                    param("requested_palette_size", uintType),
                    param("out_indices_ref", voidPtr),
                    param("out_palette_ref", voidPtr),
                    param("source_has_alpha", intType),
                    param("allocate_outputs", intType),
                    param("swizzle_output", intType),
                    param("preserve_alpha", intType),
                    param("expand_half_palette", intType),
                    param("copy_palette_tiles", intType)
                },
                "Wave611 DXPalletizer main-entry hardening: CDXEngine__BuildLandscapeTextureCache callsite 0x005479a6 passes ECX as a stack workspace and 12 stack args: source RGBA, width/height, requested palette size, output index/palette refs, and flags. Body allocates root node +0x404, inserts source pixels, repeatedly assigns/collapses octree nodes until the palette fits, builds palette data, maps pixels through DXPalletizer__FindNearestColor, optionally calls DXPalletizer__SwizzleTexture, optionally expands half-palette colors using DAT_006fbe44/DAT_006fbe54, copies tiled palette blocks when requested, and frees the root tree. Static retail decompile/instruction/xref evidence only; parameter names after the output refs are behavior labels, not exact source names; runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "palette-main", "landscape-texture-cache", "callsite-verified", "debug-path-00651d60")
            ),
            new Spec(
                "0x0054ef70",
                "DXPalletizer__FindNearestColor",
                "__thiscall",
                byteType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("channel0", uintType),
                    param("channel1", uintType),
                    param("channel2", uintType),
                    param("alpha_or_channel3", uintType)
                },
                "Wave611 DXPalletizer nearest-color hardening: callsite 0x0054ec7c passes ECX as palette base and four channel values. Body reads palette count at palette_base +0x400, computes Manhattan distance across four bytes for each palette entry, tracks the smallest distance, and returns the selected palette index in AL. Static retail decompile/instruction/xref evidence only; exact source identity, exact palette buffer layout names, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "octree-palette", "nearest-color", "manhattan-distance", "callsite-verified")
            ),
            new Spec(
                "0x0054f090",
                "DXPalletizer__SwizzleBlock",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("block_width", intType),
                    param("block_height", intType),
                    param("src_block", voidPtr),
                    param("dst_block", voidPtr)
                },
                "Wave611 DXPalletizer swizzle-block hardening: DXPalletizer__SwizzleTexture callsite 0x0054f50f pushes width 0x80, height 0x40, source scratch, and destination scratch, then cleans 0x10 bytes. Body allocates two 0x80-byte temporary lookup buffers, derives Morton-order remaps from table 0x00651ce0, uses small/large swizzle tables 0x00651760 and 0x00651960 plus block-index table 0x00651c60, writes the swizzled block, frees temporaries, and returns 0. Static retail decompile/instruction/xref evidence only; exact console texture format identity, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "texture-swizzle", "swizzle-block", "morton-order", "cdecl-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054f380",
                "DXPalletizer__SwizzleTexture",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("width", uintType),
                    param("height", intType),
                    param("src_indices", voidPtr),
                    param("dst_swizzled", voidPtr)
                },
                "Wave611 DXPalletizer swizzle-texture hardening: DXPalletizer__Palletize callsite 0x0054ecc0 pushes width, height, source index buffer, and destination buffer, then cleans 0x10 bytes. Body validates power-of-two dimensions against 0x400-shift limits, clears two 0x2000-byte stack scratch buffers, tiles input into 128x64 or smaller chunks, calls DXPalletizer__SwizzleBlock, copies swizzled rows to the destination layout, and returns 0 or -1 on invalid dimensions. Static retail decompile/instruction/xref evidence only; exact console texture format identity, runtime texture output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("dxpalletizer", "texture-swizzle", "swizzle-texture", "morton-order", "cdecl-helper", "callsite-verified")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
