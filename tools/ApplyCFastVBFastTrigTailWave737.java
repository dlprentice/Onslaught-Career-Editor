//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCFastVBFastTrigTailWave737 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, boolean updateSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.updateSignature = updateSignature;
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
        int commentOnlyUpdated = 0;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-fast-trig-tail-wave737",
            "wave737-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-fast-trig-tail"
        }, extras);
    }

    private String[] commentTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-fast-trig-tail-wave737",
            "wave737-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "locked-abi-comment-only",
            "cfastvb-fast-trig-tail"
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
        if (spec.updateSignature && !signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (spec.updateSignature && !signatureMatches(readBack, spec)) {
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

            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
            boolean needsAnyUpdate = needsUpdate(fn, spec);
            String signatureText = spec.updateSignature ? expectedSignature(spec) : fn.getSignature().toString();
            if (!needsAnyUpdate) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + signatureText);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " " + signatureText);
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
            }
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            else {
                stats.commentOnlyUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + signatureText);
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x005b81d0",
                "CFastVB__SinCosApproxVec4_Paired",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("angle_vec4", floatPtr),
                    param("out_sin_vec4", floatPtr),
                    param("out_cos_vec4", floatPtr)
                },
                "Wave737 static read-back: vec4 sine/cosine approximation helper called by the Euler-to-quaternion dispatch path. RET 0xc caller/decompile evidence shows three stack parameters; the helper reads four angle lanes from angle_vec4, performs table-backed sign/quadrant/range reduction with constants around 0x0065ea50 through 0x0065eb8c, and writes four sine-like lanes to out_sin_vec4 plus four cosine-like lanes to out_cos_vec4. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact polynomial identity, SIMD equivalence, floating-point accuracy, runtime math behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-head", "vec4-sincos", "ret-0xc", "quaternion-euler-caller")
            ),
            new Spec(
                "0x005b83b9",
                "CFastVB__SinCosVec4Approx",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("angle_vec4", floatPtr),
                    param("out_sin_vec4", floatPtr),
                    param("out_cos_vec4", floatPtr)
                },
                "Wave737 static read-back: vec4 sine/cosine approximation helper called by CFastVB__DispatchOp_BuildQuaternionFromEulerAngles. RET 0xc caller/decompile evidence shows three stack parameters; the helper reads four angle lanes from angle_vec4, performs sign/quadrant/range reduction with constants around 0x0065eb90 through 0x0065eccc, and writes four sine-like lanes to out_sin_vec4 plus four cosine-like lanes to out_cos_vec4. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact polynomial identity, SIMD equivalence, floating-point accuracy, runtime math behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("vec4-sincos", "ret-0xc", "quaternion-euler-caller")
            ),
            new Spec(
                "0x005b85c0",
                "Math__Atan2ApproxPacked",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave737 static read-back: packed atan2-style approximation helper called by CFastVB__DispatchOp_InterpolateQuaternionPairCore. Ghidra reports locked hidden MM0/MM1 inputs and a stale EAX-style return, while the instructions use packed reciprocal/polynomial operations and constants around 0x0065ed98 through 0x0065edf8; the current signature is intentionally retained until the packed register ABI is proven. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact packed lane layout, return register contract, polynomial identity, runtime math behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                commentTags("atan2-approx", "packed-mmx", "ret-plain")
            ),
            new Spec(
                "0x005b86c0",
                "CFastVB__FastAcosApprox_Scalar",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave737 static read-back: fast acos-style scalar/packed helper called by axis-angle extraction, quaternion normalization fallback, and spline blending paths. Ghidra reports locked hidden MM0 input and a stale EAX-style return; instructions use packed reciprocal-square-root and polynomial operations with constants around 0x0065ed9c through 0x0065edf8, so the current signature is intentionally retained until the register ABI is proven. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact packed lane layout, return register contract, polynomial identity, runtime math behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                commentTags("acos-approx", "packed-mmx", "ret-plain")
            ),
            new Spec(
                "0x005b8ca0",
                "CFastVB__FastTrigPairApprox_Scalar",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave737 static read-back: fast trigonometric pair approximation helper used by axis-angle quaternion, spline, and rotation-matrix dispatch paths. Ghidra reports locked hidden MM0 input and an unreliable visible return, while xrefs include both named dispatchers and adjacent no-function call sites; the body performs range reduction and polynomial evaluation around constants near 0x0065ee50, so the current signature is intentionally retained until the packed register ABI and neighboring boundaries are proven. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact packed lane layout, return register contract, polynomial identity, no-function caller boundaries, runtime math behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                commentTags("trig-pair-approx", "packed-mmx", "ret-plain")
            ),
            new Spec(
                "0x005b8da0",
                "CFastVB__FastSinApprox_Scalar_005b8da0",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave737 static read-back: fast sine-style scalar/packed helper used by quaternion interpolation, quaternion normalization fallback, and spline blending paths. Ghidra reports locked hidden MM0 input and an unreliable visible return; the body mirrors the nearby fast trig-pair reducer, preserves/sign-adjusts the packed result, and is left with its current signature until the packed register ABI is proven. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact packed lane layout, return register contract, polynomial identity, runtime math behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                commentTags("tranche-tail", "sin-approx", "packed-mmx", "ret-plain")
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

        println("ApplyCFastVBFastTrigTailWave737 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave737 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
