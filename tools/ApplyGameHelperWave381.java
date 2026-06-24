//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGameHelperWave381 extends GhidraScript {
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
            "game-helper-wave381",
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
        DataType boolType = BooleanDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004496e0",
                "CEndLevelData__IsAllSecondaryObjectivesComplete",
                "__fastcall",
                boolType,
                "Name/signature correction: source-parity CEndLevelData::IsAllSecondaryObjectivesComplete scans secondary objective status slots at this+0x4d0, returns false if any failed status is present, and logs ERROR: No secondary objectives when no complete/failed secondary objective is defined. Static retail evidence only; exact layout names, runtime progression behavior, and rebuild parity remain unproven.",
                new String[] {"CCareer__AreSecondaryObjectivesComplete"},
                tags("end-level-data", "secondary-objectives", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00470650",
                "CGame__DrawDebugStuff",
                "__fastcall",
                voidType,
                "Name/signature correction: source-parity CGame::DrawDebugStuff resets render state, draws selected unit/squad debug 3D hooks, renders heap and memory pressure text, and emits selected squad/unit debug overlay text. Static retail evidence only; concrete CGame layout, runtime debug overlay behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__RenderDebugMemoryAndSelectionInfo"},
                tags("game", "debug-overlay", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472240",
                "CConsole__AppendToStatusBufferV",
                "__cdecl",
                voidType,
                "Name/signature correction: appends formatted status/debug overlay text into the console/status buffer pointer at console+0x2710 through vsprintf and variadic stack arguments, then advances the write cursor. Static retail evidence only; exact object ownership, runtime console overlay behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__AppendToStatusBufferV"},
                tags("console", "status-overlay", "varargs", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("console", voidPtr), param("format", charPtr)}
            ),
            new Spec(
                "0x00472270",
                "Frontend__XorWideTextBlock100BytesToScratch",
                "__cdecl",
                shortPtr,
                "Name/signature correction: helper XORs a 0x64-byte wide-text block from encoded_text and xor_mask into the DAT_00679e18 scratch buffer and returns that scratch pointer for FrontendUpdate_CheatChecks text rendering. Static retail evidence only; exact frontend text ownership, runtime frontend text behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__XorBlock64Words"},
                tags("frontend", "wide-text", "xor", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("encoded_text", shortPtr), param("xor_mask", shortPtr)}
            ),
            new Spec(
                "0x00472570",
                "CGame__DoWeWantMesh",
                "__thiscall",
                boolType,
                "Signature/comment/tag correction: source-parity CGame::DoWeWantMesh compares mesh against the player cockpit and wingman mesh strings in CGame settings and returns true when a resource-build mesh is wanted. Static retail evidence only; exact settings layout, runtime resource loading behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("game", "mesh", "source-parity", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("mesh", charPtr)}
            ),
            new Spec(
                "0x004725f0",
                "CGame__GetPlayerLives",
                "__thiscall",
                intType,
                "Signature/comment/tag correction: source-parity CGame::GetPlayerLives returns mPlayer1Lives for player_index 1, mPlayer2Lives for player_index 2, and 0 for other selectors. Static retail evidence only; exact CGame layout, runtime lives behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("game", "lives", "source-parity", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("player_index", intType)}
            ),
            new Spec(
                "0x00472650",
                "CGame__IsRunningResources",
                "__fastcall",
                boolType,
                "Signature/comment/tag correction: source-parity CGame::IsRunningResources compares the current level at this+0x30 with the last resource-loaded level global DAT_006317cc. Static retail evidence only; exact resource-accumulator state, runtime resource loading behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("game", "resources", "source-parity", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472670",
                "CGame__GetNumPrimaryObjectives",
                "__fastcall",
                intType,
                "Name/signature correction: source-parity CGame::GetNumPrimaryObjectives counts non-MOS_NOT_DEFINED entries in the ten-entry mPrimaryObjectives array at CGame+0x4c with 8-byte objective records. Static retail evidence only; exact enum names, runtime objective UI behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__CountActiveSlots_A"},
                tags("game", "objectives", "primary-objectives", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00472690",
                "CGame__GetNumSecondaryObjectives",
                "__fastcall",
                intType,
                "Name/signature correction: source-parity CGame::GetNumSecondaryObjectives counts non-MOS_NOT_DEFINED entries in the ten-entry mSecondaryObjectives array at CGame+0x9c with 8-byte objective records. Static retail evidence only; exact enum names, runtime objective UI behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__CountActiveSlots_B"},
                tags("game", "objectives", "secondary-objectives", "name-corrected", "signature-hardened", "comment-hardened"),
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
            throw new RuntimeException("Wave381 game helper apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
