//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCTextureDirectiveParserTailWave893 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "ctexture-directive-parser-tail-wave893",
            "wave893-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "texture-directive-parser",
            "important-texture-compiler-infrastructure",
            "raw-commentless-tail"
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
        if (!fn.getSignature().toString().equals(spec.signature)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("MISSING_READBACK: " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("BADNAME_READBACK: " + spec.address + " got " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("BADSIG_READBACK: " + spec.address + " got " + fn.getSignature());
        }
        String comment = fn.getComment();
        if (comment == null || !comment.equals(spec.comment)) {
            throw new IllegalStateException("BADCOMMENT_READBACK: " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("BADTAGS_READBACK: " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    return;
                }
                stats.renamed++;
                println("RENAME_BLOCKED_BY_POLICY: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getSignature().toString().equals(spec.signature)) {
                println("BADSIG: " + spec.address + " got " + fn.getSignature() + " expected " + spec.signature);
                stats.bad++;
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x0058aacf",
                "CTexture__HandleDirective_If",
                "int CTexture__HandleDirective_If(void)",
                "Wave893 static read-back: CTexture directive-expression/macro expansion helper reached from CTexture__GetNextTokenWithPreprocessor at 0x0058bf56. Static retail Ghidra evidence only: preserves the current name/signature while the body observes queued/lexed token descriptors, copies NodeType8 descriptor records, parses function-like actual-parameter lists, reports \"unexpected end of file in macro expansion\" and \"not enough actual parameters for macro '%s'\", expands argument references, handles stringize/charize-like markers \"#\" and \"#@\", handles token paste marker \"##\", re-lexes synthesized token text through CTexture__InitBufferCursorRange and CTexture__ReadNextLexToken, and links the expanded token chain back through context+0x44. Exact source identity, directive-expression grammar role, macro node/token descriptor layout, hidden stack ABI, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-if", "macro-expansion", "token-paste-stringize")
            ),
            new Spec(
                "0x0058b812",
                "CTexture__RunDirectiveParser",
                "int CTexture__RunDirectiveParser(void)",
                "Wave893 static read-back: CTexture directive parser driver called by CTexture__GetNextTokenWithPreprocessor at 0x0058be46. Static retail Ghidra evidence only: initializes YACC-style parser globals DAT_009d1430/DAT_009d0c60 plus stack cursors DAT_009d1824/DAT_009d1820, uses parser tables around DAT_00657b48/DAT_00657c08/DAT_00658050/DAT_00657d68, maps lexer output through CTexture__MapLexTokenToPreprocessorToken, dispatches reductions through CTexture__ExecuteDirectiveParserAction with action ids and operand counts, and reports \"syntax error\" or \"yacc stack overflow\" through CTexture__ReportDirectiveParseError. Exact grammar table ownership, token/action enum meanings, global parser-state lifetime, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directive-yacc-parser", "parser-table", "preprocessor-token-map")
            ),
            new Spec(
                "0x0058bd25",
                "CTexture__InitializePreprocessorStateFromMemorySpan",
                "int CTexture__InitializePreprocessorStateFromMemorySpan(void)",
                "Wave893 static read-back: CTexture preprocessor bootstrap called by CVertexShader__CompileScriptWithDirectiveParser at 0x00579ac8. Static retail Ghidra evidence only: allocates a 0x70-byte preprocessor context with OID__AllocObject_DefaultTag_00662b2c, runs CTexture__PreprocessorContextCtor, stores the context at this+0x50, initializes a source buffer from the caller memory span through CTexture__InitBufferFromMemorySpan, seeds default defines through CTexture__InitPreprocessorDefaultDefines, then mirrors the active context to this+0x54 and stores the caller value at this+0x58 before returning 0. Exact preprocessor context layout, source-span ABI, default define contract, runtime compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("preprocessor-bootstrap", "memory-span", "default-defines")
            ),
            new Spec(
                "0x0058c396",
                "CTexture__InitBufferCursorRange",
                "int CTexture__InitBufferCursorRange(void)",
                "Wave893 static read-back: shared CTexture source-buffer cursor initializer called by CTexture__InitBufferFromMemorySpan, CTexture__InitPreprocessorDefaultDefines, CTexture__HandleDirective_If, and CTexture__OpenIncludeSourceAndInitBuffer. Static retail Ghidra evidence only: accepts a source pointer and length, computes strlen when length is -1, validates provider/context arguments, writes begin/end pointers and caller metadata into the destination cursor aggregate, and returns 0 on success or -0x7fffbffb on invalid input. Exact cursor field names, provider/context ownership, source encoding, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                tags("source-buffer-cursor", "memory-span", "shared-preprocessor-helper")
            ),
            new Spec(
                "0x0058d821",
                "CTexture__EmitParserMessageBySeverity",
                "int CTexture__EmitParserMessageBySeverity(void)",
                "Wave893 static read-back: CTexture parser message severity adapter referenced as DATA from CTexture__LoadScriptAndDispatchByVersion at 0x00590b1c. Static retail Ghidra evidence only: uses severity values 1/5 for CTexture__AppendDiagnosticMessageDedup, severity values 2/6 for CTexture__AppendDiagnosticMessage, adds 5000 to the incoming message id, emits through format \"%s\", and sets parser error/status flag slot 0x13 on the non-deduplicated error path. Exact diagnostic catalog, severity enum semantics, callback table ownership, runtime compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-diagnostic", "severity-adapter", "message-id-5000")
            ),
            new Spec(
                "0x0058f34c",
                "CTexture__ResolveOrCreateRegisterReference",
                "int CTexture__ResolveOrCreateRegisterReference(void)",
                "Wave893 static read-back: CTexture shader register/reference resolver called by CTexture__ParseScriptTokensAndBuildNodes at 0x0058fac0. Static retail Ghidra evidence only: rejects register names shorter than three chars, classifies prefixes through globals including DAT_005ecd94, DAT_005ecd90, DAT_005ecf14, DAT_005ecf10, and DAT_005ecf0c, uses input/temp/constant hash tables at observed context offsets including +0x1c and +0x38, validates vertex semantic usage through CTexture__ParseVertexSemanticUsageToken, creates symbol nodes with CTexture__InsertSymbolNodeInHashTable, validates constant declaration type and address offsets, and emits 0x7d5 diagnostics such as invalid input register, forbidden addressing operations, constant register address out of bounds, and invalid register name. Exact register enum, prefix string table, symbol table layout, constant declaration ABI, runtime shader compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shader-register-reference", "symbol-table", "diagnostic-0x7d5")
            ),
            new Spec(
                "0x0059020b",
                "CTexture__ParseScriptWithYaccTables",
                "int CTexture__ParseScriptWithYaccTables(void)",
                "Wave893 static read-back: CTexture shader/script YACC parser called by CTexture__LoadScriptAndDispatchByVersion at 0x00590b61. Static retail Ghidra evidence only: initializes parser globals DAT_009d2010/DAT_009d1840 plus stack cursors DAT_009d2404/DAT_009d2400, consumes terminals through CTexture__ReadParserTerminalToken, drives parse tables around DAT_00658438/DAT_00658580/DAT_00658a20/DAT_006587d0, dispatches reductions through CTexture__ApplyParserReductionAction with reduction_rule_id/rhs_count pairs, and reports \"syntax error\" or \"yacc stack overflow\" through CTexture__ReportYaccSyntaxError. Exact grammar table ownership, terminal/reduction enum meanings, global parser-state lifetime, runtime shader compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("script-yacc-parser", "parser-table", "reduction-action")
            ),
            new Spec(
                "0x00590da0",
                "CTexture__DrainParserWorkQueue",
                "int CTexture__DrainParserWorkQueue(void)",
                "Wave893 static read-back: compact parser/decode work-queue drain helper called twice by CDXTexture__ProcessInputControllerState at 0x00590f4c and 0x00590f6c. Static retail Ghidra evidence only: uses hidden ESI state, invokes a callback through state slot 0x6a when state[5] is not 0xcc, clears state[0x23], sets state[5] to 0xcc, loops while *(state[0x6a]+8) is nonzero, marks the current object/node field +0x14 with 0x30 before calling its vtable entry, then sets state[5] to 0xcd or 0xce depending on state[0x11] before returning 1. Exact work-queue structure, callback/vtable ownership, state enum meanings, runtime decode/parser scheduling behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-work-queue", "hidden-esi-state", "state-0xcc-0xcd")
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
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave893 apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
