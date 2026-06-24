//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendQueueWave376 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] allowedExistingNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
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

    private Function findFunctionAtSpecAddress(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
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
            Function fn = findFunctionAtSpecAddress(spec.address);
            if (fn == null) {
                throw new IllegalStateException("Function not found at " + spec.address);
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                if (!fn.getName().equals(spec.name)) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (!fn.getName().equals(spec.name)) {
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

            Function readBack = findFunctionAtSpecAddress(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "frontend-queue-wave376",
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
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00452fd0",
                "FEPShared__RenderSelectionBrackets",
                "__stdcall",
                voidType,
                "Owner/name/signature correction: shared frontend bracket helper used by multiple FEP render paths, not a CFEPMultiplayerStart-only method. Body loops over four CDXSurf__RenderSurface calls using DAT_0089d7f0 and returns with RET 0x4. Static render-helper evidence only; runtime frontend rendering remains unproven.",
                tags("frontend", "shared-ui", "render", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPMultiplayerStart__RenderSelectionBrackets"},
                new ParameterImpl[] {param("transition_alpha", floatType)}
            ),
            new Spec(
                "0x004530b0",
                "FEPShared__RenderSelectionMarker",
                "__stdcall",
                voidType,
                "Owner/name/signature correction: shared frontend marker helper used by CFEPBEConfig and CFEPMultiplayerStart render paths. Body renders selection marker surface DAT_0089d838, applies scale/alpha, and returns with RET 0x10. Static render-helper evidence only; runtime frontend rendering remains unproven.",
                tags("frontend", "shared-ui", "render", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPMultiplayerStart__RenderSelectionMarker"},
                new ParameterImpl[] {
                    param("x_index", floatType),
                    param("y_index", floatType),
                    param("scale", floatType),
                    param("alpha", intType)
                }
            ),
            new Spec(
                "0x00453140",
                "FEPShared__RenderContextHelpPrompt",
                "__stdcall",
                voidType,
                "Owner/name/signature correction: shared frontend help-prompt renderer used by save/load, level select, options, virtual keyboard, and multiplayer pages. The first argument is an integer help token selecting localized IDs 0x2b-0x30; the second is transition/progress. Static UI helper evidence only; runtime frontend input/render behavior remains unproven.",
                tags("frontend", "shared-ui", "help-prompt", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPMultiplayerStart__RenderHelpPromptForSelection"},
                new ParameterImpl[] {
                    param("help_token", intType),
                    param("transition", floatType)
                }
            ),
            new Spec(
                "0x00456830",
                "GlobalListNode__ClearField4AndPushGlobalList",
                "__thiscall",
                voidPtr,
                "Owner/name/signature correction: shared constructor-style callback referenced by CFEPDebriefing initialization, OID creation, and equipment construction paths. The body clears field +0x4, pushes this through CWorldPhysicsManager__PushNodeGlobalList, and returns this. Static callback evidence only; concrete object layout and runtime allocation behavior remain unproven.",
                tags("shared-callback", "global-list", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPDebriefing__ResetStateAndVector"},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00456850",
                "CFEPDebriefing__Shutdown",
                "__thiscall",
                voidType,
                "Name/signature correction: CFEPDebriefing vtable slot 1 shutdown-style cleanup. The body frees an array/object pair at fields +0x20 and +0x24 through CDXLandscape__DestroyArrayWithCallback and OID__FreeObject, then clears both fields. Static vtable cleanup evidence only; runtime debriefing behavior remains unproven.",
                tags("frontend", "debriefing", "vtable-slot", "shutdown", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPDebriefing__VFunc_01_00456850"},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00465a20",
                "TextLayout__WrapWideTextToFixedLines",
                "__stdcall",
                intType,
                "Owner/name/signature correction: shared wide-text wrapping helper used by frontend dialogs, language-test rendering, overlays, and game prompts. The body clears fixed 100-wchar line slots, measures candidate lines through CDXFont__GetTextExtent, trims spaces, and returns line count. Static text-layout evidence only; runtime text rendering remains unproven.",
                tags("text-layout", "wide-text", "shared-helper", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPLanguageTest__WrapWideTextToFixedLines"},
                new ParameterImpl[] {
                    param("line_buffer", shortPtr),
                    param("wide_text", shortPtr),
                    param("max_width", floatType)
                }
            ),
            new Spec(
                "0x004661d0",
                "CFEPMultiplayerStart__ClearJoinedPlayerSet",
                "__thiscall",
                voidType,
                "Signature/comment hardening: constructor/unwind tail-call wrapper that adds +0x20 to the CFEPMultiplayerStart receiver and jumps to CSPtrSet__Clear. Static constructor/unwind evidence only; concrete CFEPMultiplayerStart field layout remains unproven.",
                tags("frontend", "multiplayer-start", "tailcall", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004661e0",
                "CFEPMultiplayerStart__ClearSecondaryPlayerSet",
                "__thiscall",
                voidType,
                "Signature/comment hardening: constructor/unwind tail-call wrapper that adds +0x28 to the CFEPMultiplayerStart receiver and jumps to CSPtrSet__Clear. Static constructor/unwind evidence only; concrete CFEPMultiplayerStart field layout remains unproven.",
                tags("frontend", "multiplayer-start", "tailcall", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave376 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
