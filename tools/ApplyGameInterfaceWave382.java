//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGameInterfaceWave382 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
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
            "game-interface-wave382",
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004729d0",
                "CGameInterface__ctor_base",
                "__fastcall",
                voidType,
                "Name/signature correction: constructor-style base body for the global GameInterface object initializes the base monitor/control field at this+0x04 and installs the 0x005dbc2c vtable. Static retail evidence plus GAMEINTERFACE source call context only; exact source file body, concrete layout names, runtime menu behavior, and rebuild parity remain unproven.",
                new String[] {"CGameInterface__ctor_like_004729d0"},
                tags("game-interface", "constructor", "monitor", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004729e0",
                "CGameInterface__ResetMenuState",
                "__fastcall",
                voidType,
                "Name/signature correction: resets the global GameInterface menu state used by CGame::Init and CGame::InitRestartLoop, clearing fade/selection/menu-active fields, enabling six menu entries, enabling background rendering, and setting menu mode 1. Static retail evidence plus GAMEINTERFACE source call context only; exact source file body, runtime pause/menu behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__InitMouseInputState"},
                tags("game-interface", "pause-menu", "menu-state", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472a10",
                "CGameInterface__InitResources",
                "__fastcall",
                voidType,
                "Name/signature correction: source-parity GAMEINTERFACE.InitResources loads Interface_Joypad.tga and hud\\\\Menu_background.tga into GameInterface texture slots at this+0x0c and this+0x08. Static retail evidence only; texture lifetime, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {"CGameInterface__LoadHudTextures"},
                tags("game-interface", "resources", "textures", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472a50",
                "CGameInterface__Shutdown",
                "__fastcall",
                voidType,
                "Name/signature correction: source-parity GAMEINTERFACE.Shutdown releases the joypad/menu-background texture references when present, clears the texture slots, and then runs CMonitor shutdown core logic. Static retail evidence only; exact texture reference-count semantics, runtime shutdown behavior, and rebuild parity remain unproven.",
                new String[] {"CGameInterface__VFunc_02_00472a50"},
                tags("game-interface", "shutdown", "textures", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472a90",
                "CGameInterface__ToggleMenuDisplay",
                "__fastcall",
                voidType,
                "Name/signature correction: source-parity GAMEINTERFACE.ToggleMenuDisplay toggles the menu-active byte at this+0x1c, selects the first enabled entry, clears the opening flag, and switches mouse input between PlatformInput shutdown/init states. Static retail evidence only; exact UI input semantics, runtime pause/menu behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__ToggleMouseInputState"},
                tags("game-interface", "pause-menu", "mouse-input", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472ad0",
                "CGameInterface__AdvanceMenuSelectionWithWrap",
                "__fastcall",
                voidType,
                "Name/signature correction: advances the GameInterface selected menu entry at this+0x20 with wrap-around, respects disabled entry flags at this+0x2c..0x40, limits the option submenu differently in mode 2, and plays the frontend move sound when selection changes. Static retail evidence only; exact source file body, runtime input behavior, and rebuild parity remain unproven.",
                new String[] {"UISelectionList__AdvanceToNextEnabledWithWrap"},
                tags("game-interface", "pause-menu", "selection", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472b40",
                "CGameInterface__HandleMenuSelection",
                "__thiscall",
                voidType,
                "Name/signature correction: handles the active GameInterface menu selection for the controlling CController, including resume, message log/message box focus transfer, frontend quit/configuration choices, option submenu transitions, god-option notification, and DAT_008a9ab8 toggle. Callsite evidence shows one explicit controller parameter; the prior third parameter was a decompiler artifact. Static retail evidence only; exact option labels, runtime menu behavior, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__HandlePauseOptionsSelection"},
                tags("game-interface", "pause-menu", "controller", "options", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("controller", voidPtr)}
            ),
            new Spec(
                "0x00472f10",
                "CGameInterface__Render",
                "__fastcall",
                voidType,
                "Name/signature correction: source-parity GAMEINTERFACE.Render renders and processes the pause/menu overlay for the global GameInterface object passed from CDXEngine::PostRender, including fade state, joypad art, menu background, localized text, cursor/click selection, and dispatch to the selected controller. Static retail evidence only; runtime visual/menu behavior and rebuild parity remain unproven.",
                new String[] {"CDXEngine__RenderAndProcessPauseOptionsOverlay"},
                tags("game-interface", "pause-menu", "render", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave382 game-interface apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
