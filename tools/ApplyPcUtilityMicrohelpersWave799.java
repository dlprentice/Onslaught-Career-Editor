//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyPcUtilityMicrohelpersWave799 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, boolean updateSignature, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
        int commentOnlyUpdated = 0;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "pc-utility-microhelpers-wave799",
            "wave799-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "pc-utility-microhelper"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.updateSignature) {
            return true;
        }
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

    private String expectedSignature(Spec spec) {
        if (!spec.updateSignature) {
            return "<unchanged signature>";
        }
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
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        String readComment = fn.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
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
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }

            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(spec.comment)
                || !hasAllTags(fn, spec.tags);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                else if (commentOrTagsNeedUpdate) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            if (signatureNeedsUpdate) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            if (!signatureNeedsUpdate) {
                stats.commentOnlyUpdated++;
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x00441730",
                "CLIParams__SetField04",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("field04_value", intType)
                },
                "Wave799 static read-back: CLIParams field+4 setter reached from CLIParams__ParseCommandLine at 0x004240a0. Instruction evidence loads the single stack argument from [ESP+4], stores it to [ECX+4], and returns with RET 0x4, so the older unused_flags parameter was a phantom signature artifact. Stuart source layout suggests field +4 aligns with CCLIParams::mNoStaticShadows after mArtistTest, but retail field identity and runtime CLI effects remain unproven. Static retail Ghidra evidence only; exact field ownership, runtime command-line behavior, BEA patching, and rebuild parity remain deferred.",
                tags("tranche-head", "cli-params", "signature-corrected", "ret-0x4")
            ),
            new Spec(
                "0x00441b10",
                "CGame__SetGlobalSelectionSnapshot",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave799 static read-back: screen-dump selection snapshot helper called by CFrontEnd__Render, CGame__Update, and CGame__DrawGameStuff. Non-null input copies four dwords into globals 0x0066eb80 through 0x0066eb8c; null input writes the 0xffffffff sentinel at 0x0066eb84 and clears 0x0066eb80. Both paths set pending flag byte 0x0066ff74 and mode byte 0x0066ff75 from the selection_mode argument. Static retail Ghidra evidence only; exact global ownership, runtime screenshot behavior, BEA patching, and rebuild parity remain deferred.",
                tags("game-screenshot", "selection-snapshot", "global-state")
            ),
            new Spec(
                "0x00441b80",
                "Platform__ProcessPendingScreenDump",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave799 static read-back: pending screen-dump processor called by PCPlatform__DeviceFlip at 0x005158fb. The body checks flag byte 0x0066ff74, formats numbered DDS/BMP dump names from counter 0x0066ff78, uses the selection snapshot around 0x0066eb80 as an optional fallback, calls Direct3D surface/save helper paths, prints CConsole status/error messages, increments the dump counter, and clears the pending flag. Stuart source has LT.DumpScreen/PCLTShell::DumpScreen screen-capture context, but this retail helper's exact source identity and runtime filesystem/GPU behavior remain unproven. Static retail Ghidra evidence only; BEA patching and rebuild parity remain deferred.",
                tags("platform", "screen-dump", "device-flip")
            ),
            new Spec(
                "0x00441e20",
                "CDXFrontEndVideo__ClearByteFlag",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave799 static read-back: byte-flag clear microhelper called by CDXFrontEndVideo__Render at 0x005418f2. Instruction evidence writes zero to the byte pointed to by ECX and returns; the caller context ties it to front-end video render state, but the exact owning field offset is not proven by this helper alone. Static retail Ghidra evidence only; runtime Bink/video behavior, BEA patching, and rebuild parity remain deferred.",
                tags("frontend-video", "byte-flag", "render-helper")
            ),
            new Spec(
                "0x00441e30",
                "CDXFrontEndVideo__SetByteFlagAndReturnOld",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave799 static read-back: byte-flag set microhelper called by CDXFrontEndVideo__Render at 0x00541909. Instruction evidence reads the old low byte at [ECX], writes 1 to [ECX], and returns with the old byte in AL; upper EAX bits are not semantically proven. Static retail Ghidra evidence only; exact owning field offset, runtime Bink/video behavior, BEA patching, and rebuild parity remain deferred.",
                tags("frontend-video", "byte-flag", "render-helper")
            ),
            new Spec(
                "0x00441e40",
                "CGame__ClearDwordValue",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave799 static read-back: dword clear microhelper called by CGame__InitRestartLoop at 0x0046c57d. Instruction evidence writes zero to the dword pointed to by ECX and returns; the narrow read-back proves the clear operation but not the owning CGame field identity. Static retail Ghidra evidence only; exact field ownership, runtime restart-loop behavior, BEA patching, and rebuild parity remain deferred.",
                tags("game", "restart-loop", "dword-clear", "tranche-tail")
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

        println("ApplyPcUtilityMicrohelpersWave799 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave799 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
