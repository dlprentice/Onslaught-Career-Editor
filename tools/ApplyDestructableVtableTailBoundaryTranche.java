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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyDestructableVtableTailBoundaryTranche extends GhidraScript {
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

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address result = toAddr(addrText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
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

    private Function getOrCreate(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn != null) {
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected existing function name at " + spec.address + ": " + fn.getName());
            }
            return fn;
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
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
        Function fn = getOrCreate(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getOrCreate(spec, false);
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
            "destructable-vtable-tail-wave353",
            "destructable-segments",
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

        Spec[] specs = new Spec[] {
            new Spec("0x00442960", "CDestroyableSegment__VFunc_03_ApplyDamage", "__thiscall", voidType,
                "Recovered base vtable slot 3 damage-style body: subtracts damageAmount from field +0x0c while active, records last damage amount/time in +0x18/+0x14, clamps below-zero health to zero, and preserves the sourceThing stack argument without observing source-facing side effects in this body. Static retail evidence only; exact source virtual name, concrete field semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "damage"),
                new ParameterImpl[] {param("this", voidPtr), param("damageAmount", floatType), param("sourceThing", voidPtr)}),
            new Spec("0x0055df1f", "CRT__Purecall_0055df1f", "__cdecl", voidType,
                "Recovered purecall-style CRT handler: pushes error code 0x19 and calls __amsg_exit before returning. This body is referenced by many vtable placeholder slots, including the base destroyable-segment slot 5. Static retail evidence only; exact CRT library provenance, all vtable owners, runtime callability, and rebuild parity remain unproven.",
                tags("function-boundary", "crt", "purecall"),
                new ParameterImpl[] {}),
            new Spec("0x00442b00", "CDestroyableSegment__VFunc_06_CheckParentBreakGate", "__fastcall", intType,
                "Recovered shared vtable slot 6 parent segment gate: follows the parent segment pointer at this+0x20, returns zero when no parent or parent field +0x38 is set, otherwise tail-jumps through the parent vtable slot +0x18. Static retail evidence only; exact source virtual name, parent-state semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "parent-gate"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004bfc60", "SharedVFunc__ReturnFloatZero_004bfc60", "__thiscall", floatType,
                "Recovered shared vtable target that returns float zero from the common 0.0 constant; broad unrelated vtable xrefs prevent a single owner-specific name. In the destroyable-segment vtables this fills non-core slot 7. Static retail evidence only; exact owner coverage, virtual contract, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "shared-vfunc", "return-float-zero"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00405ee0", "SharedVFunc__Return3_00405ee0", "__thiscall", intType,
                "Recovered shared vtable target that returns 3; in the destroyable-segment vtables it backs the end-segment type-style slot 5. Static retail evidence only; exact owner coverage, segment-type contract, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "shared-vfunc", "return-3"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004059c0", "SharedVFunc__Return2_004059c0", "__thiscall", intType,
                "Recovered shared vtable target that returns 2; in the destroyable-segment vtables it backs the leaf-segment type-style slot 5. Static retail evidence only; exact owner coverage, segment-type contract, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "shared-vfunc", "return-2"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004014a0", "SharedVFunc__Return1_004014a0", "__thiscall", intType,
                "Recovered shared vtable target that returns 1; in the destroyable-segment vtables it backs the standard-segment type-style slot 5. Broad unrelated vtable xrefs prevent a single owner-specific name. Static retail evidence only; exact owner coverage, segment-type contract, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "shared-vfunc", "return-1"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004436d0", "CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch", "__thiscall", voidType,
                "Recovered core vtable slot 0 event dispatcher: checks eventRecord code 3000/0x0bb8 and 3002/0x0bba, dispatches vtable slot +0x20 for event 3000, accumulates core fields +0x48/+0x44 for event 3002, and can schedule/dispatch break handling. Static retail evidence only; exact source virtual name, event payload layout, runtime cascade behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "event-3000", "event-3002"),
                new ParameterImpl[] {param("this", voidPtr), param("eventRecord", voidPtr)}),
            new Spec("0x004435c0", "CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate", "__fastcall", intType,
                "Recovered core vtable slot 6 parent gate: checks core field +0x4c, otherwise follows the parent segment at +0x20 and calls the parent vtable slot +0x18 when the parent is not already broken. Static retail evidence only; exact source virtual name, field semantics, runtime cascade behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "parent-gate", "core-segment"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004434c0", "CDestroyableCoreSegment__VFunc_07_GetCoreField48", "__fastcall", floatType,
                "Recovered core vtable slot 7 field reader: returns the float at this+0x48, which the current core event/break paths update as core cascade context. Static retail evidence only; exact source virtual name, field semantics, runtime cascade behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "core-field-reader"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00443660", "CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade", "__fastcall", voidType,
                "Recovered core vtable slot 8 break/cascade handler: if core health is depleted it can delegate to the base break handler, otherwise checks the parent gate, sets field +0x4c, captures a parent slot-7 float into +0x48, and schedules event 3002/0x0bba. Static retail evidence only; exact source virtual name, runtime cascade behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "core-break"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00443590", "CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields", "__thiscall", voidType,
                "Recovered core vtable slot 11 damage-scale helper: writes fields +0x0c/+0x10 from this+0x34, scaleFactor, and divisor, with a field +0x40 special case that clears both fields. Static retail evidence only; exact source virtual name, concrete field semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "damage-scale"),
                new ParameterImpl[] {param("this", voidPtr), param("scaleFactor", floatType), param("divisor", floatType)}),
            new Spec("0x00442d40", "CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09", "__fastcall", voidType,
                "Recovered shared vtable slot 9 update helper: when the segment is unbroken it resolves mesh/unit context, periodically builds transform data, calls CDestroyableSegment__SpawnConfiguredPickup, then walks child segments at +0x24 and dispatches child slot 9. Static retail evidence only; exact source virtual name, concrete update cadence, runtime pickup behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "pickup", "child-recursion"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442870", "CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields", "__thiscall", voidType,
                "Recovered shared vtable slot 11 damage-scale helper: writes fields +0x0c/+0x10 from this+0x34, scaleFactor, and divisor. Static retail evidence only; exact source virtual name, concrete field semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "damage-scale"),
                new ParameterImpl[] {param("this", voidPtr), param("scaleFactor", floatType), param("divisor", floatType)}),
            new Spec("0x00443ea0", "CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak", "__fastcall", voidType,
                "Recovered component vtable slot 8 break handler: marks field +0x38, clears field +0x0c, then calls the linked owner callback at +0xc8 through field +0x40 when present. Static retail evidence only; exact source virtual name, owner callback contract, runtime component behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "component-break"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00443a20", "CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects", "__fastcall", voidType,
                "Recovered end-segment vtable slot 10 effect helper: clears field +0x34, calls the base rubble/effects path, resolves Generic Mesh/unit context, and performs extra end-segment effect setup using fields including +0x40/+0x50. Static retail evidence only; exact source virtual name, complete effect semantics, runtime rubble behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "rubble", "end-segment"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004439f0", "CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields", "__thiscall", voidType,
                "Recovered end-segment vtable slot 11 damage-scale helper: checks controller component-count context at +0x20, can set field +0x0c to a small constant, otherwise writes fields +0x0c/+0x10 from this+0x34, scaleFactor, and divisor. Static retail evidence only; exact source virtual name, concrete field semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "vtable-slot", "damage-scale", "end-segment"),
                new ParameterImpl[] {param("this", voidPtr), param("scaleFactor", floatType), param("divisor", floatType)})
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
            throw new IllegalStateException("Destructable vtable tail boundary tranche failed for " + failed + " target(s)");
        }
    }
}
