//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyProjectileSpawnTailWave495 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String newName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.newName)
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }
        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }
        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
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
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "round-wave495",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d9ef0",
                "CEngine__UpdateRoundAndTriggerLaunchEffect",
                "CRound__UpdateRoundAndTriggerLaunchEffect",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave495 corrective owner/comment update: Wave495 readback proved the callee at 0x004db630 is CRound__ArmProjectileAndSpawnTrailEffect, so this vtable-referenced helper is also a CRound-style register-only receiver. Vtable/data references at 0x005de940 and 0x005e3cb8 point here; the body arms the projectile/trail effect, resets the CUnit-style timestamp at +0xd0, checks round-config fields this+0xf0+0x5c and +0x6c, and when both are zero builds an effect/explosion-style payload with mode 2 before dispatching virtual slot +0xc8. Static retail evidence only; exact source method name, concrete round/config/effect layouts, runtime launch/effect behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "launch-effect", "vtable-referenced")
            ),
            new Spec(
                "0x004d9f30",
                "CExplosionInitThing__ctor_like_004d9f30",
                "CRound__UpdateEffectTransformByMode_004d9f30",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("effectMode", intType),
                    param("context", voidPtr),
                    param("targetOrOwner", voidPtr)
                },
                "Wave495 name/signature/comment correction: RET 0x0c plus ECX receiver prove a CRound-style thiscall helper with effectMode, context, and target/owner stack arguments, not a CExplosionInitThing constructor. The body constructs a CInitThing/CExplosionInitThing-like stack payload, branches through mode 0/1/3 transform paths, samples heightfield or target/context vectors, updates linked particle/effect state at this+0xe0/this+0xe4, and syncs effect transforms from round transform fields. Static retail evidence only; exact source method name, concrete CRound/effect/payload layouts, runtime effect behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "effect-transform", "cinitthing-payload", "mode-dispatch")
            ),
            new Spec(
                "0x004daa20",
                "CEngine__FindPresetIndexByName",
                "CEngine__FindPresetIndexByName",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("presetName", charPtr)
                },
                "Wave495 signature/comment hardening: cdecl helper with one presetName stack argument scans the global preset/list root at DAT_008553f8, compares presetName against each entry name at +0x30, and returns the zero-based ordinal or -1. Static retail evidence only; exact source owner, list type, string ownership, runtime preset behavior, and rebuild parity remain unproven.",
                tags("preset-list", "name-lookup")
            ),
            new Spec(
                "0x004daab0",
                "CEngine__SetProjectileTargetReader",
                "CRound__SetTargetReaderIfAllowed",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("targetReader", voidPtr),
                    param("replaceExisting", intType)
                },
                "Wave495 owner/signature/comment correction: RET 0x8 plus ECX receiver prove a CRound-style thiscall helper with targetReader and replaceExisting stack arguments. The body gates target assignment on round-config fields at this+0xf0+0x48/+0x1c, optionally removes the old reader from the owner monitor and DAT_008551a0, clears this+0xe8, binds targetReader through CGenericActiveReader__SetReader, and adds this round to DAT_008551a0 when the reader has flag bit 0x08. Static retail evidence only; exact source method name, concrete reader/list layout, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "active-reader", "targeting")
            ),
            new Spec(
                "0x004dab50",
                "CRound__RemoveActiveReaderById",
                "CRound__RemoveActiveReaderById",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave495 signature/comment hardening: register-only ECX receiver removes the active target reader rooted at this+0xe8. The body removes this+0xe8 from the owner monitor at this+0xec when flag bit 0x08 is set, removes this round from DAT_008551a0 when the current reader is flagged, then clears the CGenericActiveReader at this+0xe8. Static retail evidence only; exact reader/list layout, source method name, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("active-reader", "targeting")
            ),
            new Spec(
                "0x004daba0",
                "CEngine__FindNearbyHostileWithinProjectileRadius",
                "CRound__FindNearbyHostileWithinProjectileRadius",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave495 owner/signature/comment correction: register-only ECX receiver is a CRound-style helper that scans CMapWho around this+0x1c/0x20/0x24 with radius from round-config this+0xf0+0x90. It rejects the current target reader at this+0xe8, requires candidate flag bit 0x10 and excludes flag bit 0x04, samples target world position, and returns the first candidate inside radius squared and outside the near-zero threshold. Static retail evidence only; exact source method name, concrete CMapWho/target layout, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "targeting", "mapwho", "radius-query")
            ),
            new Spec(
                "0x004dac90",
                "CRound__SelectBestTargetReaderAndSyncAimState",
                "CRound__SelectBestTargetReaderAndSyncAimState",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("eventPayload", voidPtr),
                    param("unusedContext", voidPtr)
                },
                "Wave495 signature/comment hardening: RET 0x8 plus ECX receiver prove two stack arguments; only eventPayload is observed reaching CEventManager__AddEvent_AtTime. When round-config +0x48 equals 1 and this+0xe8 is empty, the body scans DAT_008550d0, scores candidate readers in round-local aim space, applies config angle polarity and CBattleEngine__IsWeaponModeCompatibleWithMountState, binds the best reader through the active-reader helper, writes target/aim state at this+0x108..0x114, and schedules event 0xfa3 with a randomized delay. Static retail evidence only; exact source method name, concrete reader/aim/event layouts, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("active-reader", "targeting", "event-scheduling", "aim-state")
            ),
            new Spec(
                "0x004db090",
                "CEngine__GetPresetScalarByName",
                "CRound__GetPresetScalarByConfigName",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave495 owner/signature/comment correction: register-only ECX receiver reads the round-config name pointer at this+0xf0+0x08, scans the global preset/list root at DAT_008553f8, and returns the matched entry scalar at +0x38 through x87 or the zero/default global when no match is found. Static retail evidence only; exact source method name, concrete preset/list layout, scalar meaning, runtime projectile behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "preset-list", "x87-return")
            ),
            new Spec(
                "0x004db150",
                "CEngine__SpawnConfiguredProjectile",
                "CRound__SpawnConfiguredProjectile",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave495 owner/signature/comment correction: register-only ECX receiver is a CRound-style spawn helper. It selects a nearby hostile through CRound__FindNearbyHostileWithinProjectileRadius or randomizes a ground point inside config radius, creates a projectile through CWorldPhysicsManager__CreateProjectile(this+0xf0), builds a CRoundInitThing-like stack payload with origin, destination, round-data, jump count, delay/lifespan, target reader, and config scalars, then dispatches the new projectile init slot. Static retail evidence only; exact source method name, concrete payload/layouts, runtime projectile behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "projectile-spawn", "targeting", "croundinitthing-payload")
            ),
            new Spec(
                "0x004db630",
                "CEngine__ArmProjectileAndSpawnTrailEffect",
                "CRound__ArmProjectileAndSpawnTrailEffect",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave495 owner/signature/comment correction: register-only ECX receiver arms a CRound-style projectile only when this+0x12c is clear and round-config +0x6c is set. The body sets launch state at this+0x12c, clamps position height, normalizes/scales velocity from this+0x7c..0x84 using config +0x2c, clears the particle/effect link at this+0xe0, optionally creates the configured trail effect from config +0x04, syncs effect transform rows, and refreshes effect timing. Static retail evidence only; exact source method name, concrete effect/round layouts, runtime launch/trail behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "launch-effect", "particle-effect", "velocity")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=0 would_create=0" +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave495 apply had missing/bad rows");
        }
    }
}
