//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtFpuFormatWave627 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                boolean updateSignature,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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
            "crt-fpu-format-wave627",
            "retail-binary-evidence",
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
        }
        else {
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
        if (spec.updateSignature && !fn.getSignature().toString().equals(expectedSignature(spec))) {
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
        if (spec.updateSignature) {
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature);
            }
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
                String targetSignature = spec.updateSignature ? expectedSignature(spec) : fn.getSignature().toString();
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + targetSignature);
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            }
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

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00561618",
                "CRT__ExtractFiniteExponentMaskOrPassThrough",
                new String[] {"CRT__ExtractFiniteExponentMaskOrPassThrough_00561618"},
                true,
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("unusedLowDword", uintType), param("highDword", uintType)},
                "Wave627 CRT/FPU/format hardening: finite-exponent mask helper used by adjacent acos classification wrappers. It reads the high dword of a floating-point value, returns highDword & 0x7ff00000 for finite inputs, and passes through the high dword for Inf/NaN exponent patterns. Static FPU-classification evidence only; exact CRT version, floating-point ABI details, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-classification", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x0056162e",
                "CRT__MathErrorHook_NoOp",
                new String[] {},
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave627 CRT/FPU/format hardening: compact math-error hook/return shim reached from acos/pow guard paths. Instruction read-back compares a stack FPU control word against 0x27f, conditionally restores it with FLDCW, pops EDX, and returns. Static math-error shim evidence only; the nonstandard stack cleanup, exact CRT helper identity, runtime FPU side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-control", "custom-stack")
            ),
            new Spec(
                "0x0056163b",
                "__math_exit",
                new String[] {},
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave627 CRT/FPU/format hardening: Visual Studio __math_exit library-match helper. Instruction read-back checks the saved FPU control word and status word, reports a one-argument math error when the invalid-operation bit is unmasked and set, otherwise restores the control word and returns through the same compact stack shim pattern. Static library-helper evidence only; exact CRT version, nonstandard stack cleanup, runtime FPU side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-control", "library-match", "custom-stack")
            ),
            new Spec(
                "0x00561679",
                "CRT__HandleFpuExceptionForMathOp",
                new String[] {},
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("unusedEcx", intType), param("mathOpId", intType)},
                "Wave627 CRT/FPU/format hardening: FPU exception handler reached from pow guard paths. It classifies ST0 as denormal/Inf/NaN/finite through exponent-mask checks, rescales through FSCALE constants, tests the saved FPU control/status words, and dispatches either the one-argument error handler or the math-error restore path when mathOpId is 0x1d. Static FPU-exception evidence only; exact CRT helper identity, control-word semantics, runtime math behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-control", "math-error", "signature-hardened")
            ),
            new Spec(
                "0x0056171c",
                "CRT__FlsBuf",
                new String[] {},
                true,
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("character", uintType), param("stream", voidPtr)},
                "Wave627 CRT/FPU/format hardening: flush-buffer helper for byte-oriented CRT output. It validates stream flags, initializes a file buffer when needed, writes through CRT__WriteFdTextMode_Locking_00567505, handles stdout/stderr commit-mode checks, updates stream cursor/count fields, and returns the written byte or 0xffffffff on failure. Static stream-buffer evidence only; exact FILE layout, text-mode semantics, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "file-buffer", "signature-hardened")
            ),
            new Spec(
                "0x00561834",
                "CRT__FormatOutputToStream",
                new String[] {},
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outputTarget", voidPtr), param("format", charPtr), param("argList", voidPtr)},
                "Wave627 CRT/FPU/format hardening: printf-family core formatter used by sprintf, vsprintf, fprintf, printf, and local snprintf-style wrappers. It walks the format string state machine, consumes width/precision/value arguments through the adjacent arg-list readers, routes integer/float/string/char cases, applies padding/sign/prefix flags, and writes through the adjacent output helpers. Static printf-core evidence only; exact CRT format semantics, locale behavior, FILE/buffer layout, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "format-output", "printf-core", "signature-hardened")
            ),
            new Spec(
                "0x00561f75",
                "CRT__PutCharToStreamAndCount",
                new String[] {},
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("character", uintType), param("stream", voidPtr), param("count", intPtr)},
                "Wave627 CRT/FPU/format hardening: single-byte output/count helper used by the printf-family formatter and repeated/string output helpers. It decrements the stream byte count, flushes through CRT__FlsBuf when needed, writes the byte to the stream buffer otherwise, sets count to -1 on write failure, and increments count on success. Static stream-output evidence only; exact FILE layout, text-mode behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x00561faa",
                "CRT__PutCharRepeatedToStream",
                new String[] {},
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("character", uintType), param("repeatCount", intType), param("stream", voidPtr), param("count", intPtr)},
                "Wave627 CRT/FPU/format hardening: repeated-byte output helper used by the printf-family formatter for padding. It emits character through CRT__PutCharToStreamAndCount until repeatCount is exhausted or count becomes -1. Static padding/output evidence only; exact FILE layout, text-mode behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x00561fdb",
                "CRT__PutStringToStream",
                new String[] {},
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("text", charPtr), param("length", intType), param("stream", voidPtr), param("count", intPtr)},
                "Wave627 CRT/FPU/format hardening: bounded string output helper used by the printf-family formatter. It walks length bytes from text, emits each byte through CRT__PutCharToStreamAndCount, and stops early if count becomes -1. Static string-output evidence only; exact encoding/locale behavior, FILE layout, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x00562013",
                "CRT__ReadIntAndAdvanceArgList",
                new String[] {"ControlsUI__ReadIntAndAdvance"},
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {param("argListPtr", voidPtr)},
                "Wave627 CRT/FPU/format hardening: printf-style arg-list reader for 32-bit values. It advances the caller-owned argument cursor by four bytes and returns the previous 32-bit slot; xrefs show use from both CRT__FormatOutputToStream and ControlsUI__FormatWideStringCore. Static vararg-reader evidence only; exact va_list representation, caller conventions, and rebuild parity remain unproven.",
                tags("crt-runtime", "format-output", "vararg-reader", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x00562020",
                "CRT__ReadFormatWordAndAdvance",
                new String[] {},
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {param("argListPtr", voidPtr)},
                "Wave627 CRT/FPU/format hardening: printf-style arg-list reader for the low word of the next 32-bit argument slot. It advances the caller-owned argument cursor by four bytes and loads AX from the previous slot; the current decompile preserves stale upper EAX bits. Static vararg-reader evidence only; exact wchar/short promotion semantics, caller conventions, and rebuild parity remain unproven.",
                tags("crt-runtime", "format-output", "vararg-reader", "signature-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated
                + " skipped=" + stats.skipped
                + " renamed=" + stats.renamed
                + " would_rename=" + stats.wouldRename
                + " signature_updated=" + stats.signatureUpdated
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
