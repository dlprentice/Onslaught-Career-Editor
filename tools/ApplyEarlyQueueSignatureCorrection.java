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

public class ApplyEarlyQueueSignatureCorrection extends GhidraScript {
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
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00402dd0", "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight", "__thiscall", intType,
                "Signature/comment correction: ECX-backed object pointer samples eight attached-bounds extent corners against CStaticShadows__SampleShadowHeightBilinear and a height callback at vfunc +0xc0. Exact owner/source identity, structure types, local names, runtime shadow behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00403ff0", "CDXLandscape__DestroyResourceDescriptorArray_Thunk", "__thiscall", voidType,
                "Signature/comment correction: resource-descriptor array destroy thunk advances this+8, passes element size 0x41c/count 1, and dispatches CResourceDescriptor__dtor through the array callback. Destructor/unwind context, exact render-path ownership, source identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00404dd0", "CBattleEngine__Init", "__thiscall", voidType,
                "Signature/comment correction: CBattleEngine init takes a CBattleEngineInitThing-like stack argument (ret 0x4), resolves sound/effect resources, constructs walker/jet parts, initializes reader/state fields, and zeros stealth-adjacent fields +0x5d4/+0x5d8/+0x5dc. Exact layouts/source identity, weapon_fire_breaks_stealth, runtime init behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00405930", "CControllerDefinition__VFunc_03_00405930", "__thiscall", intType,
                "Signature/comment correction: recovered CControllerDefinition vtable slot returns 0 and has no observed body-side state change in the current decompile. Exact virtual contract, owner table coverage, runtime control-remap behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004059a0", "CCylinder__VFunc_01_004059a0", "__thiscall", intType,
                "Signature/comment correction: ret 0x10 wrapper forwards four stack arguments plus this into dispatchObject vfunc +0x8. Exact CCylinder virtual contract, argument semantics, source identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("forwardedA", voidPtr),
                    param("forwardedB", voidPtr),
                    param("dispatchObject", voidPtr),
                    param("forwardedC", voidPtr)
                }),
            new Spec("0x00405d80", "CParticleManager__RemoveFromGlobalList_Thunk", "__fastcall", voidType,
                "Signature/comment correction: this saved entry is a jump thunk to 0x004cb050, the real CParticleManager__RemoveFromGlobalList body. The target signature is now tracked separately; exact source identity, runtime particle behavior, and rebuild parity remain unproven.",
                new String[] {"CParticleManager__RemoveFromGlobalList"},
                new ParameterImpl[] {param("node", voidPtr)}),
            new Spec("0x00405db0", "VFuncSlot_12_00405db0", "__thiscall", voidType,
                "Signature/comment correction: no-op vtable slot returns with ret 0x8, preserving two stack arguments and no observed body-side state change. Exact owner table, argument semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("arg1", voidPtr), param("arg2", voidPtr)}),
            new Spec("0x00406da0", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "__thiscall", voidPtr,
                "Signature/comment correction: ret 0x18 target-selection helper scans global target set DAT_008550d0, filters weapon-mode/profile/mask/range/forward-facing candidates, and excludes entries already present in BattleEngine tracked set +0x294. The fourth copied vector lane is retained as originW because callers pass a 16-byte vector; exact structure types, source identity, weapon_fire_breaks_stealth, runtime target choice, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("profile", voidPtr),
                    param("originX", floatType),
                    param("originY", floatType),
                    param("originZ", floatType),
                    param("originW", floatType),
                    param("rangeScale", floatType)
                }),
            new Spec("0x004cb050", "CParticleManager__RemoveFromGlobalList", "__fastcall", voidType,
                "Signature/comment correction: removes node from the global particle-manager linked list rooted at 0x0082b3e8 by updating the head or predecessor link. Exact source identity, node structure, runtime particle behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("node", voidPtr)})
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
