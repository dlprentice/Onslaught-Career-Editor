//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyActorSoundManagerRawHeadWave827 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "actor-soundmanager-raw-head-wave827",
            "wave827-readback-verified",
            "retail-binary-evidence",
            "comment-hardened"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();
        DataType floatType = FloatDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x004df520",
                "CActor__dtor_base_Thunk",
                "void __fastcall CActor__dtor_base_Thunk(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {},
                "Wave827 static read-back/name correction: this one-instruction CActor destructor thunk jumps to the already-commented CActor__dtor_base body at 0x004013d0, whose decompile resets the primary/secondary CActor vtables and delegates to CComplexThing__dtor_base. Xref evidence comes from CActorBase__shared_scalar_deleting_dtor_004bfd00. Static retail Ghidra evidence only; exact shared-vtable ownership, runtime lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("signature-verified", "name-corrected", "actor", "destructor", "thunk")
            ),
            new Spec(
                "0x004e0300",
                "CSoundManager__UpdateVolumeForAllSoundEvents",
                "void __thiscall CSoundManager__UpdateVolumeForAllSoundEvents(void * this)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {},
                "Wave827 static read-back/name/signature correction: CSoundManager::Init calls this SoundManager method after SetMasterVolume, and the body walks mFirstSoundEvent at this+0x0c, calculates attenuation/fade values, stores current and attenuated volume fields at event+0x68/+0x64, then updates the backend channel through CSoundManager__UpdateChannelParams when the event is playing and has a valid channel. Stuart source names the matching method CSoundManager::UpdateVolumeForAllSoundEvents. Static retail/source evidence only; exact CSoundEvent field schema, backend mixer behavior, runtime audio behavior, BEA patching, and rebuild parity remain deferred.",
                tags("signature-hardened", "name-corrected", "sound-manager", "sound-volume", "sound-event-list")
            ),
            new Spec(
                "0x004e04c0",
                "CSoundManager__SetMasterVolume",
                "void __thiscall CSoundManager__SetMasterVolume(void * this, float volume)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("volume", floatType, currentProgram)
                },
                "Wave827 static read-back: sets the retail SoundManager master-volume field at this+0x20 from the supplied volume, logs the resulting sound master volume, writes CAREER_mSoundVolume, then recomputes all active sound-event volumes through the inlined UpdateVolumeForAllSoundEvents loop. Stuart PC source has a nonlinear tan conversion around mMasterVolume; this retail decompile evidence preserves only the observed Steam-build behavior. Runtime audio output, exact options persistence behavior, BEA patching, and rebuild parity remain deferred.",
                tags("signature-verified", "sound-manager", "master-volume", "career-options", "sound-event-list")
            ),
            new Spec(
                "0x004e06b0",
                "CSoundManager__DeleteAllSamples",
                "void __thiscall CSoundManager__DeleteAllSamples(void * this)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {},
                "Wave827 static read-back/name/signature correction: this SoundManager helper walks the sample list rooted at this+0x00, preserves each next pointer from sample+0x74, calls the sample virtual deleting destructor with flag 1, and clears the first-sample pointer. Stuart source names the matching helper CSoundManager::DeleteAllSamples, and CSoundManager::Shutdown calls it before device shutdown. Static retail/source evidence only; exact CSample layout, backend stream/sample lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("signature-hardened", "name-corrected", "sound-manager", "sample-list", "destructor")
            ),
            new Spec(
                "0x004e06e0",
                "CSoundManager__Shutdown",
                "void __thiscall CSoundManager__Shutdown(void * this)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {},
                "Wave827 static read-back/signature correction: CLTShell shutdown calls this SoundManager teardown. The body returns active events to the pool, frees the event pool, deletes all samples, releases backend voice buffers, frees the debug menu pointer at this+0x10, walks the global CEffect list, and clears the initialized flag at this+0x04. This matches the source-level CSoundManager::Shutdown shape, with retail-specific backend release details. Static retail/source evidence only; exact CSoundEvent/CEffect layouts, runtime audio-device behavior, BEA patching, and rebuild parity remain deferred.",
                tags("signature-hardened", "sound-manager", "shutdown", "sample-list", "effect-list")
            ),
            new Spec(
                "0x004e0820",
                "CEffect__scalar_deleting_dtor",
                "void * __thiscall CEffect__scalar_deleting_dtor(void * this, byte flags)",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    new ParameterImpl("flags", byteType, currentProgram)
                },
                "Wave827 static read-back/name/signature correction: this is the CEffect scalar-deleting destructor wrapper, not a separate CSoundDefinition owner. The body recursively deletes the chained effect at this+0xd4, unlinks this node from the global CEffect list g_pSoundDefinitionListHead using next at this+0xd8, frees this through CDXMemoryManager__Free when flags&1 is set, returns this, and ends with RET 0x4. Stuart source maps those fields to CEffect::mChainedEffect, CEffect::mNextEffect, and CEffect::mFirstEffect. Static retail/source evidence only; exact effect-record schema, .sfx parser ownership, runtime audio behavior, BEA patching, and rebuild parity remain deferred.",
                tags("signature-hardened", "name-corrected", "sound-manager", "effect-list", "scalar-deleting-dtor")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!fn.getSignature().toString().equals(spec.expectedSignature)) {
            return false;
        }
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }

        if (!fn.getName().equals(spec.expectedName)) {
            if (dryRun) {
                println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName);
                stats.wouldRename++;
            } else {
                fn.setName(spec.expectedName, SourceType.USER_DEFINED);
                println("RENAMED: " + spec.address + " " + spec.expectedName);
                stats.renamed++;
            }
        }

        boolean signatureOk = sameSignature(fn, spec);
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasTags(fn, spec.tags);
        if (signatureOk && commentOk && tagsOk) {
            println("SKIP: " + spec.address + " " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY_UPDATE: " + spec.address + " " + spec.expectedName
                + " signature_ok=" + signatureOk + " comment_ok=" + commentOk + " tags_ok=" + tagsOk);
            if (!signatureOk) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.skipped++;
            return;
        }

        if (!signatureOk) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else {
            stats.commentOnlyUpdated++;
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        boolean readbackOk = true;
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
            stats.bad++;
            readbackOk = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            stats.bad++;
            readbackOk = false;
        }
        if (!hasTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            stats.bad++;
            readbackOk = false;
        }
        if (readbackOk) {
            println("READBACK_OK: " + spec.address + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0] : "dry";
        boolean dryRun = isDryRun(mode);
        println("ApplyActorSoundManagerRawHeadWave827 mode=" + (dryRun ? "dry" : "apply"));

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
            throw new IllegalStateException("Wave827 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
