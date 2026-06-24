//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyLifecycleInitCurrentRiskWave1129 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final List<String> tags;

        Spec(String address, String name, String signature, String comment, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = Arrays.asList(tags);
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1129-lifecycle-init-current-risk-review",
        "wave1129-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score-22-current-risk",
        "lifecycle-init-review",
        "tag-normalized"
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x00405970", "CDXCockpit__scalar_deleting_dtor",
            "void * __thiscall CDXCockpit__scalar_deleting_dtor(void * this, byte flags)",
            "Signature correction for CDXCockpit scalar-deleting destructor. Decompile/instruction evidence calls CDXCockpit__dtor_base_thunk, tests the delete flag, optionally calls OID__FreeObject, and returns this. Exact source virtual name, concrete layout, local names, and runtime behavior remain unproven.",
            "cockpit", "cdxcockpit", "scalar-deleting-dtor", "destructor-wrapper", "vtable", "comment-normalized"),
        spec("0x00421a80", "CCarrier__Init",
            "void __thiscall CCarrier__Init(void * this, void * init)",
            null,
            "carrier", "init", "air-unit", "child-helper", "vtable"),
        spec("0x00422440", "CCarver__Init",
            "void __thiscall CCarver__Init(void * this, void * init)",
            null,
            "carver", "init", "air-unit", "guide-helper", "ai-helper", "vtable"),
        spec("0x00422970", "CCarverAI__CanStartAttack",
            "int __fastcall CCarverAI__CanStartAttack(void * this)",
            null,
            "carver", "carver-ai", "attack-predicate", "cooldown", "wing-blend", "vtable"),
        spec("0x00424710", "CCockpit__scalar_deleting_dtor",
            "void * __thiscall CCockpit__scalar_deleting_dtor(void * this, byte flags)",
            "Signature correction for CCockpit scalar-deleting destructor. Decompile/instruction evidence calls CCockpit__dtor_base, tests the delete flag, optionally calls OID__FreeObject, and returns this. Exact source virtual name, concrete layout, local names, and runtime behavior remain unproven.",
            "cockpit", "ccockpit", "scalar-deleting-dtor", "destructor-wrapper", "vtable", "comment-normalized")
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

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int tagsAdded = 0;
        int commentOnlyUpdated = 0;
        int missing = 0;
        int bad = 0;

        for (Spec spec : SPECS) {
            Address address = toAddr(spec.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                missing++;
                continue;
            }

            boolean specBad = false;
            if (!spec.name.equals(function.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
                specBad = true;
            }
            if (!spec.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + function.getSignature());
                specBad = true;
            }
            if (specBad) {
                bad++;
                continue;
            }

            Set<String> existingTags = tagNames(function);
            List<String> missingTags = new ArrayList<>();
            for (String tag : spec.tags) {
                if (!existingTags.contains(tag)) {
                    missingTags.add(tag);
                }
            }

            boolean needsComment = spec.comment != null && !spec.comment.equals(function.getComment());
            if (missingTags.isEmpty() && !needsComment) {
                println("SKIP: " + spec.address + " " + spec.name + " tags/comment already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (needsComment) {
                commentOnlyUpdated++;
            }
            if (dryRun) {
                List<String> changes = new ArrayList<>();
                if (!missingTags.isEmpty()) {
                    changes.add("tags=+" + String.join(",", missingTags));
                }
                if (needsComment) {
                    changes.add("comment");
                }
                println("WOULD_UPDATE: " + spec.address + " " + spec.name + " " + String.join(" ", changes));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            if (needsComment) {
                function.setComment(spec.comment);
            }
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags) + (needsComment ? " comment" : ""));
            updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        }

        if (!dryRun) {
            int verificationFailures = 0;
            for (Spec spec : SPECS) {
                Address address = toAddr(spec.address);
                Function function = functionManager.getFunctionAt(address);
                if (function == null) {
                    println("VERIFY_MISSING: " + spec.address);
                    verificationFailures++;
                    continue;
                }
                Set<String> tags = tagNames(function);
                for (String tag : spec.tags) {
                    if (!tags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        verificationFailures++;
                    }
                }
                if (spec.comment != null && !spec.comment.equals(function.getComment())) {
                    println("VERIFY_BAD_COMMENT: " + spec.address);
                    verificationFailures++;
                }
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + commentOnlyUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1129 lifecycle/init current-risk normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
