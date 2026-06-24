//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyTexelFactoryTailWave676 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] baseTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texel-factory-tail-wave676",
            "wave676-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
        }, extras);
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
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
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

    private ParameterImpl[] ctorParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("format_descriptor", voidPtr)
        };
    }

    private ParameterImpl[] dtorParams(DataType voidPtr, DataType uintType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("delete_flags", uintType)
        };
    }

    private ParameterImpl[] factoryParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("format_descriptor", voidPtr)
        };
    }

    private Spec spec(String address, String name, String callingConvention, DataType returnType,
            ParameterImpl[] params, String comment, String... tags) {
        return new Spec(address, name, callingConvention, returnType, params, comment, baseTags(tags));
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        ParameterImpl[] ctorParams = ctorParams(voidPtr);
        ParameterImpl[] dtorParams = dtorParams(voidPtr, uintType);
        ParameterImpl[] factoryParams = factoryParams(voidPtr);

        Spec[] specs = new Spec[] {
            spec(
                "0x00587dee",
                "CFastVB__InitTexelUnpackVTable_005ea264",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave676 static read-back: profile-init thunk forwards the format descriptor to the 0x005ea138 unpack-profile registry initializer, binds vtable 0x005ea264, and returns this. Static metadata only; exact FourCC mapping, descriptor ABI, and runtime texture output remain unproven.",
                "texel-unpack-profile-registry", "format-factory-case", "packed-fourcc-case", "vtable-binding", "vtable-005ea264"
            ),
            spec(
                "0x00587e06",
                "CFastVB__InitTexelUnpackVTable_005ea274",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave676 static read-back: profile-init thunk forwards the format descriptor to the 0x005ea138 unpack-profile registry initializer, binds vtable 0x005ea274, and returns this. Static metadata only; exact FourCC mapping, descriptor ABI, and runtime texture output remain unproven.",
                "texel-unpack-profile-registry", "format-factory-case", "packed-fourcc-case", "vtable-binding", "vtable-005ea274"
            ),
            spec(
                "0x00587e1e",
                "CFastVB__TexelUnpackProfileRegistry_005ea284__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave676 static read-back: registry constructor forwards the format descriptor to the 0x005ea138 unpack-profile registry initializer, binds vtable 0x005ea284, and returns this. Static metadata only; exact FourCC mapping, descriptor ABI, and runtime texture output remain unproven.",
                "texel-unpack-profile-registry", "format-factory-case", "packed-fourcc-case", "vtable-binding", "vtable-005ea284"
            ),
            spec(
                "0x00587e36",
                "CFastVB__TexelCodecProfile_005ea294__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave676 static read-back: codec-profile constructor forwards the format descriptor through the FourCC codec initializer, binds vtable 0x005ea294, and returns this. Factory evidence routes one DXT FourCC case here after a 0x10f0-byte allocation. Static metadata only; exact DXT block ABI and runtime texture output remain unproven.",
                "texel-codec-profile", "format-factory-case", "dxt-codec", "vtable-binding", "vtable-005ea294"
            ),
            spec(
                "0x00587e4e",
                "CFastVB__TexelCodecProfile_005ea2a4__ctor",
                "__thiscall",
                voidPtr,
                ctorParams,
                "Wave676 static read-back: codec-profile constructor forwards the format descriptor through the FourCC codec initializer, binds vtable 0x005ea2a4, and returns this. Factory evidence routes one DXT FourCC case here after a 0x10f0-byte allocation. Static metadata only; exact DXT block ABI and runtime texture output remain unproven.",
                "texel-codec-profile", "format-factory-case", "dxt-codec", "vtable-binding", "vtable-005ea2a4"
            ),
            spec(
                "0x00587e66",
                "CFastVB__TexelCodecProfile_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                dtorParams,
                "Wave676 static read-back: scalar-deleting destructor calls the codec-profile destructor, optionally frees this when delete_flags bit 0 is set, and returns this. Static metadata only; exact class ownership and allocator contract remain unproven.",
                "texel-codec-profile", "scalar-deleting-dtor", "codec-profile-dtor", "optional-object-free"
            ),
            spec(
                "0x00587e82",
                "CFastVB__CreateTexelUnpackProfileByFormat",
                "__stdcall",
                voidPtr,
                factoryParams,
                "Wave676 static read-back: factory reads the format descriptor id at +0x4, dispatches numeric and FourCC-like cases, allocates profile objects sized 0x1074/0x10a4/0x10f0, calls the matching profile constructor, and invokes the observed setup callback when present. Static metadata only; exact format enum, descriptor ABI, and runtime texture output remain unproven.",
                "texel-profile-factory", "format-dispatch", "allocation-size-switch", "setup-callback", "numeric-format-cases", "fourcc-format-cases"
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
            throw new IllegalStateException("Wave676 apply encountered missing/bad rows");
        }
    }
}
