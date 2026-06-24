//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCTextureLexicalTokenWave684 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean varArgs;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean varArgs, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
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
            "ctexture-lexical-token-wave684",
            "wave684-readback-verified",
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

    private boolean hasExpectedName(Function fn, Spec spec) {
        return fn.getName().equals(spec.name);
    }

    private boolean hasAllowedStartingName(Function fn, Spec spec) {
        return fn.getName().equals(spec.name) || fn.getName().equals(spec.oldName);
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
        if (!hasExpectedName(fn, spec)) {
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
            if (!hasAllowedStartingName(fn, spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name + " old=" + spec.oldName);
                return;
            }
            boolean needsRename = !hasExpectedName(fn, spec);
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec) + " varArgs=" + fn.hasVarArgs());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec) +
                    (needsRename ? " rename=" + fn.getName() + "->" + spec.name : ""));
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
            println("OK: " + spec.address + " " + expectedSignature(spec) + " varArgs=" + spec.varArgs);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType doublePtr = new PointerDataType(DoubleDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType uintPtr = new PointerDataType(UnsignedIntegerDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0058c0e4",
                "CFastVB__ResetConversionStatus",
                "CFastVB__ResetConversionStatus",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("conversion_status_slot", voidPtr)
                },
                false,
                "Wave684 static read-back: clears the first dword in the caller-provided conversion status slot and returns without touching the surrounding CFastVB state. Static metadata only; exact owner structure, status enum semantics, runtime conversion behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fastvb-bridge", "conversion-status", "state-reset", "lexical-tranche-head")
            ),
            new Spec(
                "0x0058c178",
                "CDXTexture__InsertOrFindKeyInSortedTable",
                "CDXTexture__InsertOrFindKeyInSortedTable",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("key_value", intType),
                    param("out_index", uintPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: binary-searches the sorted key table at this+0x18, writes the found or insertion index to out_index, grows/copies the key and value arrays when needed, inserts a missing key with default value 1, and returns the local status code. Static metadata only; exact CDXTexture table layout, allocator ownership, key/value enum semantics, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "sorted-key-table", "binary-search", "table-insert", "lexical-token-support")
            ),
            new Spec(
                "0x0058c457",
                "CTexture__ParseFloatingLiteral",
                "CTexture__ParseFloatingLiteral",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_value", doublePtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: recognizes a digit-start or dot-digit floating literal, scans fractional and exponent characters, copies the span to a stack buffer, calls the CRT double parser, writes the parsed double to out_value, and returns the consumed length. Static metadata only; exact token enum, locale/overflow behavior, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "floating-literal", "double-parse", "source-span", "literal-parser")
            ),
            new Spec(
                "0x0058c5d3",
                "CTexture__ParseIdentifierToken",
                "CTexture__ParseIdentifierToken",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_identifier_node", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: accepts an alpha or underscore leader, scans identifier body characters through the CRT character-class mask helper, allocates token text from the token-list context at this+0x2c, stores the node pointer through out_identifier_node, and returns the consumed length. Static metadata only; exact identifier character set, token-node layout, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "identifier-token", "token-list", "allocation", "source-span")
            ),
            new Spec(
                "0x0058c652",
                "CTexture__ParseOperatorToken",
                "CTexture__ParseOperatorToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_operator_text", charPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: recognizes texture-script operators and punctuators, including one- through three-character forms, copies the matched operator text to out_operator_text, and returns the consumed length. Static metadata only; exact operator enum, parser precedence, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "operator-token", "punctuator-token", "source-span", "parser-token")
            ),
            new Spec(
                "0x0058c75e",
                "CTexture__ReadTypePrefixToken_FH",
                "CTexture__ReadTypePrefixToken_FH",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_token_kind", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: reads an optional f or h suffix after a numeric/float token, writes observed token-kind values 7 for f, 6 for h, and 5 for the default path, and returns the suffix length consumed. Static metadata only; exact token enum, numeric-type model, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "type-prefix", "numeric-suffix", "float-token", "token-kind")
            ),
            new Spec(
                "0x0058c7a4",
                "CTexture__ParseIntegerSuffix_UL",
                "CTexture__ParseIntegerSuffix_UL",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_token_kind", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: scans optional u and l integer suffix characters, writes observed token-kind value 4 for unsigned-long and 3 for long/default integer paths, and returns the suffix length consumed. Static metadata only; exact token enum, integer width rules, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "integer-suffix", "numeric-suffix", "integer-token", "token-kind")
            ),
            new Spec(
                "0x0058c82b",
                "CDXTexture__SetKeyEntryModeFlags",
                "CDXTexture__SetKeyEntryModeFlags",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("key_value", voidPtr),
                    param("mode_value", intType),
                    param("unused_context", uintType)
                },
                false,
                "Wave684 static read-back: inserts or finds a key-table entry, then updates the associated mode flags: mode 0xff resets the low bits and sets bit 0, mode 0x10 ORs flag 0x10, and other modes replace the low nibble with mode_value & 0xf. Static metadata only; exact key table value layout, flag names, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "sorted-key-table", "mode-flags", "flag-update", "lexical-token-support")
            ),
            new Spec(
                "0x0058c893",
                "CTexture__AppendDiagnosticMessage",
                "CTexture__AppendDiagnosticMessage",
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("diagnostic_accumulator", voidPtr),
                    param("source_location", voidPtr),
                    param("diagnostic_id", intType),
                    param("diagnostic_format", charPtr)
                },
                true,
                "Wave684 static read-back: varargs diagnostic formatter optionally prefixes source location text, formats an error X%u-style diagnostic with caller-supplied text, appends a newline, increments the accumulator count at +0x08, and appends the text line to the diagnostic list. Static metadata only; exact diagnostic accumulator layout, message catalog, varargs ABI beyond observed cdecl, runtime diagnostics, BEA patching, and rebuild parity remain unproven.",
                tags("diagnostic-report", "varargs", "text-list", "message-format", "lexer-diagnostic")
            ),
            new Spec(
                "0x0058c95c",
                "CTexture__AppendDiagnosticMessageDedup",
                "CTexture__AppendDiagnosticMessageDedup",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("diagnostic_accumulator", voidPtr),
                    param("source_location", voidPtr),
                    param("diagnostic_id", intType),
                    param("diagnostic_format", charPtr)
                },
                true,
                "Wave684 static read-back: varargs diagnostic formatter consults the sorted diagnostic key table to deduplicate or mode-gate messages, sets the observed 0x20 emitted flag, increments either the error or warning accumulator count, appends the formatted text line, and returns the emit status. Static metadata only; exact diagnostic table layout, severity enum, message catalog, runtime diagnostics, BEA patching, and rebuild parity remain unproven.",
                tags("diagnostic-report", "diagnostic-dedup", "sorted-key-table", "varargs", "message-format")
            ),
            new Spec(
                "0x0058cabd",
                "CTexture__LogUnexpectedTokenError_0058cabd",
                "CTexture__LogUnexpectedTokenError",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("diagnostic_id", intType),
                    param("token_record", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: unexpected-token reporter switches on the token record kind to choose descriptive text such as version token, integer, float, string constant, end of line, or end of file, then routes the formatted message to the diagnostic appender. Static metadata only; exact token enum, diagnostic catalog, token-record layout, runtime parser behavior, BEA patching, and rebuild parity remain unproven.",
                tags("diagnostic-report", "unexpected-token", "parser-token", "lexer-diagnostic", "address-suffix-removed")
            ),
            new Spec(
                "0x0058cc00",
                "CTexture__SkipWhitespaceAndComments",
                "CTexture__SkipWhitespaceAndComments",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("source_cursor_state", voidPtr)
                },
                false,
                "Wave684 static read-back: advances the lexer cursor across whitespace, newlines, backslash-newline continuations, // comments, /* */ comments, and optional semicolon comments gated by flag +0x28 bit 1, updates the line counter at +0x1c, and emits diagnostic id 0x3e9 for unterminated block comments. Static metadata only; exact cursor structure, comment policy, diagnostic catalog, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "whitespace-skip", "comment-skip", "line-counter", "diagnostic-report")
            ),
            new Spec(
                "0x0058cd30",
                "CTexture__ParseHexIntegerLiteral",
                "CTexture__ParseHexIntegerLiteral",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_value", uintPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: requires a 0x prefix followed by a hex digit, accumulates the base-16 integer value, writes the parsed value to out_value, warns with diagnostic id 0x3ea when the observed span exceeds 10 characters, and returns the consumed length. Static metadata only; exact integer overflow semantics, diagnostic catalog, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "integer-literal", "hex-literal", "diagnostic-report", "source-span")
            ),
            new Spec(
                "0x0058cdd5",
                "CTexture__ParseOctalIntegerLiteral",
                "CTexture__ParseOctalIntegerLiteral",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_value", uintPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: parses a leading-zero octal integer, consumes 0 through 7 digits, tracks overflow through the high 0xe0000000 bit region, writes the parsed value to out_value, warns with diagnostic id 0x3eb on overflow, and returns the consumed length. Static metadata only; exact integer overflow semantics, diagnostic catalog, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "integer-literal", "octal-literal", "diagnostic-report", "source-span")
            ),
            new Spec(
                "0x0058ce51",
                "CTexture__ParseDecimalIntegerLiteral",
                "CTexture__ParseDecimalIntegerLiteral",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_value", uintPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: consumes decimal digits, checks multiplication/addition overflow against the observed 0x19999999 threshold and wraparound paths, writes the parsed value to out_value, warns with diagnostic id 0x3ec on overflow, and returns the consumed length. Static metadata only; exact integer overflow semantics, diagnostic catalog, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "integer-literal", "decimal-literal", "diagnostic-report", "source-span")
            ),
            new Spec(
                "0x0058cef2",
                "CTexture__ParseEscapedCharLiteral",
                "CTexture__ParseEscapedCharLiteral",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_char_value", intPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: parses a normal character or C-style escape when escape handling is enabled, covers a/b/f/n/r/t/v plus octal and hex escapes, writes the integer character value to out_char_value, warns with diagnostic id 0x3ef when no escaped character is available, and returns the consumed length. Static metadata only; exact character encoding, escape policy flag, diagnostic catalog, runtime lexer behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "char-literal", "escape-sequence", "diagnostic-report", "source-span")
            ),
            new Spec(
                "0x0058d088",
                "CTexture__ParseDottedFormatAndResolveDescriptor_0058d088",
                "CTexture__ParseDottedFormatAndResolveDescriptor",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_format_descriptor", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: gated by flag +0x28 bit 1, parses a two-letter dotted format prefix, decimal component, and decimal or identifier suffix, bounds observed numeric fields below 0x100 and 0x20, calls the named-format descriptor lookup, writes the resolved descriptor to out_format_descriptor when found, and returns the consumed length. Static metadata only; exact format descriptor ABI, descriptor table coverage, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "format-descriptor", "dotted-format", "descriptor-lookup", "address-suffix-removed")
            ),
            new Spec(
                "0x0058d18b",
                "CTexture__ParseCharLiteralToken",
                "CTexture__ParseCharLiteralToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_char_value", intPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: recognizes a single-quoted character token, delegates character and escape decoding to the escaped-character helper, requires the closing quote, writes the decoded value to out_char_value, and returns the consumed length or 0 on mismatch. Static metadata only; exact character token enum, escape semantics, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "char-literal", "escape-sequence", "literal-parser", "source-span")
            ),
            new Spec(
                "0x0058d1ca",
                "CTexture__ParseStringLiteralToken",
                "CTexture__ParseStringLiteralToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_cursor", charPtr),
                    param("out_string_node", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: parses quoted strings and optional angle-bracket include-style strings gated by flag +0x28 bit 3, skips escape sequences, reports diagnostic ids 0x3ed and 0x3ee for newline or EOF termination, allocates and copies the string payload through the token-list context, and returns the consumed length. Static metadata only; exact string token enum, escape copying policy, token-node layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "string-literal", "include-string", "token-list", "diagnostic-report")
            ),
            new Spec(
                "0x0058d2ad",
                "CTexture__ReadNextLexToken",
                "CTexture__ReadNextLexToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_location", voidPtr),
                    param("out_token_record", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave684 static read-back: snapshots source/token positions, skips whitespace and comments, tries float, character, hex/octal/decimal integer, string, dotted-format descriptor, identifier, and operator parsers, stores observed token kind values and span data into out_token_record, advances the cursor, and returns 0. Static metadata only; exact token enum, token-record layout, lexer state layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("lexer", "token-fetch", "literal-parser", "parser-token", "source-span")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " varargs=" + stats.varArgs +
            " missing=" + stats.missing +
            " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave684 completed with missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
