//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyTexelProfilePrepWave667 extends GhidraScript {
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
            "texel-profile-prep-wave667",
            "wave667-readback-verified",
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
        DataType doubleType = DoubleDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00581263",
                "CFastVB__TexelUnpackProfile__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave667 static read-back: texel-unpack profile destructor resets the vtable to the observed scalar-deleting destructor table and frees the vec4 scratch/output pointer at +0x1054 before returning. Static metadata only; exact C++ class layout, allocator ownership, runtime texture conversion behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "texel-profile", "destructor", "scratch-release")
            ),
            new Spec(
                "0x00581279",
                "CFastVB__ConvertTexelVectorDomain",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_vec4_array", floatPtr),
                    param("unused_context", intType)
                },
                "Wave667 static read-back: converts count-controlled vec4 texels from source_vec4_array into the scratch/output buffer at +0x1054 using source mode +0x08, target mode +0x1050, count +0x1060, observed scale/bias conversion paths for modes 1-3, and clamp-to-0..1 handling for mode 4. Static metadata only; exact texel-domain enum, color-space meaning, runtime conversion fidelity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "texel-profile", "domain-conversion", "vec4")
            ),
            new Spec(
                "0x0058183d",
                "CFastVB__TexelCodecProfile__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave667 static read-back: texel-codec profile destructor resets the codec vtable, frees per-cell allocations from the observed +0x10ec table across bounds +0x10c8/+0x10cc and +0x10bc/+0x10c4, frees +0x10e4/+0x10ec storage, then chains to CFastVB__TexelUnpackProfile__dtor. Static metadata only; exact codec-profile layout, cell table ownership, runtime codec behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "texel-codec-profile", "destructor", "nested-release")
            ),
            new Spec(
                "0x005818b7",
                "CDXTexture__PrepareDxtScaleAndQuantizedUV",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("texture_context", voidPtr) },
                "Wave667 static read-back: prepares DXT-scale metadata by checking observed FourCC values DXT2/DXT3, storing a block scale at +0x1074 and its reciprocal at +0x1078, then quantizing float bounds at +0x24/+0x28/+0x2c/+0x30 onto the observed scale grids with ROUND. Static metadata only; exact DXT format contract, UV/bounds semantics, runtime compression behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "dxt", "quantized-uv", "scale-prep")
            ),
            new Spec(
                "0x005819b8",
                "CFastVB__LookupCurveFromRsqrtScaledInput",
                "__stdcall",
                doubleType,
                new ParameterImpl[] { param("sample_value", floatType) },
                "Wave667 static read-back: computes a fast reciprocal-square-root-derived scaled index from sample_value, rounds to the nearest table slot, handles negative rounded indices with the observed unsigned-adjust constant, and linearly interpolates the table rooted at DAT_005e96d0. Static metadata only; exact curve identity, numeric equivalence, table provenance, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "curve-lookup", "reciprocal-sqrt", "table-interpolate")
            ),
            new Spec(
                "0x00581a08",
                "CFastVB__LookupCurveFromSquaredInput",
                "__stdcall",
                doubleType,
                new ParameterImpl[] { param("sample_value", floatType) },
                "Wave667 static read-back: squares sample_value, scales and rounds it to an observed table index, handles negative rounded indices with the same unsigned-adjust constant, and linearly interpolates the table rooted at DAT_005e9ad0. Static metadata only; exact curve identity, numeric equivalence, table provenance, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "curve-lookup", "squared-input", "table-interpolate")
            ),
            new Spec(
                "0x00581cc0",
                "CFastVB__TexelUnpackProfile__InitConversionScratch",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("peer_profile", voidPtr),
                    param("unused_context", intType)
                },
                "Wave667 static read-back: compares this profile mode +0x08 against peer_profile +0x08, selects +0x1050 unless mode 4 already matches, allocates count<<4 bytes for vec4 scratch/output storage at +0x1054, vector-constructs the rows, returns the observed allocation failure code on null, and mirrors +0x14 when both profiles have +0x10 set. Static metadata only; exact profile ABI, failure-code identity, scratch lifetime, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "texel-profile", "scratch-init", "vec4")
            ),
            new Spec(
                "0x00581d49",
                "CDXTexture__ProbeTexelProfileSample",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("texel_profile", voidPtr) },
                "Wave667 static read-back: temporarily rewrites texel_profile count, stride/sample pointer, source pointer, callback table, and mode fields to sample one vec4 at +0x24, optionally routes non-mode-1/non-mode-4 data through CFastVB__ConvertTexelVectorDomain, invokes vtable slots +8 and +4, then restores the saved fields. Static metadata only; exact callback contract, sample semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "texel-profile", "sample-probe", "vtable-callback")
            ),
            new Spec(
                "0x00581e1c",
                "CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("texel_vec4_array", floatPtr),
                    param("unused_context", uintType)
                },
                "Wave667 static read-back: walks count-controlled vec4 texels from texel_vec4_array and zeros all four channels when they exactly match the key vec4 stored at +0x24/+0x28/+0x2c/+0x30. Static metadata only; exact color-key policy, floating-point equality semantics, runtime transparency behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "texel-profile", "color-key", "zero-texel")
            ),
            new Spec(
                "0x00581e8c",
                "CDXTexture__NormalizeAndCopyVec4Array",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_vec4_array", floatPtr),
                    param("unused_context", intType)
                },
                "Wave667 static read-back: fills the scratch/output buffer at +0x1054 from source_vec4_array, using either table-lookup or direct fast reciprocal-square-root normalization depending on +0x14; modes 1/4 normalize RGB and copy alpha, while other modes copy RGB and normalize alpha. Static metadata only; exact normalization curve identity, mode enum, runtime image quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "texel-profile", "vec4-normalize", "scratch-copy")
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
            throw new IllegalStateException("Wave667 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
