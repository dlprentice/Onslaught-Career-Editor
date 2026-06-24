//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyUnitAiDiveDropshipSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
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

    private Function getFunctionOrThrow(String addressText) throws Exception {
        Address address = addr(addressText);
        Function fn = existingFunction(address);
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
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

    private void applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return;
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

        Function readBack = existingFunction(addr(spec.address));
        if (readBack == null || !readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unitai-dive-dropship-wave358",
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
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00445380", "CDiveBomberAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Saved scalar-deleting destructor correction: CDiveBomberAI wrapper calls CDiveBomberAI__dtor_base, conditionally frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CDiveBomberAI__VFunc_01_00445380"},
                tags("divebomber-ai", "destructor", "scalar-deleting-dtor"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004453a0", "CDiveBomberAI__dtor_base", "__fastcall", voidType,
                "Saved destructor-base correction: CDiveBomberAI resets to the monitor/base vtable, removes tracked set entries at +0x28/+0x24/+0x0c through CSPtrSet__Remove when present, then calls CMonitor__Shutdown. Static retail evidence only; exact source identity, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_004453a0"},
                tags("divebomber-ai", "destructor", "monitor-cleanup"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00445440", "CDiveBomberGuide__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Saved scalar-deleting destructor correction: CDiveBomberGuide wrapper calls CDiveBomberGuide__dtor_base, conditionally frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, concrete layout, runtime guide behavior, and rebuild parity remain unproven.",
                new String[] {"CDiveBomberGuide__VFunc_01_00445440"},
                tags("divebomber-guide", "destructor", "scalar-deleting-dtor"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00445460", "CDiveBomberGuide__dtor_base", "__fastcall", voidType,
                "Saved destructor-base correction: CDiveBomberGuide removes the +0x2c tracked set entry through CSPtrSet__Remove when present, then calls CMonitor__Shutdown. Static retail evidence only; exact source identity, concrete layout, runtime guide behavior, and rebuild parity remain unproven.",
                new String[] {"CDiveBomberGuide__DetachFromSetAndShutdownMonitor"},
                tags("divebomber-guide", "destructor", "monitor-cleanup"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00445570", "CUnitAI__PlayOpenAnimationIfState1Or3", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI door-wing helper checks state field +0x280 for states 1 or 3, sets it to 2, resolves the open animation, and dispatches animation vfunc +0xf0. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "animation"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x004455c0", "CUnitAI__PlayCloseAnimationIfState0Or2", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI door-wing helper checks state field +0x280 for states 0 or 2, sets it to 3, resolves the close animation, and dispatches animation vfunc +0xf0. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "animation"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00445610", "CUnitAI__AdvanceOpenCloseShootAnimationState", "__fastcall", intType,
                "Saved signature/comment correction: CUnitAI door-wing state helper compares current animation state, resolves shoot/close/open-style animation names, dispatches vfunc +0xf0, and updates state field +0x280. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "animation-state"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00445ad0", "CUnitAI__UpdateDoorWingEngagement_CloseRange", "__fastcall", doubleType,
                "Saved signature/comment correction: close-range door-wing engagement helper updates tracking flags +0x64/+0x68, randomizes threshold field +0x70, calls open/close animation helpers, and dispatches movement vfunc +0xf4. Static retail evidence only; exact source identity, concrete layout, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "engagement"),
                new ParameterImpl[] {param("doorWingAI", voidPtr)}),
            new Spec("0x00445f40", "CUnitAI__UpdateDoorWingEngagement_MidRange", "__fastcall", doubleType,
                "Saved signature/comment correction: mid-range door-wing engagement helper samples attached target/weapon context, toggles +0x6c, can dispatch movement vfunc +0xf4, and otherwise calls attached-node readiness helpers. Static retail evidence only; exact source identity, concrete layout, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "engagement"),
                new ParameterImpl[] {param("doorWingAI", voidPtr)}),
            new Spec("0x00446150", "CUnitAI__UpdateDoorWingEngagement_LongRange", "__fastcall", doubleType,
                "Saved signature/comment correction: long-range door-wing engagement helper evaluates target distance/state, toggles +0x68/+0x70, calls CUnitAI__EnterDoorWingOpenTrackingState or close-animation paths, and dispatches movement/attached-node helpers. Static retail evidence only; exact source identity, concrete layout, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "engagement"),
                new ParameterImpl[] {param("doorWingAI", voidPtr)}),
            new Spec("0x00446400", "CUnitAI__EnterDoorWingOpenTrackingState", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI door-wing helper enters open tracking by setting +0x68, randomizing threshold field +0x70, calling CUnitAI__PlayOpenAnimationIfState1Or3, and checking attached-node readiness. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "state-transition"),
                new ParameterImpl[] {param("doorWingAI", voidPtr)}),
            new Spec("0x00446d70", "CDropship__Init", "__thiscall", voidType,
                "Saved CDropship init signature/comment correction: initializes CAirUnit state, selects wingflat or doorclosed animation from terrain/shadow height context, creates CMCDropship and guide/Warspite-style component helpers, enumerates Thruster nodes, and resolves Thruster Dust Effect. Static retail evidence only; exact source identity, concrete layout, runtime dropship behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("dropship", "init", "thruster"),
                new ParameterImpl[] {param("this", voidPtr), param("initThing", voidPtr)}),
            new Spec("0x00447040", "CDropshipAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Saved scalar-deleting destructor correction: CDropshipAI wrapper calls CDropshipAI__dtor_base, conditionally frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CDropshipAI__VFunc_01_00447040"},
                tags("dropship-ai", "destructor", "scalar-deleting-dtor"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00447060", "CDropshipAI__dtor_base", "__fastcall", voidType,
                "Saved destructor-base correction: CDropshipAI resets to the monitor/base vtable, removes tracked set entries at +0x28/+0x24/+0x0c through CSPtrSet__Remove when present, then calls CMonitor__Shutdown. Static retail evidence only; exact source identity, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00447060"},
                tags("dropship-ai", "destructor", "monitor-cleanup"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00447100", "CDropship__dtor_base", "__fastcall", voidType,
                "Saved destructor-base correction: CDropship cleanup removes the unit from the occupancy grid through CWorld__RemoveUnitFromOccupancyGrid_Thunk, then delegates to CAirUnit__dtor_base. Static retail evidence only; exact source identity, concrete layout, runtime dropship cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CDropship__VFunc_02_00447100"},
                tags("dropship", "destructor", "airunit"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00447120", "CDropship__ProcessDoorThrustersAndChildUnits", "__fastcall", voidType,
                "Saved CDropship vtable/body correction: processes dooropening/doorclosing state, updates thruster/child-unit linked lists, calls motion/trail and shadow-height helpers, handles child-unit transform/effect state, and can spawn pickup effects. Static retail evidence only; exact source virtual name, concrete layout, runtime dropship behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_1c_00447120"},
                tags("dropship", "door-state", "thruster", "child-units"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00447a40", "CUnitAI__SetDoorWingState2AndClampYawDelta", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI door-wing helper validates cached anchor fields +0x290/+0x294, sets state +0x27c to 2, and clamps yaw delta into +0x2a0. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "state-transition"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00447ac0", "CUnitAI__PlayWingFoldedAnimationAndSetState3", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI door-wing helper sets state +0x27c to 3, clears +0x290, adds the unit back to occupancy/shadow state, resolves wingfolded animation, and dispatches vfunc +0xf0. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "animation"),
                new ParameterImpl[] {param("unitAI", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun);
                if (dryRun) {
                    skipped++;
                } else {
                    updated++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " updated=" + updated + " skipped=" + skipped + " failed=" + failed + " dry=" + dryRun);
        if (failed > 0) {
            throw new IllegalStateException("UnitAI/DiveBomber/Dropship signature tranche failed for " + failed + " target(s)");
        }
    }
}
