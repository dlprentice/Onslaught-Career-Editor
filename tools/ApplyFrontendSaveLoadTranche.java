//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendSaveLoadTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;
        final ParameterImpl[] parameters;
        final boolean createIfMissing;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] allowedExistingNames,
                ParameterImpl[] parameters,
                boolean createIfMissing) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
            this.parameters = parameters;
            this.createIfMissing = createIfMissing;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private Function createMissingFunction(Spec spec) throws Exception {
        Address address = addr(spec.address);
        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = findFunctionAtSpecAddress(spec.address);
            boolean missing = fn == null;
            if (missing && !spec.createIfMissing) {
                throw new IllegalStateException("Function not found at " + spec.address);
            }
            if (fn != null && !allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                if (missing) {
                    stats.wouldCreate++;
                } else if (!fn.getName().equals(spec.name)) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " -> " + expectedSignature(spec) + (missing ? " (create)" : ""));
                stats.skipped++;
                return;
            }

            if (missing) {
                fn = createMissingFunction(spec);
                stats.created++;
            } else if (!fn.getName().equals(spec.name)) {
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
            "frontend-save-load-wave375",
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
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec("0x00461c40", "CFEPLoadGame__Init", "__thiscall", boolType,
                "Boundary/name/signature correction: function object created for the FEPLoadGame vtable init slot. It initializes load-game selection fields, sets the save slot to -1, clears the save-name head, and returns true. Static retail/source-correlated evidence only; exact layout, runtime save/load behavior, and rebuild parity remain unproven.",
                tags("frontend", "load-game", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)},
                true),

            new Spec("0x00461c60", "CFEPLoadGame__ButtonPressed", "__thiscall", voidType,
                "Boundary/name/signature correction: function object created for the FEPLoadGame button vtable slot. It handles frontend directional/select/back buttons, clamps selection fields, plays frontend sounds, and routes back through CFrontEnd__SetPage. Static retail/source-correlated evidence only; exact input enum semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("frontend", "load-game", "input", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("button", intType), param("value", floatType)},
                true),

            new Spec("0x00461d60", "CFEPLoadGame__Process", "__thiscall", voidType,
                "Name/signature correction: source-correlated Process vtable slot for FEPLoadGame. The body performs a non-inactive-state update-like helper call, then in active state when DAT_00677614 is clear calls CFEPLoadGame__DoLoad. Static retail/source-correlated evidence only; helper identity at 0x0041a200, runtime save-load behavior, and rebuild parity remain unproven.",
                tags("frontend", "load-game", "process", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPLoadGame__VFunc_02_00461d60"},
                new ParameterImpl[] {param("this", voidPtr), param("state", intType)},
                false),

            new Spec("0x00461d90", "CFEPLoadGame__Render", "__thiscall", voidType,
                "Name/signature correction: source-correlated Render vtable slot for FEPLoadGame. The body calls DrawSlidingTextBordersAndMask, uses the load-game title token, renders overlay effects, and draws the shared help prompt. Static retail/source-correlated evidence only; exact visual parity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("frontend", "load-game", "render", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPLoadGame__VFunc_05_00461d90"},
                new ParameterImpl[] {param("this", voidPtr), param("transition", floatType), param("dest_page", intType)},
                false),

            new Spec("0x00464620", "CFEPSaveGame__Init", "__thiscall", boolType,
                "Boundary/name/signature correction: function object created for the FEPSaveGame vtable init slot. It initializes save-game selection fields and returns true. Static retail/source-correlated evidence only; exact layout, runtime save behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)},
                true),

            new Spec("0x00464630", "CFEPSaveGame__ButtonPressed", "__thiscall", voidType,
                "Boundary/name/signature correction: function object created for the FEPSaveGame button vtable slot. It handles frontend directional/select/back buttons, clamps selection fields, plays frontend sounds, and routes back through CFrontEnd__SetPage. Static retail/source-correlated evidence only; exact input enum semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "input", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("button", intType), param("value", floatType)},
                true),

            new Spec("0x00464730", "CFEPSaveGame__Process", "__thiscall", voidType,
                "Boundary/name/signature correction: function object created for the source-correlated Process vtable slot on FEPSaveGame. It calls CFEPSaveGame__CreateSave in active-state/no-message-box context and performs message-box overwrite/delete handling for save prompts. Static retail/source-correlated evidence only; exact message-box state enum semantics, runtime save behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "process", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("state", intType)},
                true),

            new Spec("0x00464a80", "CFEPSaveGame__Render", "__thiscall", voidType,
                "Name/signature correction: source-correlated Render vtable slot for FEPSaveGame. The body calls DrawSlidingTextBordersAndMask, uses the save-game title token, renders overlay effects, and draws the shared help prompt. Static retail/source-correlated evidence only; exact visual parity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "render", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPSaveGame__VFunc_05_00464a80"},
                new ParameterImpl[] {param("this", voidPtr), param("transition", floatType), param("dest_page", intType)},
                false),

            new Spec("0x00464b10", "FEPSaveLoad__TransitionNotification", "__thiscall", voidType,
                "Owner/name correction: shared save/load transition hook in both FEPSaveGame and FEPLoadGame vtables. It reads PLATFORM__GetSysTimeFloat, adds the transition delay constant, and stores it at this+0x4. Static retail/source-correlated evidence only; exact owning class fold, runtime UI behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "load-game", "transition", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFrontEndPage__TransitionNotification"},
                new ParameterImpl[] {param("this", voidPtr), param("from_page", intType)},
                false),

            new Spec("0x00464b30", "CFEPSaveGame__RemovedMUWhinge", "__cdecl", voidType,
                "Owner/name/signature correction: source-correlated RemovedMUWhinge-style helper shared by load and virtual keyboard paths. It resolves a localized storage message from reason_token and the current storage device, clears DAT_00677614, builds the standard dialog layout, and resets dialog state fields. Static retail/source-correlated evidence only; exact text-token enum, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "load-game", "storage-message", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPLoadGame__ResolveTextByToken"},
                new ParameterImpl[] {param("reason_token", intType)},
                false),

            new Spec("0x00464bc0", "CFEPSaveGame__AskIfYouWantToDelete", "__thiscall", voidType,
                "Owner/name/signature correction: source-correlated AskIfYouWantToDelete storage-space prompt. RET 0x0c and the caller stack show three stack arguments; the body currently uses because_4096 to choose the localized prompt while this, career_in_progress, and no_space_for_bea are not directly read in this retail body. Static retail/source-correlated evidence only; exact message-box semantics, runtime save behavior, and rebuild parity remain unproven.",
                tags("frontend", "save-game", "storage-message", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPSaveGame__DrawLocalizedStatusPrompt"},
                new ParameterImpl[] {param("this", voidPtr), param("career_in_progress", intType), param("because_4096", intType), param("no_space_for_bea", intType)},
                false)
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped + " created=" + stats.created + " would_create=" + stats.wouldCreate + " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename + " missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Frontend save/load tranche failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
