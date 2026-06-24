//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendControlsSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
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

    private Function getExistingFunction(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrThrow(String addressText) {
        Address address = addr(addressText);
        Function fn = getExistingFunction(address);
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
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
        Function fn = getFunctionOrThrow(spec.address);
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

        Function readBack = getFunctionOrThrow(spec.address);
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
            "frontend-controls-wave370",
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType shortType = ShortDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00453460", "OptionsEntries__InitDefaultDualBindingsTable", "__cdecl", voidType,
                "Signature/comment hardening: initializes the default dual-binding options-entry table at DAT_00677af0 with 16 normal entries, then writes sentinel entries at DAT_00677cf0 and DAT_00677d10. Static retail evidence only; exact source identity, full table semantics, runtime remap behavior, and rebuild parity remain unproven.",
                tags("controls", "options-entry", "signature-hardened"),
                new String[] {"OptionsEntries__InitDefaultDualBindingsTable"},
                new ParameterImpl[] {}),

            new Spec("0x00453970", "CControllerDefinition__InitDefaults", "__thiscall", voidType,
                "Signature/comment hardening: initializes the CControllerDefinition helper defaults, installs vtable 0x005db404, sets visible/remap fields around +0x04..+0x20, and clears the owned surface pointer at +0x2c. Static retail evidence only; concrete class layout, exact source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__InitDefaults"},
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x004539b0", "CControllerDefinition__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Signature/comment hardening: scalar deleting destructor wrapper calls CControllerDefinition__dtor and conditionally frees the object according to flags. Static retail evidence only; allocator ownership, exact source identity, runtime lifecycle behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__scalar_deleting_dtor"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x004539d0", "CControllerDefinition__dtor", "__thiscall", voidType,
                "Signature/comment hardening: destructor resets vtable 0x005db404, gates key-sink cleanup through g_ControlRemapActive, releases the owned +0x2c surface through a CHud counter helper, then restores the CMenuItem vtable. Static retail evidence only; concrete field ownership, exact source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__dtor"},
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00453ac0", "SharedVFunc__NoOp_Ret0C", "__stdcall", voidType,
                "Owner correction: zero-body shared vtable target consists of RET 0x0c and is referenced by CControllerDefinition plus unrelated script/datatype tables, so the older CControllerDefinition-specific label was too narrow. Static retail evidence only; exact semantic contract, callers' type systems, runtime behavior, and rebuild parity remain unproven.",
                tags("shared-noop", "owner-corrected", "signature-hardened"),
                new String[] {"CControllerDefinition__VFunc_01_00453ac0", "SharedVFunc__NoOp_Ret0C"},
                new ParameterImpl[] {param("unused0", intType), param("unused1", intType), param("unused2", intType)}),

            new Spec("0x00453ad0", "CControllerDefinition__RenderBindingsAndPollRemapInput", "__thiscall", voidType,
                "Name/signature hardening: vtable slot 4 renders three binding-list columns through ControlsUI__RenderBindingsList, lazily loads the frontend arrow texture, handles page-arrow click rectangles, and polls keyboard/controller state for remap capture. Static retail evidence only; exact source method name, concrete UI layout, runtime input behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "remap", "name-corrected", "signature-hardened"),
                new String[] {"CControllerDefinition__VFunc_04_00453ad0", "CControllerDefinition__RenderBindingsAndPollRemapInput"},
                new ParameterImpl[] {param("this", voidPtr), param("x", floatType), param("y", floatType), param("interactive", intType)}),

            new Spec("0x00455010", "ControlsUI__RenderBindingsList", "__thiscall", voidType,
                "Signature hardening: RET 0x10 confirms four stack arguments after this; the body renders one control-binding column, derives action_code as rowIndex + 0x37, resolves entries through Controls__DispatchRemap and OptionsEntries__FindById, and calls Controls__BeginRemapCapture for interactive remap clicks. Static retail evidence only; exact row semantics, runtime input behavior, and rebuild parity remain unproven.",
                tags("controls", "control-bindings", "remap", "signature-hardened"),
                new String[] {"ControlsUI__RenderBindingsList"},
                new ParameterImpl[] {param("this", voidPtr), param("columnIndex", intType), param("unusedRowOffset", floatType), param("listY", floatType), param("interactive", intType)}),

            new Spec("0x00456080", "Controls__BeginRemapCapture", "__fastcall", voidType,
                "Signature hardening: begins control remap capture for the selected row/slot, toggles invert-y fields for action codes 0x38/0x39, otherwise clears g_ControlRemapActive and g_ControlRemapArmed, snapshots controller baselines, records g_ControlRemapSlotIndex/action code, and installs the key-sink callback. Static retail evidence only; exact source identity, runtime input behavior, and rebuild parity remain unproven.",
                tags("controls", "remap", "signature-hardened"),
                new String[] {"Controls__BeginRemapCapture"},
                new ParameterImpl[] {param("controllerDefinition", voidPtr)}),

            new Spec("0x004565d0", "OptionsEntries__SetBindingSlot", "__cdecl", voidType,
                "Signature hardening: callback helper finds an options entry by entryId, writes the selected slotIndex triple, and stores scan/vk into the low/high 16-bit halves of the packed key word. Static retail evidence only; exact callback ownership, runtime remap behavior, and rebuild parity remain unproven.",
                tags("controls", "options-entry", "remap", "signature-hardened"),
                new String[] {"OptionsEntries__SetBindingSlot"},
                new ParameterImpl[] {param("slotIndex", intType), param("entryId", intType), param("field0", intType), param("deviceCode", intType), param("scan", shortType), param("vk", shortType)}),

            new Spec("0x00456610", "CControllerDefinition__GetWidth", "__thiscall", intType,
                "Name/signature hardening: CControllerDefinition vtable slot 5 returns the fixed width 0x190 for this menu item. Static retail evidence only; exact frontend layout contract, runtime UI behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__VFunc_05_00456610", "CControllerDefinition__GetWidth"},
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00456620", "CControllerDefinition__GetRowHeight", "__thiscall", intType,
                "Name/signature hardening: CControllerDefinition vtable slot 6 returns fixed value 0xe6, matching the row-height/height style slot in the surrounding MenuItem vtable family. Static retail evidence only; exact frontend layout contract, runtime UI behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__VFunc_06_00456620", "CControllerDefinition__GetRowHeight"},
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00456630", "CControllerDefinition__GetFlag1C", "__thiscall", byteType,
                "Name/signature hardening: CControllerDefinition vtable slot 8 reads the byte flag at this+0x1c and returns it. Static retail evidence only; exact flag semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__VFunc_08_00456630", "CControllerDefinition__GetFlag1C"},
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00456640", "CControllerDefinition__ClearFlag1C", "__thiscall", voidType,
                "Name/signature hardening: CControllerDefinition vtable slot 12 clears the byte flag at this+0x1c. Static retail evidence only; exact flag semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("controls", "controller-definition", "signature-hardened"),
                new String[] {"CControllerDefinition__VFunc_12_00456640", "CControllerDefinition__ClearFlag1C"},
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
            throw new IllegalStateException("Frontend/control signature tranche failed for " + failed + " target(s)");
        }
    }
}
