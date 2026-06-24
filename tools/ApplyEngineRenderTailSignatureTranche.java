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

public class ApplyEngineRenderTailSignatureTranche extends GhidraScript {
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
        sb.append(spec.returnType.getDisplayName()).append(" ");
        if (spec.callingConvention != null && !spec.callingConvention.isEmpty()) {
            sb.append(spec.callingConvention).append(" ");
        }
        sb.append(spec.name).append("(");
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
            "engine-render-tail-wave362",
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
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec("0x0044a2d0", "CEngine__SetupLights", "", voidType,
                "Saved owner/comment/tag correction: engine SetupLights-style body normalizes the MAP sun vector, calls the current Atmospherics notifier, updates light/view-vector matrix context, and fills global render-light matrices. Static retail evidence only; exact source identity, concrete light/render layouts, runtime lighting behavior, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__UpdateAtmosphericsAndLightMatrices"},
                tags("engine", "lighting", "render-state"),
                new ParameterImpl[] {}),
            new Spec("0x0044a5f0", "Vec3__AssignXYZ", "__thiscall", voidType,
                "Saved signature/comment/tag hardening: vector helper writes three stack float/dword arguments into ECX vector slots and returns with RET 0xc. Static retail evidence only; exact FVector layout, caller value semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("math", "vector"),
                new ParameterImpl[] {param("this", voidPtr), param("x", floatType), param("y", floatType), param("z", floatType)}),
            new Spec("0x0044a610", "CEngine__TrackBurstEventFromPreset", "__thiscall", voidType,
                "Saved signature/comment/tag hardening: CEngine burst tracker uses three stack arguments (RET 0xc), reads engine fields +0x470 and +0x18, and forwards context to CEngine__TrackBurstEventIfNearby. Static retail evidence only; exact burst argument semantics, runtime projectile behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("engine", "projectile-burst"),
                new ParameterImpl[] {param("this", voidPtr), param("burstArg0", intType), param("burstArg1", intType), param("burstArg2", intType)}),
            new Spec("0x0044a640", "CDXEngine__SetOverlaySlotVisibilityByPlayerView", "__thiscall", voidType,
                "Saved signature/comment/tag correction: CDXEngine overlay helper uses one stack argument (RET 0x4), reads the overlay/view object at this+0x18, and forwards playerView to CDXEngine__SetOverlaySlotsEnabledForActiveViews. Static retail evidence only; exact overlay layout, player-view semantics, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "overlay", "render-state"),
                new ParameterImpl[] {param("this", voidPtr), param("playerView", intType)}),
            new Spec("0x0044a650", "CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite", "", voidType,
                "Saved comment/tag hardening: render-state helper sets state/value pairs 0x1b=1, 0x13=5, 0x14=6, and 0xe=0 through RenderState_Set. Static retail evidence only; exact D3D state names, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "render-state", "alpha"),
                new ParameterImpl[] {}),
            new Spec("0x0044a690", "RenderState__Set0x89_Zero", "", voidType,
                "Saved comment/tag hardening: narrow render-state helper calls RenderState_Set with state 0x89 and value 0. Static retail evidence only; exact D3D state meaning, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("render-state"),
                new ParameterImpl[] {}),
            new Spec("0x0044a6b0", "CDXEngine__ApplyNavMapConsoleToggle_Thunk", "__thiscall", intType,
                "Saved signature/comment/tag hardening: navmap console-toggle thunk uses five stack arguments (RET 0x14), reads this+0x10, and forwards the arguments to CDXEngine__InvalidateLandscapeTilesAndPatchSlots. Static retail evidence only; exact argument semantics, runtime navmap behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "navmap", "console"),
                new ParameterImpl[] {param("this", voidPtr), param("arg0", intType), param("arg1", intType), param("arg2", intType), param("arg3", intType), param("arg4", intType)}),
            new Spec("0x0044a6e0", "CEngine__Deserialize", "__thiscall", voidType,
                "Saved owner/signature correction: engine Deserialize uses one stack chunkReader argument (RET 0x4), reads the ENGN/map-texture count through CChunkReader, deserializes map textures through the engine +0x49c map-texture array, then dispatches MAP deserialize/init context. Static retail evidence only; exact source identity, concrete layouts, runtime resource loading, and rebuild parity remain unproven.",
                new String[] {"CResourceAccumulator__DeserializeMapTexListAndLoadMap"},
                tags("engine", "resource-deserialize", "map-textures"),
                new ParameterImpl[] {param("this", voidPtr), param("chunkReader", voidPtr)})
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
