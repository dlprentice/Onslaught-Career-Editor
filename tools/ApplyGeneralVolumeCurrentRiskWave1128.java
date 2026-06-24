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

public class ApplyGeneralVolumeCurrentRiskWave1128 extends GhidraScript {
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
        "wave1128-generalvolume-current-risk-review",
        "wave1128-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score-22-current-risk",
        "general-volume",
        "tag-normalized"
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x00402020", "CGeneralVolume__ResetCooldownTimestamp",
            "void __thiscall CGeneralVolume__ResetCooldownTimestamp(void * this, void * activeReaderTarget)",
            "Signature correction: instruction evidence shows ret 0x4 and one activeReaderTarget stack argument; body ignores that argument and stores DAT_00672fd0 into this+0xd4. Exact source identity, concrete layout, local names, runtime behavior, and rebuild parity remain unproven.",
            "cooldown-reset", "active-reader-target", "comment-normalized"),
        spec("0x0040b100", "CGeneralVolume__ctor_base",
            "void __fastcall CGeneralVolume__ctor_base(void * generalVolume)",
            "Owner/name correction: body installs the CGeneralVolume vtable and zeroes +0x4/+0x8/+0xc; ResolveVtableTypeNames confirms CGeneralVolume RTTI at vtable 0x005d892c. Runtime behavior, concrete layout, exact constructor/source identity, locals, and rebuild parity remain unproven.",
            "constructor", "vtable", "comment-normalized"),
        spec("0x0040c720", "CGeneralVolume__ResetAndSetActiveReader",
            "void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, void * activeReaderTarget)",
            "Signature correction: instruction evidence shows ret 0x4 and one activeReaderTarget stack argument; body swaps reader state, binds this+0x264 through CGenericActiveReader__SetReader, then calls CGeneralVolume__ResetCooldownTimestamp with the same target. Exact source identity, concrete layout, local names, runtime behavior, and rebuild parity remain unproven.",
            "active-reader", "reader-reset", "comment-normalized"),
        spec("0x00412830", "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
            "void __thiscall CGeneralVolume__DisableLinkedEntriesByNameAndReselect(void * this, char * entry_name)",
            null,
            "entry-selection", "string-compare", "weapon-selection"),
        spec("0x00413660", "CGeneralVolume__ApplyYawInputByWeaponClass",
            "void __thiscall CGeneralVolume__ApplyYawInputByWeaponClass(void * this, int axis_input)",
            null,
            "axis-input", "yaw", "weapon-class-control"),
        spec("0x004136e0", "CGeneralVolume__ApplyPitchInputByWeaponClass",
            "void __thiscall CGeneralVolume__ApplyPitchInputByWeaponClass(void * this, int axis_input)",
            null,
            "axis-input", "pitch", "weapon-class-control")
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
            throw new IllegalStateException("Wave1128 GeneralVolume normalization failed: missing=" + missing + " bad=" + bad);
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
