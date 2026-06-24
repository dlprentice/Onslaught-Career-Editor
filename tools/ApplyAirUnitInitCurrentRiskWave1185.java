//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyAirUnitInitCurrentRiskWave1185 extends GhidraScript {
    private static final String ADDRESS = "0x00402ad0";
    private static final String NAME = "CAirUnit__Init";
    private static final String SIGNATURE = "void __thiscall CAirUnit__Init(void * this, void * init)";
    private static final String COMMENT =
        "Wave1185 static read-back: CAirUnit init row reached from CCarrier__Init, CDropship__Init, CPlane__Init, CGroundAttackAircraft__Init, and aircraft vtable DATA refs 0x005e3548/0x005e379c. Delegates to CUnit__Init, reads init/profile config at +0x3bc, seeds speed/accel-like fields, builds Trail/Engine particle-node lists via strings 0x00622d14/0x00622cec and CSPtrSet add paths, and links into the air-unit set. Static retail Ghidra metadata/xref/decompile/instruction evidence only; concrete CUnit/CAirUnit/init/profile/particle-node layouts, exact source-body identity, runtime flight/effect behavior, BEA patching, gameplay/visual outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.";
    private static final String[] TAGS = {
        "static-reaudit",
        "wave1185-airunit-init-current-risk-review",
        "wave1185-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "air-unit",
        "lifecycle-init",
        "particle-effect-links",
        "source-identity-deferred",
        "exact-layout-deferred",
        "rebuild-grade-static-contract",
        "comment-hardened",
        "tag-normalized"
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
        Address address = toAddr(ADDRESS);
        Function function = functionManager.getFunctionAt(address);
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        if (function == null) {
            println("MISSING: " + ADDRESS + " " + NAME);
            missing++;
        } else {
            if (!NAME.equals(function.getName())) {
                println("BADNAME: " + ADDRESS + " expected=" + NAME + " actual=" + function.getName());
                bad++;
            }
            if (!SIGNATURE.equals(function.getSignature().toString())) {
                println("BADSIG: " + ADDRESS + " expected=" + SIGNATURE + " actual=" + function.getSignature());
                bad++;
            }

            if (bad == 0) {
                Set<String> actualTags = tagNames(function);
                Set<String> requiredTags = new HashSet<>(Arrays.asList(TAGS));
                requiredTags.removeAll(actualTags);
                boolean commentNeedsUpdate = function.getComment() == null || !COMMENT.equals(function.getComment());
                boolean tagsNeedUpdate = !requiredTags.isEmpty();

                if (!commentNeedsUpdate && !tagsNeedUpdate) {
                    println("SKIP: " + ADDRESS + " " + NAME + " comment/tags already current");
                    skipped++;
                } else if (dryRun) {
                    println("WOULD_UPDATE: " + ADDRESS + " " + NAME + " comment=" + commentNeedsUpdate + " tags=+" + String.join(",", requiredTags));
                    if (commentNeedsUpdate) {
                        commentOnlyUpdated++;
                    }
                    tagsAdded += requiredTags.size();
                } else {
                    if (commentNeedsUpdate) {
                        function.setComment(COMMENT);
                        commentOnlyUpdated++;
                    }
                    for (String tag : requiredTags) {
                        function.addTag(tag);
                    }
                    tagsAdded += requiredTags.size();
                    updated++;
                    currentProgram.flushEvents();
                    Thread.sleep(50L);

                    Function readBack = functionManager.getFunctionAt(address);
                    if (readBack == null) {
                        println("VERIFY_MISSING: " + ADDRESS);
                        bad++;
                    } else {
                        if (!COMMENT.equals(readBack.getComment())) {
                            println("VERIFY_BAD_COMMENT: " + ADDRESS);
                            bad++;
                        }
                        Set<String> readBackTags = tagNames(readBack);
                        for (String tag : TAGS) {
                            if (!readBackTags.contains(tag)) {
                                println("VERIFY_MISSING_TAG: " + ADDRESS + " " + tag);
                                bad++;
                            }
                        }
                    }
                    println("UPDATED: " + ADDRESS + " " + NAME + " comment=" + commentNeedsUpdate + " tags_added=" + requiredTags.size());
                }
            }
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
            throw new IllegalStateException("Wave1185 AirUnit init normalization failed: missing=" + missing + " bad=" + bad);
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
