//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.plugin.core.clear.ClearCmd;
import ghidra.app.plugin.core.clear.ClearOptions;
import ghidra.app.plugin.core.clear.ClearOptions.ClearType;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFepBeConfigBoundarySignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
            this.createIfMissing = createIfMissing;
            this.parameters = parameters;
        }
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

    private Function existingFunction(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function repairInitListingIfNeeded(Spec spec, Function existing, boolean dryRun) throws Exception {
        if (!spec.address.equals("0x0044fa90")) {
            return existing;
        }

        Address start = addr("0x0044fa90");
        Address end = addr("0x0044fd9f");
        boolean hasInstruction = getInstructionAt(start) != null;
        boolean hasBody = existing != null && existing.getBody().contains(start);
        if (hasInstruction && hasBody) {
            return existing;
        }

        if (dryRun) {
            println("DRY: 0x0044fa90 needs listing/body repair; has_instruction=" + hasInstruction + " body_contains_start=" + hasBody + "; would decode and set body 0x0044fa90-0x0044fd9f for " + spec.name);
            return existing;
        }

        AddressSet range = new AddressSet(start, end);
        boolean clearOk = true;
        boolean disasmOk = true;
        if (!hasInstruction) {
            ClearOptions options = new ClearOptions(false);
            options.setShouldClear(ClearType.DATA, true);
            options.setShouldClear(ClearType.INSTRUCTIONS, true);
            ClearCmd clear = new ClearCmd(range, options);
            clearOk = clear.applyTo(currentProgram, monitor);
            if (!clearOk) {
                throw new IllegalStateException("Instruction/data clear failed for 0x0044fa90-0x0044fd9f");
            }
            DisassembleCommand disassemble = new DisassembleCommand(start, range, true);
            disasmOk = disassemble.applyTo(currentProgram, monitor);
        }

        Function repaired = existing;
        if (repaired == null) {
            CreateFunctionCmd create = new CreateFunctionCmd(spec.name, start, null, SourceType.USER_DEFINED);
            boolean createOk = create.applyTo(currentProgram, monitor);
            repaired = create.getFunction();
            if (repaired == null && createOk) {
                repaired = getFunctionAt(start);
            }
        }
        if (repaired == null || getInstructionAt(start) == null) {
            throw new IllegalStateException("Failed to repair decoded instruction/function at 0x0044fa90; disassemble=" + disasmOk);
        }
        repaired.setBody(range);
        if (!repaired.getBody().contains(start)) {
            throw new IllegalStateException("Function body still does not contain 0x0044fa90");
        }
        println("OK: repaired decoded listing/body for 0x0044fa90 CFEPBEConfig__Init; disassemble=" + disasmOk + " clear=" + clearOk);
        return repaired;
    }

    private Function getOrCreate(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn != null) {
            return repairInitListingIfNeeded(spec, fn, dryRun);
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        return fn;
    }

    private boolean allowedName(Function fn, Spec spec) {
        if (fn.getName().equals(spec.name)) {
            return true;
        }
        for (String previous : spec.previousNames) {
            if (fn.getName().equals(previous)) {
                return true;
            }
        }
        return false;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getOrCreate(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
        }
        if (!allowedName(fn, spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
        }

        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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

        Function readBack = getOrCreate(spec, false);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fep-beconfig-wave367",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x0044eab0", "CFEPMultiplayerStart__GetConfigIdByIndex", "__cdecl", intType,
                "Frontend helper for the currently selected BattleEngine profile: walks the selected config list and returns the config id at config_index. Static retail evidence only; source identity, concrete list layout, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-multiplayer-start", "config-list", "comment-hardened"),
                new String[] {"CFEPMultiplayerStart__GetConfigIdByIndex"},
                false,
                new ParameterImpl[] {param("config_index", intType)}),
            new Spec("0x0044eb30", "CFEPMultiplayerStart__SetConfigDescriptionByIndex", "__cdecl", voidType,
                "Frontend helper for the selected BattleEngine config entry: resolves the config name, maps type ids to text strings, and falls back to Unknown Configuration. Static retail evidence only; exact source identity, string table completeness, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-multiplayer-start", "config-list", "text"),
                new String[] {"CFEPMultiplayerStart__SetConfigDescriptionByIndex"},
                false,
                new ParameterImpl[] {param("config_index", intType)}),
            new Spec("0x0044ecf0", "CFEPMultiplayerStart__GetConfigCount", "__cdecl", intType,
                "Returns the selected BattleEngine profile's config count after matching DAT_0089d94c against the profile list. Static retail evidence only; exact source identity, runtime selection state, and rebuild parity remain unproven.",
                tags("fep-multiplayer-start", "config-list", "comment-hardened"),
                new String[] {"CFEPMultiplayerStart__GetConfigCount"},
                false,
                new ParameterImpl[] {}),
            new Spec("0x0044ed40", "CFEPMultiplayerStart__LookupProfileField5CBySelectionIndex", "__cdecl", intType,
                "Looks up the selected config name and returns the matched profile/config record field at +0x5c. Static retail evidence only; exact field semantics, source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-multiplayer-start", "config-record", "field-reader"),
                new String[] {"CFEPMultiplayerStart__LookupProfileField5CBySelectionIndex"},
                false,
                new ParameterImpl[] {param("config_index", intType)}),
            new Spec("0x0044eea0", "CFEPMultiplayerStart__LookupProfileField4CPlusFlagBySelectionIndex", "__cdecl", intType,
                "Looks up the selected config name and returns profile/config field +0x4c adjusted by the boolean-style flag at +0x60. Static retail evidence only; exact field semantics, source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-multiplayer-start", "config-record", "field-reader"),
                new String[] {"CFEPMultiplayerStart__LookupProfileField4CPlusFlagBySelectionIndex"},
                false,
                new ParameterImpl[] {param("config_index", intType)}),
            new Spec("0x0044f030", "CFEPBEConfig__GetWeaponProperty", "__cdecl", intType,
                "BattleEngine config weapon-property lookup: follows the selected profile's primary weapon-name list, resolves DAT_008553e8 weapon records, and returns property slots +0x10/+0x11/+0x12. Static retail evidence only; exact stat names, source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "weapon-config", "property-reader"),
                new String[] {"CFEPBEConfig__GetWeaponProperty"},
                false,
                new ParameterImpl[] {param("config", voidPtr), param("weapon_index", intType), param("property_index", intType)}),
            new Spec("0x0044f300", "CFEPBEConfig__GetWeaponPropertyAlt", "__cdecl", intType,
                "Alternate BattleEngine config weapon-property lookup using the matched config record's alternate weapon-name list at +0x50/+0x58 before resolving DAT_008553e8 property slots. Static retail evidence only; exact stat names, source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "weapon-config", "property-reader", "alternate-list"),
                new String[] {"CFEPBEConfig__GetWeaponPropertyAlt"},
                false,
                new ParameterImpl[] {param("config", voidPtr), param("weapon_index", intType), param("property_index", intType)}),
            new Spec("0x0044f530", "CFEPBEConfig__PlayWeaponSound", "__cdecl", voidType,
                "BattleEngine config sound/text helper: resolves the selected profile's primary weapon-name list and uses weapon-record field +0x0f as the text/sound id, with Unknown Weapon fallback. Static retail evidence only; exact source identity, runtime audio/frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "weapon-config", "sound-text"),
                new String[] {"CFEPBEConfig__PlayWeaponSound"},
                false,
                new ParameterImpl[] {param("config", voidPtr), param("weapon_index", intType)}),
            new Spec("0x0044f830", "CFEPBEConfig__PlayWeaponSoundAlt", "__cdecl", voidType,
                "Alternate BattleEngine config sound/text helper using the matched config record's alternate weapon-name list at +0x50/+0x58 and weapon-record field +0x0f, with Unknown Weapon fallback. Static retail evidence only; exact source identity, runtime audio/frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "weapon-config", "sound-text", "alternate-list"),
                new String[] {"CFEPBEConfig__PlayWeaponSoundAlt"},
                false,
                new ParameterImpl[] {param("config", voidPtr), param("weapon_index", intType)}),
            new Spec("0x0044fa90", "CFEPBEConfig__Init", "__thiscall", voidType,
                "Recovered CFEPBEConfig init boundary: starts at the SEH prologue before the beconf::init() 0-5 trace strings, initializes page/config state, and ends before CFEPBEConfig__Cleanup. This corrects the old mid-prologue 0x0044fa93 note. Static retail evidence only; exact source identity, call path, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "function-boundary", "init", "boundary-corrected"),
                new String[] {"CFEPBEConfig__Init"},
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0044fda0", "CFEPBEConfig__Cleanup", "__thiscall", voidType,
                "CFEPBEConfig cleanup/shutdown helper: frees the owned frontend object at this+0x08, walks config entries at this+0x20, invokes CFEPBEConfig__CleanupSquads for each entry, and frees entry storage. Static retail evidence only; exact source identity, lifecycle caller coverage, runtime behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "cleanup", "comment-hardened"),
                new String[] {"CFEPBEConfig__Cleanup"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0044fdf0", "CFEPBEConfig__CleanupSquads", "__thiscall", voidType,
                "Clears a CFEPBEConfig entry's squad/name pointer set at +0x14, freeing nested strings and nodes before destroying the set. Static retail evidence only; exact entry layout, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "cleanup", "squad-list"),
                new String[] {"CFEPBEConfig__CleanupSquads"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0044fe70", "CFEPBEConfig__Load", "__thiscall", voidType,
                "Loads one BattleEngine config entry from CDXMemBuffer: allocates a 0x24-byte entry, initializes its string/squad set, reads versioned fields and variable strings, then appends it to this+0x20. Calling convention corrected from stale stdcall to ECX=this plus mem_buffer. Static retail evidence only; file-format completeness, runtime behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "loader", "signature-hardened"),
                new String[] {"CFEPBEConfig__Load"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("mem_buffer", voidPtr)}),
            new Spec("0x00450010", "CFEPBEConfig__UpdateTransitionTimers", "__thiscall", voidType,
                "Recovered CFEPBEConfig vtable slot 1 boundary: updates transition/timer fields at this+0x0c/+0x14/+0x18, handles a zero-state page callback path, and returns with RET 0x4. Static retail evidence only; exact virtual method name, source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "function-boundary", "vtable-slot", "timer-state"),
                new String[] {"CFEPBEConfig__UpdateTransitionTimers"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("menu_state", intType)}),
            new Spec("0x00450090", "CFEPBEConfig__ButtonPressed", "__thiscall", voidType,
                "Recovered CFEPBEConfig vtable slot 2 boundary: dispatches frontend button/action codes 0x2a-0x2e, changes selected config indices, plays selection sounds, and updates timing state. Static retail evidence only; exact source identity, complete control mapping, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "function-boundary", "vtable-slot", "button-handler"),
                new String[] {"CFEPBEConfig__ButtonPressed"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("button", intType), param("player_index", intType)}),
            new Spec("0x00450390", "CFEPBEConfig__RenderPreCommon", "__thiscall", voidType,
                "Recovered CFEPBEConfig vtable slot 3 boundary: renders the common selection marker path when dest/state is 4 and otherwise handles transition-dependent marker visibility. Static retail evidence only; exact source identity, render-state semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "function-boundary", "vtable-slot", "render-pre-common"),
                new String[] {"CFEPBEConfig__RenderPreCommon"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("transition", floatType), param("dest", intType)}),
            new Spec("0x00450400", "CFEPBEConfig__PushProjectionMatrixForRender", "__cdecl", voidType,
                "Saves the active projection matrix to a scratch buffer and installs CFEPBEConfig render projection values before frontend rendering. Static retail evidence only; exact render pipeline ownership, runtime behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "render", "projection"),
                new String[] {"CFEPBEConfig__PushProjectionMatrixForRender"},
                false,
                new ParameterImpl[] {}),
            new Spec("0x00450440", "CFEPBEConfig__PopProjectionMatrixAfterRender", "__cdecl", voidType,
                "Restores the saved projection matrix after CFEPBEConfig rendering and marks the projection state dirty. Static retail evidence only; exact render pipeline ownership, runtime behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "render", "projection"),
                new String[] {"CFEPBEConfig__PopProjectionMatrixAfterRender"},
                false,
                new ParameterImpl[] {}),
            new Spec("0x00450460", "CFEPMultiplayerStart__RenderConfigPipRow", "__cdecl", voidType,
                "Renders a row of BattleEngine config rating pips: rounds rating to a 1-5 count, selects color bands, applies alpha from argb, and calls CDXSurf__RenderSurface for each pip. Static retail evidence only; exact source identity, visual parity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-multiplayer-start", "fep-beconfig", "render", "pip-row"),
                new String[] {"CFEPMultiplayerStart__RenderConfigPipRow"},
                false,
                new ParameterImpl[] {param("x", floatType), param("y", floatType), param("rating", floatType), param("argb", uintType)}),
            new Spec("0x004505b0", "CFEPBEConfig__Render", "__thiscall", voidType,
                "Recovered CFEPBEConfig vtable slot 4 boundary: renders the BattleEngine config page, including frontend surfaces, projection push/pop, config entries, and pip rows. Static retail evidence only; exact source identity, complete visual semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "function-boundary", "vtable-slot", "render"),
                new String[] {"CFEPBEConfig__Render"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("transition", floatType), param("dest", intType)}),
            new Spec("0x00451930", "CFEPBEConfig__FindEntryByName", "__cdecl", voidPtr,
                "Linear lookup over the global config/profile list DAT_006602a0: compares entry_name against each record name at +0xa8 and returns the matching record pointer or null. Static retail evidence only; exact record layout, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "config-record", "lookup", "signature-hardened"),
                new String[] {"CFEPBEConfig__FindEntryByName"},
                false,
                new ParameterImpl[] {param("entry_name", charPtr)}),
            new Spec("0x004519c0", "CFEPBEConfig__ResetTimestampAndModeFlag", "__thiscall", voidType,
                "CFEPBEConfig vtable slot 5 helper: stores PLATFORM time at this+0x04, clears this+0x10, and re-enables that flag when current page/config 0x2c6 has more than three entries. Static retail evidence only; exact virtual method name, source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("fep-beconfig", "vtable-slot", "timestamp", "mode-flag", "name-corrected"),
                new String[] {"CFEPBEConfig__VFunc_06_004519c0", "CFEPBEConfig__ResetTimestampAndModeFlag"},
                false,
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int changedOrWouldChange = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changedOrWouldChange++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " changed_or_would_change=" + changedOrWouldChange + " failed=" + failed + " dry=" + dryRun);
        if (failed > 0) {
            throw new IllegalStateException("FEPBEConfig boundary/signature tranche failed for " + failed + " target(s)");
        }
    }
}
