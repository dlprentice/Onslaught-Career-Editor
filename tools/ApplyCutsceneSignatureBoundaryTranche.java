//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCutsceneSignatureBoundaryTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
            this.createIfMissing = createIfMissing;
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

    private Function getOrCreate(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
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
        Function fn = getOrCreate(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
        }
        if (!allowedName(fn, spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        boolean changed = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
        }

        if (changed) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getOrCreate(spec, false);
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
            "cutscene-wave345",
            "cutscene",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x0043e8e0", "CCutscene__dtor_base", "__fastcall", voidType,
                "Destructor body for CCutscene: resets the two observed vptrs, calls Stop, frees the animation-name table, unregisters the CGenericActiveReader cell, and chains to CComplexThing__dtor_base. Exact class layout, runtime behavior, source identity, and rebuild parity remain unproven.",
                tags("destructor", "name-correction"),
                new String[] {"CCutscene__scalar_deleting_dtor_0043e8e0", "CCutscene__dtor_base"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043ea90", "CCutscene__scalar_deleting_dtor", "__thiscall", voidPtr,
                "CCutscene scalar-deleting destructor wrapper: calls CCutscene__dtor_base and frees this through OID__FreeObject when flags bit 0 is set. Runtime behavior, exact class layout, and rebuild parity remain unproven.",
                tags("destructor", "vtable-slot"),
                new String[] {"CCutscene__VFunc_01_0043ea90", "CCutscene__scalar_deleting_dtor"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0043eab0", "CCutscene__Init", "__thiscall", voidType,
                "Initializes CCutscene from an initThing: clears playback fields, copies initThing names into reader/cutscene name buffers, calls Load, then chains to CComplexThing__Init. Runtime behavior, exact class layout, and source parity remain unproven.",
                tags("init", "vtable-slot", "name-correction"),
                new String[] {"CCutscene__VFunc_09_0043eab0", "CCutscene__Init"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("initThing", voidPtr)}),
            new Spec("0x0043eca0", "CCutscene__ClearAnimationsAndStop", "__fastcall", voidType,
                "Recovered function boundary: calls the Stop slot through the CCutscene vtable, walks and clears 30 animation-slot lists, invokes CCutsceneAnimNode__DestroyRecursive for linked nodes, and releases node storage. Runtime behavior, exact source name, class layout, and rebuild parity remain unproven.",
                tags("function-boundary", "animation-cleanup"),
                new String[] {"CCutscene__ClearAnimationsAndStop"},
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043ed20", "CCutsceneAnimNode__DestroyRecursive", "__thiscall", voidPtr,
                "Cutscene animation-node recursive destructor helper: destroys the owned RT object at +0x244 when present, recurses through the next pointer at +0x248, and frees this when flags bit 0 is set. Runtime animation behavior, exact node layout, and rebuild parity remain unproven.",
                tags("destructor", "animation-node", "name-correction"),
                new String[] {"CCutscene__DestroyRecursive", "CCutsceneAnimNode__DestroyRecursive"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0043ed80", "CCutscene__Load", "__thiscall", intType,
                "Loads data cutscenes cut content through CChunkReader, handles known cutscene chunks, creates animation nodes through CCutscene__AddAnimation, and marks the cutscene dirty at +0x841. Runtime file coverage, exact format completeness, and rebuild parity remain unproven.",
                tags("loader", "signature-correction"),
                new String[] {"CCutscene__Load"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043f210", "CCutscene__AddAnimation", "__thiscall", voidPtr,
                "Allocates and links a cutscene animation node for trackSlot, copies animationName and meshName, stores startFrame and durationFrames, marks the cutscene dirty, and increments the per-slot count. Runtime animation playback semantics and exact node layout remain unproven.",
                tags("animation-node", "signature-correction"),
                new String[] {"CCutscene__AddAnimation"},
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("trackSlot", intType),
                    param("animationName", charPtr),
                    param("meshName", charPtr),
                    param("startFrame", intType),
                    param("durationFrames", intType)
                }),
            new Spec("0x0043f340", "CCutscene__Start", "__fastcall", voidType,
                "Starts cutscene playback: resets frame state, stores the current cutscene global, binds the active reader by name, hides the current HUD/track slot, and schedules an EVENT_MANAGER tick. Runtime behavior and rebuild parity remain unproven.",
                tags("playback", "signature-correction"),
                new String[] {"CCutscene__Start"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043f420", "CCutscene__Stop", "__fastcall", voidType,
                "Stops cutscene playback: restores camera state when needed, calls ResetLandscape, clears the current cutscene global, and restores HUD/track slot visibility. Runtime behavior and rebuild parity remain unproven.",
                tags("playback", "signature-correction"),
                new String[] {"CCutscene__Stop"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043f510", "CCutscene__InitAnimations", "__fastcall", voidType,
                "Initializes animation name index table: deduplicates animation names, allocates the name pointer table, stores copied names, and creates the CRTCutscene object. Runtime behavior, exact table ownership, and rebuild parity remain unproven.",
                tags("animation-index", "signature-correction"),
                new String[] {"CCutscene__InitAnimations"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043f690", "CCutscene__Update", "__fastcall", voidType,
                "Updates cutscene frame playback: prepares animations when dirty, installs a MovieCamera, advances the frame counter, drives CRTCutscene index state, plays sound samples, toggles HUD/track-slot state, and requeues an EVENT_MANAGER tick. Runtime behavior and rebuild parity remain unproven.",
                tags("playback", "signature-correction"),
                new String[] {"CCutscene__Update"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043fa70", "CCutscene__PrepareAnimations", "__fastcall", voidType,
                "Prepares animation timings: resolves animation indices, derives sample durations, writes start/duration fields, and clamps the total frame count at +0x848. Runtime behavior, exact animation format, and rebuild parity remain unproven.",
                tags("animation-timing", "signature-correction"),
                new String[] {"CCutscene__PrepareAnimations"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0043fcb0", "CCutscene__EventDispatchUpdate", "__thiscall", voidType,
                "Recovered event callback boundary: handles event code 3000 (0xbb8) by forwarding to CCutscene__Update and otherwise delegates to the fallback CComplexThing event handler. Runtime event ordering and rebuild parity remain unproven.",
                tags("function-boundary", "event-callback"),
                new String[] {"CCutscene__EventDispatchUpdate"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("eventRecord", voidPtr)}),
            new Spec("0x0043fcd0", "CCutscene__ForceEnd", "__cdecl", voidType,
                "Global force-end helper: if the current cutscene global is non-null, dispatches its vtable +0x100 Stop slot; otherwise returns without side effects. Runtime input path behavior and rebuild parity remain unproven.",
                tags("playback", "global-helper", "signature-correction"),
                new String[] {"CCutscene__ForceEnd"},
                false,
                new ParameterImpl[] {})
        };

        int changed = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changed++;
                }
            }
            catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " changed_or_would_change=" + changed + " failed=" + failed + " dry=" + dryRun);
        if (failed != 0) {
            throw new IllegalStateException("Cutscene tranche failed for " + failed + " target(s)");
        }
    }
}
