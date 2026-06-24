//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyIScriptSlotGoodieWave579 extends GhidraScript {
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "iscript-slot-goodie-wave579",
            "retail-binary-evidence",
            "mission-script",
            "iscript",
            "command-handler",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] commandParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("script_args", voidPtr),
            param("unused_state", voidPtr),
            param("out_result", voidPtr)
        };
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
                "0x005338a0",
                "IScript__SetPlayerLives",
                "__stdcall",
                voidType,
                "Wave579 signature/comment hardening: fixed script command ABI handler for SetPlayerLives(player_index,lives). RET 0xc confirms three stack arguments even though only script_args is used. The body reads script_args[0] through datatype vtable slot +0x30 as player_index, reads script_args[1] through slot +0x30 as lives, and calls CGame__SetPlayerLives on global game/script state DAT_008a9a98. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact command descriptor layout, runtime mission-script behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__SetPlayerLives"},
                tags("fixed-script-abi", "player-lives", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005338d0",
                "IScript__SetSlot",
                "__stdcall",
                voidType,
                "Wave579 signature/comment hardening: fixed script command ABI handler for SetSlot(slot,val). RET 0xc confirms three stack arguments even though only script_args is used. The body reads slot from script_args[0] through datatype vtable slot +0x30, reads val from script_args[1] through slot +0x3c and masks it to one byte, then calls CGame__SetSlot on DAT_008a9a98. This updates the runtime script/game slot bitset only; it does not persist into CCareer mSlots. Static retail evidence only; runtime mission-script behavior, exact bitset ownership, and rebuild parity remain unproven.",
                new String[] {"IScript__SetSlot"},
                tags("fixed-script-abi", "slot-bit", "runtime-slot-only", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00533900",
                "IScript__SetSlotSave",
                "__stdcall",
                voidType,
                "Wave579 signature/comment hardening: fixed script command ABI handler for SetSlotSave(slot,val). RET 0xc confirms three stack arguments even though only script_args is used. The body reads slot and val, calls CGame__SetSlot on DAT_008a9a98, then re-reads the same script args and calls CCareer__SetSlot on CAREER at 0x00660620 to persist the flag into CCareer mSlots. This is the mission-script bridge from runtime slots to save-persistent slot bits. Static retail evidence only; runtime mission-script behavior, exact command descriptor layout, and rebuild parity remain unproven.",
                new String[] {"IScript__SetSlotSave"},
                tags("fixed-script-abi", "slot-bit", "persistent-slot", "career-save", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005339a0",
                "IScript__GetSlotBitValue",
                "__stdcall",
                voidType,
                "Wave579 signature/comment hardening: fixed script command ABI query handler for GetSlot(slot). RET 0xc confirms three stack arguments. The body allocates an 8-byte result object from MissionScript/IScript.cpp line 0x17d, reads slot from script_args[0] through datatype vtable slot +0x30, calls CGame__GetSlot on DAT_008a9a98, stores the boolean at result+0x04, installs bool-result vtable 0x005e4d50, and writes the result object through out_result. On allocation failure it writes null. Static retail evidence only; runtime mission-script behavior, exact result datatype label, and rebuild parity remain unproven.",
                new String[] {"IScript__GetSlotBitValue"},
                tags("fixed-script-abi", "slot-bit", "bool-result", "script-command-registry", "result-object"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00533a70",
                "IScript__SetGoodieState",
                "__stdcall",
                voidType,
                "Wave579 signature/comment hardening: fixed script command ABI handler for SetGoodieState(index,state). RET 0xc confirms three stack arguments even though only script_args is used. The body reads state from script_args[1] through datatype vtable slot +0x30, reads script index from script_args[0] through slot +0x30, and writes dword [index*4 + 0x00662560], which is g_Career_mGoodies[index-1] because g_Career_mGoodies starts at 0x00662564. Mission scripts use 1-based goodie indices; index 0 would underflow into adjacent career data. Static retail evidence only; runtime mission-script behavior, script corpus coverage, and rebuild parity remain unproven.",
                new String[] {"IScript__SetGoodieState"},
                tags("fixed-script-abi", "goodie-state", "career-save", "one-based-index", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00533aa0",
                "IScript__GetGoodieState",
                "__stdcall",
                voidType,
                "Wave579 signature/comment hardening: fixed script command ABI query handler for GetGoodieState(index). RET 0xc confirms three stack arguments. The body allocates an 8-byte result object from MissionScript/IScript.cpp line 0x196, reads script index from script_args[0] through datatype vtable slot +0x30, loads g_Career_mGoodies[index-1] from 0x00662564 + (index-1)*4, installs integer-result vtable 0x005e4af8, stores the value at result+0x04, and writes the result object through out_result. On allocation failure it writes null. Static retail evidence only; runtime mission-script behavior, script corpus coverage, and rebuild parity remain unproven.",
                new String[] {"IScript__GetGoodieState"},
                tags("fixed-script-abi", "goodie-state", "career-save", "one-based-index", "int-result", "script-command-registry", "result-object"),
                commandParams(voidPtr)
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave579 IScript slot/goodie tranche failed");
        }
    }
}
