// Tag-normalize Wave1125 Carver targeting current-risk review rows.
// @category BEA

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

public class ApplyCarverTargetingCurrentRiskWave1125 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final List<String> tags;

        Spec(String address, String name, String signature, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.tags = Arrays.asList(tags);
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1125-carver-targeting-current-risk-review",
        "wave1125-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened",
        "carver-targeting"
    };

    private static final Spec[] SPECS = {
        spec("0x00422db0", "CCarverAI__CheckNearbyEnemies",
            "void __fastcall CCarverAI__CheckNearbyEnemies(void * this)",
            "carver-ai", "nearby-enemy-scan", "mapwho-scan", "last-attack-timestamp"),
        spec("0x00423510", "CCarverGuide__AcquireNearestTargetReader",
            "void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)",
            "carver-guide", "active-reader", "nearest-target-reader", "mapwho-scan")
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

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
            String actualName = function.getName();
            if (!spec.name.equals(actualName)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + actualName);
                specBad = true;
            }

            String actualSignature = function.getSignature().toString();
            if (!spec.signature.equals(actualSignature)) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + actualSignature);
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

            if (missingTags.isEmpty()) {
                println("SKIP: " + spec.address + " " + spec.name + " tags already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (dryRun) {
                println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("TAGGED: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
            updated++;
        }

        if (!dryRun) {
            int verificationFailures = 0;
            for (Spec spec : SPECS) {
                Address address = toAddr(spec.address);
                Function function = functionManager.getFunctionAt(address);
                Set<String> tags = function == null ? new HashSet<String>() : tagNames(function);
                for (String tag : spec.tags) {
                    if (!tags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        verificationFailures++;
                    }
                }
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1125 tag normalization failed: missing=" + missing + " bad=" + bad);
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
