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

public class ApplyTextureDownsampleKernelsWave664 extends GhidraScript {
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
            "texture-downsample-wave664",
            "wave664-readback-verified",
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
                "0x0057d216",
                "CFastVB__DispatchMmxKernel_00657974",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: reads source/destination surface pointers and extent/stride fields from the two-slot downsample context, then calls the CPU-selected MMX-style kernel pointer at 0x00657974. Static metadata only; exact surface/context layout, CPU dispatch identity, and runtime downsample behavior remain unproven.",
                new String[] {},
                tags("texture-downsample", "mmx-dispatch", "cpu-dispatch")
            ),
            new Spec(
                "0x0057d4ad",
                "CFastVB__DispatchMmxKernel_00657978",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: reads source/destination surface pointers and extent/stride fields from the two-slot downsample context, then calls the CPU-selected MMX-style kernel pointer at 0x00657978. Static metadata only; exact surface/context layout, CPU dispatch identity, and runtime downsample behavior remain unproven.",
                new String[] {},
                tags("texture-downsample", "mmx-dispatch", "cpu-dispatch")
            ),
            new Spec(
                "0x0057d4db",
                "CDXTexture__Average2x2Block_RGB565",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed 16-bit source texels into one RGB565-style destination texel using 0xf81f/0x07e0 channel masks and rounded sums. Static metadata only; exact surface layout and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "rgb565")
            ),
            new Spec(
                "0x0057d62b",
                "CDXTexture__Average2x2Block_RGB555",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed 16-bit source texels into one RGB555-style destination texel using 0x7c1f/0x03e0 channel masks and rounded sums. Static metadata only; exact surface layout and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "rgb555")
            ),
            new Spec(
                "0x0057d74f",
                "CDXTexture__Average2x2Block_ARGB1555",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed 16-bit source texels into one ARGB1555-style destination texel using 0x83e0/0x7c1f masks and rounded sums. Static metadata only; exact alpha handling, surface layout, and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "argb1555")
            ),
            new Spec(
                "0x0057d89e",
                "CDXTexture__Average2x2Block_A4R4G4B4",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed 16-bit source texels into one A4R4G4B4-style destination texel using 0xf0f0/0x0f0f channel masks and rounded sums. Static metadata only; exact surface layout and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "a4r4g4b4")
            ),
            new Spec(
                "0x0057d9f1",
                "CFastVB__Downsample2x1_R5G6B5",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: retained-name byte-lane helper reads paired source samples from adjacent rows and writes one packed output byte using 0xe3/0x1c masks and rounded sums. Static metadata only; exact packed-format contract, owner identity, and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "downsample2x1", "packed-byte")
            ),
            new Spec(
                "0x0057db30",
                "CFastVB__Downsample2x1_L8",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: retained-name byte-luminance helper averages observed 2x2 source bytes into one destination byte with a rounded +2 bias. Static metadata only; exact L8 surface layout, owner identity, and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "downsample2x1", "l8")
            ),
            new Spec(
                "0x0057dbcb",
                "CFastVB__Downsample2x1_A1R5G5B5",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: retained-name helper averages observed packed 16-bit source texels through 0xe3/0xff1c-style masks and rounded sums before writing a destination word. Static metadata only; exact A1R5G5B5 contract, owner identity, and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "downsample2x1", "a1r5g5b5")
            ),
            new Spec(
                "0x0057dd17",
                "CDXTexture__Average2x2Block_RGB444",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed 16-bit source texels into one RGB444-style destination texel using 0x0f0f/0x00f0 masks and rounded sums. Static metadata only; exact surface layout and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "rgb444")
            ),
            new Spec(
                "0x0057de38",
                "CDXTexture__Average2x2Block_A8L8",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed 16-bit source texels into one A8L8-style destination texel by separately accumulating low and high byte lanes with rounded sums. Static metadata only; exact surface layout and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "a8l8")
            ),
            new Spec(
                "0x0057df84",
                "CDXTexture__Average2x2Block_A4L4",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("downsample_context", voidPtr) },
                "Wave664 static read-back: averages observed 2x2 packed byte source samples into one A4L4-style destination byte using 0xf0/0x0f masks and rounded sums. Static metadata only; exact surface layout and runtime filter quality remain unproven.",
                new String[] {},
                tags("texture-downsample", "average2x2", "a4l4")
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
            throw new IllegalStateException("Wave664 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
