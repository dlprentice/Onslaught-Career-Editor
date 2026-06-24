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

public class ApplyCTextureMacroSymbolWave682 extends GhidraScript {
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
            "ctexture-macro-symbol-wave682",
            "wave682-readback-verified",
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
                "0x0058a578",
                "CTexture__GetSymbolNameLength",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("symbol_name", charPtr) },
                false,
                "Wave682 static read-back: current-name helper walks a non-null macro symbol string to its NUL terminator and then returns the observed zero bucket/index value used by the adjacent sorted macro-symbol list helpers. Static metadata only; exact macro-table bucket policy, string encoding, current-name rationale, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("macro-symbol", "symbol-name", "bucket-index", "current-name-retained", "preprocessor-directive")
            ),
            new Spec(
                "0x0058a58d",
                "CTexture__InsertOrReplaceMacroSymbol",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("macro_symbol_node", voidPtr) },
                false,
                "Wave682 static read-back: inserts a macro-symbol node into the parser/table context list selected from this+0x4c, compares symbol names bytewise, replaces an existing equal-name node by unlinking and destroying it, or links the new node before the first greater name. Static metadata only; exact macro node layout, bucket policy, ownership contract, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("macro-symbol", "macro-insert", "macro-replace", "sorted-list", "preprocessor-directive", "recursive-cleanup")
            ),
            new Spec(
                "0x0058a60a",
                "CTexture__FindMacroSymbol",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("symbol_name", charPtr), param("out_macro_value", voidPtr), param("out_macro_payload", voidPtr) },
                false,
                "Wave682 static read-back: searches the context macro-symbol list selected from this+0x4c, compares names bytewise, stops when the sorted chain passes the requested symbol, and optionally copies the node +0x04/+0x08 payload slots to caller outputs on a match. Static metadata only; exact payload semantics, macro node layout, bucket policy, runtime expansion behavior, BEA patching, and rebuild parity remain unproven.",
                tags("macro-symbol", "macro-lookup", "sorted-list", "output-slot", "preprocessor-directive")
            ),
            new Spec(
                "0x0058a67b",
                "CTexture__EscapeQuotedStringInPlace",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("source_text", charPtr), param("source_length", intType), param("destination_text", charPtr) },
                false,
                "Wave682 static read-back: scans a bounded text span, toggles quote-state on unescaped double quotes, emits an added backslash before quote characters and in-quote backslashes when a destination buffer is provided, and still advances the output count when destination is null. Static metadata only; exact caller buffer-size contract, current-name rationale, escaped-string grammar, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("quoted-string", "escape-copy", "macro-expression", "preprocessor-directive", "current-name-retained")
            ),
            new Spec(
                "0x0058a6e0",
                "CTexture__NormalizeConditionalResultOrReport",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("condition_result", intType) },
                false,
                "Wave682 static read-back: normalizes a conditional-expression result, and when the result is zero and the parser error flag at +0x2c is still clear, appends a diagnostic from the current token record and marks the parser error flag. Static metadata only; exact expression-value convention, diagnostic catalog, token enum, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                tags("conditional-expression", "diagnostic-report", "error-state", "preprocessor-directive")
            ),
            new Spec(
                "0x0058a713",
                "CTexture__HandleDirective_Define",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("macro_name", charPtr), param("has_parameter_list", intType) },
                false,
                "Wave682 static read-back: #define handler allocates a 0x10-byte macro-symbol node, stores the macro name, optionally parses parenthesized parameter names into linked token descriptors while rejecting duplicates, captures replacement tokens from the pushback/current stream, and inserts or replaces the macro symbol. Static metadata only; exact token descriptor layout, parameter-list ABI, macro expansion semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("define-directive", "macro-symbol", "macro-parameters", "macro-replacement", "preprocessor-directive", "allocation")
            ),
            new Spec(
                "0x0058a981",
                "CTexture__RemoveMacroSymbol",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("symbol_name", charPtr) },
                false,
                "Wave682 static read-back: searches the context macro-symbol list selected from this+0x4c, compares names bytewise, unlinks the matching node when found, clears its next link, destroys it through the existing include-node destructor path, and otherwise returns zero. Static metadata only; exact macro node layout, bucket policy, ownership contract, runtime undef behavior, BEA patching, and rebuild parity remain unproven.",
                tags("undef-directive", "macro-symbol", "macro-remove", "sorted-list", "recursive-cleanup", "preprocessor-directive")
            ),
            new Spec(
                "0x0058a9ef",
                "CTexture__HandleDirective_Pragma",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                false,
                "Wave682 static read-back: generic #pragma dispatcher reads the next lexical token, compares identifier text against pack_matrix and warning, delegates to the specialized Wave681 pragma handlers, otherwise skips the logical line and marks the pragma-handled flag at +0x28. Static metadata only; exact pragma token ids, unsupported-pragma policy, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("pragma-directive", "pragma-dispatch", "directive-parser-context", "preprocessor-directive", "line-skip")
            ),
            new Spec(
                "0x0058aa69",
                "CTexture__HandleDirective_IfdefIfndef",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("symbol_name", charPtr) },
                false,
                "Wave682 static read-back: #ifdef/#ifndef helper queries the macro-symbol table, accepts a simple payload shape with empty parameter/replacement chains and kind range 2..4, returns the stored node +0x18 value for that shape, and otherwise reports a diagnostic when the macro lookup supplies a nonzero value slot. Static metadata only; exact ifdef/ifndef polarity, macro payload layout, expression-value convention, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ifdef-directive", "ifndef-directive", "macro-lookup", "conditional-expression", "preprocessor-directive", "diagnostic-report")
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
            throw new IllegalStateException("Wave682 apply encountered missing/bad rows");
        }
    }
}
