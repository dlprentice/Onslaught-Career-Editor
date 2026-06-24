//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtHeapFpWave628 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                boolean updateSignature,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-heap-fp-wave628",
            "retail-binary-evidence",
            "comment-hardened"
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
        else {
            for (int i = 0; i < spec.parameters.length; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.parameters[i].getDataType().getDisplayName())
                  .append(" ")
                  .append(spec.parameters[i].getName());
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (spec.updateSignature && !fn.getSignature().toString().equals(expectedSignature(spec))) {
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
        if (spec.updateSignature) {
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature);
            }
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
            if (!nameAllowed(fn.getName(), spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                String targetSignature = spec.updateSignature ? expectedSignature(spec) : fn.getSignature().toString();
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + targetSignature);
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " -> " + functionAtEntry(spec.address).getSignature().toString());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0056202e",
                "CRT__ReallocBase",
                new String[] {},
                true,
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("ptr", voidPtr), param("byteCount", uintType)},
                "Wave628 CRT heap/FPU hardening: realloc-family base helper used by onexit-table growth and putenv environment updates. Instruction/decompile read-back shows NULL input delegates to malloc, zero size frees and returns null, and nonzero realloc paths branch across small-block heap modes 3/2 and HeapReAlloc with retry-callback handling. Static CRT heap evidence only; exact small-block heap layout, allocation failure policy, runtime heap behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "signature-hardened")
            ),
            new Spec(
                "0x0056235d",
                "CRT__MsizeByPointer",
                new String[] {},
                true,
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("ptr", voidPtr)},
                "Wave628 CRT heap/FPU hardening: msize-family helper for CRT heap pointers. It locks heap index 9 for small-block heap modes, derives allocation size from the inline block header or small-block page metadata, and falls back to HeapSize for non-small-block pointers. Static CRT heap evidence only; exact SIZE_T width, small-block heap metadata layout, runtime heap behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "signature-hardened")
            ),
            new Spec(
                "0x0056244b",
                "CRT__HandleDomainErrorAndReturnInput",
                new String[] {},
                true,
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("fpStatus", intType), param("inputValue", doubleType), param("controlWord", intType)},
                "Wave628 CRT heap/FPU hardening: domain-error helper reached from double rounding/FPU-check paths. When the math-error hook gate is disabled it forwards sourceKind 1, fpStatus, three double slots, and the control/status word to the adjacent FPU-status double-return helper; otherwise it sets errno to EDOM (0x21), touches the FPU control helper, and returns the input double. Static FPU/errno evidence only; exact CRT matherr identity, control-word semantics, runtime floating-point behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-exception", "errno", "signature-hardened")
            ),
            new Spec(
                "0x005627ea",
                "CRT__AdjustFloatingPointForFormatFlags",
                new String[] {},
                true,
                "__cdecl",
                boolType,
                new ParameterImpl[] {param("activeFlags", uintType), param("inOutDouble", voidPtr), param("controlFlags", uintType)},
                "Wave628 CRT heap/FPU hardening: floating-point adjustment helper for format/exception flags. It masks handled status bits, writes adjusted infinity/underflow/denormal values through inOutDouble, calls CRT__Frexp for denormal scaling, and returns whether all active exception bits were handled. Static FPU-format evidence only; exact flag naming, rounding-mode semantics, runtime floating-point behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-exception", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x00562a01",
                "CRT__HandleFpStatusAndReturnDouble",
                new String[] {"CDXTexture__ValidateSourceAndSetLoadErrorClass"},
                true,
                "__cdecl",
                doubleType,
                new ParameterImpl[] {
                    param("sourceKind", intType),
                    param("fpStatus", intType),
                    param("primaryValue", doubleType),
                    param("replacementValue", doubleType),
                    param("fallbackValue", doubleType),
                    param("controlWord", intType)
                },
                "Wave628 CRT heap/FPU hardening: stale CDXTexture-labeled FPU status helper reached only from CRT floating-point exception/domain paths in this tranche. It maps fpStatus through CRT__MapFpStatusToErrorCode, snapshots three double slots for the qnan/float helper path when mapped status is nonzero, calls the FPU control helper with controlWord, sets errno by sourceKind when needed, and returns either the adjusted local double or fallbackValue. Static FPU/errno evidence only; exact CRT helper identity, qnan helper semantics, runtime FPU behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-exception", "errno", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x00562a89",
                "CRT__SetErrnoForFpSourceKind",
                new String[] {"CDXTexture__SetLoadErrorClassBySourceKind"},
                true,
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("sourceKind", intType)},
                "Wave628 CRT heap/FPU hardening: stale CDXTexture-labeled errno helper for floating-point source classifications. It writes EDOM (0x21) for sourceKind 1 and ERANGE (0x22) for sourceKind 2 or 3 through the CRT thread-local errno pointer, leaving other source kinds unchanged. Static FPU/errno evidence only; exact source-kind enum names, runtime errno behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-exception", "errno", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x00562ab1",
                "CRT__MapFpStatusToErrorCode",
                new String[] {},
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fpStatus", intType)},
                "Wave628 CRT heap/FPU hardening: table-walk mapper from floating-point status value to a paired CRT error/source code. It scans the DAT_00653768 table in 8-byte pairs up to DAT_00653840 and returns the paired value or zero when no status matches. Static FPU table evidence only; exact table ownership, enum names, runtime error semantics, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-exception", "lookup-table", "signature-hardened")
            ),
            new Spec(
                "0x00562ad6",
                "CRT__MapFormatFlagsToSourceKind",
                new String[] {},
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fpFlags", uintType)},
                "Wave628 CRT heap/FPU hardening: maps floating-point format/status flag bits into the sourceKind consumed by the adjacent errno helper. The priority order is bit 0x20 to kind 5, bit 0x8 to kind 1, bit 0x4 to kind 2, bit 0x1 to kind 3, otherwise bit 0x2 maps to kind 4. Static flag-mapping evidence only; exact enum names, CRT version identity, runtime behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-exception", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x00562b15",
                "CRT__BuildNormalizedDoubleFromParts",
                new String[] {},
                true,
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("valueBits", doubleType), param("exponentAdjust", intType)},
                "Wave628 CRT heap/FPU hardening: helper used by CRT__Frexp to rebuild a normalized double from the caller-supplied value bits and exponent adjustment. Instruction read-back loads the input double at [EBP+0x8], preserves sign/mantissa high-word bits, writes a biased exponent into the local double, and returns the rebuilt value in ST0. Static split-double evidence only; exact CRT helper identity, denormal rounding behavior, runtime floating-point behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-classification", "frexp", "signature-hardened")
            ),
            new Spec(
                "0x00562b3e",
                "CRT__ClassifyDoubleWordsCore",
                new String[] {"CFastVB__ClassifyDoubleWords"},
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {param("lowWord", uintType), param("highWord", uintType)},
                "Wave628 CRT heap/FPU hardening: stale CFastVB-labeled double-word classifier reached from CRT rounding helpers and the later CRT__ClassifyDoubleWords wrapper. It returns distinct codes for positive infinity, negative infinity, NaN, other nonzero 0x7ff exponent patterns, and finite/zero values by inspecting the split IEEE-754 low/high words. Static FPU-classification evidence only; exact code enum names, runtime floating-point behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-classification", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x00562b98",
                "CRT__Frexp",
                new String[] {},
                true,
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("value", doubleType), param("outExponent", intPtr)},
                "Wave628 CRT heap/FPU hardening: frexp-family helper used by floating-point format adjustment. It handles zero, normal, and denormal doubles, normalizes denormal mantissas by shifting split words, calls CRT__BuildNormalizedDoubleFromParts for the mantissa result, stores the computed exponent through outExponent, and returns the normalized double in ST0. Static FPU/frexp evidence only; exact CRT version identity, denormal rounding behavior, runtime floating-point behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-classification", "frexp", "signature-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated
                + " skipped=" + stats.skipped
                + " renamed=" + stats.renamed
                + " would_rename=" + stats.wouldRename
                + " signature_updated=" + stats.signatureUpdated
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
