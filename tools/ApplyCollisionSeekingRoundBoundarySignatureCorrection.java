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

public class ApplyCollisionSeekingRoundBoundarySignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.parameters = parameters;
        }
    }

    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
        }

        if (needsRename) {
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
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00425a10", "CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags", "__thiscall", boolType,
                "Signature/name/comment correction: infantry-bloke collision-seeking filter helper. It checks the tracked thing flags, asks CBattleEngine__IsWeaponModeCompatibleWithMountState for mount-state compatibility when the special flag context is present, and otherwise falls back to CCollisionSeekingRound__CheckCollisionFlags. Runtime collision behavior, exact class layout, source identity, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingInfantryBloke__VFunc_08_00425a10"},
                new ParameterImpl[] {param("this", voidPtr), param("candidateRound", voidPtr)}),
            new Spec("0x00425b50", "CCollisionSeekingRound__InitCollisionLineAndSound", "__thiscall", voidType,
                "Recovered function-boundary/signature/comment correction: CollisionSeekingRound vtable slot initializes or replaces the collision-line helper, allocates a CLine-style helper from CollisionSeekingRound.cpp line 0x1b, calls CCollisionSeekingRound__InitWithSound, and derives the radius/distance field from the owning thing. Runtime projectile behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_00_00425b50"},
                new ParameterImpl[] {param("this", voidPtr), param("roundConfig", voidPtr)}),
            new Spec("0x00425c60", "CCollisionSeekingRound__FilterCollisionCandidateByTrajectory", "__thiscall", boolType,
                "Recovered function-boundary/signature/comment correction: collision candidate filter that first applies CCollisionSeekingRound__CheckCollisionFlags, rejects same-owner context, checks target/weapon state flags, samples targeting world position, and rejects trajectory candidates outside the computed range test. Runtime collision behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_14_00425c60"},
                new ParameterImpl[] {param("this", voidPtr), param("candidateRound", voidPtr)}),
            new Spec("0x00425e30", "CCollisionSeekingRound__UpdatePrimarySeekerLeadVector", "__fastcall", voidPtr,
                "Recovered function-boundary/signature/comment correction: updates the primary seeker line/vector record from the owning thing target position and current position; when +0x38 is positive it normalizes and scales a lead vector by that distance, otherwise it writes a direct target delta and zero velocity. Runtime seeker behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_10_00425e30"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00426150", "CCollisionSeekingRound__Init", "__thiscall", voidType,
                "Signature/comment correction: initializes owner/config flags, creates or adopts the primary CLine-style seeker, writes its owner-relative offset from CUnitAI__GetWorldPositionForTargeting, and conditionally creates a secondary CMeshCollisionVolume-style seeker from collisionseekingthing.cpp line 0x39. Runtime projectile behavior, exact source identity, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("roundConfig", voidPtr)}),
            new Spec("0x00426300", "CMeshCollisionVolume__ScalarDeletingDestructor_00426300", "__thiscall", voidPtr,
                "Signature/name/comment correction: scalar-deleting destructor wrapper for the CMeshCollisionVolume-style helper vtable; it calls the local CMeshCollisionVolume destructor body and frees the object when the delete flag is set. Runtime collision-volume behavior, exact helper subtype, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CMeshCollisionVolume__VFunc_00_00426300"},
                new ParameterImpl[] {param("this", voidPtr), param("deleteFlags", intType)}),
            new Spec("0x00426340", "CLine__ScalarDeletingDestructor_00426340", "__thiscall", voidPtr,
                "Signature/name/comment correction: scalar-deleting destructor wrapper for the CLine-style collision helper vtable used by CollisionSeekingRound, BattleEngine helper lines, and related trace helpers; it resets the base vtable and frees the helper when the delete flag is set. Runtime line-helper behavior, exact helper subtype, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_00_00426340"},
                new ParameterImpl[] {param("this", voidPtr), param("deleteFlags", intType)}),
            new Spec("0x00426360", "CLine__SetBaseVtable_00426360", "__fastcall", voidType,
                "Signature/name/comment correction: tiny CLine-style helper vtable reset used by the scalar-deleting destructor and unwind thunks; xrefs are broader than CollisionSeekingRound, so the previous CollisionSeekingRound-specific name was too narrow. Runtime line-helper behavior, exact helper subtype, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__SetVtable"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00426370", "CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset", "__thiscall", voidType,
                "Recovered function-boundary/signature/comment correction: replaces the primary seeker pointer, deletes the prior helper when present, samples the owning thing target position, and refreshes the seeker owner-relative offset fields. Runtime seeker behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_18_00426370"},
                new ParameterImpl[] {param("this", voidPtr), param("newSeeker", voidPtr)}),
            new Spec("0x004263f0", "CCollisionSeekingRound__Destructor", "__fastcall", voidType,
                "Signature/comment correction: CollisionSeekingRound destructor body resets the vtable, deletes primary and secondary helper pointers, and then calls CMonitor__Shutdown. Runtime destruction behavior, exact class layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00426460", "CCollisionSeekingRound__ScalarDeletingDestructor", "__thiscall", voidPtr,
                "Signature/comment correction: scalar-deleting destructor wrapper for CCollisionSeekingRound; it calls CCollisionSeekingRound__Destructor and frees the object when the delete flag is set. Runtime destruction behavior, exact class layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("deleteFlags", intType)}),
            new Spec("0x00426480", "CCollisionSeekingRound__SetCollisionMask", "__thiscall", voidType,
                "Signature/comment correction: writes the collision mask at +0x10 and marks the explicit-mask flag at +0x0c bit 0x100. Runtime collision filtering behavior, exact class layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("collisionMask", intType)}),
            new Spec("0x004264a0", "CCollisionSeekingRound__ResolveRoundCollisionResponse", "__thiscall", voidType,
                "Recovered function-boundary/signature/comment correction: peer collision response helper that gates on the delayed-ready flag 0x400, owner/self filters, thing flags, collision-priority bits, CLine/CMeshCollisionVolume helper selection, and final response callbacks on both participating things. Runtime collision response behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_0C_004264a0"},
                new ParameterImpl[] {param("this", voidPtr), param("otherRound", voidPtr)}),
            new Spec("0x00426900", "CCollisionSeekingRound__CheckCollisionFlags", "__thiscall", boolType,
                "Signature/comment correction: checks whether the candidate owner's thing flags at +0x34 do not overlap this round collision mask at +0x10. Runtime collision filtering behavior, exact class layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("candidateRound", voidPtr)}),
            new Spec("0x00426920", "CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance", "__thiscall", intType,
                "Recovered function-boundary/signature/comment correction: computes a Chebyshev-style distance between this round map/who cell coordinates and packed candidate coordinates, scaling either side by level/depth until they are comparable. Runtime map collision behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_1C_00426920"},
                new ParameterImpl[] {param("this", voidPtr), param("packedCell", voidPtr)}),
            new Spec("0x004269b0", "CCollisionSeekingRound__InitWithSound", "__thiscall", voidType,
                "Signature/comment correction: CCollisionSeekingRound__InitWithSound wraps CCollisionSeekingRound__Init, clears the delayed-ready bit while scheduling a 3000ms EVENT_MANAGER event when sound/config context is present, then scans neighbor sectors for immediate collision dispatch. Runtime sound/collision timing, exact class layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("roundConfig", voidPtr)}),
            new Spec("0x00426a00", "CCollisionSeekingRound__ProcessMapWhoCollisionSweep", "__thiscall", voidType,
                "Recovered function-boundary/signature/comment correction: thin vtable slot that forwards this+0x24 and two sweep arguments to CHLCollisionDetector__ProcessMapWhoCollisionSweep. Runtime collision sweep behavior, exact slot source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__VFunc_08_00426a00"},
                new ParameterImpl[] {param("this", voidPtr), param("startOrContext", voidPtr), param("endOrContext", voidPtr)}),
            new Spec("0x00426a20", "CCollisionSeekingRound__MarkDelayedCollisionReady", "__thiscall", voidType,
                "Recovered function-boundary/signature/comment correction: event callback that sets collision flag 0x400 when the event timestamp/code at +0x04 equals 3000ms, matching the CCollisionSeekingRound__InitWithSound scheduling context. Runtime event timing, exact callback source name, concrete layouts, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__DelayedCollisionReadyEvent_00426a20"},
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)}),
            new Spec("0x00426a40", "CCollisionSeekingRound__CreateEffect", "__thiscall", voidType,
                "Signature/comment correction: CCollisionSeekingRound__CreateEffect initializes a CollisionSeekingRound effect from round config, builds a CLine-style trace helper from the secondary seeker state, traces for a best target hit, dispatches the impact callback when a collision component is found, and releases the helper. Runtime visual/effect behavior, exact class layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("roundConfig", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
