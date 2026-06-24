//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtLongDoubleConversionWave642 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-longdouble-conversion-wave642",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
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
        } else {
            for (int i = 0; i < spec.parameters.length; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.parameters[i].getDataType().getDisplayName())
                  .append(" ")
                  .append(spec.parameters[i].getName());
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(expectedSignature(spec))) {
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
        String actualSignature = readBack.getSignature().toString();
        String expectedSignature = expectedSignature(spec);
        if (!actualSignature.equals(expectedSignature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature);
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
            if (!nameAllowed(fn.getName(), spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
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
            stats.signatureUpdated++;
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " -> " + functionAtEntry(spec.address).getSignature().toString());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intPtr = new PointerDataType(intType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005698e3",
                "CRT__ConvertLongDoubleByFormatSpec",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("longDouble80", voidPtr), param("outBits", voidPtr), param("formatSpec", voidPtr)},
                "Wave642 CRT long-double conversion hardening: converts an internal 80-bit-style long-double record into float32 or float64 bit output using a format-spec table, Wave641 96-bit mantissa helpers, exponent bounds, rounding, and output-width fields. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "format-spec", "rounding", "float32", "float64")
            ),
            new Spec(
                "0x00569a4f",
                "CRT__ConvertLongDoubleToFloat32",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("longDouble80", voidPtr), param("outFloat32Bits", voidPtr)},
                "Wave642 CRT long-double conversion hardening: float32 wrapper that passes the internal long-double record, output pointer, and DAT_006561c0 format-spec table to CRT__ConvertLongDoubleByFormatSpec. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "format-spec", "float32")
            ),
            new Spec(
                "0x00569a65",
                "CRT__ConvertLongDoubleToFloat64",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("longDouble80", voidPtr), param("outFloat64Bits", voidPtr)},
                "Wave642 CRT long-double conversion hardening: float64 wrapper that passes the internal long-double record, output pointer, and DAT_006561d8 format-spec table to CRT__ConvertLongDoubleByFormatSpec. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "format-spec", "float64")
            ),
            new Spec(
                "0x00569a7b",
                "CRT__ParseFloatTextToFloat32",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("outFloat32Bits", voidPtr), param("parseFlags", intType)},
                "Wave642 CRT long-double conversion hardening: parse wrapper that stages a 12-byte long-double scratch value through CRT__ParseFloatTextToLongDouble and then writes float32 output through CRT__ConvertLongDoubleToFloat32. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "parser", "float32")
            ),
            new Spec(
                "0x00569aa8",
                "CRT__ParseFloatTextToFloat64",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("outFloat64Bits", voidPtr), param("parseFlags", intType)},
                "Wave642 CRT long-double conversion hardening: parse wrapper that stages a 12-byte long-double scratch value through CRT__ParseFloatTextToLongDouble and then writes float64 output through CRT__ConvertLongDoubleToFloat64. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "parser", "float64")
            ),
            new Spec(
                "0x00569ad5",
                "CRT__BuildRoundedMantissaDigits",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("outDigits", charPtr), param("requestedDigits", intType), param("decimalRecord", voidPtr)},
                "Wave642 CRT long-double conversion hardening: fills the output digit string from decimalRecord+0xc, pads with zeroes, rounds upward when the next source digit is greater than '4', carries through runs of '9', and increments the decimal exponent field when a leading carry appears. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "decimal-record", "rounding", "digits")
            ),
            new Spec(
                "0x00569b4c",
                "CRT__ConvertLongDoubleToDecimalRecord",
                new String[] {},
                "__cdecl",
                intPtr,
                new ParameterImpl[] {param("inputLowBits", intType), param("inputHighBits", intType), param("decimalRecord", voidPtr), param("digitsBuffer", charPtr)},
                "Wave642 CRT long-double conversion hardening: converts the low/high input bits through CRT__NormalizeLongDouble80MantissaExp, calls the decimal conversion core, stores sign/exponent/class fields into decimalRecord, copies generated digits into digitsBuffer, records that digits pointer at decimalRecord+0xc, and returns decimalRecord. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "decimal-record", "digits")
            ),
            new Spec(
                "0x00569ba8",
                "CRT__NormalizeLongDouble80MantissaExp",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("outLongDouble80", voidPtr), param("float64Bits", voidPtr)},
                "Wave642 CRT long-double conversion hardening: normalizes IEEE-754-style float64 bits into the local long-double-style mantissa/exponent record, handling zero, denormal, finite, and Inf/NaN exponent classes before left-normalizing the mantissa and storing the sign/exponent word. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "normalize", "float64")
            ),
            new Spec(
                "0x00569cc1",
                "CRT__HandleFloatingPointException",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("unusedStatus", intType), param("fpExceptionRecord", voidPtr), param("controlWordPtr", voidPtr)},
                "Wave642 CRT long-double conversion hardening: FPU exception sink reached from __startOneArgErrorHandling and CRT__FpuIntDispatch2_Handle; maps source-kind values to active floating-point flags, adjusts the saved record using the control word, raises when adjustment fails, and sets errno for the final source kind. Static CRT floating-point conversion evidence only; exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "fpu-exception", "errno")
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
            throw new IllegalStateException("Wave642 had missing/bad rows");
        }
    }
}
