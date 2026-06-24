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

public class ApplyTextureFormatUploadWave656 extends GhidraScript {
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
            "texture-format-upload-wave656",
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
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00574270",
                "CDXTexture__FindFormatDescriptorById",
                "__stdcall",
                intPtr,
                new ParameterImpl[] {
                    param("format_id", intType)
                },
                "Wave656 texture format/upload hardening: stdcall lookup walks the descriptor table from DAT_005e6a68 to PTR_DAT_00656f28 in 9-dword rows, returns the matching descriptor for format_id, and falls back to DAT_005e6a40 when no row matches. Static retail decompile/xref evidence only; exact descriptor layout, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "format-descriptor", "descriptor-table")
            ),
            new Spec(
                "0x00574296",
                "CFastVB__ComputeFormatMatchPenalty",
                "__fastcall",
                uintType,
                new ParameterImpl[] {
                    param("requested_descriptor", voidPtr),
                    param("candidate_descriptor", voidPtr)
                },
                "Wave656 texture format/upload hardening: fastcall scorer rejects incompatible descriptor pairs through the DAT_005e7270 matrix, then accumulates weighted field-difference penalties across five descriptor slots. Static retail evidence only; exact descriptor schema, CFastVB owner identity, runtime format quality, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "format-scoring", "compatibility-matrix")
            ),
            new Spec(
                "0x0057430b",
                "CDXTexture__SelectBestCompatibleFormat",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("format_id_list", voidPtr),
                    param("allow_mode_one_descriptor", intType),
                    param("requested_descriptor", voidPtr)
                },
                "Wave656 texture format/upload hardening: stdcall selector scans a zero-terminated format-id list, resolves rows through CDXTexture__FindFormatDescriptorById, accepts an exact descriptor match first, otherwise scores candidates with CFastVB__ComputeFormatMatchPenalty and tie-breaks on descriptor priority. Static retail evidence only; exact descriptor fields and runtime device compatibility remain unproven.",
                new String[] {},
                tags("cdxtexture", "format-selection", "descriptor-penalty", "zero-terminated-list")
            ),
            new Spec(
                "0x0057437a",
                "CFastVB__SelectBestFormatHandler",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("device_or_null", voidPtr),
                    param("usage_flags", uintType),
                    param("resource_type", intType),
                    param("requested_descriptor", voidPtr)
                },
                "Wave656 texture format/upload hardening: stdcall handler mutes D3D debug output, optionally probes a device-like vtable for candidate descriptor support, scores compatible rows with CFastVB__ComputeFormatMatchPenalty, and restores debug output before returning the selected format id. Static retail evidence only; exact device interface, descriptor schema, runtime format behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "format-handler", "d3d-probe", "debug-mute", "format-selection")
            ),
            new Spec(
                "0x00574476",
                "CDXTexture__MapFormatTokenToInternalCode",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("format_token", intType)
                },
                "Wave656 texture format/upload hardening: stdcall token mapper translates the AL16 and R16 FourCC-style texture tokens to internal format codes 0x33 and 0x14 and returns other tokens unchanged. Static retail decompile/xref evidence only; full texture-format taxonomy and runtime decode behavior remain unproven.",
                new String[] {},
                tags("cdxtexture", "format-token", "fourcc-map")
            ),
            new Spec(
                "0x00574577",
                "CFastVB__ReturnInputInt",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("value", intType)
                },
                "Wave656 texture format/upload hardening: retained-name fastcall identity helper returns value unchanged; current static evidence is the one-instruction body plus data references from texture profile/conversion tables. Static retail evidence only; helper provenance and runtime table semantics remain unproven.",
                new String[] {},
                tags("cfastvb", "identity-callback", "retained-name")
            ),
            new Spec(
                "0x0057457a",
                "CDXTexture__LoadAndUploadMappedTexture_0057457a",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("target_ref", voidPtr),
                    param("mode_flags", voidPtr),
                    param("surface_ref", voidPtr),
                    param("context_ref", voidPtr),
                    param("fallback_ref", voidPtr)
                },
                "Wave656 texture format/upload hardening: address-suffixed stdcall helper builds a temporary surface/upload state, calls mapped-texture resource loading and upload helpers, returns D3D-style status codes, and still shows implicit EAX/ESI state in the decompile. Static retail evidence only; exact calling storage, file/texture object ownership, runtime upload behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "mapped-texture-upload", "implicit-register-state", "surface-tree", "address-suffixed-helper")
            ),
            new Spec(
                "0x00574645",
                "Platform__LoadAndUploadMappedTextureWrapper",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("target_ref", voidPtr),
                    param("mode_flags", voidPtr),
                    param("unused_surface_ref", voidPtr),
                    param("context_ref", voidPtr),
                    param("fallback_ref", voidPtr)
                },
                "Wave656 texture format/upload hardening: stdcall platform wrapper forwards target_ref, mode_flags, context_ref, fallback_ref, and a null final argument into CDXTexture__LoadAndUploadMappedTexture_0057457a while leaving the third stack argument unused; screen-dump processing observes its register side effects. Static retail evidence only; exact wrapper ABI and runtime screen-dump texture upload behavior remain unproven.",
                new String[] {},
                tags("platform-wrapper", "screen-dump", "mapped-texture-upload", "ignored-arg")
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
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun && (stats.bad != 0 || stats.missing != 0)) {
            throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
