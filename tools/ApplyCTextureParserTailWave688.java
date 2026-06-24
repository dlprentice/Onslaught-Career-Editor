//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCTextureParserTailWave688 extends GhidraScript {
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
            "ctexture-parser-tail-wave688",
            "wave688-readback-verified",
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
                if (spec.varArgs) {
                    stats.varArgs++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0058f593",
                "CTexture__ReadParserTerminalToken",
                "CTexture__ReadParserTerminalToken",
                "__fastcall",
                uintType,
                new ParameterImpl[] {
                    param("parser_compile_context", voidPtr)
                },
                false,
                "Wave688 static read-back: reads preprocessed tokens through CTexture__GetNextTokenWithPreprocessor into parser_compile_context+0x10, maps token classes to parser terminal ids 0x101/0x10d/0x10e/0x10f/0x110/0x111/0x112, recognizes entrypoint/true/false text, calls CTexture__ParseShaderSemanticToken when semantic parsing is enabled, and sets +0x4c/+0x50 error flags on lexer failure. Static metadata only; exact token enum, yacc grammar terminal names, context field names, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-terminal", "token-reader", "preprocessor-token", "shader-semantic", "tranche-head")
            ),
            new Spec(
                "0x0058f66f",
                "CTexture__ParseScriptTokensAndBuildNodes",
                "CTexture__ParseScriptTokensAndBuildNodes",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("token_descriptor", voidPtr),
                    param("relative_register_node", intType),
                    param("unused_context", intType)
                },
                false,
                "Wave688 static read-back: parses underscore-delimited register/expression token text from token_descriptor+0x08, matches register strings against the observed 0x48-byte descriptor table, derives register classes and modifiers, handles relative register offsets from relative_register_node when present, allocates 0x2c-byte node payloads, calls CTexture__ResolveOrCreateRegisterReference when parser state permits deferred register resolution, and emits diagnostic 0x7d5 for invalid register forms. Static metadata only; exact descriptor-table schema, register enum, node class identity, modifier enum, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-node-builder", "register-token", "register-descriptor-table", "diagnostic-0x7d5", "node-allocation")
            ),
            new Spec(
                "0x0058fb70",
                "CTexture__DestroyNodeAndBindingsRecord",
                "CTexture__DestroyNodeAndBindingsRecord",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("node_payload_record", voidPtr)
                },
                false,
                "Wave688 static read-back: frees the object/callback pointer stored at node_payload_record+0x00 and, when node_payload_record+0x20 is non-null, releases the linked binding record through CTexture__Dtor_ReleaseBindings_DeleteOnFlag(record, 1). Static metadata only; exact node payload layout, binding-record ownership, callback/free contract, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("node-cleanup", "binding-record", "destructor-helper", "callback-free")
            ),
            new Spec(
                "0x0058fb8b",
                "CTexture__DestroyParserCompileContext",
                "CTexture__DestroyParserCompileContext",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("parser_compile_context", voidPtr)
                },
                false,
                "Wave688 static read-back: tears down the parser compile context by releasing the object at +0x08 through vtable slot +0x08, releasing the +0x34 owner/list through its vtable, freeing +0x58 callback storage, and releasing the parser-state object at +0x78 through CTexture__Dtor_ReleaseParserState_DeleteOnFlag(state, 1). Static metadata only; exact compile-context layout, vtable owner identity, release ordering contract, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-context-cleanup", "compile-context", "vtable-release", "parser-state", "callback-free")
            ),
            new Spec(
                "0x0058fbc5",
                "CTexture__ApplyParserReductionAction",
                "CTexture__ApplyParserReductionAction",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reduction_rule_id", uintType),
                    param("rhs_count", uintType),
                    param("unused_context", uintType)
                },
                false,
                "Wave688 static read-back: applies parser reduction actions unless the +0x50 fatal flag is set, pops rhs_count nodes from the +0x34 parser stack with underflow diagnostics, switches on reduction_rule_id, links node lists, validates/coissues/predicates instruction nodes, applies channel masks and swizzles, builds relative-address and literal nodes, emits diagnostics 0x7d9/0x7da/0x7db/0x7dc/0x7e6/0x7eb/0x7ec/0x7ed where observed, cleans unused stack entries, and pushes the reduction result through a 0x14-byte parser-stack record. Static metadata only; exact yacc grammar rule mapping, node layout, parser stack layout, instruction ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-reduction", "yacc-action", "parser-stack", "instruction-validation", "diagnostic-range", "tranche-tail")
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
        println("ApplyCTextureParserTailWave688 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
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
            throw new IllegalStateException("Wave687 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
