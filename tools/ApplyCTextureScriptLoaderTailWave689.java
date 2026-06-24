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

public class ApplyCTextureScriptLoaderTailWave689 extends GhidraScript {
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
            "ctexture-script-loader-tail-wave689",
            "wave689-readback-verified",
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
                "0x005907d9",
                "CTexture__LoadScriptAndDispatchByVersion",
                "CTexture__LoadScriptAndDispatchByVersion",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("preprocessor_context", voidPtr),
                    param("compile_flags", uintType),
                    param("assembly_fragment_version", uintType),
                    param("out_stream_slot", voidPtr),
                    param("unused_context", voidPtr)
                },
                false,
                "Wave689 static read-back: validates compile flags and out_stream_slot, resets the parser compile context, optionally creates the Wave687 parser-state symbol tables for assembly fragments, reads and normalizes shader-version tokens, maps observed vs/ps version constants to the internal version index, optionally creates the D3D9 shader validator callback, appends version/pending constants, runs the yacc parser, finalizes symbol/debug chunks, writes the constant/script stream to out_stream_slot, releases the validator, and pops the preprocessor frame. Static metadata only; exact compile flag enum, shader-version enum, parser-context layout, D3D validator ABI, output stream contract, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("script-loader", "shader-version", "preprocessor-context", "validator-callback", "constant-stream", "tranche-head")
            ),
            new Spec(
                "0x00590c4a",
                "CTexture__SetQueryStubVtableAndReleaseChild",
                "CTexture__SetQueryStubVtableAndReleaseChild",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("query_stub", voidPtr)
                },
                false,
                "Wave689 static read-back: sets query_stub vtable to PTR_CDXTexture__QueryInterfaceByGuid_005ed3dc and frees the child/callback pointer at query_stub+0x0c through OID__FreeObject_Callback. Static metadata only; exact stub class identity, child ownership contract, allocator provenance, runtime COM behavior, BEA patching, and rebuild parity remain unproven.",
                tags("query-stub", "vtable-reset", "child-release", "memory-stream")
            ),
            new Spec(
                "0x00590cc2",
                "CTexture__Dtor_QueryStub_DeleteOnFlag",
                "CTexture__Dtor_QueryStub_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                false,
                "Wave689 static read-back: scalar-deleting destructor wrapper for the query/memory-stream stub; calls CTexture__SetQueryStubVtableAndReleaseChild, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact destructor ABI, allocation ownership, runtime COM behavior, BEA patching, and rebuild parity remain unproven.",
                tags("query-stub", "scalar-deleting-dtor", "delete-flag", "ret-0x4", "memory-stream")
            ),
            new Spec(
                "0x00590cde",
                "CDXTexture__QueryInterfaceByGuid",
                "CDXTexture__QueryInterfaceByGuid",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("object_stub", voidPtr),
                    param("requested_guid", voidPtr),
                    param("out_interface_slot", voidPtr)
                },
                false,
                "Wave689 static read-back: clears out_interface_slot, compares requested_guid against two observed 16-byte GUID constants, returns E_NOINTERFACE on mismatch, otherwise writes object_stub to the output slot and calls the vtable AddRef-like slot at +0x04. Static metadata only; exact interface identities, COM contract completeness, refcount layout, runtime COM behavior, BEA patching, and rebuild parity remain unproven.",
                tags("query-stub", "query-interface", "guid-compare", "addref", "memory-stream")
            ),
            new Spec(
                "0x00590d25",
                "CTexture__InitMemoryWriteStream",
                "CTexture__InitMemoryWriteStream",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("memory_write_stream", voidPtr)
                },
                false,
                "Wave689 static read-back: initializes the 0x10-byte memory-write stream/query stub by clearing slots +0x08/+0x0c, installing PTR_CDXTexture__QueryInterfaceByGuid_005ed3dc, and setting the refcount-like field at +0x04 to 1. Static metadata only; exact stream object layout, vtable slot meanings, refcount semantics, runtime stream behavior, BEA patching, and rebuild parity remain unproven.",
                tags("memory-stream", "query-stub", "stream-init", "refcount-field")
            ),
            new Spec(
                "0x00590d3d",
                "CTexture__CreateMemoryWriteStream",
                "CTexture__CreateMemoryWriteStream",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("initial_byte_count", intType),
                    param("out_stream_slot", voidPtr)
                },
                false,
                "Wave689 static read-back: validates out_stream_slot, allocates a 0x10-byte memory-write stream/query stub, initializes it, calls the vtable +0x18 stream setup slot with initial_byte_count, releases the stub through vtable +0x14 on setup failure, and writes the stream pointer to out_stream_slot on success. Static metadata only; exact stream capacity contract, vtable ABI, allocator ownership, runtime stream behavior, BEA patching, and rebuild parity remain unproven.",
                tags("memory-stream", "query-stub", "stream-create", "out-stream", "tranche-tail")
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
        println("ApplyCTextureScriptLoaderTailWave689 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave689 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
