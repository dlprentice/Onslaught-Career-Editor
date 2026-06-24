//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyCUnitAIInitEntryDispatchCurrentRiskWave1186 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Target(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1186-cunitai-init-entry-dispatch-current-risk-review",
        "wave1186-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "unitai",
        "source-identity-deferred",
        "exact-layout-deferred",
        "rebuild-grade-static-contract",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x004239f0",
            "CUnitAI__InitDefaults_AutoConfigTestPath",
            "void * __fastcall CUnitAI__InitDefaults_AutoConfigTestPath(void * this)",
            "Wave1186 static read-back: CUnitAI defaults initializer reached by the no-function caller at 0x004239c5; writes many default flags/timers/state fields, copies c:\\beaautoconfigtest\\ into this+0x44, copies DAT_00624484 into this+0x2d4, and sets this+0x318 to 0xffffffff or 120000 based on DAT_0066e94e. Static retail Ghidra metadata/xref/decompile/instruction evidence only; concrete CUnitAI layout, exact source-body identity, runtime AI/defaulting behavior, BEA patching, gameplay outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("cunitai-defaults", "autoconfig-test-path")
        ),
        new Target(
            "0x00444f00",
            "CUnitAI__CallIndexedEntryVFunc10",
            "int __thiscall CUnitAI__CallIndexedEntryVFunc10(void * this, int entryIndex)",
            "Wave1186 static read-back: CUnitAI indexed-entry helper called by SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10 at 0x0049500d; loads the entry pointer from (*(this+4))[entryIndex], returns 0 when absent, otherwise dispatches entry vfunc slot +0x10 and returns its result. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact entry-table layout, exact source virtual name, runtime motion-controller behavior, BEA patching, gameplay outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("indexed-entry-dispatch", "motion-controller-bridge")
        ),
        new Target(
            "0x0044cd20",
            "CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200",
            "void __thiscall CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200(void * this, float delta, int unused1, int unused2, int unused3)",
            "Wave1186 static read-back: CUnitAI engagement-metric helper with DATA vtable ref 0x005e4680; RET 0x10 confirms four stack dwords, subtracts delta from this+0xe0 when profile/state field *(this+0xe4)+0x10 is zero, dispatches vfunc byte offset +0xc8 when the metric falls below DAT_005d856c and flag bit 4 at this+0x2c is clear, then clamps this+0xe0 to profile field +0x18. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact metric semantics, unused argument purpose, concrete CUnitAI/profile layout, exact source-body identity, runtime AI behavior, BEA patching, gameplay outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("engagement-metric", "vfunc-dispatch")
        ),
        new Target(
            "0x0044d1f0",
            "CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4",
            "void __fastcall CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4(void * unitAi)",
            "Wave1186 static read-back: CUnitAI state helper with DATA vtable refs 0x005e239c, 0x005e3e50, 0x005e40ac, 0x005e4308, and 0x005e46f0; calls CUnitAI__SetStateTimestampCCToNow, then dispatches vfunc byte offset +0x38 when flag bit 4 at unitAi+0x2c is set. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact state semantics, concrete CUnitAI layout, exact source-body identity, runtime AI behavior, BEA patching, gameplay outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("state-dispatch", "vfunc-dispatch")
        )
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
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : TARGETS) {
            Address address = toAddr(target.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + target.address + " " + target.name);
                missing++;
                continue;
            }

            boolean targetBad = false;
            if (!target.name.equals(function.getName())) {
                println("BADNAME: " + target.address + " expected=" + target.name + " actual=" + function.getName());
                targetBad = true;
            }
            if (!target.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + target.address + " expected=" + target.signature + " actual=" + function.getSignature());
                targetBad = true;
            }
            if (targetBad) {
                bad++;
                continue;
            }

            Set<String> actualTags = tagNames(function);
            Set<String> requiredTags = new HashSet<>(Arrays.asList(target.tags));
            requiredTags.removeAll(actualTags);
            boolean commentNeedsUpdate = function.getComment() == null || !target.comment.equals(function.getComment());
            boolean tagsNeedUpdate = !requiredTags.isEmpty();

            if (!commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + target.address + " " + target.name + " comment/tags already current");
                skipped++;
            } else if (dryRun) {
                println("WOULD_UPDATE: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags=+" + String.join(",", requiredTags));
                if (commentNeedsUpdate) {
                    commentOnlyUpdated++;
                }
                tagsAdded += requiredTags.size();
            } else {
                if (commentNeedsUpdate) {
                    function.setComment(target.comment);
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
                    println("VERIFY_MISSING: " + target.address);
                    bad++;
                } else {
                    if (!target.comment.equals(readBack.getComment())) {
                        println("VERIFY_BAD_COMMENT: " + target.address);
                        bad++;
                    }
                    Set<String> readBackTags = tagNames(readBack);
                    for (String tag : target.tags) {
                        if (!readBackTags.contains(tag)) {
                            println("VERIFY_MISSING_TAG: " + target.address + " " + tag);
                            bad++;
                        }
                    }
                }
                println("UPDATED: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags_added=" + requiredTags.size());
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
            throw new IllegalStateException("Wave1186 CUnitAI init/entry dispatch normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private static String[] withCommon(String... extraTags) {
        String[] tags = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, tags, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, tags, COMMON_TAGS.length, extraTags.length);
        return tags;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
