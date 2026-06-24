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

public class ApplyCollisionHLWave398 extends GhidraScript {
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
            "collision-hl-wave398",
            "hlcollision",
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
                throw new IllegalStateException("Function not found at " + spec.address);
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
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00480a30",
                "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
                "__thiscall",
                voidType,
                "Wave398 owner/signature/comment correction: corrects the older CCollisionSeekingRound owner label to the high-level collision detector context. The helper stores collision_component at +0x8, clears detector fields at +0xc/+0x10, scans neighbor MapWho sectors across layers, traverses top-layer quad children, filters candidate collision components, dispatches collision pairs, and warns on unexpected collision change state. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__ScanNeighborSectorsAndDispatchCollisions"},
                tags("owner-corrected", "sector-scan", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("collision_component", voidPtr)
                }
            ),
            new Spec(
                "0x00480c90",
                "CHLCollisionDetector__HandleCollisionEnter",
                "__thiscall",
                voidType,
                "Wave398 signature/comment correction: enter-event callback increments the collision checks counter, compares targeting positions and combined radius context, applies the 0x100 collision filter through both components, calls the current component enter callback, marks scheduled collision context, and dispatches or schedules follow-up collision handling. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("enter-callback", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_component", voidPtr)
                }
            ),
            new Spec(
                "0x00480db0",
                "CHLCollisionDetector__HandleCollisionExit",
                "__thiscall",
                voidType,
                "Wave398 signature/comment correction: exit-event callback rejects null/self candidates, applies mutual collision filters, warns when the collision-changed flag is already set, otherwise dispatches the collision pair and clears the flag. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("exit-callback", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_component", voidPtr)
                }
            ),
            new Spec(
                "0x00480e10",
                "CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions",
                "__thiscall",
                voidType,
                "Wave398 owner/signature/comment correction: corrects the older CCollisionSeekingRound owner label to high-level collision detector context. The helper recursively traverses four child pointers from a top-layer quad node or map/who entry, iterates candidate entries through the shared MapWho iterator, resolves candidate collision components, applies self/mutual filters, dispatches collision pairs, and warns on unexpected collision change state. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {"CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions"},
                tags("owner-corrected", "quad-traversal", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mapwho_entry_or_quad_node", voidPtr)
                }
            ),
            new Spec(
                "0x00480ed0",
                "CHLCollisionDetector__DispatchCollisionEventForPair",
                "__thiscall",
                voidType,
                "Wave398 signature/comment correction: pair dispatcher warns when an existing event queue/list appears too large, compares targeting positions, computes separation distance from combined radii, estimates delay from component speed-like callbacks and DAT_00672fd0 time, calls the enter handler immediately when ready, or schedules EVENT_MANAGER event 2000 while optionally reusing the saved event pointer at +0xc. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("event-dispatch", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_component", voidPtr)
                }
            ),
            new Spec(
                "0x00481060",
                "CHLCollisionDetector__ProcessMapWhoCollisionSweep",
                "__thiscall",
                voidType,
                "Wave398 signature/comment correction: map/who sweep compares previous and current sectors, descends through map layers, scans neighbor cells outside the prior-sector neighborhood, runs exit callbacks for old top-layer entries, and dispatches candidate pair collisions for newly entered cells. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mapwho-sweep", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("previous_sector", voidPtr),
                    param("current_sector", voidPtr)
                }
            ),
            new Spec(
                "0x004812d0",
                "CHLCollisionDetector__HandleScheduledCollisionEvent",
                "__thiscall",
                voidType,
                "Wave398 name/signature/comment correction: renames the vfunc-style label to a scheduled collision event handler. The callback checks event number 2000, uses the event data pointer at +0xc as the candidate collision component, saves the event pointer for reuse, calls CHLCollisionDetector__HandleCollisionEnter, then clears detector fields at +0x10 and +0xc. Static retail evidence only; exact source identity, concrete CHLCollisionDetector layout, locals/types, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {"CHLCollisionDetector__VFunc_00_004812d0"},
                tags("scheduled-event", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("event", voidPtr)
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
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave398 high-level collision apply had failures");
        }
    }
}
