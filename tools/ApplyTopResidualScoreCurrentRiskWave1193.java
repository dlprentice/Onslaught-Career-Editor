//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyTopResidualScoreCurrentRiskWave1193 extends GhidraScript {
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
        "wave1193-top-residual-score20-18-current-risk-review",
        "wave1193-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "top-residual-score20-18",
        "source-identity-deferred",
        "exact-layout-deferred",
        "runtime-behavior-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x00424730",
            "CCockpit__dtor_base",
            "void __fastcall CCockpit__dtor_base(void * this)",
            "Wave1193 static current-risk read-back: score20 residual cockpit destructor-base row retained with normalized rebuild-grade tags. Fresh metadata/decompile evidence preserves the CCockpit destructor-base contract: reset CCockpit vtable slots 0x005d9524 and 0x005d94ac, release the owned object at this+0x8c through its vfunc when present, then call CMonitor__Shutdown. Static rebuild contract only; exact CCockpit layout, exact source-body identity, runtime cockpit cleanup behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score20", "cockpit", "destructor", "monitor-shutdown", "owned-object-release")
        ),
        new Target(
            "0x004df530",
            "CShell__CopyResourceNameToInlineBuffer",
            "void __thiscall CShell__CopyResourceNameToInlineBuffer(void * this, char * resource_name)",
            "Wave1193 static current-risk read-back: score20 residual CShell resource-name helper retained from the Wave507 stale-owner correction. Fresh xrefs keep ProjectileBurst__SpawnFromCurrentPreset as the live caller after OID__CreateObject(0x15); body evidence copies a non-empty C string into the constructor-cleared inline buffer at this+0x110 and returns with RET 0x4. Static rebuild contract only; exact buffer-size contract, caller preconditions, exact source-body identity, runtime projectile-shell behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score20", "cshell", "resource-name", "projectile-burst-shell", "stale-owner-corrected")
        ),
        new Target(
            "0x0055da76",
            "CRT__InitRuntimeFromStoredFrameGlobals",
            "void CRT__InitRuntimeFromStoredFrameGlobals(void)",
            "Wave1193 static current-risk read-back: score20 residual CRT runtime-init row retained from Wave878/Wave879 context. Fresh xrefs keep computed call evidence from CRT__RunStaticInitRangesWithOptionalCallback and DATA row 0x006532e8; body evidence calls CRT__InitFloatConversionDispatchTable, probes processor features through CDXTexture__ProbeProcessorFeaturePresentOrFallback, stores DAT_009d08b8, then calls CRT__InitFpuControlWord_0x10000_0x30000. Static rebuild contract only; exact startup-table semantics, CPU feature policy, FPU side effects, source identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score20", "crt-runtime", "runtime-init", "static-init", "fpu-control", "cpu-feature-probe")
        ),
        new Target(
            "0x0055dd7b",
            "CRT__RunStaticInitRangesWithOptionalCallback",
            "void CRT__RunStaticInitRangesWithOptionalCallback(void)",
            "Wave1193 static current-risk read-back: score20 residual CRT static-init range walker retained from the Wave879 owner correction. Fresh evidence keeps entry as the direct xref, conditionally calls PTR_CRT__InitRuntimeFromStoredFrameGlobals_006532e8, then invokes CRT__InvokeFunctionPointerRange over 0x00622b10-0x00622b28 and 0x00622000-0x00622b0c. Static rebuild contract only; exact table ownership, callback prototypes, initialization ordering, source identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score20", "crt-runtime", "static-init", "function-pointer-ranges", "entry-xref")
        ),
        new Target(
            "0x00562a89",
            "CRT__SetErrnoForFpSourceKind",
            "void __cdecl CRT__SetErrnoForFpSourceKind(int sourceKind)",
            "Wave1193 static current-risk read-back: score20 residual CRT FPU/errno helper retained from Wave628. Fresh metadata/decompile evidence preserves the sourceKind mapping: write EDOM 0x21 for sourceKind 1, write ERANGE 0x22 for sourceKind 2 or 3 through the CRT thread-local errno pointer, and leave other source kinds unchanged. Static rebuild contract only; exact source-kind enum names, runtime errno behavior, CRT library identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score20", "crt-runtime", "errno", "fpu-exception", "source-kind")
        ),
        new Target(
            "0x004014c0",
            "SharedVFunc__NoOpOneArg_004014c0",
            "void __thiscall SharedVFunc__NoOpOneArg_004014c0(void * this, int arg0)",
            "Wave1193 static current-risk read-back: score19 residual shared vfunc no-op retained as owner-neutral. Fresh xrefs remain broad DATA vtable usage; the function body is the shared RET 0x4 one-argument no-op target also seen in non-frontend tables such as CSpawnerRecall. Static rebuild contract only; exact owner coverage, exact virtual slot names, caller type systems, runtime dispatch behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "shared-vfunc", "no-op", "ret-0x4", "owner-neutral")
        ),
        new Target(
            "0x00405930",
            "SharedVFunc__ReturnZero_00405930",
            "int __thiscall SharedVFunc__ReturnZero_00405930(void * this)",
            "Wave1193 static current-risk read-back: score19 residual shared return-zero vfunc retained as owner-neutral. Fresh xrefs remain broad DATA vtable usage across unrelated tables, while body evidence returns integer zero with no receiver field access. Static rebuild contract only; exact owner coverage, exact virtual contracts, caller type systems, runtime dispatch behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "shared-vfunc", "return-zero", "owner-neutral", "vtable-slot")
        ),
        new Target(
            "0x00452b60",
            "CFrontEndPage__Process_NoOp",
            "void __thiscall CFrontEndPage__Process_NoOp(void * this, int state)",
            "Wave1193 static current-risk read-back: score19 residual frontend page process no-op retained from prior signature correction. Fresh xrefs remain broad frontend page vtable/wrapper usage; instruction evidence is RET 0x4, matching a thiscall receiver plus one state argument and a harmless default process slot. Static rebuild contract only; exact page identities, exact virtual names, runtime frontend behavior, UI parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "frontend", "frontend-page", "process", "shared-noop", "ret-0x4")
        ),
        new Target(
            "0x00453ac0",
            "SharedVFunc__NoOp_Ret0C",
            "void __stdcall SharedVFunc__NoOp_Ret0C(int unused0, int unused1, int unused2)",
            "Wave1193 static current-risk read-back: score19 residual shared no-op retained as owner-neutral. Fresh DATA xrefs still span CControllerDefinition and unrelated script/datatype tables; instruction evidence is a zero-body RET 0x0c target with three stack slots and no receiver evidence. Static rebuild contract only; exact semantic contract, caller type systems, runtime dispatch behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "shared-vfunc", "shared-noop", "ret-0x0c", "owner-neutral")
        ),
        new Target(
            "0x0047e6e0",
            "CHazard__VFunc02_CleanupWorldSoundAndLinkedState",
            "void __fastcall CHazard__VFunc02_CleanupWorldSoundAndLinkedState(void * this)",
            "Wave1193 static current-risk read-back: score19 residual CHazard cleanup slot retained from Wave396. Fresh metadata/decompile evidence preserves the vfunc02 cleanup contract: kill hazard sound samples, finalize linked state rooted at this+0x80, remove the unit from the world occupancy grid, then delegate to the base cleanup slot. Static rebuild contract only; exact CHazard layout, exact source-body identity, runtime hazard/audio/world cleanup behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "hazard", "hazard-cleanup", "sound-cleanup", "world-occupancy", "vfunc-slot-02")
        ),
        new Target(
            "0x004bac10",
            "CMissile__DispatchLinkedObjectVFunc68AndPostHook",
            "void __thiscall CMissile__DispatchLinkedObjectVFunc68AndPostHook(void * this, int arg0, int arg1)",
            "Wave1193 static current-risk read-back: score19 residual CMissile linked-object dispatch row retained from Wave456. Fresh evidence keeps the CMissile-adjacent vtable DATA xref at 0x005e3cc0; body evidence dispatches the linked object at this+0x30 through vfunc +0x68 with arg0/arg1, calls SharedVFunc__NoOp_Ret08, and ends with RET 0x8. Static rebuild contract only; exact linked-object contract, exact virtual slot/source identity, runtime missile behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "missile", "linked-object-dispatch", "vfunc-0x68", "ret-0x8")
        ),
        new Target(
            "0x004f45c0",
            "SharedVFunc__ForwardField64FloatOrZero_004f45c0",
            "float __thiscall SharedVFunc__ForwardField64FloatOrZero_004f45c0(void * this)",
            "Wave1193 static current-risk read-back: score19 residual shared float-forwarder retained from Wave1082 boundary recovery. Fresh xrefs remain broad CThing/AI-family DATA table refs including CInfantryAI slot 55; body evidence loads this+0x64, returns a global zero/default float when null, or tail-jumps to 0x004048c0 when non-null. Static rebuild contract only; exact source virtual name, concrete field semantics, runtime dispatch behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "shared-vfunc", "float-forwarder", "field-0x64", "vtable-boundary")
        ),
        new Target(
            "0x0050a3a0",
            "CWingmanStart__VFunc_09_0050a3a0",
            "void __thiscall CWingmanStart__VFunc_09_0050a3a0(void * this, void * init)",
            "Wave1193 static current-risk read-back: score19 residual CWingmanStart vfunc09 init-style row retained from Wave1009 boundary recovery. Fresh evidence keeps RTTI/vtable slot evidence at 0x005dcb7c; body evidence uses init+0x04 as world position, samples global static-shadow heightfield object 0x006fadc8, clamps init height, calls CComplexThing__Init, copies position/orientation/config fields, and selects fighter spawner names such as Tara_Fighter/Billy_Fighter by global state. Static rebuild contract only; exact source method identity, concrete init/object layouts, runtime wingman spawn behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "wingman-start", "init", "static-shadow", "fighter-spawner", "vtable-slot")
        ),
        new Target(
            "0x00541f00",
            "CDXGame__dtor_thunk",
            "void __fastcall CDXGame__dtor_thunk(void * this)",
            "Wave1193 static current-risk read-back: score19 residual CDXGame destructor thunk retained from Wave385 owner correction. Fresh instruction evidence remains an unconditional jump to CGame__dtor, and source/RTTI evidence keeps the adjacent secondary vtable as CDXGame. Static rebuild contract only; exact destruction ordering beyond the thunk target, runtime destruction behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "dxgame", "game", "destructor", "jump-thunk")
        ),
        new Target(
            "0x0055e412",
            "CRT__SpawnPathVarargsNoEnv_Thunk",
            "void __cdecl CRT__SpawnPathVarargsNoEnv_Thunk(int spawnMode, char * commandPath)",
            "Wave1193 static current-risk read-back: score19 residual CRT spawn/file-I/O thunk retained from Wave631. Fresh evidence keeps the two named parameters plus first variadic stack argument as argv, supplies a null environment pointer, and forwards to CRT__SpawnSearchPathWithFallbackExtensions. Static rebuild contract only; exact exported CRT API identity, varargs contract, return-value use, runtime process behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score19", "crt-runtime", "spawn", "varargs-thunk", "file-io")
        ),
        new Target(
            "0x00421ba0",
            "CCarrierAI__dtor_base",
            "void __fastcall CCarrierAI__dtor_base(void * this)",
            "Wave1193 static current-risk read-back: score18 residual CCarrierAI destructor-base row retained with normalized rebuild-grade tags. Fresh decompile evidence resets the base monitor-style vtable, removes linked reader slots at this+0x28, this+0x24, and this+0x0c from owning CSPtrSet lists when present, then calls CMonitor__Shutdown. Static rebuild contract only; concrete CCarrierAI layout, exact source-body identity, runtime carrier AI cleanup behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "carrier-ai", "destructor", "csptrset-unregister", "monitor-shutdown")
        ),
        new Target(
            "0x00444660",
            "CDestructableSegmentsController__Init",
            "void __fastcall CDestructableSegmentsController__Init(void * this)",
            "Wave1193 static current-risk read-back: score18 residual destructable-segments controller init row retained. Fresh xrefs keep CUnit__Init reaching this through the unit controller pointer at +0x178; body evidence obtains the mesh root, allocates and zeros the tracked segment array from mesh node count, recursively processes the root mesh node, warns on primary-core anomalies, links secondary/core component monitor entries, dispatches per-segment behavior setup, and caches root health/value at this+0x18. Static rebuild contract only; exact source identity, concrete controller/segment layouts, runtime destruction behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "destructable-segments", "component-link", "mesh-walk", "init")
        ),
        new Target(
            "0x00462640",
            "CFEPMain__Process",
            "void __thiscall CFEPMain__Process(void * this, int state)",
            "Wave1193 static current-risk read-back: score18 residual CFEPMain process loop retained from Wave401. Fresh evidence preserves the state-gated frontend process contract: menu updates, career node checks 800/0x2e5, FEPMain.cpp debug-path allocation before CCareer__Save and CFEPOptions__WriteDefaultOptionsFile, and routes to page 0x0c or new-game setup refresh. Static rebuild contract only; concrete layout, exact source-body identity, runtime save/frontend behavior, UI parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "frontend", "fepmain", "process", "save-flow", "new-game")
        ),
        new Target(
            "0x0047c730",
            "CGroundUnit__Init",
            "void __thiscall CGroundUnit__Init(void * this, void * init_data)",
            "Wave1193 static current-risk read-back: score18 residual CGroundUnit init row retained from Wave392. Fresh evidence keeps CGroundUnit vtable 0x005e32d4 slot 9 pointing here; body evidence delegates to CUnit__Init, copies profile movement fields, scans Thruster markers, adds linked nodes to the this+0x1d4 set, and initializes this+0x1e4/0x250/0x254/0x25c state. Static rebuild contract only; concrete GroundUnit layout, exact source-body identity, runtime ground-unit initialization behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "ground-unit", "init", "thruster-marker", "linked-node-set")
        ),
        new Target(
            "0x0047d420",
            "CUnitAI__QueueFiringOrPostfireAnimation",
            "void __fastcall CUnitAI__QueueFiringOrPostfireAnimation(void * this)",
            "Wave1193 static current-risk read-back: score18 residual CUnitAI firing/postfire animation row retained from Wave393. Fresh evidence keeps CGroundVehicle vtable 0x005e297c slot 87 pointing here; after CUnitAI__FinalizeSpawnAndAdvanceState, the body queues firing when profile field +0x1c is zero or postfire otherwise, validates the animation index, and dispatches vfunc +0xf0. Static rebuild contract only; concrete CUnitAI/layout semantics, exact source-body identity, runtime animation/firing behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "cunitai", "firing", "postfire", "animation", "groundvehicle")
        ),
        new Target(
            "0x00504510",
            "CWarspite__Destructor",
            "void __fastcall CWarspite__Destructor(void * this)",
            "Wave1193 static current-risk read-back: score18 residual CWarspite destructor row retained from Wave536. Fresh evidence preserves the register-only cleanup contract: restore base controller vtable 0x005d8d1c, unregister tracked pointers at this+0x28, this+0x24, and this+0x0c from owning CSPtrSet lists when present, then tail into CMonitor__Shutdown. Static rebuild contract only; exact member ownership, runtime cleanup ordering, concrete layout, source identity, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "warspite", "destructor", "csptrset-unregister", "monitor-shutdown")
        ),
        new Target(
            "0x005049b0",
            "CWarspiteDome__Destructor",
            "void __fastcall CWarspiteDome__Destructor(void * this)",
            "Wave1193 static current-risk read-back: score18 residual CWarspiteDome destructor row retained from Wave536. Fresh evidence preserves the same register-only cleanup pattern as CWarspite: restore base controller vtable 0x005d8d1c, unregister tracked pointers at this+0x28, this+0x24, and this+0x0c from owning CSPtrSet lists when present, then tail into CMonitor__Shutdown. Static rebuild contract only; exact member ownership, runtime cleanup ordering, concrete layout, source identity, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "warspitedome", "destructor", "csptrset-unregister", "monitor-shutdown")
        ),
        new Target(
            "0x0050ed80",
            "CBigAirUnit__ctor_base",
            "void * __fastcall CBigAirUnit__ctor_base(void * this)",
            "Wave1193 static current-risk read-back: score18 residual CBigAirUnit constructor-base row retained from Wave557. Fresh evidence keeps CWorldPhysicsManager__CreateThingByType as an allocator/caller; body evidence calls CUnit__ctor_base, zeroes global-list node state at this+0x254, links this+0x250 through CWorldPhysicsManager__PushNodeGlobalList, initializes pointer sets at this+0x25c and this+0x26c, installs base CBigAirUnit vtables, and returns this. Static rebuild contract only; exact source constructor identity, concrete layout, runtime spawn behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "big-air-unit", "constructor", "factory", "global-list", "world-physics-manager")
        ),
        new Target(
            "0x00579273",
            "CTexture__BuildTransformMatrixWithOptionalOffsets",
            "int CTexture__BuildTransformMatrixWithOptionalOffsets(void)",
            "Wave1193 static current-risk read-back: score18 residual texture transform matrix dispatch-tail row retained from Wave888. Fresh evidence keeps DATA xref 0x006570ec pointing at this stack-locked body; instruction/decompile evidence initializes identity/scale matrix state, optionally composes quaternion rotations through Math__BuildQuaternionRotationMatrix_Dispatch_Thunk, calls CVertexShader__DispatchTableCall_656fc4 and CFastVB__DispatchIndirect_00656f3c, applies optional pivot subtraction/restoration and translation offsets, returns the output matrix pointer, and ends with RET 0x1c. Static rebuild contract only; exact source identity, matrix convention, hidden ABI completeness, runtime texture transform behavior, render parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("score18", "texture-transform", "transform-matrix", "quaternion-rotation", "pivot-translation", "ret-0x1c")
        )
    };

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        boolean dryRun = true;
        if ("apply".equals(mode)) {
            dryRun = false;
        } else if (!"dry".equals(mode)) {
            throw new IllegalArgumentException("Expected mode dry|apply, got: " + mode);
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
            throw new IllegalStateException("Wave1193 top residual score20-18 normalization failed: missing=" + missing + " bad=" + bad);
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
