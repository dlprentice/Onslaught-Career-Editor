//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFeatureUnitAiFrontendSignatureTranche extends GhidraScript {
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
            "feature-unitai-frontend-wave368",
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x004480c0", "CUnitAI__CanContinueDoorWingTransition", "__fastcall", boolType,
                "Signature hardening: door/wing transition predicate returns true when +0x294 is set or when spawned children are not ready but a target from vfunc +0x144 passes ballistic arc fireability. Exact source identity, local types, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unitai", "transition-gate", "signature-hardened"),
                new String[] {"CUnitAI__CanContinueDoorWingTransition"},
                new ParameterImpl[] {param("unitAi", voidPtr)}),

            new Spec("0x0044ca30", "CFeature__Init", "__thiscall", voidType,
                "Name/signature correction: CFeature init body copies feature data from init+0x3bc, builds a resource descriptor, creates the owned resource object, calls CActor__Init, adds the feature to the occupancy grid, updates shadow context, and optionally plays a random sample. Exact source identity, concrete feature/init layout, local types, runtime behavior, and rebuild parity remain unproven.",
                tags("feature", "init", "name-corrected", "signature-hardened"),
                new String[] {"CFeature__VFunc_09_0044ca30", "CFeature__Init"},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),

            new Spec("0x0044cbe0", "CFeature__ShutdownAndRemoveFromWorld", "__fastcall", voidType,
                "Name/signature correction: feature shutdown/removal helper calls KillSamplesForThing for the feature, calls RemoveUnitFromOccupancyGrid, calls UpdateVisibility with a remove-style flag, and then dispatches the base cleanup slot. Exact source identity, destructor ownership, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("feature", "shutdown", "name-corrected", "signature-hardened"),
                new String[] {"CFeature__VFunc_02_0044cbe0", "CFeature__ShutdownAndRemoveFromWorld"},
                new ParameterImpl[] {param("feature", voidPtr)}),

            new Spec("0x0044cd20", "CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200", "__thiscall", voidType,
                "Signature hardening: RET 0x10 shows four stack dwords; the first stack argument is the delta subtracted from +0xe0 before optional vfunc +0xc8 dispatch and clamp to profile field +0x18. Exact metric semantics, unused argument purpose, source identity, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unitai", "engagement-metric", "signature-hardened"),
                new String[] {"CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200"},
                new ParameterImpl[] {param("this", voidPtr), param("delta", floatType), param("unused1", intType), param("unused2", intType), param("unused3", intType)}),

            new Spec("0x0044cee0", "CFeature__MaybeSpawnRandomPickupFromData", "__fastcall", voidType,
                "Name/signature correction: feature-adjacent randomized pickup helper gates on feature data at +0xe4, uses random thresholds and object transform context, calls CreatePickup, resolves a pickup type through DAT_008553f8, and dispatches the pickup init vfunc. The owner inferred from caller/feature fields remains less certain than the observed pickup-spawn behavior; exact source identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("feature", "pickup-spawn", "name-corrected", "signature-hardened"),
                new String[] {"CExplosionInitThing__ctor_like_0044cee0", "CFeature__MaybeSpawnRandomPickupFromData"},
                new ParameterImpl[] {param("feature", voidPtr)}),

            new Spec("0x0044d1f0", "CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4", "__fastcall", voidType,
                "Signature hardening: updates the CUnitAI +0xcc timestamp through CUnitAI__SetStateTimestampCCToNow and dispatches vfunc +0x38 when flag bit 4 is set at +0x2c. Exact source identity, concrete state semantics, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unitai", "state-dispatch", "signature-hardened"),
                new String[] {"CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4"},
                new ParameterImpl[] {param("unitAi", voidPtr)}),

            new Spec("0x0044d210", "CUnitAI__RenderWithStaticShadowVisibilityUpdate", "__thiscall", voidType,
                "Signature hardening: RET 0x4 shows one render_context stack argument; body updates static shadow visibility with flag 0 before forwarding to CThing__Render. Exact render pass semantics, source identity, local types, runtime behavior, and rebuild parity remain unproven.",
                tags("unitai", "render", "signature-hardened"),
                new String[] {"CUnitAI__RenderWithStaticShadowVisibilityUpdate"},
                new ParameterImpl[] {param("this", voidPtr), param("render_context", intType)}),

            new Spec("0x0044d6f0", "CFrontEnd__RenderAndProcessModalPanel", "__fastcall", voidType,
                "Signature hardening: frontend modal panel renderer/input helper gates on +0x1f8c, calls DrawPanel-style panel/box/text/bar drawing paths, processes modal type state at +0x1f98, and calls CFrontEnd__HandleModalPanelButton for selection/cancel actions. Exact widget layout, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("frontend", "modal-panel", "signature-hardened"),
                new String[] {"CFrontEnd__RenderAndProcessModalPanel"},
                new ParameterImpl[] {param("frontend", voidPtr)}),

            new Spec("0x0044dd60", "CFrontEnd__HandleModalPanelButton", "__thiscall", voidType,
                "Signature hardening: RET 0x8 shows button and context stack arguments; body handles modal button codes 0x2a/0x2b/0x2c, plays frontend sounds, updates +0x1fa0/+0x1fa4 result fields, and may switch page through +0x1fa8/+0x1fac. Exact context argument semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("frontend", "modal-panel", "button-handler", "signature-hardened"),
                new String[] {"CFrontEnd__HandleModalPanelButton"},
                new ParameterImpl[] {param("this", voidPtr), param("button", intType), param("context", intType)}),

            new Spec("0x0044dea0", "CFrontEnd__IsMouseInputReady", "__fastcall", boolType,
                "Signature hardening: mouse input ready predicate returns true when the frontend modal/input gate at +0x1f8c is active and modal/input type at +0x1f98 is nonzero. Exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("frontend", "mouse-input", "signature-hardened"),
                new String[] {"CFrontEnd__IsMouseInputReady"},
                new ParameterImpl[] {param("frontend", voidPtr)}),

            new Spec("0x0044e2c0", "CMonitor__CheckSVFAnimationAndAdvanceState", "__fastcall", intType,
                "Signature hardening: SVF animation gate helper resolves the SVF token through FindAnimationIndex, compares it to the current animation index from the linked object, and dispatches vfunc +0x38 when they match. Exact source identity, concrete monitor/object layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("monitor", "animation-gate", "signature-hardened"),
                new String[] {"CMonitor__CheckSVFAnimationAndAdvanceState"},
                new ParameterImpl[] {param("monitor", voidPtr)}),

            new Spec("0x0044e300", "PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300", "__fastcall", voidType,
                "Owner-neutral rename/signature correction: attached pickup-spawn helper gates on +0x164, resolves animation/frame transform context, samples an attached frame, creates a pickup through CreatePickup, resolves DAT_008553f8 type context, and dispatches the pickup init vfunc. Exact owner class, source identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("pickup-spawn", "owner-deferred", "name-corrected", "signature-hardened"),
                new String[] {"CExplosionInitThing__ctor_like_0044e300", "PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300"},
                new ParameterImpl[] {param("object", voidPtr)}),
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
            throw new IllegalStateException("Feature/unit-AI/frontend signature tranche failed for " + failed + " target(s)");
        }
    }
}
