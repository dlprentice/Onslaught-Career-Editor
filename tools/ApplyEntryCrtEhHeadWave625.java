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

public class ApplyEntryCrtEhHeadWave625 extends GhidraScript {
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
            "entry-crt-eh-wave625",
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00560181",
                "entry",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave625 entry/CRT EH hardening: process entry routine. It installs an SEH frame, records Win32 version fields, initializes heap/TLS/file descriptor/argv/environment/static initializer state, selects startup show-command state, calls CLTShell__WinMain, then exits through CRT__CExit; initialization failures route to CDXTexture__ReportFatalAndExitProcess. Static startup evidence only; exact CRT startup identity/version, full process lifetime behavior, and rebuild parity remain unproven.",
                tags("process-entry", "crt-startup", "winmain")
            ),
            new Spec(
                "0x005602ae",
                "CDXTexture__ReportFatalAndExitProcess",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("runtimeErrorId", intType)},
                "Wave625 entry/CRT EH hardening: fatal runtime-report wrapper. If the runtime critical-mode flag is set it emits the critical-mode report first, then reports runtimeErrorId and terminates with ExitProcess(0xff). Xrefs are process-entry initialization failures. Static fatal-exit evidence only; exact CRT runtime-error message table, user-visible error behavior, and rebuild parity remain unproven.",
                tags("fatal-exit", "runtime-error", "cdxtexture")
            ),
            new Spec(
                "0x005605ca",
                "CRT__TypeMatchForCatch",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("handlerType", voidPtr), param("catchableType", voidPtr), param("throwInfo", voidPtr)},
                "Wave625 entry/CRT EH hardening: C++ exception catch-type matcher. It treats empty handler type descriptors as a catch-all, compares handler and catchable type descriptor names, then checks const/volatile/reference-style flag compatibility against handlerType, catchableType, and throwInfo bits before returning match/non-match. Static CRT EH metadata evidence only; exact MSVC structure names/layouts, language edge cases, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "cxx-exception", "type-match")
            ),
            new Spec(
                "0x00560627",
                "CRT__SehUnwindToTargetState",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("frameInfo", voidPtr), param("registrationFrame", intType), param("functionInfo", voidPtr), param("targetState", intType)},
                "Wave625 entry/CRT EH hardening: C++ exception unwind-map walker. It reads the current state from frameInfo+0x08, validates state indexes against functionInfo metadata, invokes unwind cleanup callbacks through __CallSettingFrame_12, follows previous-state links until targetState, and stores the final state back to frameInfo+0x08. Static CRT EH evidence only; exact MSVC structure names/layouts, callback side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "cxx-exception", "unwind-map")
            ),
            new Spec(
                "0x00560740",
                "CRT__CallCatchBlock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("exceptionRecord", voidPtr), param("frameInfo", voidPtr), param("contextRecord", voidPtr)},
                "Wave625 entry/CRT EH hardening: catch-block invocation wrapper. It installs an SEH frame, stashes exceptionRecord and contextRecord into the per-thread CRT record, calls CRT__SehInvokeCallSettingFrame12, then restores the catch context through CRT__CleanupCatchContext before returning the catch result. Static CRT EH evidence only; exact thread-local record layout, catch transfer semantics, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "cxx-exception", "catch-invoke")
            ),
            new Spec(
                "0x00560885",
                "CRT__BuildCatchObject",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("exceptionRecord", voidPtr), param("frameObjectBase", intType), param("handlerType", voidPtr), param("catchableType", voidPtr)},
                "Wave625 entry/CRT EH hardening: catch-object materialization helper. It validates handler/catchable metadata, computes the destination catch-object slot from catchable metadata plus frameObjectBase, validates readable/writable/executable pointers, adjusts source pointers through CRT__AdjustPointerByPMD, copies thrown data through CRT__MemMoveOverlapSafe, or invokes copy-constructor callbacks through the compact SEH lock/unlock helpers. Static CRT EH evidence only; exact MSVC structure names/layouts, object lifetime side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "cxx-exception", "catch-object")
            ),
            new Spec(
                "0x00560a49",
                "CRT__DestroyCatchObject",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("exceptionRecord", voidPtr)},
                "Wave625 entry/CRT EH hardening: catch-object cleanup helper. When exceptionRecord is non-null and the destructor callback slot referenced from exceptionRecord+0x1c is present, it invokes the destructor for exceptionRecord+0x18 through CRT__InvokeCallbackWithLockGuards under the temporary SEH frame. Static CRT EH evidence only; exact metadata layout, destructor side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "cxx-exception", "catch-object")
            ),
            new Spec(
                "0x00560ab0",
                "CRT__AdjustPointerByPMD",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("basePtr", intType), param("pmd", voidPtr)},
                "Wave625 entry/CRT EH hardening: pointer-to-member-displacement adjuster used while building catch objects. It adds the primary displacement to basePtr, then when the vbtable offset field is non-negative it reads the vbtable displacement slot and adds that value plus the vbtable offset. Static CRT EH PMD evidence only; exact MSVC PMD structure naming, object layout identity, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "cxx-exception", "pmd-adjust")
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
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
