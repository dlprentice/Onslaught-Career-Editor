//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyHudOverlayHelpersWave411 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "hud-overlay-helpers-wave411",
            "hud",
            "overlay",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
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
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00483530",
                "CHud__RenderControllerSlotStatusPanel",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud overlay helper for the controller slot status panel, called from CHud__RenderOverlayForViewpoint. It animates HUD fields +0x68/+0x94/+0x98/+0xac, calls CHud__RenderSegmentedMeterBar, formats timer/status text, and draws it with CDXFont. Static retail evidence only; exact source body identity, concrete CHud layout, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderControllerSlotStatusPanel"},
                tags("controller-status", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00484340",
                "CHud__RenderTargetMarkers3D",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud overlay helper for 3D target marker sprites, called from CHud__RenderOverlayForViewpoint. It uses CHud fields +0x50/+0x54/+0x58, applies overlay sprite state, reads CBattleEngine__GetInterpolatedAutoAimPos, and draws target marker textures. Static retail evidence only; exact source body identity, concrete CHud/BattleEngine layout, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderTargetMarkers3D"},
                tags("target-markers", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00484c50",
                "CHud__RenderTacticalRadarContacts",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud tactical radar overlay helper called from CHud__RenderOverlayForViewpoint. It partitions visible units into temporary pointer sets, projects nearby contacts using the active BattleEngine orientation, selects marker textures through CHud__SelectMarkerTextureIndexByUnitFlags, draws markers through HudOverlay__DrawSpriteQuad, and clears temporary sets. Static retail evidence only; exact source body identity, concrete unit/radar semantics, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderTacticalRadarContacts"},
                tags("tactical-radar", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004857e0",
                "HudOverlay__DrawSpriteQuad",
                "__cdecl",
                voidType,
                "Wave411 signature/comment correction: owner-neutral HUD overlay sprite helper called repeatedly by CHud__RenderTacticalRadarContacts. It forwards x/y, texture, and argb_tint_bits to CVBufTexture__DrawSpriteEx with fixed depth 0.011 and fixed sprite sizing parameters. Static retail evidence only; exact tint semantics remain unproven.",
                new String[] {"CExplosionInitThing__DrawHudSpriteQuad"},
                tags("sprite-helper", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("x", floatType),
                    param("y", floatType),
                    param("texture", voidPtr),
                    param("argb_tint_bits", floatType)
                }
            ),
            new Spec(
                "0x00485830",
                "CHud__SelectMarkerTextureIndexByUnitFlags",
                "__thiscall",
                intType,
                "Wave411 owner/signature correction: CHud tactical marker texture selector with one stack argument (unit; RET 0x4). It reads unit flags at +0x34 and returns one of CHud texture slots +0x1a0/+0x1a4/+0x1a8. Static retail evidence only; exact unit layout, texture semantics, and runtime HUD behavior remain unproven.",
                new String[] {"CExplosionInitThing__SelectMarkerTextureIndexByUnitFlags"},
                tags("marker-texture", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unit", voidPtr)
                }
            ),
            new Spec(
                "0x004858d0",
                "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud overlay helper for the objective progress gauge and heading needle, called from CHud__RenderOverlayForViewpoint. It applies overlay render state, draws gauge sprites, reads CBattleEngine__GetWeaponCharge, and rotates a heading needle from CBattleEngine__GetInterpolatedEulerOrientation. Static retail evidence only; exact source body identity, concrete CHud/BattleEngine layout, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderObjectiveProgressGaugeAndHeadingNeedle"},
                tags("objective", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00485d50",
                "CHud__RenderObjectiveStatusPanel",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud overlay helper for objective and weapon status panel, called from CHud__RenderOverlayForViewpoint. It checks CBattleEngine__CountFlag9CBySelectionMode, chooses weapon icons/names through CBattleEngine__GetWeaponIconName and CBattleEngine__GetWeaponName, handles multiplayer lives via CGame__GetPlayerLives, and draws objective text lines. Static retail evidence only; exact source body identity, concrete text-slot semantics, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderObjectiveStatusPanel"},
                tags("objective", "weapon-status", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00486940",
                "CHud__RenderObjectiveSlotFillPanel",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud overlay helper for weapon energy/ammo slot fill panel, called from CHud__RenderOverlayForViewpoint. It branches on CBattleEngine__IsEnergyWeapon, reads CBattleEngine__GetWeaponAmmoPercentage, CBattleEngine__IsWeaponOverheated, and CBattleEngine__GetWeaponAmmoCount, then draws fill sprites or ammo text. Static retail evidence only; exact source body identity, concrete ammo semantics, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderObjectiveSlotFillPanel"},
                tags("objective", "weapon-status", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00486e00",
                "CHud__RenderWorldTargetSprites",
                "__thiscall",
                voidType,
                "Wave411 owner/signature correction: CHud overlay helper for world-space target and lock sprites, called from CHud__RenderOverlayForViewpoint. It uses CHud fields +0x50/+0x54/+0x58, applies overlay state, projects target/lock info, reads CLockInfo__GetLockPercentage, and uses CUnitAI__GetWorldPositionForTargeting for unit markers. Static retail evidence only; exact source body identity, concrete list layouts, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__RenderWorldTargetSprites"},
                tags("world-targets", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave411 apply script failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
