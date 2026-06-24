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

public class ApplyPauseMenuTailWave465 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.oldName = oldName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "pausemenu-tail-wave465",
            "retail-binary-evidence"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.name)) {
                throw new IllegalStateException(
                    "Unexpected function name at " + spec.address + ": " + fn.getName()
                );
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
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
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d01c0",
                "CMenuItem__ctor_like_004d01c0",
                "CMenuItem__RestoreCompactVTable",
                "__fastcall",
                voidType,
                "Wave465 correction: Compact menu-item vtable-reset helper that writes PTR_CMenuItem__scalar_deleting_dtor_005db440 to this+0x00; reached by unwind cleanup and the shared compact scalar-deleting destructor. Static retail-binary evidence only; exact class identity, source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("menu-item", "vtable-reset", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("menu_item", voidPtr)
                }
            ),
            new Spec(
                "0x004d0290",
                "CControllerBackMenuItem__VFunc_04_004d0290",
                "CControllerBackMenuItem__RenderBindingCapacityWarning",
                "__thiscall",
                voidType,
                "Wave465 correction: Controller-back menu-item render helper that checks free binding capacity through Controls__FindFirstFreeBindingSlot, uses localized warning ids 0xe8/0xe9 to choose highlight color, and forwards to CMenuItem__RenderWithColor. Static retail-binary evidence only; exact UI text semantics, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("menu-item", "controller-back", "render", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("render_flags", intType)
                }
            ),
            new Spec(
                "0x004d0490",
                "VFuncSlot_00_004d0490",
                "CMenuItem__shared_compact_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave465 correction: Shared compact menu-item scalar-deleting destructor referenced by multiple menu-item family vtables; calls CMenuItem__RestoreCompactVTable, frees this when flags bit 0 is set, and returns this. Static retail-binary evidence only; exact concrete type ownership, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("menu-item", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", intType)
                }
            ),
            new Spec(
                "0x004d04b0",
                "CPauseMenu__VFunc_01_004d04b0",
                "CPauseMenu__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave465 correction: CPauseMenu scalar-deleting destructor wrapper referenced from the pause-menu vtable; calls CPauseMenu__dtor_base, frees this when flags bit 0 is set, and returns this. Static retail-binary evidence only; exact layout, source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("pause-menu", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", intType)
                }
            ),
            new Spec(
                "0x004d0510",
                "CPauseMenu__LoadPauseTextures",
                "CPauseMenu__LoadPauseTextures",
                "__fastcall",
                voidType,
                "Wave465 correction: Loads pause-menu texture resources by walking the menu range list at +0x14, calling CMenuItemRange__LoadTexture per child, loading pause_circle01/02, releasing any prior shared blank texture, and loading FrontEnd_v2/FE_Blank.tga. Static retail-binary evidence only; runtime rendering behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("pause-menu", "texture-load", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("pause_menu", voidPtr)
                }
            ),
            new Spec(
                "0x004d05e0",
                "CPauseMenu__ctor_like_004d05e0",
                "CPauseMenu__dtor_base",
                "__fastcall",
                voidType,
                "Wave465 correction: CPauseMenu destructor-body helper that restores the pause-menu vtable, destroys child menu ranges, clears the linked item set, releases transient prompt/menu objects and pause textures, releases the shared blank texture, and calls CMonitor__Shutdown. Static retail-binary evidence only; exact layout, source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("pause-menu", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("pause_menu", voidPtr)
                }
            ),
            new Spec(
                "0x004d06e0",
                "CPauseMenu__ResumeGameAndPersistOptions",
                "CPauseMenu__ResumeGameAndPersistOptions",
                "__fastcall",
                voidType,
                "Wave465 correction: Resume/persist helper that relinquishes controllers currently targeting the pause menu, unpauses the game, reinitializes mouse input, serializes the current career/options buffer, optionally writes the active save slot, writes defaultoptions.bea, frees the buffer, clears transient prompt/menu objects, and timestamps the pause menu. Static retail-binary evidence only; runtime save/UI behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("pause-menu", "options-persist", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("pause_menu", voidPtr)
                }
            ),
            new Spec(
                "0x004d0810",
                "CPauseMenu__ButtonPressed",
                "CPauseMenu__ButtonPressed",
                "__thiscall",
                voidType,
                "Wave465 correction: Pause-menu button dispatcher that stores the selected item id, handles range navigation, resume/defaultoptions persistence, message-box/message-log transitions, controller handoff to temporary menu ranges, binding-prompt construction, option toggles through CEngine__SetOptionValueAndNotifyTarget, and frontend sound feedback. Static retail-binary evidence only; exact action ids, UI semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("pause-menu", "button-dispatch", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("menu_item", voidPtr),
                    param("button_context", intType)
                }
            ),
            new Spec(
                "0x004d0db0",
                "CPauseMenu__InitBindingPromptAction",
                "CPauseMenu__InitBindingPromptAction",
                "__thiscall",
                voidPtr,
                "Wave465 correction: Binding-prompt action-node initializer that calls CPauseMenu__InitAndSetActiveReader with action_id and pause_menu, stores the menu item at +0x08, returns this, and has RET 0x0c cleanup for three stack arguments. Static retail-binary evidence only; exact node layout, source identity, runtime binding behavior, and rebuild parity remain unproven.",
                tags("pause-menu", "binding-prompt", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("menu_item", voidPtr),
                    param("pause_menu", voidPtr),
                    param("action_id", intType)
                }
            ),
            new Spec(
                "0x004d0e40",
                "CGameMenu__ctor_like_004d0e40",
                "CGameMenu__InitBase",
                "__fastcall",
                voidType,
                "Wave465 correction: Compact CGameMenu base initializer that clears +0x04 and installs PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c before the caller initializes the embedded CMenuItemRangeVariant and owned action set. Static retail-binary evidence only; exact layout, source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("game-menu", "constructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("game_menu", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave465 apply had missing/bad targets");
        }
    }
}
