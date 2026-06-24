//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyTokenArchiveWave518 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "tokenarchive-wave518",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "particle-config"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f52b0",
                "CTokenArchive__GetTokenName",
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("token_id", intType)},
                "Wave518 TokenArchive signature/comment hardening: maps token_id 0..0x7b to particle-configuration token strings and returns the \"**Unknown Token**\" fallback for out-of-range ids. Callers include CTokenArchive__ReadNextToken and the token writer helpers. Static retail evidence only; exact enum naming, runtime parser coverage, and rebuild parity remain unproven.",
                tags("token-name", "token-table")
            ),
            new Spec(
                "0x004f57b0",
                "CTokenArchive__ReadNextToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_token_id", intPtr),
                    param("out_int_or_ref_index", intPtr),
                    param("out_float", new PointerDataType(floatType)),
                    param("out_string", charPtr)
                },
                "Wave518 TokenArchive signature/comment hardening: reads a token line through CTokenArchive__ReadLine, scans token/value text, searches the 0..0x7b token-name table, writes out_token_id, and parses integer, float, string, and reference-token forms into caller-provided outputs. Reference tokens allocate string storage under this+0x9c4c and increment the pending-reference count at +0x8; colour tokens 0x31..0x39 apply the 1/255 normalization constant. Static retail evidence only; concrete CTokenArchive layout, full token enum semantics, runtime particle parsing, and rebuild parity remain unproven.",
                tags("parser", "reference-fixup", "token-reader")
            ),
            new Spec(
                "0x004f5b80",
                "CTokenArchive__RegisterReferenceFixup",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("ref_value", intType),
                    param("slot_index", intType),
                    param("fixup_record", voidPtr)
                },
                "Wave518 TokenArchive signature/comment correction: ret 0x0c proves three stack arguments, so the stale fourth parameter is removed. The body stores ref_value into fixup_record, then stores fixup_record+4 into the per-slot fixup-target table at this+0x0c+(slot_index*4). Static retail evidence only; exact fixup-record layout, owner lifetimes, and runtime parser behavior remain unproven.",
                tags("reference-fixup", "stale-param-correction")
            ),
            new Spec(
                "0x004f5ba0",
                "CTokenArchive__ResolveReferences",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("list_head_ptr", voidPtr)},
                "Wave518 TokenArchive signature/comment hardening: counts the linked list reached through list_head_ptr, allocates a temporary pointer array, resolves each stored reference string through CTokenArchive__BinarySearchByPredicate, writes the resolved object pointer or null into the paired fixup target, frees each stored string and the temporary array, then resets the pending-reference count at +0x8. Static retail evidence only; concrete list item layout, comparison predicate semantics, runtime particle linking, and rebuild parity remain unproven.",
                tags("reference-fixup", "resolver")
            ),
            new Spec(
                "0x004f5c90",
                "CTokenArchive__WriteInt",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("token_id", intType), param("value", intType)},
                "Wave518 TokenArchive signature/comment hardening: ret 0x8 proves a callee-cleaned two-argument helper. The body fetches the token name with CTokenArchive__GetTokenName and formats a 400-byte local line with \"%s %d\" for integer token output. Static retail evidence only; final archive sink and runtime write coverage remain unproven.",
                tags("token-writer", "integer")
            ),
            new Spec(
                "0x004f5cd0",
                "CTokenArchive__WriteFloat",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("token_id", intType), param("value", floatType)},
                "Wave518 TokenArchive signature/comment hardening: ret 0x8 proves a callee-cleaned two-argument helper. The body fetches the token name with CTokenArchive__GetTokenName and formats a 400-byte local line with \"%s %f\" for float token output. Static retail evidence only; final archive sink and runtime write coverage remain unproven.",
                tags("float", "token-writer")
            ),
            new Spec(
                "0x004f5d10",
                "CTokenArchive__WriteString",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("token_id", intType), param("value", charPtr)},
                "Wave518 TokenArchive signature/comment hardening: ret 0x8 proves a callee-cleaned two-argument helper. The body fetches the token name with CTokenArchive__GetTokenName and formats a 400-byte local line with \"%s %s\" for string token output. Static retail evidence only; final archive sink and runtime write coverage remain unproven.",
                tags("string", "token-writer")
            ),
            new Spec(
                "0x004f5d50",
                "CTokenArchive__WritePointer",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("token_id", intType), param("named_object", voidPtr)},
                "Wave518 TokenArchive signature/comment hardening: ret 0x8 proves a callee-cleaned two-argument helper. Null named_object formats \"%s NONE\"; non-null named_object formats \"%s %s\" using the string at named_object+4. Static retail evidence only; concrete named-object layout, final archive sink, and runtime write coverage remain unproven.",
                tags("pointer-reference", "token-writer")
            ),
            new Spec(
                "0x004f5dc0",
                "CTokenArchive__WriteFloatPointer",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("token_id", intType), param("value_ref_record", voidPtr)},
                "Wave518 TokenArchive signature/comment hardening: ret 0x8 proves a callee-cleaned two-argument helper. The record supplies a float at +0 and an optional named-object pointer at +4; null object formats \"%s %f NONE\", while non-null object formats \"%s %f %s\" using the string at object+4. Static retail evidence only; concrete record layout, final archive sink, and runtime write coverage remain unproven.",
                tags("float", "pointer-reference", "token-writer")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
