//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFatalControllerSignatureTranche extends GhidraScript {
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

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int missing = 0;
        int bad = 0;
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

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return addr;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = addr(addrText);
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrThrow(spec.address);
            if (!nameAllowed(fn.getName(), spec)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        String[] fatalTags = new String[] {"static-reaudit", "fatal-controller-wave327", "fatal-error", "signature-hardened"};
        String[] controllerTags = new String[] {"static-reaudit", "fatal-controller-wave327", "controller-system", "signature-hardened"};
        String[] sourceParityTags = new String[] {"static-reaudit", "fatal-controller-wave327", "controller-system", "signature-hardened", "source-parity", "owner-corrected"};
        String[] compilerTags = new String[] {"static-reaudit", "fatal-controller-wave327", "controller-system", "signature-hardened", "compiler-wrapper", "behavior-named"};
        String[] inputTags = new String[] {"static-reaudit", "fatal-controller-wave327", "input-system", "signature-hardened", "owner-corrected"};

        Spec[] specs = new Spec[] {
            new Spec("0x0042c750", "FatalError__ExitWithLocalizedPrefix_A", "__stdcall", voidType,
                "Signature/comment/tag correction: builds a 400-byte localized fatal-error message from localization string id 0xcc, the separator string at 0x00624624, and caller message text, then exits through FatalError__ExitProcess. This variant pops a second caller context/status argument; current decompile evidence does not show that value used by the body. Runtime fatal behavior, exact source identity, full format ownership, and rebuild parity remain unproven.",
                new String[] {}, fatalTags, new ParameterImpl[] {param("message", charPtr), param("callerContext", intType)}),
            new Spec("0x0042d0b0", "FatalError__ExitWithLocalizedPrefix_B", "__stdcall", voidType,
                "Signature/comment/tag correction: single-argument localized fatal wrapper used by mesh/resource deserialize paths; it prepends localization string id 0xcc and separator text before FatalError__ExitProcess. Runtime fatal behavior, exact source identity, full format ownership, and rebuild parity remain unproven.",
                new String[] {}, fatalTags, new ParameterImpl[] {param("message", charPtr)}),
            new Spec("0x0042d780", "CController__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Behavior-name/signature/comment/tag correction: compiler scalar deleting destructor wrapper for CController; calls CController__dtor, frees this through OID__FreeObject when flags bit 0 is set, and returns this. It is not a gameplay virtual behavior body; exact compiler provenance and rebuild parity remain unproven.",
                new String[] {"CController__VFunc_00_0042d780"}, compilerTags, new ParameterImpl[] {param("this", voidPtr), param("flags", uintType)}),
            new Spec("0x0042d7d0", "CController__SetNonInteractiveSection", "__cdecl", voidType,
                "Owner/signature/comment/tag correction: source-parity static CController::SetNonInteractiveSection(bool). When the non-interactive flag changes, it preserves or resumes the inactivity timer around FMV/loading sections, with attract-mode gating, then stores the new flag. Runtime inactivity behavior, exact global naming, and rebuild parity remain unproven.",
                new String[] {"CFrontEnd__SetLoadingTransitionGate"}, sourceParityTags, new ParameterImpl[] {param("nonInteractive", boolType)}),
            new Spec("0x0042da00", "Input__UpdateCursorCenterWithWindowScale", "__cdecl", voidType,
                "Owner/signature/comment/tag correction: retail input/cursor helper called from CGame init/update paths. It initializes cached cursor-center globals from PLATFORM window dimensions, then eases cached center coordinates toward the current window center when the resize/move flag is set and dev mode is off. Exact source identity, concrete global names, runtime mouse behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__UpdateCursorCenterWithWindowScale"}, inputTags, new ParameterImpl[] {param("recenterNow", boolType)}),
            new Spec("0x0042e3d0", "CController__GetMappedInputValue", "__thiscall", floatType,
                "Signature/comment/tag correction: helper used by CController__DoMappings to resolve mapping input values. Negative input codes dispatch to analog vtable slots for the supplied pad number and apply dead-zone/remap scaling; non-negative codes query the button/key vtable slot and return 1.0 or 0.0. Exact enum names, runtime input behavior, and rebuild parity remain unproven.",
                new String[] {}, controllerTags, new ParameterImpl[] {param("this", voidPtr), param("padNumber", intType), param("inputCode", intType)}),
            new Spec("0x0042e750", "CController__SetVibration", "__thiscall", voidType,
                "Owner/signature/comment/tag correction: source-parity CController::SetVibration(float,int). It ignores non-zero vibration outside GAME_STATE_PLAYING, then dispatches DeviceSetVibration(inValue) only when the player's CAREER vibration option is enabled, otherwise dispatches zero. Runtime force-feedback behavior, exact device backend, and rebuild parity remain unproven.",
                new String[] {"CGame__DispatchVibrationWithCareerGate"}, sourceParityTags, new ParameterImpl[] {param("this", voidPtr), param("inValue", floatType), param("playerIndex", intType)}),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped + " renamed=" + stats.renamed + " missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Fatal/controller signature tranche failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
