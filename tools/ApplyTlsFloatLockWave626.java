//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyTlsFloatLockWave626 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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
            "tls-float-lock-wave626",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
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
        if (!fn.getSignature().toString().equals(expectedSignature(spec))) {
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
        String actualSignature = readBack.getSignature().toString();
        String expectedSignature = expectedSignature(spec);
        if (!actualSignature.equals(expectedSignature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature);
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

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00560b2c",
                "CTexture__InitializeThreadLocalState",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: texture/CRT thread-local initialization entry. It initializes four global critical sections, allocates a TLS index, allocates a 0x74-byte per-thread record, stores it with TlsSetValue, seeds defaults through CTexture__InitializeThreadLocalRecordDefaults, writes the current thread id and sentinel state, and returns success/failure. Static TLS-initialization evidence only; exact CRT TLS layout, thread lifetime behavior, and rebuild parity remain unproven.",
                tags("tls-init", "critical-section", "ctexture")
            ),
            new Spec(
                "0x00560b80",
                "CTexture__InitializeThreadLocalRecordDefaults",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("tlsRecord", voidPtr)},
                "Wave626 TLS/float/lock hardening: initializes default fields inside the 0x74-byte TLS record. The current body writes the callback/table pointer at tlsRecord+0x50 to DAT_006560a8 and sets tlsRecord+0x14 to 1. Static TLS-record evidence only; exact record structure naming, callback ownership, and rebuild parity remain unproven.",
                tags("tls-init", "tls-record", "ctexture")
            ),
            new Spec(
                "0x00560b93",
                "CRT__GetOrInitThreadLocalRecord",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: lazy TLS record accessor. It preserves GetLastError, reads the TLS slot, allocates and installs a 0x74-byte record when missing, initializes defaults, writes current thread id and sentinel state, exits with __amsg_exit(0x10) on allocation/TLS failure, restores LastError, and returns the record pointer. Static CRT TLS evidence only; exact record layout, failure UI, and runtime threading behavior remain unproven.",
                tags("tls-init", "tls-record", "crt-runtime")
            ),
            new Spec(
                "0x00560bfa",
                "CDXTexture__InvokeTlsCleanupCallbackAndFinalize",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: TLS cleanup/finalize wrapper. It installs a temporary SEH frame, fetches the TLS record, invokes the callback pointer at record+0x60 when present, marks cleanup state, then routes to CRT__FatalRuntimeErrorAndExit. Static cleanup evidence only; exact callback ownership, exception unwinding behavior, and rebuild parity remain unproven.",
                tags("tls-cleanup", "seh", "cdxtexture")
            ),
            new Spec(
                "0x00560c5b",
                "CDXTexture__InvokeGlobalCleanupCallbackAndFinalize",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: global cleanup/finalize wrapper. It installs a temporary SEH frame, invokes PTR_CDXTexture__InvokeTlsCleanupCallbackAndFinalize_00653654 when present, then falls through to CDXTexture__InvokeTlsCleanupCallbackAndFinalize. Static cleanup evidence only; exact global callback ownership, exception unwinding behavior, and rebuild parity remain unproven.",
                tags("tls-cleanup", "seh", "cdxtexture")
            ),
            new Spec(
                "0x00560cb1",
                "CRT__InitFpuControlWord_0x10000_0x30000",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: compact FPU control-word initializer. It forwards mask/value pair 0x10000/0x30000 to CRT__ControlFpMasked_0056947e. Static FPU-control evidence only; exact CRT startup policy, processor state side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-control")
            ),
            new Spec(
                "0x00560cc3",
                "CDXTexture__ProbeFeatureModuloGate",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: fallback processor-feature probe gate. It compares DAT_005d87e0 against DAT_005e5bb0 modulo DAT_005e5bb8 and returns 1 or 0. Static fallback-probe evidence only; exact feature meaning, entropy/probe intent, and runtime processor behavior remain unproven.",
                tags("processor-feature", "fallback-probe", "cdxtexture")
            ),
            new Spec(
                "0x00560d01",
                "CDXTexture__ProbeProcessorFeaturePresentOrFallback",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: processor feature probe wrapper. It resolves KERNEL32!IsProcessorFeaturePresent dynamically, invokes it with feature id 0 when available, and otherwise calls CDXTexture__ProbeFeatureModuloGate. Static processor-probe evidence only; exact feature policy, platform behavior, and rebuild parity remain unproven.",
                tags("processor-feature", "kernel32", "cdxtexture")
            ),
            new Spec(
                "0x00560d2a",
                "CRT__InsertDecimalSeparatorBeforeExponent",
                new String[] {"CRT__InsertDecimalSeparatorBeforeExponent_00560d2a"},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("text", charPtr)},
                "Wave626 TLS/float/lock hardening: decimal-separator insertion helper for formatted floating-point text. It scans past digit characters until an exponent marker or terminator, writes the locale decimal separator from DAT_00653aa0, then shifts the remainder of the string right one byte. Static float-format evidence only; exact locale table semantics, buffer capacity assumptions, and rebuild parity remain unproven.",
                tags("float-format", "locale-decimal", "name-corrected")
            ),
            new Spec(
                "0x00560dea",
                "__fassign",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("storeFloat", intType), param("outValue", voidPtr), param("numberText", charPtr)},
                "Wave626 TLS/float/lock hardening: Visual Studio 2003 __fassign helper. A nonzero storeFloat path parses numberText through CRT__ParseFloatTextToFloat32 and copies the resulting 8 bytes to outValue; the zero path parses through CRT__ParseFloatTextToFloat64 and stores the resulting double pointer/value slot. Static library-helper evidence only; exact CRT ABI details and runtime conversion edge cases remain unproven.",
                tags("float-parse", "vs2003-crt", "library-match")
            ),
            new Spec(
                "0x00560e28",
                "CRT__FormatFloatScientificFromLongDouble",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("longDoubleValue", voidPtr), param("outBuffer", charPtr), param("precision", intType), param("uppercaseExponent", intType)},
                "Wave626 TLS/float/lock hardening: scientific-format wrapper for a spilled long-double/double value. It converts the value to a decimal record, rounds mantissa digits using precision+1, then emits through CRT__FormatFloatScientificCore. Static float-format evidence only; exact CRT ABI, rounding edge cases, locale behavior, and rebuild parity remain unproven.",
                tags("float-format", "scientific-format", "crt-runtime")
            ),
            new Spec(
                "0x00560e89",
                "CRT__FormatFloatScientificCore",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("outBuffer", charPtr), param("precision", intType), param("uppercaseExponent", intType), param("decimalRecord", voidPtr), param("generalFormatMode", intType)},
                "Wave626 TLS/float/lock hardening: scientific-format core. It optionally shifts mantissa text for general-format mode, writes a negative sign when the decimal record is negative, inserts the locale decimal separator when precision is positive, appends e+000/E+000, and writes exponent digits with sign handling. Static float-format evidence only; exact decimal-record layout, locale behavior, and rebuild parity remain unproven.",
                tags("float-format", "scientific-format", "locale-decimal")
            ),
            new Spec(
                "0x00560f4b",
                "CRT__FormatFloatFixedFromLongDouble",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("longDoubleValue", voidPtr), param("outBuffer", charPtr), param("precision", intType)},
                "Wave626 TLS/float/lock hardening: fixed-format wrapper for a spilled long-double/double value. It converts the value to a decimal record, rounds mantissa digits using exponent plus requested precision, then emits through CRT__FormatFloatFixedCore. Static float-format evidence only; exact CRT ABI, rounding edge cases, locale behavior, and rebuild parity remain unproven.",
                tags("float-format", "fixed-format", "crt-runtime")
            ),
            new Spec(
                "0x00560fa0",
                "CRT__FormatFloatFixedCore",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("outBuffer", charPtr), param("precision", intType), param("decimalRecord", voidPtr), param("generalFormatMode", intType)},
                "Wave626 TLS/float/lock hardening: fixed-format core. It writes a negative sign when needed, ensures a leading zero for nonpositive exponents, inserts the locale decimal separator when precision is positive, shifts text in place through CRT__ShiftStringRightInPlace, and zero-pads fractional gaps. Static float-format evidence only; exact decimal-record layout, locale behavior, and rebuild parity remain unproven.",
                tags("float-format", "fixed-format", "locale-decimal")
            ),
            new Spec(
                "0x00561047",
                "CRT__FormatFloatGeneral_SelectStyle",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("longDoubleValue", voidPtr), param("outBuffer", charPtr), param("precision", intType), param("uppercaseExponent", intType)},
                "Wave626 TLS/float/lock hardening: general-format selector for floating-point output. It converts and rounds the value, then chooses scientific output when exponent-1 is below -4 or not below precision, otherwise trims trailing digit text and emits fixed-format output. Static float-format evidence only; exact CRT ABI, %g edge cases, locale behavior, and rebuild parity remain unproven.",
                tags("float-format", "general-format", "crt-runtime")
            ),
            new Spec(
                "0x0056112b",
                "CRT__ShiftStringRightInPlace",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("text", charPtr), param("count", intType)},
                "Wave626 TLS/float/lock hardening: in-place string right-shift helper used by float-format cores. For nonzero count it measures the NUL-terminated text and calls CRT__MemMoveOverlapSafe(text+count, text, length+1). Static string/format helper evidence only; buffer capacity assumptions and rebuild parity remain unproven.",
                tags("float-format", "string-shift", "memmove")
            ),
            new Spec(
                "0x00561150",
                "CTexture__InitializeGlobalCriticalSections",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave626 TLS/float/lock hardening: initializes four global critical-section slots used by the adjacent TLS/CRT lock setup. The body calls InitializeCriticalSection for PTR_DAT_006536b4, PTR_DAT_006536a4, PTR_DAT_00653694, and PTR_DAT_00653674. Static lock-initialization evidence only; exact lock ownership, lifecycle cleanup, and rebuild parity remain unproven.",
                tags("critical-section", "tls-init", "ctexture")
            ),
            new Spec(
                "0x00561179",
                "CRT__LockByIndex",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("lockIndex", intType)},
                "Wave626 TLS/float/lock hardening: CRT indexed-lock acquisition helper. It lazily allocates a 0x18-byte critical section for DAT_00653670[lockIndex], serializes creation through lock index 0x11, frees the losing allocation if another thread installed the slot first, and enters the selected critical section. Static lock-helper evidence only; exact CRT lock-table layout, thread races, and rebuild parity remain unproven.",
                tags("crt-runtime", "critical-section", "lock-helper")
            ),
            new Spec(
                "0x005611da",
                "CRT__UnlockByIndex",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("lockIndex", intType)},
                "Wave626 TLS/float/lock hardening: CRT indexed-lock release helper. It loads DAT_00653670[lockIndex] and calls LeaveCriticalSection on that slot. Static lock-helper evidence only; exact CRT lock-table layout, invalid-index behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "critical-section", "lock-helper")
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
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
