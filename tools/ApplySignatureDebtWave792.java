//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.LongLongDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedLongLongDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySignatureDebtWave792 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "signature-debt-wave792",
            "wave792-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "param-name-hardened",
            "crt-runtime"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        } else {
            for (int i = 0; i < spec.params.length; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.params[i].getDataType().getDisplayName())
                    .append(" ")
                    .append(spec.params[i].getName());
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!signature.equals(expectedSignature(spec))) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + signature);
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }

            String signature = fn.getSignature().toString();
            boolean signatureNeedsUpdate = !signature.equals(expectedSignature(spec));
            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            Set<String> actualTags = tagNames(fn);
            boolean tagsNeedUpdate = false;
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    tagsNeedUpdate = true;
                    break;
                }
            }

            if (!signatureNeedsUpdate && !commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " signature=" + signature + " -> " + expectedSignature(spec));
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                stats.skipped++;
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " signature=" + expectedSignature(spec));
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.updated++;
            Thread.sleep(50L);
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplySignatureDebtWave792 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType longLongType = LongLongDataType.dataType;
        DataType ulongLongType = UnsignedLongLongDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055e0c0",
                "__aulldiv",
                "__stdcall",
                ulongLongType,
                new ParameterImpl[] {
                    param("dividend_low", uintType),
                    param("dividend_high", uintType),
                    param("divisor_low", uintType),
                    param("divisor_high", uintType)
                },
                "Wave792 signature-debt hardening: Visual C++ library-matched unsigned 64-bit division helper. Pre-Wave792 decompile renders a four-dword stack prototype and returns the quotient in EDX:EAX; instruction evidence reads dividend_low/dividend_high/divisor_low/divisor_high from the stack and returns with ret 0x10. Static retail CRT helper evidence only; exact compiler CRT source version, divide-by-zero behavior, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "u64-division", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0055e128",
                "__ftol",
                "__cdecl",
                longLongType,
                new ParameterImpl[] {},
                "Wave792 signature-debt hardening: Visual C++ library-matched FPU float-to-longlong conversion helper. Pre-Wave792 decompile renders longlong __ftol(void) using ST0 as an implicit x87 input, and instruction evidence changes the FPU control word before storing the rounded integer result. Static retail CRT helper evidence only; exact compiler CRT source version, x87 exception/rounding behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0055e4d4",
                "__fclose_lk",
                "__cdecl",
                intType,
                new ParameterImpl[] { param("stream", voidPtr) },
                "Wave792 signature-debt hardening: Visual C++ 2003 library-matched locked fclose helper. Pre-Wave792 decompile renders int __fclose_lk(FILE *), tests stream flag bits, flushes and frees the stream buffer, closes the file descriptor, frees tmpname when present, clears the stream flags, and returns status. Static retail CRT helper evidence only; exact FILE structure layout, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "stdio", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0055fcc0",
                "__alldiv",
                "__stdcall",
                longLongType,
                new ParameterImpl[] {
                    param("dividend_low", uintType),
                    param("dividend_high", intType),
                    param("divisor_low", uintType),
                    param("divisor_high", intType)
                },
                "Wave792 signature-debt hardening: Visual C++ library-matched signed 64-bit division helper. Pre-Wave792 decompile renders a four-dword stack prototype, normalizes operand signs, performs unsigned division, reapplies the sign, and returns the quotient in EDX:EAX with ret 0x10. Static retail CRT helper evidence only; exact compiler CRT source version, divide-by-zero behavior, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "s64-division", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00560289",
                "__amsg_exit",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("runtime_error_code", intType) },
                "Wave792 signature-debt hardening: Visual C++ 2003 library-matched abnormal-message exit helper. Pre-Wave792 decompile shows __amsg_exit reporting runtime_error_code and then calling exit(0xff); this pass only replaces the stale param_1 name. Static retail CRT helper evidence only; exact CRT source version, runtime report formatting, process-exit behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "runtime-error", "param-name-cleared")
            ),
            new Spec(
                "0x005639d0",
                "__allmul",
                "__stdcall",
                longLongType,
                new ParameterImpl[] {
                    param("left_low", uintType),
                    param("left_high", intType),
                    param("right_low", uintType),
                    param("right_high", intType)
                },
                "Wave792 signature-debt hardening: Visual C++ library-matched 64-bit multiplication helper. Pre-Wave792 decompile renders a four-dword stack prototype, computes the product into EDX:EAX, and instruction evidence returns with ret 0x10. Static retail CRT helper evidence only; exact signed/unsigned caller intent, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "i64-multiply", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00569ec0",
                "__aullrem",
                "__stdcall",
                ulongLongType,
                new ParameterImpl[] {
                    param("dividend_low", uintType),
                    param("dividend_high", uintType),
                    param("divisor_low", uintType),
                    param("divisor_high", uintType)
                },
                "Wave792 signature-debt hardening: Visual C++ library-matched unsigned 64-bit remainder helper. Pre-Wave792 decompile renders a four-dword stack prototype and returns the remainder in EDX:EAX; instruction evidence follows the same high-divisor normalization shape as __aulldiv and returns with ret 0x10. Static retail CRT helper evidence only; exact compiler CRT source version, divide-by-zero behavior, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "u64-remainder", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0056b840",
                "___free_lc_time",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("locale_time_block", voidPtr) },
                "Wave792 signature-debt hardening: Visual C++ library-matched locale-time cleanup helper. Pre-Wave792 decompile renders void ___free_lc_time(undefined4 *), null-checks the locale-time block, and frees many pointer fields through CRT__FreeBase. Static retail CRT helper evidence only; exact locale structure layout, ownership contract, runtime cleanup behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "locale-cleanup", "undefined-signature-cleared")
            ),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave792 apply encountered missing/bad rows");
        }
    }
}
