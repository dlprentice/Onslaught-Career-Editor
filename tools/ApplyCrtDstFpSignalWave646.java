//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyCrtDstFpSignalWave646 extends GhidraScript {
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
            "crt-dst-fp-signal-wave646",
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

    private Spec[] buildSpecs() throws Exception {
        DataType boolType = BooleanDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType doubleType = DoubleDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType uintPtr = new PointerDataType(uintType);
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x0056ce69",
                "CRT__IsInDst_WrapperLocked",
                new String[] {},
                "__cdecl",
                boolType,
                new ParameterImpl[] {
                    param("localTimeFields", voidPtr)
                },
                "Wave646: lock-scoped wrapper around the CRT DST predicate; acquires lock index 0xb, calls CRT__IsInDst for the caller-supplied local-time field record, unlocks, and returns the predicate result.",
                tags("crt-runtime", "timezone", "dst", "locking")
            ),
            new Spec(
                "0x0056ce8a",
                "CRT__IsInDst",
                new String[] {},
                "__cdecl",
                boolType,
                new ParameterImpl[] {
                    param("localTimeFields", voidPtr)
                },
                "Wave646: compares a CRT local-time field record against cached daylight-saving transition year/day/millisecond boundaries, recomputing those boundaries from timezone rule fields when the record year changes.",
                tags("crt-runtime", "timezone", "dst", "local-time")
            ),
            new Spec(
                "0x0056d036",
                "CRT__ComputeDstTransitionDayMillis",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("transitionKind", intType),
                    param("ruleType", intType),
                    param("year", uintType),
                    param("monthIndex", intType),
                    param("weekOfMonth", intType),
                    param("dayOfWeek", intType),
                    param("dayOfMonth", intType),
                    param("hour", intType),
                    param("minute", intType),
                    param("second", intType),
                    param("millisecond", intType)
                },
                "Wave646: computes and caches a DST transition boundary from timezone rule fields; handles nth-weekday versus fixed-day rules, normalizes transition milliseconds across day boundaries, and writes the start/end year, day, and millisecond globals.",
                tags("crt-runtime", "timezone", "dst", "rule-compute")
            ),
            new Spec(
                "0x0056d176",
                "CRT__IsFiniteDoubleWords",
                new String[] {},
                "__cdecl",
                boolType,
                new ParameterImpl[] {
                    param("value", doubleType)
                },
                "Wave646: bitwise finite check for a double, returning false when the exponent bits are all ones for NaN or infinity and true otherwise.",
                tags("crt-runtime", "floating-point", "double-classification")
            ),
            new Spec(
                "0x0056d18a",
                "CRT__ClassifyDoubleWords",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("value", doubleType)
                },
                "Wave646: classifies a double into CRT floating-point status codes, delegating NaN/infinity payload handling to CRT__ClassifyDoubleWordsCore and returning signed zero, denormal, normal, infinite, or NaN class bits.",
                tags("crt-runtime", "floating-point", "double-classification", "fpclass")
            ),
            new Spec(
                "0x0056d21c",
                "CRT__IsDigitCharTypeMask_Thunk",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("charValue", intType)
                },
                "Wave646: digit-test thunk that pushes ctype mask 4 and lead-byte mask zero into CRT__IsCharTypeMaskOrLeadByte, preserving the callee's integer predicate result.",
                tags("crt-runtime", "ctype", "digit", "thunk")
            ),
            new Spec(
                "0x0056d22d",
                "CRT__IsCharTypeMaskOrLeadByte",
                new String[] {"CRT__IsCharTypeMaskOrLeadByte_0056d22d"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("charValue", intType),
                    param("leadByteMask", uintType),
                    param("ctypeMask", intType)
                },
                "Wave646: checks the active CRT ctype byte table for the requested mask and, when provided, falls back to the two-byte lead-byte/codepage mask table before returning a boolean integer.",
                tags("crt-runtime", "ctype", "codepage", "lead-byte")
            ),
            new Spec(
                "0x0056d25e",
                "CRT__MessageBoxA_WithActivePopupFallback",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("messageText", charPtr),
                    param("captionText", charPtr),
                    param("styleFlags", uintType)
                },
                "Wave646: lazily loads user32 MessageBoxA/GetActiveWindow/GetLastActivePopup, resolves the active popup window when possible, and calls MessageBoxA with caller text, caption, and style flags.",
                tags("crt-runtime", "runtime-error", "user32", "MessageBoxA")
            ),
            new Spec(
                "0x0056d2e7",
                "CRT__RaiseSignal",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("signalNumber", intType)
                },
                "Wave646: CRT signal dispatcher that selects global or per-thread signal action slots, handles ignore/default actions, resets one-shot handlers, updates floating-point signal state, invokes the registered callback, and restores saved per-thread state.",
                tags("crt-runtime", "signal", "thread-local", "runtime-error")
            ),
            new Spec(
                "0x0056d469",
                "CRT__FindSignalActionEntry",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("signalNumber", intType),
                    param("signalTable", voidPtr)
                },
                "Wave646: scans a 12-byte CRT signal action table for the requested signal number and returns the matching entry pointer or null when the table range is exhausted.",
                tags("crt-runtime", "signal", "table-scan")
            ),
            new Spec(
                "0x0056d4a6",
                "CRT__UIntAddWithOverflowCheck",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("lhs", uintType),
                    param("rhs", uintType),
                    param("outSum", uintPtr)
                },
                "Wave646: adds two unsigned dwords, writes the sum to outSum, and returns one when the addition wrapped below either operand.",
                tags("crt-runtime", "integer-arithmetic", "overflow", "long-double")
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

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : buildSpecs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
    }
}
