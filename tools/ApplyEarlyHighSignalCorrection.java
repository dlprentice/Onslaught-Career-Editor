//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyEarlyHighSignalCorrection extends GhidraScript {
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

    private Function getFunctionOrThrow(String addressText) throws Exception {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
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
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
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

        Function readBack = getFunctionOrThrow(spec.address);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "early-high-signal-wave364",
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
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);

        Spec[] specs = new Spec[] {
            new Spec("0x00440b70", "CDamage__ctor_clear_head_and_init_flag", "__fastcall", voidType,
                "Wave364 owner correction: tiny damage.cpp-adjacent helper clears the damage-object head pointer and the +0x1588c initialization/sentinel field used by CDamage__Init. Corrects the stale CUnitAI owner label. Static retail evidence only; exact source method identity, concrete CDamage layout, runtime damage behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ResetPrimaryAndTailSentinels"},
                tags("damage-system", "owner-corrected"),
                new ParameterImpl[] {param("damage", voidPtr)}),
            new Spec("0x00441490", "CDXEngine__UpdateWrappedThingPositionsAndDistance", "__cdecl", voidType,
                "Wave364 signature/comment/tag hardening: CDXEngine__Render helper walks the world/debug render list at DAT_0066eb78, computes camera-relative distance into +0x80, wraps positions around the world-size threshold, refreshes terrain height through CStaticShadows__SampleShadowHeightBilinear when wrapped, dispatches the object update callback, and updates mapwho position when present. Static retail evidence only; exact list layout, source method identity, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "world-wrap", "signature-hardened"),
                new ParameterImpl[] {param("camera_x", floatType), param("camera_y", floatType), param("camera_z", floatType)}),
            new Spec("0x004416e0", "CConsole__ResetStatusHistoryBuffer", "__fastcall", voidType,
                "Wave364 owner correction: console/status-history reset helper clears 30 0x50-byte text slots and timestamp slots, resets the ring cursor at +0x9e4 and last-render timestamp at +0x9e8, and enables the buffer at +0x9ec when DAT_00662dd0 is set. Corrects the stale CUnit cooldown-table owner label. Static retail evidence only; exact console layout, source identity, runtime overlay behavior, and rebuild parity remain unproven.",
                new String[] {"CUnit__ResetPerSlotCooldownTables"},
                tags("console", "status-history", "owner-corrected"),
                new ParameterImpl[] {param("console", voidPtr)}),
            new Spec("0x004419e0", "CConsole__RenderStatusHistoryOverlay", "__fastcall", voidType,
                "Wave364 owner correction: console/status-history overlay renderer draws up to six recent ring-buffer lines through Text__AsciiToWideScratch and CDXFont__DrawText, aging/fading entries from DAT_00672fd0 timestamps and resetting +0x9e8 after inactivity. Corrects the stale frontend-cheat-check owner label. Static retail evidence only; exact console layout, runtime overlay behavior, and rebuild parity remain unproven.",
                new String[] {"FrontendUpdate_CheatChecks__RenderCheatStatusText"},
                tags("console", "status-history", "owner-corrected"),
                new ParameterImpl[] {param("console", voidPtr)}),
            new Spec("0x00441e50", "CDebugMarkers__Shutdown", "__fastcall", voidType,
                "Wave364 owner correction: debug-marker shutdown helper walks the global marker head passed by reference, unlinks entries from DAT_0066ffb0, and frees each marker through OID__FreeObject; CGame__ShutdownRestartLoop calls it before world/subsystem teardown. Corrects the stale CGame local-helper label. Static retail evidence only; exact debug-marker manager layout, source identity, runtime marker behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__FreeObjectIfPresent"},
                tags("debug-marker", "owner-corrected"),
                new ParameterImpl[] {param("head_ref", voidPtrPtr)}),
            new Spec("0x00441ea0", "CDebugMarkers__Render", "__fastcall", voidType,
                "Wave364 owner correction: DEBUGMARKERS.Render-style path called from CDXEngine__Render iterates the marker list, sets world matrices, ensures the default mesh texture, renders debug volume overlays, projects marker text into the window, and draws labels through CDXFont__DrawText. Corrects the stale CDXEngine-only billboard label. Static retail evidence only; exact debug-marker structure layout, runtime visual behavior, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__RenderWorldDebugTextBillboards"},
                tags("debug-marker", "render", "owner-corrected"),
                new ParameterImpl[] {param("debug_markers", voidPtr)}),
            new Spec("0x004422d0", "CDebugMarker__ctor", "__fastcall", voidPtr,
                "Wave364 owner correction: debug-marker constructor inserts this at the global DAT_0066ffb0 marker list head, clears link/owner-style fields, seeds default size/transform values, copies default vector/matrix globals, sets color/id defaults, and copies the initial text string into +0x98. Corrects the stale sound-event-node constructor label; sound manager is only one caller that creates visible sound markers. Static retail evidence only; exact class layout, source identity, runtime marker behavior, and rebuild parity remain unproven.",
                new String[] {"CSoundManager__SoundEventNode__Ctor"},
                tags("debug-marker", "constructor", "owner-corrected"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00442380", "CDebugMarker__UnlinkFromGlobalList", "__fastcall", voidType,
                "Wave364 owner correction: debug-marker unlink helper removes this from the global DAT_0066ffb0 singly-linked marker list before callers free the marker through OID__FreeObject. Corrects the stale sound-event-node unlink label. Static retail evidence only; exact destructor identity, allocator ownership, runtime marker behavior, and rebuild parity remain unproven.",
                new String[] {"CSoundManager__SoundEventNode__UnlinkFromGlobalList"},
                tags("debug-marker", "unlink", "owner-corrected"),
                new ParameterImpl[] {param("this", voidPtr)})
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
