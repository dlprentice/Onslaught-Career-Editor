//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyCTextureParserSymbolTailWave685 extends GhidraScript {
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
            "ctexture-parser-symbol-tail-wave685",
            "wave685-readback-verified",
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0058d419",
                "CTexture__ParseVertexSemanticUsageToken",
                "CTexture__ParseVertexSemanticUsageToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("semantic_text", charPtr),
                    param("out_semantic_kind", voidPtr),
                    param("out_usage_index", voidPtr)
                },
                false,
                "Wave685 static read-back: splits a vertex semantic string into an alpha semantic prefix and optional decimal usage index, bounds the usage below 16, uppercases the prefix, maps observed D3D-style names such as POSITION, NORMAL, TEXCOORD, COLOR, FOG, DEPTH, SAMPLE, DIFFUSE, and SPECULAR to byte codes, writes semantic kind and usage outputs, and returns HRESULT-style success or failure. Static metadata only; exact enum ownership, shader ABI layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "vertex-semantic", "semantic-usage", "hresult", "tranche-head")
            ),
            new Spec(
                "0x0058d6b4",
                "CTexture__HashIdentifierMod7",
                "CTexture__HashIdentifierMod7",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("identifier_text", charPtr)
                },
                false,
                "Wave685 static read-back: case-folds each identifier byte through the locale-aware uppercase helper, accumulates hash = hash * 0x13 + char, returns hash modulo seven, and returns zero for null or empty identifiers. Static metadata only; exact identifier table ownership, locale edge cases, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "identifier-hash", "hash-bucket-count-7", "case-fold", "symbol-table-support")
            ),
            new Spec(
                "0x0058d6f0",
                "CTexture__FindIdentifierInHashTable",
                "CTexture__FindIdentifierInHashTable",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("identifier_text", charPtr)
                },
                false,
                "Wave685 static read-back: hashes identifier_text into one of seven buckets, walks linked nodes through offset +0x20, compares node text case-insensitively through lstrcmpiA, and returns the matching node pointer or null. Static metadata only; exact symbol-node structure, owning table type, allocation lifetime, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "identifier-hash", "hash-bucket-count-7", "symbol-lookup", "linked-list")
            ),
            new Spec(
                "0x0058d722",
                "CDXTexture__CollectHashBucketsToArray",
                "CDXTexture__CollectHashBucketsToArray",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_node_array", voidPtr)
                },
                false,
                "Wave685 static read-back: iterates the seven hash buckets at this+bucket*4, follows each bucket chain through node offset +0x20, and writes node pointers sequentially into out_node_array. Static metadata only; exact CDXTexture/CTexture table ownership, array capacity contract, symbol-node structure, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "hash-bucket-count-7", "symbol-table-flatten", "linked-list", "cdxtexture")
            ),
            new Spec(
                "0x0058d747",
                "CTexture__ResetParserSemanticValue",
                "CTexture__ResetParserSemanticValue",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("semantic_value", voidPtr)
                },
                false,
                "Wave685 static read-back: clears selected dword fields in the parser semantic-value aggregate at offsets 0x00, 0x04, 0x08, 0x34, 0x58, 0x5c, 0x60, and 0x78. Static metadata only; exact yacc semantic-value structure, field names, parser lifecycle, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "semantic-value-reset", "yacc-parser", "state-clear", "parser-support")
            ),
            new Spec(
                "0x0058d763",
                "CTexture__ReportYaccSyntaxError",
                "CTexture__ReportYaccSyntaxError",
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("parser_state", voidPtr),
                    param("message_format", charPtr)
                },
                true,
                "Wave685 static read-back: marks the parser error flag at +0x4c, treats the literal syntax error path as an unexpected-token diagnostic, emits version/instruction-modifier diagnostics for selected token/error-code combinations, and otherwise formats the caller-supplied yacc message through the diagnostic appender. Static metadata only; exact yacc state layout, diagnostic catalog, varargs ABI beyond observed cdecl, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "yacc-syntax-error", "diagnostic-report", "varargs", "parser-error-flag")
            ),
            new Spec(
                "0x0058d88d",
                "CTexture__NormalizeParserResultOrReport",
                "CTexture__NormalizeParserResultOrReport",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reduction_result", voidPtr)
                },
                false,
                "Wave685 static read-back: returns a non-null parser reduction result unchanged; for a null result, emits the internal production failed diagnostic only once, sets parser flags at +0x4c and +0x50, and returns null. Static metadata only; exact yacc state layout, production enum, reduction value ownership, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "reduction-result", "diagnostic-report", "parser-error-flag", "yacc-parser")
            ),
            new Spec(
                "0x0058d8c2",
                "CTexture__ParseShaderSemanticToken",
                "CTexture__ParseShaderSemanticToken",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("token_record", voidPtr)
                },
                false,
                "Wave685 static read-back: parses underscore-delimited shader semantic tokens from token_record+0x08, consults the shader-version semantic table through state +0x38, sets observed output fields at +0x40, +0x44, +0x48, and +0x54, recognizes modifier fragments such as centroid, pp, bias, and sampler/texture forms, and returns parser token codes including the observed failure code 0x10d. Static metadata only; exact semantic table schema, token enum, shader ABI layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-symbol", "shader-semantic-token", "semantic-modifier", "shader-version-table", "parser-token")
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
            throw new IllegalStateException("Wave685 completed with missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
