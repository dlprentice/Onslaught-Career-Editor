//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyCDXMemBufferIoWave606 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "dxmembuffer-io-wave606",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "owner-corrected"
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> readBackTags = tagNames(readBack);
        for (String tag : spec.tags) {
            if (!readBackTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + expectedSignature(spec));
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        VoidDataType voidType = VoidDataType.dataType;
        PointerDataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        IntegerDataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00547d40",
                "CDXMemBuffer__SetBufferSize",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("requested_size", uintType) },
                "Wave606 CDXMemBuffer IO hardening: plain RET plus CMissionScriptObjectCode__LoadAsync callsite read-back proves one caller-popped requested_size argument. The body stores DAT_00650f6c as 0x100000 when requested_size is zero, otherwise rounds requested_size up to a 1 MiB boundary with (requested_size + 0xfffff) & 0xfff00000. Stuart's source has a related SetNextReadBufferSize helper, but this retail body differs from the source default/rounding behavior. Static retail evidence only; exact global ownership, runtime streaming behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__SetBufferSize", "CDXMemBuffer__SetBufferSize"},
                tags("cdxmembuffer", "buffer-size", "ret-c3", "global-read-buffer")
            ),
            new Spec(
                "0x00547dc0",
                "CDXMemBuffer__OpenWrite",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("filename", charPtr),
                    param("mem_type", intType)
                },
                "Wave606 CDXMemBuffer IO hardening: RET 0x8 and callsite read-back prove ECX=this plus filename and mem_type stack arguments. The body allocates a 0x100000-byte write buffer through OID__AllocObject using the retail DXMemBuffer.cpp line 0xe3 site string, records mem_type and filename, opens filename with CreateFileA GENERIC_WRITE/CREATE_ALWAYS/FILE_ATTRIBUTE_NORMAL, frees the buffer on open failure, builds the .crc sidecar name, clears the CRC state slot, and returns AL as success. This corresponds to the retail write/open path rather than the already-refreshed read InitFromFile path. Static retail evidence only; exact CRC semantics, compressed output behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__OpenWrite", "CDXMemBuffer__OpenWrite"},
                tags("cdxmembuffer", "open-write", "ret-0x8", "createfile", "write-buffer")
            ),
            new Spec(
                "0x005482c0",
                "CDXMemBuffer__GetFileSize",
                "__fastcall",
                uintType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave606 CDXMemBuffer IO hardening: plain RET and the CText__Init callsite load ECX with the stack CDXMemBuffer before calling, then use EAX as the allocation size. The body wraps Win32 GetFileSize(this[0], NULL) and returns the API result directly. Static retail evidence only; exact error handling, file-handle lifetime, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__GetFileSize", "CDXMemBuffer__GetFileSize"},
                tags("cdxmembuffer", "file-size", "ret-c3", "win32-file")
            ),
            new Spec(
                "0x00548820",
                "CDXMemBuffer__ReadLine",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("output", charPtr),
                    param("max_chars", intType)
                },
                "Wave606 CDXMemBuffer IO hardening: RET 0x8 and effect/token callsites prove ECX=this plus output and max_chars stack arguments. The body fills output until newline, EOF, or max_chars-1, normalizes CRLF by rewriting the preceding carriage return to newline and appending NUL, updates the position slot at this+0x12c, sets the EOF flag at this+0x24, and refreshes the read buffer through the compressed-extension path when needed. The compressed path checks DAT_006318a0, uses DAT_008c029c scratch storage, calls uncompress, validates CRC side data, and fatal-errors on failed compressed reads. Static retail evidence only; the saved name preserves the line-oriented retail usage, while Stuart's source has a related ReadString helper. Exact compressed block format, CRC semantics, runtime parser behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__ReadLine", "CDXMemBuffer__ReadLine"},
                tags("cdxmembuffer", "read-line", "ret-0x8", "compressed-buffer", "crc-check")
            ),
            new Spec(
                "0x00548a70",
                "CDXMemBuffer__WriteBytes",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("data", voidPtr),
                    param("size", uintType)
                },
                "Wave606 CDXMemBuffer IO hardening: RET 0x8 and memory/controller callsites prove ECX=this plus data and size stack arguments. The body copies bytes into the write buffer, flushes when the requested byte count would overflow the current buffer, writes compressed blocks through compress and DAT_008c029c when the filename matches the compressed extension marker, writes raw buffered data with WriteFile otherwise, logs the Write failed diagnostic on failure, and updates current pointer, buffered byte count, and position slots. Static retail evidence only; Stuart's source has a related Write helper, but exact compression/CRC side effects, flush boundaries, runtime output format, BEA patching, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__WriteBytes", "CDXMemBuffer__WriteBytes"},
                tags("cdxmembuffer", "write-bytes", "ret-0x8", "compressed-buffer", "writefile")
            ),
            new Spec(
                "0x00548d30",
                "CDXMemBuffer__IsEOF",
                "__fastcall",
                boolType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave606 CDXMemBuffer IO hardening: plain RET and callsites in CEffect__LoadSFXFile, CConsole__ExecScript, and CPCController__ReadControllerState prove an ECX-only state query. The body returns the dword EOF flag stored at this+0x24. Static retail evidence only; the saved name preserves the observed EOF query role, while Stuart's source has a related EndOfFile helper. Exact read-state transitions, runtime parser behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__IsEOF", "CDXMemBuffer__IsEOF"},
                tags("cdxmembuffer", "eof", "ret-c3", "read-state")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad == 0 && stats.missing == 0) {
                println("REPORT: Save succeeded");
            } else {
                println("REPORT: Save blocked by bad/missing rows");
            }
        } else {
            println("REPORT: Save succeeded");
        }
    }
}
