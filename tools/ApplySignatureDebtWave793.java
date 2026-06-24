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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySignatureDebtWave793 extends GhidraScript {
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
            "signature-debt-wave793",
            "wave793-readback-verified",
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
        boolean renderedAnyParam = false;
        if (spec.callingConvention.equals("__thiscall")) {
            sb.append("void * this");
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
        println("ApplySignatureDebtWave793 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType uintPtr = new PointerDataType(uintType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055f7a3",
                "___timet_from_ft",
                "__cdecl",
                intType,
                new ParameterImpl[] { param("file_time", voidPtr) },
                "Wave793 signature-debt hardening: Visual C++ 2003 library-matched FILETIME-to-time_t conversion helper. Pre-Wave793 decompile renders int ___timet_from_ft(FILETIME *), rejects a zero FILETIME, converts through FileTimeToLocalFileTime and FileTimeToSystemTime, then calls CRT__SystemTimeToUnixTimestampLocal or returns -1. Static retail CRT helper evidence only; exact FILETIME structure typing, local-time conversion edge cases, runtime clock behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "time-conversion", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00560ae0",
                "__CallSettingFrame@12",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("frame_arg0", intType),
                    param("frame_arg1", intType),
                    param("nlg_destination", intType)
                },
                "Wave793 signature-debt hardening: Visual C++ library-matched non-local-goto setting-frame helper. Pre-Wave793 decompile renders three stack arguments, notifies __NLG_Notify1 with nlg_destination, performs an indirect frame call, maps destination 0x100 to 2, and notifies again. Static retail CRT/SEH helper evidence only; exact compiler CRT source version, hidden frame-call contract, runtime exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "seh", "non-local-goto", "undefined-signature-cleared")
            ),
            new Spec(
                "0x00561339",
                "__seh_longjmp_unwind@4",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("longjmp_registration", voidPtr) },
                "Wave793 signature-debt hardening: Visual C++ 1998/2003 library-matched SEH longjmp unwind helper. Pre-Wave793 decompile renders void __seh_longjmp_unwind_4(int) and calls __local_unwind2 using fields at longjmp_registration+0x18 and +0x1c. Static retail CRT/SEH helper evidence only; exact registration-record layout, runtime exception unwinding behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "seh", "longjmp", "undefined-signature-cleared")
            ),
            new Spec(
                "0x005615d5",
                "__fload_withFB",
                "__fastcall",
                uintType,
                new ParameterImpl[] {
                    param("dispatch_cookie", intType),
                    param("floating_record", voidPtr)
                },
                "Wave793 signature-debt hardening: Visual C++ library-matched fastcall floating-load helper. Pre-Wave793 decompile renders uint __fastcall __fload_withFB(undefined4, int), reads the high dword of floating_record at +4, masks the exponent bits, and returns either the masked exponent or the original high dword for the 0x7ff exponent case. Static retail CRT/FPU helper evidence only; exact floating-record layout, x87/SSE exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "fpu", "fastcall", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0056163b",
                "__math_exit",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave793 signature-debt hardening: Visual C++ library-matched math-exit helper. Pre-Wave793 decompile renders void __math_exit(void), checks FPU status/control-word state, and calls __startOneArgErrorHandling only when the masked status and return-control bits indicate the error path. Static retail CRT/FPU helper evidence only; exact math-runtime source version, x87 exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "fpu", "math-runtime", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0056d4c7",
                "___add_12",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("accumulator", uintPtr),
                    param("addend", uintPtr)
                },
                "Wave793 signature-debt hardening: Visual C++ 2003 library-matched 12-byte addition helper. Pre-Wave793 decompile renders void ___add_12(uint *, uint *), adds three dwords from addend into accumulator, and propagates carries through CRT__UIntAddWithOverflowCheck. Static retail CRT arithmetic helper evidence only; exact signedness intent, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "multiword-arithmetic", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0059ccce",
                "Memcpy",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("destination", voidPtr),
                    param("source", voidPtr),
                    param("byte_count", uintType)
                },
                "Wave793 signature-debt hardening: Visual C++ 2003 library-matched C++ stream/memory-file Memcpy virtual helper. Pre-Wave793 decompile shows an owner-ambiguous __thiscall shape matching CHtmlStream::Memcpy or CMemFile::Memcpy, with Ghidra rendering the implicit this pointer plus destination/source/byte_count parameters; the body copies byte_count bytes from source to destination in dword and tail-byte loops, and returns destination. Static retail library helper evidence only; exact C++ owner class, vtable slot identity, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "cpp-stream", "memcpy", "undefined-signature-cleared")
            ),
            new Spec(
                "0x005d0983",
                "init_namebuf",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("temp_name_selector", intType) },
                "Wave793 signature-debt hardening: Visual C++ 2003 library-matched temporary-name buffer initializer. Pre-Wave793 decompile renders void __cdecl init_namebuf(int), selects one of two global name buffers, normalizes a path separator, writes s/t selector text, appends the current process id in base 0x20, and appends the extension suffix. Static retail CRT temporary-file helper evidence only; exact global buffer ownership, runtime temp-path behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp-2003", "temp-name-buffer", "undefined-signature-cleared")
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
            throw new IllegalStateException("Wave793 apply encountered missing/bad rows");
        }
    }
}
