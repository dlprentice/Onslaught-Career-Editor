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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFatalErrorSpineWave998 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
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
        int noReturnUpdated = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
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

    private Address addr(String value) {
        if (!value.startsWith("0x") && !value.startsWith("0X")) {
            value = "0x" + value;
        }
        Address address = toAddr(value);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + value);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            fn = getFunctionContaining(entry);
            if (fn != null && !fn.getEntryPoint().equals(entry)) {
                fn = null;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private boolean hasTag(Function fn, String tag) {
        return fn.getTags().stream().anyMatch(existing -> existing.getName().equals(tag));
    }

    private String expectedSignature(Spec spec) {
        StringBuilder builder = new StringBuilder();
        builder.append("noreturn ")
            .append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                builder.append(", ");
            }
            builder.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        builder.append(")");
        return builder.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsNoReturn = !fn.hasNoReturn();
            boolean needsComment = !spec.comment.equals(fn.getComment());
            int missingTags = 0;
            for (String tag : spec.tags) {
                if (!hasTag(fn, tag)) {
                    missingTags++;
                }
            }
            boolean needsSignatureShape = !fn.getSignature().toString().equals(expectedSignature(spec));
            boolean needsUpdate = needsNoReturn || needsComment || missingTags > 0 || needsSignatureShape;

            if (dryRun) {
                println("DRY: " + spec.address
                    + " " + spec.name
                    + " expected=" + expectedSignature(spec)
                    + " current=" + fn.getSignature().toString()
                    + " needsNoReturn=" + needsNoReturn
                    + " needsComment=" + needsComment
                    + " missingTags=" + missingTags
                    + " needsSignatureShape=" + needsSignatureShape);
                stats.skipped++;
                if (needsNoReturn || needsSignatureShape) {
                    stats.noReturnUpdated++;
                } else if (needsComment || missingTags > 0) {
                    stats.commentOnlyUpdated++;
                }
                stats.tagsAdded += missingTags;
                return;
            }

            if (needsSignatureShape) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            if (needsNoReturn) {
                fn.setNoReturn(true);
                stats.noReturnUpdated++;
            }
            if (needsComment) {
                fn.setComment(spec.comment);
                if (!needsNoReturn && !needsSignatureShape) {
                    stats.commentOnlyUpdated++;
                }
            }
            for (String tag : spec.tags) {
                if (!hasTag(fn, tag)) {
                    fn.addTag(tag);
                    stats.tagsAdded++;
                }
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!readBack.hasNoReturn()) {
                throw new IllegalStateException("Read-back noReturn mismatch at " + spec.address);
            }
            if (!readBack.getSignature().toString().equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature().toString());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            for (String tag : spec.tags) {
                if (!hasTag(readBack, tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }
            if (needsUpdate) {
                stats.updated++;
            } else {
                stats.skipped++;
            }
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fatal-error",
            "fatal-controller-wave327",
            "fatal-error-spine-review-wave998",
            "wave998-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "no-return"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0042c750",
                "FatalError__ExitWithLocalizedPrefix_A",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("message", charPtr), param("callerContext", intType)},
                "Wave998 fatal-error spine correction: localized fatal wrapper A builds a 400-byte message from localization id 0xcc, separator string 0x00624624, and caller message text, then unconditionally exits through noreturn FatalError__ExitProcess. RET 0x8/metadata still prove two stack arguments; current decompile does not show callerContext used by the body. Runtime fatal behavior, exact source identity, full format ownership, and rebuild parity remain unproven.",
                tags("localized-prefix", "two-argument-wrapper")
            ),
            new Spec(
                "0x0042d0b0",
                "FatalError__ExitWithLocalizedPrefix_B",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("message", charPtr)},
                "Wave998 fatal-error spine correction: localized fatal wrapper B builds the same localization id 0xcc plus separator-string prefix and caller message text, then unconditionally exits through noreturn FatalError__ExitProcess. RET 0x4/metadata still prove the single message stack argument and xrefs tie this variant to mesh/resource deserialize paths. Runtime fatal behavior, exact source identity, full format ownership, and rebuild parity remain unproven.",
                tags("localized-prefix", "single-argument-wrapper")
            ),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " no_return_updated=" + stats.noReturnUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave998 fatal-error spine correction failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
