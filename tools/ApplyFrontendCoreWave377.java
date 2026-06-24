//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendCoreWave377 extends GhidraScript {
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
            "frontend-core-wave377",
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00466980",
                "CFrontEnd__GetPlayer0ControllerPort",
                "__thiscall",
                intType,
                "Signature/source-parity hardening: CFrontEnd player-0 controller port helper reads offset +0x274 and normalizes the unset -1 sentinel to 0, matching Stuart's CFrontEnd::GetPlayer0ControllerPort shape. Static source/decompile evidence only; runtime controller behavior remains unproven.",
                tags("frontend", "controller", "source-parity", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004669a0",
                "CFrontEnd__ReceiveButtonAction",
                "__thiscall",
                voidType,
                "Name/signature/source-parity correction: CFrontEnd::ReceiveButtonAction-style vtable slot dispatches frontend button input from a controller pointer, captures player-0 on BUTTON_FRONTEND_MENU_SELECT 0x2c, routes BUTTON_FRONTEND_CHEAT 0x2d, and returns with RET 0x0c. Static source/decompile/vtable evidence only; runtime input behavior remains unproven.",
                tags("frontend", "controller", "input", "vtable-slot", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"VFuncSlot_03_004669a0"},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_controller", voidPtr),
                    param("button", intType),
                    param("action_value", floatType)
                }
            ),
            new Spec(
                "0x00466ab0",
                "CFrontEnd__SetLanguage",
                "__thiscall",
                voidType,
                "Signature/source-parity hardening: CFrontEnd::SetLanguage takes one stack language_index, cleans up frontend options, and copies the selected text set into g_Text via CText__CopyFrom before returning with RET 0x4. Static source/decompile evidence only; runtime localization behavior remains unproven.",
                tags("frontend", "localization", "source-parity", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("language_index", intType)}
            ),
            new Spec(
                "0x00467200",
                "CFrontEnd__DrawSlidingTextBordersAndMask",
                "__thiscall",
                voidType,
                "Signature/source-parity hardening: CFrontEnd::DrawSlidingTextBordersAndMask takes transition and dest_page, uses the source static got_standard_SlidingTextBordersAndMask page predicate, and calls FEPShared__RenderSelectionBrackets while shaping page-transition masks. Static source/decompile evidence only; runtime frontend rendering remains unproven.",
                tags("frontend", "render", "transition", "source-parity", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("transition", floatType), param("dest_page", intType)}
            ),
            new Spec(
                "0x004679a0",
                "FrontEnd__HasStandardSlidingTextBordersAndMaskPage",
                "__cdecl",
                intType,
                "Owner/name/source-parity correction: source static got_standard_SlidingTextBordersAndMask page predicate, not a CFrontEnd instance method. The retail switch returns true for standard page switch set 7,8,9,10,11,13,14,16,17,19. Static source/decompile evidence only; runtime page styling remains unproven.",
                tags("frontend", "render", "page-predicate", "source-parity", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFrontEnd__HasStandardSlidingTextBordersAndMask"},
                new ParameterImpl[] {param("dest_page", intType)}
            ),
            new Spec(
                "0x00467bd0",
                "CFrontEnd__DrawTitleBar",
                "__stdcall",
                voidType,
                "Signature/source-parity hardening: CFrontEnd::DrawTitleBar takes WCHAR title text, transition, and dest_page, renders title-bar sprites, measures text, and dispatches CDXFont__DrawTextDynamic. Static source/decompile evidence only; runtime title rendering remains unproven.",
                tags("frontend", "render", "title-bar", "source-parity", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("title_text", shortPtr), param("transition", floatType), param("dest_page", intType)}
            ),
            new Spec(
                "0x00468700",
                "CFrontEnd__RenderCursorEndSceneAndAsyncSave",
                "__stdcall",
                voidType,
                "Name/signature/comment hardening: CFrontEnd vtable slot 7 renders the mouse cursor sprite, optionally ends scene when end_scene is nonzero, and schedules async career save. Static decompile/vtable evidence only; runtime frame behavior remains unproven.",
                tags("frontend", "render", "cursor", "async-save", "vtable-slot", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFrontEnd__VFunc_07_00468700"},
                new ParameterImpl[] {param("end_scene", intType)}
            ),
            new Spec(
                "0x004691c0",
                "CFrontEnd__ReleaseParticleHudWaypointResources",
                "__fastcall",
                voidType,
                "Signature/comment hardening: frontend cleanup helper drains particle-manager state, clears HUD handle table +0x48, releases six retained object references at +0x1a0, then frees waypoint/mesh/texture level resources. Static decompile evidence only; runtime cleanup behavior remains unproven.",
                tags("frontend", "cleanup", "particles", "hud", "level-resources", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("frontend", voidPtr)}
            ),
            new Spec(
                "0x00469390",
                "CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture",
                "__cdecl",
                uintType,
                "Signature/comment hardening: frontend modal mouse-input gate for CVBufTexture-style dispatch; if mouse input is not consumed by the modal path, passes float rectangle arguments plus dispatch_context to Input__DispatchClickInRect. Static decompile/xref evidence only; runtime mouse behavior remains unproven.",
                tags("frontend", "input", "mouse", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {
                    param("x", floatType),
                    param("y", floatType),
                    param("width", floatType),
                    param("height", floatType),
                    param("dispatch_context", intType)
                }
            ),
            new Spec(
                "0x004693d0",
                "CFrontEnd__GetCursorStateInRect",
                "__cdecl",
                uintType,
                "Signature/comment hardening: frontend modal mouse-input gate around CDXEngine__GetCursorStateInRect with four float rectangle arguments. Static decompile/xref evidence only; runtime mouse behavior remains unproven.",
                tags("frontend", "input", "mouse", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("x", floatType), param("y", floatType), param("width", floatType), param("height", floatType)}
            ),
            new Spec(
                "0x00469400",
                "CFrontEnd__GetClickStateInRect",
                "__cdecl",
                uintType,
                "Signature/comment hardening: frontend modal mouse-input gate around Input__GetClickStateInRect with four float rectangle arguments. Static decompile/xref evidence only; runtime mouse behavior remains unproven.",
                tags("frontend", "input", "mouse", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("x", floatType), param("y", floatType), param("width", floatType), param("height", floatType)}
            ),
            new Spec(
                "0x00469430",
                "CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady",
                "__cdecl",
                uintType,
                "Name/signature correction: CFEPDirectory directory cursor-state consume wrapper, more specific than the old CheckMouseInputReady label; gates through CFrontEnd__IsMouseInputReady and otherwise calls Input__GetCursorStateInRectAndConsume with four float rectangle arguments. Static decompile/xref evidence only; runtime directory mouse behavior remains unproven.",
                tags("frontend", "directory", "input", "mouse", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPDirectory__CheckMouseInputReady"},
                new ParameterImpl[] {param("x", floatType), param("y", floatType), param("width", floatType), param("height", floatType)}
            ),
            new Spec(
                "0x00469550",
                "CFrontEnd__ResolveLevelNameTextByCode",
                "__cdecl",
                shortPtr,
                "Return/signature hardening: maps level_code values to localized level-name text through CText__GetStringById and falls back to Text__AsciiToWideScratch(\"Unnamed Level\"). Static decompile evidence only; runtime localization behavior remains unproven.",
                tags("frontend", "localization", "level-name", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("level_code", intType)}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave377 frontend core apply failed; see FAIL lines above");
        }
    }
}
