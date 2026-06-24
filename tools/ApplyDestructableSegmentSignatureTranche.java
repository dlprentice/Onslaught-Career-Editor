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

public class ApplyDestructableSegmentSignatureTranche extends GhidraScript {
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
            "destructable-segment-wave348",
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
            new Spec("0x004425a0", "CDestructableSegment__Init", "__thiscall", voidPtr,
                "Base destructable-segment initializer: stores controller, mesh/component index, parent segment, segment value, default vector/value fields, active flag, child CSPtrSet, base vtable 0x005db02c, and global segment monitor membership at DAT_00855180. Static retail evidence only; exact source identity, concrete class layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("init", "base-segment"),
                new String[] {"CDestructableSegment__Init"},
                new ParameterImpl[] {param("this", voidPtr), param("controller", voidPtr), param("segmentIndex", intType), param("parentSegment", voidPtr), param("segmentValue", floatType)}),
            new Spec("0x00442640", "CDestroyableSegment__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Scalar-deleting destructor wrapper for the base destroyable segment: calls CDestroyableSegment__dtor_base, frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, concrete class layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "vtable-slot", "name-correction"),
                new String[] {"CDestroyableSegment__VFunc_01_00442640", "CDestroyableSegment__scalar_deleting_dtor"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00442660", "CDestroyableSegment__dtor_base", "__fastcall", voidType,
                "Destructor body for the base destroyable segment: restores the base vtable, removes this from DAT_00855180, walks child-list entries at this+0x24 and invokes their deleting destructors, clears the child CSPtrSet, and chains to CMonitor__Shutdown. Static retail evidence only; exact source identity, concrete class layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "name-correction"),
                new String[] {"CDestroyableSegment__ctor_like_00442660", "CDestroyableSegment__dtor_base"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442700", "CDestructableSegment__RegisterChild", "__thiscall", voidType,
                "Registers a child segment by adding childSegment to the parent segment child CSPtrSet at this+0x24. This corrects the earlier broad monitor-registration wording: global monitor membership is handled by CDestructableSegment__Init. Static retail evidence only; exact source identity, concrete class layout, runtime hierarchy behavior, and rebuild parity remain unproven.",
                tags("child-list", "name-correction"),
                new String[] {"CDestructableSegment__Register", "CDestructableSegment__RegisterChild"},
                new ParameterImpl[] {param("this", voidPtr), param("childSegment", voidPtr)}),
            new Spec("0x00442710", "CDestroyableSegment__SpawnConfiguredPickup", "__fastcall", intType,
                "Destroyable-segment helper that checks the owning unit/config through this+0x3c, creates a configured pickup when config+0xe8 is present, builds a stack init payload using the segment/controller context, and dispatches the pickup vfunc. This corrects the stale CExplosionInitThing ctor-like owner label; the body is still only statically characterized. Exact source identity, concrete init payload type, runtime pickup behavior, and rebuild parity remain unproven.",
                tags("pickup", "name-correction"),
                new String[] {"CExplosionInitThing__ctor_like_00442710", "CDestroyableSegment__SpawnConfiguredPickup"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442890", "CDestroyableSegment__SumActiveValueRecursive", "__thiscall", floatType,
                "Recursively sums active, not-destroyed segment values using this+0x10 when field +0x0c is not the sentinel, then walks the child list at this+0x24 and adds child sums. Static retail evidence only; exact source identity, concrete value semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("recursive-sum", "health-metric"),
                new String[] {"CDestroyableSegment__SumActiveValueRecursive"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442900", "CDestructableSegment__GetTotalHealth", "__fastcall", floatType,
                "Recursively sums total active, not-destroyed segment health/value using this+0x0c, then walks child segments through the child list at this+0x24. Used by controller initialization/root health queries. Static retail evidence only; exact source identity, concrete health semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("recursive-sum", "health-metric"),
                new String[] {"CDestructableSegment__GetTotalHealth"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004429a0", "CDestructableSegment__DispatchChildDestructionEvents", "__fastcall", voidType,
                "Walks child segments at this+0x24 and either dispatches the child break vfunc immediately or schedules event 3000 through CEventManager__AddEvent_AtTime with randomized delay/jitter based on the current segment state. Static retail evidence only; exact source identity, event payload layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("child-events", "event-3000"),
                new String[] {"CDestructableSegment__DispatchChildDestructionEvents"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442a80", "CDestructableSegment__SetSubtreeActiveFlagRecursive", "__fastcall", voidType,
                "Recursively sets the active flag at this+0x1c for this segment and every child segment reachable through the child list at this+0x24. Static retail evidence only; exact source identity, concrete layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("recursive", "active-flag"),
                new String[] {"CDestructableSegment__SetSubtreeActiveFlagRecursive"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442ac0", "CDestructableSegment__PropagateDamageToChildren", "__thiscall", voidType,
                "Walks child segments at this+0x24 and invokes each child damage-style vfunc at slot +0x0c with damageArg plus the owning controller/unit context from this+0x3c. The second stack argument is preserved as part of the observed ABI but is not consumed in the current decompile. Static retail evidence only; exact source identity, concrete argument semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("child-damage", "vtable-slot"),
                new String[] {"CDestructableSegment__PropagateDamageToChildren"},
                new ParameterImpl[] {param("this", voidPtr), param("damageArg", intType), param("unusedArg", intType)}),
            new Spec("0x00442b20", "CDestroyableSegment__VFunc_08_HandleSegmentBreak", "__fastcall", voidType,
                "Destroyable-segment vfunc slot 8 break handler: marks the segment broken, clears field +0x0c, updates a controller flag, finalizes linked unit state for mesh-linked children, gathers/removes matching linked segment entries, and dispatches child destruction events. Static retail evidence only; exact source virtual name, concrete layouts, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("break-handler", "vtable-slot", "name-correction"),
                new String[] {"CDestroyableSegment__VFunc_08_00442b20", "CDestroyableSegment__VFunc_08_HandleSegmentBreak"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442f60", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects", "__fastcall", voidType,
                "Destroyable-segment vfunc slot 10 rubble/effects path: resolves Generic Mesh, derives a spawn count from this+0x34, builds interpolated pose/anchor data, creates particle effects, periodically applies landscape damage and configured pickup spawning, pushes transforms, assigns outward velocity, and warns when rubble mode data is missing. Static retail evidence only; exact source virtual name, concrete layouts, runtime rubble behavior, and rebuild parity remain unproven.",
                tags("rubble", "particle-effects", "vtable-slot", "name-correction"),
                new String[] {"VFuncSlot_10_00442f60", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects"},
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
            throw new IllegalStateException("Destructable segment tranche failed for " + failed + " target(s)");
        }
    }
}
