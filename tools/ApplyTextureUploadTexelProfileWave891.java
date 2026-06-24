//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureUploadTexelProfileWave891 extends GhidraScript {
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
            "texture-upload-texel-profile-wave891",
            "wave891-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "texture-upload",
            "texel-profile",
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
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("MISSING_READBACK: " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("BADNAME_READBACK: " + spec.address + " got " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("BADSIG_READBACK: " + spec.address + " got " + fn.getSignature());
        }
        String comment = fn.getComment();
        if (comment == null || !comment.equals(spec.comment)) {
            throw new IllegalStateException("BADCOMMENT_READBACK: " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("BADTAGS_READBACK: " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    return;
                }
                stats.renamed++;
                println("RENAME_BLOCKED_BY_POLICY: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getSignature().toString().equals(spec.signature)) {
                println("BADSIG: " + spec.address + " got " + fn.getSignature() + " expected " + spec.signature);
                stats.bad++;
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
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x00580a05",
                "CDXTexture__UploadSurfaceRegionWithFallback",
                "int CDXTexture__UploadSurfaceRegionWithFallback(void)",
                "Wave891 static read-back: texture upload/lock descriptor builder reached from CDXTexture__UploadDecodedBufferToSurface, CDXTexture__LoadAndUploadMappedTexture_0057457a, and CDXTexture__CopyOrUploadSurfaceRegionWithFallback. Static retail Ghidra evidence only: finalizes prior upload state, reads the source surface descriptor through vtable slot 0x30, validates optional rectangles, aligns DXT and packed YUY2/RGBG/UYVY-style regions, creates and locks a temporary surface for the 0x10000 flag path, mutes D3D debug output around lock/copy fallback calls, releases failed temporary objects, and fills the output upload descriptor before AddRefing the source surface. Exact texture surface/context layout, hidden stack ABI, Direct3D interface identity, runtime upload behavior, BEA patching, and rebuild parity remain unproven.",
                tags("surface-upload", "d3d-lock-fallback", "dxt-region-alignment")
            ),
            new Spec(
                "0x00580ef4",
                "CDXTexture__CreateTexelCodecProfileFromSurfaceDesc",
                "int CDXTexture__CreateTexelCodecProfileFromSurfaceDesc(void)",
                "Wave891 static read-back: active texel codec profile descriptor builder reached from CDXTexture__ConvertSurfaceWithActiveProfile and CDXTexture__ConvertSurfaceRegionWithActiveProfile. Static retail Ghidra evidence only: shuts down an existing active profile, reads a surface descriptor through vtable slot 0x20, validates a six-dword optional region, rejects unsupported descriptor/flag combinations, aligns DXT and packed YUY2/RGBG/UYVY-style regions, optionally probes format support under D3D debug mute, locks the source surface through vtable slot 0x24, fills the profile descriptor fields, and AddRefs the source surface. Exact texel profile ABI, texture surface/context layout, descriptor flag semantics, runtime conversion behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texel-profile-descriptor", "surface-lock", "dxt-region-alignment")
            ),
            new Spec(
                "0x00581a4f",
                "CFastVB__TexelUnpackProfile__ctorFromDescriptor",
                "int CFastVB__TexelUnpackProfile__ctorFromDescriptor(void)",
                "Wave891 static read-back: shared texel-unpack profile constructor reached by the broad CFastVB profile-constructor fan-in from 0x0058577f through 0x00587477. Static retail Ghidra evidence only: installs the base profile vtable 0x005e9ed0, vector-constructs 0x100 entries, copies descriptor bounds/stride/format fields, selects lookup table globals DAT_00657980 or DAT_00657a00, normalizes key-color bytes into floats, initializes all-one or descriptor-backed lookup rows for formats 0x28/0x29, computes active width/height/depth and row-span fields, and adjusts the base pointer when a row/depth pitch is present. Exact texel profile layout, descriptor layout, palette/key-color contract, runtime unpack behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texel-unpack-profile", "constructor-fan-in", "lookup-table-init")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave891 apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
