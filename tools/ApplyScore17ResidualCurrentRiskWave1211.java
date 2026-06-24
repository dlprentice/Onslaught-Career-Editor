//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyScore17ResidualCurrentRiskWave1211 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;

        Spec(String address, String name, String signature) {
            this.address = address;
            this.name = name;
            this.signature = signature;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] TAGS = {
        "static-reaudit",
        "wave1211-score17-residual-current-risk-review",
        "wave1211-readback-verified",
        "current-risk-review",
        "retail-binary-evidence",
        "score17-residual",
        "rebuild-grade-static-contract"
    };

    private static final Spec[] SPECS = {
        new Spec("0x00402030", "CActor__StickToGround", "void __thiscall CActor__StickToGround(void * this)"),
        new Spec("0x0040c5b0", "CRepairPadAI__IsWithinRepairBounds", "int __thiscall CRepairPadAI__IsWithinRepairBounds(void * this)"),
        new Spec("0x004d66b0", "CRadarWarningReceiver__Update", "void __fastcall CRadarWarningReceiver__Update(void * this)"),
        new Spec("0x004e97e0", "CGenericActiveReader__SwapWithCandidateIfFormationCloser", "bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser(void * this, void * candidate_reader)"),
        new Spec("0x004e9f00", "CSquadNormal__VFunc_52_004e9f00", "void __fastcall CSquadNormal__VFunc_52_004e9f00(void * this)"),
        new Spec("0x004f45e0", "CComplexThing__SetVar", "void __stdcall CComplexThing__SetVar(void * var_name, void * data)"),
        new Spec("0x0052a830", "CD3DApplication__FindDepthStencilFormat", "bool __thiscall CD3DApplication__FindDepthStencilFormat(void * this, uint adapter_index, int device_type, int target_format, int * out_depth_stencil_format)"),
        new Spec("0x005d06f0", "CRT__InitSehFrameNoop", "void CRT__InitSehFrameNoop(void)")
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
            throw new IllegalStateException("Wave1211 score-17 residual current-risk tag normalization failed: missing="
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
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!spec.name.equals(function.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        if (!spec.signature.equals(function.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address
                + " actual=" + function.getSignature());
        }
        Set<String> existingTags = tagNames(function);
        for (String tag : TAGS) {
            if (!existingTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }
}
