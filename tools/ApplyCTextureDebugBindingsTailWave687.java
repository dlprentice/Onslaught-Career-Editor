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

public class ApplyCTextureDebugBindingsTailWave687 extends GhidraScript {
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
            "ctexture-debug-bindings-tail-wave687",
            "wave687-readback-verified",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0058eefb",
                "CTexture__ParseDebugChunkAndRelocateBindings",
                "CTexture__ParseDebugChunkAndRelocateBindings",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("texture_compile_context", voidPtr)
                },
                false,
                "Wave687 static read-back: builds a DBGU owned-node list, finds binding records from the compile-context +0x34 list with kind 0x11, allocates relocation arrays, registers serialized chunks for debug/binding metadata, reserves and shifts pending constant-stream dwords, relocates binding offsets against the +0x68 debug insertion point, serializes debug symbol records, updates +0x5c/+0x64/+0x68 counts, and emits diagnostic 0x7ee when debug info exceeds 0x8000 dwords. Static metadata only; exact DBGU/debug chunk schema, binding-record layout, compile-context field names, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("debug-chunk", "dbgu-chunk", "binding-relocation", "constant-stream", "diagnostic-0x7ee", "tranche-head")
            ),
            new Spec(
                "0x0058f1e0",
                "CTexture__Dtor_ReleaseBindings_DeleteOnFlag",
                "CTexture__Dtor_ReleaseBindings_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                false,
                "Wave687 static read-back: destructor wrapper for a binding/node record; calls CTexture__DestroyNodeAndBindingsRecord, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, and returns this. Static metadata only; exact record class identity, allocation ownership, caller lifetime contract, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("binding-record", "destructor-wrapper", "delete-flag", "node-cleanup")
            ),
            new Spec(
                "0x0058f1fc",
                "CDXTexture__ReleaseTexturePointerArray7",
                "CDXTexture__ReleaseTexturePointerArray7",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("texture_pointer_array7", voidPtr)
                },
                false,
                "Wave687 static read-back: iterates exactly seven pointer slots, calls CTexture__Dtor_ReleaseBindings_DeleteOnFlag(slot, 1) for each non-null entry, and leaves slot clearing to the destructor/free path. Static metadata only; exact table owner, slot type, lifetime contract, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("binding-record", "seven-slot-array", "destructor-loop", "symbol-table-release")
            ),
            new Spec(
                "0x0058f219",
                "CTexture__CreateStreamAndWriteConstantTable",
                "CTexture__CreateStreamAndWriteConstantTable",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_memory_stream", voidPtr)
                },
                false,
                "Wave687 static read-back: creates a memory-write stream sized from pending constant count +0x5c multiplied by four, copies the constant dword buffer from +0x58 into the stream backing memory, stores the stream pointer through out_memory_stream, and returns the allocation/creation HRESULT. Static metadata only; exact memory-stream ABI, constant-stream schema, stream ownership, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constant-stream", "memory-write-stream", "stream-materialization", "pending-constant-buffer")
            ),
            new Spec(
                "0x0058f270",
                "CTexture__InsertSymbolNodeInHashTable",
                "CTexture__InsertSymbolNodeInHashTable",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("identifier_text", charPtr),
                    param("payload_record", voidPtr),
                    param("symbol_kind", intType)
                },
                false,
                "Wave687 static read-back: hashes identifier_text with CTexture__HashIdentifierMod7, copies the null-terminated identifier into owned storage, allocates a 0x24-byte symbol node, stores the copied name, payload_record, symbol_kind, and previous bucket head at +0x20, then inserts the node at the selected seven-bucket table head or returns the observed out-of-memory HRESULT. Static metadata only; exact symbol-node class, payload-record layout, symbol kind enum, hash-table owner, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("symbol-hash-table", "identifier-copy", "bucket-insert", "allocation", "hresult")
            ),
            new Spec(
                "0x0058f305",
                "CTexture__InitSymbolHashTables",
                "CTexture__InitSymbolHashTables",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("symbol_table_context", voidPtr)
                },
                false,
                "Wave687 static read-back: zeros three adjacent seven-bucket symbol hash tables at +0x00, +0x1c, and +0x38, clears bookkeeping fields at +0x54/+0x58/+0x5c/+0x60, and returns the symbol_table_context pointer. Static metadata only; exact context class, bucket ownership, bookkeeping field names, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("symbol-hash-table", "three-table-init", "seven-bucket-table", "context-init")
            ),
            new Spec(
                "0x0058f331",
                "CTexture__ReleaseSymbolHashTables",
                "CTexture__ReleaseSymbolHashTables",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("symbol_table_context", voidPtr)
                },
                false,
                "Wave687 static read-back: releases the three seven-slot symbol hash tables at +0x38, +0x1c, and +0x00 by calling CDXTexture__ReleaseTexturePointerArray7 for each table. Static metadata only; exact context class, release ordering contract, node ownership, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("symbol-hash-table", "three-table-release", "seven-slot-array", "binding-record")
            ),
            new Spec(
                "0x0058f577",
                "CTexture__Dtor_ReleaseParserState_DeleteOnFlag",
                "CTexture__Dtor_ReleaseParserState_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                false,
                "Wave687 static read-back: parser-state destructor wrapper that calls CTexture__ReleaseSymbolHashTables, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, and returns this; it is reached from LoadScript cleanup and parser compile-context teardown. Static metadata only; exact parser-state class identity, grammar/context layout, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("parser-state", "destructor-wrapper", "symbol-table-release", "delete-flag")
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
        println("ApplyCTextureDebugBindingsTailWave687 mode=" + (dryRun ? "dry" : "apply"));
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
