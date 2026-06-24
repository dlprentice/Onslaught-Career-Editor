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

public class ApplyCTexturePreprocessorTokenWave683 extends GhidraScript {
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
            "ctexture-preprocessor-token-wave683",
            "wave683-readback-verified",
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
                "0x0058b1a0",
                "CTexture__InitPreprocessorDefaultDefines",
                "CTexture__InitPreprocessorDefaultDefines",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("default_define_pairs", voidPtr)
                },
                false,
                "Wave683 static read-back: seeds the preprocessor macro-symbol table with DIRECT3D, a runtime string-table default symbol, and numeric DIRECT3D_VERSION/D3DX_VERSION nodes, then optionally walks caller-provided default-define pairs through a temporary token-list context and the #define handler. Static metadata only; exact default-pair ABI, full macro payload layout, token descriptor layout, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("preprocessor-defaults", "macro-symbol", "define-directive", "token-list", "preprocessor-directive")
            ),
            new Spec(
                "0x0058b3c7",
                "CTexture__ExecuteDirectiveParserAction",
                "CTexture__ExecuteDirectiveParserAction",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("action_id", intType),
                    param("operand_count", uintType)
                },
                false,
                "Wave683 static read-back: directive-parser action dispatcher pops operand_count parser stack nodes, routes action ids to #define/#undef/#include/#error/#if/#ifdef/#ifndef/#elif/#else/#endif/#pragma helpers, evaluates arithmetic/comparison/logical expression cases, and emits diagnostics for stack underflow, divide-by-zero, or out-of-memory paths. Static metadata only; exact parser action enum, node layout, expression grammar, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-parser", "parser-action", "conditional-expression", "preprocessor-directive", "diagnostic-report")
            ),
            new Spec(
                "0x0058bd87",
                "CTexture__GetNextTokenWithPreprocessor",
                "CTexture__GetNextTokenWithPreprocessor",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_token", voidPtr)
                },
                false,
                "Wave683 static read-back: token fetcher serves queued pushback tokens or lexical tokens, recognizes a line-start # directive path, runs the directive parser, handles __FILE__/__LINE__ macro literals, manages include-frame EOF pop to a synthetic newline token, and suppresses/skips disabled conditional blocks with brace-depth tracking. Static metadata only; exact token enum, include context layout, conditional-skip semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-fetch", "directive-parser", "include-frame", "conditional-expression", "preprocessor-directive", "pushback-token")
            ),
            new Spec(
                "0x0058c08a",
                "CTexture__Preprocessor_PopIncludeFrameAtEof_0058c08a",
                "CTexture__Preprocessor_PopIncludeFrameAtEof",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("preprocessor_context", voidPtr)
                },
                false,
                "Wave683 static read-back: drains preprocessor tokens until an EOF token, unlinks the current include-file frame from the context +0x48 chain, destroys that frame, and refreshes the active stream/provider slot at +0x80 from the new frame head or the sentinel value 1. Static metadata only; exact include frame layout, stream/provider sentinel contract, runtime include behavior, BEA patching, and rebuild parity remain unproven.",
                tags("include-frame", "eof-token", "preprocessor-context", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c0ea",
                "CTexture__TokenList_FreeChain_0058c0ea",
                "CTexture__TokenList_FreeChain",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("list_head_slot", voidPtr)
                },
                false,
                "Wave683 static read-back: walks the list-head slot as a singly linked allocation chain, frees each current head node with OID__FreeObject_Callback, and stores the next link back into the slot until the list is empty. Static metadata only; exact token node payload layout, allocator ownership policy, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "list-free", "allocation", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c107",
                "CTexture__TokenList_PushAllocatedNode_0058c107",
                "CTexture__TokenList_PushAllocatedNode",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("payload_size", intType)
                },
                false,
                "Wave683 static read-back: allocates payload_size+4 bytes, writes the previous list head as the new node's first dword, links the new node into the head slot, and leaves the allocated node pointer as the return value used by identifier/string-token callers. Static metadata only; exact payload ownership, failure propagation, token node layout, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "list-push", "allocation", "return-pointer", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c129",
                "CTexture__TokenList_InitState_0058c129",
                "CTexture__TokenList_InitState",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("token_list_state", voidPtr)
                },
                false,
                "Wave683 static read-back: initializes a 0x20-byte token-list aggregate by clearing the head/count/buffer-like fields and setting the observed +0x10 default flag/value to 1. Static metadata only; exact field names, list ownership, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "state-init", "preprocessor-context", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c149",
                "CTexture__TokenList_ClearAndFreeBuffers_0058c149",
                "CTexture__TokenList_ClearAndFreeBuffers",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("token_list_state", voidPtr)
                },
                false,
                "Wave683 static read-back: frees the token-list node chain from the state head slot and then frees the two owned buffer/string slots observed at +0x18 and +0x1c. Static metadata only; exact buffer roles, ownership policy, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "list-free", "buffer-free", "preprocessor-context", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c2b9",
                "CTexture__AppendDiagnosticTextLine",
                "CTexture__AppendDiagnosticTextLine",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("text_line", charPtr)
                },
                false,
                "Wave683 static read-back: appends a diagnostic text line by allocating a list node large enough for the incoming NUL-terminated string plus link dword, linking it at the head, copying the string payload, and increasing the byte-count field at +0x04. Static metadata only; exact diagnostic list layout, string encoding, ownership policy, runtime diagnostics, BEA patching, and rebuild parity remain unproven.",
                tags("diagnostic-report", "text-list", "allocation", "preprocessor-directive")
            ),
            new Spec(
                "0x0058c30f",
                "CTexture__TokenList_EmitConcatenatedText_0058c30f",
                "CTexture__TokenList_EmitConcatenatedText",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_stream_slot", voidPtr)
                },
                false,
                "Wave683 static read-back: creates a memory write stream sized from the accumulated byte count plus a NUL terminator, writes the terminator at the end, and copies linked text-node payloads backward into the buffer to emit concatenated diagnostic/replacement text. Static metadata only; exact stream ABI, node ordering contract, buffer ownership, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "text-list", "stream-output", "macro-replacement", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c378",
                "CTexture__TokenList_GetCount_0058c378",
                "CTexture__TokenList_GetCount",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("token_list_state", voidPtr)
                },
                false,
                "Wave683 static read-back: returns the token-list state dword at +0x08, used by caller-side checks before emitting or consuming accumulated token/text list content. Static metadata only; exact field semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "count-field", "preprocessor-context", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c37c",
                "CTexture__TokenList_InitState_Extended_0058c37c",
                "CTexture__TokenList_InitState_Extended",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("preprocessor_span_state", voidPtr)
                },
                false,
                "Wave683 static read-back: initializes the extended preprocessor span/token state by clearing the observed head/end and auxiliary slots and setting the logical line/counter field at +0x1c to 1. Static metadata only; exact span structure, current-line semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("token-list", "state-init", "source-span", "preprocessor-context", "preprocessor-directive", "address-suffix-removed")
            ),
            new Spec(
                "0x0058c3fe",
                "CTexture__SkipLineContinuationAndAdvance",
                "CTexture__SkipLineContinuationAndAdvance",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("source_cursor_state", voidPtr)
                },
                false,
                "Wave683 static read-back: advances a source cursor until newline or end-of-span, treats backslash-LF and backslash-CRLF as line continuations, increments the observed line counter at +0x1c for continuations, and returns 1 only when a real newline is encountered. Static metadata only; exact source cursor layout, newline normalization policy, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("source-span", "line-continuation", "cursor-advance", "preprocessor-directive")
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
            throw new IllegalStateException("Wave683 completed with missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
