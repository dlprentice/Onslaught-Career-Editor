// Normalize Wave1066 CEventManager/CScheduledEvent scheduler review tags.
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

public class ApplyEventManagerSchedulerReviewWave1066 extends GhidraScript {
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
        "event-manager-scheduler-review-wave1066",
        "wave1066-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-reviewed",
        "signature-reviewed",
        "event-manager",
        "scheduler"
    };

    private static final Spec[] SPECS = {
        spec("0x0044afa0", "CEventManager__ctor",
            "void * __fastcall CEventManager__ctor(void * this)",
            "ctor", "csptrset-buckets", "ring-buffer", "source-backed"),
        spec("0x0044afe0", "CEventManager__scalar_deleting_dtor",
            "void * __thiscall CEventManager__scalar_deleting_dtor(void * this, uchar free_flag)",
            "scalar-deleting-dtor", "destructor", "ownership-free"),
        spec("0x0044b000", "CEventManager__dtor",
            "void __fastcall CEventManager__dtor(void * this)",
            "destructor", "shutdown", "csptrset-clear"),
        spec("0x0044b060", "CEventManager__Init",
            "void __fastcall CEventManager__Init(void * this)",
            "init", "event-pool", "free-list", "overflow-list"),
        spec("0x0044b1f0", "CEventManager__Shutdown",
            "void __fastcall CEventManager__Shutdown(void * this)",
            "shutdown", "event-pool", "overflow-list", "resource-release"),
        spec("0x0044b2a0", "CEventManager__GetNextFreeEvent",
            "void * __fastcall CEventManager__GetNextFreeEvent(void * this)",
            "event-pool", "free-list", "fatal-on-exhaustion"),
        spec("0x0044b2d0", "CEventManager__AddEvent_TimeFromNow",
            "void __thiscall CEventManager__AddEvent_TimeFromNow(void * this, float * time_from_now, int event_num, void * to_call, int start_or_end, void * data, void * re_use_event)",
            "add-event", "relative-time", "absolute-time", "source-backed"),
        spec("0x0044b310", "CEventManager__AddEvent_ScheduledEvent",
            "void __thiscall CEventManager__AddEvent_ScheduledEvent(void * this, void * event)",
            "add-event", "scheduled-event", "free-list-return", "relative-time"),
        spec("0x0044b5c0", "CEventManager__Update",
            "void __fastcall CEventManager__Update(void * this)",
            "update", "advance-time", "flush", "frame-tick"),
        spec("0x0044b600", "CEventManager__AdvanceTime",
            "int __fastcall CEventManager__AdvanceTime(void * this)",
            "advance-time", "ring-buffer", "frame-count", "carry-return"),
        spec("0x0044b640", "CEventManager__Flush",
            "void __fastcall CEventManager__Flush(void * this)",
            "flush", "priority-buffer", "overflow-list", "active-reader"),
        spec("0x004de1f0", "CScheduledEvent__Set",
            "void __thiscall CScheduledEvent__Set(void * this, short event_num, float * time, void * to_call, void * data)",
            "scheduled-event", "active-reader", "monitor-pointer", "source-backed"),
        spec("0x004de230", "CScheduledEvent__dtor",
            "void __fastcall CScheduledEvent__dtor(void * this)",
            "scheduled-event", "destructor", "active-reader", "monitor-unlink")
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
            if (!spec.name.equals(function.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
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
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags));
            updated++;
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
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1066 event-manager scheduler tag normalization failed: missing=" + missing + " bad=" + bad);
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
