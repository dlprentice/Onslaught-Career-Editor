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

public class ApplyCockpitVolumeUnitAiSignatureCorrection extends GhidraScript {
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

        Spec[] specs = new Spec[] {
            new Spec("0x004244b0", "CCockpit__ctor", "__thiscall", voidPtr,
                "Signature/name/comment correction: CCockpit constructor-like body called from CBattleEngine__Init after OID allocation. It stores the owning battleEngine at +0x110, initializes cockpit matrices/state, resolves render animation data, schedules EVENT_MANAGER event 0x7d1, and returns this. Callsite read-back shows one explicit battleEngine stack argument; runtime behavior, exact CCockpit layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {"CCockpit__ctor_like_004244b0"},
                new ParameterImpl[] {param("this", voidPtr), param("battleEngine", voidPtr)}),
            new Spec("0x004247a0", "CGeneralVolume__InitRandomizedVelocityOffsets", "__thiscall", voidType,
                "Signature/comment correction: initializes randomized velocity offsets at +0x90/+0x94/+0x98/+0x9c, zeroes +0xa0 phase, and clamps offset components against the observed 0.01 range token. Callsite read-back shows one explicit scalar randomRange argument; runtime behavior, exact owner layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("randomRange", intType)}),
            new Spec("0x00424920", "CGeneralVolume__BeginFlyToWalkTransition", "__fastcall", voidType,
                "Signature/comment correction: begins the fly-to-walk cockpit/volume transition by finding the flytowalk animation, storing the animation index at +0x11c, initializing timing fields, and setting transition state +0x114 to the fly-to-walk state. CBattleEngine__Morph callsite read-back shows ECX-only object dispatch; runtime behavior, exact owner layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00424990", "CGeneralVolume__BeginWalkToFlyTransition", "__fastcall", voidType,
                "Signature/comment correction: begins the walk-to-fly cockpit/volume transition by finding the walktofly animation, storing the animation index at +0x11c, initializing timing fields, and setting transition state +0x114 to the walk-to-fly state. CBattleEngine__Morph callsite read-back shows ECX-only object dispatch; runtime behavior, exact owner layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00424a20", "CUnitAI__UpdateDeployAimAndScheduleEvent", "__fastcall", voidType,
                "Signature/comment correction: UnitAI deploy aim/update helper that snapshots previous transform data, chooses target tracking versus neutral decay based on linked unit state, applies damped randomized offsets, advances deploy animation phase, and schedules event 0x7d1. Runtime behavior, exact CUnitAI layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00424be0", "CUnitAI__AdvanceDeployAnimationPhase", "__fastcall", voidType,
                "Signature/comment correction: advances deploy animation phase using +0x120/+0x124/+0x128, checks transition state +0x114, switches to the follow-up animation when thresholds are reached, and clears the transition state. Runtime behavior, exact CUnitAI layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00424ca0", "CUnitAI__UpdateDeployTrackingTransformTowardTarget", "__fastcall", voidType,
                "Signature/comment correction: target tracking transform helper; copies the base matrix into +0x2c, samples linked-unit target data and terrain normal context, builds a target-facing orientation, and writes the tracking transform back into the UnitAI object. Runtime behavior, exact CUnitAI layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004250f0", "CUnitAI__DecayDeployTrackingTransformToNeutral", "__fastcall", voidType,
                "Signature/comment correction: neutral deploy tracking decay helper; copies the base matrix into +0x2c, damps rotation offsets at +0xa4/+0xa8 toward neutral, and rebuilds the orientation from linked-unit direction and current basis data. Runtime behavior, exact CUnitAI layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00425760", "Mat34__OrthonormalizeAxes", "__fastcall", voidType,
                "Signature/name/comment correction: generic matrix helper, not CUnitAI-specific. It normalizes the first two 3D axes, builds the third axis with a cross product, normalizes that axis, then recomputes the second axis for an orthonormal Mat34-style basis. Runtime behavior, exact matrix owner types, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__OrthonormalizeMat34Axes"},
                new ParameterImpl[] {param("mat34", voidPtr)})
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
