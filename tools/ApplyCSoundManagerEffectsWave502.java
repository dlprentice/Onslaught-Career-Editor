//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyCSoundManagerEffectsWave502 extends GhidraScript {
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
            "csoundmanager-wave502",
            "retail-binary-evidence",
            "source-parity",
            "audio",
            "sound-manager",
            "effect-playback",
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

    private ParameterImpl[] playEffectParams(DataType voidPtr, DataType intType, DataType floatType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("effect", voidPtr),
            param("owner", voidPtr),
            param("volume", floatType),
            param("tracking_type", intType),
            param("once", intType),
            param("fade_seconds", floatType),
            param("from_point_seconds", floatType),
            param("to_point_seconds", floatType),
            param("repeat", intType),
            param("pitch", floatType),
            param("sound_type", intType),
            param("ignore_owner_pos", intType)
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e00d0",
                "CSoundManager__Init",
                "CSoundManager__Init",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave502 signature/comment/tag hardening: source-aligns to CSoundManager::Init with retail PC differences. The body clears active/sample lists, initializes game/menu/master volumes, loads data\\\\sounds\\\\sounds.sfx through the effect loader, allocates 256 pooled CSoundEvent records, registers the sound debug menu/cvars/playsound command, sets radio/HUD message volume defaults, then calls the PC sound manager init and clears the initialized flag on failure. Static retail/source evidence only; exact CSoundManager layout, PC backend behavior, runtime device initialization, BEA launch, patching, and rebuild parity remain unproven.",
                tags("init", "pc-sound", "event-pool", "cvars")
            ),
            new Spec(
                "0x004e1800",
                "CMonitor__StopSoundEventByOwnerAndName",
                "CSoundManager__StopSample",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("sample_name", charPtr), param("owner", voidPtr)},
                "Wave502 name/signature/comment hardening: source-aligns to CSoundManager::StopSample, not a CMonitor method. The retail body requires the manager initialized flag, walks active sound events, matches playing events by owner reader and sample-name string, invokes completion callback/channel release behavior, clears the playing flag, and clears the active reader. Static retail/source evidence only; exact CSoundEvent layout, callback ownership, runtime stop behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "sample-query", "stop-sample")
            ),
            new Spec(
                "0x004e1880",
                "CMonitor__FindSoundEventByOwnerAndName",
                "CSoundManager__GetSoundEventForThing",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("sample_name", charPtr), param("owner", voidPtr)},
                "Wave502 name/signature/comment hardening: source-aligns to CSoundManager::GetSoundEventForThing, not a CMonitor method. The retail body requires the manager initialized flag, walks active sound events, and returns the first playing event whose owner reader and sample-name string match the supplied owner/name pair. Static retail/source evidence only; exact event lifetime guarantees, CSoundEvent layout, runtime lookup behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "sample-query", "event-lookup")
            ),
            new Spec(
                "0x004e1910",
                "CBattleEngine__FindSoundEventByNameIfEnabled",
                "CSoundManager__GetEffectByName",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("name", charPtr), param("ordinal", intType)},
                "Wave502 name/signature/comment hardening: source-aligns to CSoundManager::GetEffectByName, not BattleEngine. The wrapper checks the manager initialized flag and delegates name/ordinal lookup to the static CEffect list lookup. Static retail/source evidence only; exact CEffect layout, effect-list ownership, runtime lookup behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "effect-lookup")
            ),
            new Spec(
                "0x004e1940",
                "CMonitor__PlayRandomSampleFromChain",
                "CSoundManager__PlayEffect",
                "__thiscall",
                voidType,
                playEffectParams(voidPtr, intType, floatType),
                "Wave502 name/signature/comment hardening: source-aligns to CSoundManager::PlayEffect with an extra retail stack flag preserved by RET 0x30. The body counts a chained CEffect list, randomly selects one entry, scales volume by effect volume, resolves once/looping state, applies pitch variance, sets the language-dependent sample flag, resolves the effect sample through CSoundManager__GetOrCreateSample, forwards to CSoundManager__PlaySample, and clears the language flag. Static retail/source evidence only; exact CEffect layout, enum values, extra retail flag meaning, runtime random selection/playback behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "effect-playback", "chain-random")
            ),
            new Spec(
                "0x004e1ab0",
                "CMonitor__HasAnySoundEventForReaderChain",
                "CSoundManager__IsEffectPlaying",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("effect", voidPtr), param("owner", voidPtr)},
                "Wave502 name/signature/comment hardening: source-aligns to CSoundManager::IsEffectPlaying, not a CMonitor method. The body walks a chained CEffect list and checks active sound events for a playing event whose owner reader matches the supplied owner and whose sample name matches the effect sample name. Static retail/source evidence only; exact CEffect/CSoundEvent layout, runtime playback-state behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "effect-query", "chain-scan")
            ),
            new Spec(
                "0x004e2360",
                "CSoundManager__GetDebugMenuText",
                "CSoundManager__GetDebugMenuText",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("entry_index", intType), param("text", charPtr)},
                "Wave502 signature/comment/tag hardening: source-aligns to CSoundManager::GetDebugMenuText. The body selects the nth active sound event, writes [no sound] when no playing event exists, otherwise formats sample/channel text, appends volume/current-attenuated-volume, and appends tracking-mode owner/dead-target text for no/SIP/follow-dont-die/follow-and-die modes. Static retail/source evidence only; exact debug menu wrapper boundary near 0x004e2500, CSoundEvent layout, runtime visible debug text, BEA launch, patching, and rebuild parity remain unproven.",
                tags("debug-menu", "event-debug-text")
            ),
            new Spec(
                "0x004e2530",
                "CSoundManager__LoadSoundDefinitions",
                "CEffect__LoadSFXFile",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("filename", charPtr)},
                "Wave502 name/signature/comment hardening: source-aligns to static CEffect::LoadSFXFile, not a CSoundManager method. The retail body opens the supplied SFX filename with CDXMemBuffer, skips comment lines, reads version and effect count, allocates 0xDC-byte CEffect records, copies effect/sample/lowpass names, parses volume/falloff/pitch-variance, reads looping/language-dependent flags by version, consumes the comment line, and chains duplicate effect names off the first matching effect while removing duplicates from the main list. Static retail/source evidence only; exact CEffect layout typing, SFX file coverage, runtime parse behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "effect-definition", "sfx-parser")
            ),
            new Spec(
                "0x004e2a90",
                "CSoundManager__FindSoundDefinitionByPathAndIndex",
                "CEffect__GetEffectByName",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("name", charPtr), param("ordinal", intType)},
                "Wave502 name/signature/comment hardening: source-aligns to static CEffect::GetEffectByName. The retail body gates lookup on SOUND initialized state, normalizes repeated backslashes from the supplied name into a local buffer, walks the CEffect main list, compares names case-insensitively, and returns the nth matching effect. Static retail/source evidence only; exact CEffect layout typing, list ownership, runtime lookup behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "effect-lookup", "sfx-parser")
            ),
            new Spec(
                "0x004e2b30",
                "CSoundManager__ReleaseSoundEventNode",
                "CSoundEvent__DestructorBody",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave502 name/signature/comment hardening: source-aligns to CSoundEvent destructor body plus inlined active-reader cleanup, not a CSoundManager release helper. The body unlinks/frees the debug marker at event+0x70 when present, then removes this active reader from its owner deletion-event set if an owner reader is still attached. Static retail/source evidence only; exact CSoundEvent/CActiveReader layout typing, destructor flavor, runtime event deletion behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-corrected", "event-lifecycle", "destructor")
            ),
            new Spec(
                "0x004e2c50",
                "CSoundManager__ReloadLanguageSampleBank",
                "CSoundManager__ReloadLanguageSampleBank",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave502 signature/comment/tag hardening: retail PC language-sample-bank reload helper. When the manager is initialized and the language XAP path differs from this+0x88, the body updates the cached path, traces Loading XAP, moves active sound events back to the pool, stops active voices, deletes all samples, runs memory cleanup, and reloads the compressed sample bank. Static retail/source-adjacent evidence only; exact retail-only source name, CSoundManager/sample layout typing, runtime language reload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("language-audio", "sample-bank", "pc-sound")
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
            throw new RuntimeException("Wave502 had missing/bad rows");
        }
    }
}
