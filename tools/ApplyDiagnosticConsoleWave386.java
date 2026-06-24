//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyDiagnosticConsoleWave386 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;
        final boolean setVarArgs;
        final boolean setNoReturn;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters,
                boolean setVarArgs,
                boolean setNoReturn) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
            this.setVarArgs = setVarArgs;
            this.setNoReturn = setNoReturn;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int varArgs = 0;
        int noReturn = 0;
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

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            fn = getFunctionContaining(entry);
            if (fn != null && !fn.getEntryPoint().equals(entry)) {
                fn = null;
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
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.setVarArgs) {
            if (spec.parameters.length > 0) {
                sb.append(", ");
            }
            sb.append("...");
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
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
            if (spec.setVarArgs) {
                fn.setVarArgs(true);
            }
            if (spec.setNoReturn) {
                fn.setNoReturn(true);
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (spec.setVarArgs && !readBack.hasVarArgs()) {
                throw new IllegalStateException("Read-back varArgs mismatch at " + spec.address);
            }
            if (spec.setNoReturn && !readBack.hasNoReturn()) {
                throw new IllegalStateException("Read-back noReturn mismatch at " + spec.address);
            }
            if (readBack.hasVarArgs()) {
                stats.varArgs++;
            }
            if (readBack.hasNoReturn()) {
                stats.noReturn++;
            }
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString()
                + " varArgs=" + readBack.hasVarArgs() + " noReturn=" + readBack.hasNoReturn());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "diagnostic-console-wave386",
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
        DataType charType = CharDataType.dataType;
        DataType charPtr = new PointerDataType(charType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0040c640",
                "DebugTrace",
                "__cdecl",
                voidType,
                "Wave386 diagnostic correction: DebugTrace is retained as the broad retail diagnostic trace target, but the Steam body is a single RET stub. Xrefs still show hundreds of logging callsites across resource, frontend, memory, mesh, sound, and game paths. Runtime debug trace output, exact original implementation, and rebuild parity remain unproven.",
                new String[] {},
                tags("diagnostic-trace", "ret-stub", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {param("message", charPtr)},
                false,
                false
            ),
            new Spec(
                "0x0042cfa0",
                "FatalError__ExitProcess",
                "__cdecl",
                voidType,
                "Wave386 fatal-error correction: prints the supplied message/code through CConsole__Printf, shuts down mouse input, formats a localized fatal message using localization id 0xcb, normalizes newline/comma characters, touches the texture/path fallback helper, and ends through ExitProcess. Runtime fatal behavior, exact UI/error presentation, and rebuild parity remain unproven.",
                new String[] {},
                tags("fatal-error", "process-exit", "no-return", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {param("message", charPtr), param("code", intType)},
                false,
                true
            ),
            new Spec(
                "0x0042d080",
                "FatalError_LocalizedStringId",
                "__stdcall",
                voidType,
                "Wave386 fatal-error correction: when the guard byte is zero, loads a localized string by stringId, converts it through FromWCHAR, and forwards the message/code pair to FatalError__ExitProcess; when the guard is nonzero it returns. Runtime fatal behavior, caller intent for the guard byte, and rebuild parity remain unproven.",
                new String[] {},
                tags("fatal-error", "localized-string", "guard-gated", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {param("gate", charType), param("stringId", intType), param("code", intType)},
                false,
                false
            ),
            new Spec(
                "0x00441740",
                "CConsole__Printf",
                "__cdecl",
                voidType,
                "Wave386 console correction: variadic console print sink that formats into a 700-byte stack buffer with vsprintf, mirrors the formatted text and newline through DebugTrace, opens/appends the configured console file path when console+0x9ec is enabled, advances the 30-slot status/history ring at +0x9e4, copies up to 0x50 bytes, and updates timestamp fields. Runtime console output, exact layout names, buffer safety, and rebuild parity remain unproven.",
                new String[] {},
                tags("console-system", "variadic", "status-history", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {param("console", voidPtr), param("format", charPtr)},
                true,
                false
            ),
            new Spec(
                "0x004418a0",
                "CConsole__PrintfNoNewline",
                "__cdecl",
                voidType,
                "Wave386 console correction: variadic no-newline console print sink that checks the same console enable/file-open state, formats into a 256-byte stack buffer with vsprintf, writes the formatted text without the DebugTrace newline mirror, then advances the same 30-slot status/history ring and timestamp fields. Runtime console output, exact layout names, buffer safety, and rebuild parity remain unproven.",
                new String[] {},
                tags("console-system", "variadic", "status-history", "no-newline", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {param("console", voidPtr), param("format", charPtr)},
                true,
                false
            ),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " varargs=" + stats.varArgs
            + " noreturn=" + stats.noReturn
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave386 diagnostic/console correction failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
