//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFrontendSaveMultiplayerWave802 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "frontend-save-multiplayer-wave802",
            "wave802-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.newName)
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

    private boolean allowedName(Function fn, Spec spec) {
        return fn.getName().equals(spec.newName) || fn.getName().equals(spec.oldName);
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
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
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        String readComment = fn.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.newName);
                return;
            }
            if (!allowedName(fn, spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName()
                    + " expected=" + spec.oldName + " or " + spec.newName);
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.newName);
            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(spec.comment)
                || !hasAllTags(fn, spec.tags);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.newName);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                else if (commentOrTagsNeedUpdate) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.newName, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            if (!signatureNeedsUpdate) {
                stats.commentOnlyUpdated++;
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.newName + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x0044d390",
                "CFEPSaveGame__InitDialogAndLayoutState",
                "FEMessBox__Create",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("wrap_width", floatType),
                    param("text_scale", floatType),
                    param("wide_text", shortPtr),
                    param("font", voidPtr),
                    param("fade_start", intType),
                    param("fade_ticks", intType),
                    param("prompt_mode", intType),
                    param("option_mode", intType),
                    param("question_id", intType)
                },
                "Wave802 static read-back: corrected the stale CFEPSaveGame-only label to the shared FEMessBox.Create path. RET 0x2c proves eleven explicit stack arguments after ECX=this; source callsites in FEPSaveGame.cpp, FEPLoadGame.cpp, and FrontEnd.cpp call FEMESSBOX.Create with x/y/wrap/text/font/fade/option/question arguments. The body stores the layout fields at this+0x04/+0x08/+0x0c/+0x10/+0x14/+0x1f5c/+0x1f78/+0x1f84/+0x1f90/+0x1f98/+0x1f9c, wraps wide text through TextLayout__WrapWideTextToFixedLines, records font height, and arms the message-box active state. Static retail Ghidra/source-callsite evidence only; exact FEMessBox layout, runtime frontend message-box behavior, BEA patching, and rebuild parity remain deferred.",
                tags("femessbox", "message-box-create", "name-corrected", "signature-corrected", "ret-002c", "tranche-head")
            ),
            new Spec(
                "0x00465640",
                "CLTShell__InvokeWithLoadingTransitionGate",
                "CFMV__PlayFullscreenWithLoadingGate",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("movie_path", charPtr),
                    param("force_loading_gate", intType),
                    param("use_language_index", intType),
                    param("vfunc_arg3", intType),
                    param("vfunc_arg4", intType),
                    param("vfunc_arg5", intType),
                    param("vfunc_arg6", intType)
                },
                "Wave802 static read-back: corrected the CLTShell-only placeholder to the FMV full-screen play wrapper. RET 0x1c proves seven explicit stack arguments after ECX=this. Retail instructions store a loading/non-interactive gate at this+0x0c using force_loading_gate or DAT_006630cc, call CController__SetNonInteractiveSection(true), dispatch vtable slot +0x2c with movie_path, conditional g_LanguageIndex, and four forwarded args, then clear the non-interactive section. Source callsites include CGame::RunIntroFMV/RunOutroFMV and FEPGoodies.cpp FMV.PlayFullscreen(...). Static retail Ghidra/source-callsite evidence only; exact CFMV layout, exact vtable slot contract, runtime video playback/localization behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cfmv", "play-fullscreen", "loading-gate", "name-corrected", "signature-corrected", "ret-001c")
            ),
            new Spec(
                "0x00465f10",
                "CFEPMultiplayerStart__ctor",
                "CFEPMultiplayerStart__ctor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave802 static read-back: CFEPMultiplayerStart constructor body called by CDXFrontEnd__Constructor. The body installs the CFEPMultiplayerStart vtable at this+0x00, constructs monitor/camera/frontend-video/member helpers, calls CMissionScriptObjectCode__CMissionScriptObjectCode at this+0x37e8, initializes the SubObj8848 helper at this+0x8848, and sets multiple embedded vtable/member blocks. Static retail Ghidra evidence only; exact FEPMultiplayerStart layout, runtime multiplayer frontend behavior, BEA patching, and rebuild parity remain deferred.",
                tags("fepmultiplayerstart", "constructor", "frontend-page", "embedded-subobjects")
            ),
            new Spec(
                "0x004661c0",
                "DeviceObject__ctor_like_00512d50",
                "DeviceObject__dtor_thunk",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave802 static read-back: corrected ctor_like placeholder to a one-instruction DeviceObject cleanup thunk. The body is JMP 0x00512d50, whose read-back body installs the DeviceObject scalar-deleting dtor vtable and unlinks this from the two global DeviceObject lists rooted at DAT_00889074 and DAT_00889078. Xrefs come from constructor-unwind rows and CDXFrontEndVideo__scalar_deleting_dtor. Static retail Ghidra evidence only; exact DeviceObject layout, runtime D3D device-object lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("deviceobject", "dtor-thunk", "name-corrected", "signature-corrected", "jmp-thunk")
            ),
            new Spec(
                "0x004661f0",
                "CFEPMultiplayerStart__InitWaitingThreadSubsystem",
                "CFEPMultiplayerStart__CleanupMissionScriptWaitingThread",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave802 static read-back: corrected the init-like label to a constructor-unwind cleanup wrapper. The body adds 0x0c to ECX and jumps to CWaitingThread__dtor_body at 0x00528bf0; the unwind xref supplies a pointer that resolves to the CMissionScriptObjectCode waiting-thread subobject inside CFEPMultiplayerStart construction state. Static retail Ghidra evidence only; exact owner layout, runtime async script/thread behavior, BEA patching, and rebuild parity remain deferred.",
                tags("fepmultiplayerstart", "missionscriptobjectcode", "waitingthread", "cleanup-thunk", "name-corrected", "signature-corrected")
            ),
            new Spec(
                "0x00466290",
                "CWaitingThread__ctor_like_00528bf0",
                "CWaitingThread__dtor_thunk",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave802 static read-back: corrected ctor_like placeholder to a one-instruction CWaitingThread cleanup thunk. The body is JMP 0x00528bf0, whose read-back body signals and waits for the thread handles when active, closes handles, marks handle fields -1, and unlinks the object from DAT_0089c01c. Static retail Ghidra evidence only; exact CWaitingThread layout, runtime threading behavior, BEA patching, and rebuild parity remain deferred.",
                tags("waitingthread", "dtor-thunk", "name-corrected", "signature-corrected", "jmp-thunk")
            ),
            new Spec(
                "0x00512d50",
                "DeviceObject__ctor_like_00512d50",
                "DeviceObject__dtor_body",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave802 static read-back: corrected ctor_like placeholder to the DeviceObject cleanup body. The body installs the DeviceObject scalar-deleting dtor vtable at this+0x00, scans DAT_00889074 and DAT_00889078, and unlinks this from either global list by updating the previous node or root pointer. Static retail Ghidra evidence only; exact DeviceObject layout, runtime D3D device-object lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("deviceobject", "dtor-body", "global-list-unlink", "name-corrected", "signature-corrected")
            ),
            new Spec(
                "0x00528bf0",
                "CWaitingThread__ctor_like_00528bf0",
                "CWaitingThread__dtor_body",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave802 static read-back: corrected ctor_like placeholder to the CWaitingThread cleanup body. The body installs the base/purecall-adjacent vtable, checks the event handle at this+0x0c, signals shutdown at this+0x14, waits on and closes handles at this+0x04/+0x08/+0x0c/+0x10, resets them to -1, and unlinks this from the global list rooted at DAT_0089c01c via the next pointer at this+0x18. Static retail Ghidra evidence only; exact CWaitingThread layout, runtime threading behavior, BEA patching, and rebuild parity remain deferred.",
                tags("waitingthread", "dtor-body", "handle-cleanup", "global-list-unlink", "name-corrected", "signature-corrected", "tranche-tail")
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

        println("ApplyFrontendSaveMultiplayerWave802 mode=" + (dryRun ? "dry" : "apply"));
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave802 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
