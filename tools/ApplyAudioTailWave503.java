//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyAudioTailWave503 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String newName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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
        int created = 0;
        int wouldCreate = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "audio-tail-wave503",
            "retail-binary-evidence",
            "audio",
            "sound-manager",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.newName)
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
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
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e1200",
                "CMessageBox__StopAndReleaseChannel",
                "CSoundManager__KillAllInstancesOfSample",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("sample", voidPtr)},
                "Wave503 name/signature/comment hardening: source-aligns to CSoundManager::KillAllInstancesOfSample, not a CMessageBox channel helper. The retail body walks active sound events, matches event+0x0c against the supplied sample pointer, invokes owner completion callback when requested, stops any assigned backend channel with blocking stop, clears the playing flag, and clears the active reader. Static retail/source evidence only; exact CSoundEvent/sample/backend-channel layout, runtime sample shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "source-parity", "sample-lifecycle", "event-stop")
            ),
            new Spec(
                "0x004e2bb0",
                "CUnit__BuildVoiceXapPathIfChanged",
                "CSoundManager__BuildLanguageSampleBankPathIfChanged",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("out_path", charPtr)},
                "Wave503 name/signature/comment hardening: retail PC language sample-bank path helper, not a CUnit voice helper. The body requires the sound manager initialized flag, formats the current language XAP path as <root>/data/sounds/sounds_<language>_pc.xap, compares it with the cached path at this+0x88, optionally copies the new path to out_path, and returns true only when the path changed. Static retail evidence only; exact CSoundManager path-buffer layout, CText language source, runtime language switching behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "language-audio", "sample-bank", "pc-sound")
            ),
            new Spec(
                "0x004e2e60",
                "CUnit__PlayImpactSoundForMaterials",
                "CUnit__PlayImpactSoundForMaterials",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("primary_unit", voidPtr), param("secondary_unit", voidPtr)},
                "Wave503 signature/comment hardening: impact-material sound-effect dispatcher. The retail body rejects null inputs, queries both objects through vtable slot +0xac for material ids, uses the lower/higher material ids to select either impact_Wood or hit_%d effect names, resolves the effect through CSoundManager__GetEffectByName, then plays it on the primary object through CSoundManager__PlayEffect with fixed volume/tracking parameters. Static retail evidence only; exact source owner, material enum names, vtable slot identity, runtime collision/impact sound behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("impact-sound", "material-sound", "effect-playback")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave503 had missing/bad rows");
        }
    }
}
