// Tag-normalize Wave1059 collision-seeking round tail review rows.
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

public class ApplyCollisionSeekingRoundTailWave1059 extends GhidraScript {
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
        "collision-seeking-round-tail-review-wave1059",
        "wave1059-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened"
    };

    private static final Spec[] SPECS = {
        spec("0x00425b50", "CCollisionSeekingRound__InitCollisionLineAndSound",
            "void __thiscall CCollisionSeekingRound__InitCollisionLineAndSound(void * this, void * roundConfig)",
            "collision-seeking-round", "line-helper", "init-with-sound", "vtable-slot"),
        spec("0x00425e30", "CCollisionSeekingRound__UpdatePrimarySeekerLeadVector",
            "void * __fastcall CCollisionSeekingRound__UpdatePrimarySeekerLeadVector(void * this)",
            "collision-seeking-round", "primary-seeker", "lead-vector", "vtable-slot"),
        spec("0x00426300", "CMeshCollisionVolume__ScalarDeletingDestructor_00426300",
            "void * __thiscall CMeshCollisionVolume__ScalarDeletingDestructor_00426300(void * this, int deleteFlags)",
            "mesh-collision-volume", "scalar-deleting-destructor", "collision-helper"),
        spec("0x00426370", "CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset",
            "void __thiscall CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset(void * this, void * newSeeker)",
            "collision-seeking-round", "primary-seeker", "helper-replacement", "owner-relative-offset"),
        spec("0x004263f0", "CCollisionSeekingRound__Destructor",
            "void __fastcall CCollisionSeekingRound__Destructor(void * this)",
            "collision-seeking-round", "destructor", "monitor-shutdown"),
        spec("0x00426460", "CCollisionSeekingRound__ScalarDeletingDestructor",
            "void * __thiscall CCollisionSeekingRound__ScalarDeletingDestructor(void * this, int deleteFlags)",
            "collision-seeking-round", "scalar-deleting-destructor", "destructor-wrapper"),
        spec("0x00426480", "CCollisionSeekingRound__SetCollisionMask",
            "void __thiscall CCollisionSeekingRound__SetCollisionMask(void * this, int collisionMask)",
            "collision-seeking-round", "collision-mask", "explicit-mask-flag"),
        spec("0x004264a0", "CCollisionSeekingRound__ResolveRoundCollisionResponse",
            "void __thiscall CCollisionSeekingRound__ResolveRoundCollisionResponse(void * this, void * otherRound)",
            "collision-seeking-round", "collision-response", "delayed-ready-flag", "peer-collision"),
        spec("0x00425a10", "CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
            "bool __thiscall CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags(void * this, void * candidateRound)",
            "infantry-bloke", "collision-filter", "mount-state", "collision-seeking-context"),
        spec("0x00425c60", "CCollisionSeekingRound__FilterCollisionCandidateByTrajectory",
            "bool __thiscall CCollisionSeekingRound__FilterCollisionCandidateByTrajectory(void * this, void * candidateRound)",
            "collision-seeking-round", "trajectory-filter", "collision-filter"),
        spec("0x00426900", "CCollisionSeekingRound__CheckCollisionFlags",
            "bool __thiscall CCollisionSeekingRound__CheckCollisionFlags(void * this, void * candidateRound)",
            "collision-seeking-round", "collision-mask", "flag-filter"),
        spec("0x00426920", "CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance",
            "int __thiscall CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance(void * this, void * packedCell)",
            "collision-seeking-round", "mapwho-distance", "chebyshev-distance"),
        spec("0x00426a00", "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
            "void __thiscall CCollisionSeekingRound__ProcessMapWhoCollisionSweep(void * this, void * startOrContext, void * endOrContext)",
            "collision-seeking-round", "mapwho-sweep", "hlcollisiondetector-bridge"),
        spec("0x00426a20", "CCollisionSeekingRound__MarkDelayedCollisionReady",
            "void __thiscall CCollisionSeekingRound__MarkDelayedCollisionReady(void * this, void * event)",
            "collision-seeking-round", "delayed-ready-flag", "event-callback")
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
            throw new IllegalStateException("Wave1059 tag normalization failed: missing=" + missing + " bad=" + bad);
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
