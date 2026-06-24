//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyWave1219FinalScore16CurrentRisk extends GhidraScript {
    private static final class Spec {
        final String address;
        final String name;
        final String signature;

        Spec(String address, String name, String signature) {
            this.address = address;
            this.name = name;
            this.signature = signature;
        }
    }

    private static final class Stats {
        int updated = 0;
        int skipped = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] TAGS = {
        "static-reaudit",
        "retail-binary-evidence",
        "current-risk-review",
        "wave1219-final-score16-current-risk-review",
        "wave1219-readback-verified",
        "final-score16-tail",
        "rebuild-grade-static-contract"
    };

    private static final Spec[] SPECS = {
        new Spec("0x004098e0", "CLine__ctor_copy", "void __thiscall CLine__ctor_copy(void * this, void * sourceLine)"),
        new Spec("0x00414e50", "CBoat__Init", "void __thiscall CBoat__Init(void * this, void * init)"),
        new Spec("0x00415d70", "CBoatGuide__ctor", "void * __thiscall CBoatGuide__ctor(void * this, void * guideOwner)"),
        new Spec("0x00423650", "CFrameTimer__ctor", "void * __fastcall CFrameTimer__ctor(void * this)"),
        new Spec("0x004422d0", "CDebugMarker__ctor", "void * __fastcall CDebugMarker__ctor(void * this)"),
        new Spec("0x004496e0", "CEndLevelData__IsAllSecondaryObjectivesComplete", "bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)"),
        new Spec("0x00488ef0", "CCollisionSeekingThing__ctor_base", "void __fastcall CCollisionSeekingThing__ctor_base(void * this)"),
        new Spec("0x00488f00", "CHLCollisionDetector__ctor_base", "void __fastcall CHLCollisionDetector__ctor_base(void * this)"),
        new Spec("0x004b6cd0", "COggLoader__readerSubobject_dtor_body", "void __fastcall COggLoader__readerSubobject_dtor_body(void * reader_subobject)"),
        new Spec("0x004b6d30", "COggLoader__ctor_base", "void * __fastcall COggLoader__ctor_base(void * this)"),
        new Spec("0x004d1f10", "CPlane__Hit_CheckFatalDamageAndDie", "void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void * this, void * hit_thing, void * hit_context)"),
        new Spec("0x004dea50", "CSentinel__Init", "void __thiscall CSentinel__Init(void * this, void * init_data)"),
        new Spec("0x004f4530", "SharedUnitAnimation__FindAnimationIndexOrZero", "int __thiscall SharedUnitAnimation__FindAnimationIndexOrZero(void * this, void * animation_name)"),
        new Spec("0x004f4560", "SharedUnitAnimation__PlayAnimationByNameIfPresent", "void __thiscall SharedUnitAnimation__PlayAnimationByNameIfPresent(void * this, void * animation_name, int play_flag, int reset_flag)"),
        new Spec("0x00512670", "PCLTShell__ctor", "void * __thiscall PCLTShell__ctor(void * this)"),
        new Spec("0x005245e0", "COggFileRead__scalar_deleting_dtor", "void * __thiscall COggFileRead__scalar_deleting_dtor(void * this, byte flags)")
    };

    @Override
    protected void run() throws Exception {
        boolean dryRun = true;
        String[] args = getScriptArgs();
        if (args.length > 0) {
            String mode = args[0].trim().toLowerCase();
            if ("apply".equals(mode)) {
                dryRun = false;
            } else if (!"dry".equals(mode)) {
                throw new IllegalArgumentException("Expected mode dry|apply, got: " + args[0]);
            }
        }

        Stats stats = new Stats();
        for (Spec spec : SPECS) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=0"
            + " tags_added=" + stats.tagsAdded
            + " tags_removed=0"
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1219 final score16 current-risk tag normalization failed: missing="
                + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function function = functionAtEntry(spec.address);
        if (function == null) {
            println("MISSING: " + spec.address + " " + spec.name);
            stats.missing++;
            return;
        }

        if (!spec.name.equals(function.getName())) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
            stats.bad++;
            return;
        }
        if (!spec.signature.equals(function.getSignature().toString())) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + function.getSignature());
            stats.bad++;
            return;
        }

        Set<String> existingTags = tagNames(function);
        List<String> missingTags = new ArrayList<>();
        for (String tag : TAGS) {
            if (!existingTags.contains(tag)) {
                missingTags.add(tag);
            }
        }

        if (missingTags.isEmpty()) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        stats.tagsAdded += missingTags.size();
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name
                + " missing_tags=" + String.join(",", missingTags));
            return;
        }

        for (String tag : missingTags) {
            function.addTag(tag);
        }
        currentProgram.flushEvents();
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name
            + " tags_added=" + missingTags.size());
        stats.updated++;
        Thread.sleep(50L);
    }

    private Function functionAtEntry(String addressText) {
        Address entry = toAddr(addressText);
        Function function = getFunctionAt(entry);
        if (function != null) {
            return function;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function function = functionAtEntry(spec.address);
        if (function == null) {
            throw new IllegalStateException("Read-back missing: " + spec.address);
        }
        if (!spec.name.equals(function.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address
                + ": " + function.getName());
        }
        if (!spec.signature.equals(function.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address
                + ": " + function.getSignature());
        }
        Set<String> names = tagNames(function);
        for (String tag : TAGS) {
            if (!names.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }
}
