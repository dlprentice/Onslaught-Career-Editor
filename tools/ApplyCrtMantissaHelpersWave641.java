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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtMantissaHelpersWave641 extends GhidraScript {
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
            "crt-mantissa-helpers-wave641",
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
        } else {
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

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType uintPtr = new PointerDataType(uintType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005696e9",
                "CRT__AreHigherMaskBitsClear",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("words96", uintPtr), param("bitIndex", intType)},
                "Wave641 CRT mantissa-helper hardening: tests whether the 96-bit word array has any nonzero bits above the selected bit index, first masking the containing dword and then checking higher dwords through index 2. Called by CRT__BitMaskClearFromIndexWithCarry. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "bit-mask")
            ),
            new Spec(
                "0x00569732",
                "CRT__PropagateMaskCarryBackward",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("words96", uintPtr), param("bitIndex", intType)},
                "Wave641 CRT mantissa-helper hardening: adds the selected mask bit into the containing 96-bit word dword through CRT__UIntAddWithOverflowCheck, then propagates carry backward into lower dword indexes while carry remains set. Called by CRT__BitMaskClearFromIndexWithCarry. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "carry-propagation")
            ),
            new Spec(
                "0x00569788",
                "CRT__BitMaskClearFromIndexWithCarry",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("words96", uintPtr), param("bitIndex", intType)},
                "Wave641 CRT mantissa-helper hardening: clears the selected bit and all lower-order storage after it in a 96-bit mantissa word array; when the selected bit is set and higher bits remain nonzero, it calls the carry-propagation helper before clearing. Direct callers are two rounding sites in CRT__ConvertLongDoubleByFormatSpec. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "bit-mask", "rounding")
            ),
            new Spec(
                "0x00569814",
                "CRT__Copy3DWords",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("destWords96", uintPtr), param("srcWords96", uintPtr)},
                "Wave641 CRT mantissa-helper hardening: copies exactly three dwords from the source 96-bit word array to the destination array. Used by CRT__ConvertLongDoubleByFormatSpec while preserving and restoring mantissa scratch state around rounding/shift paths. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "copy-helper")
            ),
            new Spec(
                "0x0056982f",
                "CRT__Zero3DWords",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("words96", uintPtr)},
                "Wave641 CRT mantissa-helper hardening: zeros exactly three dwords in a 96-bit word array. CRT__ConvertLongDoubleByFormatSpec uses this on underflow/overflow/zero-class paths before packing float32 or float64 output. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "zero-helper")
            ),
            new Spec(
                "0x0056983b",
                "CRT__Are3DWordsZero",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("words96", uintPtr)},
                "Wave641 CRT mantissa-helper hardening: returns nonzero only when all three dwords in the 96-bit word array are zero. CRT__ConvertLongDoubleByFormatSpec uses it to classify an exponent-underflow input with zero mantissa. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "zero-test")
            ),
            new Spec(
                "0x00569856",
                "CRT__ShiftMantissaRight96",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("words96", uintPtr), param("bitCount", uintType)},
                "Wave641 CRT mantissa-helper hardening: shifts a three-dword mantissa word array right by the requested bit count, first carrying bits across adjacent words and then moving whole dwords or zero-filling based on bitCount / 32. CRT__ConvertLongDoubleByFormatSpec uses it before float32/float64 packing. Static long-double mantissa helper evidence only; exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "floating-point", "long-double", "mantissa", "shift-helper")
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
            throw new IllegalStateException("Wave641 had missing/bad rows");
        }
    }
}
