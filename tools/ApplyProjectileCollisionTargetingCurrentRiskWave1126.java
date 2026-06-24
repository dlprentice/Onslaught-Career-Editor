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

public class ApplyProjectileCollisionTargetingCurrentRiskWave1126 extends GhidraScript {
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
        "wave1126-projectile-collision-targeting-current-risk-review",
        "wave1126-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened",
        "current-risk-review",
        "projectile-collision-targeting"
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x00425c60", "CCollisionSeekingRound__FilterCollisionCandidateByTrajectory",
            "bool __thiscall CCollisionSeekingRound__FilterCollisionCandidateByTrajectory(void * this, void * candidateRound)",
            "Wave1126 static read-back: collision-seeking round candidate filter. The body first calls CCollisionSeekingRound__CheckCollisionFlags, rejects the candidate when it shares this round's owner/context at the target slot, checks projectile/target state flags, samples the candidate center position, asks this round for a movement/trajectory vector, and rejects candidates outside the computed trajectory/range test. Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime collision behavior, exact slot source name, concrete CCollisionSeekingRound/CRound/target layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            "collision-seeking-round", "collision-filter", "trajectory-filter", "same-owner-reject", "target-state-filter", "range-test"),
        spec("0x00426920", "CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance",
            "int __thiscall CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance(void * this, void * packedCell)",
            "Wave1126 static read-back: collision-seeking round packed map-cell distance helper. The body selects this round's current map/who cell context, right-shifts either side until the cell depths are comparable, then returns the Chebyshev-style max absolute delta between the scaled packed coordinates. Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime map collision behavior, exact slot source name, concrete CCollisionSeekingRound/map-who cell layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            "collision-seeking-round", "chebyshev-distance", "mapwho-distance", "scaled-cell-distance"),
        spec("0x004daba0", "CRound__FindNearbyHostileWithinProjectileRadius",
            "void * __fastcall CRound__FindNearbyHostileWithinProjectileRadius(void * this)",
            "Wave495 owner/signature/comment correction: register-only ECX receiver is a CRound-style helper that scans CMapWho around this+0x1c/0x20/0x24 with radius from round-config this+0xf0+0x90. It rejects the current target reader at this+0xe8, requires candidate flag bit 0x10 and excludes flag bit 0x04, samples target world position, and returns the first candidate inside radius squared and outside the near-zero threshold. Static retail evidence only; exact source method name, concrete CMapWho/target layout, runtime targeting behavior, and rebuild parity remain unproven.",
            "round", "projectile", "targeting", "mapwho", "radius-query", "nearby-hostile-scan", "spawn-config-callee")
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
        int commentUpdated = 0;
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
            boolean needsComment = !spec.comment.equals(function.getComment());

            if (missingTags.isEmpty() && !needsComment) {
                println("SKIP: " + spec.address + " " + spec.name + " tags/comment already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (needsComment) {
                commentUpdated++;
            }
            if (dryRun) {
                if (!missingTags.isEmpty()) {
                    println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                }
                if (needsComment) {
                    println("WOULD_COMMENT: " + spec.address + " " + spec.name);
                }
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            if (needsComment) {
                function.setComment(spec.comment);
            }
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags) + " comment=" + needsComment);
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
                if (!spec.comment.equals(function.getComment())) {
                    println("VERIFY_COMMENT_FAIL: " + spec.address);
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
            + " comment_only_updated=" + commentUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1126 tag/comment normalization failed: missing=" + missing + " bad=" + bad);
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
