//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureResampleSurfaceVolumeWave665 extends GhidraScript {
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
            "texture-resample-wave665",
            "wave665-readback-verified",
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
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0057e0c3",
                "CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: validates matching source/destination format, dimensions, depth, and row-byte fields from the two-surface texture context, then either delegates DXT block copying or copies rows directly after palette and dirty-flag checks. Static metadata only; exact surface layout, palette contract, and runtime copy behavior remain unproven.",
                new String[] {},
                tags("texture-resample", "direct-copy", "dxt-copy")
            ),
            new Spec(
                "0x0057e200",
                "CFastVB__BlendEqualDimensionVolumeData",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: validates equal source/destination width, height, and depth fields, then copies volume rows through source vtable read slot +4 and destination vtable write slot +8 using one vector-row scratch buffer. Static metadata only; exact surface layout, vtable contract, and runtime volume-copy behavior remain unproven.",
                new String[] {},
                tags("texture-resample", "volume-copy", "equal-dimension")
            ),
            new Spec(
                "0x0057e2de",
                "CFastVB__BlendClampedVolumeData",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: handles mode byte 1 by sizing source/destination vector-row scratch buffers, copying overlapping source rows, and writing zero-filled destination rows for extents beyond the copied region. Static metadata only; exact clamped-volume semantics, surface layout, and runtime padding behavior remain unproven.",
                new String[] {},
                tags("texture-resample", "volume-copy", "clamped-volume")
            ),
            new Spec(
                "0x0057e4d3",
                "CDXTexture__ResampleSurfaceNearestNeighbor",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: handles mode byte 2 by allocating source and destination vec4 row buffers, using 16.16 stepping to choose source rows/columns, and writing nearest-neighbor destination rows. Static metadata only; exact surface layout, sampler edge rules, and runtime resample quality remain unproven.",
                new String[] {},
                tags("texture-resample", "nearest-neighbor", "surface-resample")
            ),
            new Spec(
                "0x0057e6cc",
                "CDXTexture__DownsampleSurface2x2_WithFastPaths",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: handles mode byte 5 by validating 2D half-size dimensions, trimming odd source extents, trying packed-format fast paths including the Wave664 helpers, and falling back to a vec4 2x2 average. Static metadata only; exact format table, surface layout, and runtime downsample quality remain unproven.",
                new String[] {},
                tags("texture-resample", "surface-downsample", "fast-path-dispatch")
            ),
            new Spec(
                "0x0057eadb",
                "CDXTexture__DownsampleVolume2x2x2",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: handles mode byte 5 by validating 3D half-size dimensions, trimming odd source extents, staging source vec4 row planes, and averaging observed 2x2x2 samples into destination rows. Static metadata only; exact volume layout, edge handling, and runtime downsample quality remain unproven.",
                new String[] {},
                tags("texture-resample", "volume-downsample", "average2x2x2")
            ),
            new Spec(
                "0x0057ef10",
                "CFastVB__BuildResampleKernel1D",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] { param("wrap_edges", intType) },
                "Wave665 static read-back: builds an allocated one-dimensional resample-kernel table from source/destination counts held in caller registers, storing low/high sample indices and bilinear weights while wrap_edges controls observed edge wrapping versus clamping. Static metadata only; exact register-carried count contract, edge-mode naming, and allocation ownership remain unproven.",
                new String[] {},
                tags("texture-resample", "resample-kernel", "bilinear-kernel")
            ),
            new Spec(
                "0x0057f002",
                "CDXTexture__ResampleSurfaceBilinear",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: handles mode byte 3 for single-slice surfaces by building X/Y resample kernels, caching two source rows, bilinearly combining vec4 channels, and writing destination rows. Static metadata only; exact kernel layout, edge rules, and runtime bilinear quality remain unproven.",
                new String[] {},
                tags("texture-resample", "bilinear", "surface-resample")
            ),
            new Spec(
                "0x0057f391",
                "CDXTexture__ResampleVolumeTrilinear",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("texture_resample_context", voidPtr) },
                "Wave665 static read-back: handles mode byte 3 for volumes by building X/Y/Z resample kernels, caching four source row planes, trilinearly combining vec4 channels, and writing destination volume rows. Static metadata only; exact kernel layout, edge rules, and runtime trilinear quality remain unproven.",
                new String[] {},
                tags("texture-resample", "trilinear", "volume-resample")
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
            throw new IllegalStateException("Wave665 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
