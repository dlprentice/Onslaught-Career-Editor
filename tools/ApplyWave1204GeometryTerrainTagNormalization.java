// Tag-only normalization for Wave1204 geometry/terrain residual current-risk review.
// Usage: ApplyWave1204GeometryTerrainTagNormalization.java dry|apply

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;

public class ApplyWave1204GeometryTerrainTagNormalization extends GhidraScript {
    private static final class Spec {
        final String address;
        final String name;
        final String[] tags;

        Spec(String address, String name, String[] tags) {
            this.address = address;
            this.name = name;
            this.tags = tags;
        }
    }

    private static final String[] SHADOW_HEIGHTFIELD_TAGS = new String[] {
        "static-reaudit",
        "retail-binary-evidence",
        "comment-hardened",
        "signature-corrected",
        "geometry",
        "terrain-heightfield",
        "shadow-heightfield",
        "static-shadows",
        "current-risk-review",
        "wave1204-geometry-terrain-residual-current-risk-review",
        "wave1204-readback-verified"
    };

    private static final Spec[] SPECS = new Spec[] {
        new Spec(
            "0x00402dd0",
            "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
            SHADOW_HEIGHTFIELD_TAGS
        )
    };

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        boolean apply = "apply".equals(mode);
        boolean dry = "dry".equals(mode) || "check".equals(mode);
        if (!apply && !dry) {
            throw new IllegalArgumentException("Usage: ApplyWave1204GeometryTerrainTagNormalization.java dry|apply");
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;
        int tagsAdded = 0;

        println("MODE: " + (apply ? "apply" : "dry"));
        for (Spec spec : SPECS) {
            Address address = toAddr(spec.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                missing++;
                continue;
            }
            if (!spec.name.equals(function.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
                bad++;
                continue;
            }

            Set<String> currentTags = tagNames(function);
            LinkedHashSet<String> missingTags = new LinkedHashSet<>();
            missingTags.addAll(Arrays.asList(spec.tags));
            missingTags.removeAll(currentTags);

            if (missingTags.isEmpty()) {
                println("SKIP: " + spec.address + " " + spec.name + " tags already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (!apply) {
                println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags));
            updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        }

        if (apply) {
            for (Spec spec : SPECS) {
                Function function = functionManager.getFunctionAt(toAddr(spec.address));
                if (function == null) {
                    println("VERIFY_MISSING: " + spec.address);
                    bad++;
                    continue;
                }
                Set<String> currentTags = tagNames(function);
                for (String tag : spec.tags) {
                    if (!currentTags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        bad++;
                    }
                }
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=0"
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1204 tag normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (apply) {
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
