//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCSoundManagerSamplePlaybackWave501 extends GhidraScript {
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
            "csoundmanager-wave501",
            "retail-binary-evidence",
            "source-parity",
            "audio",
            "sound-manager",
            "sample-playback",
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

    private ParameterImpl[] playNamedParams(DataType voidPtr, DataType charPtr, DataType intType, DataType floatType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("sample_name", charPtr),
            param("owner", voidPtr),
            param("volume", floatType),
            param("tracking_type", intType),
            param("once", intType),
            param("fade_seconds", floatType),
            param("from_point_seconds", floatType),
            param("to_point_seconds", floatType),
            param("repeat", intType),
            param("pitch", floatType),
            param("inform_owner_when_complete", intType),
            param("ignore_owner_pos", intType),
            param("sound_type", intType)
        };
    }

    private ParameterImpl[] playSampleParams(DataType voidPtr, DataType intType, DataType floatType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("sample", voidPtr),
            param("owner", voidPtr),
            param("volume", floatType),
            param("tracking_type", intType),
            param("once", intType),
            param("fade_seconds", floatType),
            param("from_point_seconds", floatType),
            param("to_point_seconds", floatType),
            param("repeat", intType),
            param("pitch", floatType),
            param("inform_owner_when_complete", intType),
            param("ignore_owner_pos", intType),
            param("sound_type", intType)
        };
    }

    private ParameterImpl[] startEventParams(DataType voidPtr, DataType intType, DataType floatType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("owner", voidPtr),
            param("sample", voidPtr),
            param("tracking_type", intType),
            param("volume", floatType),
            param("fade_seconds", floatType),
            param("from_point_seconds", floatType),
            param("to_point_seconds", floatType),
            param("loop", intType),
            param("pitch", floatType),
            param("inform_owner_when_complete", intType),
            param("ignore_owner_pos", intType),
            param("sound_type", intType)
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004dff30",
                "CSample__ctor_like_004dff30",
                "CSample__DestructorBody",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave501 name/signature/comment hardening: this is the CSample destructor body, not a constructor. The retail body installs the CSample vtable, walks active sound events whose sample pointer equals this, invokes owner-complete/channel-release/active-reader clear behavior, then unlinks this sample from the global first-sample list at DAT_00896988. Static retail/source evidence only; exact CSample/CPCSoundManager ownership split, runtime sample unload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "sample-lifecycle", "destructor")
            ),
            new Spec(
                "0x004dffc0",
                "CSample__VFunc_00_004dffc0",
                "CSample__DeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", intType), param("unused", intType)},
                "Wave501 name/signature/comment hardening: CSample vtable 0x005dee6c slot 0 points here. The body duplicates the destructor cleanup path, stops events referencing this sample with block_until_stopped=1, unlinks the sample from the global first-sample list, frees this through CDXMemoryManager__Free when delete_flags bit 0 is set, and returns this; the second stack slot is preserved as unused because the retail epilogue/signature shape carried it before hardening. Static retail/source evidence only; exact compiler destructor flavor, allocator ownership, runtime sample unload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "sample-lifecycle", "deleting-destructor", "vtable")
            ),
            new Spec(
                "0x004e0890",
                "CSoundManager__CreateSample",
                "CSoundManager__CreateSample",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("name", charPtr),
                    param("channel_type", intType),
                    param("sample_source", voidPtr),
                    param("reuse_existing", intType)
                },
                "Wave501 signature/comment/tag hardening: source-aligns to CSoundManager sample creation with retail PC backend differences. The body chooses sounds/music path context from channel_type, optionally reuses an existing sample with the same name, creates the backend sample through CPCSoundManager__CreateSampleFromFile, stores channel_type and default flags, copies the name into the sample+0x08 buffer, links new samples into the manager first-sample list, and marks _L/_R suffixes as stereo side variants. Static retail/source evidence only; exact backend sample-source type, concrete CSample layout typing, runtime file loading behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sample-create", "pc-sound")
            ),
            new Spec(
                "0x004e0a00",
                "CSoundManager__GetOrCreateSample",
                "CSoundManager__GetOrCreateSample",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("name", charPtr),
                    param("channel_type", intType),
                    param("reload_if_exists", intType)
                },
                "Wave501 signature/comment/tag hardening: source-aligns to CSoundManager::GetSample with retail reload-if-existing behavior. The body requires the manager initialized flag at this+0x04 and a non-empty sample name, scans the first-sample list for a case-insensitive name match, returns the existing sample unless reload_if_exists is set, and otherwise gates creation through the retail load-allowed globals before calling CSoundManager__CreateSample. Static retail/source evidence only; exact globals, sample list layout typing, runtime loading behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sample-lookup", "sample-create")
            ),
            new Spec(
                "0x004e0a90",
                "CSoundManager__PlayNamedSample",
                "CSoundManager__PlayNamedSample",
                "__thiscall",
                voidType,
                playNamedParams(voidPtr, charPtr, intType, floatType),
                "Wave501 signature/comment/tag hardening: source-aligns to CSoundManager::PlayNamedSample. RET 0x34 proves the full source-style stack argument payload after this; the body checks the initialized flag, resolves the sample through CSoundManager__GetOrCreateSample(this, sample_name, 0, 0), forwards the remaining playback arguments to CSoundManager__PlaySample when found, and logs an error if lookup fails. Static retail/source evidence only; exact argument enum values, runtime playback behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("playback-wrapper", "sample-lookup")
            ),
            new Spec(
                "0x004e0b30",
                "CSoundManager__PlaySample",
                "CSoundManager__PlaySample",
                "__thiscall",
                voidType,
                playSampleParams(voidPtr, intType, floatType),
                "Wave501 signature/comment/tag hardening: source-aligns to CSoundManager::PlaySample. RET 0x34 proves the full source-style stack argument payload after this; the body checks manager initialization, suppresses non-repeat samples during GAME_STATE_PRE_RUNNING, optionally rejects duplicate once-only events by sample and owner, then forwards to CSoundManager__StartSoundEvent. The return register can carry incidental event pointers from the callee, but callers in this evidence set use the function as a void playback wrapper. Static retail/source evidence only; runtime once-only/playback behavior, exact layout typing, BEA launch, patching, and rebuild parity remain unproven.",
                tags("playback-wrapper", "start-event-caller")
            ),
            new Spec(
                "0x004e0bd0",
                "CSoundManager__PlaySound",
                "CSoundManager__StartSoundEvent",
                "__thiscall",
                voidPtr,
                startEventParams(voidPtr, intType, floatType),
                "Wave501 name/signature/comment hardening: the older PlaySound label is superseded by source parity with CSoundManager::StartSoundEvent. The retail body allocates a CSoundEvent with insert-at-top when owner is null or owner position is ignored, stores owner/sample/tracking/volume/fade/range/loop/pitch/completion/ignore/sound-type fields, calculates pan and position, deletes too-distant non-looping events back to the pool, computes current volume/attenuated volume, starts an assigned channel through CSoundManager__PlaySoundOnChannel, and returns the event pointer or NULL. Static retail/source evidence only; concrete CSoundEvent layout typing, runtime playback/mixing behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "start-event", "playback-core")
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
            throw new RuntimeException("Wave501 had missing/bad rows");
        }
    }
}
