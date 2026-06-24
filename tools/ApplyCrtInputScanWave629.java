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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtInputScanWave629 extends GhidraScript {
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
            "crt-input-scan-wave629",
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

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(expectedSignature(spec));
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
                println("BADNAME: " + spec.address + " expected " + spec.name + " current " + fn.getName());
                return;
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean signatureNeeded = !signatureMatches(fn, spec);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                } else {
                    println("WOULD_UPDATE: " + spec.address + " " + spec.name);
                }
                return;
            }
            if (renameNeeded) {
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
            if (signatureNeeded) {
                stats.signatureUpdated++;
            }
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " -> " + functionAtEntry(spec.address).getSignature().toString());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("ERROR: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00562cef",
                "CRT__InputFormatCore",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("inputStream", voidPtr), param("format", charPtr), param("argList", voidPtr)},
                "Wave629 CRT input-scan hardening: sscanf-style core walks the format string, consumes characters from the input stream descriptor, handles whitespace/literal matching, assignment suppression, width/length modifiers, integer/float/string/char/scanset/n conversions, and advances the vararg cursor. Static CRT input-parser evidence only; exact CRT identity/version, exact FILE/va_list/locale/scanset layouts, runtime scanf behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "scanf-core", "vararg-consumer")
            ),
            new Spec(
                "0x00563714",
                "CRT__NormalizeDigitForBase",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", uintType)},
                "Wave629 CRT input-scan hardening: helper returns decimal digits unchanged and normalizes alphabetic hex digits by uppercasing and subtracting seven, using CRT__GetCharTypeMask_Compat when locale state requires ctype indirection. Static digit-normalization evidence only; exact locale behavior, caller-specific base semantics, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "ctype", "digit-normalization")
            ),
            new Spec(
                "0x0056374b",
                "CRT__GetCharFromStream",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave629 CRT input-scan hardening: decrements the stream descriptor count, returns the next buffered byte when available, advances the cursor, and falls back to CRT__ReadByteWithBufferRefill on underflow. Static stream-input evidence only; exact FILE descriptor layout, EOF/error behavior, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "stream-input")
            ),
            new Spec(
                "0x00563765",
                "CRT__UngetCharIfNotEof",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("charValue", intType), param("stream", voidPtr)},
                "Wave629 CRT input-scan hardening: guards EOF before routing the character back through CRT__UngetCharToStream. Static stream-input evidence only; exact FILE descriptor layout, EOF/error behavior, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "stream-input")
            ),
            new Spec(
                "0x0056377c",
                "CRT__GetNonSpaceCharFromStream",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charsRead", intPtr), param("stream", voidPtr)},
                "Wave629 CRT input-scan hardening: repeatedly increments the consumed-character counter and pulls stream bytes until CRT__IsCharTypeMask0x08 reports a non-whitespace character. Static stream/ctype evidence only; exact FILE descriptor layout, locale whitespace semantics, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "stream-input", "ctype")
            ),
            new Spec(
                "0x0056381b",
                "CRT__EnsureStdStreamBufferForCommitMode",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave629 CRT input-scan hardening: for commit-mode stdout/stderr descriptors, bumps the global buffer-use counter, allocates or reuses a 0x1000-byte buffer when needed, falls back to the inline two-byte buffer on allocation failure, sets stream cursor/count fields, and marks buffering flags. Static CRT stream-buffer evidence only; exact FILE/global layout, runtime buffering behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "stdio-buffer")
            ),
            new Spec(
                "0x005638a8",
                "CRT__FlushStreamIfWritePending",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("enabled", intType), param("stream", voidPtr)},
                "Wave629 CRT input-scan hardening: when enabled and the stream has pending write-buffer state, flushes through CDXTexture__FlushWriteStreamSegment, clears the write/buffer flag bits, and zeroes stream cursor/count/base fields. Static CRT stream-output evidence only; exact FILE layout, runtime flush behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "stdio-buffer")
            ),
            new Spec(
                "0x005638d2",
                "CRT__ParseFloatTextToFloatAndStatus",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("outRecord", voidPtr), param("text", charPtr)},
                "Wave629 CRT input-scan hardening: parses text through the long-double parser, converts successful values to a stored double payload, records overflow/underflow/error status bits, stores the consumed-character count relative to the original text pointer, and writes zero payloads on parse failure. Static float-parser evidence only; exact parse-record layout, locale edge cases, runtime scanf behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "float-parser")
            ),
            new Spec(
                "0x00563951",
                "CRT__GetCharTypeMask_Compat",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", intType), param("mask", intType)},
                "Wave629 CRT input-scan hardening: ctype compatibility helper reads the active ctype table for single-byte values, otherwise prepares a one- or two-byte character buffer for CRT__GetStringTypeACompat, and returns the requested mask bits. This corrects the stale ECX/EDI-inflated signature to the observed two stack arguments. Static ctype/locale evidence only; exact locale table layout, runtime codepage behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "input-scan", "ctype", "signature-corrected")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave629 apply encountered missing/bad rows");
        }
    }
}
