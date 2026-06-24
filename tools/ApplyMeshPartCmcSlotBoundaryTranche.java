//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMeshPartCmcSlotBoundaryTranche extends GhidraScript {
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

    private Function getOrCreate(Address address, String name, boolean dryRun) throws Exception {
        Function fn = existingFunction(address);
        if (fn != null) {
            return fn;
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + address);
        }
        return fn;
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
        Address address = addr(spec.address);
        Function fn = getOrCreate(address, spec.name, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
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

        Function readBack = existingFunction(address);
        if (readBack == null || !readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "meshpart-cmc-slot-wave357",
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
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00495770", "CMCComponent__VFunc_08_CheckOwnerRangeWindow", "__thiscall", boolType,
                "Recovered CMCComponent vtable slot 8 boundary: reads owner pointer through this+0x08, compares owner range/window floats at +0xe0/+0xe4 and +0xe8/+0xf0 against cached component floats at this+0x0c/+0x10, and returns a boolean. Static retail evidence only; exact source virtual name, concrete owner layout, runtime component behavior, and rebuild parity remain unproven.",
                tags("cmccomponent", "function-boundary", "vtable-slot", "range-window"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004959a0", "CMCComponent__VFunc_04_UpdateTurretBarrelTransform", "__thiscall", voidType,
                "Recovered CMCComponent vtable slot 4 boundary: handles turret/barrel MeshPart token paths, uses vector/matrix helper calls, writes transform/output-style arguments, and returns with RET 0x10. Static retail evidence only; exact source virtual name, concrete transform/output layout, runtime component behavior, and rebuild parity remain unproven.",
                tags("cmccomponent", "function-boundary", "vtable-slot", "turret-barrel"),
                new ParameterImpl[] {param("this", voidPtr), param("meshPart", voidPtr), param("heightAdjustOut", voidPtr), param("transformOut", voidPtr), param("reservedArg", intType)}),
            new Spec("0x00496100", "CMCDropship__VFunc_05_UpdateDoorAnimationValue", "__thiscall", voidType,
                "Recovered CMCDropship vtable slot 5 boundary: filters MeshPart names by the door token, selects dooropening or doorclosing animation rows based on owner state context, updates a door animation value output, caches owner state/time fields on this, and returns with RET 0x8. Static retail evidence only; exact source virtual name, concrete dropship/animation layout, runtime door behavior, and rebuild parity remain unproven.",
                tags("cmcdropship", "function-boundary", "vtable-slot", "door-animation"),
                new ParameterImpl[] {param("this", voidPtr), param("meshPart", voidPtr), param("doorAnimationValueOut", voidPtr)}),
            new Spec("0x00496200", "CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow", "__thiscall", boolType,
                "Recovered CMCDropship vtable slot 8 boundary: reads owner pointer through this+0x08, compares cached state at this+0x0c with owner state +0x27c, compares owner time/window fields +0x2a4/+0x2a8 against this+0x10, and returns a boolean. Static retail evidence only; exact source virtual name, concrete dropship layout, runtime door/state behavior, and rebuild parity remain unproven.",
                tags("cmcdropship", "function-boundary", "vtable-slot", "state-time-window"),
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
            throw new IllegalStateException("MeshPart/CMC slot boundary tranche failed for " + failed + " target(s)");
        }
    }
}
