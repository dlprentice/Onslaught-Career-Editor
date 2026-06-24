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

public class ApplyDestructableControllerSignatureTranche extends GhidraScript {
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

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
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
        Function fn = existingFunction(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + spec.address);
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
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = existingFunction(addr(spec.address));
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
            "destructable-controller-wave349",
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
            new Spec("0x004433f0", "CDestroyableCoreSegment__AreCoreChildrenDestroyed", "__fastcall", intType,
                "Core-segment helper reached from controller threshold/cascade paths: warns when the first core part has no children, walks the child CSPtrSet at this+0x24, and returns false when a child still reports the checked slot-0x14 state and has not set field +0x38. Corrects the older controller-owner label because callers pass the root/core segment pointer. Static retail evidence only; exact source identity, concrete class layout, runtime cascade behavior, and rebuild parity remain unproven.",
                tags("core-segment", "child-state", "name-correction"),
                new String[] {"CDestructableSegmentsController__AreCoreChildrenDestroyed", "CDestroyableCoreSegment__AreCoreChildrenDestroyed"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00443480", "CDestroyableCoreSegment__Init", "__thiscall", voidPtr,
                "Core/primary destroyable-segment initializer: delegates to CDestructableSegment__Init, clears extra core fields at +0x44/+0x48/+0x4c, stores the core component ordinal at +0x40, assigns vtable 0x005db06c, and returns this. Static retail evidence only; exact source identity, concrete class layout, runtime hierarchy behavior, and rebuild parity remain unproven.",
                tags("init", "core-segment", "name-correction"),
                new String[] {"CDestructableSegment__InitPrimary", "CDestroyableCoreSegment__Init"},
                new ParameterImpl[] {param("this", voidPtr), param("controller", voidPtr), param("segmentIndex", intType), param("parentSegment", voidPtr), param("segmentValue", floatType), param("coreComponentOrdinal", intType)}),
            new Spec("0x004434d0", "CDestroyableCoreSegment__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Scalar-deleting destructor wrapper for the core/primary destroyable segment: calls CDestroyableCoreSegment__dtor_base, frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, concrete class layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "core-segment", "vtable-slot", "name-correction"),
                new String[] {"CDestroyableCoreSegment__VFunc_01_004434d0", "CDestroyableCoreSegment__scalar_deleting_dtor"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004434f0", "CDestroyableCoreSegment__dtor_base", "__fastcall", voidType,
                "Destructor body for the core/primary destroyable segment: restores the base segment vtable, removes this from DAT_00855180, invokes deleting destructors for children in the this+0x24 list, clears that CSPtrSet, and chains to CMonitor__Shutdown. Static retail evidence only; exact source identity, concrete class layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "core-segment", "name-correction"),
                new String[] {"CDestroyableSegment__ctor_like_004434f0", "CDestroyableCoreSegment__dtor_base"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004435f0", "CDestroyableCoreSegment__VFunc_03_ApplyDamage", "__thiscall", voidType,
                "Core/primary segment damage-style vfunc slot 3: ignores first-core ordinal 1, subtracts damageAmount from field +0x0c while active, records the raw damage and DAT_00672fd0 in fields +0x18/+0x14, clamps to zero, and dispatches break/rubble slots when depleted and not already broken. The damageSource argument is part of the observed vfunc ABI but is not consumed in the current decompile. Static retail evidence only; exact source virtual name, concrete layout, runtime damage behavior, and rebuild parity remain unproven.",
                tags("damage", "core-segment", "vtable-slot", "name-correction"),
                new String[] {"CDestroyableCoreSegment__VFunc_03_004435f0", "CDestroyableCoreSegment__VFunc_03_ApplyDamage"},
                new ParameterImpl[] {param("this", voidPtr), param("damageAmount", floatType), param("damageSource", voidPtr)}),
            new Spec("0x00443780", "CDestroyableSwapSegment__VFunc_03_ApplyDamage", "__thiscall", voidType,
                "Swap-segment damage-style vfunc slot 3: samples slot 0x10 before and after applying damage, records raw damage/time in fields +0x18/+0x14, clamps field +0x0c to zero, dispatches swap/rubble and child-destruction side effects when the slot-0x10 state changes, scales field +0x34, and marks the controller/core state. Static retail evidence only; exact source virtual name, concrete layout, runtime swap behavior, and rebuild parity remain unproven.",
                tags("damage", "swap-segment", "vtable-slot", "name-correction"),
                new String[] {"CDestroyableSwapSegment__VFunc_03_00443780", "CDestroyableSwapSegment__VFunc_03_ApplyDamage"},
                new ParameterImpl[] {param("this", voidPtr), param("damageAmount", floatType), param("damageSource", voidPtr)}),
            new Spec("0x00443810", "CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak", "__fastcall", voidType,
                "Swap-segment vfunc slot 8 break handler: runs the swap/rubble slot once while field +0x44 is clear, sets that one-shot flag, then delegates to CDestroyableSegment__VFunc_08_HandleSegmentBreak. Static retail evidence only; exact source virtual name, concrete layout, runtime swap behavior, and rebuild parity remain unproven.",
                tags("break-handler", "swap-segment", "vtable-slot", "name-correction"),
                new String[] {"CDestroyableSwapSegment__VFunc_08_00443810", "CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004439c0", "CDestroyableSegment__SharedVFunc_08_HandleChildBreak", "__fastcall", voidType,
                "Shared vfunc slot 8 break handler used by the leaf/end segment vtables: optionally dispatches the swap/rubble slot when field +0x38 is clear and the controller/component count is positive, then delegates to the base segment break handler. Static retail evidence only; exact source virtual name, concrete owner class, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("break-handler", "shared-vfunc", "vtable-slot", "name-correction"),
                new String[] {"VFuncSlot_08_004439c0", "CDestroyableSegment__SharedVFunc_08_HandleChildBreak"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00443fc0", "CDestructableSegmentsController__Ctor", "__thiscall", voidPtr,
                "Controller constructor-like initializer: stores caller-provided values into fields +0x10/+0x14/+0x24/+0x28, clears segment array/root/counters/threshold state fields, sets field +0x00 to 1, and returns this. Static retail evidence only; exact source constructor identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("ctor", "controller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__Ctor"},
                new ParameterImpl[] {param("this", voidPtr), param("field10Value", voidPtr), param("field14Value", voidPtr), param("field24Value", voidPtr), param("field28Value", voidPtr)}),
            new Spec("0x00444000", "CDestructableSegmentsController__Dtor", "__fastcall", voidType,
                "Controller destructor helper: frees the owned segment-array pointer at this+0x04 and invokes the deleting destructor on the root segment pointer at this+0x0c when present. Static retail evidence only; exact source destructor identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("destructor", "controller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__Dtor"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00444030", "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold", "__thiscall", voidType,
                "Controller indexed damage path: resolves a tracked segment pointer by segmentIndex, dispatches its damage-style vfunc with damageAmount and damageSource, warns for missing mesh parts when the root still has children, triggers the owning unit callback when core children are destroyed or current subtree health falls below the cached threshold, and updates the one-shot threshold flag at +0x2c. Static retail evidence only; exact source identity, concrete layout, runtime damage behavior, and rebuild parity remain unproven.",
                tags("damage", "threshold", "controller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentIndex", intType), param("damageAmount", floatType), param("damageSource", voidPtr)}),
            new Spec("0x00444160", "CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold", "__fastcall", voidType,
                "Controller random-damage burst path: deduplicates non-null segment pointers into a temporary CSPtrSet, randomly applies a large damage value to segments whose slot-0x14 state exceeds 1, clears the temporary set, and reuses the same cached-health threshold update logic as the indexed damage path. Static retail evidence only; exact source identity, concrete layout, runtime random-damage behavior, and rebuild parity remain unproven.",
                tags("damage", "random-burst", "threshold", "controller"),
                new String[] {"CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004442d0", "CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex", "__thiscall", floatType,
                "Indexed segment getter for field +0x14: returns the tracked segment value when segmentIndex resolves, otherwise returns the observed fallback constant. Damage-style segment vfuncs write DAT_00672fd0 to this field, so this supersedes the older field-only label while keeping exact runtime/UI semantics unproven. Static retail evidence only; concrete layout and rebuild parity remain unproven.",
                tags("getter", "damage", "controller", "name-correction"),
                new String[] {"CDestructableSegmentsController__GetSegmentField14ByIndex", "CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentIndex", intType)}),
            new Spec("0x00444300", "CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex", "__thiscall", floatType,
                "Indexed segment getter for field +0x18: returns the tracked segment value when segmentIndex resolves, otherwise returns zero. Damage-style segment vfuncs write the raw damage amount to this field, so this supersedes the older field-only label while keeping exact runtime/UI semantics unproven. Static retail evidence only; concrete layout and rebuild parity remain unproven.",
                tags("getter", "damage", "controller", "name-correction"),
                new String[] {"CDestructableSegmentsController__GetSegmentField18ByIndex", "CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentIndex", intType)}),
            new Spec("0x00444330", "CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive", "__fastcall", floatType,
                "Controller health query: if any tracked segment is active, returns CDestroyableSegment__SumActiveValueRecursive for the root segment; otherwise returns zero. Static retail evidence only; exact health semantics, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("health-metric", "controller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00444370", "CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive", "__fastcall", floatType,
                "Controller health query: if any tracked segment is active, returns CDestructableSegment__GetTotalHealth for the root segment; otherwise returns zero. Static retail evidence only; exact health semantics, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("health-metric", "controller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004443b0", "CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive", "__fastcall", floatType,
                "Controller health query: if any tracked segment is active, returns the cached total-health field at this+0x18; otherwise returns zero. Static retail evidence only; exact health semantics, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("health-metric", "controller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004443f0", "CDestructableSegmentsController__TriggerCoreCascadeIfEligible", "__fastcall", voidType,
                "Controller cascade trigger: checks the root/core segment child-state helper, compares cached total health against the current active-value sum, and when eligible activates the root subtree, propagates a large child-damage value through the root segment, and sets the one-shot threshold flag at +0x2c. Renamed from the older threshold-exceeded label to avoid overclaiming the exact threshold direction. Static retail evidence only; runtime cascade behavior, concrete layout, exact source identity, and rebuild parity remain unproven.",
                tags("cascade", "threshold", "controller", "name-correction"),
                new String[] {"CDestructableSegmentsController__TriggerCascadeIfThresholdExceeded", "CDestructableSegmentsController__TriggerCoreCascadeIfEligible"},
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
            throw new IllegalStateException("Destructable controller tranche failed for " + failed + " target(s)");
        }
    }
}
