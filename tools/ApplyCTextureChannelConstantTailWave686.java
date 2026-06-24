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

public class ApplyCTextureChannelConstantTailWave686 extends GhidraScript {
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
            "ctexture-channel-constant-tail-wave686",
            "wave686-readback-verified",
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
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0058e256",
                "CTexture__ParseChannelMaskStrict",
                "CTexture__ParseChannelMaskStrict",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("token_record", voidPtr),
                    param("unused_context", intType)
                },
                false,
                "Wave686 static read-back: parses a channel mask string from token_record+0x08, accepts ordered x/y/z/w or r/g/b/a components, sets bitfields 0x10000/0x20000/0x40000/0x80000, returns default mask 0xf0000 for empty input, and reports diagnostic 0x7d3 for invalid or out-of-order masks. Static metadata only; exact channel-mask enum ownership, token-record layout, shader ABI layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("channel-mask", "parser-token", "shader-component-mask", "diagnostic-0x7d3", "tranche-head")
            ),
            new Spec(
                "0x0058e309",
                "CTexture__ParseSwizzleMask",
                "CTexture__ParseSwizzleMask",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("token_record", voidPtr),
                    param("unused_context", intType)
                },
                false,
                "Wave686 static read-back: parses up to four swizzle characters from token_record+0x08, accepts x/y/z/w or r/g/b/a aliases, packs two-bit component selectors starting at bit 0x10, returns default swizzle 0xe40000 for empty input, and reports diagnostic 0x7d4 for invalid forms. Static metadata only; exact swizzle enum ownership, token-record layout, shader ABI layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("swizzle-mask", "parser-token", "shader-component-mask", "diagnostic-0x7d4", "shader-operand")
            ),
            new Spec(
                "0x0058e3c3",
                "CTexture__FlushPendingConstantTableWrites",
                "CTexture__FlushPendingConstantTableWrites",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_location", voidPtr),
                    param("unused_context", intType)
                },
                false,
                "Wave686 static read-back: if pending constant dwords remain between +0x64 and +0x5c, records source_location at +0x30, calls the writer vtable slot at +0x10 using source_location+0x10/+0x14, flushes the pending dword span from +0x58, marks +0x4c/+0x50 on failure, and advances +0x64 to the current +0x5c count. Static metadata only; exact writer ABI, context field names, constant-stream format, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constant-stream", "pending-constant-flush", "writer-vtable", "source-location", "error-flag")
            ),
            new Spec(
                "0x0058e413",
                "CTexture__EnsurePendingConstantCapacity",
                "CTexture__EnsurePendingConstantCapacity",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("additional_dword_count", intType),
                    param("unused_context", intType)
                },
                false,
                "Wave686 static read-back: grows the pending constant dword array at +0x58 when +0x5c plus additional_dword_count exceeds capacity +0x60, starts empty capacity at 0x100 dwords, doubles capacity until large enough, copies existing dwords, frees the old buffer, and returns the observed out-of-memory HRESULT. Static metadata only; exact allocator ownership, constant-buffer field names, capacity limit policy, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constant-stream", "capacity-growth", "pending-constant-buffer", "allocator", "hresult")
            ),
            new Spec(
                "0x0058e491",
                "CTexture__AppendPendingConstantEntry",
                "CTexture__AppendPendingConstantEntry",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("constant_dword", intType),
                    param("unused_context", intType)
                },
                false,
                "Wave686 static read-back: ensures capacity for one pending constant dword, writes constant_dword into the array at +0x58 indexed by +0x5c, increments the pending count, and propagates allocation failure. Static metadata only; exact constant dword meaning, buffer ownership, caller ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constant-stream", "pending-constant-append", "capacity-growth", "shader-constant", "hresult")
            ),
            new Spec(
                "0x0058e4b5",
                "CTexture__ValidateInstructionOperandsAndReserveConstantSlots",
                "CTexture__ValidateInstructionOperandsAndReserveConstantSlots",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("instruction_record", voidPtr),
                    param("unused_context", uintType)
                },
                false,
                "Wave686 static read-back: validates instruction_record operands against shader version, fragment-linker, predicate, relative-addressing, destination/source modifier, and SUB modifier rules, reserves pending constant slots through CTexture__EnsurePendingConstantCapacity, emits packed instruction and operand dwords into +0x58, flushes constants when no relative-address sentinel is present, and reports diagnostics such as 0x7d7, 0x7d8, 0x7d9, 0x7dd, and 0x7e3-0x7ea. Static metadata only; exact instruction enum, operand-node layout, shader ABI encoding, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constant-stream", "instruction-operand-validation", "shader-version-gates", "relative-addressing", "diagnostic-report")
            ),
            new Spec(
                "0x0058ecdb",
                "CTexture__FinalizeSymbolTablesIntoConstantStream",
                "CTexture__FinalizeSymbolTablesIntoConstantStream",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("constant_stream_context", voidPtr)
                },
                false,
                "Wave686 static read-back: initializes a FINF owned-node list, flattens three symbol hash tables through CDXTexture__CollectHashBucketsToArray, sorts the combined node array, allocates 0x14-byte records per symbol, emits serialized chunks, inserts debug-comment dwords at the front of the pending constant stream, updates +0x5c/+0x68/+0x64 counts, reports diagnostic 0x7ef when fragment info exceeds 0x8000 dwords, and frees temporary arrays/lists. Static metadata only; exact FINF/debug chunk schema, symbol-record layout, serialized chunk ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constant-stream", "symbol-table-finalize", "finf-chunk", "debug-comment", "serialized-chunk")
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
        println("ApplyCTextureChannelConstantTailWave686 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave686 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
