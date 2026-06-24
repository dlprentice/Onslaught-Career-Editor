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

public class ApplyTextureDualProfileUploadWave666 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] allowedExistingNames, String[] tags) {
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
            "texture-dual-profile-wave666",
            "wave666-readback-verified",
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
        DataType intPtr = new PointerDataType(intType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0057fa10",
                "CFastVB__BlendWeightTable_scalar_deleting_dtor",
                "__thiscall",
                intPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType),
                    param("unused_context", intType)
                },
                "Wave666 static read-back: deleting-destructor wrapper for allocated blend-weight table storage; delete_flags bit 2 backs up to the count prefix and runs CDXTexture__RepeatCallbackN with the observed entry cleanup callback before optional base free, while bit 1 controls object/base freeing. Static metadata only; exact C++ container identity, callback body semantics, allocator ownership, runtime conversion behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dual-profile", "blend-weight-table", "deleting-dtor")
            ),
            new Spec(
                "0x0057fa5c",
                "CFastVB__BlendDualProfileBoneWeights",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("dual_profile_context", voidPtr) },
                "Wave666 static read-back: builds X/Y/Z resample bucket tables from source/destination profile extents at +0x1060/+0x1064/+0x1068, allocates vec4 scratch rows and 0xc-byte weight-table entries, reads source profile rows through vtable slot +4, accumulates weighted 4-float vectors, clamps observed modes 1-3, writes destination rows through vtable slot +8, and releases scratch storage. Static metadata only; exact profile/layout identity, retained CFastVB owner label, runtime blend quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dual-profile", "weighted-resample", "vec4-scratch")
            ),
            new Spec(
                "0x00580120",
                "CFastVB__RunDualProfileConversionStage",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("dual_profile_context", voidPtr) },
                "Wave666 static read-back: validates source/destination depth fields at +0x1068 are single-slice, builds X/Y resample bucket tables, allocates temporary vec4 rows and weight-table entries, reads source rows through vtable slot +4, applies weighted 2D conversion with observed mode clamps, writes destination rows through vtable slot +8, and releases scratch storage. Static metadata only; exact profile layout, clamp semantics, runtime conversion quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dual-profile", "conversion-stage", "weighted-resample")
            ),
            new Spec(
                "0x0058070e",
                "CFastVB__InitDualTexelConversionPipeline",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_profile_descriptor", voidPtr),
                    param("destination_profile_descriptor", voidPtr),
                    param("conversion_flags", intType),
                    param("unused_context", uintType)
                },
                "Wave666 static read-back: initializes the two-profile conversion state, validates the low conversion mode and high flag mask, writes observed flag bits into descriptor fields +0x40/+0x44, creates paired texel-unpack profiles, initializes conversion scratch, tries the direct copy/resample/downsample helpers through the dual-profile weighted stages, then releases both active profiles. Static metadata only; exact descriptor layout, flag enum, profile ABI, runtime texture conversion behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "dual-profile", "texel-unpack", "conversion-dispatch")
            ),
            new Spec(
                "0x0058083d",
                "CDXTexture__ResetSurfaceCopyContext",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("surface_copy_context", voidPtr) },
                "Wave666 static read-back: clears five consecutive dwords in the surface-copy/upload context at offsets +0x00 through +0x10. Static metadata only; exact context ownership, COM/D3D surface semantics, runtime upload behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "surface-copy", "upload-context", "context-reset")
            ),
            new Spec(
                "0x00580850",
                "CDXTexture__CopyLockedRectPitchAware",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("source_surface", voidPtr),
                    param("destination_surface", voidPtr)
                },
                "Wave666 static read-back: queries the source surface descriptor, locks source and destination rectangles through vtable slot +0x34, adjusts DXT-style row count for observed FourCC values DXT1-DXT5, copies min(source_pitch,destination_pitch) bytes per row, advances each pitch independently, and unlocks both surfaces. Static metadata only; exact locked-rect layout, D3D interface identity, runtime copy fidelity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "surface-copy", "locked-rect", "pitch-aware", "dxt")
            ),
            new Spec(
                "0x0058092d",
                "CDXTexture__FinalizeTextureUploadAndReleaseTemp",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("upload_context", voidPtr) },
                "Wave666 static read-back: unlocks the active temporary/destination surface when present, attempts a device vtable +0x78 surface update with D3D9 debug mute toggled, falls back to CDXTexture__CopyLockedRectPitchAware on failure, releases observed surface/device/context slots at +0x04/+0x08/+0x0c/+0x10, clears them, and returns zero. Static metadata only; exact COM interface contract, UpdateSurface identity, runtime upload behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "surface-upload", "release-temp", "fallback-copy")
            ),
            new Spec(
                "0x005809de",
                "CFastVB__ShutdownActiveProfile",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("active_profile_slot", voidPtr) },
                "Wave666 static read-back: releases an active profile pointer by calling vtable slot +0x28 first, then vtable slot +0x08 if the pointer remains present, clears the slot, and returns zero. Static metadata only; exact profile vtable contract, retained CFastVB owner label, runtime profile lifetime, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "profile-lifetime", "active-profile", "release")
            ),
            new Spec(
                "0x00580a00",
                "CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("upload_context", voidPtr) },
                "Wave666 static read-back: duplicate/tail entry for the texture-upload finalizer; it follows the same unlock, debug-muted device update, pitch-aware fallback copy, release, clear, and zero-return pattern as 0x0058092d. Static metadata only; exact duplicate-entry reason, COM interface contract, runtime upload behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "surface-upload", "release-temp", "duplicate-entry")
            ),
            new Spec(
                "0x00580eef",
                "CFastVB__ShutdownActiveProfile_Thunk",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("active_profile_slot", voidPtr) },
                "Wave666 static read-back: thunk/alias entry to the active-profile shutdown body, calling profile vtable slot +0x28, then slot +0x08 if still present, clearing the slot, and returning zero. Static metadata only; exact thunk ABI, profile vtable contract, retained CFastVB owner label, runtime profile lifetime, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "profile-lifetime", "active-profile", "thunk")
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
            throw new IllegalStateException("Wave666 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
