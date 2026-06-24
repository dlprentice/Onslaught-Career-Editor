//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCTextureIncludeContextWave680 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, boolean updateSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.updateSignature = updateSignature;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
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

    private String[] baseTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "ctexture-include-context-wave680",
            "wave680-readback-verified",
            "retail-binary-evidence",
            "comment-hardened"
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
        if (!spec.updateSignature) {
            return true;
        }
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
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

    private String expectedSignature(Spec spec, Function fn) {
        if (!spec.updateSignature) {
            return fn.getSignature().toString();
        }
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
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
        sb.append(")");
        return sb.toString();
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
            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec, fn));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec, fn));
                return;
            }

            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec, functionAtEntry(spec.address)));
        }
        catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec spec(String address, String name, boolean updateSignature, String callingConvention, DataType returnType,
            ParameterImpl[] params, String comment, String... tags) {
        return new Spec(address, name, updateSignature, callingConvention, returnType, params, comment, baseTags(tags));
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            spec(
                "0x00589367",
                "CTexture__ReleaseIncludeNodeTreeRecursive",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("include_node", voidPtr) },
                "Wave680 static read-back: recursive include-node release helper visits object/vtable-owned payload slots at +0x04 and +0x08, then recurses through the child link at +0x0c before freeing the child node. Static metadata only; exact node layout, payload ownership, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-node", "recursive-cleanup", "payload-release"
            ),
            spec(
                "0x0058939b",
                "CTexture__IncludeNodeDtor",
                true,
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", intType), param("unused_context", intType) },
                "Wave680 static read-back: scalar-deleting destructor wrapper for include nodes calls CTexture__ReleaseIncludeNodeTreeRecursive, frees this when delete_flags bit 0 is set, and returns this. Static metadata only; exact destructor ABI, allocation provenance, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-node", "scalar-deleting-destructor", "recursive-cleanup"
            ),
            spec(
                "0x005893b7",
                "CTexture__IncludeNodeCtor",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("primary_payload", voidPtr), param("secondary_payload", intType), param("unused_context", intType) },
                "Wave680 static read-back: include-node constructor clears links at +0x08/+0x0c, stores primary_payload at +0x00, and stores secondary_payload at +0x04. Static metadata only; exact node layout, payload type, caller ownership, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-node", "constructor", "payload-slots"
            ),
            spec(
                "0x005893d1",
                "CTexture__FreeChildIncludeNodeChainRecursive",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("include_node", voidPtr) },
                "Wave680 static read-back: child-chain cleanup follows the +0x0c child link recursively and frees each child node without invoking the payload destructors used by CTexture__ReleaseIncludeNodeTreeRecursive. Static metadata only; exact node layout, ownership split, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-node-chain", "recursive-cleanup", "child-link"
            ),
            spec(
                "0x005893e9",
                "CTexture__IncludeNodeChain_scalar_deleting_dtor",
                true,
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", intType), param("unused_context", intType) },
                "Wave680 static read-back: scalar-deleting destructor wrapper for child-only include-node chains calls CTexture__FreeChildIncludeNodeChainRecursive, frees this when delete_flags bit 0 is set, and returns this. Static metadata only; exact destructor ABI, ownership split, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-node-chain", "scalar-deleting-destructor", "recursive-cleanup"
            ),
            spec(
                "0x00589405",
                "CTexture__PreprocessorContextCtor",
                true,
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("preprocessor_context", voidPtr) },
                "Wave680 static read-back: preprocessor-context constructor initializes token-list state, mapped-file context at +0x3c, GDI bitmap record at +0x4c, and clears include/source buffer and child-context slots through +0x6c before returning the context pointer. Static metadata only; exact context layout, source-provider contract, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "preprocessor-context", "constructor", "mapped-file-context", "gdi-record"
            ),
            spec(
                "0x00589438",
                "CTexture__CleanupIncludeContextRecursive",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("preprocessor_context", voidPtr) },
                "Wave680 static read-back: recursive include-context cleanup destroys the include-node chain at +0x38, recurses through child context +0x6c, releases provider-backed buffer state through +0x58/+0x64, deletes the GDI object slot, closes mapped-file state, and runs the no-op node payload hook. Static metadata only; exact context layout, provider ABI, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "preprocessor-context", "recursive-cleanup", "mapped-file-context", "gdi-record"
            ),
            spec(
                "0x0058948d",
                "CTexture__IncludeContextDtor",
                true,
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", intType), param("unused_context", intType) },
                "Wave680 static read-back: scalar-deleting destructor wrapper for include contexts calls CTexture__CleanupIncludeContextRecursive, frees this when delete_flags bit 0 is set, and returns this. Static metadata only; exact destructor ABI, context allocation ownership, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "preprocessor-context", "scalar-deleting-destructor", "recursive-cleanup"
            ),
            spec(
                "0x005894a9",
                "CTexture__OpenIncludeSourceAndInitBuffer",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave680 static read-back: locked-storage include-source open helper records provider state at +0x58, converts wide paths when requested, allocates full-path buffers through the token-list allocator, opens mapped-file input or provider-backed input, records buffer pointer/count at +0x64/+0x68, and initializes the buffer cursor range. Signature is preserved because Ghidra still reports unknown calling convention with locked parameter storage. Static metadata only; exact provider ABI, path encoding policy, buffer lifetime, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-preserved", "ghidra-locked-storage", "include-source", "mapped-file-context", "provider-backed-buffer"
            ),
            spec(
                "0x00589650",
                "CTexture__InitBufferFromMemorySpan",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave680 static read-back: locked-storage memory-span helper records caller buffer pointer/count at +0x64/+0x68, rejects null pointer with nonzero length, and delegates to the shared buffer cursor range initializer. Signature is preserved because Ghidra still reports unknown calling convention with locked parameter storage. Static metadata only; exact memory-span ABI, cursor layout, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-preserved", "ghidra-locked-storage", "memory-span", "buffer-cursor"
            ),
            spec(
                "0x00589689",
                "CTexture__FreeIncludeFileChainRecursive",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("include_file_node", voidPtr) },
                "Wave680 static read-back: include-file chain cleanup follows the next link at +0x04 recursively and frees each linked include-file node. Static metadata only; exact include-file node layout, allocation ownership, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-file-chain", "recursive-cleanup"
            ),
            spec(
                "0x005896a1",
                "CTexture__IncludeFileChainDtor",
                true,
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", intType), param("unused_context", intType) },
                "Wave680 static read-back: scalar-deleting destructor wrapper for include-file chains calls CTexture__FreeIncludeFileChainRecursive, frees this when delete_flags bit 0 is set, and returns this. Static metadata only; exact destructor ABI, include-file node layout, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-file-chain", "scalar-deleting-destructor", "recursive-cleanup"
            ),
            spec(
                "0x005896bd",
                "CTexture__DirectiveParserContextCtor",
                true,
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                "Wave680 static read-back: directive-parser context constructor resets status/token-list state, initializes directive/conditional flags, snapshots current LC_NUMERIC locale, forces C locale when needed, saves the prior floating-point control word, and masks floating-point exceptions before returning the context pointer. Static metadata only; exact parser layout, locale/fpu policy, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "directive-parser-context", "constructor", "locale-state", "fpu-control"
            ),
            spec(
                "0x00589762",
                "CTexture__DirectiveParserContextDtor",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                "Wave680 static read-back: directive-parser context destructor releases queued token/payload objects, include-file chain, include context, and include-node chain, restores saved locale when non-C, frees the locale snapshot, restores the saved floating-point control word, and clears token-list buffers. Static metadata only; exact parser layout, locale/fpu policy, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "directive-parser-context", "destructor", "locale-state", "fpu-control", "recursive-cleanup"
            ),
            spec(
                "0x00589802",
                "CTexture__PushPreprocessorStateNode",
                true,
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("state_value", intType), param("unused_context", intType) },
                "Wave680 static read-back: allocates a 0x0c-byte preprocessor state node, stores state_value, links it at context +0x48, mirrors state_value to +0x80, and returns zero or allocation failure. Static metadata only; exact state enum, node layout, runtime conditional behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "preprocessor-state", "allocation", "conditional-frame"
            ),
            spec(
                "0x00589846",
                "CTexture__GetCurrentSourceLocation",
                true,
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("out_primary_location", voidPtr), param("out_secondary_location", voidPtr), param("unused_context", voidPtr) },
                "Wave680 static read-back: copies two source-location fields from the active include context at this+0x54 offsets +0x18/+0x1c into non-null output slots and returns zero. Static metadata only; exact line/column meaning, active-context layout, runtime diagnostic behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "source-location", "diagnostic-context", "preprocessor-context"
            ),
            spec(
                "0x0058986b",
                "CTexture__GetActiveIncludeRange",
                true,
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("out_range_start", voidPtr), param("out_range_length", voidPtr), param("unused_context", voidPtr) },
                "Wave680 static read-back: walks to the terminal child include context through +0x6c, writes the active range start, writes a guarded length when end >= start, and returns zero. Static metadata only; exact range semantics, include-context layout, runtime diagnostic behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "include-context", "source-range", "diagnostic-context"
            ),
            spec(
                "0x005898a4",
                "CTexture__MapLexTokenToPreprocessorToken",
                true,
                "__fastcall",
                intType,
                new ParameterImpl[] { param("directive_parser_context", voidPtr) },
                "Wave680 static read-back: maps the current lexical token record into preprocessor token codes, including operator pairs, defined(), directive keywords, inactive-conditional handling, error/end-token state, and fallback token classes. Static metadata only; exact token enum, parser state layout, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.",
                "signature-hardened", "directive-parser-context", "token-map", "preprocessor-token", "conditional-frame"
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
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave680 apply encountered missing/bad rows");
        }
    }
}
