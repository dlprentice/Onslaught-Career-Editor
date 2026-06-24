//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendLocalizationWave378 extends GhidraScript {
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
            "frontend-localization-wave378",
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

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00469c20",
                "CFrontEnd__ResolveEpisodeNameTextByIndex",
                "__cdecl",
                shortPtr,
                "Return/signature hardening: episode indices 1..8 resolve through CText__GetStringById and the fallback path returns Text__AsciiToWideScratch(\"Unnamed Episode\"). Static decompile/xref evidence only; runtime localization behavior remains unproven.",
                tags("frontend", "localization", "episode-name", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("episode_index", intType)}
            ),
            new Spec(
                "0x00469cf0",
                "CFrontEnd__ResolveLevelNameTextIdByCode",
                "__cdecl",
                intType,
                "Parameter/comment hardening: maps level/world code values to localized text-id constants and returns -1 for unmapped values. Static decompile/xref evidence only; runtime level-name localization remains unproven.",
                tags("frontend", "localization", "level-name", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("level_code", intType)}
            ),
            new Spec(
                "0x0046a1f0",
                "FrontEndText__GetLevelNameTextAfterCode",
                "__cdecl",
                shortPtr,
                "Owner/return/signature correction: frontend text helper, not CUnitAI; resolves a level_code through CFrontEnd__ResolveLevelNameTextIdByCode, then returns CText__GetStringByIdAfter with after_index. Only observed caller is a no-boundary briefing renderer region. Static decompile/callsite evidence only; runtime briefing rendering remains unproven.",
                tags("frontend", "localization", "briefing", "level-name", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CUnitAI__GetStringByResolvedTextIdAfter"},
                new ParameterImpl[] {param("level_code", intType), param("after_index", intType)}
            ),
            new Spec(
                "0x0046a210",
                "FrontEnd__GetBriefingLevelListTextColor",
                "__cdecl",
                uintType,
                "Name/signature correction: returns literal 0xffffdf5f; the only observed caller masks and shifts the returned value as a draw-color component, so this is not a text-id helper. Static instruction/callsite evidence only; runtime briefing rendering remains unproven.",
                tags("frontend", "briefing", "render", "color", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFrontEnd__GetFallbackUnnamedLevelTextId"},
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x0046a220",
                "FrontEndText__GetMultiplayerLevelDescriptionByType",
                "__cdecl",
                shortPtr,
                "Owner/return/signature correction: frontend multiplayer level description helper, not CUnitAI; maps level_type values to CText__GetStringById entries and falls back to Text__AsciiToWideScratch(\"Unknown Multiplayer Level Description\"). Static decompile/callsite evidence only; runtime multiplayer frontend rendering remains unproven.",
                tags("frontend", "localization", "multiplayer", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CUnitAI__GetMultiplayerLevelDescriptionByType"},
                new ParameterImpl[] {param("level_type", intType)}
            ),
            new Spec(
                "0x0046a2a0",
                "FrontEndText__GetLocalizedOrFallbackTextByToken",
                "__cdecl",
                shortPtr,
                "Owner/comment correction: broad frontend text-token resolver used across modal panels, local-coop prompts, BE config, directories, virtual keyboard, save/load, and level-select paths; not save-game-specific. It gates a debug fallback toggle through PlatformInput__ConsumeKeyOnce(0x2d) and DAT_00679b88 before choosing localized CText__GetStringById or ASCII fallback text. Static decompile/xref evidence only; runtime frontend localization behavior remains unproven.",
                tags("frontend", "localization", "text-token", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPSaveGame__GetLocalizedOrFallbackTextByToken"},
                new ParameterImpl[] {param("text_token", intType)}
            ),
            new Spec(
                "0x0046b1e0",
                "FrontEndText__GetAsciiFallbackTextByToken",
                "__cdecl",
                shortPtr,
                "Owner/return/signature correction: ASCII fallback frontend text-token resolver used by FrontEndText__GetLocalizedOrFallbackTextByToken, not save-game-specific; maps token cases to Text__AsciiToWideScratch and has an \"Unknown Text\" fallback. Static decompile/xref evidence only; runtime fallback toggle behavior remains unproven.",
                tags("frontend", "localization", "text-token", "fallback", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPSaveGame__GetAsciiFallbackTextByToken"},
                new ParameterImpl[] {param("text_token", intType)}
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
            throw new RuntimeException("Wave378 frontend localization apply failed; see FAIL lines above");
        }
    }
}
