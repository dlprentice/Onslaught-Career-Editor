//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyOptionsPlatformInputCommentTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
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

    private Function getFunctionOrThrow(String addressText) throws Exception {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ");
        if (spec.callingConvention != null && !spec.callingConvention.isEmpty()) {
            sb.append(spec.callingConvention).append(" ");
        }
        sb.append(spec.name).append("(");
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

    private void applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return;
        }

        if (spec.callingConvention != null && !spec.callingConvention.isEmpty()) {
            fn.setCallingConvention(spec.callingConvention);
        }
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
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "options-platform-input-wave363",
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
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec("0x0042d260", "OptionsEntries__InitSingleBindingEntry", "__thiscall", voidPtr,
                "Saved comment/tag hardening: options-entry single-binding initializer uses ECX as the 0x20-byte entry pointer, returns this, writes the active byte, entry_id, and slot-0 device/scan/vk fields, clears slot-0 field0, and resets slot-1 defaults to 0xffffffff/0. Instruction read-back shows RET 0x14. Static retail evidence only; exact source identity, semantic action mapping, runtime remap behavior, and rebuild parity remain unproven.",
                tags("options-entry", "control-bindings"),
                new ParameterImpl[] {param("this", voidPtr), param("active", ghidra.program.model.data.ByteDataType.dataType), param("entry_id", intType), param("slot0_device_code", intType), param("slot0_scan", ghidra.program.model.data.ShortDataType.dataType), param("slot0_vk", ghidra.program.model.data.ShortDataType.dataType)}),
            new Spec("0x0042d2b0", "OptionsEntries__InitDualBindingEntry", "__thiscall", voidPtr,
                "Saved comment/tag hardening: options-entry dual-binding initializer uses ECX as the 0x20-byte entry pointer, returns this, writes the active byte, entry_id, slot-0 metadata, and slot-1 device/scan/vk metadata. Instruction read-back shows RET 0x20. Static retail evidence only; exact source identity, semantic action mapping, runtime remap behavior, and rebuild parity remain unproven.",
                tags("options-entry", "control-bindings"),
                new ParameterImpl[] {param("this", voidPtr), param("active", ghidra.program.model.data.ByteDataType.dataType), param("entry_id", intType), param("slot0_device_code", intType), param("slot0_scan", ghidra.program.model.data.ShortDataType.dataType), param("slot1_device_code", intType), param("slot1_scan", ghidra.program.model.data.ShortDataType.dataType), param("slot0_vk", ghidra.program.model.data.ShortDataType.dataType), param("slot1_vk", ghidra.program.model.data.ShortDataType.dataType)}),
            new Spec("0x0042d300", "OptionsEntries__InitSentinelEntry", "__thiscall", voidType,
                "Saved comment/tag hardening: options-entry sentinel helper uses ECX as the entry pointer, clears the active byte, and writes entry_id -1 at +0x04 to terminate table scans. Static retail evidence only; exact source identity, table lifetime, runtime remap behavior, and rebuild parity remain unproven.",
                tags("options-entry", "control-bindings", "sentinel"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042d310", "PlatformInput__InitMouse", "", intType,
                "Saved comment/tag hardening: DirectInput mouse device init path creates the mouse device from the global DirectInput interface, applies data format and cooperative level, zeroes mouse-state globals, resets profiler state, centers the cursor from window dimensions, and enables the global input state. Static retail evidence only; exact source identity, concrete global names/layouts, runtime input behavior, and rebuild parity remain unproven.",
                tags("platform-input", "directinput", "mouse-input"),
                new ParameterImpl[] {}),
            new Spec("0x0042d3b0", "PlatformInput__ShutdownMouse", "", intType,
                "Saved comment/tag hardening: DirectInput mouse shutdown path unacquires/releases the mouse device, clears the global mouse pointer, disables the global input state, snapshots cursor position through GetCursorPos when not in dev mode, and resets profiler state. Static retail evidence only; exact source identity, concrete global names/layouts, runtime input behavior, and rebuild parity remain unproven.",
                tags("platform-input", "directinput", "mouse-input"),
                new ParameterImpl[] {}),
            new Spec("0x0042d420", "PlatformInput__PollMouseMotion", "", intType,
                "Saved comment/tag hardening: mouse-motion poll path zeros the DIMOUSESTATE-style globals, reads device state, reacquires on 0x8007001e input-loss loops, then accumulates mouse deltas and wheel movement into cursor globals when not in dev mode. Static retail evidence only; exact source identity, concrete global names/layouts, runtime input behavior, and rebuild parity remain unproven.",
                tags("platform-input", "directinput", "mouse-input", "input-poll"),
                new ParameterImpl[] {}),
            new Spec("0x0042d4d0", "PlatformInput__PollMouseState", "", intType,
                "Saved comment/tag hardening: mouse-state poll path shares the DirectInput device-state/reacquire flow, updates cursor delta/wheel globals, and derives held/edge state for left/right/middle button transitions from 0x80, 0x8000, and 0x800000 masks. Static retail evidence only; exact source identity, concrete global names/layouts, runtime input behavior, and rebuild parity remain unproven.",
                tags("platform-input", "directinput", "mouse-input", "input-poll"),
                new ParameterImpl[] {})
        };

        int updated = 0;
        int skipped = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun);
                if (dryRun) {
                    skipped++;
                }
                else {
                    updated++;
                }
            }
            catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " updated=" + updated + " skipped=" + skipped + " failed=" + failed + " dry=" + dryRun);
        if (failed != 0) {
            throw new IllegalStateException("Failed targets: " + failed);
        }
    }
}
