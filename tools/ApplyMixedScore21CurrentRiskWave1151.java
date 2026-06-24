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

public class ApplyMixedScore21CurrentRiskWave1151 extends GhidraScript {
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
        "wave1151-mixed-score21-current-risk-review",
        "wave1151-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score-21-current-risk",
        "mixed-score21-current-risk-review"
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x00403ff0", "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk",
            "void __thiscall CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk(void * this)",
            "resource-descriptor", "cleanup-thunk", "compiler-unwind"),
        spec("0x00405990", "CDXCockpit__dtor_base_thunk",
            "void __fastcall CDXCockpit__dtor_base_thunk(void * this)",
            "cockpit", "destructor", "jump-thunk"),
        spec("0x004059a0", "CCylinder__VFunc_01_004059a0",
            "int __thiscall CCylinder__VFunc_01_004059a0(void * this, void * forwardedA, void * forwardedB, void * dispatchObject, void * forwardedC)",
            "cylinder", "primitive-collision", "vtable-wrapper"),
        spec("0x004098c0", "CLine__VFunc_01_004098c0",
            "int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)",
            "cline", "primitive-collision", "vtable-wrapper"),
        spec("0x00417870", "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward",
            "void __fastcall CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward(void * this)",
            "building", "occupancy", "static-shadow", "vtable-slot-02"),
        spec("0x004661c0", "DeviceObject__dtor_thunk",
            "void __thiscall DeviceObject__dtor_thunk(void * this)",
            "deviceobject", "destructor", "jump-thunk"),
        spec("0x0046a220", "FrontEndText__GetMultiplayerLevelDescriptionByType",
            "short * __cdecl FrontEndText__GetMultiplayerLevelDescriptionByType(int level_type)",
            "frontend", "localization", "multiplayer"),
        spec("0x004bd5c0", "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
            "void __cdecl CWorld__RasterizeFootprintIntoOccupancyBitplanes(int min_world_x, int min_world_y, int max_world_x, int max_world_y, int skip_shadow_rebuild)",
            "world", "occupancy", "heightfield", "static-shadow"),
        spec("0x004cf050", "CMenuItem__Destructor_Thunk",
            "void __thiscall CMenuItem__Destructor_Thunk(void * this)",
            "menuitem", "destructor", "jump-thunk", "pause-menu"),
        spec("0x004dba40", "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
            "void * __fastcall CRTBuilding__VFuncSlot10_PickRandomLinkedEntry(void * this)",
            "rtbuilding", "linked-list", "random-selection", "vtable-slot-10"),
        spec("0x0055e3ea", "CRT__FpuIntrinsicDispatch2Thunk",
            "void __cdecl CRT__FpuIntrinsicDispatch2Thunk(void)",
            "crt-runtime", "compiler-runtime", "fpu-intrinsic-dispatch"),
        spec("0x00564a0b", "CRT__SpawnSearchPathWithFallbackExtensions",
            "int __cdecl CRT__SpawnSearchPathWithFallbackExtensions(int spawnMode, char * commandPath, void * argv, void * envp)",
            "crt-runtime", "spawn", "path-probe"),
        spec("0x00569cb8", "CRT__FloatDispatchAmsgExitCode2Thunk",
            "void CRT__FloatDispatchAmsgExitCode2Thunk(void)",
            "crt-runtime", "compiler-runtime", "float-conversion-dispatch", "amsg-exit-code-2")
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

            if (missingTags.isEmpty()) {
                println("SKIP: " + spec.address + " " + spec.name + " tags already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (dryRun) {
                println("WOULD_UPDATE: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags));
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
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=0"
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1151 mixed score21 current-risk normalization failed: missing=" + missing + " bad=" + bad);
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
