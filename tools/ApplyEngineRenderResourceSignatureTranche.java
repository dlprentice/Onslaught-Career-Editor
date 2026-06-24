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

public class ApplyEngineRenderResourceSignatureTranche extends GhidraScript {
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
            "engine-render-resource-wave361",
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

        Spec[] specs = new Spec[] {
            new Spec("0x0044a1c0", "CEngine__UpdatePos", "__thiscall", voidType,
                "Saved signature/tag hardening: CEngine UpdatePos uses one stack argument (RET 0x4), checks the render-landscape flag at +0x4a8, loads the landscape pointer at +0x10 and current viewpoint at +0x4ac, and forwards camera/viewpoint context to CDXLandscape__SetTileData. Static retail evidence only; exact source identity, concrete layout, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("engine", "landscape", "render-position"),
                new ParameterImpl[] {param("this", voidPtr), param("camera", voidPtr)}),
            new Spec("0x0044a1f0", "CEngine__LoadMixers", "__thiscall", voidType,
                "Saved owner/signature correction: CEngine LoadMixers uses one stack argument (RET 0x4), loads the map texture array from +0x49c, calls CMapTex__LoadMixerTextureSet with set/6/0x100, and builds copied mixer levels through the 0x4c..0x1c8 map-texture offsets. Static retail evidence only; exact source identity, concrete layout, runtime texture/resource loading, and rebuild parity remain unproven.",
                new String[] {"CResourceAccumulator__LoadAndCopyMixerTextureSet"},
                tags("engine", "map-textures", "resource-load"),
                new ParameterImpl[] {param("this", voidPtr), param("set", intType)}),
            new Spec("0x0044a2a0", "CEngine__SetKempyCube", "__thiscall", voidType,
                "Saved owner/signature correction: CEngine SetKempyCube uses one stack argument (RET 0x4), loads the KempyCube-style engine field at +0x498, and forwards number to the current Ghidra CDXEngine__InitKempyCubeResources target/KempyCube change context. Static retail evidence only; exact source identity, concrete layout, runtime resource selection, and rebuild parity remain unproven.",
                new String[] {"CResourceAccumulator__InitKempyCubeResources"},
                tags("engine", "kempy-cube", "resource-select"),
                new ParameterImpl[] {param("this", voidPtr), param("number", intType)}),
            new Spec("0x0044a2c0", "CEngine__SetWater", "__thiscall", voidType,
                "Saved owner/signature correction: CEngine SetWater uses one stack argument (RET 0x4), loads the water/render field at +0x14, and forwards number to CWaterRenderSystem__ReloadTextures. Static retail evidence only; exact source identity, concrete layout, runtime water resource selection, and rebuild parity remain unproven.",
                new String[] {"CResourceAccumulator__ReloadWaterRenderTextures"},
                tags("engine", "water", "resource-select"),
                new ParameterImpl[] {param("this", voidPtr), param("number", intType)})
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
