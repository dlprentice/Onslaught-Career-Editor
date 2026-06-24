//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.Float10DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySignatureDebtWave794 extends GhidraScript {
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
            "signature-debt-wave794",
            "wave794-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "param-name-hardened",
            "crt-runtime",
            "fpu"
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
        boolean renderedAnyParam = false;
        if (spec.returnType == Float10DataType.dataType) {
            sb.append("float10 * __return_storage_ptr__");
            renderedAnyParam = true;
        }
        if (spec.params.length == 0 && !renderedAnyParam) {
            sb.append("void");
        } else {
            for (int i = 0; i < spec.params.length; i++) {
                if (renderedAnyParam || i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.params[i].getDataType().getDisplayName())
                    .append(" ")
                    .append(spec.params[i].getName());
                renderedAnyParam = true;
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
        println("ApplySignatureDebtWave794 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType ushortType = UnsignedShortDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType float10Type = Float10DataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00561360",
                "__trandisp1",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("dispatch_cookie", intType),
                    param("transition_table", voidPtr)
                },
                "Wave794 signature-debt hardening: Visual C++ library-matched one-operand transcendental dispatch helper. Pre-Wave794 decompile renders void __fastcall __trandisp1(undefined4, int), uses hidden ST0/EBP FPU state, stores transition_table into the caller scratch frame, derives an FPU condition index, and dispatches through transition_table plus DAT_0065374c. Static retail CRT/FPU helper evidence only; exact transition-table layout, x87 stack contract, runtime transcendental behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "transcendental-dispatch", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x005613c7",
                "__trandisp2",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("dispatch_cookie", intType),
                    param("transition_table", voidPtr)
                },
                "Wave794 signature-debt hardening: Visual C++ 1998/2003/2005/2008 library-matched two-operand transcendental dispatch helper. Pre-Wave794 decompile renders void __fastcall __trandisp2(undefined4, int), uses hidden ST0/ST1/EBP FPU state, stores transition_table into the caller scratch frame, combines two FPU condition indexes through DAT_0065374c, and dispatches through the selected table slot. Static retail CRT/FPU helper evidence only; exact transition-table layout, x87 stack contract, runtime transcendental behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "transcendental-dispatch", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00561547",
                "__startOneArgErrorHandling",
                "__fastcall",
                float10Type,
                new ParameterImpl[] {
                    param("dispatch_cookie", intType),
                    param("error_context", intType),
                    param("fpu_control_word", ushortType),
                    param("error_slot0", intType),
                    param("error_slot1", intType),
                    param("error_slot2", intType)
                },
                "Wave794 signature-debt hardening: Visual C++ library-matched one-argument floating-point error handler. Pre-Wave794 decompile renders a fastcall helper returning float10, spills hidden ST0 to a local double, forwards error_context and the observed control-word/error slots into CRT__HandleFloatingPointException, and restores the original floating result. Static retail CRT/FPU helper evidence only; exact error-record layout, x87 exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "fpu-error", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00562b03",
                "__frnd",
                "__cdecl",
                float10Type,
                new ParameterImpl[] {
                    param("input_value", doubleType)
                },
                "Wave794 signature-debt hardening: Visual C++ library-matched floating round helper. Pre-Wave794 decompile renders float10 __frnd(double) and returns ROUND(input_value) through the x87-style float10 return path. Static retail CRT/FPU helper evidence only; exact compiler CRT source version, rounding mode behavior, x87 exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "rounding", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00563a10",
                "__cintrindisp2",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave794 signature-debt hardening: Visual C++ library-matched two-operand intrinsic dispatch wrapper. Pre-Wave794 decompile renders void __cintrindisp2(void), calls __trandisp2, then calls CRT__FpuIntDispatch2_Handle. Static retail CRT/FPU helper evidence only; exact hidden x87 operand contract, runtime intrinsic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "intrinsic-dispatch", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00563a4e",
                "__cintrindisp1",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave794 signature-debt hardening: Visual C++ library-matched one-operand intrinsic dispatch wrapper. Pre-Wave794 decompile renders void __cintrindisp1(void), calls __trandisp1, then calls CRT__FpuIntDispatch2_Handle. Static retail CRT/FPU helper evidence only; exact hidden x87 operand contract, runtime intrinsic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "intrinsic-dispatch", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00563a8b",
                "__ctrandisp2",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("left_mantissa_low", uintType),
                    param("left_packed_high", intType),
                    param("right_mantissa_low", uintType),
                    param("right_packed_high", intType)
                },
                "Wave794 signature-debt hardening: Visual C++ 1998/2003/2005/2008 library-matched two-operand transcendental dispatch wrapper. Pre-Wave794 decompile renders void __ctrandisp2(undefined4, undefined4, undefined4, undefined4), loads two packed floating operands through __fload, calls __trandisp2, and clears/handles FPU status through CRT__FpuTransDispatch2_ClearStatusAndHandle. Static retail CRT/FPU helper evidence only; exact packed operand format, hidden x87 stack contract, runtime transcendental behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "transcendental-dispatch", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00563c0b",
                "__ctrandisp1",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("mantissa_low", uintType),
                    param("packed_high", intType)
                },
                "Wave794 signature-debt hardening: Visual C++ library-matched one-operand transcendental dispatch wrapper. Pre-Wave794 decompile renders void __ctrandisp1(undefined4, undefined4), loads one packed floating operand through __fload, calls __trandisp1, and clears/handles FPU status through CRT__FpuTransDispatch2_ClearStatusAndHandle. Static retail CRT/FPU helper evidence only; exact packed operand format, hidden x87 stack contract, runtime transcendental behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "transcendental-dispatch", "x87", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00563c3e",
                "__fload",
                "__cdecl",
                float10Type,
                new ParameterImpl[] {
                    param("mantissa_low", uintType),
                    param("packed_high", intType)
                },
                "Wave794 signature-debt hardening: Visual C++ 1998/2003/2005/2008 library-matched packed floating-load helper. Pre-Wave794 decompile renders float10 __fload(uint, int), checks the 0x7ff0 exponent field in packed_high, builds a float10 NaN/Inf-style payload for the all-ones exponent case, or converts the packed high/low dwords through the double-to-float10 path otherwise. Static retail CRT/FPU helper evidence only; exact packed operand format, NaN/Inf policy, x87 exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "fload", "x87", "undefined-signature-cleared")
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
            throw new IllegalStateException("Wave794 apply encountered missing/bad rows");
        }
    }
}
