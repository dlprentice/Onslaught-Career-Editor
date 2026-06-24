//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.LongLongDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyControlsUiWideFormatWave632 extends GhidraScript {
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
            "controlsui-wide-format-wave632",
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
            stats.signatureUpdated++;
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
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType longLongType = LongLongDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00565083",
                "ControlsUI__FormatWideStringCore",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outputTarget", voidPtr), param("formatWide", shortPtr), param("argList", voidPtr)},
                "Wave632 ControlsUI/wide-format hardening: core wide formatted-output formatter reached from ControlsUI__FormatWideStringSafe. It walks a wide format-state table, consumes width, precision, and value arguments through adjacent 32-bit and 64-bit arg-list readers, emits char/string/integer/padding/sign/prefix cases through the adjacent wide-output helpers, and returns the emitted count or -1 after write failure. Static decompile/xref evidence only; exact CRT variant, full format/locale edge cases, output descriptor layout, runtime ControlsUI text behavior, and rebuild parity remain unproven.",
                tags("controlsui", "wide-format", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x005657d0",
                "ControlsUI__WriteWideCharAndCount",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("wideChar", uintType), param("outputTarget", voidPtr), param("count", intPtr)},
                "Wave632 ControlsUI/wide-format hardening: single wide-character output/count helper used by ControlsUI__FormatWideStringCore and the adjacent repeated/string helpers. It writes through CRT__WriteWideCharToStreamWithConversion, sets count to -1 on 0xffff failure, and increments count on success. Static wide-output evidence only; exact output descriptor layout, conversion edge cases, and rebuild parity remain unproven.",
                tags("controlsui", "wide-output", "format-output", "signature-hardened")
            ),
            new Spec(
                "0x005657f0",
                "ControlsUI__WriteRepeatedWideChar",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("wideChar", uintType), param("repeatCount", intType), param("outputTarget", voidPtr), param("count", intPtr)},
                "Wave632 ControlsUI/wide-format hardening: repeated wide-character padding helper used by ControlsUI__FormatWideStringCore. It emits wideChar through ControlsUI__WriteWideCharAndCount until repeatCount is exhausted or count becomes -1. Static padding/output evidence only; exact output descriptor layout, runtime UI text behavior, and rebuild parity remain unproven.",
                tags("controlsui", "wide-output", "format-output", "padding", "signature-hardened")
            ),
            new Spec(
                "0x00565821",
                "ControlsUI__WriteWideStringAndCount",
                new String[] {"CRT__MapWideCharsWithCallbackStopOnError"},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("wideText", shortPtr), param("wideCharCount", intType), param("outputTarget", voidPtr), param("count", intPtr)},
                "Wave632 ControlsUI/wide-format hardening: bounded wide-string output helper used only by ControlsUI__FormatWideStringCore in current xrefs. It walks wideCharCount 16-bit units from wideText, emits each through ControlsUI__WriteWideCharAndCount, and stops when count becomes -1. Static wide-string output evidence only; exact output descriptor layout, locale/conversion edge cases, and rebuild parity remain unproven.",
                tags("controlsui", "wide-output", "format-output", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x0056585a",
                "CRT__ReadLongLongAndAdvanceArgList",
                new String[] {"CRT__ReadIntAndAdvance8"},
                "__cdecl",
                longLongType,
                new ParameterImpl[] {param("argListPtr", voidPtr)},
                "Wave632 ControlsUI/wide-format hardening: printf-style arg-list reader for 64-bit values. It advances the caller-owned argument cursor by eight bytes and returns the previous 64-bit slot through EDX:EAX; current xrefs are ControlsUI__FormatWideStringCore I64 handling and CRT__FormatOutputToStream. Static vararg-reader evidence only; exact va_list representation, signedness, caller conventions, and rebuild parity remain unproven.",
                tags("crt-runtime", "format-output", "vararg-reader", "name-corrected", "signature-hardened")
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
