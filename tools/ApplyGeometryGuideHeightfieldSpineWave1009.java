//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyGeometryGuideHeightfieldSpineWave1009 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int signatureUpdated = 0;
        int commentUpdated = 0;
        int tagUpdated = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String text) {
        if (!text.startsWith("0x") && !text.startsWith("0X")) {
            text = "0x" + text;
        }
        Address address = toAddr(text);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + text);
        }
        return address;
    }

    private Function functionAt(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "geometry-guide-heightfield-spine-review-wave1009",
            "wave1009-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "static-shadow"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean needsTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAt(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " missing " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected name at " + spec.address + ": " + fn.getName());
            }

            boolean signatureNeeded = !fn.getSignature().toString().equals(expectedSignature(spec));
            boolean commentNeeded = !spec.comment.equals(fn.getComment());
            boolean tagsNeeded = needsTags(fn, spec);

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec) +
                    " signature_needed=" + signatureNeeded +
                    " comment_needed=" + commentNeeded +
                    " tags_needed=" + tagsNeeded);
                stats.skipped++;
                if (signatureNeeded) {
                    stats.signatureUpdated++;
                }
                if (commentNeeded) {
                    stats.commentUpdated++;
                }
                if (tagsNeeded) {
                    stats.tagUpdated++;
                }
                return;
            }

            if (signatureNeeded) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            }
            if (commentNeeded) {
                fn.setComment(spec.comment);
                stats.commentUpdated++;
            }
            if (tagsNeeded) {
                for (String tag : spec.tags) {
                    fn.addTag(tag);
                }
                stats.tagUpdated++;
            }

            Function readBack = functionAt(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!readBack.getSignature().toString().equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }
            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00448580",
                "CDropshipAI__VFunc_09_00448580",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("context", voidPtr)
                },
                "Wave1009 boundary recovery: CDropshipAI RTTI/vtable slot evidence at 0x005db218 points to this previously no-function code island. The body uses ECX as the AI/controller object, reads the controlled unit through this+0x08, samples the global static-shadow heightfield object at 0x006fadc8 through CStaticShadows__SampleShadowHeightBilinear, clamps against the global flat fallback, and advances dropship AI state through virtual calls. Static retail evidence only; exact source method identity, concrete object/layout names, runtime dropship behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CDropshipAI", "dropship", "terrain-height")
            ),
            new Spec(
                "0x00448930",
                "CDropshipGuide__VFunc_03_00448930",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave1009 boundary recovery: CDropshipGuide RTTI/vtable slot evidence at 0x005db234 points to this previously no-function guide update body. The body uses ECX as the guide object, reads owner/guide state from +0x18, builds local vector/matrix temporaries, and repeatedly samples the global static-shadow heightfield object at 0x006fadc8 while steering/ground-height clamping dropship guide movement. Static retail evidence only; exact source method identity, concrete guide layout, runtime pathing behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CDropshipGuide", "dropship-guide", "terrain-height")
            ),
            new Spec(
                "0x004dfaa0",
                "VFuncSlot_09_004dfaa0",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave1009 boundary recovery: data/vtable slot evidence at 0x005dfe44 points to this previously no-function unit-style virtual slot. The body uses ECX as this, checks the +0x2c flag bit, samples the global static-shadow heightfield object at 0x006fadc8 from this+0x1c/+0x20/+0x24 context, may dispatch virtual slot +0x110, constructs a CInitThing-style local, and can create/spawn pickup state through world/physics helpers. Owner remains conservatively bounded to the saved vtable slot label. Static retail evidence only; exact owner/source identity, concrete object/layout names, runtime spawn behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "unit-style", "pickup-spawn", "terrain-height")
            ),
            new Spec(
                "0x004e9600",
                "CSquadNormal__VFunc_20_004e9600",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position", voidPtr)
                },
                "Wave1009 boundary recovery: CNormalSquad RTTI/vtable slot evidence at 0x005df144 points to this previously no-function CSquadNormal virtual body. The body forwards position to CThing__Teleport, walks the member list at this+0xa4, transforms each child offset through the member's transform, writes child positions through virtual slot +0x50, samples the global static-shadow heightfield object at 0x006fadc8, and clamps child height when terrain is lower than the owner/member height. Static retail evidence only; exact source method identity, concrete squad/member layouts, runtime formation behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CSquadNormal", "formation", "terrain-height")
            ),
            new Spec(
                "0x004e96f0",
                "CSquadNormal__VFunc_21_004e96f0",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("orientation", voidPtr)
                },
                "Wave1009 boundary recovery: CNormalSquad RTTI/vtable slot evidence at 0x005df148 points to this previously no-function CSquadNormal virtual body. The body forwards orientation to CComplexThing__TeleportOrientation, walks the member list at this+0xa4, recomputes child offsets with Mat34/Vec3 helpers, samples the global static-shadow heightfield object at 0x006fadc8, clamps child height when needed, and forwards the orientation to each child through virtual slot +0x54. Static retail evidence only; exact source method identity, concrete squad/member layouts, runtime formation behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CSquadNormal", "formation", "terrain-height")
            ),
            new Spec(
                "0x004e9f00",
                "CSquadNormal__VFunc_52_004e9f00",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave1009 boundary recovery: CNormalSquad RTTI/vtable slot evidence at 0x005df1c4 points to this previously no-function CSquadNormal render/debug-style virtual body. The body calls CUnit__RenderWithIdentityWorldAndShadowProbe, samples the global static-shadow heightfield object at 0x006fadc8 for the squad/member positions, and uses CDXEngine beam/debug-volume drawing helpers around multiple linked member/target positions. Static retail evidence only; exact source method identity, concrete render/debug layout, runtime visualization behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CSquadNormal", "render-debug", "terrain-height")
            ),
            new Spec(
                "0x004eaae0",
                "CRelaxedSquad__VFunc_07_004eaae0",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave1009 boundary recovery: data/vtable slot evidence at 0x005e3a9c in the relaxed-squad virtual table area points to this previously no-function body. The body copies matrix/global debug state, sets a world matrix, samples the global static-shadow heightfield object at 0x006fadc8 from this+0x1c/+0x20/+0x24 context, offsets the sampled height, and renders a debug volume/overlay through CThing__RenderDebugVolumeOverlay. Static retail evidence only; exact source method identity, concrete squad/debug layout, runtime render behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CRelaxedSquad", "render-debug", "terrain-height")
            ),
            new Spec(
                "0x004f0e40",
                "CTentacle__VFunc_22_004f0e40",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave1009 boundary recovery: CTentacle RTTI/vtable slot evidence at 0x005e3ff4 points to this previously no-function virtual body. The body installs an SEH frame, gates on this+0x214, plays/finishes activation animation, resolves the Tentacle_Activation_Effect particle manager, transforms an effect anchor, creates the particle effect, samples the global static-shadow heightfield object at 0x006fadc8, clamps the effect height, and updates particle link coordinates before cleanup. Static retail evidence only; exact source method identity, concrete tentacle/effect layouts, runtime particle behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CTentacle", "particle-effect", "terrain-height")
            ),
            new Spec(
                "0x0050a3a0",
                "CWingmanStart__VFunc_09_0050a3a0",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init", voidPtr)
                },
                "Wave1009 boundary recovery: CWingmanStart RTTI/vtable slot evidence at 0x005dcb7c points to this previously no-function init-style body. The body uses init+0x04 as world position, clears a flag at this+0x2c, samples the global static-shadow heightfield object at 0x006fadc8, clamps init height, calls CComplexThing__Init, copies position/orientation/config fields into the object, and selects fighter spawner names such as Tara_Fighter/Billy_Fighter by global state. Static retail evidence only; exact source method identity, concrete init/object layouts, runtime wingman spawn behavior, and rebuild parity remain unproven.",
                tags("vtable-slot", "CWingmanStart", "init", "terrain-height")
            ),
            new Spec(
                "0x00534ac0",
                "ScriptCommand__SampleStaticShadowHeight_00534ac0",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("script_value", voidPtr),
                    param("unused_arg", voidPtr),
                    param("out_result", voidPtr)
                },
                "Wave1009 boundary recovery: ScriptCommandRegistry__InitBuiltins stores this previously no-function command callback at 0x00531270. The body calls the script value vtable slot +0x44 to obtain a world-position vector, samples the global static-shadow heightfield object at 0x006fadc8, allocates an 8-byte CDataType scalar wrapper from CDXMemoryManager at MissionScript.cpp line token 0x2e3, writes the sampled height into the wrapper payload, and stores the wrapper or null into out_result. Static retail evidence only; exact script command name/source identity, concrete script-value layout, runtime script behavior, and rebuild parity remain unproven.",
                tags("script-command", "MissionScript.cpp", "terrain-height")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " signature_updated=" + stats.signatureUpdated
            + " comment_updated=" + stats.commentUpdated
            + " tag_updated=" + stats.tagUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave1009 geometry/guide/heightfield spine hardening failed");
        }
    }
}
