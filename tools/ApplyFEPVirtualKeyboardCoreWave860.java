//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyFEPVirtualKeyboardCoreWave860 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedPrototype;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedPrototype, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedPrototype = expectedPrototype;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fepvirtualkeyboard-core-wave860",
            "wave860-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "frontend",
            "fepvirtualkeyboard",
            "virtual-keyboard",
            "save-name"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0051ff90",
                "CFEPVirtualKeyboard__Init",
                "int CFEPVirtualKeyboard__Init(void * this)",
                null,
                null,
                null,
                "Wave860 static read-back: CFEPVirtualKeyboard vtable 0x005db830 slot 0 init helper. The body seeds weighted-column state this+0x6f4 to 0.5, clears edit cursor/mode/keyboard page fields at this+0x44, this+0x4c, this+0x50, and this+0x6e4..0x6f0, calls CFEPVirtualKeyboard__InitKeyboardLayout(this), and returns 1. Static retail Ghidra evidence only; exact CFEPVirtualKeyboard layout, runtime virtual-keyboard behavior, save-name side effects, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "init", "keyboard-layout")
            ),
            new Spec(
                "0x0051ffd0",
                "CFEPVirtualKeyboard__Shutdown",
                "void CFEPVirtualKeyboard__Shutdown(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram)
                },
                "Wave860 static read-back/signature correction: CFEPVirtualKeyboard vtable 0x005db830 slot 1 shutdown helper. The body checks whether PlatformInput's active key sink is DAT_0051feb0 and, when active, clears it through PlatformInput__SetKeySinkCore(&DAT_00855bb0, null). The stale cdecl storage was corrected to the vtable object-method convention. Static retail Ghidra evidence only; exact key-sink object contract, runtime virtual-keyboard input behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "shutdown", "key-sink", "signature-hardened")
            ),
            new Spec(
                "0x0051fff0",
                "CFEPVirtualKeyboard__SeedUniqueDefaultSaveName",
                "void CFEPVirtualKeyboard__SeedUniqueDefaultSaveName(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram)
                },
                "Wave860 static read-back/name correction: supersedes stale CFEPOptions__EnumerateSaveFiles. The ECX receiver is the virtual-keyboard edit buffer owner, and the body writes a default wide save name at this+0x04 by combining string 0x0063fd34 (BEA) with format 0x00629314 ( %d), enumerates existing savegames through EnumerateSaveFiles_1/2, increments the suffix until a non-duplicate name is found or the 0x1001 cap is reached, clamps cursor length to 0x1f at this+0x44, and sets this+0x48. Static retail Ghidra evidence only; exact save-name policy, runtime filesystem behavior, BEA patching, and rebuild parity remain unproven.",
                tags("name-corrected", "signature-hardened", "save-enumeration", "default-save-name")
            ),
            new Spec(
                "0x00520130",
                "CFEPVirtualKeyboard__TransitionNotification",
                "void CFEPVirtualKeyboard__TransitionNotification(void * this, int from_page)",
                null,
                null,
                null,
                "Wave860 static read-back: CFEPVirtualKeyboard vtable 0x005db830 slot 6 transition-notification helper. For from_page 0, 9, or 0xe it reseeds the default save name when this+0x48 is set, using the same BEA plus numeric suffix and EnumerateSaveFiles_1/2 duplicate-avoidance loop as CFEPVirtualKeyboard__SeedUniqueDefaultSaveName, then resets keyboard page/row/column fields this+0x6e4..0x6ec, restores weighted-column 0.5 at this+0x6f4, and clamps cursor position this+0x44 to the edit-buffer length or 0x1f. Static retail Ghidra evidence only; exact transition semantics, runtime save-name behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "transition-notification", "default-save-name", "save-enumeration")
            ),
            new Spec(
                "0x005202d0",
                "CFEPVirtualKeyboard__Process",
                "void CFEPVirtualKeyboard__Process(void * this, int state)",
                null,
                null,
                null,
                "Wave860 static read-back: CFEPVirtualKeyboard vtable 0x005db830 slot 2 process helper. For non-state-3 paths it refreshes the shared save list through CFEPDirectory__RefreshSaveFileList(&DAT_008a1f8c, state). In state 0 it installs key sink DAT_0051feb0 through PlatformInput__SetKeySinkCore when needed, checks movie/HUD gate DAT_00677614, polls PCPlatform__GetStorageDeviceInfo on DAT_008a9694, and shows CFEPSaveGame__RemovedMUWhinge(0x3c) when no storage device is inserted. Leaving state 0 clears the key sink when this keyboard sink is active. Static retail Ghidra evidence only; exact process-state meaning, runtime storage/input behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "process", "key-sink", "save-list", "storage-device")
            ),
            new Spec(
                "0x00520370",
                "CFEPVirtualKeyboard__ButtonPressed",
                "void CFEPVirtualKeyboard__ButtonPressed(void * this, int button, float val)",
                null,
                null,
                null,
                "Wave860 static read-back: CFEPVirtualKeyboard vtable 0x005db830 slot 3 button handler. Buttons 0x2a/0x2b move row selection through CFEPVirtualKeyboard__MoveSelectionToRow with wraparound; button 0x2c plays accept sound and dispatches the selected key token through CFEPVirtualKeyboard__HandleKeyToken; button 0x2e plays cancel sound and returns to page 0 with fade 0x46; buttons 0x36/0x37 cycle key-column selection, reset weighted-column this+0x6f4 to 0.5, and loop until CFEPVirtualKeyboard__IsSpecialKeyBlocked returns false. Static retail Ghidra evidence only; exact input mapping, live UI behavior, save-name side effects, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "button-handler", "selection", "key-token")
            ),
            new Spec(
                "0x00521100",
                "CFEPVirtualKeyboard__Render",
                "void CFEPVirtualKeyboard__Render(void * this, float transition, int dest)",
                null,
                null,
                null,
                "Wave860 static read-back: CFEPVirtualKeyboard vtable 0x005db830 slot 5 render helper. The body computes a clamped alpha from transition, renders/polls the shared save list through CFEPDirectory__RenderSaveFileList(&DAT_008a1f8c, transition, dest-or-0xe), copies a clicked save-name row into this+0x04 with CRT__WcsNcpyZeroPad, updates cursor length this+0x44 and active flag this+0x48, plays accept sound on selection, renders context help prompt 5, calls CFEPVirtualKeyboard__DrawPanel(this, DAT_0063fd30, transition, alpha), draws the localized title bar, and renders overlay effects. Static retail Ghidra evidence only; exact render layout, runtime frontend/input behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "render", "save-list", "draw-panel")
            ),
            new Spec(
                "0x005214d0",
                "CFEPVirtualKeyboard__IsSpecialKeyBlocked",
                "int CFEPVirtualKeyboard__IsSpecialKeyBlocked(void * this)",
                null,
                null,
                null,
                "Wave860 static read-back: CFEPVirtualKeyboard special-key filter called by ButtonPressed and MoveSelectionToRow. The body reads the selected key token from the table indexed by this+0x6e4/0x6e8/0x6ec; blocks tokens 4 and 5 on keyboard page 1, and blocks token 9 when the edit buffer at this+0x04 is empty or contains only spaces. Static retail Ghidra evidence only; exact key-token enum identity, runtime UI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("special-key-filter", "selection", "edit-buffer")
            )
        };
    }

    private Set<String> currentTags(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, String[] expected) {
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean applyTags(Function fn, String[] expected, boolean dryRun) {
        boolean changed = false;
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                changed = true;
                if (!dryRun) {
                    fn.addTag(tag);
                }
            }
        }
        return changed;
    }

    private boolean conventionOk(Function fn, String expectedConvention) throws Exception {
        if (expectedConvention == null) {
            return true;
        }
        return expectedConvention.equals(fn.getCallingConventionName());
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            stats.bad++;
            return;
        }

        boolean nameOk = fn.getName().equals(spec.expectedName);
        boolean prototypeOk = fn.getSignature().getPrototypeString().equals(spec.expectedPrototype);
        boolean conventionOk = conventionOk(fn, spec.callingConvention);
        boolean signatureOk = prototypeOk && conventionOk;
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasAllTags(fn, spec.tags);
        boolean canUpdateSignature = spec.callingConvention != null;

        if (!nameOk && !dryRun) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
        }
        if (!nameOk) {
            stats.wouldRename++;
            if (!dryRun) {
                stats.renamed++;
            }
        }

        if (!signatureOk && canUpdateSignature) {
            if (!dryRun) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            stats.signatureUpdated++;
        } else if (!signatureOk) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedPrototype + " convention=" + spec.callingConvention + " actual=" + fn.getSignature().getPrototypeString() + " convention=" + fn.getCallingConventionName());
            stats.bad++;
        }

        if (!commentOk && !dryRun) {
            fn.setComment(spec.comment);
        }
        if (!tagsOk) {
            applyTags(fn, spec.tags, dryRun);
        }

        if (commentOk && tagsOk && signatureOk && nameOk) {
            stats.skipped++;
            println("SKIP_OK: " + spec.address + " " + spec.expectedName);
        } else {
            stats.updated++;
            if (signatureOk || !canUpdateSignature) {
                stats.commentOnlyUpdated++;
            }
            println((dryRun ? "DRY_UPDATE: " : "APPLY_UPDATE: ") + spec.address + " " + spec.expectedName);
        }

        if (!dryRun) {
            Function readback = functionAtEntry(spec.address);
            String actualSignature = readback.getSignature().getPrototypeString();
            boolean readbackOk = readback.getName().equals(spec.expectedName)
                && actualSignature.equals(spec.expectedPrototype)
                && conventionOk(readback, spec.callingConvention)
                && spec.comment.equals(readback.getComment())
                && hasAllTags(readback, spec.tags);
            if (readbackOk) {
                println("READBACK_OK: " + spec.address + " " + actualSignature + " convention=" + readback.getCallingConventionName());
            } else {
                println("READBACK_BAD: " + spec.address + " name=" + readback.getName() + " signature=" + actualSignature + " convention=" + readback.getCallingConventionName());
                stats.bad++;
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
