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

public class ApplyEngineViewpointSignatureTranche extends GhidraScript {
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
            "engine-viewpoint-wave360",
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
            new Spec("0x00449820", "CEngine__ctor", "__fastcall", voidType,
                "Saved name/signature/comment correction: CEngine constructor installs the engine vtable, seeds near/far clip constants, clears owned resource pointers, sets the render-landscape flag at +0x4a8, and initializes viewpoint-adjacent fields. Static retail evidence only; exact source identity, concrete layout, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {"CEngine__ctor_like_00449820"},
                tags("engine", "constructor", "viewpoint"),
                new ParameterImpl[] {param("engine", voidPtr)}),
            new Spec("0x00449890", "CEngine__Shutdown", "__fastcall", voidType,
                "Saved name/signature/comment correction: CEngine shutdown releases screen effects, shadow/tree systems, gamut, landscape/camera/water/map texture/HUD texture resources, and trims VB/IB pool capacities. Static retail evidence only; exact source identity, concrete layout, runtime resource-lifetime behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_00_00449890"},
                tags("engine", "shutdown", "resource-lifecycle"),
                new ParameterImpl[] {param("engine", voidPtr)}),
            new Spec("0x004499d0", "CEngine__Init", "__fastcall", intType,
                "Saved signature/comment correction: CEngine init registers cg_renderlandscape/cg_drawpolybuckets and hit-effect cvars, allocates gamut/map texture/water/landscape/HUD/light resources, initializes screen effects/shadows/trees, and returns 1/0 for success. Static retail evidence only; exact source identity, concrete layout, runtime init behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("engine", "init", "resource-lifecycle"),
                new ParameterImpl[] {param("engine", voidPtr)}),
            new Spec("0x00449d50", "CEngine__InitResources", "__fastcall", voidType,
                "Saved name/signature/comment correction: CEngine resource init loads zoom textures, blob shadows, hilight.tga, hiteffect.tga, cloak.tga, and the landscape cloud-shadow texture. Static retail evidence only; exact source identity, texture ownership, runtime resource behavior, and rebuild parity remain unproven.",
                new String[] {"CEngine__VFunc_02_00449d50"},
                tags("engine", "init-resources", "textures"),
                new ParameterImpl[] {param("engine", voidPtr)}),
            new Spec("0x00449dc0", "CEngine__LoadAllNamedMeshes", "__thiscall", voidType,
                "Saved owner/signature correction: CEngine LoadAllNamedMeshes uses one stack argument (RET 0x4) dataFile, resets the global named-mesh count, reports Loading named meshes, reads mesh names from the buffer, reuses existing entries by case-insensitive compare, and calls CMesh__FindOrCreate for new entries. Static retail evidence only; exact source identity, global mesh-table layout, runtime loading behavior, and rebuild parity remain unproven.",
                new String[] {"CWorld__LoadNamedMeshCacheFromBuffer"},
                tags("engine", "named-meshes", "world-load"),
                new ParameterImpl[] {param("this", voidPtr), param("dataFile", voidPtr)}),
            new Spec("0x00449ef0", "CEngine__GetViewMatrixFromCamera", "__thiscall", voidType,
                "Saved owner/signature correction: CEngine GetViewMatrixFromCamera uses two stack arguments (RET 0x8), builds a pitch basis around the 1.570796-style constant, calls the camera orientation vfunc, transposes orientation terms, multiplies matrix bases, and copies twelve dwords to outViewMatrix. Static retail evidence only; exact source identity, matrix layout, runtime camera behavior, and rebuild parity remain unproven.",
                new String[] {"CFrontEnd__BuildCameraBasisFromYaw"},
                tags("engine", "viewpoint", "camera-matrix"),
                new ParameterImpl[] {param("this", voidPtr), param("camera", voidPtr), param("outViewMatrix", voidPtr)}),
            new Spec("0x0044a020", "CEngine__SetViewpoint", "__thiscall", voidType,
                "Saved signature/comment/tag hardening: CEngine SetViewpoint uses four stack arguments (RET 0x10), copies viewport state for the selected viewpoint, stores the player pointer, destroys any prior camera wrapper, allocates a CInterpolatedCamera, and stores the new camera wrapper. Static retail evidence only; exact source identity, concrete layout, runtime camera behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("engine", "viewpoint", "camera"),
                new ParameterImpl[] {param("this", voidPtr), param("viewpoint", intType), param("camera", voidPtr), param("viewport", voidPtr), param("player", voidPtr)}),
            new Spec("0x0044a0d0", "CEngine__SelectViewpoint", "__thiscall", voidType,
                "Saved signature/comment correction: CEngine SelectViewpoint uses one stack argument (RET 0x4), writes current viewpoint at +0x4ac, copies the selected viewport block into the current viewport fields, and calls D3DDevice__SetViewport. Static retail evidence only; exact source identity, concrete layout, runtime viewport behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("engine", "viewpoint", "viewport"),
                new ParameterImpl[] {param("this", voidPtr), param("viewpoint", intType)}),
            new Spec("0x0044a110", "CEngine__ResetPos", "__thiscall", voidType,
                "Saved owner/signature correction: CEngine ResetPos uses two stack arguments (RET 0x8), loads mLandscape from this+0x10, and forwards x/y reset coordinates to the landscape reset-position helper. Static retail evidence only; exact source identity, landscape layout, runtime position behavior, and rebuild parity remain unproven.",
                new String[] {"CCutscene__ResetLandscape"},
                tags("engine", "landscape", "position-reset"),
                new ParameterImpl[] {param("this", voidPtr), param("x", intType), param("y", intType)}),
            new Spec("0x0044a130", "CEngine__InitDamageSystem", "__fastcall", voidType,
                "Saved owner/signature correction: CEngine InitDamageSystem resets landscape damage tables, iterates world tree entries, applies tree-shadow landscape damage stamps, updates current damage tracking as a LockCurrentDamage-style step, and resets the landscape wrapper. Static retail evidence only; exact source identity, concrete layout, runtime damage behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__RebuildLandscapeDamageStamps"},
                tags("engine", "landscape", "damage-system"),
                new ParameterImpl[] {param("engine", voidPtr)})
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
