//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.DeleteFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.DataType;
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

public class ApplyCDXSnowBoundaryWave615 extends GhidraScript {
    private static class Spec {
        final String startAddress;
        final String staleAddress;
        final String endAddress;
        final String nextAddress;
        final String staleName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String startAddress,
                String staleAddress,
                String endAddress,
                String nextAddress,
                String staleName,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.startAddress = startAddress;
            this.staleAddress = staleAddress;
            this.endAddress = endAddress;
            this.nextAddress = nextAddress;
            this.staleName = staleName;
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
        int renamed = 0;
        int wouldRename = 0;
        int created = 0;
        int wouldCreate = 0;
        int deleted = 0;
        int wouldDelete = 0;
        int bodySet = 0;
        int wouldSetBody = 0;
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

    private Function functionAtEntry(Address address) {
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
            "cdxsnow-boundary-wave615",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "boundary-corrected",
            "vtable-verified"
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

    private boolean needsBodySet(Function fn, Spec spec) {
        return !fn.getBody().contains(addr(spec.staleAddress)) || !fn.getBody().contains(addr(spec.endAddress));
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
        if (!hasAllTags(fn, spec.tags)) {
            return true;
        }
        return needsBodySet(fn, spec);
    }

    private void setBody(Function fn, Spec spec) throws Exception {
        AddressSet body = new AddressSet(addr(spec.startAddress), addr(spec.endAddress));
        fn.setBody(body);
    }

    private void applyMetadata(Function fn, Spec spec, Stats stats) throws Exception {
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsBodySet(fn, spec)) {
            setBody(fn, spec);
            stats.bodySet++;
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
    }

    private Function createFunctionAt(Spec spec) throws Exception {
        Address start = addr(spec.startAddress);
        Address end = addr(spec.endAddress);
        AddressSet range = new AddressSet(start, end);
        DisassembleCommand disassemble = new DisassembleCommand(start, range, true);
        disassemble.applyTo(currentProgram, monitor);
        Function fn = createFunction(start, spec.name);
        if (fn == null) {
            fn = functionAtEntry(start);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.startAddress);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        setBody(fn, spec);
        return fn;
    }

    private void deleteStaleFunction(Spec spec) throws Exception {
        Address stale = addr(spec.staleAddress);
        Function staleFn = getFunctionAt(stale);
        if (staleFn == null) {
            return;
        }
        if (!staleFn.getName().equals(spec.staleName)) {
            throw new IllegalStateException(
                "Unexpected stale-entry function at " + spec.staleAddress + ": " + staleFn.getName());
        }
        DeleteFunctionCmd delete = new DeleteFunctionCmd(stale, true);
        boolean removed = delete.applyTo(currentProgram);
        if (!removed) {
            throw new IllegalStateException(
                "Failed to remove stale function at " + spec.staleAddress + ": " + delete.getStatusMsg());
        }
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Address start = addr(spec.startAddress);
        Address stale = addr(spec.staleAddress);
        Address end = addr(spec.endAddress);
        Address next = addr(spec.nextAddress);
        Function readBack = functionAtEntry(start);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.startAddress);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.startAddress + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.startAddress + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.startAddress);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.startAddress);
        }
        if (!readBack.getBody().contains(stale)) {
            throw new IllegalStateException("Read-back body does not contain stale split address " + spec.staleAddress);
        }
        if (!readBack.getBody().contains(end)) {
            throw new IllegalStateException("Read-back body does not contain terminal RET " + spec.endAddress);
        }
        Function staleEntry = getFunctionAt(stale);
        if (staleEntry != null && !staleEntry.getEntryPoint().equals(start)) {
            throw new IllegalStateException("Stale split address is still a separate function entry: " + staleEntry.getName());
        }
        Function staleContaining = getFunctionContaining(stale);
        if (staleContaining == null || !staleContaining.getEntryPoint().equals(start)) {
            throw new IllegalStateException("Stale split address is not contained by corrected function");
        }
        Function nextFn = getFunctionAt(next);
        if (nextFn == null) {
            throw new IllegalStateException("Next function missing at " + spec.nextAddress);
        }
        if (readBack.getBody().contains(next)) {
            throw new IllegalStateException("Corrected body overlaps next function at " + spec.nextAddress);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address start = addr(spec.startAddress);
            Address stale = addr(spec.staleAddress);
            Function startFn = functionAtEntry(start);
            Function containingStart = getFunctionContaining(start);
            if (containingStart != null && !containingStart.getEntryPoint().equals(start)) {
                stats.bad++;
                println("BAD: " + spec.startAddress + " is inside " + containingStart.getName());
                return;
            }

            Function staleEntry = getFunctionAt(stale);
            if (startFn == null) {
                if (staleEntry == null) {
                    stats.missing++;
                    println("MISSING: corrected entry absent and stale split entry absent");
                    return;
                }
                if (!staleEntry.getName().equals(spec.staleName)) {
                    stats.bad++;
                    println("BADNAME: stale " + spec.staleAddress + " actual=" + staleEntry.getName() + " expected=" + spec.staleName);
                    return;
                }
                if (dryRun) {
                    stats.wouldDelete++;
                    stats.wouldCreate++;
                    stats.wouldSetBody++;
                    stats.skipped++;
                    println("DRYBOUNDARY: delete " + spec.staleAddress + " " + spec.staleName
                        + "; create " + expectedSignature(spec)
                        + " body=" + spec.startAddress + "-" + spec.endAddress);
                    return;
                }
                deleteStaleFunction(spec);
                stats.deleted++;
                Function created = createFunctionAt(spec);
                stats.created++;
                stats.bodySet++;
                applyMetadata(created, spec, stats);
                verifyReadBack(spec);
                stats.updated++;
                println("OKBOUNDARY: " + spec.startAddress + " " + expectedSignature(spec)
                    + " deleted_stale=" + spec.staleAddress + " created=true");
                Thread.sleep(50);
                return;
            }

            if (staleEntry != null && !staleEntry.getEntryPoint().equals(start)) {
                stats.bad++;
                println("BAD: stale split entry still exists at " + spec.staleAddress + " name=" + staleEntry.getName());
                return;
            }

            if (!needsUpdate(startFn, spec)) {
                verifyReadBack(spec);
                stats.skipped++;
                println("SKIP: " + spec.startAddress + " " + expectedSignature(spec));
                return;
            }

            if (dryRun) {
                if (!startFn.getName().equals(spec.name)) {
                    stats.wouldRename++;
                }
                if (needsBodySet(startFn, spec)) {
                    stats.wouldSetBody++;
                }
                stats.skipped++;
                println("DRY: " + spec.startAddress + " " + startFn.getSignature()
                    + " -> " + expectedSignature(spec));
                return;
            }

            applyMetadata(startFn, spec, stats);
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.startAddress + " " + expectedSignature(spec));
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.startAddress + " " + spec.name + " "
                + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec spec = new Spec(
            "0x00555020",
            "0x0055515e",
            "0x00555403",
            "0x00555410",
            "CDXSnow__Init",
            "CAtmosphericsProfile__ResetAndInitSnowResources",
            "__thiscall",
            voidType,
            new ParameterImpl[] { param("this", voidPtr) },
            "Wave615 boundary correction: vtable 0x005e5974 slot +0x0c points to 0x00555020, and Atmospherics__ResetAndUpdate dispatches that slot. The old 0x0055515e CDXSnow__Init row had no xrefs and began mid-body after the SEH prologue/resource setup; this function now covers 0x00555020-0x00555403, including the old address, CVBufTexture snow allocation at this+0x8, cg_snow_* console-variable registration, snow quad/index population, and resource cleanup/reinit flow. Static retail evidence only; exact source method name, concrete CAtmosphericsProfile/CDXSnow layout, runtime snow behavior, BEA patching, and rebuild parity remain unproven.",
            tags("catmospherics-profile", "snow", "resource-init", "seh-prologue")
        );

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        applySpec(spec, dryRun, stats);
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " deleted=" + stats.deleted +
            " would_delete=" + stats.wouldDelete +
            " body_set=" + stats.bodySet +
            " would_set_body=" + stats.wouldSetBody +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
