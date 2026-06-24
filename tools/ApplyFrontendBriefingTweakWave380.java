//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendBriefingTweakWave380 extends GhidraScript {
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
            "frontend-briefing-tweak-wave380",
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
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00452430",
                "CFEPBriefing__ResetTimerAndClearState",
                "__thiscall",
                voidType,
                "Name/signature correction: CFEPBriefing vtable slot refreshes a timer from PLATFORM__GetSysTimeFloat plus the 0x005db3b4 constant, stores it at this+0x04, and clears this+0x08. Static retail evidence only; exact source identity, concrete briefing layout, runtime briefing behavior, and rebuild parity remain unproven.",
                new String[] {"CFEPBriefing__VFunc_06_00452430"},
                tags("frontend", "briefing", "timer", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("reset_state", intType)}
            ),
            new Spec(
                "0x004530a0",
                "CTweak__dtor_base_thunk_004530a0",
                "__fastcall",
                voidType,
                "Name/signature correction: one-instruction jump thunk to CTweak__dtor_base at 0x005286b0 used by static cleanup stubs. Static thunk evidence only; exact static object ownership, runtime tweak cleanup, and rebuild parity remain unproven.",
                new String[] {"CTweak__ctor_like_005286b0"},
                tags("frontend", "tweak", "destructor", "thunk", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00528690",
                "CTweak__ctor_base",
                "__thiscall",
                voidPtr,
                "Name/signature correction: constructor-style CTweak base body installs the base purecall vtable, stores callback_context at this+0x08, links this into the DAT_0089c018 global tweak list through this+0x04, and returns this. Static retail evidence only; exact source identity, concrete CTweak layout, runtime tweak registration, and rebuild parity remain unproven.",
                new String[] {"CTweak__ctor_like_00528690"},
                tags("tweak", "constructor", "global-list", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("callback_context", voidPtr)}
            ),
            new Spec(
                "0x005286b0",
                "CTweak__dtor_base",
                "__fastcall",
                voidType,
                "Name/signature correction: not a constructor; destructor-base body resets the CTweak base vtable and unlinks this from the DAT_0089c018 global tweak list via the next pointer at this+0x04. Static retail evidence only; exact source identity, concrete CTweak layout, runtime tweak cleanup, and rebuild parity remain unproven.",
                new String[] {"CTweak__ctor_like_005286b0"},
                tags("tweak", "destructor", "global-list", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00528b20",
                "CTweakInt_SetNumViewpoints__ctor",
                "__thiscall",
                voidPtr,
                "Name/signature correction: derived CTweak integer constructor performs the base list-link setup, then installs the PTR_CEngine__SetNumViewpoints_005e4aa4 vtable and stores initial_value at this+0x0c. Static retail evidence only; exact source identity, concrete CTweak layout, runtime viewpoint tweak behavior, and rebuild parity remain unproven.",
                new String[] {"CTweak__ctor_like_00528b20"},
                tags("tweak", "engine", "viewpoint", "constructor", "name-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("callback_context", voidPtr), param("initial_value", intType)}
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
            throw new RuntimeException("Wave380 frontend briefing/tweak apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
