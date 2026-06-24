//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyLandscapeTextureWave421 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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
            "landscape-texture-wave421",
            "retail-binary-evidence"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType byteType = ByteDataType.dataType;
        DataType bytePtr = new PointerDataType(ByteDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0048e310",
                "CLandscapeTexture__FreeTexture",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: releases the CLandscapeTexture texture/surface pointer at +0x08 through OID__FreeObject when present, then clears the field. Static retail evidence only; exact class layout, texture ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "texture-lifetime", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0048e330",
                "CLandscapeTexture__Constructor",
                "__thiscall",
                voidPtr,
                "Wave421 signature/comment hardening: CLandscapeTexture base constructor calls CIBuffer__Constructor, installs the 0x005dc1d8 vtable pointer, clears dirty/update state at +0x2c, and returns this. Static retail evidence only; the adjacent vtable layout still has unconfirmed entries, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "constructor", "vtable-context", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0048e360",
                "CLandscapeTexture__SetupMipLevel",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: stores mip_level at +0x24 and edge_flags at +0x28, computes a 2<<mip_level tile edge at +0x2c, derives the byte count at +0x30 with edge-flag reductions for bits 1/2/4/8, sets shared/static mode at +0x18, then dispatches vtable slot +0x04. Static retail evidence only; exact source body identity, vtable-slot target identity, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "mip-level", "vtable-dispatch", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("mip_level", intType), param("edge_flags", uintType)}
            ),
            new Spec(
                "0x0048e430",
                "CLandscapeTexture__ConstructorMip",
                "__thiscall",
                voidPtr,
                "Wave421 signature/comment hardening: mip-texture constructor calls the CUMTexture constructor-like base path, installs the 0x005dc1f0 vtable pointer, clears dirty/update state at +0x2c, clears the update buffer pointer at +0x40, and returns this. Static retail evidence only; adjacent vtable entries remain provisional, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "constructor", "mip-texture", "vtable-context", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0048e450",
                "CLandscapeTexture__Destructor",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: destructor restores the 0x005dc1f0 vtable, frees the update buffer at +0x40, decrements the global CLandscapeTexture count at 0x006fabf8, releases shared texture state 0x006fabf4 when the count reaches zero, then calls the CUMTexture destructor-like base path. Static retail evidence only; exact ownership semantics, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "destructor", "shared-texture-lifetime", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0048e4d0",
                "CLandscapeTexture__Init",
                "__thiscall",
                intType,
                "Wave421 signature/comment hardening: initializes mip level and tile-set index, writes U/V masks at +0x48/+0x4a, derives texture size/mask fields +0x38/+0x3c, dispatches vtable slot +0x04, allocates/fills the nonzero-mip update buffer at +0x40/+0x44, configures the CUMTexture path, and refreshes shared texture/device state. Static retail evidence only; one decompile path still exposes register-carryover around the configure call, so exact call signature, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "init", "mip-level", "update-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("mip_level", intType), param("tile_set_index", intType)}
            ),
            new Spec(
                "0x0048e610",
                "CLandscapeTexture__Reset",
                "__thiscall",
                uintType,
                "Wave421 signature/comment hardening: calls the CUMTexture reset/vfunc path, returns early on negative status, then when dirty state is set resets +0x2c to one, fills the update buffer at +0x40 with 0xff when present, or refreshes the full 0..63 tile range through CLandscapeTexture__UpdateTileRange. Static retail evidence only; exact HRESULT semantics, runtime texture refresh behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "reset", "update-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0048e7b0",
                "CLandscapeTexture__ResetUpdateQueue",
                "__cdecl",
                voidType,
                "Wave421 signature/comment hardening: resets the global landscape tile-update cursor 0x0062d868 back to the queue base 0x006fa7d8. Static retail evidence only; queue lifetime, runtime update ordering, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "update-queue", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x0048e7c0",
                "CLandscapeTexture__FlushUpdateQueue",
                "__cdecl",
                voidType,
                "Wave421 signature/comment hardening: walks 20-byte landscape update records between 0x006fa7d8 and cursor 0x0062d868, calls CLandscapeTexture__UpdateTile for immediate/eligible entries, compacts deferred records in place, records X/x trace characters on the stack, and writes the compacted cursor back. Static retail evidence only; exact scheduling semantics, runtime update ordering, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "update-queue", "queue-flush", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x0048e880",
                "CLandscapeTexture__QueueTileUpdate",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: converts tile_coord into mip/mask-adjusted texture X/Y, deduplicates an existing queue record for the same receiver/tile, preserves immediate-update mode when an existing record is already immediate, flushes near the 0x006fabbf queue cap, then appends one 20-byte update record. Static retail evidence only; exact update_mode enum, runtime queue behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "update-queue", "tile-coordinate", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("tile_coord", uintType), param("update_mode", intType)}
            ),
            new Spec(
                "0x0048e950",
                "CLandscapeTexture__CopyTileToTexture",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: when global mip level 0x006fabf0 is active, scales the caller tile_rect, locks either shared texture 0x006fabf4 or the per-instance texture at +0x08, copies RGB565 pixels from the 0x0067a7d8 landscape buffer into the locked destination, then unlocks the shared/per-instance texture. Static retail evidence only; exact rect structure, runtime GPU upload behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "texture-copy", "rgb565", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("tile_rect", intPtr)}
            ),
            new Spec(
                "0x0048ea80",
                "CLandscapeTexture__UpdateTile",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: marks the texture dirty, derives a tile rectangle from tile_coord, object mip level, and global mip level, locks the shared/per-instance texture or uses the 0x0067a7d8 intermediate buffer, blits the terrain tile via CLandscapeTexture__BlitTileRegionWithLightingMask, applies overlay alpha entries through CLandscapeTexture__BlendAlpha, copies or unlocks the tile, and refreshes device state when using shared textures. Static retail evidence only; exact overlay record layout, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "tile-update", "rgb565", "alpha-overlay", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("tile_coord", uintType)}
            ),
            new Spec(
                "0x0048ee00",
                "CLandscapeTexture__BlendAlpha",
                "__cdecl",
                voidType,
                "Wave421 signature/comment hardening: clips an alpha mask square against the destination bounds, walks the destination RGB565 buffer with the supplied pitch, and for alpha bytes below 0x20 blends packed RGB565 channels through the 0x07e0f81f parallel-channel mask. Static retail evidence only; exact overlay asset semantics, runtime visual parity, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "alpha-blend", "rgb565", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("dest", shortPtr),
                    param("pitch", intType),
                    param("alpha", bytePtr),
                    param("x", intType),
                    param("y", intType),
                    param("level", byteType),
                    param("size", intType)
                }
            ),
            new Spec(
                "0x0048ef00",
                "CLandscapeTexture__UpdateTileRange",
                "__thiscall",
                voidType,
                "Wave421 signature/comment hardening: updates an inclusive tile range by deriving the pixel rectangle, locking the shared/per-instance texture or using 0x0067a7d8, looping tile flags from min_y*64+min_x through max bounds, blitting each tile, applying linked overlay alpha entries, copying the rect through CLandscapeTexture__CopyTileToTexture, and refreshing device state for shared textures. Static retail evidence only; exact tile flag semantics, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("landscape-texture", "tile-range", "tile-update", "alpha-overlay", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("min_x", intType),
                    param("min_y", intType),
                    param("max_x", intType),
                    param("max_y", intType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave421 LandscapeTexture apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
