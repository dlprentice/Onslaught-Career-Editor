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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySignatureDebtWave791 extends GhidraScript {
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
            "signature-debt-wave791",
            "wave791-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "param-name-hardened",
            "crt-seh"
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
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
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
        println("ApplySignatureDebtWave791 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intPtr = new PointerDataType(intType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055d6a0",
                "CRT__SehPopExceptionFrameAndJump",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("continuation_target", voidPtr) },
                "Wave791 signature-debt hardening: CRT/SEH helper pops the FS:[0] exception-list frame, restores ESP/EBP from the current frame, and transfers control through continuation_target. Evidence: Wave620 comment/xrefs plus pre-Wave791 decompile/instruction read-back for 0x0055d6a0; caller CRT__SehUnwindAndResumeSearch reaches this indirect-jump helper. Static retail CRT helper evidence only; exact MSVC CRT version, exception-record/frame layout identity, runtime exception behavior, and rebuild parity remain unproven.",
                tags("wave620-followup", "fs-exception-list", "indirect-jump", "seh-frame")
            ),
            new Spec(
                "0x0055d6d4",
                "CRT__InvokeCallbackWithLockGuards",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("transfer_cookie", intType),
                    param("callback_target", voidPtr)
                },
                "Wave791 signature-debt hardening: compact CRT callback-transfer helper that Ghidra renders as LOCK/UNLOCK pseudo-operations before an indirect transfer through callback_target. Evidence: Wave620 comment/xrefs plus pre-Wave791 decompile/instruction read-back; callers include CRT__BuildCatchObject and CRT__DestroyCatchObject. Static retail CRT helper evidence only; exact helper identity, callback contract, runtime exception behavior, and rebuild parity remain unproven.",
                tags("wave620-followup", "callback-wrapper", "indirect-jump", "lock-unlock-pseudo")
            ),
            new Spec(
                "0x0055d6db",
                "CRT__SehLockUnlockAndJump",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("transfer_cookie", intType),
                    param("callback_target", voidPtr)
                },
                "Wave791 signature-debt hardening: sibling compact CRT callback-transfer helper that Ghidra renders as LOCK/UNLOCK pseudo-operations before an indirect transfer through callback_target. Evidence: Wave620 comment/xrefs plus pre-Wave791 decompile/instruction read-back; xref evidence reaches it from CRT__BuildCatchObject. Static retail CRT helper evidence only; exact helper identity, callback contract, runtime exception behavior, and rebuild parity remain unproven.",
                tags("wave620-followup", "callback-wrapper", "indirect-jump", "lock-unlock-pseudo")
            ),
            new Spec(
                "0x0055d6e2",
                "CRT__SehRtlUnwindAndRestoreFrame",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("target_frame", voidPtr),
                    param("exception_record", voidPtr)
                },
                "Wave791 signature-debt hardening: CRT/SEH helper builds temporary SEH state, calls RtlUnwind(target_frame, 0x0055d70a, exception_record, 0), clears exception_record flag bit 0x2, and restores the FS exception-list state. Evidence: Wave620 comment/xrefs plus pre-Wave791 decompile/instruction read-back; callers include CRT__SehUnwindAndResumeSearch and CRT__SehFilterCppException. Static retail SEH helper evidence only; exact exception-record layout identity, runtime unwind behavior, and rebuild parity remain unproven.",
                tags("wave620-followup", "fs-exception-list", "rtlunwind", "seh-frame")
            ),
            new Spec(
                "0x0055d7bb",
                "CRT__SehCallback_Call_005602d2",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("callback_arg0", intType),
                    param("callback_arg1", intType),
                    param("callback_arg2", intType)
                },
                "Wave791 signature-debt hardening: CRT/SEH callback wrapper reached by DATA xref from CRT__SehInvokeCallSettingFrame12; instruction evidence clears direction flag, marshals frame/caller arguments, and calls CRT__SehDispatchWithScopeTable/0x005602d2 before returning. Parameter names stay conservative because the exact handler prototype is still unproven. Static retail CRT/SEH callback evidence only; runtime exception behavior and rebuild parity remain unproven.",
                tags("wave620-followup", "callback-wrapper", "data-xref", "conservative-param-names")
            ),
            new Spec(
                "0x0055d896",
                "CRT__SehFilterCppException",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("exception_record", voidPtr),
                    param("seh_frame", voidPtr),
                    param("dispatcher_context", voidPtr)
                },
                "Wave791 signature-debt hardening: CRT C++ exception filter reads exception_record flags at +0x4, marks seh_frame+0x24 on the early path, otherwise dispatches through CRT__SehDispatchWithScopeTable, may call CRT__SehRtlUnwindAndRestoreFrame(seh_frame, exception_record), then transfers through the frame callback at +0x18. Evidence: Wave620 comment/xrefs plus pre-Wave791 decompile/instruction read-back. Static retail C++ exception-filter evidence only; exact CRT version, frame layout identity, runtime translator behavior, and rebuild parity remain unproven.",
                tags("wave620-followup", "exception-filter", "indirect-jump", "data-xref")
            ),
            new Spec(
                "0x0055d90b",
                "CRT__GetRangeOfTryBlocksForState",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("eh_func_info", voidPtr),
                    param("try_nesting_index", intType),
                    param("current_state", intType),
                    param("out_low_try", intPtr),
                    param("out_high_try", intPtr)
                },
                "Wave791 signature-debt hardening: CRT C++ EH metadata helper walks 0x14-byte try-block records from eh_func_info+0x10 using the count at +0x0c, compares current_state against record bounds, writes out_low_try/out_high_try, and returns the selected try-block record pointer as an int. Evidence: Wave620 comment/xrefs plus pre-Wave791 decompile/instruction read-back; callers include CRT__SehLookupAndInvokeScopeHandler and CRT__ValidateCatchHandlersForThrow. Static retail EH-table evidence only; exact metadata layout identity, runtime catch selection behavior, and rebuild parity remain unproven.",
                tags("wave620-followup", "eh-metadata", "try-block-range", "out-params")
            ),
            new Spec(
                "0x0055d988",
                "__global_unwind2",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("target_frame", voidPtr) },
                "Wave791 signature-debt hardening: Visual C++ library-matched __global_unwind2 row. Pre-Wave791 decompile shows a direct RtlUnwind(target_frame, 0x0055d9a0, NULL, NULL) call; xrefs include _longjmp and a CRT unwind callsite at 0x005612d6. This removes exact-undefined return debt only; exact CRT version, runtime unwind behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "rtlunwind", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0055d9ca",
                "__local_unwind2",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("registration_frame", voidPtr),
                    param("stop_state", intType)
                },
                "Wave791 signature-debt hardening: Visual C++ library-matched __local_unwind2 row. Pre-Wave791 decompile shows registration_frame-driven local unwind over scope records until state -1 or stop_state, updating frame state and invoking cleanup callbacks through CRT__SehStoreFrameGlobals. Xrefs include _longjmp, __seh_longjmp_unwind@4, and CRT callsites around 0x005612e3/0x00561323. This removes exact-undefined return debt only; exact scope-record layout, runtime unwind behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "local-unwind", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0055da55",
                "__NLG_Notify1",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("nlg_destination", intType) },
                "Wave791 signature-debt hardening: Visual C++ library-matched __NLG_Notify1 row. Pre-Wave791 decompile shows a fastcall-style notification helper storing nlg_destination plus implicit EAX and EBP values into DAT_006532d8/DAT_006532d4/DAT_006532dc; xrefs come from __CallSettingFrame@12. This removes exact-undefined return debt only; exact non-local-goto diagnostic semantics, runtime exception behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-cpp", "nlg-notify", "undefined-signature-cleared")
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
            throw new IllegalStateException("Wave791 apply encountered missing/bad rows");
        }
    }
}
