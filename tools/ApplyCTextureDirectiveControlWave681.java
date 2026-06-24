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
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCTextureDirectiveControlWave681 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean varArgs;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean varArgs, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.varArgs = varArgs;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int varArgs = 0;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "ctexture-directive-control-wave681",
            "wave681-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        if (fn.hasVarArgs() != spec.varArgs) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0 && !spec.varArgs) {
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
        if (spec.varArgs) {
            if (spec.parameters.length > 0) {
                sb.append(", ");
            }
            sb.append("...");
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec) + " varArgs=" + fn.hasVarArgs());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setVarArgs(spec.varArgs);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            if (spec.varArgs) {
                stats.varArgs++;
            }
            println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature().toString()
                + " varArgs=" + functionAtEntry(spec.address).hasVarArgs());
            Thread.sleep(50);
        }
        catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00589bd6",
                "CTexture__ReportDirectiveParseError",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr), param("diagnostic_format", charPtr) },
                true,
                "Wave681 static read-back: diagnostic helper marks the directive-parser context error flag at +0x2c, special-cases syntax-error tokens, and otherwise formats cdecl varargs into a bounded local buffer before appending a diagnostic message. Static metadata only; exact diagnostic string catalog, token enum, source-location semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "diagnostic-report", "varargs", "preprocessor-directive", "error-state")
            ),
            new Spec(
                "0x00589c82",
                "CTexture__SetCurrentSourceLocation",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("line_or_token_position", intType), param("source_location_value", intType), param("unused_context", intType) },
                false,
                "Wave681 static read-back: updates active include-context source-location fields below this+0x54, subtracts one from the line/token position when the current token is not end-of-line, optionally stores the secondary source value, and returns zero. Static metadata only; exact line/column meaning, active-context layout, diagnostic range semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "source-location", "diagnostic-context", "preprocessor-directive")
            ),
            new Spec(
                "0x00589cab",
                "CTexture__HandleDirective_Include",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave681 static read-back: #include handler accepts string/resource include tokens, reports syntax/provider/nesting errors, resolves full paths when needed, allocates a 0x70-byte include context, opens the include source, and links it at parser context +0x50. Static metadata only; exact provider ABI, path encoding policy, include-token enum, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "include-directive", "include-source", "preprocessor-directive", "allocation")
            ),
            new Spec(
                "0x00589e73",
                "CTexture__HandleDirective_Error",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave681 static read-back: #error handler captures the remaining logical line, folds line continuations, trims leading spaces/tabs, copies up to the bounded diagnostic buffer, appends the diagnostic, and marks parser error/status flags. Static metadata only; exact diagnostic ids, line-folding edge cases, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "error-directive", "diagnostic-report", "preprocessor-directive", "error-state")
            ),
            new Spec(
                "0x00589f49",
                "CTexture__PushConditionalFrame",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("condition_value", intType), param("unused_context", voidPtr) },
                false,
                "Wave681 static read-back: allocates a 0x10-byte conditional frame, records the incoming condition and parent active state, links it at active include-context +0x38, and updates the parser active flag at this+0x3c. Static metadata only; exact frame layout, condition-expression semantics, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "conditional-frame", "if-directive", "preprocessor-directive", "allocation")
            ),
            new Spec(
                "0x00589fa1",
                "CTexture__HandleDirective_Elif",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("condition_value", intType), param("unused_context", intType) },
                false,
                "Wave681 static read-back: #elif handler validates a current conditional frame, rejects #elif after #else, updates branch-seen state, and recomputes the parser active flag from parent activity, prior branches, and the new condition value. Static metadata only; exact conditional-frame fields, expression parser semantics, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "elif-directive", "conditional-frame", "preprocessor-directive", "error-state")
            ),
            new Spec(
                "0x0058a014",
                "CTexture__HandleDirective_Else",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave681 static read-back: #else handler validates the current conditional frame, rejects missing-frame and duplicate-else cases, activates the branch only when no prior branch fired under an active parent, and marks branch/else state. Static metadata only; exact conditional-frame fields, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "else-directive", "conditional-frame", "preprocessor-directive", "error-state")
            ),
            new Spec(
                "0x0058a076",
                "CTexture__HandleDirective_Endif",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave681 static read-back: #endif handler validates the active conditional frame, restores parser activity from the parent frame state, unlinks the top frame from active include-context +0x38, clears its child link, and destroys it. Static metadata only; exact conditional-frame fields, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "endif-directive", "conditional-frame", "preprocessor-directive", "recursive-cleanup")
            ),
            new Spec(
                "0x0058a0c6",
                "CTexture__HandlePragma_PackMatrix",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave681 static read-back: #pragma pack_matrix parser accepts optional row_major/column_major arguments, writes parser matrix-pack mode at +0x24, skips malformed lines, sets the pragma-handled flag at +0x28, and returns lexer status or zero. Static metadata only; exact pragma token ids, shader compile option mapping, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "pragma-pack-matrix", "pragma-directive", "preprocessor-directive", "parser-state")
            ),
            new Spec(
                "0x0058a1e3",
                "CTexture__HandlePragma_Warning",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave681 static read-back: #pragma warning parser handles once/error/disable/default modes, collects numeric warning ids through dynamically grown arrays, applies each mode through CDXTexture__SetKeyEntryModeFlags, frees temporary arrays, and marks the pragma-handled flag. Static metadata only; exact warning-id catalog, option propagation, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser-context", "pragma-warning", "warning-control", "pragma-directive", "preprocessor-directive")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " varargs=" + stats.varArgs
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave681 apply encountered missing/bad rows");
        }
    }
}
