//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
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

public class ApplyInputCursorWave567 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.name + " " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }

            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + spec.name + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005234d0",
                "PlatformInput__SetGlobalInputState",
                "PlatformInput__SetGlobalInputState",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("global_input_state", intType) },
                "Wave567 comment/tag hardening: PlatformInput__InitMouse pushes 1 and PlatformInput__ShutdownMouse pushes 0 before calling this setter, which writes DAT_0089bdf0. Input__HandleMouseWindowMessage checks that global before refreshing stored mouse x/y and normalized window coordinates. Static retail evidence only; exact variable name, runtime mouse-capture semantics, BEA patching, and rebuild parity remain unproven.",
                tags("platform-input", "mouse-state", "signature-confirmed")
            ),
            new Spec(
                "0x005234e0",
                "Input__HandleMouseWindowMessage",
                "Input__HandleMouseWindowMessage",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("message", uintType),
                    param("wparam", uintType),
                    param("lparam", uintType)
                },
                "Wave567 signature/comment hardening: caller 0x00512f83 reaches this only for Windows mouse messages 0x200..0x20a and pushes message, wparam, and lparam; RET 0x0c confirms three stdcall arguments. The body updates cursor x/y from LOWORD/HIWORD(lparam), normalizes by PLATFORM window dimensions, scales to 640x480 when CVBufTexture global mode is active, tracks left/middle/right button down/up latches, and accumulates wheel delta from HIWORD(wparam). Static retail evidence only; exact Windows-proc boundary, runtime mouse behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mouse-message", "windows-message", "signature-corrected")
            ),
            new Spec(
                "0x00523b50",
                "CDXEngine__GetCursorStateInRect",
                "CDXEngine__GetCursorStateInRect",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("left", floatType),
                    param("top", floatType),
                    param("right", floatType),
                    param("bottom", floatType)
                },
                "Wave567 signature/comment hardening: CGameInterface__Render, CFrontEnd__GetCursorStateInRect, and ControlsUI__RenderBindingsList call this four-float rectangle predicate. The body returns nonzero only when cursor-ready DAT_0089bdf4 is set, dev mode is clear, no key-trap callback is installed, and stored cursor x/y lies in [left,right) and [top,bottom). Static retail evidence only; exact cursor globals, runtime UI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cursor-rect", "frontend-input", "signature-corrected")
            ),
            new Spec(
                "0x00523bc0",
                "Input__DispatchClickInRect",
                "Input__DispatchClickInRect",
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("left", floatType),
                    param("top", floatType),
                    param("right", floatType),
                    param("bottom", floatType),
                    param("button_action", intType)
                },
                "Wave567 signature/comment hardening: CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture passes four rectangle bounds plus a button-action value. The body gates through the key-trap callback and dev-mode state, consumes the click-ready latch DAT_0089bdfc when stored cursor x/y lies inside [left,right) and [top,bottom), and dispatches CFrontEnd__ReceiveButtonAction(&DAT_0089d758,DAT_008a9564,button_action,1.0). Static retail evidence only; exact action enum, runtime frontend behavior, BEA patching, and rebuild parity remain unproven.",
                tags("click-rect", "frontend-input", "button-dispatch", "signature-corrected")
            ),
            new Spec(
                "0x00523cc0",
                "Input__GetClickStateInRect",
                "Input__GetClickStateInRect",
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("left", floatType),
                    param("top", floatType),
                    param("right", floatType),
                    param("bottom", floatType)
                },
                "Wave567 signature/comment hardening: modal panel, GameInterface, MessageLog, FrontEnd, controller-definition, controls-list, and multiplayer-start callers use this four-float click rectangle predicate. The body rejects key-trap/dev-mode paths, checks click-ready DAT_0089bdfc, tests stored cursor x/y against [left,right) and [top,bottom), consumes DAT_0089bdfc on a hit, and returns the result in AL. Static retail evidence only; exact click-state type, runtime UI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("click-rect", "frontend-input", "consume-click", "signature-corrected")
            ),
            new Spec(
                "0x00523d40",
                "Input__GetCursorStateInRectAndConsume",
                "Input__GetCursorStateInRectAndConsume",
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("left", floatType),
                    param("top", floatType),
                    param("right", floatType),
                    param("bottom", floatType)
                },
                "Wave567 signature/comment hardening: CFrontEnd__RenderAndProcessModalPanel and CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady call this four-float cursor rectangle predicate. The body rejects key-trap/dev-mode paths, checks cursor-ready DAT_0089bdf4, tests stored cursor x/y against [left,right) and [top,bottom), consumes DAT_0089bdf4 on a hit, and returns the result in AL. Static retail evidence only; exact cursor-state type, runtime UI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cursor-rect", "frontend-input", "consume-cursor", "signature-corrected")
            ),
            new Spec(
                "0x00523db0",
                "Input__ResetMouseTransientState",
                "CProfiler__ResetAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave567 owner/signature/comment correction: supersedes the misleading CProfiler__ResetAll label. The body clears the cursor/click button down/up latches, click-ready and cursor-ready flags, wheel accumulator, and byte DAT_00640054. Xrefs include PlatformInput__InitMouse, PlatformInput__ShutdownMouse, CFrontEnd__Process, CGame__MainLoop, and two no-function render-tail callsites at 0x0053f2dc/0x0053f306 that immediately test the same mouse transient globals. Source has both CProfiler::ResetAll and CVBufTexture::ResetAll callsite hints, so this saved name is behavior-bounded retail input state, not exact source identity. Runtime mouse behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mouse-state", "transient-reset", "owner-corrected", "signature-corrected", "renamed")
            )
        };

        Stats stats = new Stats();
        println("ApplyInputCursorWave567 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave567 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
